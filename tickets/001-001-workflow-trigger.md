# Ticket 001-001: Workflow Trigger and Initial Label Swap

## Summary

Create the basic GitHub Actions workflow file that triggers on the `ai:implement` label and performs the initial label swap.

## Acceptance Criteria

- [ ] Workflow file at `.github/workflows/agent-implement.yml`
- [ ] Triggers on `issues.labeled` event
- [ ] Only runs when label is `ai:implement`
- [ ] Removes `ai:implement` label on start
- [ ] Adds `ai:in-progress` label on start

## Technical Notes

- Use `GITHUB_TOKEN` for label operations
- Use `github.event.issue` context for issue details
- Add condition to check `github.event.label.name == 'ai:implement'`

## Test Plan

1. Create a test issue
2. Add `ai:implement` label
3. Verify workflow triggers
4. Verify labels are swapped (`ai:implement` removed, `ai:in-progress` added)

## Dependencies

None
