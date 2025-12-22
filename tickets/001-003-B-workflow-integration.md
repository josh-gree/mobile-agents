# Ticket 001-003-B: Integrate Script into Workflow

## Summary

Update the GitHub Actions workflow to use the Python Agent SDK script.

## Acceptance Criteria

- [x] Workflow sets up Python 3.12
- [x] Workflow installs uv and syncs dependencies
- [x] Workflow caches `.venv` based on `uv.lock` hash
- [x] Workflow runs tests before agent execution
- [x] Workflow runs `.github/scripts/run_claude.py`
- [x] Environment variables passed correctly (ISSUE_TITLE, ISSUE_BODY, ANTHROPIC_API_KEY)
- [x] Uses PAT_TOKEN for checkout to allow workflow file modifications

## Implementation

```yaml
- name: Setup Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.12'

- name: Install uv
  uses: astral-sh/setup-uv@v6

- name: Cache uv
  uses: actions/cache@v4
  with:
    path: .venv
    key: ${{ runner.os }}-uv-${{ hashFiles('uv.lock') }}

- name: Install dependencies
  run: uv sync

- name: Run tests
  run: uv run pytest

- name: Run Claude Code
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
    ISSUE_TITLE: ${{ github.event.issue.title }}
    ISSUE_BODY: ${{ github.event.issue.body }}
  run: uv run python .github/scripts/run_claude.py
```

## Dependencies

- 001-003-A (Agent SDK script)
