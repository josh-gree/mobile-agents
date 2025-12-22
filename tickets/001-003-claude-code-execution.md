# Ticket 001-003: Claude Code CLI Execution

## Summary

Extend the workflow to run Claude Code CLI with the issue content as the prompt.

## Acceptance Criteria

- [ ] Reads issue title and body as instructions
- [ ] Runs Claude Code CLI with combined issue content as prompt
- [ ] Claude Code makes changes to the codebase

## Technical Notes

- Requires `ANTHROPIC_API_KEY` secret in the repository
- Combine issue title and body into a coherent prompt
- Consider using `--print` or appropriate CLI flags for non-interactive mode

## Test Plan

1. Create issue with clear instructions (e.g., "Add a hello world function to utils.js")
2. Add `ai:implement` label
3. Verify Claude Code runs and makes changes to files

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
