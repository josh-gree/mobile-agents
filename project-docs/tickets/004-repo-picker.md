# Ticket 004: Repository Picker

## Summary

Build the repository selection screen that lists the user's accessible repositories.

## Acceptance Criteria

- [ ] Fetch user's repositories from GitHub API
- [ ] Display repos in a searchable/filterable list
- [ ] Show repo name, owner, and description
- [ ] Tap repo to select and navigate to issue list
- [ ] Store selected repo in app state/context
- [ ] Handle loading and error states
- [ ] Paginate or lazy load if user has many repos

## Technical Notes

- GitHub API endpoint: `GET /user/repos`
- Sort by recently pushed or alphabetically
- Consider showing only repos where user has push access (for triggering workflows)
- Simple search: filter client-side by repo name

## Test Plan

1. After login, see list of repositories
2. Search filters the list
3. Tap a repo - navigates to issue list for that repo
4. Handle user with 0 repos gracefully
5. Handle API errors (show error message, retry option)

## Dependencies

- Ticket 003 (GitHub OAuth - need auth token)

## Out of Scope

- Repo creation
- Repo settings / configuration
- Checking if agent workflow is installed in repo
