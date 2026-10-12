from pathlib import Path
from typing import Optional

def save_prompt_instruction(path: Optional[str | Path], instruction_data: str) -> Optional[str | Path] | None:
    """Saves agent's instruction into a markdown file."""
    # If the file didn't provide a path (it's None or empty string), return None safely
    if not path:
        return None
    file_path = Path(path)
    # If a relative path was passed, resolve it against the current working directory
    if not file_path.is_absolute():
        file_path = Path.cwd() / file_path
    try:
        with open(file_path, 'w') as file:
            file.write(instruction_data)
        return file_path
    except FileNotFoundError as e:
        raise e