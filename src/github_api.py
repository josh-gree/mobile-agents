"""GitHub API helper functions for posting issue comments."""

import httpx
from typing import Optional


async def post_issue_comment(
    owner: str,
    repo: str,
    issue_number: int,
    body: str,
    token: str,
    timeout: float = 30.0,
) -> bool:
    """Post a comment on a GitHub issue.

    Args:
        owner: Repository owner (username or organization)
        repo: Repository name
        issue_number: Issue number to comment on
        body: Comment body (markdown supported)
        token: GitHub API token
        timeout: Request timeout in seconds

    Returns:
        True if comment was posted successfully, False otherwise
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments"

    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    payload = {"body": body}

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return True
    except httpx.HTTPStatusError as e:
        print(f"Error posting GitHub comment: HTTP {e.response.status_code}")
        print(f"Response: {e.response.text}")
        return False
    except httpx.RequestError as e:
        print(f"Error posting GitHub comment: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error posting GitHub comment: {e}")
        return False


async def get_issue(
    owner: str,
    repo: str,
    issue_number: int,
    token: str,
    timeout: float = 30.0,
) -> Optional[dict]:
    """Fetch issue details from GitHub.

    Args:
        owner: Repository owner (username or organization)
        repo: Repository name
        issue_number: Issue number to fetch
        token: GitHub API token
        timeout: Request timeout in seconds

    Returns:
        Issue data as dict if successful, None otherwise
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"

    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        print(f"Error fetching GitHub issue: HTTP {e.response.status_code}")
        return None
    except httpx.RequestError as e:
        print(f"Error fetching GitHub issue: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error fetching GitHub issue: {e}")
        return None
