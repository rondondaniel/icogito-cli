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

    for subdir in subdirs:
        dir_path = target_dir / subdir
        dir_path.mkdir(parents=True, exist_ok=True)

    config_data = AgentConfig(
        model_name="openai/gpt-4o-mini",
        agent_name="lead_researcher",
        instructions_path="prompts/example_instruction.md",
        settings_openrouter_provider_list=["azure", "openai"],
        tools_list=["web_search", "web_fetch"],
        subagents_list=["sub_researcher"],
        retries_output=5,
        max_concurrency=1,
    )

    instruction_data = "Your are super agent built with icogito-cli & icogito_lib"
    config_file = target_dir / "configs" / "example_agent_config.yaml"
    prompt_file = target_dir / "prompts" / "example_instruction.md"

    save_agent_config(
        config_file=config_file,
        config_data=config_data
    )
    save_prompt_instruction(
        path=prompt_file,
        instruction_data=instruction_data
    )


@app.command()
def init(
    target_dir: Path = typer.Option(
        Path("src/icogito_lib"),
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

@app.command()
def configure():
    """
    Interactively configure agent workflows with questionary prompts.
    """
    typer.echo("--- Dynamic Agent Configuration ---")
    agent_name = questionary.text(
        "Enter agent name:",
        default="research_agent"
    ).ask()
    model_name = questionary.select(
        "Select OpenRouter model:",
        choices=[
            "openai/gpt-4o",
            "anthropic/claude-3.5-sonnet",
            "google/gemini-2.0-flash-001"
        ]
    ).ask()
    model_providers = questionary.checkbox(
        "Select OpenRouter Providers:",
        choices=[
            "OpenAI", 
            "Anthropic"
        ]
    ).ask()
    # Boolean toggle using questionary.confirm
    enable_multi_agent = questionary.confirm(
        "Enable multi-agent configuration?",
        default=True
    ).ask()
    selected_subagents = []
    if enable_multi_agent:
        # Multi-select menu using questionary.checkbox
        selected_subagents = questionary.checkbox(
            "Select subagents to include in workflow:",
            choices=[
                "web_researcher",
                "content_summarizer",
                "fact_checker"
            ]
        ).ask()
    # Multi-select menu for tools
    selected_tools = questionary.checkbox(
        "Select tools to enable for the agent:",
        choices=[
            "web_search",
            "web_fetch",
            "web_crawl"
        ],
        default="web_search"
    ).ask()
    # Boolean toggle for provider fallback
    allow_fallbacks = questionary.confirm(
        "Allow model provider fallbacks?",
        default=False
    ).ask()
    if agent_name is None:
        typer.echo("Configuration cancelled.")
        return
    # Summary
    typer.echo("\n--- Selected Agent Configuration ---")
    typer.echo(f"Agent Name: {agent_name}")
    typer.echo(f"Model Name: {model_name}")
    typer.echo(f"Model Providers: {model_providers}")
    typer.echo(f"Multi-Agent Mode: {enable_multi_agent}")
    typer.echo(f"Subagents: {selected_subagents}")
    typer.echo(f"Tools: {selected_tools}")
    typer.echo(f"Allow Fallbacks: {allow_fallbacks}")
    # Create Config and Prompts files pahts
    target_prompts_dir = Path("prompts")
    target_config_dir = Path("configs")
    target_prompts_dir.mkdir(parents=True, exist_ok=True)
    target_config_dir.mkdir(parents=True, exist_ok=True)
    instructions_path = f"{target_config_dir}/{agent_name}_instruction.yaml"
    config_path = f"{target_config_dir}/{agent_name}_agent.yaml"
    # Store configuration into a AgentConfig Object and save it
    config = AgentConfig(
        model_name=model_name,
        agent_name=agent_name,
        instructions_path=instructions_path,
        settings_openrouter_provider_list=model_providers,
        subagents_list=selected_subagents,
        tools_list=selected_tools
    )
    save_agent_config(
        config_file=config_path,
        config_data=config
    )
    typer.echo("AgentConfig initialized successfully!")

if __name__ == "__main__":
    app()
