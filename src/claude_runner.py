"""Claude Agent SDK runner for GitHub Actions."""

import os
from pathlib import Path

from claude_agent_sdk import query, ClaudeAgentOptions


FILE_EDITING_TOOLS = ["Read", "Edit", "Write", "Glob", "Grep"]


def build_prompt(title: str, body: str, cwd: str | None = None) -> str:
    """Build the prompt for Claude with system instructions."""
    if not title or not body:
        raise ValueError("Title and body are required")

    if cwd is None:
        cwd = os.getcwd()

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

Do NOT just describe what changes should be made - actually make them using the tools."""

    return f"{system_instructions}\n\n# {title}\n\n{body}"


def get_options(cwd: str | None = None) -> ClaudeAgentOptions:
    """Get Claude agent options with file editing tools."""
    return ClaudeAgentOptions(
        allowed_tools=FILE_EDITING_TOOLS,
        permission_mode="bypassPermissions",
        max_turns=10,
        cwd=Path(cwd) if cwd else None,
    )


async def run_claude(prompt: str, cwd: str | None = None):
    """Run Claude with the given prompt. Returns an async iterator of messages."""
    options = get_options(cwd)
    async for message in query(prompt=prompt, options=options):
        yield message
