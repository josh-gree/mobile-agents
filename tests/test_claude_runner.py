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
    build_plan_prompt,
    build_plan_continuation_prompt,
    get_options,
    run_claude,
    run_summary_agent,
    run_claude_chunked,
    run_claude_plan_chunked,
    is_complete,
    is_plan_complete,
    cleanup_completion_marker,
    extract_session_id,
    extract_turn_summary,
    build_chunk_summary_prompt,
    build_final_summary_prompt,
    FILE_EDITING_TOOLS,
    COMPLETION_MARKER,
    PLAN_FILE,
)
from claude_agent_sdk.types import SystemMessage


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
    with pytest.raises(ValueError, match="Title is required"):
        build_prompt("", "body")

    with pytest.raises(ValueError, match="Title is required"):
        build_prompt(None, "body")


def test_build_prompt_allows_empty_body():
    """Test that body is optional - title alone is sufficient."""
    # Empty string body should work
    result = build_prompt("title", "")
    assert "# title" in result
    assert not result.endswith("\n\n")  # No extra content after title

    # None body should work (converted to empty string)
    result = build_prompt("title", None)
    assert "# title" in result


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


def test_get_options_accepts_resume():
    options = get_options(resume="session-123")
    assert options.resume == "session-123"


def test_get_options_accepts_custom_allowed_tools():
    custom_tools = ["Read", "Write"]
    options = get_options(allowed_tools=custom_tools)
    assert options.allowed_tools == custom_tools


def test_get_options_with_none_allowed_tools():
    options = get_options(allowed_tools=None)
    # When allowed_tools is None, the SDK sets it to an empty list []
    # which allows unrestricted tool access
    assert options.allowed_tools == []


def test_get_options_defaults_to_file_editing_tools():
    options = get_options()
    assert options.allowed_tools == FILE_EDITING_TOOLS


# extract_session_id tests

def test_extract_session_id_from_init_message():
    msg = SystemMessage(subtype="init", data={"session_id": "abc-123", "type": "system"})
    assert extract_session_id(msg) == "abc-123"


def test_extract_session_id_returns_none_for_non_init():
    msg = SystemMessage(subtype="other", data={"session_id": "abc-123"})
    assert extract_session_id(msg) is None


def test_extract_session_id_returns_none_for_non_system_message():
    assert extract_session_id({"type": "message"}) is None


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


async def test_run_claude_chunked_resumes_session():
    with tempfile.TemporaryDirectory() as tmpdir:
        call_count = 0
        captured_options = []

        async def mock_query(prompt, options):
            nonlocal call_count
            call_count += 1
            # Capture the options for each call
            captured_options.append(options)
            # First chunk returns init message with session_id
            if call_count == 1:
                yield SystemMessage(subtype="init", data={"session_id": "test-session-123"})
            yield {"type": "message", "content": "work"}

        with patch("claude_runner.query", mock_query):
            messages = []
            async for msg in run_claude_chunked("Title", "Body", tmpdir, max_chunks=3):
                messages.append(msg)

            # First chunk should have no resume, subsequent chunks should use session_id
            assert captured_options[0].resume is None
            assert captured_options[1].resume == "test-session-123"
            assert captured_options[2].resume == "test-session-123"


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


# build_plan_prompt tests

def test_build_plan_prompt_includes_planning_instructions():
    result = build_plan_prompt("My Feature", "Add new feature", "/test/dir")
    assert "planning agent" in result
    assert "implementation plan" in result
    assert ".plan.md" in result


def test_build_plan_prompt_includes_issue_content():
    result = build_plan_prompt("My Title", "My Body", "/test/dir")
    assert "# My Title" in result
    assert "My Body" in result


def test_build_plan_prompt_handles_empty_body():
    result = build_plan_prompt("Title Only", "", "/test/dir")
    assert "# Title Only" in result


def test_build_plan_prompt_raises_when_title_missing():
    with pytest.raises(ValueError, match="Title is required"):
        build_plan_prompt("", "body")


# build_plan_continuation_prompt tests

def test_build_plan_continuation_prompt_includes_continue_message():
    result = build_plan_continuation_prompt("Title", "Body", "/test/dir")
    assert "Continue working" in result
    assert "ran out of turns" in result


