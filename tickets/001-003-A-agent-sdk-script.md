# Ticket 001-003-A: Create Node.js Script Using Agent SDK

## Summary

Create a Node.js script that uses `@anthropic-ai/claude-agent-sdk` to run Claude Code programmatically.

## Acceptance Criteria

- [ ] Script at `.github/scripts/run-claude.mjs`
- [ ] Reads `ISSUE_TITLE` and `ISSUE_BODY` from environment variables
- [ ] Uses `query()` from Agent SDK with combined prompt
- [ ] Configures `permissionMode: 'bypassPermissions'` for CI
- [ ] Streams and logs output messages
- [ ] Exits with appropriate code on success/failure

## Technical Notes

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

const prompt = `# ${process.env.ISSUE_TITLE}\n\n${process.env.ISSUE_BODY}`;

const result = await query({
  prompt,
  options: {
    permissionMode: 'bypassPermissions',
    maxTurns: 10  // Limit agentic loop iterations
  }
});

for await (const message of result) {
  console.log(JSON.stringify(message));
}
```

## Dependencies

- 001-002 (branch creation)
