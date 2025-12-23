# Agent Workflow

A GitHub Actions workflow that uses Claude Code to automatically implement issues.

## How It Works

You can trigger the workflow in two ways:

### Option 1: Add a label
Add the `ai:implement` label to an issue

### Option 2: Use a trigger in the title
Include `[ai:implement]` or `@ai-implement` anywhere in the issue title. The workflow will automatically add the label for you.

**Example titles:**
- `[ai:implement] Add user authentication`
- `Fix login bug @ai-implement`
- `@ai-implement Implement dark mode feature`

Once triggered, the workflow automatically:
1. Swaps labels (`ai:implement` → `ai:in-progress`)
2. Creates a branch: `agent/issue-{number}-{slug}`
3. Runs tests to ensure the codebase is healthy
4. Runs Claude Code with the issue content as the prompt
5. Claude Code makes changes using file editing tools
6. Commits changes and creates a PR
7. Updates labels (`ai:in-progress` → `ai:completed` or `ai:failed`)

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

## Labels

Create these labels in your repository:

| Label | Purpose |
|-------|---------|
| `ai:implement` | Trigger the workflow |
| `ai:in-progress` | Agent is working |
| `ai:completed` | Successful completion |
| `ai:failed` | Workflow failed |

## Agent Capabilities

The agent is restricted to file editing tools only:
- `Read` - Read file contents
- `Edit` - Modify existing files
- `Write` - Create new files
- `Glob` - Find files by pattern
- `Grep` - Search file contents

This prevents the agent from running arbitrary shell commands.
