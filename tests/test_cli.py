import pytest
import os
from pathlib import Path
from typer.testing import CliRunner

# Ensure TAVILY_API_KEY is set in environment so imports in cli.py don't fail
os.environ["TAVILY_API_KEY"] = "dummy-test-key"

from icogito_cli.cli import app
from icogito_lib.utils.save_agent_config import PROJECT_ROOT

runner = CliRunner()


def test_doctor_command():
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "System status: OK" in result.stdout
    assert "Available Tavily tools: web_search, web_fetch, web_crawl" in result.stdout
    assert "AgentFactory ready: AgentFactory" in result.stdout


def test_doctor_command_verbose():
    result = runner.invoke(app, ["doctor", "--verbose"])
    assert result.exit_code == 0
    assert "System status: OK" in result.stdout
    assert "Detailed logs: All services reporting nominal operations." in result.stdout


def test_init_command(tmp_path: Path):
    target_dir = tmp_path / "scaffold_test"
    result = runner.invoke(app, ["init", "--target-dir", str(target_dir)])
    assert result.exit_code == 0
    assert f"Initializing agent scaffolding at {target_dir}..." in result.stdout
    assert (target_dir / "configs" / "example_agent_config.yaml").exists()
    assert (target_dir / "prompts" / "example_instruction.md").exists()


def test_configure_command_success(mocker):
    agent_name = "my_custom_agent_test_unique"
    expected_config_file = PROJECT_ROOT / "configs" / f"{agent_name}_agent.yaml"
    expected_prompt_dir = PROJECT_ROOT / "prompts"
    expected_config_dir = PROJECT_ROOT / "configs"

    # Mock questionary prompt ask calls
    mock_text = mocker.patch("questionary.text")
    mock_select = mocker.patch("questionary.select")
    mock_checkbox = mocker.patch("questionary.checkbox")
    mock_confirm = mocker.patch("questionary.confirm")

    mock_text.return_value.ask.return_value = agent_name
    mock_select.return_value.ask.return_value = "openai/gpt-4o"
    mock_checkbox.return_value.ask.side_effect = [
        ["OpenAI"],  # OpenRouter Providers
        ["web_researcher"],  # Subagents
        ["web_search", "web_fetch"],  # Tools
    ]
    mock_confirm.return_value.ask.side_effect = [
        True,  # enable multi agent
        False,  # allow fallbacks
    ]

    try:
        result = runner.invoke(app, ["configure"])
        assert result.exit_code == 0
        assert "--- Dynamic Agent Configuration ---" in result.stdout
        assert f"Agent Name: {agent_name}" in result.stdout
        assert "AgentConfig initialized successfully!" in result.stdout
        assert expected_config_file.exists()
    finally:
        if expected_config_file.exists():
            expected_config_file.unlink()


def test_configure_command_cancelled(mocker):
    mock_text = mocker.patch("questionary.text")
    mock_select = mocker.patch("questionary.select")
    mock_checkbox = mocker.patch("questionary.checkbox")
    mock_confirm = mocker.patch("questionary.confirm")

    # If user cancels (agent_name is None)
    mock_text.return_value.ask.return_value = None
    mock_select.return_value.ask.return_value = "openai/gpt-4o"
    mock_checkbox.return_value.ask.return_value = []
    mock_confirm.return_value.ask.return_value = False

    result = runner.invoke(app, ["configure"])
    assert result.exit_code == 0
    assert "Configuration cancelled." in result.stdout
