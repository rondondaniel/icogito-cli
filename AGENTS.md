# AGENTS.md

Guidance for coding agents (Jules, Codex, etc.) working in this repo. Mirrors CLAUDE.md.

## Project

`icogito` — Python CLI framework for building Agent/Multi-Agent systems on top of `pydantic-ai` + `pydantic-ai-harness`, with OpenRouter as model provider and Tavily for web search/fetch/crawl tools. Requires Python >=3.12, uses `uv` for packaging (`uv_build` backend).

Scaffold CLI (`src/icogito/cli.py`) includes `init` (directory scaffolding), `doctor` (system status and tool check) and `configure` (interactive questionary flow that generates agent YAML configs + instruction prompts via `icogito.core`).

## Commands

```bash
uv sync                  # install deps into .venv (per uv.lock)
uv sync --extra test     # install deps + test extras into .venv
uv run icogito           # run the CLI entrypoint (icogito.cli:main)
uv run python -m icogito.cli <command>  # alt invocation
uv run icogito configure # interactive agent config (writes configs/ + prompts/ under cwd)
uv run --extra test pytest  # run tests (pytest + pytest-mock, in tests/)
```

Tests live in `tests/` (`test_cli.py` tests CLI commands and questionary flows using `CliRunner` and `monkeypatch`; `test_core.py` tests core logic; util tests cover load/save config and prompt helpers). `pythonpath = ["src"]` is configured in `pyproject.toml`. `TAVILY_API_KEY` must be set for Tavily web tools (tests mock or set dummy keys). No linter or type-checker configured in `pyproject.toml`.

## Architecture

Single package `icogito` under `src/icogito/`, registered in `pyproject.toml` with console script (`icogito = "icogito.cli:main"`).

- **`cli.py`** — Typer CLI entrypoint (`main()`, `app`). Defines `init`, `doctor`, and `configure` commands. Interactive prompt workflows use `questionary` and delegate file and config operations to `icogito.core`.
- **`core.py`** — Core operational functions bridging CLI commands and framework capabilities (`create_scaffolding`, `get_doctor_status`, `create_agent_config`, `save_config`).
- **`factory.py`** — `AgentFactory.create_agent(config)` builds a `pydantic_ai.Agent` from an `AgentConfig`: sets up OpenRouter model/provider, wires instructions/description/output_type/deps_type, and attaches capabilities (`IdentifiedToolOutputLimits`, `PrefectDurability` for durable execution, and — if `config.subagents_list` is set — `IdentifiedSubAgents`). Tools/subagents resolved from string names in `AgentConfig` via `tool_registry` / `subagent_configs` lookup maps; subagents built recursively via `create_subagent`.
- **`models.py`** — `AgentConfig` (pydantic model driving agent construction. Required: `model_name`, `agent_name`, `instructions_path`, `config_file_path`, `agent_instruction`, `allow_fallbacks`, `settings_openrouter_provider_list`; optional: sub-agent instructions/description paths, tool/subagent name lists, output schema, deps type, retry/concurrency settings), `ResearchState` (dataclass tracking visited URLs / searched queries, passed as agent deps), and `UsageLimitErrorResponse` (structured usage-limit error).
- **`tools/tavily_web_tools.py`** — `web_search`, `web_fetch`, `web_crawl` tool functions backed by `AsyncTavilyClient`. Requires `TAVILY_API_KEY` in environment; raises at import time if missing. Blocked/empty responses raise `ModelRetry` rather than returning error silently, so agent retries with fixed `BLOCKED_MESSAGE` instead of re-fetching same blocked URL.
- **`utils/`** — modular helpers for loading/saving agent configurations and instruction prompts:
  - `load_agent_config.py` — loads YAML file into `AgentConfig`. Example configs in `examples/deep_research/configs/`.
  - `save_agent_config.py` / `save_prompt_instruction.py` — write `AgentConfig` YAML (`model_dump`) / instruction markdown.
  - `get_prompt_instruction.py` — resolves prompt instruction paths and reads instruction/description text.

### Known upstream workarounds

`IdentifiedToolOutputLimits` and `IdentifiedSubAgents` in `factory.py` both subclass a `pydantic-ai-harness` class solely to patch a bug: base `get_toolset()` implementations build leaf toolset but never stamp parent's `id` onto it, which breaks Prefect/Temporal durable execution (leaf toolset needs an id). Both overrides just call `super().get_toolset()` and set `._id` if missing. If upgrading `pydantic-ai-harness`, check whether this is still needed.
