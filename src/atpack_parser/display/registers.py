"""Shared register display utilities for CLI and interactive mode."""

from rich.console import Console
from rich.table import Table

from ..models import Device


def display_registers(
    device: Device,
    device_name: str,
    console: Console,
    no_color: bool = False,
    module_filter: str = None,
) -> None:
    """Display device registers in a table format."""
    title = f"📋 Registers: {device_name}"
    if module_filter:
        title += f" (Module: {module_filter})"

    table = Table(title=title)
    table.add_column("Module", style="cyan" if not no_color else None)
    table.add_column("Register", style="green" if not no_color else None)
    table.add_column("Offset", style="yellow" if not no_color else None)
    table.add_column("Size", style="blue" if not no_color else None)
    table.add_column("Access", style="magenta" if not no_color else None)
    table.add_column("Bitfields", style="dim" if not no_color else None)

    # Collect registers from device modules
    registers = []
    for mod in device.modules:
        if module_filter and mod.name.upper() != module_filter.upper():
            continue
        for rg in mod.register_groups:
            for reg in rg.registers:
                registers.append(
                    {"module": mod.name, "group": rg.name, "register": reg}
                )

    if registers:
        # Sort by offset like CLI does
        sorted_registers = sorted(registers, key=lambda x: x["register"].offset)
        for item in sorted_registers:
            reg = item["register"]
            table.add_row(
                item["module"],
                reg.name,
                f"0x{reg.offset:04X}",
                str(reg.size),
                reg.access or "RW",
                str(len(reg.bitfields)),
            )

        console.print(table)
    else:
        filter_msg = f" with module filter '{module_filter}'" if module_filter else ""
        console.print(
            f"[yellow]No registers found for device {device_name}{filter_msg}[/yellow]"
        )
