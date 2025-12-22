# Agent Workflow

A GitHub Actions workflow that uses Claude Code to automatically implement issues.

## How It Works

1. Add the `ai:implement` label to an issue
2. The workflow automatically:
   - Swaps labels (`ai:implement` → `ai:in-progress`)
   - Creates a branch: `agent/issue-{number}-{slug}`
   - Runs Claude Code with the issue content as the prompt
   - Claude Code makes changes to the codebase

## Required Secrets

### `ANTHROPIC_API_KEY`

The workflow requires an Anthropic API key to run Claude Code.

1. Get an API key from [Anthropic Console](https://console.anthropic.com/)
2. Go to your repository's **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `ANTHROPIC_API_KEY`
5. Value: Your Anthropic API key

## Security

The workflow only runs for issues created by:
- Repository owners (`OWNER`)
- Collaborators (`COLLABORATOR`)
- Organisation members (`MEMBER`)

Issues from external contributors will not trigger the workflow.

## Labels

The workflow uses these labels (create them in your repository if they don't exist):

| Label | Purpose |
|-------|---------|
| `ai:implement` | Trigger the workflow |
| `ai:in-progress` | Indicates the agent is working |
| `ai:completed` | Added on successful completion |
| `ai:failed` | Added if the workflow fails |
