from pathlib import Path
from typing import Optional

# Get the project root directory (utils/ -> project_root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

def save_prompt_instruction(path: Optional[str | Path], instruction_data: str) -> None:
    # If the file didn't provide a path (it's None or empty string), return None safely
    if not path:
        return None
        
    file_path = Path(path)
    
    # If a relative path was passed, resolve it against the project root
    if not file_path.is_absolute():
        file_path = PROJECT_ROOT / file_path

    try:
        with open(file_path, 'w') as file:
            file.write(instruction_data)
    except FileNotFoundError as e:
        raise e