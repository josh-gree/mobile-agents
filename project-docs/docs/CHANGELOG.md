# Changelog

## Recent Changes

### December 23, 2024 - Initial Project Setup

This represents the initial commit establishing the mobile-agents project infrastructure and core functionality.

#### 🎯 Core Features Implemented

**Agent Workflow System**
- Implemented GitHub Actions-based agent workflows that use Claude Code to automatically implement issues
- Two workflow modes:
  - **Plan Mode** (`ai:plan` label): Generates implementation plan before execution
  - **Direct Implementation** (`ai:implement` label): Skip planning and implement directly
- Support for title-based triggers using `[ai:plan]`, `@ai-plan`, `[ai:implement]`, or `@ai-implement` syntax
- Comment-based commands (`/apply`, `/close`) for plan approval and issue management

**Workflow Infrastructure**
- `.github/workflows/agent-implement.yml` - Main implementation workflow
- `.github/workflows/agent-plan.yml` - Plan generation workflow
- `.github/workflows/comment-handler.yml` - Handles issue comment commands
- `.github/workflows/ci.yml` - Continuous integration pipeline

**Python Scripts**
- `run_claude.py` - Core Claude Code execution script with file editing restrictions
- `run_claude_plan.py` - Plan generation using Claude Code in explore mode
- `generate_pr_description.py` - AI-powered PR description generation from diffs

**Source Code**
- `src/claude_runner.py` - Claude agent SDK integration (21KB implementation)
- `src/github_api.py` - GitHub API utilities
- `src/random_utils.py` - Utility functions
- `src/version.py` - Version management

#### 📚 Documentation

**Architecture Decision Records (ADRs)**
- `001-agent-execution-model.md` - GitHub Actions as execution environment
- `002-trigger-mechanism.md` - Label-based triggering system
- `003-mobile-app-technology.md` - PWA approach for mobile interface
- `004-agent-llm-tooling.md` - Claude Code CLI selection
- `005-github-integration-auth.md` - OAuth App authentication strategy
- `006-issue-to-pr-contract.md` - Branch naming and PR conventions

**Specifications**
- `mvp-spec.md` - Complete MVP specification covering core hypothesis, scope, architecture, and success criteria

**Tickets**
- `001-agent-workflow.md` - Main agent workflow epic
- `001-001-workflow-trigger.md` - Workflow trigger implementation
- `001-002-branch-creation.md` - Branch creation logic
- `001-003-claude-code-execution.md` - Claude Code integration
- `001-003-A-agent-sdk-script.md` - Agent SDK script details
- `001-003-B-workflow-integration.md` - Workflow integration details
- `001-003-C-test-execution.md` - Test execution requirements
- `001-004-commit-and-pr.md` - Commit and PR creation
- `001-005-completion-labels.md` - Label management
- `002-pwa-scaffold.md` - PWA scaffolding plan
- `003-github-oauth.md` - OAuth implementation plan
- `004-repo-picker.md` - Repository picker UI
- `005-issue-list.md` - Issue list view
- `006-ci-caching.md` - CI caching optimization

#### 🛠️ Technology Stack

- **Python 3.12** with `uv` for dependency management
- **claude-agent-sdk** for Claude Code integration
- **pytest** for testing
- **GitHub Actions** for CI/CD and agent execution

#### 🔒 Security Features

- Workflow execution restricted to repository owners only
- Agent limited to file editing tools (Read, Edit, Write, Glob, Grep)
- No arbitrary shell command execution
- Requires `ANTHROPIC_API_KEY` and `PAT_TOKEN` secrets

#### 🏷️ Label System

Status labels implemented:
- `ai:plan` - Trigger plan generation
- `ai:planning` - Agent is generating plan
- `ai:planned` - Plan ready for review
- `ai:plan-failed` - Plan generation failed
- `ai:implement` - Trigger direct implementation
- `ai:in-progress` - Agent is implementing
- `ai:completed` - Successful completion
- `ai:failed` - Implementation failed

#### 📦 Project Structure

```
mobile-agents/
├── .github/
│   ├── scripts/          # Python scripts for workflows
│   └── workflows/        # GitHub Actions workflows
├── project-docs/
│   ├── adr/             # Architecture Decision Records
│   ├── docs/            # Specifications and documentation
│   └── tickets/         # Implementation tickets
├── src/                 # Python source code
├── tests/               # Test suite
├── pyproject.toml       # Python project configuration
└── uv.lock             # Dependency lock file
```

#### 🎯 Next Steps

The project is now ready for:
1. Testing the agent workflows with real issues
2. Building the PWA mobile interface
3. Implementing GitHub OAuth flow
4. Creating repository picker and issue list views
5. Adding PR review capabilities (Phase 2)

---

*This changelog documents the initial project setup and core infrastructure.*
