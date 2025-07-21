"""TUI command for AtPack CLI."""

from typing import Annotated, Optional
from pathlib import Path

import typer

def launch_tui(
    directory: Annotated[
        Optional[Path], 
        typer.Argument(
            help="Directory to browse for AtPack files (default: ./atpacks/)"
        )
    ] = None
):
    """🖥️ Launch the Terminal User Interface (TUI)."""
    try:
        from ..tui.main import run_tui
        
        start_dir = str(directory) if directory else None
        
        if directory and not directory.exists():
            typer.echo(f"❌ Directory '{directory}' does not exist.")
            raise typer.Exit(1)
        
        dir_msg = f" from '{directory}'" if directory else " from './atpacks/'"
        typer.echo(f"🖥️ Starting AtPack Parser TUI{dir_msg}...")
        run_tui(start_dir)
        
    except ImportError as e:
        if "textual" in str(e).lower():
            typer.echo("❌ TUI requires textual package. Install with: pip install textual")
            typer.echo("💡 Or install with TUI support: pip install atpack-parser[tui]")
        else:
            typer.echo(f"❌ Error launching TUI: {e}")
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"❌ Error launching TUI: {e}")
        raise typer.Exit(1)
