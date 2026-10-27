# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

`icogito` — Python CLI framework for building Agent/Multi-Agent systems on top of `pydantic-ai` + `pydantic-ai-harness`, with OpenRouter as the model provider and Tavily for web search/fetch/crawl tools. Requires Python >=3.12, uses `uv` for packaging (`uv_build` backend).

Scaffold CLI (`src/icogito/cli.py`) includes `init` (directory scaffolding), `doctor` (system status and tool check) and `configure` (interactive questionary flow that generates agent YAML configs + instruction prompts via `icogito.core`).

## Commands

```bash
uv sync                  # install deps + dev group (mypy, pytest) into .venv (per uv.lock)
uv run icogito           # run the CLI entrypoint (icogito.cli:main)
uv run python -m icogito.cli <command>  # alt invocation
uv run icogito configure # interactive agent config (writes configs/ + prompts/ under cwd)
uv run pytest            # run tests (pytest + pytest-mock, in tests/)
uv run mypy              # type-check src/ and tests/ (config in pyproject.toml)
```

Tests live in `tests/` (`test_cli.py` tests CLI commands and questionary flows using `CliRunner` and `monkeypatch`; `test_core.py` tests core logic; util tests cover load/save config and prompt helpers). `pythonpath = ["src"]` is configured in `pyproject.toml`. `TAVILY_API_KEY` must be set for Tavily web tools (tests mock or set dummy keys). mypy is configured in `pyproject.toml` and gates CI and release; `src/icogito/py.typed` marks the package typed. No linter configured.

## Architecture

Single package `icogito` under `src/icogito/`, registered in `pyproject.toml` with console script (`icogito = "icogito.cli:main"`).

- **`cli.py`** — Typer CLI entrypoint (`main()`, `app`). Defines `init`, `doctor`, and `configure` commands. Interactive prompt workflows use `questionary` and delegate file and config operations to `icogito.core`.
- **`core.py`** — Core operational functions bridging CLI commands and framework capabilities (`create_scaffolding`, `get_doctor_status`, `create_agent_config` writes the instruction prompt file, `save_config` writes the YAML).
- **`factory.py`** — `AgentFactory.create_agent(config, enable_prefect=False)` builds a `pydantic_ai.Agent` from an `AgentConfig`: sets up the OpenRouter model/provider, wires instructions/description/output_type/deps_type, and attaches capabilities (`IdentifiedToolOutputLimits`, optional `PrefectDurability` for durable execution, and — if `config.subagents_list` is set — `IdentifiedSubAgents`). Prefect imports (`from pydantic_ai.durable_exec.prefect import PrefectDurability, TaskConfig` / `from prefect import flow, task`) must always be wrapped in `try...except ImportError` blocks with `HAS_PREFECT` check to ensure safe dynamic imports. Tools/subagents are resolved from string names in `AgentConfig` via `tool_registry` / `subagent_configs` lookup maps, and subagents are built recursively via `create_subagent`.
- **`models.py`** — `AgentConfig` (pydantic model driving agent construction. Required: `model_name`, `agent_name`, `instructions_path`, `config_file_path`, `allow_fallbacks`, `settings_openrouter_provider_list`; optional: sub-agent instructions/description paths, tool/subagent name lists, output schema, deps type, retry/concurrency settings), `ResearchState` (dataclass tracking visited URLs / searched queries, passed as agent deps), and `UsageLimitErrorResponse` (structured usage-limit error).
- **`tools/tavily_web_tools.py`** — `web_search`, `web_fetch`, `web_crawl` tool functions backed by `AsyncTavilyClient`. Requires `TAVILY_API_KEY` in the environment; raises at import time if missing. Blocked/empty responses raise `ModelRetry` rather than returning an error silently, so the agent will retry with a fixed `BLOCKED_MESSAGE` instead of re-fetching the same blocked URL.
- **`utils/`** — modular helpers for loading/saving agent configurations and instruction prompts:
  - `load_agent_config.py` — loads YAML file into `AgentConfig`. Example configs in `examples/deep_research/configs/`.
  - `save_agent_config.py` / `save_prompt_instruction.py` — write `AgentConfig` YAML (`model_dump`) / instruction markdown.
  - `get_prompt_instruction.py` — resolves prompt instruction paths and reads instruction/description text.

### Known upstream workarounds

`IdentifiedToolOutputLimits` and `IdentifiedSubAgents` in `factory.py` both subclass a `pydantic-ai-harness` class solely to patch a bug: the base `get_toolset()` implementations build a leaf toolset but never stamp the parent's `id` onto it, which breaks Prefect/Temporal durable execution (a leaf toolset needs an id). Both overrides just call `super().get_toolset()` and set `._id` if missing. If upgrading `pydantic-ai-harness`, check whether this is still needed.

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
