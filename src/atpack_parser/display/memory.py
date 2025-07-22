"""Shared memory display utilities for CLI and interactive mode."""

from typing import List

from rich.console import Console
from rich.table import Table

from ..models import MemorySegment, MemorySpace


def display_hierarchical_memory(
    memory_spaces: List[MemorySpace],
    device_name: str,
    console: Console,
    no_color: bool = False,
) -> None:
    """Display memory spaces in a hierarchical table format."""
    title = f"💾 Memory Layout: {device_name} (Hierarchical)"

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

    console.print(table)


def display_flat_memory(
    memory_segments: List[MemorySegment],
    device_name: str,
    console: Console,
    no_color: bool = False,
) -> None:
    """Display memory segments in a flat table format."""
    title = f"💾 Memory Layout: {device_name} (Flat)"

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

    console.print(table)
