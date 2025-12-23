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

    if cwd is None:
        cwd = os.getcwd()

    # Allow empty body
    if body is None:
        body = ""

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

    return f"{system_instructions}\n\n# {title}\n\n{body}"


def build_continuation_prompt(title: str, body: str, cwd: str) -> str:
    """Build a continuation prompt for when the agent needs more turns."""
    completion_marker_path = f"{cwd}/{COMPLETION_MARKER}"

    return f"""Continue working on the task below. You were working on this but ran out of turns.

Review what has been done so far and continue from where you left off.

Working directory: {cwd}

Remember:
- Use the file editing tools to make changes
- When FULLY COMPLETE, write "DONE" to: {completion_marker_path}

# {title}

{body}"""


def build_pr_description_prompt(title: str, body: str, diff: str, issue_number: int, cwd: str | None = None) -> str:
    """Build prompt for generating PR description."""
    if cwd is None:
        cwd = os.getcwd()

    # Allow empty body
    if body is None:
        body = ""

    # Build issue section based on whether body exists
    if body.strip():
        issue_section = f"""## Original Issue

### {title}

{body}"""
    else:
        issue_section = f"""## Original Issue

### {title}

(No additional details provided)"""

    return f"""You are writing a pull request description. Based on the issue and the git diff of changes made, write a clear PR description.

Working directory: {cwd}

Write the PR description to: {cwd}/.pr-description.md

The description should:
1. Start with "Closes #{issue_number}" on its own line
2. Have a "## Summary" section with 2-3 bullet points describing what was done
3. Be concise and factual

Do NOT include a test plan section.

{issue_section}

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
