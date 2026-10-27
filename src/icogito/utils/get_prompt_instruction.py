from pathlib import Path

from icogito.models import PathLike


def get_prompt_instruction(path: PathLike | None) -> str | None:
    """Reads an instruction/description markdown file. Relative paths resolve against the current working directory."""
    # If the YAML didn't provide a path (it's None or empty string), return None safely
    if not path:
        return None

    # Path.cwd() / absolute_path yields the absolute path unchanged
    return (Path.cwd() / path).read_text(encoding="utf-8")