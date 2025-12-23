#!/usr/bin/env python3
"""Entry point for running Claude agent from GitHub Actions."""

import asyncio
import json
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from claude_runner import run_claude_chunked


async def main():
    issue_title = os.environ.get("ISSUE_TITLE")
    issue_body = os.environ.get("ISSUE_BODY")
    api_key = os.environ.get("ANTHROPIC_API_KEY")

    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable is required", file=sys.stderr)
        sys.exit(1)

    if not issue_title or not issue_body:
        print("Error: ISSUE_TITLE and ISSUE_BODY environment variables are required", file=sys.stderr)
        sys.exit(1)

    try:
        cwd = os.getcwd()

        # Run in chunks of 10 turns, up to 5 chunks (50 turns max)
        async for message in run_claude_chunked(issue_title, issue_body, cwd):
            print(json.dumps(message, default=str))

    except Exception as e:
        print(f"Error running Claude: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
