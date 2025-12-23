"""Tests for github_api module."""

import pytest
from unittest.mock import patch, AsyncMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from github_api import post_issue_comment, get_issue


@pytest.fixture
def mock_httpx_client():
    """Mock httpx.AsyncClient for testing."""
    with patch("github_api.httpx.AsyncClient") as mock:
        yield mock


async def test_post_issue_comment_success(mock_httpx_client):
    """Test successful comment posting."""
    # Setup mock
    mock_response = AsyncMock()
    mock_response.status_code = 201
    mock_response.raise_for_status = AsyncMock()

    mock_client_instance = AsyncMock()
    mock_client_instance.post = AsyncMock(return_value=mock_response)
    mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
    mock_client_instance.__aexit__ = AsyncMock(return_value=None)

    mock_httpx_client.return_value = mock_client_instance

    # Call function
    result = await post_issue_comment(
        owner="test-owner",
        repo="test-repo",
        issue_number=123,
        body="Test comment",
        token="test-token",
    )

    # Verify
    assert result is True
    mock_client_instance.post.assert_called_once()


async def test_post_issue_comment_failure(mock_httpx_client):
    """Test comment posting with HTTP error."""
    import httpx

    # Setup mock to raise HTTPStatusError
    mock_response = AsyncMock()
    mock_response.status_code = 404
    mock_response.text = "Not Found"
    mock_response.raise_for_status = AsyncMock(
        side_effect=httpx.HTTPStatusError("404", request=None, response=mock_response)
    )

    mock_client_instance = AsyncMock()
    mock_client_instance.post = AsyncMock(return_value=mock_response)
    mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
    mock_client_instance.__aexit__ = AsyncMock(return_value=None)

    mock_httpx_client.return_value = mock_client_instance

    # Call function
    result = await post_issue_comment(
        owner="test-owner",
        repo="test-repo",
        issue_number=123,
        body="Test comment",
        token="test-token",
    )

    # Verify
    assert result is False


async def test_get_issue_success(mock_httpx_client):
    """Test successful issue fetch."""
    # Setup mock
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = AsyncMock(return_value={"number": 123, "title": "Test Issue"})
    mock_response.raise_for_status = AsyncMock()

    mock_client_instance = AsyncMock()
    mock_client_instance.get = AsyncMock(return_value=mock_response)
    mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
    mock_client_instance.__aexit__ = AsyncMock(return_value=None)

    mock_httpx_client.return_value = mock_client_instance

    # Call function
    result = await get_issue(
        owner="test-owner",
        repo="test-repo",
        issue_number=123,
        token="test-token",
    )

    # Verify
    assert result is not None
    assert result["number"] == 123
    assert result["title"] == "Test Issue"


async def test_get_issue_failure(mock_httpx_client):
    """Test issue fetch with HTTP error."""
    import httpx

    # Setup mock to raise HTTPStatusError
    mock_response = AsyncMock()
    mock_response.status_code = 404
    mock_response.raise_for_status = AsyncMock(
        side_effect=httpx.HTTPStatusError("404", request=None, response=mock_response)
    )

    mock_client_instance = AsyncMock()
    mock_client_instance.get = AsyncMock(return_value=mock_response)
    mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
    mock_client_instance.__aexit__ = AsyncMock(return_value=None)

    mock_httpx_client.return_value = mock_client_instance

    # Call function
    result = await get_issue(
        owner="test-owner",
        repo="test-repo",
        issue_number=123,
        token="test-token",
    )

    # Verify
    assert result is None
