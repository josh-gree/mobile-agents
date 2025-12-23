# ADR 006: Issue to PR Contract

## Status

Proposed

## Context

We're building a mobile-first app that allows developers to delegate coding tasks to AI agents from their phone. The MVP flow is:

1. Developer creates or selects a GitHub issue
2. Developer instructs the agent (from mobile)
3. Agent reads the issue, creates a branch, implements changes, commits, and opens a PR

For this workflow to be effective and maintainable, we need clear conventions for how the agent transforms an issue into a PR. This ensures traceability, maintains consistency across agent-generated work, and makes it obvious to reviewers that an agent was involved.

The key challenge is establishing a simple, clear contract that provides:
- Traceability from issue → branch → commits → PR
- Automatic issue closure when PR is merged (when appropriate)
- Clear identification of agent-generated work
- Minimal cognitive overhead for human reviewers

## Decision

### 1. Branch Naming Convention

Agent creates branches with the format: `agent/issue-{issue-number}-{slug}`

**Examples:**
- `agent/issue-123-fix-login-bug`
- `agent/issue-456-add-user-profile`

**Rules:**
- Prefix: Always `agent/` to clearly identify agent-generated branches
- Issue number: Directly references the GitHub issue
- Slug: Short kebab-case description derived from issue title (max 5 words)
- Agent truncates/simplifies slug if issue title is verbose

### 2. PR Title

Format: `Fixes #{issue-number}: {issue title or summary}`

**Examples:**
- `Fixes #123: Login bug with OAuth redirect`
- `Fixes #456: Add user profile page`

**Rules:**
- Always starts with `Fixes #` for automatic issue closure
- Uses issue title or agent's summary if title is too long
- Maximum 72 characters (standard Git/GitHub practice)

### 3. PR Body

Standard structure:

```markdown
## Summary
[Agent's brief description of what was implemented]

## Changes
- [Key change 1]
- [Key change 2]
- [etc.]

## Implementation Notes
[Any technical decisions, trade-offs, or areas needing human review]

Closes #{issue-number}
```

**Rules:**
- Summary: 2-3 sentences maximum, focus on what was done
- Changes: Bulleted list of key modifications
- Implementation Notes: Optional section for context humans should know
- Footer: Always includes `Closes #` keyword for issue linking
- No test plan section (as per global instructions) unless explicitly requested

### 4. Commit Messages

Format: `[Agent] {conventional commit type}: {description}`

**Examples:**
- `[Agent] feat: implement OAuth login flow`
- `[Agent] fix: resolve redirect loop in auth callback`
- `[Agent] refactor: extract user validation logic`

**Rules:**
- Prefix: Always `[Agent]` to identify agent commits
- Type: Use conventional commit types (feat, fix, refactor, test, docs, chore)
- Description: Imperative mood, lowercase, no period, max 72 chars
- Body/footer: Optional for additional context

### 5. What the Agent Reads

**Primary input (MVP):**
- Issue title
- Issue body
- Issue labels (for context, e.g., `bug`, `enhancement`)

**Not included in MVP:**
- Issue comments (future enhancement for follow-up instructions)
- Linked PRs or issues
- External references

**Rules:**
- Issue body is treated as the primary instruction set
- If issue body is empty or too vague, agent should fail fast and request clarification
- Agent should respect labels like `bug` vs `feature` in its approach

## Consequences

### Positive

- **Clear traceability**: Branch name directly contains issue number, making it trivial to trace work
- **Automatic issue closure**: Using `Fixes #` ensures issues close when PR merges
- **Agent identification**: `agent/` prefix and `[Agent]` commit prefix make agent work immediately obvious
- **Familiar conventions**: Follows GitHub and conventional commit standards
- **Simple to implement**: Straightforward string formatting, no complex logic
- **Reviewer friendly**: Humans can immediately identify and understand agent-generated work

### Negative

- **Namespace collision**: Multiple agents working on same issue would create branch conflicts (acceptable for MVP, future: add agent ID or timestamp)
- **Branch clutter**: `agent/` branches accumulate if not cleaned up (future: add automatic branch deletion post-merge)
- **Rigid format**: Less flexibility for edge cases (acceptable trade-off for consistency)
- **Comment exclusion**: Agent won't see follow-up instructions in comments initially (deliberate MVP limitation)

### Mitigation Strategies

For future iterations:
- Add agent instance ID to branch name if parallel work needed: `agent-{id}/issue-123-fix`
- Implement automatic branch cleanup after PR merge
- Add comment monitoring for follow-up instructions
- Consider draft PR workflow for complex issues requiring human checkpoints

## Notes

- This ADR focuses on MVP simplicity; conventions will evolve based on real usage
- The `Fixes #` keyword can be changed to `Relates to #` if auto-closure isn't desired (agent should detect this from issue labels or future config)
- British spelling applies throughout agent-generated text as per project standards
