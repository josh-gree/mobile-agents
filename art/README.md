# Art Library

An isolated Python library with its own development tooling and CI pipeline.

## Overview

The `art` library is a standalone Python package designed to demonstrate an isolated subdirectory setup within a monorepo. It has its own dependencies, testing framework, and CI pipeline that only triggers on changes to this directory.

## Features

- ✨ Isolated Python package with modern tooling
- 🧪 Testing with pytest
- 🔍 Linting and formatting with ruff
- 🚀 Dedicated CI/CD pipeline
- 📦 Dependency management with uv

## Installation

### Development Setup

1. Navigate to the art directory:
   ```bash
   cd art
   ```

2. Install dependencies using uv:
   ```bash
   uv sync
   ```

This will create a virtual environment and install all dependencies including development tools.

## Usage

### Running Tests

```bash
cd art
uv run pytest
```

For verbose output:
```bash
uv run pytest -v
```

### Linting and Formatting

Check code quality:
```bash
uv run ruff check .
```

Auto-fix issues:
```bash
uv run ruff check . --fix
```

Check formatting:
```bash
uv run ruff format --check .
```

Format code:
```bash
uv run ruff format .
```

## Project Structure

```
art/
├── src/
│   └── art/
│       ├── __init__.py      # Package initialization
│       └── example.py       # Example module
├── tests/
│   ├── __init__.py
│   └── test_example.py      # Example tests
├── pyproject.toml           # Package configuration
├── uv.lock                  # Locked dependencies
├── .python-version          # Python version (3.12)
└── README.md                # This file
```

## Development Workflow

1. **Make changes** to the code in `src/art/`
2. **Write tests** in `tests/`
3. **Run tests** with `uv run pytest`
4. **Check code quality** with `uv run ruff check .`
5. **Format code** with `uv run ruff format .`
6. **Commit changes** - CI will automatically run on push

## CI/CD

The art library has its own dedicated CI pipeline (`.github/workflows/art-ci.yml`) that:

- ✅ Triggers only on changes to the `art/` directory
- ✅ Runs linting checks (ruff)
- ✅ Runs formatting checks (ruff format)
- ✅ Runs the test suite (pytest)
- ✅ Operates independently from the main project CI

## Contributing

1. Make your changes in a feature branch
2. Ensure all tests pass: `uv run pytest`
3. Ensure code quality checks pass: `uv run ruff check .`
4. Ensure code is formatted: `uv run ruff format .`
5. Submit a pull request

## Requirements

- Python 3.12 or higher
- uv package manager

## License

[Add your license information here]
