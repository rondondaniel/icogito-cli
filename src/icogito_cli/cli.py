import typer
from typing import Optional

# Initialize the Typer application
app = typer.Typer(
    name="my-packaged-cli",
    help="A modern Python CLI framework to build Agent/Multi-Agents systems.",
    add_completion=True,
)

@app.command()
def init(
    env: str = typer.Option("development", "--env", "-e", help="Target environment"),
    force: bool = typer.Option(False, "--force", "-f", help="Force re-initialization"),
):
    """
    Initialize the workspace configuration.
    """
    typer.echo(f"Initializing project in [{env}] environment...")
    if force:
        typer.echo("Force flag set: Overwriting existing configuration.")

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