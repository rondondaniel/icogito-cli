import yaml
from pathlib import Path

from icogito_lib.utils.save_agent_config import save_agent_config
from icogito_lib.schemas.agents import AgentConfig


def _make_config(agent_name: str = "test_agent") -> AgentConfig:
    return AgentConfig(
        model_name="openai/gpt-4o-mini",
        agent_name=agent_name,
        instructions_path="prompts/test.md",
        settings_openrouter_provider_list=["openai"],
        tools_list=["web_search"],
        subagents_list=[],
        retries_output=3,
        max_concurrency=2,
    )


def test_save_agent_config_none_or_empty():
    assert save_agent_config(None, _make_config()) is None
    assert save_agent_config("", _make_config()) is None


def test_save_agent_config_absolute_path(tmp_path: Path):
    config_file = tmp_path / "configs" / "agent.yaml"
    config_file.parent.mkdir(parents=True, exist_ok=True)

    result = save_agent_config(config_file, _make_config())

    assert result == config_file
    assert config_file.exists()
    saved = yaml.safe_load(config_file.read_text())
    assert saved["agent_name"] == "test_agent"


def test_save_agent_config_relative_path_resolves_against_cwd(tmp_path: Path, monkeypatch):
    # Regression test: relative paths must resolve against the current working
    # directory (matching the mkdir calls in cli.py), not a hardcoded PROJECT_ROOT.
    monkeypatch.chdir(tmp_path)
    (tmp_path / "configs").mkdir()

    result = save_agent_config("configs/agent.yaml", _make_config())

    assert result == tmp_path / "configs" / "agent.yaml"
    assert (tmp_path / "configs" / "agent.yaml").exists()


def test_save_agent_config_missing_parent_dir_raises(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    try:
        save_agent_config("nonexistent_dir/agent.yaml", _make_config())
        assert False, "expected FileNotFoundError"
    except FileNotFoundError:
        pass
