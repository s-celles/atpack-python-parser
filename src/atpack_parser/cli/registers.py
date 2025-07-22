"""Registers command group for AtPack CLI."""

import json
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.panel import Panel
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
from ..display import display_registers

# Create registers sub-command app
registers_app = typer.Typer(name="registers", help="📋 Register information")


@registers_app.command("list")
def list_registers(
    device_name: DeviceName,
    atpack_path: AtPackPath,
    module: Annotated[
        Optional[str], typer.Option("--module", "-m", help="Filter by module")
    ] = None,
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format")
    ] = "table",
    output: Annotated[
        Optional[Path], typer.Option("--output", "-o", help="Export to file")
    ] = None,
    no_color: Annotated[
        bool, typer.Option("--no-color", help="Disable colored output")
    ] = False,
):
    """📋 List registers for a device."""
    try:
        parser = AtPackParser(atpack_path)
        device = parser.get_device(device_name)

        # Collect registers
        registers = []
        for mod in device.modules:
            if module and mod.name.upper() != module.upper():
                continue
            for rg in mod.register_groups:
                for reg in rg.registers:
                    registers.append(
                        {"module": mod.name, "group": rg.name, "register": reg}
                    )

        if format == "json":
            data = []
            for item in registers:
                reg_data = item["register"].model_dump()
                reg_data["module"] = item["module"]
                reg_data["group"] = item["group"]
                data.append(reg_data)

            json_output = json.dumps(data, indent=2)
            if output:
                output.write_text(json_output, encoding="utf-8")
                console.print(
                    f"[green]Exported {len(registers)} registers to {output}[/green]"
                )
            else:
                print(json_output)
        else:
            from rich.console import Console

            # Create console with color control
            output_console = (
                Console(force_terminal=not no_color)
                if not no_color
                else Console(force_terminal=False)
            )

            # Use shared display function
            display_registers(device, device_name, output_console, no_color, module)

            if output:
                # Export would need to be handled separately
                console.print(
                    f"[green]Exported {len(registers)} registers to {output}[/green]"
                )

    except DeviceNotFoundError as e:
        handle_device_not_found_error(e, parser, no_color)
    except AtPackError as e:
        handle_atpack_error(e, no_color)


