"""Tests for claude_runner module."""

import pytest
from unittest.mock import patch
import tempfile
from pathlib import Path

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from claude_runner import (
    build_prompt,
    build_pr_description_prompt,
    build_continuation_prompt,
    get_options,
    run_claude,
    run_claude_chunked,
    is_complete,
    cleanup_completion_marker,
    FILE_EDITING_TOOLS,
    COMPLETION_MARKER,
)


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


# build_pr_description_prompt tests

def test_build_pr_description_prompt_includes_issue_and_diff():
    result = build_pr_description_prompt("Fix bug", "Fix the login bug", "+added line", 123, "/test/dir")
    assert "Fix bug" in result
    assert "Fix the login bug" in result
    assert "+added line" in result
    assert ".pr-description.md" in result
    assert "Closes #123" in result


def test_build_pr_description_prompt_includes_working_directory():
    result = build_pr_description_prompt("Title", "Body", "diff", 456, "/my/dir")
    assert "/my/dir/.pr-description.md" in result


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


def test_get_options_accepts_custom_max_turns():
    options = get_options(max_turns=5)
    assert options.max_turns == 5


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


# build_prompt completion signal tests

def test_build_prompt_includes_completion_signal():
    result = build_prompt("Title", "Body", "/test/dir")
    assert "COMPLETION SIGNAL" in result
    assert ".claude-complete" in result
    assert "DONE" in result


# build_continuation_prompt tests

def test_build_continuation_prompt_includes_task():
    result = build_continuation_prompt("My Title", "My Body", "/test/dir")
    assert "# My Title" in result
    assert "My Body" in result


def test_build_continuation_prompt_includes_continue_message():
    result = build_continuation_prompt("Title", "Body", "/test/dir")
    assert "Continue working" in result
    assert "ran out of turns" in result


def test_build_continuation_prompt_includes_completion_signal():
    result = build_continuation_prompt("Title", "Body", "/test/dir")
    assert ".claude-complete" in result
    assert "DONE" in result


# is_complete tests

def test_is_complete_returns_false_when_no_marker():
    with tempfile.TemporaryDirectory() as tmpdir:
        assert is_complete(tmpdir) is False


def test_is_complete_returns_true_when_marker_exists():
    with tempfile.TemporaryDirectory() as tmpdir:
        marker_path = Path(tmpdir) / COMPLETION_MARKER
        marker_path.write_text("DONE")
        assert is_complete(tmpdir) is True


# cleanup_completion_marker tests

def test_cleanup_completion_marker_removes_marker():
    with tempfile.TemporaryDirectory() as tmpdir:
        marker_path = Path(tmpdir) / COMPLETION_MARKER
        marker_path.write_text("DONE")
        assert marker_path.exists()

        cleanup_completion_marker(tmpdir)
        assert not marker_path.exists()


def test_cleanup_completion_marker_no_error_when_missing():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Should not raise when marker doesn't exist
        cleanup_completion_marker(tmpdir)


# run_claude_chunked tests

async def test_run_claude_chunked_stops_on_completion():
    with tempfile.TemporaryDirectory() as tmpdir:
        call_count = 0

        async def mock_query(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            # Simulate agent creating completion marker on first chunk
            marker_path = Path(tmpdir) / COMPLETION_MARKER
            marker_path.write_text("DONE")
            yield {"type": "message", "content": "Done"}

        with patch("claude_runner.query", mock_query):
            messages = []
            async for msg in run_claude_chunked("Title", "Body", tmpdir, max_chunks=5):
                messages.append(msg)

            # Should only run one chunk since completion marker was created
            assert call_count == 1
            assert len(messages) == 1


async def test_run_claude_chunked_continues_without_completion():
    with tempfile.TemporaryDirectory() as tmpdir:
        chunk_count = 0

        async def mock_query(*args, **kwargs):
            nonlocal chunk_count
            chunk_count += 1
            yield {"type": "message", "content": f"Chunk {chunk_count}"}

        with patch("claude_runner.query", mock_query):
            messages = []
            async for msg in run_claude_chunked("Title", "Body", tmpdir, max_chunks=3):
                messages.append(msg)

            # Should run all 3 chunks since no completion marker
            assert chunk_count == 3
            assert len(messages) == 3


async def test_run_claude_chunked_cleans_up_marker():
    with tempfile.TemporaryDirectory() as tmpdir:
        async def mock_query(*args, **kwargs):
            marker_path = Path(tmpdir) / COMPLETION_MARKER
            marker_path.write_text("DONE")
            yield {"type": "message", "content": "Done"}

        with patch("claude_runner.query", mock_query):
            async for _ in run_claude_chunked("Title", "Body", tmpdir):
                pass

            # Marker should be cleaned up
            marker_path = Path(tmpdir) / COMPLETION_MARKER
            assert not marker_path.exists()
