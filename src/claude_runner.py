"""Claude Agent SDK runner for GitHub Actions."""

import os
from pathlib import Path
from typing import Callable, Awaitable

from claude_agent_sdk import query, ClaudeAgentOptions
from claude_agent_sdk.types import SystemMessage, AssistantMessage, UserMessage


FILE_EDITING_TOOLS = ["Read", "Edit", "Write", "Glob", "Grep"]
COMPLETION_MARKER = ".claude-complete"
DEFAULT_TURNS_PER_CHUNK = 10
DEFAULT_MAX_CHUNKS = 5


def build_prompt(title: str, body: str, cwd: str | None = None) -> str:
    """Build the prompt for Claude with system instructions."""
    if not title:
        raise ValueError("Title is required")

    # Allow empty body - title alone is sufficient
    if body is None:
        body = ""

    if cwd is None:
        cwd = os.getcwd()

    completion_marker_path = f"{cwd}/{COMPLETION_MARKER}"

    system_instructions = f"""You are a code editing agent. Your task is to make changes to the codebase.

Working directory: {cwd}

IMPORTANT: You MUST use the file editing tools (Read, Edit, Write, Glob, Grep) to complete your task.
- Use Glob to find files by pattern
- Use Grep to search for code
- Use Read to read file contents
- Use Edit to modify existing files
- Use Write to create new files

All file paths must be absolute paths within the working directory.
For example, to create a file called "hello.txt" in the root, use: {cwd}/hello.txt

Do NOT just describe what changes should be made - actually make them using the tools.

## COMPLETION SIGNAL

When you have FULLY COMPLETED the task:
1. Write the word "DONE" to: {completion_marker_path}
2. This signals that no more work is needed

IMPORTANT: Only write to this file when you are 100% finished with ALL requested changes.
If you still have work to do, do NOT create this file."""

    # Include body only if it's not empty
    if body.strip():
        return f"{system_instructions}\n\n# {title}\n\n{body}"
    else:
        return f"{system_instructions}\n\n# {title}"


def build_continuation_prompt(title: str, body: str, cwd: str) -> str:
    """Build a continuation prompt for when the agent needs more turns."""
    completion_marker_path = f"{cwd}/{COMPLETION_MARKER}"

    base_prompt = f"""Continue working on the task below. You were working on this but ran out of turns.

Review what has been done so far and continue from where you left off.

Working directory: {cwd}

Remember:
- Use the file editing tools to make changes
- When FULLY COMPLETE, write "DONE" to: {completion_marker_path}

# {title}"""

    # Include body only if it's not empty
    if body and body.strip():
        return f"{base_prompt}\n\n{body}"
    else:
        return base_prompt


def build_pr_description_prompt(title: str, body: str, diff: str, issue_number: int, cwd: str | None = None) -> str:
    """Build prompt for generating PR description."""
    if cwd is None:
        cwd = os.getcwd()

    # Handle empty body gracefully
    issue_content = f"### {title}"
    if body and body.strip():
        issue_content = f"{issue_content}\n\n{body}"

    return f"""You are writing a pull request description. Based on the issue and the git diff of changes made, write a clear PR description.

Working directory: {cwd}

Write the PR description to: {cwd}/.pr-description.md

The description should:
1. Start with "Closes #{issue_number}" on its own line
2. Have a "## Summary" section with 2-3 bullet points describing what was done
3. Be concise and factual

Do NOT include a test plan section.

## Original Issue

{issue_content}

## Changes Made (git diff)

```diff
{diff}
```

Now write the PR description to {cwd}/.pr-description.md using the Write tool."""


