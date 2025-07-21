"""Global commands for AtPack CLI."""

import json
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.panel import Panel
from rich.table import Table

from .. import AtPackParser
from .common import console
from ..utils import get_family_emoji

def scan(
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
                    family_emoji = get_family_emoji(family)

                    family_display = f"{family_emoji} {family}"

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
  atpack files extract mypack.atpack
  
  atpack devices list mypack.atpack
  atpack devices info PIC16F877 mypack.atpack
  atpack devices search '*877*' mypack.atpack
  
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
            ("extract", "Extract AtPack file"),
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
            "📁 files", "list, info, extract", "Manage AtPack files and show metadata"
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
            "files": "📁 Files: list, info, extract - Manage AtPack files\n  Example: atpack files list mypack.atpack",
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
