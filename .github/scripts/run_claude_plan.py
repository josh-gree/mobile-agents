#!/usr/bin/env python3
"""Entry point for running Claude agent to generate a plan from GitHub Actions."""

import asyncio
import json
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from claude_runner import run_claude_plan


async def main():
    issue_title = os.environ.get("ISSUE_TITLE")
    issue_body = os.environ.get("ISSUE_BODY")
    api_key = os.environ.get("ANTHROPIC_API_KEY")

    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable is required", file=sys.stderr)
        sys.exit(1)

    if not issue_title:
        print("Error: ISSUE_TITLE environment variable is required", file=sys.stderr)
        sys.exit(1)

    # Allow empty body if title is provided
    if issue_body is None:
        issue_body = ""

    try:
        cwd = os.getcwd()

        # Run plan generation with limited turns (planning should be quick)
        async for message in run_claude_plan(issue_title, issue_body, cwd):
            print(json.dumps(message, default=str))

    except Exception as e:
        print(f"Error running Claude plan: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
