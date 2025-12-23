# Ticket 002: PWA Project Scaffold

## Summary

Set up the Progressive Web App project structure with React, TypeScript, and Vite.

## Acceptance Criteria

- [ ] Vite + React + TypeScript project initialised
- [ ] PWA manifest configured (name, icons, theme colour)
- [ ] Service worker registered for installability
- [ ] Basic routing set up (react-router-dom)
- [ ] Placeholder pages: Login, RepoList, IssueList, IssueDetail
- [ ] Mobile-first CSS reset / base styles
- [ ] Environment variable support for GitHub OAuth client ID

## Technical Notes

- Use Vite's PWA plugin (`vite-plugin-pwa`)
- Keep styling minimal for now - can use Tailwind or simple CSS modules
- Structure:
  ```
  src/
    pages/
      Login.tsx
      RepoList.tsx
      IssueList.tsx
      IssueDetail.tsx
    components/
    hooks/
    lib/
    App.tsx
    main.tsx
  ```

## Test Plan

1. `npm run dev` starts development server
2. `npm run build` produces production build
3. App is installable as PWA on mobile browser
4. Navigation between placeholder pages works

## Dependencies

None - can be done in parallel with ticket 001.

## Out of Scope

- Actual GitHub API integration
- Styling / visual design
- Authentication logic
