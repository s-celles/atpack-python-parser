"""TUI command for AtPack CLI."""

from typing import Annotated

import typer

def launch_tui():
    """🖥️ Launch the Terminal User Interface (TUI)."""
    try:
        from ..tui.main import run_tui
        
        typer.echo("🖥️ Starting AtPack Parser TUI...")
        run_tui()
        
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
