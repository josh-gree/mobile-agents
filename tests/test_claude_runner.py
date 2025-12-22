"""Tests for claude_runner module."""

import pytest
from unittest.mock import patch

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from claude_runner import build_prompt, get_options, run_claude, FILE_EDITING_TOOLS


# build_prompt tests

def test_build_prompt_includes_system_instructions_and_title_body():
    result = build_prompt("My Title", "Some body text", "/test/dir")
    assert "# My Title" in result
    assert "Some body text" in result
    assert "You are a code editing agent" in result
    assert "MUST use the file editing tools" in result


def test_build_prompt_includes_working_directory():
    result = build_prompt("Title", "Body", "/my/working/dir")
    assert "Working directory: /my/working/dir" in result
    assert "/my/working/dir/hello.txt" in result


def test_build_prompt_handles_multiline_body():
    body = "Line 1\nLine 2\nLine 3"
    result = build_prompt("Title", body, "/test")
    assert "# Title" in result
    assert "Line 1\nLine 2\nLine 3" in result


def test_build_prompt_raises_when_title_missing():
    with pytest.raises(ValueError, match="Title and body are required"):
        build_prompt("", "body")

    with pytest.raises(ValueError, match="Title and body are required"):
        build_prompt(None, "body")


def test_build_prompt_raises_when_body_missing():
    with pytest.raises(ValueError, match="Title and body are required"):
        build_prompt("title", "")

    with pytest.raises(ValueError, match="Title and body are required"):
        build_prompt("title", None)


# get_options tests

def test_get_options_returns_file_editing_tools():
    options = get_options("/test/dir")
    assert options.allowed_tools == FILE_EDITING_TOOLS


def test_get_options_sets_bypass_permissions_mode():
    options = get_options()
    assert options.permission_mode == "bypassPermissions"


def test_get_options_sets_max_turns():
    options = get_options()
    assert options.max_turns == 10


# run_claude tests

async def test_run_claude_yields_messages():
    mock_messages = [{"type": "message", "content": "Hello"}]

    async def mock_query(*args, **kwargs):
        for msg in mock_messages:
            yield msg

    with patch("claude_runner.query", mock_query):
        messages = []
        async for msg in run_claude("Test prompt"):
            messages.append(msg)

        assert messages == mock_messages


async def test_run_claude_yields_all_messages():
    mock_messages = [
        {"type": "message", "content": "First"},
        {"type": "message", "content": "Second"},
        {"type": "message", "content": "Third"},
    ]

    async def mock_query(*args, **kwargs):
        for msg in mock_messages:
            yield msg

    with patch("claude_runner.query", mock_query):
        messages = []
        async for msg in run_claude("Test prompt"):
            messages.append(msg)

        assert len(messages) == 3
        assert messages[0]["content"] == "First"
        assert messages[2]["content"] == "Third"
