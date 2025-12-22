# Ticket 001-003-B: Integrate Script into Workflow

## Summary

Update the GitHub Actions workflow to use the Node.js Agent SDK script instead of CLI.

## Acceptance Criteria

- [ ] Workflow installs `@anthropic-ai/claude-agent-sdk`
- [ ] Workflow runs `.github/scripts/run-claude.mjs`
- [ ] Environment variables passed correctly (ISSUE_TITLE, ISSUE_BODY, ANTHROPIC_API_KEY)
- [ ] Remove old CLI-based step

## Technical Notes

```yaml
- name: Run Claude Code
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
    ISSUE_TITLE: ${{ github.event.issue.title }}
    ISSUE_BODY: ${{ github.event.issue.body }}
  run: |
    npm install @anthropic-ai/claude-agent-sdk
    node .github/scripts/run-claude.mjs
```

## Dependencies

- 001-003-A (Agent SDK script)
