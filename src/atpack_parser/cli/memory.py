"""Memory command group for AtPack CLI."""

import json
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console

from .. import AtPackParser
from ..exceptions import AtPackError, DeviceNotFoundError
from .common import (
    AtPackPath,
    DeviceName,
    console,
    handle_atpack_error,
    handle_device_not_found_error,
)
from ..display import display_flat_memory, display_hierarchical_memory

# Create memory sub-command app
memory_app = typer.Typer(name="memory", help="💾 Memory information")


@memory_app.command("show")
def show_memory(
    device_name: DeviceName,
    atpack_path: AtPackPath,
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format")
    ] = "table",
    flat: Annotated[
        bool,
        typer.Option(
            "--flat", help="Show flat memory layout (default is hierarchical)"
        ),
    ] = False,
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

        # Default is hierarchical, flat is the option
        hierarchical = not flat

        if hierarchical:
            memory_spaces = parser.get_device_memory_hierarchical(device_name)

            # Flatten for filtering if segment is specified
            if segment:
                all_segments = []
                for space in memory_spaces:
                    all_segments.extend(space.segments)
                memory_segments = [
                    seg for seg in all_segments if seg.name.upper() == segment.upper()
                ]
                if not memory_segments:
                    console.print(
                        f"[red]Memory segment '{segment}' not found[/red]"
                        if not no_color
                        else f"Memory segment '{segment}' not found"
                    )
                    raise typer.Exit(1)
            else:
                memory_segments = None  # Will display hierarchically
        else:
            memory_segments = parser.get_device_memory(device_name)

            # Filter by segment if specified
            if segment:
                memory_segments = [
                    seg
                    for seg in memory_segments
                    if seg.name.upper() == segment.upper()
                ]
                if not memory_segments:
                    console.print(
                        f"[red]Memory segment '{segment}' not found[/red]"
                        if not no_color
                        else f"Memory segment '{segment}' not found"
                    )
                    raise typer.Exit(1)

        if format == "json":
            if hierarchical and memory_segments is None:
                # Export hierarchical structure
                data = [space.model_dump() for space in memory_spaces]
            else:
                # Export flat segments
                data = [seg.model_dump() for seg in memory_segments]

            json_output = json.dumps(data, indent=2)
            if output:
                output.write_text(json_output, encoding="utf-8")
                count_items = len(
                    memory_spaces
                    if hierarchical and memory_segments is None
                    else memory_segments
                )
                item_type = (
                    "memory spaces"
                    if hierarchical and memory_segments is None
                    else "memory segments"
                )
                console.print(
                    f"[green]Exported {count_items} {item_type} to {output}[/green]"
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
            if hierarchical:
                title += " (Hierarchical)"
            else:
                title += " (Flat)"

            if hierarchical and memory_segments is None:
                # Display hierarchical table
                display_hierarchical_memory(
                    memory_spaces, device_name, output_console, no_color
                )
                if output:
                    # Export table as text - will be handled separately
                    total_segments = sum(len(space.segments) for space in memory_spaces)
                    console.print(
                        f"[green]Exported {len(memory_spaces)} memory spaces "
                        f"with {total_segments} segments to {output}[/green]"
                    )
            else:
                # Display flat table
                display_flat_memory(
                    memory_segments, device_name, output_console, no_color
                )
                if output:
                    # Export table as text - will be handled separately
                    console.print(
                        f"[green]Exported {len(memory_segments)} memory "
                        f"segments to {output}[/green]"
                    )

    except DeviceNotFoundError as e:
        handle_device_not_found_error(e, parser, no_color)
    except AtPackError as e:
        handle_atpack_error(e, no_color)
