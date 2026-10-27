from pathlib import Path
from typing import Any, Optional
import typer
import questionary

from icogito import core
from icogito.models import AgentConfig

APP_NAME = "icogito"


def safe_ask(question: Any) -> Any:
    """Evaluates questionary prompts and translates None returns into typer.Abort() exceptions."""
    answer = question.ask()
    if answer is None:
        raise typer.Abort()
    return answer


def get_global_app_dir() -> Path:
    """Returns the global OS-appropriate application directory for icogito."""
    app_dir = Path(typer.get_app_dir(APP_NAME))
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


app = typer.Typer(
    name="icogito-cli",
    help="A modern Python CLI framework to build Agent/Multi-Agents systems.",
    add_completion=True,
)


@app.command()
def init(
    target_dir: Path = typer.Argument(
        default=Path.cwd(),
        help="Target directory for the new project",
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Force re-initialization"),
):
    """
    Initialize directory scaffolding for a new agent project.
    """
    typer.secho(f"Initializing agent scaffolding at {target_dir}...", fg=typer.colors.GREEN)
    core.create_scaffolding(target_dir)
    typer.secho(
        f"Successfully generated directory structure at {target_dir}.",
        fg=typer.colors.GREEN,
    )


@app.command()
def doctor(
    verbose: Optional[bool] = typer.Option(False, "--verbose", "-v", help="Show extra details")
):
    """
    Check the system status.
    """
    global_app_dir = get_global_app_dir()
    status = core.get_doctor_status(verbose=bool(verbose))
    typer.echo(f"System status: {status['status']}")
    typer.echo(f"Global App Directory: {global_app_dir}")
    typer.echo(f"Available Tavily tools: {', '.join(status['tools_available'])}")
    typer.echo(f"AgentFactory ready: {status['agent_factory_ready']}")

    if verbose and "details" in status:
        typer.echo(f"Detailed logs: {status['details']}")


def prompt_agent_config(agent: str, is_sub_agent: bool = False) -> AgentConfig:
    """Interactively prompts user for agent configuration via questionary."""
    agent_name = safe_ask(
        questionary.text(
            f"Enter agent name for {agent}:",
            default="research_agent"
        )
    )
    model_name = safe_ask(
        questionary.select(
            "Select OpenRouter model:",
            choices=[
                "openai/gpt-4o-mini",
                "openai/gpt-6-luna",
                "openai/gpt-6-luna-pro"
            ]
        )
    )
    model_providers = safe_ask(
        questionary.checkbox(
            "Select OpenRouter Providers:",
            choices=[
                "openai",
                "openai/flex",
                "azure"
            ]
        )
    )
    allow_fallbacks = safe_ask(
        questionary.confirm(
            "Allow model provider fallbacks?",
            default=False
        )
    )
    agent_instruction = safe_ask(
        questionary.text(
            "Enter agent's instructions:",
            default="You are an AI agent built with icogito"
        )
    )
    selected_tools = safe_ask(
        questionary.checkbox(
            "Select tools to enable for the agent:",
            choices=[
                "web_search",
                "web_fetch",
                "web_crawl"
            ],
            default="web_search"
        )
    )

    if is_sub_agent:
        number_of_sub_agents = 0
    else:
        number_of_sub_agents = int(
            safe_ask(
                questionary.text(
                    "Number of sub agents: ",
                    validate=lambda text: text.isdigit() or "Please enter a valid number"
                )
            )
        )

    sub_agents_names = []
    if number_of_sub_agents > 0:
        for i in range(int(number_of_sub_agents)):
            subagent_config = prompt_agent_config(f"{agent_name}'s sub-agent-{i}", is_sub_agent=True)
            sub_agents_names.append(subagent_config.agent_name)
            core.save_config(subagent_config)

    config = core.create_agent_config(
        agent_name=agent_name,
        model_name=model_name,
        model_providers=model_providers,
        allow_fallbacks=allow_fallbacks,
        instruction_text=agent_instruction,
        selected_tools=selected_tools,
        sub_agents_names=sub_agents_names,
    )
    return config


@app.command()
def configure():
    """
    Interactively configure agent workflows with questionary prompts.
    """
    typer.echo("--- Dynamic Agent Configuration ---")
    enable_multi_agent = safe_ask(
        questionary.select(
            "Enable multi-agent configuration?",
            choices=[
                "Yes",
                "No"
            ],
        )
    )

    if enable_multi_agent == "No":
        config = prompt_agent_config("root-agent")
        core.save_config(config)
    else:
        number_of_agents = int(
            safe_ask(
                questionary.text(
                    "Number of root agents: ",
                    validate=lambda text: text.isdigit() or "Please enter a valid number"
                )
            )
        )
        for i in range(int(number_of_agents)):
            config = prompt_agent_config(f"root-agent-{i}")
            core.save_config(config)

    typer.echo("AgentConfig initialized successfully!")


def main():
    try:
        app(standalone_mode=False)
    except (KeyboardInterrupt, typer.Abort):
        typer.echo("Process canceled by user.")
        raise typer.Exit(code=0)


if __name__ == "__main__":
    main()
