import os
from pathlib import Path
import pytest

# Ensure TAVILY_API_KEY is set in environment so tool imports in core.py don't fail
os.environ["TAVILY_API_KEY"] = "dummy-test-key"

from icogito.core import (
    create_scaffolding,
    get_doctor_status,
    create_agent_config,
    save_config,
)
from icogito.schemas.agents import AgentConfig


def test_create_scaffolding(tmp_path: Path):
    target_dir = tmp_path / "my_agent_project"
    created_paths = create_scaffolding(target_dir)

    assert target_dir in created_paths
    assert target_dir.exists()
    assert target_dir.is_dir()

    expected_subdirs = ["agents", "configs", "schemas", "prompts", "tools", "utils"]
    for subdir in expected_subdirs:
        sub_path = target_dir / subdir
        assert sub_path.exists()
        assert sub_path.is_dir()
        assert sub_path in created_paths


def test_get_doctor_status_default():
    status = get_doctor_status(verbose=False)
    assert status["status"] == "OK"
    assert status["tools_available"] == ["web_search", "web_fetch", "web_crawl"]
    assert status["agent_factory_ready"] == "AgentFactory"
    assert "details" not in status


def test_get_doctor_status_verbose():
    status = get_doctor_status(verbose=True)
    assert status["status"] == "OK"
    assert status["tools_available"] == ["web_search", "web_fetch", "web_crawl"]
    assert status["agent_factory_ready"] == "AgentFactory"
    assert status["details"] == "All services reporting nominal operations."


def test_create_agent_config(tmp_path: Path):
    prompts_dir = tmp_path / "prompts"
    configs_dir = tmp_path / "configs"

    config = create_agent_config(
        agent_name="researcher",
        model_name="openai/gpt-4o-mini",
        model_providers=["openai"],
        allow_fallbacks=True,
        agent_instruction="Research topics thoroughly.",
        selected_tools=["web_search"],
        sub_agents_names=["sub_researcher"],
        prompts_dir=prompts_dir,
        configs_dir=configs_dir,
    )

    assert isinstance(config, AgentConfig)
    assert config.agent_name == "researcher"
    assert config.model_name == "openai/gpt-4o-mini"
    assert config.settings_openrouter_provider_list == ["openai"]
    assert config.allow_fallbacks is True
    assert config.agent_instruction == "Research topics thoroughly."
    assert config.tools_list == ["web_search"]
    assert config.subagents_list == ["sub_researcher"]

    assert config.instructions_path == f"{prompts_dir}/researcher_instruction.md"
    assert config.config_file_path == f"{configs_dir}/researcher_agent.yaml"

    assert prompts_dir.exists()
    assert configs_dir.exists()


def test_save_config(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    config = create_agent_config(
        agent_name="writer",
        model_name="openai/gpt-4o-mini",
        model_providers=["openai"],
        allow_fallbacks=False,
        agent_instruction="Write concise summaries.",
        selected_tools=["web_search"],
        prompts_dir="prompts",
        configs_dir="configs",
    )

    save_config(config)

    yaml_file = tmp_path / "configs" / "writer_agent.yaml"
    instruction_file = tmp_path / "prompts" / "writer_instruction.md"

    assert yaml_file.exists()
    assert instruction_file.exists()
    assert instruction_file.read_text() == "Write concise summaries."
