# Agent Workflow

A GitHub Actions workflow that uses Claude Code to automatically implement issues.

## How It Works

You can trigger the workflow in three ways:

### Option 1: Plan First (Recommended)
Generate an implementation plan before executing changes:

1. Add the `ai:plan` label to an issue (or include `[ai:plan]` or `@ai-plan` in the title)
2. The agent will analyze the codebase and post an implementation plan as a comment
3. Review the plan and either:
   - Comment `/apply` to start implementation based on the plan
   - Comment `/close` to close the issue and clean up branches

**Example titles:**
- `[ai:plan] Add user authentication`
- `Fix login bug @ai-plan`
- `@ai-plan Implement dark mode feature`

**Plan workflow:**
1. Swaps labels (`ai:plan` → `ai:planning` → `ai:planned`)
2. Agent explores codebase and generates implementation plan
3. Posts plan as issue comment
4. Wait for `/apply` or `/close` command

### Option 2: Direct Implementation
Skip planning and implement directly:

Add the `ai:implement` label to an issue (or include `[ai:implement]` or `@ai-implement` in the title)

**Example titles:**
- `[ai:implement] Add user authentication`
- `Fix login bug @ai-implement`
- `@ai-implement Implement dark mode feature`

**Implementation workflow:**
1. Swaps labels (`ai:implement` → `ai:in-progress`)
2. Creates a branch: `agent/issue-{number}-{slug}`
3. Runs tests to ensure the codebase is healthy
4. Runs Claude Code with the issue content (and plan if available) as the prompt
5. Claude Code makes changes using file editing tools
6. Commits changes and creates a PR
7. Updates labels (`ai:in-progress` → `ai:completed` or `ai:failed`)

### Option 3: Plan + Apply Together
Create an `ai:plan` label first, then after reviewing the plan comment, add the `ai:implement` label to execute the plan

## Stack

- **Python 3.12** with [uv](https://github.com/astral-sh/uv) for dependency management
- **claude-agent-sdk** - Python SDK for Claude Code
- **pytest** for testing

## Development

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Run the agent locally (requires env vars)
ANTHROPIC_API_KEY=... ISSUE_TITLE="..." ISSUE_BODY="..." uv run python .github/scripts/run_claude.py
```

## Required Secrets

### `ANTHROPIC_API_KEY`

The workflow requires an Anthropic API key to run Claude Code.

1. Get an API key from [Anthropic Console](https://console.anthropic.com/)
2. Add as repository secret: **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

### `PAT_TOKEN`

A fine-grained Personal Access Token is required to allow the agent to modify workflow files.

1. Create a fine-grained PAT at [GitHub Settings](https://github.com/settings/tokens?type=beta)
2. Grant permissions: **Contents** (read/write), **Workflows** (read/write), **Pull requests** (read/write)
3. Add as repository secret: `PAT_TOKEN`

## Security

The workflow only runs for issues created by the repository owner (`author_association == 'OWNER'`).

## Comment Commands

Use these commands in issue comments (only works for issue author/owner):

| Command | Purpose |
|---------|---------|
| `/apply` | Start implementation after a plan has been generated |
| `/close` | Close the issue and clean up any associated branches |

## Labels

Create these labels in your repository:

| Label | Purpose |
|-------|---------|
| `ai:plan` | Trigger plan generation |
| `ai:planning` | Agent is generating plan |
| `ai:planned` | Plan ready for review |
| `ai:plan-failed` | Plan generation failed |
| `ai:implement` | Trigger direct implementation |
| `ai:in-progress` | Agent is implementing |
| `ai:completed` | Successful completion |
| `ai:failed` | Implementation failed |

## Agent Capabilities

The agent is restricted to file editing tools only:
- `Read` - Read file contents
- `Edit` - Modify existing files
- `Write` - Create new files
- `Glob` - Find files by pattern
- `Grep` - Search file contents

This prevents the agent from running arbitrary shell commands.
