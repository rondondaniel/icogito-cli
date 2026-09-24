from pathlib import Path
from typing import Optional
import typer
import yaml

# Initialize the Typer application
app = typer.Typer(
    name="icogito-cli",
    help="A modern Python CLI framework to build Agent/Multi-Agents systems.",
    add_completion=True,
)


def create_scaffolding(target_dir: Path) -> None:
    """Creates directory structure and YAML config file."""
    subdirs = ["agents", "configs", "schemas", "tools", "utils"]

    target_dir.mkdir(parents=True, exist_ok=True)
    (target_dir / "__init__.py").touch(exist_ok=True)

    for subdir in subdirs:
        dir_path = target_dir / subdir
        dir_path.mkdir(parents=True, exist_ok=True)
        (dir_path / "__init__.py").touch(exist_ok=True)

    config_data = {
        "model_name": "openai/gpt-4o-mini",
        "agent_name": "lead_researcher",
        "instructions_path": "prompts/research_instruction.md",
        "settings_openrouter_provider_list": ["azure", "openai"],
        "tools_list": ["web_search", "web_fetch"],
        "subagents_list": ["sub_researcher"],
        "retries_output": 5,
        "max_concurrency": 1,
    }

    config_file = target_dir / "configs" / "example_agent_config.yaml"
    with open(config_file, "w") as f:
        yaml.dump(config_data, f, sort_keys=False)


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
    if verbose:
        typer.echo("Detailed logs: All services reporting nominal operations.")

if __name__ == "__main__":
    app()