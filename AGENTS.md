# AGENTS.md

Guidance for coding agents (Jules, Codex, etc.) working in this repo. Mirrors CLAUDE.md.

## Project

`icogito-cli` — Python CLI framework for building Agent/Multi-Agent systems on top of `pydantic-ai` + `pydantic-ai-harness`, with OpenRouter as model provider and Tavily for web search/fetch/crawl tools. Requires Python >=3.12, uses `uv` for packaging (uv_build backend).

Early-stage scaffold: `icogito_cli/cli.py` currently only has placeholder `init`/`doctor` Typer commands; real agent-building logic lives in `icogito_lib/` but is not yet wired into the CLI.

## Commands

```bash
uv sync                  # install deps into .venv (per uv.lock)
uv run icogito-cli       # run the CLI entrypoint (icogito_cli.cli:app)
uv run python -m icogito_cli.cli <command>  # alt invocation
```

No tests, linter, or type-checker configured yet (no `tool.*` sections in `pyproject.toml`, no test directory). `.mypy_cache/` exists but mypy isn't declared as a dependency — verify before assuming it's runnable.

## Architecture

Two packages under `src/`, both `uv_build`-managed but only `icogito_cli` is registered as installable package with console script (`icogito-cli = "icogito_cli.cli:app"`) — `icogito_lib` has no build/package config of its own yet.

- **`icogito_cli/`** — Typer CLI shell (`cli.py`). Not yet connected to `icogito_lib`.
- **`icogito_lib/`** — actual agent framework:
  - `schemas/agents.py` — `AgentConfig` (pydantic model driving agent construction: model name, instructions/description paths, tool/subagent name lists, output schema, deps type, retry/concurrency settings) and `ResearchState` (dataclass tracking visited URLs / searched queries, passed as agent deps).
  - `utils/load_agent_config.py` — loads YAML file into `AgentConfig`. No example YAML configs exist in repo yet.
  - `utils/get_prompt_instruction.py` — resolves path (relative paths resolved against `icogito_lib/`, one level up from `utils/`) and reads it as instruction/description text for an agent.
  - `tools/tavily_web_tools.py` — `web_search`, `web_fetch`, `web_crawl` tool functions backed by `AsyncTavilyClient`. Requires `TAVILY_API_KEY` in environment (loaded via `.env`/`dotenv`); raises at import time if missing. Blocked/empty responses raise `ModelRetry` rather than returning error silently, so agent retries with fixed `BLOCKED_MESSAGE` instead of re-fetching same blocked URL.
  - `agents/factory.py` — `AgentFactory.create_agent(config)` builds `pydantic_ai.Agent` from `AgentConfig`: sets up OpenRouter model/provider, wires instructions/description/output_type/deps_type, attaches capabilities (`IdentifiedToolOutputLimits`, `PrefectDurability` for durable execution, and — if `config.subagents_list` set — `IdentifiedSubAgents`). Tools/subagents resolved from string names in `AgentConfig` via `tool_registry` / `subagent_configs` lookup maps; subagents built recursively via `create_subagent`.

### Known upstream workarounds

`IdentifiedToolOutputLimits` and `IdentifiedSubAgents` in `factory.py` both subclass a `pydantic-ai-harness` class solely to patch a bug: base `get_toolset()` implementations build leaf toolset but never stamp parent's `id` onto it, which breaks Prefect/Temporal durable execution (leaf toolset needs an id). Both overrides just call `super().get_toolset()` and set `._id` if missing. If upgrading `pydantic-ai-harness`, check whether this is still needed.

### Import style caveat

Modules within `icogito_lib` import each other with bare top-level names (e.g. `from schemas.agents import AgentConfig`, `from utils.get_prompt_instruction import get_prompt_instruction`), not `icogito_lib.schemas...`. This only resolves if `icogito_lib/` itself is on `sys.path` (not just `src/`) — currently no package/path config guarantees that. Be aware when adding new cross-module imports or wiring `icogito_lib` into `icogito_cli`.

### Declared vs. used dependencies

`pyproject.toml` dependencies: `loguru`, `pydantic`, `pydantic-ai`, `pydantic-ai-harness`, `tavily-python`, `typer`. Code also imports `yaml` (PyYAML), `dotenv` (python-dotenv), and `pydantic_ai.durable_exec.prefect` (Prefect) without declaring them directly — likely transitive via `pydantic-ai-harness`/`pydantic-ai`, but confirm with `uv tree` before relying on them.
