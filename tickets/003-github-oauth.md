# Ticket 003: GitHub OAuth Authentication

## Summary

Implement GitHub OAuth flow so users can sign in and grant repository access.

## Acceptance Criteria

- [ ] GitHub OAuth App created (manual step, document in README)
- [ ] Login page with "Sign in with GitHub" button
- [ ] OAuth redirect flow implemented
- [ ] Access token stored securely (localStorage or similar)
- [ ] Auth context/hook for checking auth state across app
- [ ] Redirect to repo list on successful login
- [ ] Logout functionality
- [ ] Handle token expiry / invalid token gracefully

## Technical Notes

- OAuth scopes required: `repo`, `workflow`
- Flow:
  1. User clicks sign in
  2. Redirect to GitHub OAuth authorise URL
  3. GitHub redirects back with code
  4. Exchange code for access token (requires backend proxy or use implicit flow)
- For MVP, can use a simple serverless function or Netlify/Vercel function to exchange code
- Store token in localStorage (acceptable for MVP)

## Test Plan

1. Click "Sign in with GitHub"
2. Authorise on GitHub
3. Redirected back to app, logged in
4. Refresh page - still logged in
5. Click logout - returns to login page

## Dependencies

- Ticket 002 (PWA scaffold)

## Out of Scope

- Token refresh (GitHub OAuth tokens don't expire, but may be revoked)
- Multiple account support
- GitHub App migration