def get_options(cwd: str | None = None, max_turns: int = 10, resume: str | None = None, allowed_tools: list[str] | None = FILE_EDITING_TOOLS) -> ClaudeAgentOptions:
    """Get Claude agent options with file editing tools.

    Args:
        cwd: Working directory
        max_turns: Maximum number of turns
        resume: Session ID to resume from
        allowed_tools: List of allowed tools, or None for unrestricted. Defaults to FILE_EDITING_TOOLS.
    """
    options_dict = {
        "permission_mode": "bypassPermissions",
        "max_turns": max_turns,
        "cwd": Path(cwd) if cwd else None,
        "resume": resume,
    }

    # Only set allowed_tools if it's not None
    if allowed_tools is not None:
        options_dict["allowed_tools"] = allowed_tools

    return ClaudeAgentOptions(**options_dict)


async def run_claude(prompt: str, cwd: str | None = None, max_turns: int = 10, resume: str | None = None, allowed_tools: list[str] | None = FILE_EDITING_TOOLS):
    """Run Claude with the given prompt. Returns an async iterator of messages.

    Args:
        prompt: The prompt to run
        cwd: Working directory
        max_turns: Maximum number of turns
        resume: Session ID to resume from
        allowed_tools: List of allowed tools, or None for unrestricted. Defaults to FILE_EDITING_TOOLS.
    """
    options = get_options(cwd, max_turns, resume, allowed_tools)
    async for message in query(prompt=prompt, options=options):
        yield message


def is_complete(cwd: str) -> bool:
    """Check if the completion marker file exists."""
    marker_path = Path(cwd) / COMPLETION_MARKER
    return marker_path.exists()


def cleanup_completion_marker(cwd: str) -> None:
    """Remove the completion marker file if it exists."""
    marker_path = Path(cwd) / COMPLETION_MARKER
    if marker_path.exists():
        marker_path.unlink()


def extract_session_id(message) -> str | None:
    """Extract session_id from a SystemMessage init message."""
    if isinstance(message, SystemMessage) and message.subtype == "init":
        return message.data.get("session_id")
    return None


def extract_turn_summary(messages: list) -> str:
    """Extract a concise summary of turns from messages.

    Focuses on tool uses and key text responses, omitting verbose details.
    """
    summary_parts = []

    for i, message in enumerate(messages, 1):
        if isinstance(message, AssistantMessage):
            # Extract tool uses
            if hasattr(message, 'tool_uses') and message.tool_uses:
                for tool_use in message.tool_uses:
                    tool_name = tool_use.get('name', 'Unknown')
                    # Add concise description of tool use
                    if tool_name in ['Read', 'Edit', 'Write', 'Glob', 'Grep']:
                        params = tool_use.get('params', {})
                        if tool_name == 'Read':
                            file_path = params.get('file_path', '')
                            if file_path:
                                file_name = file_path.split('/')[-1]
                                summary_parts.append(f"- Read {file_name}")
                        elif tool_name == 'Write':
                            file_path = params.get('file_path', '')
                            if file_path:
                                file_name = file_path.split('/')[-1]
                                summary_parts.append(f"- Created {file_name}")
                        elif tool_name == 'Edit':
                            file_path = params.get('file_path', '')
                            if file_path:
                                file_name = file_path.split('/')[-1]
                                summary_parts.append(f"- Modified {file_name}")
                        elif tool_name == 'Glob':
                            pattern = params.get('pattern', '')
                            summary_parts.append(f"- Searched for files: {pattern}")
                        elif tool_name == 'Grep':
                            pattern = params.get('pattern', '')
                            summary_parts.append(f"- Searched code: {pattern}")

            # Extract key text (first 100 chars)
            if hasattr(message, 'text') and message.text:
                text_snippet = message.text[:100].replace('\n', ' ').strip()
                if text_snippet:
                    summary_parts.append(f"- Note: {text_snippet}...")

    return "\n".join(summary_parts) if summary_parts else "No significant activity recorded"


