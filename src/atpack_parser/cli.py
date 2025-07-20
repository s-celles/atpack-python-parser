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
            console.print_json(json.dumps(files, indent=2))
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
):
    """📋 List all devices in an AtPack."""
    try:
        parser = AtPackParser(atpack_path)
        devices = parser.get_devices()
        device_family = parser.device_family

        if format == "json":
            data = {
                "device_family": device_family.value,
                "device_count": len(devices),
                "devices": devices,
            }
            console.print_json(json.dumps(data, indent=2))
        else:
            # Family emoji
            family_emoji = {
                DeviceFamily.ATMEL: "🔵",
                DeviceFamily.PIC: "🟡",
                DeviceFamily.UNSUPPORTED: "⚫",
            }

            table = Table(
                title=f"{family_emoji[device_family]} {device_family.value} "
                f"Devices in {atpack_path.name}"
            )
            table.add_column("Device Name", style="cyan")
            table.add_column("Index", style="dim")

            for i, device in enumerate(devices, 1):
                table.add_row(device, str(i))

            console.print(table)
            console.print(f"\n[green]Total: {len(devices)} devices[/green]")

    except AtPackError as e:
        console.print(f"[red]Error: {e}[/red]")
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
            console.print_json(device.model_dump_json(indent=2))
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
):
    """💾 Show memory layout for a device."""
    try:
        parser = AtPackParser(atpack_path)
        memory_segments = parser.get_device_memory(device_name)

        if format == "json":
            data = [seg.model_dump() for seg in memory_segments]
            console.print_json(json.dumps(data, indent=2))
        else:
            table = Table(title=f"💾 Memory Layout: {device_name}")
            table.add_column("Segment", style="cyan")
            table.add_column("Start Address", style="green")
            table.add_column("End Address", style="green")
            table.add_column("Size", style="yellow")
            table.add_column("Type", style="magenta")
            table.add_column("Page Size", style="blue")
            table.add_column("Address Space", style="dim")

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

    except DeviceNotFoundError as e:
        console.print(f"[red]Device not found: {e}[/red]")
        raise typer.Exit(1)
    except AtPackError as e:
        console.print(f"[red]Error: {e}[/red]")
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
            console.print_json(json.dumps(data, indent=2))
        else:
            table = Table(
                title=f"📋 Registers: {device_name}"
                + (f" (Module: {module})" if module else "")
            )
            table.add_column("Module", style="cyan")
            table.add_column("Register", style="green")
            table.add_column("Offset", style="yellow")
            table.add_column("Size", style="blue")
            table.add_column("Access", style="magenta")
            table.add_column("Bitfields", style="dim")

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

            console.print(table)

    except DeviceNotFoundError as e:
        console.print(f"[red]Device not found: {e}[/red]")
        raise typer.Exit(1)
    except AtPackError as e:
        console.print(f"[red]Error: {e}[/red]")
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
            console.print_json(found_register.model_dump_json(indent=2))
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

                for bf in found_register.bitfields:
                    bit_range = (
                        f"{bf.bit_offset}"
                        if bf.bit_width == 1
                        else f"{bf.bit_offset + bf.bit_width - 1}:{bf.bit_offset}"
                    )
                    values_str = f"{len(bf.values)} values" if bf.values else "N/A"

                    table.add_row(
                        bf.name,
                        bit_range,
                        f"0x{bf.mask:0{found_register.size * 2}X}",
                        bf.caption or "N/A",
                        values_str,
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
                    if hasattr(value, "model_dump"):
                        data[key] = [item.model_dump() for item in value]
                    else:
                        data[key] = value
                console.print_json(json.dumps(data, indent=2))
            else:
                items = config.get(config_type, [])
                if hasattr(items, "model_dump"):
                    data = [item.model_dump() for item in items]
                else:
                    data = items
                console.print_json(json.dumps(data, indent=2))
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
            console.print_json(json.dumps(data, indent=2))
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
  atpack devices info ATmega16 mypack.atpack
  
  atpack memory show ATmega16 mypack.atpack
  
  atpack registers list ATmega16 mypack.atpack
  atpack registers list ATmega16 mypack.atpack --module GPIO
  atpack registers show ATmega16 PORTB mypack.atpack
  
  atpack config show PIC16F876A mypack.atpack
  atpack config show PIC16F876A mypack.atpack --type fuses
  
  atpack scan ./atpacks/ --format json
    """
    tree_text += examples_text
    
    panel = Panel(
        tree_text,
        title="🌳 Command Tree with Examples",
        border_style="green",
        padding=(1, 2)
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
        "files": [("list", "List files in an AtPack"), ("info", "Show AtPack file information")],
        "devices": [("list", "List all devices"), ("info", "Show device details")],
        "memory": [("show", "Show memory layout")],
        "registers": [("list", "List registers"), ("show", "Show register details")],
        "config": [("show", "Show configuration information")],
    }
    
    # Global commands
    global_commands = [
        ("scan", "🔍", "Scan directory for AtPack files"),
        ("help-tree", "🌳", "Show command tree structure")
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
            "📁 files", 
            "list, info", 
            "Manage AtPack files and show metadata"
        )
        help_table.add_row(
            "🔌 devices", 
            "list, info", 
            "Browse devices and get detailed specs"
        )
        help_table.add_row(
            "💾 memory", 
            "show", 
            "Analyze memory layouts and segments"
        )
        help_table.add_row(
            "📋 registers", 
            "list, show", 
            "Explore registers and bitfields"
        )
        help_table.add_row(
            "⚙️ config", 
            "show", 
            "View fuses, config words, interrupts"
        )
        help_table.add_row(
            "🔍 Global", 
            "scan, help-tree", 
            "Utility commands"
        )
        
        console.print(help_table)
        
        console.print(f"\n[dim]💡 Use [/dim][bold]atpack help COMMAND[/bold][dim] for specific help[/dim]")
        console.print(f"[dim]💡 Use [/dim][bold]atpack help-tree[/bold][dim] to see the complete structure[/dim]")
        console.print(f"[dim]💡 Use [/dim][bold]atpack COMMAND --help[/bold][dim] for detailed options[/dim]\n")
        
    else:
        # Show specific command help
        help_map = {
            "files": "📁 Files: list, info - Manage AtPack files\n  Example: atpack files list mypack.atpack",
            "devices": "🔌 Devices: list, info - Device information\n  Example: atpack devices info ATmega16 mypack.atpack", 
            "memory": "💾 Memory: show - Memory layouts\n  Example: atpack memory show ATmega16 mypack.atpack",
            "registers": "📋 Registers: list, show - Register details\n  Example: atpack registers list ATmega16 mypack.atpack",
            "config": "⚙️ Config: show - Configuration data\n  Example: atpack config show ATmega16 mypack.atpack",
            "scan": "🔍 Scan: Search for AtPack files\n  Example: atpack scan ./atpacks/",
            "help-tree": "🌳 Help Tree: Show command structure\n  Example: atpack help-tree"
        }
        
        if command in help_map:
            panel = Panel(
                help_map[command],
                title=f"❓ Help for '{command}'",
                border_style="blue"
            )
            console.print(panel)
        else:
            console.print(f"[red]Unknown command: {command}[/red]")
            console.print("[dim]Available commands: files, devices, memory, registers, config, scan, help-tree[/dim]")
            console.print("[dim]Use 'atpack help-tree' to see the complete command structure[/dim]")

if __name__ == "__main__":
    app()
