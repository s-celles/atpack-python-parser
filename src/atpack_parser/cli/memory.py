"""Memory command group for AtPack CLI."""

import json
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.table import Table

from .. import AtPackParser
from ..exceptions import AtPackError, DeviceNotFoundError
from .common import AtPackPath, DeviceName, console

# Create memory sub-command app
memory_app = typer.Typer(name="memory", help="💾 Memory information")


@memory_app.command("show")
def show_memory(
    device_name: DeviceName,
    atpack_path: AtPackPath,
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format")
    ] = "table",
    segment: Annotated[
        Optional[str],
        typer.Option("--segment", "-s", help="Show specific memory segment"),
    ] = None,
    output: Annotated[
        Optional[Path], typer.Option("--output", "-o", help="Export to file")
    ] = None,
    no_color: Annotated[
        bool, typer.Option("--no-color", help="Disable colored output")
    ] = False,
):
    """💾 Show memory layout for a device."""
    try:
        parser = AtPackParser(atpack_path)
        memory_segments = parser.get_device_memory(device_name)

        # Filter by segment if specified
        if segment:
            memory_segments = [
                seg for seg in memory_segments if seg.name.upper() == segment.upper()
            ]
            if not memory_segments:
                console.print(
                    f"[red]Memory segment '{segment}' not found[/red]"
                    if not no_color
                    else f"Memory segment '{segment}' not found"
                )
                raise typer.Exit(1)

        if format == "json":
            data = [seg.model_dump() for seg in memory_segments]
            json_output = json.dumps(data, indent=2)
            if output:
                output.write_text(json_output, encoding="utf-8")
                console.print(
                    f"[green]Exported {len(memory_segments)} memory segments to {output}[/green]"
                )
            else:
                print(json_output)
        else:
            # Create console with color control
            output_console = (
                Console(force_terminal=not no_color)
                if not no_color
                else Console(force_terminal=False)
            )

            title = f"💾 Memory Layout: {device_name}"
            if segment:
                title += f" (Segment: {segment})"

            table = Table(title=title)
            table.add_column("Segment", style="cyan" if not no_color else None)
            table.add_column("Start Address", style="green" if not no_color else None)
            table.add_column("End Address", style="green" if not no_color else None)
            table.add_column("Size", style="yellow" if not no_color else None)
            table.add_column("Type", style="magenta" if not no_color else None)
            table.add_column("Page Size", style="blue" if not no_color else None)
            table.add_column("Address Space", style="dim" if not no_color else None)

            for seg in memory_segments:
                end_addr = seg.start + seg.size - 1
                page_size_str = f"{seg.page_size}" if seg.page_size else "N/A"

                table.add_row(
                    seg.name,
                    f"0x{seg.start:04X}",
                    f"0x{end_addr:04X}",
                    f"{seg.size:,}",
                    seg.type or "N/A",
                    page_size_str,
                    seg.address_space or "N/A",
                )

            if output:
                # Export table as text
                with output_console.capture() as capture:
                    output_console.print(table)

                output.write_text(capture.get(), encoding="utf-8")
                console.print(
                    f"[green]Exported {len(memory_segments)} memory segments to {output}[/green]"
                )
            else:
                output_console.print(table)

    except DeviceNotFoundError as e:
        console.print(
            f"[red]Device not found: {e}[/red]"
            if not no_color
            else f"Device not found: {e}"
        )
        raise typer.Exit(1)
    except AtPackError as e:
        console.print(f"[red]Error: {e}[/red]" if not no_color else f"Error: {e}")
        raise typer.Exit(1)
