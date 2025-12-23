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
    has_plan = os.environ.get("HAS_PLAN", "not-found")

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

        # If there's a plan, append it to the issue body with clear implementation instructions
        if has_plan == "found":
            plan_file = os.path.join(cwd, ".plan-context.md")
            if os.path.exists(plan_file):
                with open(plan_file, "r") as f:
                    plan_content = f.read()
                issue_body = f"""{issue_body}

## Implementation Plan

{plan_content}

---

**IMPORTANT**: You must IMPLEMENT this plan by making actual code changes using the file editing tools.
Do not just describe what should be done - use Edit, Write, Read, Glob, and Grep to make the changes.
Follow the implementation steps outlined in the plan above."""
                print("Found and included implementation plan in context")

        # Run in chunks of 10 turns, up to 5 chunks (50 turns max)
        async for message in run_claude_chunked(issue_title, issue_body, cwd):
            print(json.dumps(message, default=str))

    except Exception as e:
        print(f"Error running Claude: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
