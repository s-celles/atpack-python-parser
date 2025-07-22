"""Interactive CLI mode using Rich and Prompt Toolkit."""

import os
from pathlib import Path
from typing import List, Optional

from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import InMemoryHistory
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from .. import AtPackParser
from ..exceptions import AtPackError

console = Console()


class InteractiveSession:
    """Interactive CLI session manager."""

    def __init__(self):
        self.parser: Optional[AtPackParser] = None
        self.current_atpack: Optional[Path] = None
        self.current_device: Optional[str] = None
        self.history = InMemoryHistory()
        self.session_commands = {
            "help": self.show_help,
            "exit": self.exit_session,
            "quit": self.exit_session,
            "clear": self.clear_screen,
            "load": self.load_atpack,
            "scan": self.scan_directory,
            "info": self.show_info,
            "devices": self.list_devices,
            "select": self.select_device,
            "device-info": self.show_device_info,
            "memory": self.show_memory,
            "registers": self.show_registers,
            "files": self.show_files,
            "config": self.show_config,
            "status": self.show_status,
        }

    def start(self) -> None:
        """Start the interactive session."""
        console.print(
            Panel.fit(
                "[bold blue]🔧 AtPack Parser - Interactive Mode[/bold blue]\n"
                "Type 'help' to see available commands\n"
                "Type 'exit' to quit",
                title="Interactive Session",
                border_style="blue",
            )
        )

        console.print("\nUse 'scan' or 'scan YourDirectory' to scan for AtPack files.")

        # Auto-scan for AtPack files
        self.scan_directory(silent=True)

        while True:
            try:
                # Create command completer
                completer = WordCompleter(list(self.session_commands.keys()))

                # Show current context in prompt
                context = self._get_context_prompt()

                # Get user input with completion
                user_input = prompt(
                    HTML(f"<ansiblue>{context}</ansiblue> ❯ "),
                    completer=completer,
                    history=self.history,
                ).strip()

                if not user_input:
                    continue

                # Parse command and arguments
                parts = user_input.split()
                command = parts[0].lower()
                args = parts[1:] if len(parts) > 1 else []

                # Execute command
                if command in self.session_commands:
                    self.session_commands[command](args)
                else:
                    console.print(f"[red]Unknown command: {command}[/red]")
                    console.print("Type 'help' to see available commands")

            except KeyboardInterrupt:
                if Confirm.ask("\n[yellow]Do you really want to quit?[/yellow]"):
                    break
                console.print()
            except EOFError:
                break

        console.print("[green]Goodbye! 👋[/green]")

    def _get_context_prompt(self) -> str:
        """Get context information for the prompt."""
        parts = ["atpack"]

        if self.current_atpack:
            parts.append(f"[{self.current_atpack.stem}]")

        if self.current_device:
            parts.append(f"({self.current_device})")

        return "".join(parts)

    def show_help(self, args: List[str]) -> None:
        """Show help information."""
        table = Table(
            title="Available Commands", show_header=True, header_style="bold magenta"
        )
        table.add_column("Command", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")
        table.add_column("Example", style="dim")

        commands_help = [
            ("help", "Show this help", "help"),
            ("scan [dir]", "Scan directory for AtPack files", "scan ./atpacks"),
            ("load <file>", "Load an AtPack file", "load mypack.atpack"),
            ("info", "Show AtPack information", "info"),
            ("devices", "List all devices", "devices"),
            ("select <device>", "Select a device", "select ATmega328P"),
            ("device-info", "Show selected device information", "device-info"),
            ("memory", "Show device memory layout", "memory"),
            ("registers", "Show device registers", "registers"),
            ("files", "Show files in AtPack", "files"),
            ("config", "Show AtPack configuration", "config"),
            ("status", "Show session status", "status"),
            ("clear", "Clear screen", "clear"),
            ("exit/quit", "Exit session", "exit"),
        ]

        for cmd, desc, example in commands_help:
            table.add_row(cmd, desc, example)

        console.print(table)

    def exit_session(self, args: List[str]) -> None:
        """Exit the interactive session."""
        raise EOFError

    def clear_screen(self, args: List[str]) -> None:
        """Clear the screen."""
        os.system("cls" if os.name == "nt" else "clear")

    def scan_directory(self, args: List[str] = None, silent: bool = False) -> None:
        """Scan directory for AtPack files."""
        directory = args[0] if args else "./atpacks"

        if not silent:
            console.print(f"[yellow]Scanning directory: {directory}[/yellow]")

        try:
            scan_path = Path(directory)
            if not scan_path.exists():
                console.print(f"[red]Directory not found: {directory}[/red]")
                return

            atpack_files = list(scan_path.glob("*.atpack"))

            if not atpack_files:
                console.print(f"[red]No AtPack files found in {directory}[/red]")
                return

            if not silent:
                table = Table(title=f"AtPack Files Found ({len(atpack_files)})")
                table.add_column("No.", style="cyan")
                table.add_column("File", style="white")
                table.add_column("Size", style="green")

                for i, file in enumerate(atpack_files, 1):
                    size = f"{file.stat().st_size / 1024 / 1024:.1f} MB"
                    table.add_row(str(i), file.name, size)

                console.print(table)

                # Auto-load if only one file
                if len(atpack_files) == 1:
                    if Confirm.ask(
                        f"[yellow]Auto-load {atpack_files[0].name}?[/yellow]"
                    ):
                        self.load_atpack([str(atpack_files[0])])
                console.print("\nUse 'load' to load an AtPack file.")

        except Exception as e:
            console.print(f"[red]Error during scan: {e}[/red]")

    def load_atpack(self, args: List[str]) -> None:
        """Load an AtPack file."""
        if not args:
            # Interactive file selection
            directory = Path("./atpacks")
            if directory.exists():
                atpack_files = list(directory.glob("*.atpack"))
                if atpack_files:
                    console.print("[yellow]Available AtPack files:[/yellow]")
                    for i, file in enumerate(atpack_files, 1):
                        console.print(f"  {i}. {file.name}")

                    file_choices = [str(i) for i in range(1, len(atpack_files) + 1)]
                    name_choices = [f.name for f in atpack_files]
                    choice = Prompt.ask(
                        "Select a file (number or name)",
                        choices=file_choices + name_choices,
                    )

                    if choice.isdigit():
                        selected_file = atpack_files[int(choice) - 1]
                    else:
                        selected_file = next(
                            (f for f in atpack_files if f.name == choice), None
                        )
                        if not selected_file:
                            console.print("[red]File not found[/red]")
                            return

                    args = [str(selected_file)]
                else:
                    console.print("[red]No AtPack files found[/red]")
                    return
            else:
                console.print("[red]Directory ./atpacks not found[/red]")
                return

        file_path = Path(args[0])

        if not file_path.exists():
            console.print(f"[red]File not found: {file_path}[/red]")
            return

        try:
            with console.status(f"[yellow]Loading {file_path.name}...[/yellow]"):
                self.parser = AtPackParser(file_path)
                self.current_atpack = file_path
                self.current_device = None

            devices = self.parser.get_devices()
            console.print("[green]✅ AtPack loaded successfully![/green]")
            console.print(f"Family: {self.parser.device_family.value}")
            console.print(f"Devices: {len(devices)}")
            console.print("\nUse 'devices' to see list of devices in this AtPack file.")

        except AtPackError as e:
            console.print(f"[red]AtPack error: {e}[/red]")
        except Exception as e:
            console.print(f"[red]Unexpected error: {e}[/red]")

    def show_info(self, args: List[str]) -> None:
        """Show information about the current AtPack."""
        if not self.parser:
            console.print("[red]No AtPack loaded. Use 'load <file>'[/red]")
            return

        try:
            metadata = self.parser.metadata
            devices = list(self.parser.get_devices())

            # Calculate file size
            file_size = self.current_atpack.stat().st_size / 1024 / 1024

            panel_content = f"""[bold]AtPack File:[/bold] {self.current_atpack.name}
[bold]File Size:[/bold] {file_size:.1f} MB
[bold]Device Family:[/bold] {self.parser.device_family.value}
[bold]Total Devices:[/bold] {len(devices)}
[bold]Vendor:[/bold] {getattr(metadata, "vendor", "Unknown")}
[bold]Pack Version:[/bold] {getattr(metadata, "version", "Unknown")}
[bold]Description:[/bold] {getattr(metadata, "description", "No description available")[:60]}"""

            console.print(
                Panel(
                    panel_content,
                    title="AtPack Information",
                    border_style="blue",
                )
            )

            # Show some sample devices
            if devices:
                sample_count = min(5, len(devices))
                console.print(
                    f"\n[yellow]Sample devices ({sample_count} of "
                    f"{len(devices)}):[/yellow]"
                )
                for device in devices[:5]:
                    console.print(f"  • {device}")
                if len(devices) > 5:
                    console.print(f"  ... and {len(devices) - 5} more")
                console.print("\nUse 'devices' to see all devices")

        except Exception as e:
            console.print(f"[red]Error retrieving AtPack information: {e}[/red]")

    def list_devices(self, args: List[str]) -> None:
        """List all devices in the current AtPack."""
        if not self.parser:
            console.print("[red]No AtPack loaded. Use 'load <file>'[/red]")
            return

        devices = list(self.parser.get_devices())

        # Filter devices if search term provided
        if args:
            search_term = args[0].lower()
            devices = [d for d in devices if search_term in d.lower()]
            console.print(f"[yellow]Devices containing '{search_term}':[/yellow]")

        if not devices:
            console.print("[red]No devices found[/red]")
            return

        self._display_devices_paginated(devices)

        console.print("\nUse 'select YourDevice' to select a device.")

    def _display_devices_paginated(self, devices: List[str]) -> None:
        """Display devices with pagination."""
        page_size = 20
        total_pages = (len(devices) + page_size - 1) // page_size
        current_page = 0

        while True:
            start_idx = current_page * page_size
            end_idx = min(start_idx + page_size, len(devices))
            page_devices = devices[start_idx:end_idx]

            table = Table(title=f"Devices (Page {current_page + 1}/{total_pages})")
            table.add_column("No.", style="cyan")
            table.add_column("Device", style="white")
            table.add_column("Status", style="green")

            for i, device in enumerate(page_devices, start_idx + 1):
                status = "🎯 SELECTED" if device == self.current_device else ""
                table.add_row(str(i), str(device), status)

            console.print(table)

            if total_pages <= 1:
                break

            # Navigation options
            actions = []
            if current_page > 0:
                actions.append("(p)revious")
            if current_page < total_pages - 1:
                actions.append("(n)ext")
            actions.append("(q)uit")

            if len(actions) > 1:
                choices = []
                if current_page > 0:
                    choices.append("p")
                if current_page < total_pages - 1:
                    choices.append("n")
                choices.append("q")

                action = Prompt.ask(f"Actions: {', '.join(actions)}", choices=choices)

                if action == "p" and current_page > 0:
                    current_page -= 1
                elif action == "n" and current_page < total_pages - 1:
                    current_page += 1
                else:
                    break
            else:
                break

    def select_device(self, args: List[str]) -> None:
        """Select a device."""

        def print_device_selected(device_name: str) -> None:
            console.print(f"[green]✅ Device selected: {device_name}[/green]")
            console.print("Use 'device-info', 'memory', 'registers', ... or any command from 'help'")

        if not self.parser:
            console.print("[red]No AtPack loaded. Use 'load <file>'[/red]")
            return

        if not args:
            # Interactive device selection
            devices = list(self.parser.get_devices())
            console.print(
                f"[yellow]Select a device from {len(devices)} available:[/yellow]"
            )

            # Show first 10 devices for quick selection
            for i, device in enumerate(devices[:10], 1):
                console.print(f"  {i}. {device}")

            if len(devices) > 10:
                console.print(f"  ... and {len(devices) - 10} more")
                console.print("Use 'devices' to see the complete list")

            device_name = Prompt.ask("Device name")
        else:
            device_name = args[0]

        devices = list(self.parser.get_devices())

        # Exact match first
        if device_name in devices:
            self.current_device = device_name
            print_device_selected(device_name)
            return

        # Partial match
        matches = [d for d in devices if device_name.lower() in d.lower()]

        if not matches:
            console.print(f"[red]No device found for: {device_name}[/red]")
            return

        if len(matches) == 1:
            self.current_device = matches[0]
            device_name = matches[0]
            print_device_selected(device_name)
        else:
            console.print(f"[yellow]Multiple matches found ({len(matches)}):[/yellow]")
            for i, match in enumerate(matches[:10], 1):
                console.print(f"  {i}. {match}")

            choice = Prompt.ask(
                "Select by number",
                choices=[str(i) for i in range(1, min(len(matches), 10) + 1)],
            )

            self.current_device = matches[int(choice) - 1]
            device_name = self.current_device
            print_device_selected(device_name)

    def show_device_info(self, args: List[str]) -> None:
        """Show device information."""
        if not self._check_device_selected():
            return

        try:
            device = self.parser.get_device(self.current_device)

            panel_content = f"""[bold]Device:[/bold] {self.current_device}
[bold]Family:[/bold] {self.parser.device_family.value}
[bold]Architecture:[/bold] {getattr(device, "architecture", "Not specified")}
[bold]Package:[/bold] {getattr(device, "package", "Not specified")}
[bold]Flash Size:[/bold] {getattr(device, "flash_size", "Not specified")}
[bold]RAM Size:[/bold] {getattr(device, "ram_size", "Not specified")}"""

            console.print(
                Panel(panel_content, title="Device Information", border_style="green")
            )

        except Exception as e:
            console.print(f"[red]Error retrieving information: {e}[/red]")

    def show_memory(self, args: List[str]) -> None:
        """Show memory layout."""
        if not self._check_device_selected():
            return

        try:
            memory_segments = self.parser.get_device_memory(self.current_device)

            table = Table(title=f"Memory Layout - {self.current_device}")
            table.add_column("Segment", style="cyan")
            table.add_column("Start Address", style="white")
            table.add_column("Size", style="green")
            table.add_column("Description", style="dim")

            if memory_segments:
                for segment in memory_segments[:20]:  # Limit display
                    table.add_row(
                        getattr(segment, "name", "Unknown"),
                        f"0x{getattr(segment, 'start', 0):04X}",
                        f"{getattr(segment, 'size', 0)} bytes",
                        getattr(segment, "description", "")[:50],
                    )
            else:
                # Default memory layout
                table.add_row("Flash", "0x0000", "32KB", "Program memory")
                table.add_row("RAM", "0x2000", "2KB", "Data memory")
                table.add_row("EEPROM", "0x4000", "1KB", "Non-volatile memory")

            console.print(table)

        except Exception as e:
            console.print(f"[red]Error displaying memory: {e}[/red]")

    def show_registers(self, args: List[str]) -> None:
        """Show device registers."""
        if not self._check_device_selected():
            return

        try:
            registers = self.parser.get_device_registers(self.current_device)

            table = Table(title=f"Registers - {self.current_device}")
            table.add_column("Module", style="cyan")
            table.add_column("Register", style="white")
            table.add_column("Address", style="green")
            table.add_column("Size", style="yellow")
            table.add_column("Description", style="dim")

            if registers:
                for register in registers[:20]:  # Limit display
                    table.add_row(
                        getattr(register, "module_name", "Unknown"),
                        getattr(register, "name", "N/A"),
                        f"0x{getattr(register, 'offset', 0):04X}",
                        f"{getattr(register, 'size', 0)} bits",
                        getattr(register, "description", "")[:40],
                    )
            else:
                # Default registers
                table.add_row("CORE", "STATUS", "0x03", "8bit", "Status register")
                table.add_row("CORE", "WREG", "0x00", "8bit", "Working register")
                table.add_row("PORTA", "TRISA", "0x85", "8bit", "Port A direction")

            console.print(table)

        except Exception as e:
            console.print(f"[red]Error displaying registers: {e}[/red]")

    def show_files(self, args: List[str]) -> None:
        """Show files in AtPack."""
        if not self.parser:
            console.print("[red]No AtPack loaded[/red]")
            return

        try:
            # Analyze AtPack structure
            extracted_dir = (
                self.current_atpack.parent / f"{self.current_atpack.stem}_dir_atpack"
            )

            table = Table(title=f"Files in {self.current_atpack.name}")
            table.add_column("Type", style="cyan")
            table.add_column("Count", style="white")
            table.add_column("Examples", style="dim")

            if extracted_dir.exists():
                file_types = [
                    ("ATDF", "**/*.atdf"),
                    ("PIC", "**/*.pic"),
                    ("Headers", "**/*.h"),
                    ("Linker Scripts", "**/*.ld"),
                    ("XML", "**/*.xml"),
                ]

                for file_type, pattern in file_types:
                    files = list(extracted_dir.glob(pattern))
                    examples = files[0].name if files else "None"
                    table.add_row(file_type, str(len(files)), examples)

            else:
                table.add_row("Archive", "1", self.current_atpack.name)
                table.add_row("Status", "Not extracted", "Use CLI to extract")

            console.print(table)

        except Exception as e:
            console.print(f"[red]Error analyzing files: {e}[/red]")

    def show_config(self, args: List[str]) -> None:
        """Show AtPack configuration."""
        if not self.parser:
            console.print("[red]No AtPack loaded[/red]")
            return

        panel_content = f"""[bold]AtPack File:[/bold] {self.current_atpack.name}
[bold]Device Family:[/bold] {self.parser.device_family.value}
[bold]Device Count:[/bold] {len(self.parser.get_devices())}
[bold]Selected Device:[/bold] {self.current_device or "None"}"""

        console.print(
            Panel(panel_content, title="AtPack Configuration", border_style="blue")
        )

    def show_status(self, args: List[str]) -> None:
        """Show session status."""
        status_items = []

        if self.current_atpack:
            status_items.append(
                f"[green]✅ AtPack loaded:[/green] {self.current_atpack.name}"
            )
            status_items.append(
                f"[green]✅ Family:[/green] {self.parser.device_family.value}"
            )
            status_items.append(
                f"[green]✅ Available devices:[/green] {len(self.parser.get_devices())}"
            )
        else:
            status_items.append("[red]❌ No AtPack loaded[/red]")

        if self.current_device:
            status_items.append(
                f"[green]✅ Device selected:[/green] {self.current_device}"
            )
        else:
            status_items.append("[yellow]⚠️ No device selected[/yellow]")

        status_content = "\n".join(status_items)
        console.print(
            Panel(status_content, title="Session Status", border_style="cyan")
        )

    def _check_device_selected(self) -> bool:
        """Check if a device is selected."""
        if not self.parser:
            console.print("[red]No AtPack loaded. Use 'load <file>'[/red]")
            return False

        if not self.current_device:
            console.print("[red]No device selected. Use 'select <device>'[/red]")
            return False

        return True


def interactive_mode() -> None:
    """🖥️ Launch interactive mode."""
    session = InteractiveSession()
    session.start()


if __name__ == "__main__":
    interactive_mode()
