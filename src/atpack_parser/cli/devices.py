"""Devices command group for AtPack CLI."""

import fnmatch
import json
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .. import AtPackParser
from ..exceptions import AtPackError, DeviceNotFoundError
from ..models import DeviceFamily
from .common import AtPackPath, DeviceName, console

# Create devices sub-command app
devices_app = typer.Typer(name="devices", help="🔌 Device information")


@devices_app.command("list")
def list_devices(
    atpack_path: AtPackPath,
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
    """📋 List all devices in an AtPack."""
    try:
        parser = AtPackParser(atpack_path)
        devices = parser.get_devices()
        device_family = parser.device_family

        data = {
            "device_family": device_family.value,
            "device_count": len(devices),
            "devices": devices,
        }

        if format == "json":
            json_output = json.dumps(data, indent=2)
            if output:
                output.write_text(json_output, encoding="utf-8")
                console.print(
                    f"[green]Exported {len(devices)} devices to {output}[/green]"
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

            # Family emoji
            family_emoji = {
                DeviceFamily.ATMEL: "🔵" if not no_color else "[ATMEL]",
                DeviceFamily.PIC: "🟡" if not no_color else "[PIC]",
                DeviceFamily.UNSUPPORTED: "⚫" if not no_color else "[UNSUPPORTED]",
            }

            table = Table(
                title=f"{family_emoji[device_family]} {device_family.value} "
                f"Devices in {atpack_path.name}"
            )
            table.add_column("Device Name", style="cyan" if not no_color else None)
            table.add_column("Index", style="dim" if not no_color else None)

            for i, device in enumerate(devices, 1):
                table.add_row(device, str(i))

            if output:
                # Export table as text
                with output_console.capture() as capture:
                    output_console.print(table)
                    output_console.print(f"\nTotal: {len(devices)} devices")

                output.write_text(capture.get(), encoding="utf-8")
                console.print(
                    f"[green]Exported {len(devices)} devices to {output}[/green]"
                )
            else:
                output_console.print(table)
                output_console.print(
                    f"\n[green]Total: {len(devices)} devices[/green]"
                    if not no_color
                    else f"\nTotal: {len(devices)} devices"
                )

    except AtPackError as e:
        console.print(f"[red]Error: {e}[/red]" if not no_color else f"Error: {e}")
        raise typer.Exit(1)


@devices_app.command("info")
def device_info(
    device_name: DeviceName,
    atpack_path: AtPackPath,
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format")
    ] = "table",
):
    """ℹ️ Show detailed information for a specific device."""
    try:
        parser = AtPackParser(atpack_path)
        device = parser.get_device(device_name)

        if format == "json":
            print(device.model_dump_json(indent=2))
        else:
            # Family emoji
            family_emoji = {
                DeviceFamily.ATMEL: "🔵",
                DeviceFamily.PIC: "🟡",
                DeviceFamily.UNSUPPORTED: "⚫",
            }

            # Basic info panel
            info_text = f"""
[bold]Family:[/bold] {family_emoji[device.family]} {device.family.value}
[bold]Architecture:[/bold] {device.architecture or "N/A"}
[bold]Series:[/bold] {device.series or "N/A"}
[bold]Memory Segments:[/bold] {len(device.memory_segments)}
[bold]Modules:[/bold] {len(device.modules)}
[bold]Interrupts:[/bold] {len(device.interrupts)}
[bold]Signatures:[/bold] {len(device.signatures)}
            """.strip()

            panel = Panel(
                info_text, title=f"🔌 Device: {device.name}", border_style="blue"
            )
            console.print(panel)

            # Memory overview
            if device.memory_segments:
                memory_table = Table(title="💾 Memory Overview")
                memory_table.add_column("Segment", style="cyan")
                memory_table.add_column("Start Address", style="green")
                memory_table.add_column("End Address", style="green")
                memory_table.add_column("Size", style="yellow")
                memory_table.add_column("Type", style="magenta")

                for seg in sorted(device.memory_segments, key=lambda x: x.start):
                    end_addr = seg.start + seg.size - 1
                    memory_table.add_row(
                        seg.name,
                        f"0x{seg.start:04X}",
                        f"0x{end_addr:04X}",
                        f"{seg.size:,} bytes",
                        seg.type or "N/A",
                    )

                console.print(memory_table)

            # Module overview
            if device.modules:
                module_table = Table(title="🔧 Modules Overview")
                module_table.add_column("Module", style="cyan")
                module_table.add_column("Register Groups", style="green")
                module_table.add_column("Total Registers", style="yellow")

                for module in device.modules:
                    total_regs = sum(len(rg.registers) for rg in module.register_groups)
                    module_table.add_row(
                        module.name, str(len(module.register_groups)), str(total_regs)
                    )

                console.print(module_table)

    except DeviceNotFoundError as e:
        console.print(f"[red]Device not found: {e}[/red]")
        raise typer.Exit(1)
    except AtPackError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@devices_app.command("search")
def search_devices(
    pattern: Annotated[
        str, typer.Argument(help="Search pattern (supports wildcards * and ?)")
    ],
    atpack_path: AtPackPath,
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
    """🔍 Search for devices by name pattern (supports * and ? wildcards)."""
    try:
        parser = AtPackParser(atpack_path)
        all_devices = parser.get_devices()
        device_family = parser.device_family

        # Filter devices using pattern matching
        matching_devices = [
            device
            for device in all_devices
            if fnmatch.fnmatch(device.upper(), pattern.upper())
        ]

        if not matching_devices:
            console.print(
                f"[yellow]No devices found matching pattern '{pattern}'[/yellow]"
            )
            console.print(f"[dim]Total devices in AtPack: {len(all_devices)}[/dim]")
            return

        data = {
            "search_pattern": pattern,
            "device_family": device_family.value,
            "total_devices": len(all_devices),
            "matching_count": len(matching_devices),
            "matching_devices": matching_devices,
        }

        if format == "json":
            json_output = json.dumps(data, indent=2)
            if output:
                output.write_text(json_output, encoding="utf-8")
                console.print(
                    f"[green]Exported {len(matching_devices)} matching devices to {output}[/green]"
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

            # Family emoji
            family_emoji = {
                DeviceFamily.ATMEL: "🔵" if not no_color else "[ATMEL]",
                DeviceFamily.PIC: "🟡" if not no_color else "[PIC]",
                DeviceFamily.UNSUPPORTED: "⚫" if not no_color else "[UNSUPPORTED]",
            }

            table = Table(
                title=f"{family_emoji[device_family]} {device_family.value} Devices matching '{pattern}'"
            )
            table.add_column("Device Name", style="cyan" if not no_color else None)
            table.add_column("Index", style="dim" if not no_color else None)

            for i, device in enumerate(matching_devices, 1):
                table.add_row(device, str(i))

            if output:
                # Export table as text
                with output_console.capture() as capture:
                    output_console.print(table)
                    output_console.print(
                        f"\nMatching: {len(matching_devices)}/{len(all_devices)} devices"
                    )

                output.write_text(capture.get(), encoding="utf-8")
                console.print(
                    f"[green]Exported {len(matching_devices)} matching devices to {output}[/green]"
                )
            else:
                output_console.print(table)
                success_msg = (
                    f"[green]Matching: {len(matching_devices)}/{len(all_devices)} devices[/green]"
                    if not no_color
                    else f"Matching: {len(matching_devices)}/{len(all_devices)} devices"
                )
                output_console.print(f"\n{success_msg}")

    except AtPackError as e:
        error_msg = f"[red]Error: {e}[/red]" if not no_color else f"Error: {e}"
        console.print(error_msg)
        raise typer.Exit(1)
