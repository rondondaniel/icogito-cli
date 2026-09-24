# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

`icogito-cli` — Python CLI framework for building Agent/Multi-Agent systems on top of `pydantic-ai` + `pydantic-ai-harness`, with OpenRouter as the model provider and Tavily for web search/fetch/crawl tools. Requires Python >=3.12, uses `uv` for packaging (uv_build backend).

Early-stage scaffold: `icogito_cli/cli.py` currently only has placeholder `init`/`doctor` Typer commands; the real agent-building logic lives in `icogito_lib/` but is not yet wired into the CLI.

## Commands

```bash
uv sync                  # install deps into .venv (per uv.lock)
uv run icogito-cli       # run the CLI entrypoint (icogito_cli.cli:app)
uv run python -m icogito_cli.cli <command>  # alt invocation
```

There are no tests, linter, or type-checker configured yet (no `tool.*` sections in `pyproject.toml`, no test directory). `.mypy_cache/` exists but mypy isn't declared as a dependency — verify before assuming it's runnable.

## Architecture

Two packages under `src/`, both `uv_build`-managed but only `icogito_cli` is registered as the installable package with a console script (`icogito-cli = "icogito_cli.cli:app"`) — `icogito_lib` has no build/package config of its own yet.

- **`icogito_cli/`** — Typer CLI shell (`cli.py`). Not yet connected to `icogito_lib`.
- **`icogito_lib/`** — the actual agent framework:
  - `schemas/agents.py` — `AgentConfig` (pydantic model driving agent construction: model name, instructions/description paths, tool/subagent name lists, output schema, deps type, retry/concurrency settings) and `ResearchState` (dataclass tracking visited URLs / searched queries, passed as agent deps).
  - `utils/load_agent_config.py` — loads a YAML file into an `AgentConfig`. No example YAML configs exist in the repo yet.
  - `utils/get_prompt_instruction.py` — resolves a path (relative paths are resolved against `icogito_lib/`, i.e. one level up from `utils/`) and reads it as the instruction/description text for an agent.
  - `tools/tavily_web_tools.py` — `web_search`, `web_fetch`, `web_crawl` tool functions backed by `AsyncTavilyClient`. Requires `TAVILY_API_KEY` in the environment (loaded via `.env`/`dotenv`); raises at import time if missing. Blocked/empty responses raise `ModelRetry` rather than returning an error silently, so the agent will retry with a fixed `BLOCKED_MESSAGE` instead of re-fetching the same blocked URL.
  - `agents/factory.py` — `AgentFactory.create_agent(config)` builds a `pydantic_ai.Agent` from an `AgentConfig`: sets up the OpenRouter model/provider, wires instructions/description/output_type/deps_type, and attaches capabilities (`IdentifiedToolOutputLimits`, `PrefectDurability` for durable execution, and — if `config.subagents_list` is set — `IdentifiedSubAgents`). Tools/subagents are resolved from string names in `AgentConfig` via `tool_registry` / `subagent_configs` lookup maps, and subagents are built recursively via `create_subagent`.

### Known upstream workarounds

`IdentifiedToolOutputLimits` and `IdentifiedSubAgents` in `factory.py` both subclass a `pydantic-ai-harness` class solely to patch a bug: the base `get_toolset()` implementations build a leaf toolset but never stamp the parent's `id` onto it, which breaks Prefect/Temporal durable execution (a leaf toolset needs an id). Both overrides just call `super().get_toolset()` and set `._id` if missing. If upgrading `pydantic-ai-harness`, check whether this is still needed.

### Import style caveat

Modules within `icogito_lib` import each other with bare top-level names (e.g. `from schemas.agents import AgentConfig`, `from utils.get_prompt_instruction import get_prompt_instruction`), not `icogito_lib.schemas...`. This only resolves if `icogito_lib/` itself is on `sys.path` (not just `src/`) — currently there's no package/path config guaranteeing that. Be aware when adding new cross-module imports or wiring `icogito_lib` into `icogito_cli`.

### Declared vs. used dependencies

`pyproject.toml` dependencies: `loguru`, `pydantic`, `pydantic-ai`, `pydantic-ai-harness`, `tavily-python`, `typer`. Code also imports `yaml` (PyYAML), `dotenv` (python-dotenv), and `pydantic_ai.durable_exec.prefect` (Prefect) without declaring them directly — likely transitive via `pydantic-ai-harness`/`pydantic-ai`, but confirm with `uv tree` before relying on them.

<!-- rtk-instructions v2 -->
# Command output

Command output here is condensed to save tokens, keeping every signal and
dropping costly noise. Treat it as the complete result: run commands
normally, and batch related commands into one call to avoid extra turns.
Truncated results state their recovery path in their own output. Re-run a
command as `rtk proxy <cmd>` only when its result is unusable: empty when
output was clearly expected, contradicting its exit code, or garbled.
<!-- /rtk-instructions -->

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
