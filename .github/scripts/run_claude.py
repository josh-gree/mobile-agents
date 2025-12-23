#!/usr/bin/env python3
"""Entry point for running Claude agent from GitHub Actions."""

import asyncio
import json
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from claude_runner import run_claude_chunked
from github_api import post_issue_comment


async def main():
    issue_title = os.environ.get("ISSUE_TITLE")
    issue_body = os.environ.get("ISSUE_BODY")
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    has_plan = os.environ.get("HAS_PLAN", "not-found")

    # GitHub API parameters (optional - for posting progress comments)
    issue_number = os.environ.get("ISSUE_NUMBER")
    github_token = os.environ.get("GITHUB_TOKEN")
    github_repository = os.environ.get("GITHUB_REPOSITORY")  # format: "owner/repo"

    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable is required", file=sys.stderr)
        sys.exit(1)

    if not issue_title:
        print("Error: ISSUE_TITLE environment variable is required", file=sys.stderr)
        sys.exit(1)

    # Allow empty body if title is provided
    if issue_body is None:
        issue_body = ""

    # Parse GitHub repository info if available
    github_enabled = False
    repo_owner = None
    repo_name = None
    if issue_number and github_token and github_repository:
        try:
            repo_owner, repo_name = github_repository.split("/")
            issue_number = int(issue_number)
            github_enabled = True
            print(f"GitHub integration enabled for {repo_owner}/{repo_name}#{issue_number}")
        except (ValueError, AttributeError):
            print("Warning: Could not parse GitHub repository info, progress comments disabled")

    # Define callback for chunk completion
    async def on_chunk_complete(chunk_num: int, summary: str):
        """Post a progress update comment to the GitHub issue."""
        if not github_enabled:
            return

        comment_body = f"""## 🔄 Progress Update - Chunk {chunk_num + 1}

{summary}

---
*This is an automated progress update. The agent is still working...*"""

        success = await post_issue_comment(
            repo_owner, repo_name, issue_number, comment_body, github_token
        )
        if success:
            print(f"Posted progress update for chunk {chunk_num + 1}")
        else:
            print(f"Failed to post progress update for chunk {chunk_num + 1}")

    # Define callback for final completion
    async def on_final_complete(all_summaries: list[str]):
        """Post a final summary comment to the GitHub issue."""
        if not github_enabled:
            return

        num_chunks = len(all_summaries)

        comment_body = f"""## ✨ Implementation Complete

The agent has finished working on this issue after {num_chunks} chunk(s).

### 🎯 Total Progress
- **Chunks completed:** {num_chunks}
- **Status:** All requested changes have been implemented

*Review the changes in the pull request and verify that everything works as expected.*"""

        success = await post_issue_comment(
            repo_owner, repo_name, issue_number, comment_body, github_token
        )
        if success:
            print("Posted final completion summary")
        else:
            print("Failed to post final completion summary")

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
        # Pass callbacks if GitHub integration is enabled
        async for message in run_claude_chunked(
            issue_title,
            issue_body,
            cwd,
            on_chunk_complete=on_chunk_complete if github_enabled else None,
            on_final_complete=on_final_complete if github_enabled else None,
        ):
            print(json.dumps(message, default=str))

    except Exception as e:
        print(f"Error running Claude: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
