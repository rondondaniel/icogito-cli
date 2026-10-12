# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

`icogito-cli` — Python CLI framework for building Agent/Multi-Agent systems on top of `pydantic-ai` + `pydantic-ai-harness`, with OpenRouter as the model provider and Tavily for web search/fetch/crawl tools. Requires Python >=3.12, uses `uv` for packaging (uv_build backend).

Early-stage scaffold: `icogito_cli/cli.py` has `init` (directory scaffolding), `doctor` (import/status check) and `configure` (interactive questionary flow that writes agent YAML configs + instruction prompts via `icogito_lib` utils). It does not yet build or run agents from those configs.

## Commands

```bash
uv sync                  # install deps into .venv (per uv.lock)
uv run icogito-cli       # run the CLI entrypoint (icogito_cli.cli:app)
uv run python -m icogito_cli.cli <command>  # alt invocation
uv run icogito-cli configure   # interactive agent config (writes configs/ + prompts/ under cwd)
uv run --extra test pytest     # run tests (pytest + pytest-mock, in tests/)
```

Tests live in `tests/` (`test_cli.py` mocks `questionary` prompts with ordered `side_effect` answer lists and uses `tmp_path` + `monkeypatch.chdir`; util tests cover load/save config and prompt helpers). `TAVILY_API_KEY` must be set before importing `cli.py` (tests set a dummy). No linter or type-checker configured (no `tool.*` sections in `pyproject.toml`). `.mypy_cache/` exists but mypy isn't declared as a dependency — verify before assuming it's runnable.

## Architecture

Two packages under `src/`, both `uv_build`-managed but only `icogito_cli` is registered as the installable package with a console script (`icogito-cli = "icogito_cli.cli:app"`) — `icogito_lib` has no build/package config of its own yet.

- **`icogito_cli/`** — Typer CLI shell (`cli.py`). Imports `icogito_lib` (`AgentFactory`, Tavily tools, `AgentConfig`, save utils). `configure` asks (via `questionary`) whether to enable multi-agent mode and how many root agents, then `agent_config()` prompts per agent: name, OpenRouter model, providers, fallbacks, instructions, tools, number of sub-agents (sub-agents are prompted recursively with `is_sub_agent=True`, one level only). `save_config()` writes `configs/<name>_agent.yaml` and `prompts/<name>_instruction.md` relative to the cwd. No cancel handling: a `None` answer from questionary crashes on `int(None)`.
- **`icogito_lib/`** — the actual agent framework:
  - `schemas/agents.py` — `AgentConfig` (pydantic model driving agent construction. Required: `model_name`, `agent_name`, `instructions_path`, `config_file_path`, `agent_instruction`, `allow_fallbacks`, `settings_openrouter_provider_list`; optional: sub-agent instructions/description paths, tool/subagent name lists, output schema, deps type, retry/concurrency settings) and `ResearchState` (dataclass tracking visited URLs / searched queries, passed as agent deps).
  - `utils/load_agent_config.py` — loads YAML file into `AgentConfig`. Example configs in `examples/deep_research/configs/`.
  - `utils/save_agent_config.py` / `utils/save_prompt_instruction.py` — write `AgentConfig` YAML (`model_dump`) / instruction markdown. Return `None` for empty path; relative paths resolve against cwd; missing parent dir raises `FileNotFoundError` (callers must mkdir first, as `cli.py` does).
  - `utils/get_prompt_instruction.py` — resolves a path (relative paths are resolved against `icogito_lib/`, i.e. one level up from `utils/`) and reads it as the instruction/description text for an agent.
  - `tools/tavily_web_tools.py` — `web_search`, `web_fetch`, `web_crawl` tool functions backed by `AsyncTavilyClient`. Requires `TAVILY_API_KEY` in the environment (loaded via `.env`/`dotenv`); raises at import time if missing. Blocked/empty responses raise `ModelRetry` rather than returning an error silently, so the agent will retry with a fixed `BLOCKED_MESSAGE` instead of re-fetching the same blocked URL.
  - `agents/factory.py` — `AgentFactory.create_agent(config)` builds a `pydantic_ai.Agent` from an `AgentConfig`: sets up the OpenRouter model/provider, wires instructions/description/output_type/deps_type, and attaches capabilities (`IdentifiedToolOutputLimits`, `PrefectDurability` for durable execution, and — if `config.subagents_list` is set — `IdentifiedSubAgents`). Tools/subagents are resolved from string names in `AgentConfig` via `tool_registry` / `subagent_configs` lookup maps, and subagents are built recursively via `create_subagent`.

### Known upstream workarounds

`IdentifiedToolOutputLimits` and `IdentifiedSubAgents` in `factory.py` both subclass a `pydantic-ai-harness` class solely to patch a bug: the base `get_toolset()` implementations build a leaf toolset but never stamp the parent's `id` onto it, which breaks Prefect/Temporal durable execution (a leaf toolset needs an id). Both overrides just call `super().get_toolset()` and set `._id` if missing. If upgrading `pydantic-ai-harness`, check whether this is still needed.

### Import style caveat

`cli.py` prepends both `src/` and `src/icogito_lib/` to `sys.path` and imports with the `icogito_lib.` prefix. Modules within `icogito_lib` import each other with a mix of bare names (e.g. `from schemas.agents import AgentConfig`) and `icogito_lib.`-prefixed names (e.g. the save/load utils). Bare names only resolve if `icogito_lib/` is on `sys.path` — currently only guaranteed by that `cli.py` hack, no package/path config. Be aware when adding cross-module imports.

### Declared vs. used dependencies

`pyproject.toml` dependencies: `graphifyy`, `loguru`, `prefect`, `pydantic`, `pydantic-ai`, `pydantic-ai-harness`, `pyyaml`, `questionary`, `tavily-python`, `typer`; optional `test` extra: `pytest`, `pytest-mock`. `dotenv` (python-dotenv) is imported without being declared — likely transitive; confirm with `uv tree`.

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