def build_chunk_summary_prompt(
    title: str,
    body: str,
    chunk_messages: list,
    chunk_num: int,
    cwd: str,
) -> str:
    """Build a prompt for summarizing what was done in a chunk.

    Returns a prompt that asks Claude to summarize the chunk's work.
    """
    turn_summary = extract_turn_summary(chunk_messages)

    return f"""You are analyzing the progress of an AI agent working on a task. Based on the activity log below, provide a concise summary.

# Original Task
**{title}**

{body if body else '(No additional description)'}

# Activity in Chunk {chunk_num + 1}
{turn_summary}

# Your Task
Provide a brief summary with two sections:

## ✅ Completed This Chunk
List 2-4 bullet points of what was accomplished in this chunk. Be specific but concise.

## 📋 Remaining Work
List 1-3 bullet points of what still needs to be done. If the task appears complete, say "All work appears to be complete."

Keep your response concise and focused. Use bullet points only, no additional explanations."""


def build_final_summary_prompt(
    title: str,
    body: str,
    all_chunk_summaries: list[str],
    cwd: str,
) -> str:
    """Build a prompt for generating a final comprehensive summary.

    Takes all chunk summaries and creates an overall summary.
    """
    chunks_text = "\n\n".join([
        f"### Chunk {i + 1}\n{summary}"
        for i, summary in enumerate(all_chunk_summaries)
    ])

    return f"""You are creating a final summary of an AI agent's work on a task.

# Original Task
**{title}**

{body if body else '(No additional description)'}

# Progress Across All Chunks
{chunks_text}

# Your Task
Provide a comprehensive final summary:

## 📊 Summary of All Changes
Provide 3-5 bullet points summarizing the key changes made across all chunks. Focus on the overall outcome.

## 🎯 Completion Status
State whether the task was fully completed or if there are remaining items. Be factual and concise.

Keep your response clear and focused."""


async def run_summary_agent(prompt: str, cwd: str, max_turns: int = 3) -> str:
    """Run a quick agent session to generate a summary.

    Uses a limited number of turns to quickly generate a summary.
    Returns the summary text or an error message.

    Note: This function uses unrestricted tools (allowed_tools=None) to allow
    the agent to generate plain text responses without being forced to use
    file editing tools.
    """
    try:
        summary_text = ""
        # Use allowed_tools=None to allow unrestricted text generation
        async for message in run_claude(prompt, cwd, max_turns, allowed_tools=None):
            # Extract text from assistant messages
            if isinstance(message, AssistantMessage):
                # Extract text from content blocks
                for block in message.content:
                    if hasattr(block, 'text') and block.text:
                        summary_text += block.text

        return summary_text.strip() if summary_text else "Summary generation did not produce output."
    except Exception as e:
        return f"Error generating summary: {e}"


