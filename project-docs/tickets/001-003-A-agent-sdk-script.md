# Ticket 001-003-A: Create Python Script Using Agent SDK

## Summary

Create a Python script that uses `claude-agent-sdk` to run Claude Code programmatically.

## Acceptance Criteria

- [x] Script at `.github/scripts/run_claude.py`
- [x] Core module at `src/claude_runner.py`
- [x] Reads `ISSUE_TITLE` and `ISSUE_BODY` from environment variables
- [x] Uses `query()` from Agent SDK with combined prompt
- [x] Configures `permissionMode: 'bypassPermissions'` for CI
- [x] Restricts tools to file editing only (Read, Edit, Write, Glob, Grep)
- [x] Streams and logs output messages
- [x] Exits with appropriate code on success/failure
- [x] Tests with pytest

## Implementation

```python
from claude_agent_sdk import query, ClaudeAgentOptions

FILE_EDITING_TOOLS = ["Read", "Edit", "Write", "Glob", "Grep"]

options = ClaudeAgentOptions(
    allowed_tools=FILE_EDITING_TOOLS,
    permission_mode="bypassPermissions",
    max_turns=10,
)

async for message in query(prompt=prompt, options=options):
    print(json.dumps(message, default=str))
```

## Dependencies

- 001-002 (branch creation)
