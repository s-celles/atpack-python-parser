"""Config command group for AtPack CLI."""

import json
from typing import Annotated

import typer
from rich.table import Table

from .. import AtPackParser
from ..exceptions import AtPackError, DeviceNotFoundError
from .common import AtPackPath, DeviceName, console, handle_device_not_found_error, handle_atpack_error

# Create config sub-command app
config_app = typer.Typer(name="config", help="⚙️ Configuration information")


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
                    if (
                        isinstance(value, list)
                        and value
                        and hasattr(value[0], "model_dump")
                    ):
                        data[key] = [item.model_dump() for item in value]
                    elif hasattr(value, "model_dump"):
                        data[key] = value.model_dump()
                    else:
                        data[key] = value
                print(json.dumps(data, indent=2))
            else:
                items = config.get(config_type, [])
                if (
                    isinstance(items, list)
                    and items
                    and hasattr(items[0], "model_dump")
                ):
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
        handle_device_not_found_error(e, parser)
    except AtPackError as e:
        handle_atpack_error(e)
