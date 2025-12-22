#!/usr/bin/env python3
"""Generate PR description using Claude."""

import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from claude_runner import build_pr_description_prompt, run_claude


async def main():
    issue_title = os.environ.get("ISSUE_TITLE")
    issue_body = os.environ.get("ISSUE_BODY")
    diff = os.environ.get("GIT_DIFF", "")
    api_key = os.environ.get("ANTHROPIC_API_KEY")

    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable is required", file=sys.stderr)
        sys.exit(1)

    if not issue_title or not issue_body:
        print("Error: ISSUE_TITLE and ISSUE_BODY environment variables are required", file=sys.stderr)
        sys.exit(1)

    try:
        cwd = os.getcwd()
        prompt = build_pr_description_prompt(issue_title, issue_body, diff, cwd)

        # Use fewer turns for this simpler task
        async for message in run_claude(prompt, cwd, max_turns=3):
            print(json.dumps(message, default=str))

    except Exception as e:
        print(f"Error generating PR description: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
