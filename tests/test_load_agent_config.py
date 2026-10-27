import pytest
from pydantic import ValidationError
from pathlib import Path
from icogito.utils.load_agent_config import load_agent_config
from icogito.models import AgentConfig


def test_load_agent_config_success(tmp_path: Path):
    yaml_content = """
model_name: "openai/gpt-4o-mini"
agent_name: "test_agent"
instructions_path: "prompts/test.md"
config_file_path: "configs/test_agent.yaml"
allow_fallbacks: false
settings_openrouter_provider_list:
  - "openai"
tools_list:
  - "web_search"
subagents_list: []
retries_output: 3
max_concurrency: 2
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    config = load_agent_config(str(yaml_file))

    assert isinstance(config, AgentConfig)
    assert config.model_name == "openai/gpt-4o-mini"
    assert config.agent_name == "test_agent"
    assert config.instructions_path == "prompts/test.md"
    assert config.config_file_path == "configs/test_agent.yaml"
    assert config.allow_fallbacks is False
    assert config.settings_openrouter_provider_list == ["openai"]
    assert config.tools_list == ["web_search"]
    assert config.subagents_list == []
    assert config.retries_output == 3
    assert config.max_concurrency == 2


def test_load_agent_config_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_agent_config("non_existent_config_file.yaml")


def test_load_agent_config_missing_required_fields(tmp_path: Path):
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text('model_name: "openai/gpt-4o-mini"\nagent_name: "a"\n', encoding="utf-8")

    with pytest.raises(ValidationError):
        load_agent_config(str(yaml_file))
