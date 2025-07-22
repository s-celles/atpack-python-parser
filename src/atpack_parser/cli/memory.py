"""Memory command group for AtPack CLI."""

import json
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.table import Table

from .. import AtPackParser
from ..exceptions import AtPackError, DeviceNotFoundError
from .common import (
    AtPackPath,
    DeviceName,
    console,
    handle_atpack_error,
    handle_device_not_found_error,
)

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
                _display_hierarchical_memory(
                    memory_spaces, title, output_console, no_color, output
                )
            else:
                # Display flat table
                _display_flat_memory(
                    memory_segments, title, output_console, no_color, output
                )

    except DeviceNotFoundError as e:
        handle_device_not_found_error(e, parser, no_color)
    except AtPackError as e:
        handle_atpack_error(e, no_color)


def _display_flat_memory(memory_segments, title, output_console, no_color, output):
    """Display memory segments in a flat table format."""
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


def _display_hierarchical_memory(
    memory_spaces, title, output_console, no_color, output
):
    """Display memory spaces in a hierarchical table format."""
    table = Table(title=title)
    table.add_column("Memory Space/Segment", style="cyan" if not no_color else None)
    table.add_column("Start Address", style="green" if not no_color else None)
    table.add_column("End Address", style="green" if not no_color else None)
    table.add_column("Size", style="yellow" if not no_color else None)
    table.add_column("Type", style="magenta" if not no_color else None)
    table.add_column("Page Size", style="blue" if not no_color else None)
    table.add_column("Description", style="dim" if not no_color else None)

    for space in memory_spaces:
        # Add memory space header
        space_name = f"📁 {space.name}"
        space_start = f"0x{space.start:04X}" if space.start is not None else "N/A"
        space_end = (
            f"0x{space.start + space.size - 1:04X}"
            if (space.start is not None and space.size is not None)
            else "N/A"
        )
        space_size = f"{space.size:,}" if space.size is not None else "N/A"

        table.add_row(
            space_name,
            space_start,
            space_end,
            space_size,
            space.space_type,
            "N/A",
            f"Container with {len(space.segments)} segment(s)",
        )

        # Add child segments with indentation
        for seg in space.segments:
            end_addr = seg.start + seg.size - 1
            page_size_str = f"{seg.page_size}" if seg.page_size else "N/A"
            segment_name = f"  └── {seg.name}"  # Indented with tree characters

            table.add_row(
                segment_name,
                f"0x{seg.start:04X}",
                f"0x{end_addr:04X}",
                f"{seg.size:,}",
                seg.type or "N/A",
                page_size_str,
                seg.section or "N/A",
            )

    if output:
        # Export table as text
        with output_console.capture() as capture:
            output_console.print(table)

        output.write_text(capture.get(), encoding="utf-8")
        total_segments = sum(len(space.segments) for space in memory_spaces)
        console.print(
            f"[green]Exported {len(memory_spaces)} memory spaces with {total_segments} segments to {output}[/green]"
        )
    else:
        output_console.print(table)
