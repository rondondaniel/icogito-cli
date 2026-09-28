import yaml
from typing import Optional
from pathlib import Path
from icogito_lib.schemas.agents import AgentConfig

def save_agent_config(config_file: Optional[str | Path], config_data: AgentConfig) -> Optional[str | Path] | None:
    """Saves a single YAML file and converts it into an AgentConfig model."""
    # If the file didn't provide a path (it's None or empty string), return None safely
    if not config_file:
        return None
    file_path = Path(config_file)
    # If a relative path was passed, resolve it against the current working directory
    if not file_path.is_absolute():
        file_path = Path.cwd() / file_path
    try:
        with open(file_path, "w") as file:
            yaml.dump(config_data.model_dump(), file, sort_keys=False)
        return file_path
    except FileNotFoundError as e:
        raise e