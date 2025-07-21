"""Command Line Interface for AtPack Parser using Typer."""

from typing import Annotated

import typer
from rich.console import Console

from .files import files_app
from .devices import devices_app
from .memory import memory_app
from .registers import registers_app
from .config import config_app
from .global_commands import scan, help_tree_command, interactive_help
from .tui_command import launch_tui

# Create console for rich output
console = Console()

# Create Typer app with hierarchical commands
app = typer.Typer(
    name="atpack",
    help="🔧 AtPack Parser - Parse AtPack files",
    rich_markup_mode="rich",
)

# Add sub-command groups
app.add_typer(files_app)
app.add_typer(devices_app)
app.add_typer(memory_app)
app.add_typer(registers_app)
app.add_typer(config_app)

# Add global commands
app.command("scan")(scan)
app.command("help-tree")(help_tree_command)
app.command("help")(interactive_help)
app.command("tui")(launch_tui)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Annotated[
        bool, typer.Option("--version", "-v", help="Show version")
    ] = False,
):
    """
    🔧 AtPack Parser CLI - Parse AtPack files

    Available command groups:
    • files    - Manage AtPack files (list, info, extract)
    • devices  - Device information (list, info, search, packages, pinout)
    • memory   - Memory layouts (show)
    • registers - Register details (list, show)
    • config   - Configuration data (show)
    • scan     - Directory scanning
    • help-tree - Show command structure

    Use 'atpack COMMAND --help' for detailed help on each command.
    Use 'atpack help-tree' to see the complete command structure.
    """
    if version:
        from .. import __version__

        atpack = typer.style("AtPack", bg=typer.colors.BLUE)
        parser = typer.style("Parser", bg=typer.colors.WHITE, fg=typer.colors.BLACK)
        version = typer.style("v" + __version__, bg=typer.colors.RED)
        typer.echo(f"{atpack} {parser} {version}")
        raise typer.Exit()

    # If no command is provided, show help
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())
        raise typer.Exit()


if __name__ == "__main__":
    app()
