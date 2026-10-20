import pytest
from pathlib import Path
from icogito.factory import AgentFactory
from icogito.core import create_agent_config, save_config
from pydantic_ai import Agent
from pydantic_ai.models.openrouter import OpenRouterModel


def test_agent_factory_create_agent(tmp_path: Path):
    prompts_dir = tmp_path / "prompts"
    configs_dir = tmp_path / "configs"

    config = create_agent_config(
        agent_name="test_agent",
        model_name="openai/gpt-4o-mini",
        model_providers=["openai"],
        allow_fallbacks=False,
        agent_instruction="You are a helpful assistant.",
        selected_tools=["web_search"],
        prompts_dir=prompts_dir,
        configs_dir=configs_dir,
    )
    save_config(config)

    factory = AgentFactory(openrouter_api_key="test-api-key")
    agent = factory.create_agent(config)

    assert isinstance(agent, Agent)
    assert isinstance(agent.model, OpenRouterModel)
    assert agent.name == "test_agent"
