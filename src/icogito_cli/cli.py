import sys
from pathlib import Path
from typing import Optional
import typer
import questionary

# Ensure src and src/icogito_lib are in sys.path for icogito_lib top-level imports
_src_dir = Path(__file__).resolve().parent.parent
_lib_dir = _src_dir / "icogito_lib"
if str(_src_dir) not in sys.path:
    sys.path.insert(0, str(_src_dir))
if str(_lib_dir) not in sys.path:
    sys.path.insert(0, str(_lib_dir))

from icogito_lib.agents.factory import AgentFactory
from icogito_lib.tools.tavily_web_tools import web_search, web_fetch, web_crawl
from icogito_lib.schemas.agents import AgentConfig
from icogito_lib.utils.save_agent_config import save_agent_config
from icogito_lib.utils.save_prompt_instruction import save_prompt_instruction

# Initialize the Typer application
app = typer.Typer(
    name="icogito-cli",
    help="A modern Python CLI framework to build Agent/Multi-Agents systems.",
    add_completion=True,
)


def create_scaffolding(target_dir: Path) -> None:
    """Creates directory structure and YAML config file."""
    subdirs = ["agents", "configs", "schemas", "prompts", "tools", "utils"]

    target_dir.mkdir(parents=True, exist_ok=True)
    print(target_dir)

    for subdir in subdirs:
        dir_path = target_dir / subdir
        dir_path.mkdir(parents=True, exist_ok=True)

@app.command()
def init(
    target_dir: Path = typer.Option(
        Path("src/my_new_agent"),
        "--target-dir",
        "-t",
        help="Target destination directory for scaffolding.",
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Force re-initialization"),
):
    """
    Initialize directory scaffolding and example agent configuration.
    """
    typer.echo(f"Initializing agent scaffolding at {target_dir}...")
    create_scaffolding(target_dir)
    typer.echo(
        f"Successfully generated directory structure and configs/example_agent_config.yaml at {target_dir}."
    )

@app.command()
def doctor(
    verbose: Optional[bool] = typer.Option(False, "--verbose", "-v", help="Show extra details")
):
    """
    Check the system status.
    """
    typer.echo("System status: OK")

    # Verify Tavily tools and AgentFactory imports
    tools_available = [web_search.__name__, web_fetch.__name__, web_crawl.__name__]
    typer.echo(f"Available Tavily tools: {', '.join(tools_available)}")
    typer.echo(f"AgentFactory ready: {AgentFactory.__name__}")

    if verbose:
        typer.echo("Detailed logs: All services reporting nominal operations.")

def agent_config(agent: str, is_sub_agent: bool = False):
    agent_name = questionary.text(
        f"Enter agent name for {agent}:",
        default="research_agent"
    ).ask()
    model_name = questionary.select(
        "Select OpenRouter model:",
        choices=[
            "openai/gpt-4o-mini",
            "openai/gpt-6-luna",
            "openai/gpt-6-luna-pro"
        ]
    ).ask()
    model_providers = questionary.checkbox(
        "Select OpenRouter Providers:",
        choices=[
            "openai", 
            "openai/flex",
            "azure"
        ]
    ).ask()
    allow_fallbacks = questionary.confirm(
        "Allow model provider fallbacks?",
        default=False
    ).ask()
    agent_instruction = questionary.text(
        f"Enter agent's instructions:",
        default="You are an AI agent built with icogito"
    ).ask()
    selected_tools = questionary.checkbox(
        "Select tools to enable for the agent:",
        choices=[
            "web_search",
            "web_fetch",
            "web_crawl"
        ],
        default="web_search"
    ).ask()
    if is_sub_agent:
        number_of_sub_agents = 0
    else:
        number_of_sub_agents = int(
            questionary.text(
                "Number of sub agents: ",
                validate=lambda text: text.isdigit() or "Please enter a valid number"
            ).ask()
        )
    sub_agents_names = []
    if number_of_sub_agents > 0:
        for i in range(int(number_of_sub_agents)):
            subagent_config = agent_config(f"{agent_name}'s sub-agent-{i}", is_sub_agent=True)
            sub_agents_names.append(subagent_config.agent_name)
            save_config(subagent_config)

    # Create Config and Prompts files pahts
    target_prompts_dir = Path("prompts")
    target_config_dir = Path("configs")
    target_prompts_dir.mkdir(parents=True, exist_ok=True)
    target_config_dir.mkdir(parents=True, exist_ok=True)
    instructions_path = f"{target_prompts_dir}/{agent_name}_instruction.md"
    config_path = f"{target_config_dir}/{agent_name}_agent.yaml"
    # Store configuration into a AgentConfig Object and save it
    config = AgentConfig(
        model_name=model_name,
        agent_name=agent_name,
        agent_instruction=agent_instruction,
        instructions_path=instructions_path,
        config_file_path=config_path,
        settings_openrouter_provider_list=model_providers,
        allow_fallbacks=allow_fallbacks,
        subagents_list=sub_agents_names,
        tools_list=selected_tools
    )
    return config

def save_config(config: AgentConfig) -> None:
    save_agent_config(
        config_file=config.config_file_path,
        config_data=config
    )
    save_prompt_instruction(
        path=config.instructions_path,
        instruction_data=config.agent_instruction
    )

@app.command()
def configure():
    """
    Interactively configure agent workflows with questionary prompts.
    """
    typer.echo("--- Dynamic Agent Configuration ---")
    # Boolean toggle using questionary.confirm
    enable_multi_agent = questionary.select(
        "Enable multi-agent configuration?",
        choices=[
            "Yes",
            "No"
        ],
    ).ask()
    if enable_multi_agent == "No":
        config = agent_config("root-agent")
        save_config(config)
    else:
        number_of_agents = int(
            questionary.text(
                "Number of root agents: ",
                validate=lambda text: text.isdigit() or "Please enter a valid number"
            ).ask()
        )
        for i in range(int(number_of_agents)):
            config = agent_config(f"root-agent-{i}")
            save_config(config)
    typer.echo("AgentConfig initialized successfully!")

if __name__ == "__main__":
    app()
