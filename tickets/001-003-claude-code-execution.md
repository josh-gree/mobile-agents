# Ticket 001-003: Claude Code SDK Execution

## Summary

Extend the workflow to run Claude Code via the Agent SDK with the issue content as the prompt.

## Approach

Use `@anthropic-ai/claude-agent-sdk` programmatically instead of CLI for better control over the agentic loop.

## Subtasks

- 001-003-A: Create Node.js script using Agent SDK
- 001-003-B: Integrate script into workflow
- 001-003-C: Test end-to-end execution

## Dependencies

- 001-002 (branch creation)

## Implementation Notes

Extended `.github/workflows/agent-implement.yml` with:
- Added `ANTHROPIC_API_KEY` secret from repository secrets
- Added step to install Claude Code CLI via npm (`@anthropic-ai/claude-code`)
- Combines issue title and body into a prompt (title as heading, body as content)
- Runs Claude Code with `--print --dangerously-skip-permissions` flags:
  - `--print`: Non-interactive mode for CI environments
  - `--dangerously-skip-permissions`: Bypasses permission checks (appropriate for isolated CI runner)
