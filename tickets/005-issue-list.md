# Ticket 005: Issue List View

## Summary

Display the list of issues for the selected repository.

## Acceptance Criteria

- [ ] Fetch issues from GitHub API for selected repo
- [ ] Display issue title, number, and labels
- [ ] Show agent status via labels (`ai:in-progress`, `ai:completed`, `ai:failed`)
- [ ] Visual indicator for agent-related issues
- [ ] Tap issue to navigate to issue detail view
- [ ] Pull-to-refresh to reload issues
- [ ] Handle loading and error states
- [ ] Filter to open issues by default

## Technical Notes

- GitHub API endpoint: `GET /repos/{owner}/{repo}/issues`
- Filter: `state=open` by default
- Labels to highlight: `ai:implement`, `ai:in-progress`, `ai:completed`, `ai:failed`
- Consider colour-coding agent status labels

## Test Plan

1. Select a repo - see list of open issues
2. Issues show title, number, labels
3. Pull down to refresh list
4. Tap issue - navigates to detail view
5. Handle repo with 0 issues gracefully

## Dependencies

- Ticket 004 (Repo picker - need selected repo)

## Out of Scope

- Issue creation
- Issue editing
- Closed issues view
- Advanced filtering (by label, assignee, etc.)