async def run_claude_chunked(
    title: str,
    body: str,
    cwd: str | None = None,
    turns_per_chunk: int = DEFAULT_TURNS_PER_CHUNK,
    max_chunks: int = DEFAULT_MAX_CHUNKS,
    on_chunk_complete: Callable[[int, str], Awaitable[None]] | None = None,
    on_final_complete: Callable[[list[str]], Awaitable[None]] | None = None,
):
    """Run Claude in chunks, allowing more turns for complex tasks.

    Uses session resume to continue the conversation across chunks,
    preserving context from previous turns.

    Yields messages from each chunk. Stops when:
    - The completion marker file is created (agent signals done)
    - max_chunks is reached

    Args:
        title: Task title
        body: Task description
        cwd: Working directory
        turns_per_chunk: Number of turns per chunk
        max_chunks: Maximum number of chunks
        on_chunk_complete: Optional callback called after each chunk with (chunk_num, summary)
        on_final_complete: Optional callback called at end with list of all summaries
    """
    if cwd is None:
        cwd = os.getcwd()

    # Clean up any leftover completion marker from previous runs
    cleanup_completion_marker(cwd)

    session_id = None
    all_chunk_summaries = []

    for chunk_num in range(max_chunks):
        # Build prompt - initial or continuation
        if chunk_num == 0:
            prompt = build_prompt(title, body, cwd)
        else:
            prompt = build_continuation_prompt(title, body, cwd)

        # Collect messages from this chunk
        chunk_messages = []

        # Run this chunk, resuming session if we have one
        async for message in run_claude(prompt, cwd, turns_per_chunk, resume=session_id):
            # Capture session_id from init message
            if session_id is None:
                session_id = extract_session_id(message)
            chunk_messages.append(message)
            yield message

        # Generate summary for this chunk
        if on_chunk_complete:
            try:
                summary_prompt = build_chunk_summary_prompt(
                    title, body, chunk_messages, chunk_num, cwd
                )
                summary = await run_summary_agent(summary_prompt, cwd)
                all_chunk_summaries.append(summary)
                await on_chunk_complete(chunk_num, summary)
            except Exception as e:
                print(f"Error generating/posting chunk summary: {e}")
                # Continue execution even if summary fails

        # Check if agent signalled completion
        if is_complete(cwd):
            cleanup_completion_marker(cwd)
            # Generate final summary
            if on_final_complete and all_chunk_summaries:
                try:
                    final_prompt = build_final_summary_prompt(
                        title, body, all_chunk_summaries, cwd
                    )
                    final_summary = await run_summary_agent(final_prompt, cwd)
                    await on_final_complete(all_chunk_summaries)
                except Exception as e:
                    print(f"Error generating/posting final summary: {e}")
            return

    # If we get here, we hit max_chunks without completion
    # Still generate final summary
    if on_final_complete and all_chunk_summaries:
        try:
            final_prompt = build_final_summary_prompt(
                title, body, all_chunk_summaries, cwd
            )
            final_summary = await run_summary_agent(final_prompt, cwd)
            await on_final_complete(all_chunk_summaries)
        except Exception as e:
            print(f"Error generating/posting final summary: {e}")


def build_plan_prompt(title: str, body: str, cwd: str | None = None) -> str:
    """Build prompt for generating an implementation plan."""
    if not title:
        raise ValueError("Title is required")

    # Allow empty body - title alone is sufficient
    if body is None:
        body = ""

    if cwd is None:
        cwd = os.getcwd()

    plan_file = f"{cwd}/.plan.md"

    # Handle empty body gracefully
    issue_content = f"# {title}"
    if body and body.strip():
        issue_content = f"{issue_content}\n\n{body}"

    return f"""You are a planning agent. Your task is to analyze the issue and create a detailed implementation plan.

Working directory: {cwd}

IMPORTANT: You MUST use the file editing tools (Read, Edit, Write, Glob, Grep) to explore the codebase and create the plan.

Steps to follow:
1. Use Glob and Grep to explore the codebase structure
2. Use Read to examine relevant files
3. Analyze the issue requirements
4. Create a detailed implementation plan in markdown format
5. Write the plan to: {plan_file}

The plan should include:
- **Overview**: Brief summary of what needs to be done
- **Files to modify/create**: List of files that will be changed or created
- **Implementation steps**: Numbered list of specific steps to implement the feature
- **Testing approach**: How to verify the changes work
- **Potential risks/considerations**: Any gotchas or edge cases to watch out for

Do NOT implement the changes - only create the plan.

All file paths must be absolute paths within the working directory.

When you have finished creating the plan, write it to: {plan_file}

## Issue to plan for:

{issue_content}"""


async def run_claude_plan(title: str, body: str, cwd: str | None = None, max_turns: int = 15):
    """Run Claude to generate an implementation plan.

    Returns an async iterator of messages. The plan will be written to .plan.md
    """
    if cwd is None:
        cwd = os.getcwd()

    prompt = build_plan_prompt(title, body, cwd)

    # Run with limited turns - planning should be faster than implementation
    async for message in run_claude(prompt, cwd, max_turns):
        yield message


PLAN_FILE = ".plan.md"
DEFAULT_PLAN_TURNS_PER_CHUNK = 10
DEFAULT_PLAN_MAX_CHUNKS = 3


def is_plan_complete(cwd: str) -> bool:
    """Check if the plan file exists (signals planning is done)."""
    plan_path = Path(cwd) / PLAN_FILE
    return plan_path.exists()


