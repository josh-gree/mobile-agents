# Ticket 001-002: Branch Creation from Issue

## Summary

Extend the workflow to check out the repository and create a properly named branch based on the issue.

## Acceptance Criteria

- [ ] Checks out the repository
- [ ] Creates branch: `agent/issue-{number}-{slug}`
- [ ] Slug derived from issue title (max 5 words, kebab-case)
- [ ] Pushes branch to remote

## Technical Notes

- Use `actions/checkout@v4`
- Slug generation: lowercase, remove special chars, take first 5 words, join with hyphens
- Example: "Add user authentication to login page" → `agent/issue-42-add-user-authentication-to-login`

## Test Plan

1. Create issue titled "Add a hello world function"
2. Add `ai:implement` label
3. Verify branch `agent/issue-{N}-add-a-hello-world` is created

## Dependencies

- 001-001 (workflow trigger)