def test_build_plan_continuation_prompt_includes_plan_file():
    result = build_plan_continuation_prompt("Title", "Body", "/test/dir")
    assert ".plan.md" in result


def test_build_plan_continuation_prompt_includes_issue():
    result = build_plan_continuation_prompt("My Title", "My Body", "/test/dir")
    assert "# My Title" in result
    assert "My Body" in result


# is_plan_complete tests

def test_is_plan_complete_returns_false_when_no_plan():
    with tempfile.TemporaryDirectory() as tmpdir:
        assert is_plan_complete(tmpdir) is False


def test_is_plan_complete_returns_true_when_plan_exists():
    with tempfile.TemporaryDirectory() as tmpdir:
        plan_path = Path(tmpdir) / PLAN_FILE
        plan_path.write_text("# Plan\n\nDo stuff")
        assert is_plan_complete(tmpdir) is True


# run_claude_plan_chunked tests

async def test_run_claude_plan_chunked_stops_when_plan_created():
    with tempfile.TemporaryDirectory() as tmpdir:
        call_count = 0

        async def mock_query(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            # Simulate agent creating plan file on first chunk
            plan_path = Path(tmpdir) / PLAN_FILE
            plan_path.write_text("# Plan\n\nDo stuff")
            yield {"type": "message", "content": "Done"}

        with patch("claude_runner.query", mock_query):
            messages = []
            async for msg in run_claude_plan_chunked("Title", "Body", tmpdir, max_chunks=5):
                messages.append(msg)

            # Should only run one chunk since plan was created
            assert call_count == 1


async def test_run_claude_plan_chunked_continues_without_plan():
    with tempfile.TemporaryDirectory() as tmpdir:
        chunk_count = 0

        async def mock_query(*args, **kwargs):
            nonlocal chunk_count
            chunk_count += 1
            yield {"type": "message", "content": f"Chunk {chunk_count}"}

        with patch("claude_runner.query", mock_query):
            messages = []
            async for msg in run_claude_plan_chunked("Title", "Body", tmpdir, max_chunks=3):
                messages.append(msg)

            # Should run all 3 chunks since no plan created
            assert chunk_count == 3


async def test_run_claude_plan_chunked_resumes_session():
    with tempfile.TemporaryDirectory() as tmpdir:
        call_count = 0
        captured_options = []

        async def mock_query(prompt, options):
            nonlocal call_count
            call_count += 1
            captured_options.append(options)
            if call_count == 1:
                yield SystemMessage(subtype="init", data={"session_id": "plan-session-456"})
            yield {"type": "message", "content": "work"}

        with patch("claude_runner.query", mock_query):
            messages = []
            async for msg in run_claude_plan_chunked("Title", "Body", tmpdir, max_chunks=3):
                messages.append(msg)

            # First chunk should have no resume, subsequent chunks should use session_id
            assert captured_options[0].resume is None
            assert captured_options[1].resume == "plan-session-456"
            assert captured_options[2].resume == "plan-session-456"


# Summary generation tests

def test_extract_turn_summary_with_empty_messages():
    messages = []
    result = extract_turn_summary(messages)
    assert result == "No significant activity recorded"


def test_build_chunk_summary_prompt_includes_title():
    messages = []
    prompt = build_chunk_summary_prompt("Test Title", "Test Body", messages, 0, "/tmp")
    assert "Test Title" in prompt
    assert "Chunk 1" in prompt


def test_build_chunk_summary_prompt_includes_body():
    messages = []
    prompt = build_chunk_summary_prompt("Test Title", "Test Body", messages, 0, "/tmp")
    assert "Test Body" in prompt


def test_build_chunk_summary_prompt_handles_empty_body():
    messages = []
    prompt = build_chunk_summary_prompt("Test Title", "", messages, 0, "/tmp")
    assert "Test Title" in prompt
    assert "(No additional description)" in prompt


def test_build_final_summary_prompt_includes_title():
    summaries = ["Summary 1", "Summary 2"]
    prompt = build_final_summary_prompt("Test Title", "Test Body", summaries, "/tmp")
    assert "Test Title" in prompt


def test_build_final_summary_prompt_includes_all_summaries():
    summaries = ["Summary 1", "Summary 2"]
    prompt = build_final_summary_prompt("Test Title", "Test Body", summaries, "/tmp")
    assert "Summary 1" in prompt
    assert "Summary 2" in prompt
    assert "Chunk 1" in prompt
    assert "Chunk 2" in prompt


# run_summary_agent tests

async def test_run_summary_agent_uses_unrestricted_tools():
    """Test that run_summary_agent calls run_claude with allowed_tools=None."""
    from unittest.mock import AsyncMock
    from claude_agent_sdk.types import AssistantMessage, TextBlock

    with tempfile.TemporaryDirectory() as tmpdir:
        captured_allowed_tools = None

        async def mock_run_claude(prompt, cwd, max_turns, allowed_tools=None):
            nonlocal captured_allowed_tools
            captured_allowed_tools = allowed_tools
            # Return a mock AssistantMessage with text in content blocks
            msg = AssistantMessage(
                content=[TextBlock(text="Test summary text")],
                model="claude"
            )
            yield msg

        with patch("claude_runner.run_claude", mock_run_claude):
            from claude_runner import run_summary_agent
            result = await run_summary_agent("Test prompt", tmpdir)

            # Verify that allowed_tools was None (unrestricted)
            assert captured_allowed_tools is None
            # Verify that we got the summary text
            assert result == "Test summary text"


async def test_run_summary_agent_extracts_text_from_messages():
    """Test that run_summary_agent correctly extracts text from AssistantMessage."""
    from claude_agent_sdk.types import AssistantMessage, TextBlock

    with tempfile.TemporaryDirectory() as tmpdir:
        async def mock_run_claude(*args, **kwargs):
            yield AssistantMessage(
                content=[TextBlock(text="First part. ")],
                model="claude"
            )
            yield AssistantMessage(
                content=[TextBlock(text="Second part.")],
                model="claude"
            )

        with patch("claude_runner.run_claude", mock_run_claude):
            from claude_runner import run_summary_agent
            result = await run_summary_agent("Test prompt", tmpdir)

            assert result == "First part. Second part."


async def test_run_summary_agent_handles_no_output():
    """Test that run_summary_agent returns error message when no text is produced."""
    with tempfile.TemporaryDirectory() as tmpdir:
        async def mock_run_claude(*args, **kwargs):
            # Yield messages with no text
            yield {"type": "other"}

        with patch("claude_runner.run_claude", mock_run_claude):
            from claude_runner import run_summary_agent
            result = await run_summary_agent("Test prompt", tmpdir)

            assert result == "Summary generation did not produce output."


async def test_run_summary_agent_handles_exceptions():
    """Test that run_summary_agent handles exceptions gracefully."""
    with tempfile.TemporaryDirectory() as tmpdir:
        async def mock_run_claude(*args, **kwargs):
            raise RuntimeError("Test error")
            yield  # Make it a generator

        with patch("claude_runner.run_claude", mock_run_claude):
            from claude_runner import run_summary_agent
            result = await run_summary_agent("Test prompt", tmpdir)

            assert "Error generating summary" in result
            assert "Test error" in result


async def test_run_claude_chunked_with_callbacks():
    with tempfile.TemporaryDirectory() as tmpdir:
        callback_calls = []
        final_calls = []

        async def mock_callback(chunk_num: int, summary: str):
            callback_calls.append((chunk_num, summary))

        async def mock_final(summaries: list[str]):
            final_calls.append(summaries)

        async def mock_query(*args, **kwargs):
            yield {"type": "message", "content": "work"}

        async def mock_summary_agent(*args, **kwargs):
            return "Test summary"

        # Create completion marker after first chunk
        with patch("claude_runner.query", mock_query):
            with patch("claude_runner.run_summary_agent", mock_summary_agent):
                messages = []
                async for msg in run_claude_chunked(
                    "Title",
                    "Body",
                    tmpdir,
                    turns_per_chunk=1,
                    max_chunks=2,
                    on_chunk_complete=mock_callback,
                    on_final_complete=mock_final,
                ):
                    messages.append(msg)
                    # Create completion marker after first message
                    if len(messages) == 1:
                        (Path(tmpdir) / COMPLETION_MARKER).write_text("DONE")

                # Should have called chunk callback once
                assert len(callback_calls) == 1
                assert callback_calls[0][0] == 0
                assert callback_calls[0][1] == "Test summary"

                # Should have called final callback
                assert len(final_calls) == 1
