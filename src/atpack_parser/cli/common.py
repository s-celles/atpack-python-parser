"""Common types and utilities for CLI commands."""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

# Create console for rich output
console = Console()

# Common types
AtPackPath = Annotated[Path, typer.Argument(help="Path to AtPack file or directory")]
DeviceName = Annotated[
    str, typer.Argument(help="Device name (e.g., ATmega16, PIC16F876A)")
]
OutputFormat = Annotated[str, typer.Option("--format", "-f", help="Output format")]
