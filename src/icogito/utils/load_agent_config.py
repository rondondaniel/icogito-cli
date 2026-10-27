import yaml
from pathlib import Path
from icogito.models import AgentConfig

def load_agent_config(yaml_path: str) -> AgentConfig:
    """Loads a single YAML file and converts it into an AgentConfig model."""
    file_path = Path.cwd() / yaml_path
    with open(file_path, 'r') as file:
        raw_config = yaml.safe_load(file)
        
    return AgentConfig(**raw_config)