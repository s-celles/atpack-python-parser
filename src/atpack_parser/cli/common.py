"""Common types and utilities for CLI commands."""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from ..exceptions import AtPackError, DeviceNotFoundError

# Create console for rich output
console = Console()

# Common types
AtPackPath = Annotated[Path, typer.Argument(help="Path to AtPack file or directory")]
DeviceName = Annotated[
    str, typer.Argument(help="Device name (e.g., ATmega16, PIC16F876A)")
]
OutputFormat = Annotated[str, typer.Option("--format", "-f", help="Output format")]


def handle_device_not_found_error(e: DeviceNotFoundError, no_color: bool = False) -> None:
    """Handle DeviceNotFoundError consistently across all CLI commands."""
    error_msg = (
        f"[red]Device not found: {e}[/red]"
        if not no_color
        else f"Device not found: {e}"
    )
    console.print(error_msg)
    raise typer.Exit(1)


def handle_atpack_error(e: AtPackError, no_color: bool = False) -> None:
    """Handle AtPackError consistently across all CLI commands."""
    error_msg = (
        f"[red]Error: {e}[/red]"
        if not no_color
        else f"Error: {e}"
    )
    console.print(error_msg)
    raise typer.Exit(1)
