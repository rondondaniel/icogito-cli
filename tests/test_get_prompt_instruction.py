import pytest
from pathlib import Path
from icogito_lib.utils.get_prompt_instruction import get_prompt_instruction, PROJECT_ROOT


def test_get_prompt_instruction_none_or_empty():
    assert get_prompt_instruction(None) is None
    assert get_prompt_instruction("") is None


def test_get_prompt_instruction_absolute_path(tmp_path: Path):
    test_file = tmp_path / "prompt.txt"
    content = "You are a helpful AI assistant."
    test_file.write_text(content, encoding="utf-8")

    result = get_prompt_instruction(test_file)
    assert result == content

    result_str = get_prompt_instruction(str(test_file))
    assert result_str == content


def test_get_prompt_instruction_relative_path(tmp_path: Path, monkeypatch):
    # Test relative path resolving against PROJECT_ROOT
    rel_file = PROJECT_ROOT / "test_prompt_rel.txt"
    content = "Relative prompt content"
    try:
        rel_file.write_text(content, encoding="utf-8")
        result = get_prompt_instruction("test_prompt_rel.txt")
        assert result == content
    finally:
        if rel_file.exists():
            rel_file.unlink()
