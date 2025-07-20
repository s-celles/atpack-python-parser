"""Command Line Interface for AtPack Parser using Typer."""

import json
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from . import AtPackParser
from .exceptions import AtPackError, DeviceNotFoundError
from .models import DeviceFamily

# Create Typer app with hierarchical commands
app = typer.Typer(
    name="atpack",
    help="🔧 AtPack Parser - Parse AtPack files",
    rich_markup_mode="rich",
)

# Create console for rich output
console = Console()

# Sub-commands
files_app = typer.Typer(name="files", help="📁 AtPack file management")
devices_app = typer.Typer(name="devices", help="🔌 Device information")
memory_app = typer.Typer(name="memory", help="💾 Memory information")
registers_app = typer.Typer(name="registers", help="📋 Register information")
config_app = typer.Typer(name="config", help="⚙️ Configuration information")

app.add_typer(files_app)
app.add_typer(devices_app)
app.add_typer(memory_app)
app.add_typer(registers_app)
app.add_typer(config_app)


# Common types
AtPackPath = Annotated[Path, typer.Argument(help="Path to AtPack file or directory")]
DeviceName = Annotated[
    str, typer.Argument(help="Device name (e.g., ATmega16, PIC16F876A)")
]
OutputFormat = Annotated[str, typer.Option("--format", "-f", help="Output format")]


@app.callback()
def main(
    version: Annotated[
        bool, typer.Option("--version", "-v", help="Show version")
    ] = False,
):
    """
    🔧 AtPack Parser CLI - Parse AtPack files

    Available command groups:
    • files    - Manage AtPack files (list, info)
    • devices  - Device information (list, info)
    • memory   - Memory layouts (show)
    • registers - Register details (list, show)
    • config   - Configuration data (show)
    • scan     - Directory scanning
    • help-tree - Show command structure

    Use 'atpack COMMAND --help' for detailed help on each command.
    Use 'atpack help-tree' to see the complete command structure.
    """
    if version:
        from . import __version__

        console.print(f"AtPack Parser v{__version__}")
        raise typer.Exit()


# Files commands
@files_app.command("list")
def list_files(
    atpack_path: AtPackPath,
    pattern: Annotated[
        Optional[str], typer.Option("--pattern", "-p", help="File pattern filter")
    ] = None,
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format")
    ] = "table",
):
    """📁 List files in an AtPack."""
    try:
        parser = AtPackParser(atpack_path)
        files = parser.list_files(pattern)

        if format == "json":
            print(json.dumps(files, indent=2))
        else:
            table = Table(title=f"Files in {atpack_path.name}")
            table.add_column("File Path", style="cyan")
            table.add_column("Size", style="green")

            for file_path in files:
                try:
                    content = parser.read_file(file_path)
                    size = len(content.encode("utf-8"))
                    table.add_row(file_path, f"{size:,} bytes")
                except Exception:
                    table.add_row(file_path, "Unknown")

            console.print(table)

    except AtPackError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@files_app.command("info")
def file_info(atpack_path: AtPackPath):
    """ℹ️ Show AtPack file information."""
    try:
        parser = AtPackParser(atpack_path)
        metadata = parser.metadata
        device_family = parser.device_family

        # Create info panel
        info_text = f"""
[bold]Name:[/bold] {metadata.name}
[bold]Vendor:[/bold] {metadata.vendor}
[bold]Version:[/bold] {metadata.version}
[bold]Device Family:[/bold] {device_family.value}
[bold]Description:[/bold] {metadata.description or "N/A"}
[bold]URL:[/bold] {metadata.url or "N/A"}
        """.strip()

        panel = Panel(info_text, title="📦 AtPack Information", border_style="blue")
        console.print(panel)

        # Show device count
        try:
            devices = parser.get_devices()
            console.print(f"\n[green]Found {len(devices)} devices[/green]")
        except Exception as e:
            console.print(f"\n[yellow]Warning: Could not count devices: {e}[/yellow]")

    except AtPackError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


