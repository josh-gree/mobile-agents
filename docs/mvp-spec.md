# MVP Specification: Mobile Agent Trigger

## Core Hypothesis

Developers can meaningfully delegate coding tasks to AI agents from their phone, starting from an issue and ending with an open PR.

## The Loop

```
Issue → Instruct Agent → [Agent runs in CI] → Branch + Commit + PR
```

We're validating **delegation**, not review. Review comes in a later phase.

## Scope

### In Scope

| Component | Description |
|-----------|-------------|
| **GitHub OAuth** | User signs in, app gets token for reading issues and triggering workflows |
| **Issue list** | View issues for a selected repo |
| **Issue view** | Title, body, labels, comments (read-only) |
| **"Implement" action** | Trigger agent by adding `ai:implement` label |
| **Status indicator** | Agent running / completed / failed (via label changes) |
| **Link to PR** | Once agent finishes, show link to resulting PR |

### Out of Scope (Phase 2+)

- PR review / diff viewing
- Issue creation or editing
- Structured task contracts
- Repo creation / settings / bootstrap
- CI failure explorer
- Work inbox with filters
- Offline support
- Any code editing
- Multi-provider (GitLab, etc.)

## Architecture Decisions

See `/ADR/` for full context:

| Decision | Choice |
|----------|--------|
| Agent execution | GitHub Actions workflow in user's repo |
| Trigger mechanism | Label-based (`ai:implement`) |
| Mobile app tech | PWA (migrate to React Native if needed) |
| Agent LLM tooling | Claude Code CLI |
| GitHub auth | OAuth App (migrate to GitHub App later) |
| Issue-to-PR contract | `agent/issue-{n}-{slug}` branch, `Fixes #{n}` PR |

## Agent Workflow

The agent runs as a GitHub Actions workflow. It:

1. Triggers on `issues.labeled` event when `ai:implement` is added
2. Removes `ai:implement`, adds `ai:in-progress`
3. Reads issue title and body as instructions
4. Checks out the repo
5. Runs Claude Code CLI to implement the task
6. Creates branch: `agent/issue-{number}-{slug}`
7. Commits changes with `[Agent]` prefix
8. Opens PR with `Fixes #{number}` in title
9. Removes `ai:in-progress`, adds `ai:completed` (or `ai:failed`)

### Required Secrets

- `ANTHROPIC_API_KEY` — for Claude Code CLI

### Workflow File

Lives at `.github/workflows/agent-implement.yml` in user's repo.

## Mobile App

### Tech Stack

- PWA (Progressive Web App)
- React + TypeScript
- GitHub OAuth for authentication

### Screens

1. **Login** — GitHub OAuth flow
2. **Repo picker** — List user's repos, select one
3. **Issue list** — Issues for selected repo
4. **Issue detail** — View issue, trigger agent, see status

### Key Interactions

- Tap issue → view detail
- Tap "Implement" → adds `ai:implement` label → shows spinner
- Poll for label changes → update status
- When `ai:completed` → show link to PR

## Build Order

### Phase 1: Agent Workflow

Get a working GitHub Actions workflow that:
- Triggers on label
- Reads issue
- Produces a PR

Test via GitHub UI before building the app.

### Phase 2: Mobile App Shell

- GitHub OAuth
- Repo picker
- Issue list (read-only)

### Phase 3: Trigger & Status

- "Implement" button (adds label via API)
- Poll for status label changes
- Show PR link on completion

## Success Criteria

1. User can tap "Implement" on an issue from their phone
2. Agent runs without manual intervention
3. PR appears linked to the issue within minutes
4. Clear visibility into agent status (running/done/failed)

## Metrics (Future)

- Time from trigger to PR opened
- Agent success rate (completed vs failed)
- Number of issues implemented via mobile
- User retention / repeat usage

## Risks

| Risk | Mitigation |
|------|------------|
| Agent produces bad code | Human review required before merge (Phase 2) |
| GitHub Actions latency | Progress indicators, async mindset |
| OAuth token expiry | Standard refresh flow |
| Agent fails on complex issues | Start with simple tasks, fail fast on ambiguous issues |

## Future Phases

### Phase 2: PR Review
- Diff viewer
- Comment on PRs
- Approve / merge
- Instruct agent via PR comments

### Phase 3: Iteration Loop
- Agent responds to review comments
- CI failure handling
- "Fix CI" action

### Phase 4: Full Workflow
- Issue creation
- Structured task contracts
- Work inbox
- Multi-repo support
