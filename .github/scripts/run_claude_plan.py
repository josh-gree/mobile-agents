#!/usr/bin/env python3
"""Entry point for running Claude agent to generate a plan from GitHub Actions."""

import asyncio
import json
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from claude_runner import run_claude_plan_chunked
from github_api import post_issue_comment


async def main():
    issue_title = os.environ.get("ISSUE_TITLE")
    issue_body = os.environ.get("ISSUE_BODY")
    api_key = os.environ.get("ANTHROPIC_API_KEY")

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
        """Post a planning progress update comment to the GitHub issue."""
        if not github_enabled:
            return

        comment_body = f"""## 🔍 Planning Progress - Chunk {chunk_num + 1}

{summary}

---
*This is an automated progress update. The planning agent is still exploring the codebase...*"""

        success = await post_issue_comment(
            repo_owner, repo_name, issue_number, comment_body, github_token
        )
        if success:
            print(f"Posted planning progress update for chunk {chunk_num + 1}")
        else:
            print(f"Failed to post planning progress update for chunk {chunk_num + 1}")

    # Define callback for final completion
    async def on_final_complete(all_summaries: list[str]):
        """Post a final planning summary comment to the GitHub issue."""
        if not github_enabled:
            return

        num_chunks = len(all_summaries)

        comment_body = f"""## 🗺️ Planning Complete

The planning agent has finished exploring the codebase after {num_chunks} chunk(s).

### 🎯 Planning Progress
- **Chunks completed:** {num_chunks}
- **Status:** Implementation plan has been generated

*The detailed plan has been posted in a separate comment. Review it and use `/apply` to start implementation.*"""

        success = await post_issue_comment(
            repo_owner, repo_name, issue_number, comment_body, github_token
        )
        if success:
            print("Posted final planning summary")
        else:
            print("Failed to post final planning summary")

    try:
        cwd = os.getcwd()

        # Run plan generation in chunks (10 turns per chunk, up to 3 chunks = 30 turns max)
        # Pass callbacks if GitHub integration is enabled
        async for message in run_claude_plan_chunked(
            issue_title,
            issue_body,
            cwd,
            on_chunk_complete=on_chunk_complete if github_enabled else None,
            on_final_complete=on_final_complete if github_enabled else None,
        ):
            print(json.dumps(message, default=str))

    except Exception as e:
        print(f"Error running Claude plan: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
