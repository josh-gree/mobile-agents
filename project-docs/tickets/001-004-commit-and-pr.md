# Ticket 001-004: Commit Changes and Open PR

## Summary

Extend the workflow to commit the agent's changes and open a pull request.

## Acceptance Criteria

- [ ] Commits changes with `[Agent]` prefix (conventional commit style)
- [ ] Opens PR targeting default branch
- [ ] PR title includes `Fixes #{number}`
- [ ] PR body follows structure from ADR 006

## Technical Notes

- Use `GITHUB_TOKEN` for git operations and PR creation
- Configure git user for commits (e.g., `github-actions[bot]`)
- Use `gh pr create` or GitHub API for PR creation
- Only commit if there are actual changes

## Test Plan

1. Trigger workflow on an issue
2. Verify commit message format: `[Agent] feat: <description>`
3. Verify PR is created with `Fixes #N` in title
4. Verify PR body structure matches ADR 006

## Dependencies

- 001-003 (Claude Code execution)
