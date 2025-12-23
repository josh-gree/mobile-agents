# Ticket 001: Agent GitHub Actions Workflow

> **Note:** This ticket has been split into sub-tickets for easier implementation:
> - [001-001](./001-001-workflow-trigger.md) - Workflow trigger and initial label swap
> - [001-002](./001-002-branch-creation.md) - Branch creation from issue
> - [001-003](./001-003-claude-code-execution.md) - Claude Code CLI execution
> - [001-004](./001-004-commit-and-pr.md) - Commit changes and open PR
> - [001-005](./001-005-completion-labels.md) - Completion label management

## Summary

Create the GitHub Actions workflow that runs the AI agent when an issue is labelled `ai:implement`.

## Acceptance Criteria

- [ ] Workflow file at `.github/workflows/agent-implement.yml`
- [ ] Triggers on `issues.labeled` event for `ai:implement` label
- [ ] Removes `ai:implement` label, adds `ai:in-progress` on start
- [ ] Reads issue title and body as instructions
- [ ] Checks out the repository
- [ ] Runs Claude Code CLI with issue content as prompt
- [ ] Creates branch: `agent/issue-{number}-{slug}`
- [ ] Commits changes with `[Agent]` prefix (conventional commit style)
- [ ] Opens PR with `Fixes #{number}` in title
- [ ] Adds `ai:completed` label on success, `ai:failed` on failure
- [ ] Removes `ai:in-progress` label on completion

## Technical Notes

- Requires `ANTHROPIC_API_KEY` secret in the repository
- Use `GITHUB_TOKEN` for all GitHub operations (branches, commits, PRs, labels)
- Branch slug derived from issue title (max 5 words, kebab-case)
- PR body follows structure from ADR 006

## Test Plan

1. Create a test issue with clear instructions (e.g., "Add a hello world function to utils.js")
2. Add `ai:implement` label via GitHub UI
3. Verify workflow triggers and runs
4. Verify PR is created with correct format
5. Verify labels are updated correctly

## Dependencies

None - this is the foundation.

## Out of Scope

- Mobile app integration (future tickets)
- Complex error handling / retry logic
- Agent configuration options
