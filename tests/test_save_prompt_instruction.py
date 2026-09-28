from pathlib import Path

from icogito_lib.utils.save_prompt_instruction import save_prompt_instruction


def test_save_prompt_instruction_none_or_empty():
    assert save_prompt_instruction(None, "content") is None
    assert save_prompt_instruction("", "content") is None


def test_save_prompt_instruction_absolute_path(tmp_path: Path):
    prompt_file = tmp_path / "prompts" / "agent.md"
    prompt_file.parent.mkdir(parents=True, exist_ok=True)

    result = save_prompt_instruction(prompt_file, "You are a helpful agent.")

    assert result == prompt_file
    assert prompt_file.read_text() == "You are a helpful agent."


def test_save_prompt_instruction_relative_path_resolves_against_cwd(tmp_path: Path, monkeypatch):
    # Regression test: relative paths must resolve against the current working
    # directory (matching the mkdir calls in cli.py), not a hardcoded PROJECT_ROOT.
    monkeypatch.chdir(tmp_path)
    (tmp_path / "prompts").mkdir()

    result = save_prompt_instruction("prompts/agent.md", "You are a helpful agent.")

    assert result == tmp_path / "prompts" / "agent.md"
    assert (tmp_path / "prompts" / "agent.md").read_text() == "You are a helpful agent."


def test_save_prompt_instruction_missing_parent_dir_raises(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    try:
        save_prompt_instruction("nonexistent_dir/agent.md", "content")
        assert False, "expected FileNotFoundError"
    except FileNotFoundError:
        pass
