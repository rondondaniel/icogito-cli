from pathlib import Path
import os
from icogito.core import (
    create_scaffolding,
    get_doctor_status,
    create_agent_config,
    save_config,
)
from icogito.schemas.agents import AgentConfig


def test_create_scaffolding(tmp_path: Path):
    target_dir = tmp_path / "test_scaffold"
    paths = create_scaffolding(target_dir)

    assert target_dir.exists()
    assert len(paths) == 7
    for subdir in ["agents", "configs", "schemas", "prompts", "tools", "utils"]:
        assert (target_dir / subdir).is_dir()


def test_get_doctor_status():
    status = get_doctor_status(verbose=False)
    assert status["status"] == "OK"
    assert status["tools_available"] == ["web_search", "web_fetch", "web_crawl"]
    assert status["agent_factory_ready"] == "AgentFactory"
    assert "details" not in status


def test_get_doctor_status_verbose():
    status = get_doctor_status(verbose=True)
    assert status["status"] == "OK"
    assert status["details"] == "All services reporting nominal operations."


def test_create_agent_config(tmp_path: Path):
    prompts_dir = tmp_path / "prompts"
    configs_dir = tmp_path / "configs"

    config = create_agent_config(
        agent_name="my_agent",
        model_name="openai/gpt-4o-mini",
        model_providers=["openai"],
        allow_fallbacks=False,
        agent_instruction="You are a test agent.",
        selected_tools=["web_search"],
        sub_agents_names=["sub1"],
        prompts_dir=prompts_dir,
        configs_dir=configs_dir,
    )

    assert isinstance(config, AgentConfig)
    assert config.agent_name == "my_agent"
    assert config.model_name == "openai/gpt-4o-mini"
    assert config.instructions_path == f"{prompts_dir}/my_agent_instruction.md"
    assert config.config_file_path == f"{configs_dir}/my_agent_agent.yaml"
    assert config.subagents_list == ["sub1"]
    assert config.tools_list == ["web_search"]


def test_save_config(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "prompts").mkdir()
    (tmp_path / "configs").mkdir()

    config = create_agent_config(
        agent_name="saved_agent",
        model_name="openai/gpt-4o-mini",
        model_providers=["openai"],
        allow_fallbacks=False,
        agent_instruction="Instruction content",
        selected_tools=["web_search"],
    )

    save_config(config)

    assert (tmp_path / "configs" / "saved_agent_agent.yaml").exists()
    prompt_file = tmp_path / "prompts" / "saved_agent_instruction.md"
    assert prompt_file.exists()
    assert prompt_file.read_text() == "Instruction content"
