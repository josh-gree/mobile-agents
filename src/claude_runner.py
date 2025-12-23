"""Claude Agent SDK runner for GitHub Actions."""

import os
from pathlib import Path

from claude_agent_sdk import query, ClaudeAgentOptions
from claude_agent_sdk.types import SystemMessage


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


def get_options(cwd: str | None = None, max_turns: int = 10, resume: str | None = None) -> ClaudeAgentOptions:
    """Get Claude agent options with file editing tools."""
    return ClaudeAgentOptions(
        allowed_tools=FILE_EDITING_TOOLS,
        permission_mode="bypassPermissions",
        max_turns=max_turns,
        cwd=Path(cwd) if cwd else None,
        resume=resume,
    )


async def run_claude(prompt: str, cwd: str | None = None, max_turns: int = 10, resume: str | None = None):
    """Run Claude with the given prompt. Returns an async iterator of messages."""
    options = get_options(cwd, max_turns, resume)
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


async def run_claude_chunked(
    title: str,
    body: str,
    cwd: str | None = None,
    turns_per_chunk: int = DEFAULT_TURNS_PER_CHUNK,
    max_chunks: int = DEFAULT_MAX_CHUNKS,
):
    """Run Claude in chunks, allowing more turns for complex tasks.

    Uses session resume to continue the conversation across chunks,
    preserving context from previous turns.

    Yields messages from each chunk. Stops when:
    - The completion marker file is created (agent signals done)
    - max_chunks is reached
    """
    if cwd is None:
        cwd = os.getcwd()

    # Clean up any leftover completion marker from previous runs
    cleanup_completion_marker(cwd)

    session_id = None

    for chunk_num in range(max_chunks):
        # Build prompt - initial or continuation
        if chunk_num == 0:
            prompt = build_prompt(title, body, cwd)
        else:
            prompt = build_continuation_prompt(title, body, cwd)

        # Run this chunk, resuming session if we have one
        async for message in run_claude(prompt, cwd, turns_per_chunk, resume=session_id):
            # Capture session_id from init message
            if session_id is None:
                session_id = extract_session_id(message)
            yield message

        # Check if agent signalled completion
        if is_complete(cwd):
            cleanup_completion_marker(cwd)
            return

    # If we get here, we hit max_chunks without completion


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
):
    """Run Claude planning in chunks, allowing more turns for complex exploration.

    Uses session resume to continue the conversation across chunks,
    preserving context from previous turns.

    Yields messages from each chunk. Stops when:
    - The .plan.md file is created (agent signals done)
    - max_chunks is reached
    """
    if cwd is None:
        cwd = os.getcwd()

    session_id = None

    for chunk_num in range(max_chunks):
        # Build prompt - initial or continuation
        if chunk_num == 0:
            prompt = build_plan_prompt(title, body, cwd)
        else:
            prompt = build_plan_continuation_prompt(title, body, cwd)

        # Run this chunk, resuming session if we have one
        async for message in run_claude(prompt, cwd, turns_per_chunk, resume=session_id):
            # Capture session_id from init message
            if session_id is None:
                session_id = extract_session_id(message)
            yield message

        # Check if agent created the plan file
        if is_plan_complete(cwd):
            return

    # If we get here, we hit max_chunks without completing the plan
