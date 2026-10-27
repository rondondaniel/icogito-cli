import os
from pathlib import Path
import pytest
from typer.testing import CliRunner

# Ensure TAVILY_API_KEY is set in environment so imports in cli.py don't fail
os.environ["TAVILY_API_KEY"] = "dummy-test-key"

import typer
from icogito.cli import app, main, prompt_agent_config, get_global_app_dir

runner = CliRunner()


def test_get_global_app_dir(mocker, tmp_path: Path):
    fake_global_dir = tmp_path / ".config" / "icogito"
    mocker.patch("typer.get_app_dir", return_value=str(fake_global_dir))

    global_dir = get_global_app_dir()
    assert global_dir == fake_global_dir
    assert fake_global_dir.exists()


def test_doctor_command(mocker, tmp_path: Path):
    fake_global_dir = tmp_path / ".config" / "icogito"
    mocker.patch("typer.get_app_dir", return_value=str(fake_global_dir))

    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "System status: OK" in result.stdout
    assert f"Global App Directory: {fake_global_dir}" in result.stdout
    assert "Available Tavily tools: web_search, web_fetch, web_crawl" in result.stdout
    assert "AgentFactory ready: AgentFactory" in result.stdout


def test_doctor_command_verbose(mocker, tmp_path: Path):
    fake_global_dir = tmp_path / ".config" / "icogito"
    mocker.patch("typer.get_app_dir", return_value=str(fake_global_dir))

    result = runner.invoke(app, ["doctor", "--verbose"])
    assert result.exit_code == 0
    assert "System status: OK" in result.stdout
    assert "Detailed logs: All services reporting nominal operations." in result.stdout


def test_init_command_positional_arg(tmp_path: Path):
    target_dir = tmp_path / "scaffold_test"
    result = runner.invoke(app, ["init", str(target_dir)])
    assert result.exit_code == 0
    assert f"Initializing agent scaffolding at {target_dir}..." in result.stdout
    assert f"Successfully generated directory structure at {target_dir}." in result.stdout
    assert (target_dir / "configs").exists()
    assert (target_dir / "prompts").exists()
    assert (target_dir / "agents").exists()
    assert (target_dir / "schemas").exists()
    assert (target_dir / "tools").exists()
    assert (target_dir / "utils").exists()


def test_init_command_default_cwd(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["init", "."])
    assert result.exit_code == 0
    assert (tmp_path / "configs").exists()
    assert (tmp_path / "agents").exists()
    assert (tmp_path / "schemas").exists()
    assert (tmp_path / "prompts").exists()
    assert (tmp_path / "tools").exists()
    assert (tmp_path / "utils").exists()


def _mock_questionary(mocker, text, select, checkbox, confirm):
    """Patch questionary prompts; each arg is the ordered list of answers."""
    for name, answers in (
        ("text", text),
        ("select", select),
        ("checkbox", checkbox),
        ("confirm", confirm),
    ):
        mocker.patch(f"questionary.{name}").return_value.ask.side_effect = answers


def test_prompt_agent_config_direct(mocker, tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _mock_questionary(
        mocker,
        text=["test_interactive_agent", "Direct test instructions", "0"],
        select=["openai/gpt-4o-mini"],
        checkbox=[["openai"], ["web_search"]],
        confirm=[True],
    )

    config = prompt_agent_config("test-agent")

    assert config.agent_name == "test_interactive_agent"
    assert config.model_name == "openai/gpt-4o-mini"
    assert config.settings_openrouter_provider_list == ["openai"]
    assert config.allow_fallbacks is True
    assert (tmp_path / config.instructions_path).read_text() == "Direct test instructions"
    assert config.tools_list == ["web_search"]
    assert config.subagents_list == []


def test_configure_command_single_agent(tmp_path: Path, monkeypatch, mocker):
    monkeypatch.chdir(tmp_path)
    agent_name = "solo_agent"

    _mock_questionary(
        mocker,
        text=[agent_name, "I'm a nice agent", "0"],  # name, instr, subagents count
        select=["No", "openai/gpt-4o-mini"],
        checkbox=[["openai"], ["web_search", "web_fetch"]],
        confirm=[False],
    )

    result = runner.invoke(app, ["configure"])
    assert result.exit_code == 0
    assert "--- Dynamic Agent Configuration ---" in result.stdout
    assert "AgentConfig initialized successfully!" in result.stdout
    assert (tmp_path / "configs" / f"{agent_name}.yaml").exists()
    prompt_file = tmp_path / "prompts" / f"{agent_name}_instruction.md"
    assert prompt_file.read_text() == "I'm a nice agent"


def test_configure_command_multi_agent_with_subagent(
    tmp_path: Path, monkeypatch, mocker
):
    monkeypatch.chdir(tmp_path)

    _mock_questionary(
        mocker,
        # roots count, root name, root instr, subagents count, sub name, sub instr
        text=["1", "root_agent", "root instr", "1", "sub_agent", "sub instr"],
        select=["Yes", "openai/gpt-4o-mini", "openai/gpt-6-luna"],
        checkbox=[
            ["openai"], ["web_search"],  # root providers, tools
            ["azure"], ["web_fetch"],  # sub providers, tools
        ],
        confirm=[False, True],
    )

    result = runner.invoke(app, ["configure"])
    assert result.exit_code == 0
    assert "AgentConfig initialized successfully!" in result.stdout
    for name in ("root_agent", "sub_agent"):
        assert (tmp_path / "configs" / f"{name}.yaml").exists()
        assert (tmp_path / "prompts" / f"{name}_instruction.md").exists()

    root_yaml = (tmp_path / "configs" / "root_agent.yaml").read_text()
    assert "sub_agent" in root_yaml


def test_configure_command_multiple_root_agents(tmp_path: Path, monkeypatch, mocker):
    monkeypatch.chdir(tmp_path)

    _mock_questionary(
        mocker,
        # roots count, then (name, instr, subagents count) per root
        text=["2", "root_a", "instr a", "0", "root_b", "instr b", "0"],
        select=["Yes", "openai/gpt-4o-mini", "openai/gpt-4o-mini"],
        checkbox=[["openai"], ["web_search"], ["openai"], ["web_crawl"]],
        confirm=[False, False],
    )

    result = runner.invoke(app, ["configure"])
    assert result.exit_code == 0
    for name in ("root_a", "root_b"):
        assert (tmp_path / "configs" / f"{name}.yaml").exists()
        assert (tmp_path / "prompts" / f"{name}_instruction.md").exists()


def test_main_keyboard_interrupt(mocker, capsys):
    mocker.patch("icogito.cli.app", side_effect=KeyboardInterrupt)
    with pytest.raises(typer.Exit) as exc_info:
        main()
    assert exc_info.value.exit_code == 0
    captured = capsys.readouterr()
    assert "Process canceled by user." in captured.out


def test_main_typer_abort(mocker, capsys):
    mocker.patch("icogito.cli.app", side_effect=typer.Abort)
    with pytest.raises(typer.Exit) as exc_info:
        main()
    assert exc_info.value.exit_code == 0
    captured = capsys.readouterr()
    assert "Process canceled by user." in captured.out
