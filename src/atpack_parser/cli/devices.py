"""Devices command group for AtPack CLI."""

import fnmatch
import json
import io
import csv
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .. import AtPackParser
from ..exceptions import AtPackError, DeviceNotFoundError
from ..models import DeviceFamily
from ..utils.family_display import get_family_emoji, format_family_display
from ..utils.device_specs import (
    get_max_frequency_from_oscillators,
    get_device_default_frequency,
    get_temperature_range_from_device_name,
    get_device_default_vdd_range,
)
from ..utils.units import (
    format_frequency,
    format_voltage,
    format_voltage_range,
    format_temperature,
    parse_temperature_range,
)
from .common import AtPackPath, DeviceName, console, handle_device_not_found_error, handle_atpack_error

# Create devices sub-command app
devices_app = typer.Typer(name="devices", help="🔌 Device information")


def _detect_atmel_pin_type(pad_name: str) -> str:
    """Detect ATMEL pin type based on pad name.

    Note: ATMEL pin type is inferred from the pad name using heuristic pattern matching.
    This is necessary because ATMEL AtPack files don't explicitly specify pin types,
    so we analyze the pad name (e.g., VCC → power, RESET → control, ADC → analog, etc.)
    to determine the most likely pin function category. This inference is based on
    common naming conventions used in ATMEL microcontroller pad designations.
    """
    if not pad_name:
        return "Unknown"

    pad_upper = pad_name.upper()

    # Power pins
    if any(power in pad_upper for power in ["VCC", "AVCC", "GND", "VSS"]):
        return "power"

    # Reset pins
    if "RESET" in pad_upper:
        return "control"

    # Oscillator/Crystal pins
    if any(osc in pad_upper for osc in ["XTAL", "OSC"]):
        return "oscillator"

    # ADC/Analog pins
    if any(analog in pad_upper for analog in ["ADC", "AREF", "AVSS"]):
        return "analog"

    # Programming/Debug pins
    if any(prog in pad_upper for prog in ["PDI", "UPDI", "TDI", "TDO", "TMS", "TCK"]):
        return "programming"

    # Digital I/O pins (default for Port pins)
    return "digital"


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

            # Format family display with emoji
            family_display = (
                format_family_display(device_family, include_name=True)
                if not no_color
                else f"[{device_family.value}]"
            )

            table = Table(title=f"{family_display} Devices in {atpack_path.name}")
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
        handle_atpack_error(e, no_color)


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
            # Format family display with emoji
            family_display = format_family_display(device.family, include_name=True)

            # Basic info panel
            info_text = f"""
[bold]Family:[/bold] {family_display}
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
        handle_device_not_found_error(e, parser)
    except AtPackError as e:
        handle_atpack_error(e)


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

            # Format family display with emoji
            family_display = (
                format_family_display(device_family, include_name=True)
                if not no_color
                else f"[{device_family.value}]"
            )

            table = Table(title=f"{family_display} Devices matching '{pattern}'")
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
        handle_atpack_error(e, no_color)


@devices_app.command("packages")
def list_packages(
    device_name: DeviceName,
    atpack_path: AtPackPath,
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format (table, json, csv)")
    ] = "table",
    output: Annotated[
        Optional[Path], typer.Option("--output", "-o", help="Export to file")
    ] = None,
    no_color: Annotated[
        bool, typer.Option("--no-color", help="Disable colored output")
    ] = False,
):
    """📦 List all packages/variants available for a device."""
    try:
        parser = AtPackParser(atpack_path)
        device = parser.get_device(device_name)
        device_family = parser.device_family

        package_data = []

        if device_family == DeviceFamily.ATMEL:
            # Handle ATMEL package variants
            if device.atmel_package_variants:
                for variant in device.atmel_package_variants:
                    # Format temperature range using pint
                    temp_range = "N/A"
                    if variant.temp_min is not None and variant.temp_max is not None:
                        temp_range = parse_temperature_range(
                            f"{variant.temp_min}°C to {variant.temp_max}°C"
                        )

                    # Format voltage range using pint
                    vcc_range = "N/A"
                    if variant.vcc_min is not None and variant.vcc_max is not None:
                        vcc_range = format_voltage_range(
                            f"{variant.vcc_min}V", f"{variant.vcc_max}V"
                        )

                    # Format frequency using pint
                    max_speed = "N/A"
                    if variant.speed_max:
                        max_speed = format_frequency(f"{variant.speed_max} Hz")

                    package_data.append(
                        {
                            "package": variant.package,
                            "pinout": variant.pinout,
                            "order_code": variant.order_code or "N/A",
                            "temp_range": temp_range,
                            "vcc_range": vcc_range,
                            "max_speed": max_speed,
                        }
                    )

            # Also check for pinout packages if no package variants are available
            if not package_data and device.atmel_pinouts:
                for pinout in device.atmel_pinouts:
                    package_data.append(
                        {
                            "package": pinout.name,
                            "pinout": pinout.name,
                            "order_code": "N/A",
                            "temp_range": "N/A",
                            "vcc_range": "N/A",
                            "max_speed": "N/A",
                        }
                    )

        elif device_family == DeviceFamily.PIC:
            # For PIC devices, package info is typically not encoded in the device files
            # but we can infer likely packages based on pin count and device characteristics
            pin_count = len(device.pinout) if device.pinout else 0

            # Common PIC package mappings based on pin count
            common_packages = []
            if pin_count == 8:
                common_packages = ["PDIP-8", "SOIC-8"]
            elif pin_count == 14:
                common_packages = ["PDIP-14", "SOIC-14"]
            elif pin_count == 18:
                common_packages = ["PDIP-18", "SOIC-18"]
            elif pin_count == 20:
                common_packages = ["PDIP-20", "SOIC-20"]
            elif pin_count == 28:
                common_packages = ["PDIP-28", "SOIC-28", "PLCC-28"]
            elif pin_count == 40:
                common_packages = ["PDIP-40", "PLCC-44", "TQFP-44"]
            elif pin_count == 44:
                common_packages = ["PLCC-44", "TQFP-44", "QFN-44"]
            elif pin_count == 64:
                common_packages = ["TQFP-64", "QFN-64"]
            elif pin_count == 80:
                common_packages = ["TQFP-80", "PQFP-80"]
            elif pin_count == 100:
                common_packages = ["TQFP-100", "PQFP-100"]
            else:
                common_packages = ["Unknown"]

            # Get device specifications using configuration-based approach
            vdd_range = "N/A"
            if device.power_specs:
                if device.power_specs.vdd_min and device.power_specs.vdd_max:
                    vdd_range = f"{device.power_specs.vdd_min}V to {device.power_specs.vdd_max}V"
            else:
                # Use default VDD range from configuration if power specs not available
                vdd_range = get_device_default_vdd_range(device_name)

            # Extract temperature range from device name using configuration
            temp_range = get_temperature_range_from_device_name(device_name)

            # Extract frequency info from oscillator configs using configuration
            max_freq = get_max_frequency_from_oscillators(
                device.oscillator_configs, device_name
            )

            # Fallback to device series default if oscillator-based detection fails
            if max_freq == "N/A":
                max_freq = get_device_default_frequency(device_name)

            # For PIC devices, create entries for each likely package type
            if common_packages and common_packages != ["Unknown"]:
                for pkg in common_packages:
                    package_data.append(
                        {
                            "package": f"{pkg}(1)",
                            "pinout": f"{pin_count}-pin",
                            "order_code": f"{device_name}-{pkg.replace('-', '')}(1)",
                            "temp_range": (
                                f"{temp_range}(2)"
                                if temp_range != "N/A"
                                else temp_range
                            ),
                            "vcc_range": vdd_range,
                            "max_speed": (
                                f"{max_freq}(2)" if max_freq != "N/A" else max_freq
                            ),
                        }
                    )
            else:
                # Fallback to single default entry
                package_data.append(
                    {
                        "package": (
                            f"{pin_count}-pin(1)" if pin_count > 0 else "Unknown(1)"
                        ),
                        "pinout": f"{pin_count}-pin",
                        "order_code": f"{device_name}-(1)",
                        "temp_range": (
                            f"{temp_range}(2)" if temp_range != "N/A" else temp_range
                        ),
                        "vcc_range": vdd_range,
                        "max_speed": (
                            f"{max_freq}(2)" if max_freq != "N/A" else max_freq
                        ),
                    }
                )
        else:
            console.print(f"[red]Unsupported device family: {device_family}[/red]")
            return

        if not package_data:
            console.print(
                f"[yellow]No package information found for {device_name}[/yellow]"
            )
            return

        # Output formatting
        if format == "json":
            output_data = {
                "device": device_name,
                "family": device_family.value,
                "package_count": len(package_data),
                "packages": package_data,
            }

            json_output = json.dumps(output_data, indent=2)
            if output:
                output.write_text(json_output, encoding="utf-8")
                console.print(
                    f"[green]Exported package list for {device_name} to {output}[/green]"
                )
            else:
                print(json_output)

        elif format == "csv":
            import csv
            import io

            csv_output = io.StringIO()
            fieldnames = [
                "package",
                "pinout",
                "order_code",
                "temp_range",
                "vcc_range",
                "max_speed",
            ]

            writer = csv.DictWriter(csv_output, fieldnames=fieldnames)
            writer.writeheader()

            for package in package_data:
                writer.writerow(package)

            csv_text = csv_output.getvalue()
            if output:
                output.write_text(csv_text, encoding="utf-8")
                console.print(
                    f"[green]Exported package list for {device_name} to {output}[/green]"
                )
            else:
                print(csv_text)

        else:  # table format
            output_console = (
                Console(force_terminal=not no_color)
                if not no_color
                else Console(force_terminal=False)
            )

            # Format family display with emoji
            family_emoji = (
                get_family_emoji(device_family)
                if not no_color
                else f"[{device_family.value}]"
            )
            title = f"📦 {family_emoji} {device_name} Packages"

            table = Table(title=title)
            table.add_column("Package", style="cyan" if not no_color else None)
            table.add_column("Pinout", style="green" if not no_color else None)
            table.add_column("Order Code", style="yellow" if not no_color else None)
            table.add_column("Temperature", style="blue" if not no_color else None)
            table.add_column("VCC Range", style="magenta" if not no_color else None)
            table.add_column("Max Speed", style="red" if not no_color else None)

            for package in package_data:
                table.add_row(
                    package["package"],
                    package["pinout"],
                    package["order_code"],
                    package["temp_range"],
                    package["vcc_range"],
                    package["max_speed"],
                )

            if output:
                with output_console.capture() as capture:
                    output_console.print(table)
                    output_console.print(f"\nTotal packages: {len(package_data)}")

                    # Add footnotes for PIC devices
                    if device_family == DeviceFamily.PIC:
                        output_console.print(
                            "(1) Package information inferred from pin count (not explicitly defined in AtPack file)"
                        )
                        output_console.print(
                            "(2) Data derived from internal device specifications database pic_device_specs.json (not explicitly defined in AtPack file)"
                        )

                output.write_text(capture.get(), encoding="utf-8")
                console.print(
                    f"[green]Exported package list for {device_name} to {output}[/green]"
                )
            else:
                output_console.print(table)
                output_console.print(
                    f"\n[green]Total packages: {len(package_data)}[/green]"
                    if not no_color
                    else f"\nTotal packages: {len(package_data)}"
                )

                # Add footnotes for PIC devices to explain inferred data
                if device_family == DeviceFamily.PIC:
                    footnote1_msg = "[dim](1) Package information inferred from pin count (not explicitly defined in AtPack file)[/dim]"
                    footnote2_msg = "[dim](2) Data derived from internal device specifications database pic_device_specs.json (not explicitly defined in AtPack file)[/dim]"
                    if no_color:
                        footnote1_msg = "(1) Package information inferred from pin count (not explicitly defined in AtPack file)"
                        footnote2_msg = "(2) Data derived from internal device specifications database pic_device_specs.json (not explicitly defined in AtPack file)"
                    output_console.print(footnote1_msg)
                    output_console.print(footnote2_msg)

    except DeviceNotFoundError as e:
        handle_device_not_found_error(e, parser, no_color)
    except AtPackError as e:
        handle_atpack_error(e, no_color)


@devices_app.command("pinout")
def show_pinout(
    device_name: DeviceName,
    atpack_path: AtPackPath,
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format (table, json, csv)")
    ] = "table",
    output: Annotated[
        Optional[Path], typer.Option("--output", "-o", help="Export to file")
    ] = None,
    no_color: Annotated[
        bool, typer.Option("--no-color", help="Disable colored output")
    ] = False,
    package: Annotated[
        Optional[str],
        typer.Option("--package", "-p", help="Specific package/pinout to show"),
    ] = None,
    show_functions: Annotated[
        bool, typer.Option("--functions", help="Show pin alternative functions")
    ] = False,
):
    """📌 Show pinout information for a device. If no package is specified, shows all packages."""
    try:
        parser = AtPackParser(atpack_path)
        device = parser.get_device(device_name)
        device_family = parser.device_family

        # Prepare pinout data based on device family, grouped by package
        packages_pinout_data = {}

        if device_family == DeviceFamily.ATMEL:
            # Handle ATMEL pinouts
            if device.atmel_pinouts:
                for pinout in device.atmel_pinouts:
                    if package and package.lower() not in pinout.name.lower():
                        continue

                    package_name = pinout.name
                    packages_pinout_data[package_name] = []

                    for pin in pinout.pins:
                        pad_name = pin.get("pad", "")
                        # Detect pin type from pad name
                        pin_type = _detect_atmel_pin_type(pad_name)

                        packages_pinout_data[package_name].append(
                            {
                                "package": package_name,
                                "position": pin.get("position", ""),
                                "pad": pad_name,
                                "pin_type": pin_type,
                                "functions": [],  # ATMEL functions would need additional parsing
                            }
                        )
            else:
                console.print(
                    f"[yellow]No ATMEL pinout information found for {device_name}[/yellow]"
                )
                return

        elif device_family == DeviceFamily.PIC:
            # Handle PIC pinouts
            if device.pinout:
                package_name = package or "Default"
                packages_pinout_data[package_name] = []

                for pin_info in device.pinout:
                    functions = []
                    if show_functions and pin_info.alternative_functions:
                        functions = [f.name for f in pin_info.alternative_functions]

                    packages_pinout_data[package_name].append(
                        {
                            "package": package_name,
                            "position": (
                                str(pin_info.physical_pin)
                                if pin_info.physical_pin
                                else ""
                            ),
                            "pad": pin_info.primary_function or "",
                            "pin_type": pin_info.pin_type or "Unknown",
                            "functions": functions,
                        }
                    )
            else:
                console.print(
                    f"[yellow]No PIC pinout information found for {device_name}[/yellow]"
                )
                return
        else:
            console.print(f"[red]Unsupported device family: {device_family}[/red]")
            return

        if not packages_pinout_data:
            console.print(
                f"[yellow]No pinout data available for {device_name}[/yellow]"
            )
            return

        # Flatten data for JSON/CSV output
        all_pinout_data = []
        for pkg_name, pins in packages_pinout_data.items():
            all_pinout_data.extend(pins)

        # Output formatting
        if format == "json":
            output_data = {
                "device": device_name,
                "family": device_family.value,
                "package_filter": package,
                "total_pins": len(all_pinout_data),
                "packages": packages_pinout_data,
            }

            json_output = json.dumps(output_data, indent=2)
            if output:
                output.write_text(json_output, encoding="utf-8")
                console.print(
                    f"[green]Exported pinout for {device_name} to {output}[/green]"
                )
            else:
                print(json_output)

        elif format == "csv":
            import csv
            import io

            csv_output = io.StringIO()
            fieldnames = ["package", "position", "pad", "pin_type"]
            if show_functions:
                fieldnames.append("functions")

            writer = csv.DictWriter(csv_output, fieldnames=fieldnames)
            writer.writeheader()

            for pin in all_pinout_data:
                row = {
                    "package": pin["package"],
                    "position": pin["position"],
                    "pad": pin["pad"],
                    "pin_type": pin["pin_type"],
                }
                if show_functions:
                    row["functions"] = (
                        ", ".join(pin["functions"]) if pin["functions"] else ""
                    )
                writer.writerow(row)

            csv_text = csv_output.getvalue()
            if output:
                output.write_text(csv_text, encoding="utf-8")
                console.print(
                    f"[green]Exported pinout for {device_name} to {output}[/green]"
                )
            else:
                print(csv_text)

        else:  # table format
            output_console = (
                Console(force_terminal=not no_color)
                if not no_color
                else Console(force_terminal=False)
            )

            # Format family display with emoji
            family_emoji = (
                get_family_emoji(device_family)
                if not no_color
                else f"[{device_family.value}]"
            )

            # Output each package separately for better readability
            for pkg_name, pinout_data in packages_pinout_data.items():
                title = f"📌 {family_emoji} {device_name} - {pkg_name}"

                table = Table(title=title)
                table.add_column(
                    "Pin", style="cyan" if not no_color else None, min_width=4
                )
                table.add_column(
                    "Pad/Function", style="green" if not no_color else None
                )
                table.add_column("Type", style="yellow" if not no_color else None)

                if show_functions:
                    table.add_column(
                        "Alt Functions", style="blue" if not no_color else None
                    )

                # Sort by position if numeric, otherwise alphabetically
                try:
                    pinout_data_sorted = sorted(
                        pinout_data,
                        key=lambda x: (
                            int(x["position"]) if x["position"].isdigit() else 999
                        ),
                    )
                except (ValueError, TypeError):
                    pinout_data_sorted = sorted(
                        pinout_data, key=lambda x: x["position"]
                    )

                for pin in pinout_data_sorted:
                    row = [pin["position"], pin["pad"], pin["pin_type"]]

                    if show_functions:
                        functions_str = ", ".join(
                            pin["functions"][:3]
                        )  # Limit to first 3 functions
                        if len(pin["functions"]) > 3:
                            functions_str += f" (+{len(pin['functions']) - 3} more)"
                        row.append(functions_str)

                    table.add_row(*row)

                output_console.print(table)
                output_console.print(
                    f"[green]Package {pkg_name}: {len(pinout_data)} pins[/green]"
                    if not no_color
                    else f"Package {pkg_name}: {len(pinout_data)} pins"
                )

                # Add spacing between packages if showing multiple
                if len(packages_pinout_data) > 1:
                    output_console.print()

            # Summary
            total_packages = len(packages_pinout_data)
            total_pins = len(all_pinout_data)

            summary_msg = f"Total: {total_packages} package{'s' if total_packages != 1 else ''}, {total_pins} pin{'s' if total_pins != 1 else ''}"
            output_console.print(
                f"[bold green]{summary_msg}[/bold green]"
                if not no_color
                else summary_msg
            )

            # Add explanatory note for ATMEL devices
            if device_family == DeviceFamily.ATMEL:
                atmel_note = "Note: Pin types for ATMEL devices are inferred from pad names using heuristic pattern matching."
                output_console.print(
                    f"[dim]{atmel_note}[/dim]" if not no_color else atmel_note
                )

            if output:
                with output_console.capture() as capture:
                    # Re-capture all output for file export
                    for pkg_name, pinout_data in packages_pinout_data.items():
                        title = f"📌 {family_emoji} {device_name} - {pkg_name}"
                        table = Table(title=title)
                        table.add_column("Pin", min_width=4)
                        table.add_column("Pad/Function")
                        table.add_column("Type")

                        if show_functions:
                            table.add_column("Alt Functions")

                        try:
                            pinout_data_sorted = sorted(
                                pinout_data,
                                key=lambda x: (
                                    int(x["position"])
                                    if x["position"].isdigit()
                                    else 999
                                ),
                            )
                        except (ValueError, TypeError):
                            pinout_data_sorted = sorted(
                                pinout_data, key=lambda x: x["position"]
                            )

                        for pin in pinout_data_sorted:
                            row = [pin["position"], pin["pad"], pin["pin_type"]]

                            if show_functions:
                                functions_str = ", ".join(pin["functions"][:3])
                                if len(pin["functions"]) > 3:
                                    functions_str += (
                                        f" (+{len(pin['functions']) - 3} more)"
                                    )
                                row.append(functions_str)

                            table.add_row(*row)

                        output_console.print(table)
                        output_console.print(
                            f"Package {pkg_name}: {len(pinout_data)} pins"
                        )
                        if len(packages_pinout_data) > 1:
                            output_console.print()

                    output_console.print(summary_msg)

                    # Add explanatory note for ATMEL devices in export
                    if device_family == DeviceFamily.ATMEL:
                        output_console.print(
                            "Note: Pin types for ATMEL devices are inferred from pad names using heuristic pattern matching."
                        )

                output.write_text(capture.get(), encoding="utf-8")
                console.print(
                    f"[green]Exported pinout for {device_name} to {output}[/green]"
                )

    except DeviceNotFoundError as e:
        handle_device_not_found_error(e, parser, no_color)
    except AtPackError as e:
        handle_atpack_error(e, no_color)