# Device commands
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
                memory_table.add_column("Start", style="green")
                memory_table.add_column("Size", style="yellow")
                memory_table.add_column("Type", style="magenta")

                for seg in sorted(device.memory_segments, key=lambda x: x.start):
                    memory_table.add_row(
                        seg.name,
                        f"0x{seg.start:04X}",
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


# Memory commands
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


# Register commands
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
            # Create console with color control
            output_console = (
                Console(force_terminal=not no_color)
                if not no_color
                else Console(force_terminal=False)
            )

            table = Table(
                title=f"📋 Registers: {device_name}"
                + (f" (Module: {module})" if module else "")
            )
            table.add_column("Module", style="cyan" if not no_color else None)
            table.add_column("Register", style="green" if not no_color else None)
            table.add_column("Offset", style="yellow" if not no_color else None)
            table.add_column("Size", style="blue" if not no_color else None)
            table.add_column("Access", style="magenta" if not no_color else None)
            table.add_column("Bitfields", style="dim" if not no_color else None)

            for item in sorted(registers, key=lambda x: x["register"].offset):
                reg = item["register"]
                table.add_row(
                    item["module"],
                    reg.name,
                    f"0x{reg.offset:04X}",
                    str(reg.size),
                    reg.access or "RW",
                    str(len(reg.bitfields)),
                )

            if output:
                # Export table as text
                with output_console.capture() as capture:
                    output_console.print(table)

                output.write_text(capture.get(), encoding="utf-8")
                console.print(
                    f"[green]Exported {len(registers)} registers to {output}[/green]"
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
        console.print(f"[red]Device not found: {e}[/red]")
        raise typer.Exit(1)
    except AtPackError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


# Config commands
@config_app.command("show")
def show_config(
    device_name: DeviceName,
    atpack_path: AtPackPath,
    config_type: Annotated[
        str,
        typer.Option(
            "--type", "-t", help="Config type (fuses, config, interrupts, signatures)"
        ),
    ] = "all",
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format")
    ] = "table",
):
    """⚙️ Show configuration information for a device."""
    try:
        parser = AtPackParser(atpack_path)
        config = parser.get_device_config(device_name)

        if format == "json":
            if config_type == "all":
                data = {}
                for key, value in config.items():
                    if isinstance(value, list) and value and hasattr(value[0], "model_dump"):
                        data[key] = [item.model_dump() for item in value]
                    elif hasattr(value, "model_dump"):
                        data[key] = value.model_dump()
                    else:
                        data[key] = value
                print(json.dumps(data, indent=2))
            else:
                items = config.get(config_type, [])
                if isinstance(items, list) and items and hasattr(items[0], "model_dump"):
                    data = [item.model_dump() for item in items]
                elif hasattr(items, "model_dump"):
                    data = items.model_dump()
                else:
                    data = items
                print(json.dumps(data, indent=2))
        else:
            if config_type in ["all", "fuses"] and config["fuses"]:
                table = Table(title="🔒 Fuse Configuration")
                table.add_column("Fuse", style="cyan")
                table.add_column("Offset", style="green")
                table.add_column("Size", style="yellow")
                table.add_column("Default", style="blue")
                table.add_column("Bitfields", style="dim")

                for fuse in config["fuses"]:
                    default_str = (
                        f"0x{fuse.default_value:0{fuse.size * 2}X}"
                        if fuse.default_value
                        else "N/A"
                    )
                    table.add_row(
                        fuse.name,
                        f"0x{fuse.offset:04X}",
                        str(fuse.size),
                        default_str,
                        str(len(fuse.bitfields)),
                    )

                console.print(table)

            if config_type in ["all", "config"] and config["config_words"]:
                table = Table(title="⚙️ Configuration Words")
                table.add_column("Config Word", style="cyan")
                table.add_column("Address", style="green")
                table.add_column("Default", style="yellow")
                table.add_column("Mask", style="blue")
                table.add_column("Fields", style="dim")

                for cw in config["config_words"]:
                    table.add_row(
                        cw.name,
                        f"0x{cw.address:04X}",
                        f"0x{cw.default_value:04X}",
                        f"0x{cw.mask:04X}",
                        str(len(cw.bitfields)),
                    )

                console.print(table)

            if config_type in ["all", "interrupts"] and config["interrupts"]:
                table = Table(title="⚡ Interrupts")
                table.add_column("Index", style="cyan")
                table.add_column("Name", style="green")
                table.add_column("Description", style="white")

                for interrupt in sorted(config["interrupts"], key=lambda x: x.index):
                    table.add_row(
                        str(interrupt.index), interrupt.name, interrupt.caption or "N/A"
                    )

                console.print(table)

            if config_type in ["all", "signatures"] and config["signatures"]:
                table = Table(title="✍️ Device Signatures")
                table.add_column("Name", style="cyan")
                table.add_column("Address", style="green")
                table.add_column("Value", style="yellow")

                for sig in config["signatures"]:
                    addr_str = (
                        f"0x{sig.address:02X}" if sig.address is not None else "N/A"
                    )
                    table.add_row(sig.name, addr_str, f"0x{sig.value:02X}")

                console.print(table)

    except DeviceNotFoundError as e:
        console.print(f"[red]Device not found: {e}[/red]")
        raise typer.Exit(1)
    except AtPackError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


# Global commands
@app.command("scan")
def scan_directory(
    directory: Annotated[
        Path, typer.Argument(help="Directory to scan for AtPack files")
    ],
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format")
    ] = "table",
):
    """🔍 Scan directory for AtPack files."""
    try:
        atpack_files = []

        # Look for .atpack files and directories with _atpack suffix
        for path in directory.rglob("*"):
            if path.is_file() and path.suffix == ".atpack":
                atpack_files.append(path)
            elif path.is_dir() and path.name.endswith("_atpack"):
                atpack_files.append(path)

        if format == "json":
            data = []
            for atpack_path in atpack_files:
                try:
                    parser = AtPackParser(atpack_path)
                    metadata = parser.metadata
                    data.append(
                        {
                            "path": str(atpack_path),
                            "name": metadata.name,
                            "vendor": metadata.vendor,
                            "family": parser.device_family.value,
                            "device_count": len(parser.get_devices()),
                        }
                    )
                except Exception:
                    data.append(
                        {
                            "path": str(atpack_path),
                            "name": atpack_path.name,
                            "vendor": "Unknown",
                            "family": "Unknown",
                            "device_count": 0,
                        }
                    )
            print(json.dumps(data, indent=2))
        else:
            table = Table(title=f"🔍 AtPack Files in {directory}")
            table.add_column("Path", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Vendor", style="yellow")
            table.add_column("Family", style="blue")
            table.add_column("Devices", style="magenta")

            for atpack_path in sorted(atpack_files):
                try:
                    parser = AtPackParser(atpack_path)
                    metadata = parser.metadata
                    device_count = len(parser.get_devices())
                    family = parser.device_family.value

                    # Family emoji
                    family_emoji = {"ATMEL": "🔵", "PIC": "🟡", "UNSUPPORTED": "⚫"}
                    family_display = f"{family_emoji.get(family, '⚫')} {family}"

                    table.add_row(
                        str(atpack_path.relative_to(directory)),
                        metadata.name,
                        metadata.vendor,
                        family_display,
                        str(device_count),
                    )
                except Exception:
                    table.add_row(
                        str(atpack_path.relative_to(directory)),
                        atpack_path.name,
                        "Error",
                        "⚫ Unknown",
                        "0",
                    )

            console.print(table)
            console.print(f"\n[green]Found {len(atpack_files)} AtPack files[/green]")

    except Exception as e:
        console.print(f"[red]Error scanning directory: {e}[/red]")
        raise typer.Exit(1)


@app.command("help-tree")
def help_tree_command():
    """🌳 Show the complete command tree structure with examples."""
    show_command_tree_content()


def show_command_tree_content():
    """Show the complete command tree structure."""
    tree_text = generate_command_tree()

    examples_text = """

📚 Usage Examples:
  atpack files list mypack.atpack
  atpack files info mypack.atpack
  
  atpack devices list mypack.atpack
  atpack devices info PIC16F877 mypack.atpack
  
  atpack memory show PIC16F877 mypack.atpack
  
  atpack registers list PIC16F877 mypack.atpack
  atpack registers list PIC16F877 mypack.atpack --module GPIO
  atpack registers show PIC16F877 PORTB mypack.atpack
  
  atpack config show PIC16F877 mypack.atpack
  atpack config show PIC16F877 mypack.atpack --type fuses
  
  atpack scan ./atpacks/ --format json
    """
    tree_text += examples_text

    panel = Panel(
        tree_text,
        title="🌳 Command Tree with Examples",
        border_style="green",
        padding=(1, 2),
    )
    console.print(panel)


def generate_command_tree() -> str:
    """Generate a dynamic command tree from the Typer app structure."""
    lines = ["🔧 atpack - AtPack Parser CLI"]

    # Get all registered sub-apps
    sub_apps = {
        "files": ("📁", "AtPack file management"),
        "devices": ("🔌", "Device information"),
        "memory": ("💾", "Memory information"),
        "registers": ("📋", "Register information"),
        "config": ("⚙️", "Configuration information"),
    }

    # Commands for each sub-app
    sub_commands = {
        "files": [
            ("list", "List files in an AtPack"),
            ("info", "Show AtPack file information"),
        ],
        "devices": [
            ("list", "List all devices"),
            ("info", "Show device details"),
            ("search", "Search devices by pattern"),
        ],
        "memory": [("show", "Show memory layout")],
        "registers": [("list", "List registers"), ("show", "Show register details")],
        "config": [("show", "Show configuration information")],
    }

    # Global commands
    global_commands = [
        ("scan", "🔍", "Scan directory for AtPack files"),
        ("help-tree", "🌳", "Show command tree structure"),
    ]

    # Build tree for sub-apps
    sub_app_count = len(sub_apps)
    for i, (name, (emoji, desc)) in enumerate(sub_apps.items()):
        is_last_sub_app = i == sub_app_count - 1 and not global_commands
        prefix = "└── " if is_last_sub_app else "├── "
        lines.append(f"{prefix}{emoji} {name} - {desc}")

        if name in sub_commands:
            cmd_count = len(sub_commands[name])
            for j, (cmd_name, cmd_desc) in enumerate(sub_commands[name]):
                is_last_cmd = j == cmd_count - 1
                if is_last_sub_app:
                    sub_prefix = "    └── " if is_last_cmd else "    ├── "
                else:
                    sub_prefix = "│   └── " if is_last_cmd else "│   ├── "
                lines.append(f"{sub_prefix}{cmd_name} - {cmd_desc}")

    # Add global commands
    for i, (cmd_name, emoji, desc) in enumerate(global_commands):
        is_last = i == len(global_commands) - 1
        prefix = "└── " if is_last else "├── "
        lines.append(f"{prefix}{emoji} {cmd_name} - {desc}")

    return "\n".join(lines)


@app.command("help")
def interactive_help(
    command: Annotated[
        Optional[str], typer.Argument(help="Specific command for detailed help")
    ] = None,
):
    """❓ Get interactive help for commands."""

    if not command:
        # Show overview
        console.print("\n[bold blue]🔧 AtPack Parser CLI Help[/bold blue]\n")

        help_table = Table(show_header=True, header_style="bold magenta")
        help_table.add_column("Command Group", style="cyan", min_width=12)
        help_table.add_column("Commands", style="green")
        help_table.add_column("Description", style="white")

        help_table.add_row(
            "📁 files", "list, info", "Manage AtPack files and show metadata"
        )
        help_table.add_row(
            "🔌 devices", "list, info, search", "Browse devices and get detailed specs"
        )
        help_table.add_row("💾 memory", "show", "Analyze memory layouts and segments")
        help_table.add_row(
            "📋 registers", "list, show", "Explore registers and bitfields"
        )
        help_table.add_row("⚙️ config", "show", "View fuses, config words, interrupts")
        help_table.add_row("🔍 Global", "scan, help-tree", "Utility commands")

        console.print(help_table)

        console.print(
            f"\n[dim]💡 Use [/dim][bold]atpack help COMMAND[/bold][dim] for specific help[/dim]"
        )
        console.print(
            f"[dim]💡 Use [/dim][bold]atpack help-tree[/bold][dim] to see the complete structure[/dim]"
        )
        console.print(
            f"[dim]💡 Use [/dim][bold]atpack COMMAND --help[/bold][dim] for detailed options[/dim]\n"
        )

    else:
        # Show specific command help
        help_map = {
            "files": "📁 Files: list, info - Manage AtPack files\n  Example: atpack files list mypack.atpack",
            "devices": "🔌 Devices: list, info, search - Device information\n  Example: atpack devices search '*877*' mypack.atpack",
            "memory": "💾 Memory: show - Memory layouts\n  Example: atpack memory show ATmega16 mypack.atpack",
            "registers": "📋 Registers: list, show - Register details\n  Example: atpack registers list ATmega16 mypack.atpack",
            "config": "⚙️ Config: show - Configuration data\n  Example: atpack config show ATmega16 mypack.atpack",
            "scan": "🔍 Scan: Search for AtPack files\n  Example: atpack scan ./atpacks/",
            "help-tree": "🌳 Help Tree: Show command structure\n  Example: atpack help-tree",
        }

        if command in help_map:
            panel = Panel(
                help_map[command], title=f"❓ Help for '{command}'", border_style="blue"
            )
            console.print(panel)
        else:
            console.print(f"[red]Unknown command: {command}[/red]")
            console.print(
                "[dim]Available commands: files, devices, memory, registers, config, scan, help-tree[/dim]"
            )
            console.print(
                "[dim]Use 'atpack help-tree' to see the complete command structure[/dim]"
            )


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
    import fnmatch

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


if __name__ == "__main__":
    app()