@registers_app.command("show")
def show_register(
    device_name: DeviceName,
    register_name: Annotated[str, typer.Argument(help="Register name")],
    atpack_path: AtPackPath,
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format")
    ] = "table",
):
    """📋 Show detailed register information."""
    try:
        parser = AtPackParser(atpack_path)
        device = parser.get_device(device_name)

        # Find register
        found_register = None
        for mod in device.modules:
            for rg in mod.register_groups:
                for reg in rg.registers:
                    if reg.name.upper() == register_name.upper():
                        found_register = reg
                        break
                if found_register:
                    break
            if found_register:
                break

        if not found_register:
            console.print(
                f"[red]Register '{register_name}' not found in "
                f"device '{device_name}'[/red]"
            )
            raise typer.Exit(1)

        if format == "json":
            print(found_register.model_dump_json(indent=2))
        else:
            # Register info panel
            info_text = f"""
[bold]Name:[/bold] {found_register.name}
[bold]Caption:[/bold] {found_register.caption or "N/A"}
[bold]Offset:[/bold] 0x{found_register.offset:04X}
[bold]Size:[/bold] {found_register.size} bytes
[bold]Access:[/bold] {found_register.access or "RW"}
[bold]Mask:[/bold] {f"0x{found_register.mask:0{found_register.size * 2}X}" if found_register.mask else "N/A"}
[bold]Initial Value:[/bold] {f"0x{found_register.initial_value:0{found_register.size * 2}X}" if found_register.initial_value else "N/A"}
            """.strip()

            panel = Panel(
                info_text,
                title=f"📋 Register: {found_register.name}",
                border_style="blue",
            )
            console.print(panel)

            # Bitfields table
            if found_register.bitfields:
                table = Table(title="🔧 Bitfields")
                table.add_column("Name", style="cyan")
                table.add_column("Bits", style="green")
                table.add_column("Mask", style="yellow")
                table.add_column("Description", style="white")
                table.add_column("Values", style="dim")

                # Sort bitfields by bit position (ascending order)
                sorted_bitfields = sorted(
                    found_register.bitfields, key=lambda bf: bf.bit_offset
                )

                # Group bitfields by bit position to identify primary fields and aliases
                bit_groups = {}  # Maps bit_position -> [list of bitfields at that position]

                for bf in sorted_bitfields:
                    if bf.bit_width > 1:
                        # Multi-bit field - create entry for each bit it covers
                        for bit_pos in range(
                            bf.bit_offset, bf.bit_offset + bf.bit_width
                        ):
                            if bit_pos not in bit_groups:
                                bit_groups[bit_pos] = []
                            bit_groups[bit_pos].append(bf)
                    else:
                        # Single-bit field
                        if bf.bit_offset not in bit_groups:
                            bit_groups[bf.bit_offset] = []
                        bit_groups[bf.bit_offset].append(bf)

                # Process each bit position in order
                displayed_multibit_fields = (
                    set()
                )  # Track multi-bit fields we've already shown

                for bit_pos in sorted(bit_groups.keys()):
                    fields_at_this_bit = bit_groups[bit_pos]

                    # Separate multi-bit fields from single-bit fields
                    multi_bit_fields = [
                        bf for bf in fields_at_this_bit if bf.bit_width > 1
                    ]
                    single_bit_fields = [
                        bf for bf in fields_at_this_bit if bf.bit_width == 1
                    ]

                    # Show multi-bit fields first (only once per field)
                    for bf in multi_bit_fields:
                        if bf.name not in displayed_multibit_fields:
                            displayed_multibit_fields.add(bf.name)

                            bit_range = (
                                f"{bf.bit_offset + bf.bit_width - 1}:{bf.bit_offset}"
                            )
                            values_str = (
                                f"{len(bf.values)} values" if bf.values else "N/A"
                            )

                            table.add_row(
                                bf.name,
                                bit_range,
                                f"0x{bf.mask:0{found_register.size * 2}X}",
                                bf.caption or "N/A",
                                values_str,
                            )

                    # Show single-bit fields
                    if single_bit_fields:
                        # Check if this bit is part of a multi-bit field
                        parent_multibit = None
                        for bf in multi_bit_fields:
                            if bf.bit_offset <= bit_pos < bf.bit_offset + bf.bit_width:
                                parent_multibit = bf.name
                                break

                        if parent_multibit:
                            # This bit is part of a multi-bit field - show as indented aliases
                            for bf in single_bit_fields:
                                bit_range = f"{bf.bit_offset}"
                                values_str = (
                                    f"{len(bf.values)} values" if bf.values else "N/A"
                                )

                                table.add_row(
                                    f"├─ {bf.name}",
                                    bit_range,
                                    f"0x{bf.mask:0{found_register.size * 2}X}",
                                    bf.caption or "N/A",
                                    values_str,
                                )
                        else:
                            # This bit is NOT part of a multi-bit field - show as primary fields
                            # Find the primary field (first one, or one that's not obviously an alias)
                            primary_field = single_bit_fields[0]
                            for bf in single_bit_fields:
                                # Prefer shorter, simpler names as primary (e.g., "R" over "I2C_READ")
                                if (
                                    len(bf.name) < len(primary_field.name)
                                    and "_" not in bf.name
                                ):
                                    primary_field = bf

                            # Show primary field
                            bit_range = f"{primary_field.bit_offset}"
                            values_str = (
                                f"{len(primary_field.values)} values"
                                if primary_field.values
                                else "N/A"
                            )

                            table.add_row(
                                primary_field.name,
                                bit_range,
                                f"0x{primary_field.mask:0{found_register.size * 2}X}",
                                primary_field.caption or "N/A",
                                values_str,
                            )

                            # Show aliases indented
                            aliases = [
                                bf for bf in single_bit_fields if bf != primary_field
                            ]
                            for alias in aliases:
                                alias_values_str = (
                                    f"{len(alias.values)} values"
                                    if alias.values
                                    else "N/A"
                                )

                                table.add_row(
                                    f"├─ {alias.name}",
                                    bit_range,
                                    f"0x{alias.mask:0{found_register.size * 2}X}",
                                    alias.caption or "N/A",
                                    alias_values_str,
                                )

                console.print(table)

    except DeviceNotFoundError as e:
        handle_device_not_found_error(e, parser)
    except AtPackError as e:
        handle_atpack_error(e)
