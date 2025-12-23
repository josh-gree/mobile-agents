# Ticket 001-005: Completion Label Management

## Summary

Extend the workflow to update labels on completion (success or failure).

## Acceptance Criteria

- [ ] Adds `ai:completed` label on success
- [ ] Adds `ai:failed` label on failure
- [ ] Removes `ai:in-progress` label on completion (success or failure)

## Technical Notes

- Use `GITHUB_TOKEN` for label operations
- Use `if: success()` and `if: failure()` conditions
- Consider using `if: always()` for removing `ai:in-progress`
- May need separate steps for success/failure paths

## Test Plan

1. Trigger workflow on an issue with valid instructions
2. Verify `ai:in-progress` removed and `ai:completed` added on success
3. Trigger workflow on an issue that will fail (e.g., impossible task)
4. Verify `ai:in-progress` removed and `ai:failed` added on failure

## Dependencies

- 001-004 (commit and PR)