def build_plan_continuation_prompt(title: str, body: str, cwd: str) -> str:
    """Build a continuation prompt for when the planning agent needs more turns."""
    plan_file = f"{cwd}/{PLAN_FILE}"

    # Handle empty body gracefully
    issue_content = f"# {title}"
    if body and body.strip():
        issue_content = f"{issue_content}\n\n{body}"

    return f"""Continue working on the implementation plan. You were exploring the codebase but ran out of turns.

Review what you've learned so far and continue creating the plan.

Working directory: {cwd}

Remember:
- Use Glob, Grep, and Read to explore the codebase
- When you have enough information, write the plan to: {plan_file}
- The plan should include: Overview, Files to modify/create, Implementation steps, Testing approach, Potential risks

## Issue to plan for:

{issue_content}"""


async def run_claude_plan_chunked(
    title: str,
    body: str,
    cwd: str | None = None,
    turns_per_chunk: int = DEFAULT_PLAN_TURNS_PER_CHUNK,
    max_chunks: int = DEFAULT_PLAN_MAX_CHUNKS,
    on_chunk_complete: Callable[[int, str], Awaitable[None]] | None = None,
    on_final_complete: Callable[[list[str]], Awaitable[None]] | None = None,
):
    """Run Claude planning in chunks, allowing more turns for complex exploration.

    Uses session resume to continue the conversation across chunks,
    preserving context from previous turns.

    Yields messages from each chunk. Stops when:
    - The .plan.md file is created (agent signals done)
    - max_chunks is reached

    Args:
        title: Task title
        body: Task description
        cwd: Working directory
        turns_per_chunk: Number of turns per chunk
        max_chunks: Maximum number of chunks
        on_chunk_complete: Optional callback called after each chunk with (chunk_num, summary)
        on_final_complete: Optional callback called at end with list of all summaries
    """
    if cwd is None:
        cwd = os.getcwd()

    session_id = None
    all_chunk_summaries = []

    for chunk_num in range(max_chunks):
        # Build prompt - initial or continuation
        if chunk_num == 0:
            prompt = build_plan_prompt(title, body, cwd)
        else:
            prompt = build_plan_continuation_prompt(title, body, cwd)

        # Collect messages from this chunk
        chunk_messages = []

        # Run this chunk, resuming session if we have one
        async for message in run_claude(prompt, cwd, turns_per_chunk, resume=session_id):
            # Capture session_id from init message
            if session_id is None:
                session_id = extract_session_id(message)
            chunk_messages.append(message)
            yield message

        # Generate summary for this chunk
        if on_chunk_complete:
            try:
                summary_prompt = build_chunk_summary_prompt(
                    title, body, chunk_messages, chunk_num, cwd
                )
                summary = await run_summary_agent(summary_prompt, cwd)
                all_chunk_summaries.append(summary)
                await on_chunk_complete(chunk_num, summary)
            except Exception as e:
                print(f"Error generating/posting chunk summary: {e}")
                # Continue execution even if summary fails

        # Check if agent created the plan file
        if is_plan_complete(cwd):
            # Generate final summary
            if on_final_complete and all_chunk_summaries:
                try:
                    final_prompt = build_final_summary_prompt(
                        title, body, all_chunk_summaries, cwd
                    )
                    final_summary = await run_summary_agent(final_prompt, cwd)
                    await on_final_complete(all_chunk_summaries)
                except Exception as e:
                    print(f"Error generating/posting final summary: {e}")
            return

    # If we get here, we hit max_chunks without completing the plan
    # Still generate final summary
    if on_final_complete and all_chunk_summaries:
        try:
            final_prompt = build_final_summary_prompt(
                title, body, all_chunk_summaries, cwd
            )
            final_summary = await run_summary_agent(final_prompt, cwd)
            await on_final_complete(all_chunk_summaries)
        except Exception as e:
            print(f"Error generating/posting final summary: {e}")
