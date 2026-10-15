# icogito

> A modern Python CLI framework to build Agent/Multi-Agent systems on top of `pydantic-ai`, `pydantic-ai-harness`, OpenRouter, and Tavily tools.

`icogito` provides an end-to-end toolkit for scaffolding, configuring, and running production-grade AI agent and multi-agent architectures. It integrates durable execution via Prefect, modular tool registry integration (including Tavily search, fetch, and crawl tools), and OpenRouter model routing.

---

## Key Features

- **CLI-Driven Scaffolding**: Easily create standardized directory structures (`agents/`, `configs/`, `prompts/`, `schemas/`, `tools/`, `utils/`) using `icogito init`.
- **Interactive Configuration**: Build single-agent and multi-agent workflow configurations interactively with `icogito configure`.
- **System Diagnostics**: Verify tools, environment setup, and framework status with `icogito doctor`.
- **Agent Factory**: Instantiates `pydantic-ai` Agents dynamically from YAML configurations (`AgentConfig`).
- **Durable Execution & Subagents**: Supports task durability via `PrefectDurability` and hierarchical multi-agent delegation via `SubAgents`.
- **Built-in Web Tools**: Tavily web integration for search, fetch, and crawl capabilities with built-in retry handling.

---

## Get Started

### Prerequisites

- **Python**: Version `>= 3.12`
- **uv**: Recommended fast Python package and environment manager ([docs.astral.sh/uv](https://docs.astral.sh/uv/))
- **API Keys**:
  - `OPENROUTER_API_KEY`: Required for model inference via OpenRouter.
  - `TAVILY_API_KEY`: Required when using Tavily web tools (`web_search`, `web_fetch`, `web_crawl`).

### Installation

Clone the repository and install dependencies using `uv`:

```bash
# Clone the repository
git clone https://github.com/danielrondon/icogito.git
cd icogito

# Sync project dependencies into .venv
uv sync

# (Optional) Sync test extra dependencies if developing or running tests
uv sync --extra test
```

### Local Environment Setup

Configure your environment variables before running agent workflows or tools:

```bash
export OPENROUTER_API_KEY="your-openrouter-api-key"
export TAVILY_API_KEY="your-tavily-api-key"
```

---

## Usage

### CLI Commands

The `icogito` CLI provides commands for project initialization, diagnostics, and agent configuration.

#### 1. Initialize Project Scaffolding (`icogito init`)

Scaffold a standard agent directory structure in your project or a target directory:

```bash
# Initialize scaffolding in the current directory
uv run icogito init

# Or specify a target directory
uv run icogito init ./my_agent_project
```

This creates the following directory layout:
```
.
├── agents/
├── configs/
├── prompts/
├── schemas/
├── tools/
└── utils/
```

#### 2. System Diagnostics (`icogito doctor`)

Check system environment status, global app directory path, available Tavily web tools, and `AgentFactory` readiness:

```bash
# Run standard diagnostic check
uv run icogito doctor

# Verbose diagnostic output
uv run icogito doctor --verbose
```

#### 3. Interactive Agent Configuration (`icogito configure`)

Interactively configure single or multi-agent systems. This wizard prompts for agent names, OpenRouter models, providers, instructions, enabled tools, and subagents, then generates the corresponding YAML configs in `configs/` and Markdown instructions in `prompts/`:

```bash
uv run icogito configure
```

---

### Programmatic Usage

`icogito` provides high-level utilities and `AgentFactory` for loading configs and instantiating runtime agents.

#### Loading Configuration and Instantiating Agents

```python
import os
from icogito.factory import AgentFactory
from icogito.utils.load_agent_config import load_agent_config

# Load agent configuration from YAML
config = load_agent_config("configs/research_agent_config.yaml")

# Initialize AgentFactory with your OpenRouter API Key
factory = AgentFactory(openrouter_api_key=os.getenv("OPENROUTER_API_KEY"))

# Create a pydantic-ai Agent instance
agent = factory.create_agent(config)

# Run the agent (async)
# result = await agent.run("Research recent developments in AI agent frameworks.")
```

#### Multi-Agent Setup with Subagents

When building a multi-agent system, subagent configurations are registered with `AgentFactory`:

```python
from icogito.factory import AgentFactory
from icogito.utils.load_agent_config import load_agent_config

# Load root agent config and subagent configs
sub_config = load_agent_config("configs/sub_researcher_config.yaml")
root_config = load_agent_config("configs/root_manager_config.yaml")

# Register subagent configs map
subagent_configs = {
    sub_config.agent_name: sub_config
}

factory = AgentFactory(
    openrouter_api_key=os.getenv("OPENROUTER_API_KEY"),
    subagent_configs=subagent_configs
)

# Build the root agent (automatically wires subagents recursively)
root_agent = factory.create_agent(root_config)
```

---

## Development & Testing

To run the full test suite using `pytest`:

```bash
uv run --extra test pytest
```

---

## Authors

- **Daniel Rondon** — [hello@danielrondon.com](mailto:hello@danielrondon.com)
