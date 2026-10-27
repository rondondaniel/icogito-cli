import pytest
from pathlib import Path
from icogito.factory import AgentFactory, HAS_PREFECT
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
        instruction_text="You are a helpful assistant.",
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
    # instructions must come from the on-disk prompt file via get_prompt_instruction
    assert (prompts_dir / "test_agent_instruction.md").read_text() == "You are a helpful assistant."
    assert "You are a helpful assistant." in str(agent._instructions)


def test_agent_factory_prefect_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    prompts_dir = tmp_path / "prompts"
    configs_dir = tmp_path / "configs"

    config = create_agent_config(
        agent_name="test_agent_prefect",
        model_name="openai/gpt-4o-mini",
        model_providers=["openai"],
        allow_fallbacks=False,
        instruction_text="You are a helpful assistant.",
        selected_tools=[],
        prompts_dir=prompts_dir,
        configs_dir=configs_dir,
    )
    save_config(config)

    factory = AgentFactory(openrouter_api_key="test-api-key")

    monkeypatch.setattr("icogito.factory.HAS_PREFECT", False)

    with pytest.raises(ImportError) as exc_info:
        factory.create_agent(config, enable_prefect=True)

    assert "pip install \"icogito[prefect]\"" in str(exc_info.value)


def test_agent_factory_prefect_enabled(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    prompts_dir = tmp_path / "prompts"
    configs_dir = tmp_path / "configs"

    config = create_agent_config(
        agent_name="test_agent_prefect",
        model_name="openai/gpt-4o-mini",
        model_providers=["openai"],
        allow_fallbacks=False,
        instruction_text="You are a helpful assistant.",
        selected_tools=[],
        prompts_dir=prompts_dir,
        configs_dir=configs_dir,
    )
    save_config(config)

    factory = AgentFactory(openrouter_api_key="test-api-key")

    # Mock PrefectDurability and TaskConfig
    class DummyTaskConfig:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    class DummyPrefectDurability:
        def __init__(self, model_task_config):
            self.model_task_config = model_task_config

    monkeypatch.setattr("icogito.factory.HAS_PREFECT", True)
    monkeypatch.setattr("icogito.factory.PrefectDurability", DummyPrefectDurability)
    monkeypatch.setattr("icogito.factory.TaskConfig", DummyTaskConfig)

    agent = factory.create_agent(config, enable_prefect=True)
    assert isinstance(agent, Agent)
    assert agent._root_capability is not None
