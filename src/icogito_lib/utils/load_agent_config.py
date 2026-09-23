import yaml
from pathlib import Path
from schemas.agents import AgentConfig

def load_agent_config(yaml_path: str) -> AgentConfig:
    """Loads a single YAML file and converts it into an AgentConfig model."""
    with open(yaml_path, 'r') as file:
        raw_config = yaml.safe_load(file)
        
    return AgentConfig(**raw_config)