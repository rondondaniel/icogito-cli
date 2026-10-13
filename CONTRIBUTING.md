# Contributing to icogito

Thank you for your interest in contributing to `icogito`! This document provides guidelines and instructions for setting up your development environment, following our `uv`-based packaging workflow, and submitting pull requests.

---

## Prerequisites

- **Python 3.12+**: `icogito` requires Python 3.12 or newer.
- **uv**: We use [`uv`](https://github.com/astral-sh/uv) for fast, deterministic dependency management and virtual environment execution.

---

## Local Development & `uv` Packaging Workflow

### 1. Installation & Environment Setup

Install `uv` if you haven't already (refer to [astral-sh/uv installation docs](https://docs.astral.sh/uv/getting-started/installation/)).

Clone the repository and install all dependencies (including test dependencies) into the local virtual environment (`.venv`):

```bash
git clone https://github.com/your-org/icogito.git
cd icogito

# Sync base dependencies and test dependencies into .venv
uv sync --extra test
```

### 2. Running the CLI Locally

You can execute the CLI entrypoint directly with `uv run`:

```bash
uv run icogito --help
```

Alternatively, invoke via Python module:

```bash
uv run python -m icogito.cli --help
```

### 3. Running Tests

We use `pytest` for testing. Ensure test dependencies are synced (`uv sync --extra test`), then run pytest:

```bash
uv run --extra test pytest
```

---

## Repository Structure Overview

```
icogito/
├── src/
│   └── icogito/        # Core agent framework and CLI commands
│       ├── agents/     # Agent factory and creation logic
│       ├── configs/    # Agent YAML configurations
│       ├── prompts/    # Instruction prompt markdown templates
│       ├── schemas/    # Pydantic schemas and models
│       ├── tools/      # Tool integrations (e.g., Tavily web tools)
│       ├── utils/      # Helper utilities (loading/saving configs, prompts)
│       ├── cli.py      # Typer CLI application entrypoint and commands
│       └── core.py     # Core workflow and business logic functions
├── tests/              # Test suite
├── .github/            # GitHub templates and workflows
├── pyproject.toml      # Project configuration and dependencies
└── uv.lock             # Lockfile for reproducible builds
```

- **`src/icogito/`**: Single package containing CLI commands built with Typer (`cli.py`), core operational logic (`core.py`), and framework infrastructure (`agents/`, `schemas/`, `tools/`, `utils/`, etc.).

---

## Contributing Guidelines

### Submitting Issues

Before opening a new issue, please search existing issues to see if it has already been reported.

- Use the **Bug Report** template for bugs, including steps to reproduce, expected behavior, and system details.
- Use the **Feature Request** template for new capabilities or improvements.

Note: GitHub issues are synchronized with our internal Linear workspace for tracking and project management.

### Submitting Pull Requests

1. **Fork & Branch**: Create a new feature or bugfix branch off `main`:
   ```bash
   git checkout -b feature/my-new-feature
   ```
2. **Implement & Test**: Write clean code and add corresponding unit tests under `tests/`. Verify tests pass locally:
   ```bash
   uv run --extra test pytest
   ```
3. **Commit & Push**: Keep commits atomic and descriptive.
4. **Open Pull Request**: Fill out all sections of the Pull Request template.

---

## Code Style & Standards

- Follow PEP 8 guidelines.
- Use explicit type hints for function signatures and data models.
- Prefer `pydantic` models for structured data and configuration schemas.
