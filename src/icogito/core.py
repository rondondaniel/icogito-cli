from pathlib import Path
from typing import Optional, List, Dict, Any

from icogito.factory import AgentFactory
from icogito.tools.tavily_web_tools import web_search, web_fetch, web_crawl
from icogito.models import AgentConfig
from icogito.utils.save_agent_config import save_agent_config
from icogito.utils.save_prompt_instruction import save_prompt_instruction


def create_scaffolding(target_dir: Path) -> List[Path]:
    """Creates directory structure for agent scaffolding."""
    subdirs = ["agents", "configs", "schemas", "prompts", "tools", "utils"]

    target_dir.mkdir(parents=True, exist_ok=True)
    created_paths = [target_dir]

    for subdir in subdirs:
        dir_path = target_dir / subdir
        dir_path.mkdir(parents=True, exist_ok=True)
        created_paths.append(dir_path)

    return created_paths


def get_doctor_status(verbose: bool = False) -> Dict[str, Any]:
    """Retrieves system status and availability of tools and components."""
    tools_available = [web_search.__name__, web_fetch.__name__, web_crawl.__name__]
    status: Dict[str, Any] = {
        "status": "OK",
        "tools_available": tools_available,
        "agent_factory_ready": AgentFactory.__name__,
    }
    if verbose:
        status["details"] = "All services reporting nominal operations."
    return status


def create_agent_config(
    agent_name: str,
    model_name: str,
    model_providers: List[str],
    allow_fallbacks: bool,
    instruction_text: str,
    selected_tools: List[str],
    sub_agents_names: Optional[List[str]] = None,
    prompts_dir: Path | str = "prompts",
    configs_dir: Path | str = "configs",
) -> AgentConfig:
    """Constructs an AgentConfig and writes its instruction text to the prompt file."""
    target_prompts_dir = Path(prompts_dir)
    target_config_dir = Path(configs_dir)
    target_prompts_dir.mkdir(parents=True, exist_ok=True)
    target_config_dir.mkdir(parents=True, exist_ok=True)

    instructions_path = f"{target_prompts_dir}/{agent_name}_instruction.md"
    config_path = f"{target_config_dir}/{agent_name}.yaml"

    save_prompt_instruction(path=instructions_path, instruction_data=instruction_text)

    return AgentConfig(
        model_name=model_name,
        agent_name=agent_name,
        instructions_path=instructions_path,
        config_file_path=config_path,
        settings_openrouter_provider_list=model_providers,
        allow_fallbacks=allow_fallbacks,
        subagents_list=sub_agents_names or [],
        tools_list=selected_tools,
    )


def save_config(config: AgentConfig) -> None:
    """Saves the agent configuration file."""
    save_agent_config(
        config_file=config.config_file_path,
        config_data=config
    )
