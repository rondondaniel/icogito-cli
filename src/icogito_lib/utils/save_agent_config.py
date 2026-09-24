import yaml
from typing import Optional
from pathlib import Path
from icogito_lib.schemas.agents import AgentConfig

# Get the project root directory (utils/ -> project_root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

def save_agent_config(config_file: Optional[str | Path], config_data: AgentConfig) -> Optional[str | Path] | None:
    """Saves a single YAML file and converts it into an AgentConfig model."""
    if not config_file:
        return None
    file_path = Path(config_file)   
    # If a relative path was passed, resolve it against the project root
    if not file_path.is_absolute():
        file_path = PROJECT_ROOT / file_path
    try:
        with open(file_path, "w") as f:
            yaml.dump(config_data.model_dump(), f, sort_keys=False)
            return file_path
    except FileNotFoundError as e:
        raise e