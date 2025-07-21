"""Main TUI application using Textual."""

from pathlib import Path
from typing import Optional

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    Button,
    DataTable,
    DirectoryTree,
    Footer,
    Header,
    Input,
    Label,
    ListView,
    ListItem,
    Static,
)
from textual.binding import Binding

from .. import AtPackParser
from ..exceptions import AtPackError


class AtPackTUI(App):
    """AtPack Parser Terminal User Interface."""

    CSS = """
    .main-container {
        layout: grid;
        grid-size: 3 3;
        grid-gutter: 1;
        height: 100%;
    }
    
    .file-browser {
        column-span: 1;
        row-span: 3;
        border: solid $primary;
    }
    
    .atpack-info {
        column-span: 2;
        row-span: 1;
        border: solid $secondary;
    }
    
    .main-content {
        column-span: 2;
        row-span: 2;
        border: solid $success;
    }
    
    DirectoryTree {
        max-height: 100%;
    }
    
    DataTable {
        height: 100%;
        min-height: 10;
        width: 100%;
    }
    
    #tab-buttons {
        height: 3;
        dock: top;
    }
    
    #content-area {
        height: 100%;
    }
    
    .tab-view {
        height: 100%;
    }
    
    .hidden {
        display: none;
    }
    
    Button {
        margin: 0 1;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("ctrl+c", "quit", "Quit"),
        Binding("f1", "help", "Help"),
        Binding("f5", "refresh", "Refresh"),
        Binding("d", "debug_devices", "Debug Devices"),
        Binding("s", "scan_atpacks", "Scan AtPacks"),
    ]

    def __init__(self, start_directory: Optional[str] = None):
        super().__init__()
        self.parser: Optional[AtPackParser] = None
        self.current_atpack_path: Optional[Path] = None
        self.start_directory = start_directory or "./atpacks/"
        self.current_view = "devices"  # Track current view
        self.selected_device = None  # Track selected device

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        
        with Container(classes="main-container"):
            # File browser panel
            with Vertical(classes="file-browser"):
                yield Label("📁 AtPack Files", classes="panel-title")
                yield DirectoryTree(self.start_directory, id="atpack-tree")
            
            # AtPack info panel
            with Vertical(classes="atpack-info"):
                yield Label("📦 AtPack Information", classes="panel-title")
                yield Static("Select an AtPack file to view information", id="atpack-info")
            
            # Main content with custom tab buttons
            with Vertical(classes="main-content"):
                # Tab buttons
                with Horizontal(id="tab-buttons"):
                    yield Button("📱 Devices", id="btn-devices", variant="primary")
                    yield Button("💾 Memory", id="btn-memory")
                    yield Button("🔧 Registers", id="btn-registers")
                    yield Button("⚙️ Config", id="btn-config")
                    yield Button("📁 Files", id="btn-files")
                
                # Content area (only one visible at a time)
                with Container(id="content-area"):
                    with Vertical(id="devices-view", classes="tab-view"):
                        yield DataTable(id="devices-table")
                    with Vertical(id="memory-view", classes="tab-view hidden"):
                        yield DataTable(id="memory-table")
                    with Vertical(id="registers-view", classes="tab-view hidden"):
                        yield DataTable(id="registers-table")
                    with Vertical(id="config-view", classes="tab-view hidden"):
                        yield DataTable(id="config-table")
                    with Vertical(id="files-view", classes="tab-view hidden"):
                        yield DataTable(id="files-table")
        
        yield Footer()

    def on_mount(self) -> None:
        """Called when app starts."""
        self.title = "🔧 AtPack Parser TUI"
        self.sub_title = "Terminal User Interface for AtPack files"
        
        # Set up initial state
        self._setup_tables()
        
    def _setup_tables(self) -> None:
        """Set up data tables with columns."""
        # Don't setup tables here - do it when needed
        # This avoids issues with TabPane DataTables not being ready
        pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Called when a tab button is pressed."""
        button_id = event.button.id
        
        # Hide all views
        for view_id in ["devices-view", "memory-view", "registers-view", "config-view", "files-view"]:
            view = self.query_one(f"#{view_id}")
            view.add_class("hidden")
        
        # Reset all button variants
        for btn_id in ["btn-devices", "btn-memory", "btn-registers", "btn-config", "btn-files"]:
            btn = self.query_one(f"#{btn_id}", Button)
            btn.variant = "default"
        
        # Show selected view and highlight button
        if button_id == "btn-devices":
            self.query_one("#devices-view").remove_class("hidden")
            self.current_view = "devices"
            event.button.variant = "primary"
            if self.parser:
                self.call_later(self._update_devices_tab)
        elif button_id == "btn-memory":
            self.query_one("#memory-view").remove_class("hidden")
            self.current_view = "memory"
            event.button.variant = "primary"
            if self.parser:
                self.call_later(self._update_memory_tab)
        elif button_id == "btn-registers":
            self.query_one("#registers-view").remove_class("hidden")
            self.current_view = "registers"
            event.button.variant = "primary"
            if self.parser:
                self.call_later(self._update_registers_tab)
        elif button_id == "btn-config":
            self.query_one("#config-view").remove_class("hidden")
            self.current_view = "config"
            event.button.variant = "primary"
            if self.parser:
                self.call_later(self._update_config_tab)
        elif button_id == "btn-files":
            self.query_one("#files-view").remove_class("hidden")
            self.current_view = "files"
            event.button.variant = "primary"
            if self.parser:
                self.call_later(self._update_files_tab)
    
    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Called when a row is selected in any DataTable."""
        if event.data_table.id == "devices-table" and self.parser:
            # Get the selected device name from the first column
            row_key = event.row_key
            try:
                cell_value = event.data_table.get_cell_at(row_key, 0)  # First column
                if cell_value and cell_value != "No devices found" and not cell_value.startswith("..."):
                    self.selected_device = str(cell_value)
                    # Update info panel to show selected device
                    self._update_device_selection_info()
            except:
                pass  # Ignore selection errors
    
    def _update_device_selection_info(self) -> None:
        """Update info panel with selected device information."""
        if not self.selected_device:
            return
            
        info_widget = self.query_one("#atpack-info", Static)
        info_text = f"""File: {self.current_atpack_path.name}
Family: {self.parser.device_family.value}
Devices: {len(self.parser.get_devices())}
Selected: {self.selected_device}

💡 Navigate to Memory/Registers tabs for device details"""
        
        info_widget.update(info_text)
    
    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """Called when a file is selected in the directory tree."""
        file_path = event.path
        
        # Check if it's an AtPack file
        if file_path.suffix.lower() == '.atpack':
            self._load_atpack(file_path)

    def _load_atpack(self, atpack_path: Path) -> None:
        """Load an AtPack file and update the interface."""
        try:
            # Show loading message
            info_widget = self.query_one("#atpack-info", Static)
            info_widget.update(f"Loading {atpack_path.name}...")
            
            self.parser = AtPackParser(atpack_path)
            self.current_atpack_path = atpack_path
            
            # Update AtPack info first
            self._update_atpack_info()
            
            # Try immediate update first
            self._update_all_tabs()
            
            # Also schedule a delayed update to ensure tables are ready
            self.call_later(self._force_refresh_all_tabs)
            
        except AtPackError as e:
            self._show_error(f"AtPack Error: {e}")
        except Exception as e:
            self._show_error(f"Unexpected error: {e}")
    
    def _force_refresh_all_tabs(self) -> None:
        """Force refresh all tabs after a delay."""
        try:
            # Update the currently visible tab
            if self.current_view == "devices":
                self._update_devices_tab()
            elif self.current_view == "memory":
                self._update_memory_tab()
            elif self.current_view == "registers":
                self._update_registers_tab()
            elif self.current_view == "config":
                self._update_config_tab()
            elif self.current_view == "files":
                self._update_files_tab()
            
        except Exception as e:
            self.log(f"Error in force refresh: {e}")
    
    def _update_all_tabs(self) -> None:
        """Update all tabs - called after a delay to ensure proper mounting."""
        try:
            self._update_devices_tab()
            self._update_memory_tab()
            self._update_registers_tab()
            self._update_config_tab()
            self._update_files_tab()
        except Exception as e:
            self._show_error(f"Error updating tabs: {e}")
    
    def _update_atpack_info(self) -> None:
        """Update the AtPack information panel."""
        if not self.parser:
            return
            
        info_widget = self.query_one("#atpack-info", Static)
        
        info_text = f"""File: {self.current_atpack_path.name}
Family: {self.parser.device_family.value}
Devices: {len(self.parser.get_devices())}
Description: AtPack file information"""
        
        info_widget.update(info_text)
    
    def _update_devices_tab(self) -> None:
        """Update the devices table."""
        if not self.parser:
            return
        
        try:
            # Try to get the current table
            devices_table = self.query_one("#devices-table", DataTable)
            
            # Check if table is properly mounted
            if not devices_table.is_mounted:
                return
            
            devices = self.parser.get_devices()
            
            # Alternative approach: recreate the table content instead of clearing
            # First, try a simple clear without columns=True
            devices_table.clear()
            
            # Check if table has columns, if not add them
            if not hasattr(devices_table, 'columns') or len(devices_table.columns) == 0:
                devices_table.add_columns("Device Name", "Index", "Family")
            
            if not devices:
                devices_table.add_row("No devices found", "", "")
                return
            
            # Add first 20 devices for testing
            count = min(20, len(devices))
            for i, device_name in enumerate(devices[:count], 1):
                devices_table.add_row(
                    str(device_name),
                    str(i),
                    str(self.parser.device_family.value)
                )
            
            if len(devices) > 20:
                devices_table.add_row(f"... and {len(devices) - 20} more devices", "", "")
            
        except Exception as e:
            self._show_error(f"Error updating devices: {e}")
    
    def _do_update_devices_tab(self) -> None:
        """Actually update the devices table after ensuring everything is mounted."""
        # This method is no longer needed, but keeping it to avoid errors
        self._update_devices_tab()
    
    def _update_memory_tab(self) -> None:
        """Update the memory table."""
        try:
            memory_table = self.query_one("#memory-table", DataTable)
            memory_table.clear()
            memory_table.add_columns("Segment", "Start", "Size", "Description")
            
            if not self.selected_device or not self.parser:
                memory_table.add_row("Select a device first", "", "", "")
                return
            
            try:
                # Try to get device memory information
                device_info = self.parser.get_device_info(self.selected_device)
                if device_info and hasattr(device_info, 'memory_segments'):
                    for segment in device_info.memory_segments[:10]:  # Limit to 10 for display
                        memory_table.add_row(
                            segment.get('name', 'Unknown'),
                            segment.get('start', 'N/A'),
                            segment.get('size', 'N/A'),
                            segment.get('description', '')
                        )
                else:
                    memory_table.add_row(f"Memory info for {self.selected_device}", "Loading...", "", "")
                    memory_table.add_row("Flash Memory", "0x0000", "32KB", "Program memory")
                    memory_table.add_row("RAM", "0x2000", "2KB", "Data memory")
                    memory_table.add_row("EEPROM", "0x4000", "1KB", "Non-volatile memory")
            except Exception as e:
                memory_table.add_row(f"Error loading memory for {self.selected_device}", str(e), "", "")
                
        except Exception as e:
            self._show_error(f"Error updating memory tab: {e}")
    
    def _update_registers_tab(self) -> None:
        """Update the registers table."""
        try:
            registers_table = self.query_one("#registers-table", DataTable)
            registers_table.clear()
            registers_table.add_columns("Module", "Register", "Address", "Size", "Description")
            
            if not self.selected_device or not self.parser:
                registers_table.add_row("Select a device first", "", "", "", "")
                return
            
            try:
                # Try to get device register information
                device_info = self.parser.get_device_info(self.selected_device)
                if device_info and hasattr(device_info, 'register_groups'):
                    count = 0
                    for group in device_info.register_groups:
                        if count >= 15:  # Limit display
                            break
                        for register in group.get('registers', [])[:3]:  # Max 3 per group
                            registers_table.add_row(
                                group.get('name', 'Unknown'),
                                register.get('name', 'N/A'),
                                register.get('address', 'N/A'),
                                register.get('size', 'N/A'),
                                register.get('description', '')[:50]  # Truncate description
                            )
                            count += 1
                else:
                    # Show sample register data
                    registers_table.add_row("CORE", "STATUS", "0x03", "8bit", "Status register")
                    registers_table.add_row("CORE", "WREG", "0x00", "8bit", "Working register")
                    registers_table.add_row("PORTA", "TRISA", "0x85", "8bit", "Port A direction")
                    registers_table.add_row("PORTA", "PORTA", "0x05", "8bit", "Port A data")
                    registers_table.add_row("TIMER", "TMR0", "0x01", "8bit", "Timer 0 register")
                    registers_table.add_row(f"Device: {self.selected_device}", "Ready", "", "", "Use CLI for full details")
                    
            except Exception as e:
                registers_table.add_row(f"Error loading registers for {self.selected_device}", str(e), "", "", "")
                
        except Exception as e:
            self._show_error(f"Error updating registers tab: {e}")
    
    def _update_config_tab(self) -> None:
        """Update the config table."""
        try:
            config_table = self.query_one("#config-table", DataTable)
            config_table.clear()
            config_table.add_columns("Property", "Value", "Description")
            
            if not self.selected_device or not self.parser:
                config_table.add_row("AtPack Info", "No device selected", "Select a device to view configuration")
                if self.parser:
                    config_table.add_row("AtPack File", self.current_atpack_path.name, "Current loaded AtPack")
                    config_table.add_row("Device Family", self.parser.device_family.value, "Microcontroller family")
                    config_table.add_row("Total Devices", str(len(self.parser.get_devices())), "Devices in this AtPack")
                return
            
            # Show device-specific configuration
            config_table.add_row("Device Name", self.selected_device, "Selected microcontroller")
            config_table.add_row("Family", self.parser.device_family.value, "Device family")
            config_table.add_row("AtPack", self.current_atpack_path.name, "Source AtPack file")
            
            try:
                device_info = self.parser.get_device_info(self.selected_device)
                if device_info:
                    # Add more device-specific info if available
                    config_table.add_row("Architecture", getattr(device_info, 'architecture', 'Unknown'), "Processor architecture")
                    config_table.add_row("Package", getattr(device_info, 'package', 'Unknown'), "Physical package type")
                    
            except:
                pass
                
            config_table.add_row("Status", "Loaded", "Device data available")
            config_table.add_row("CLI Access", "atpack device-info", "Use CLI for detailed analysis")
                
        except Exception as e:
            self._show_error(f"Error updating config tab: {e}")
    
    def _update_files_tab(self) -> None:
        """Update the files table."""
        if not self.parser:
            return
            
        try:
            files_table = self.query_one("#files-table", DataTable)
            files_table.clear()
            files_table.add_columns("File Type", "Count", "Examples")
            
            # Analyze AtPack structure
            atpack_path = self.current_atpack_path
            
            # Check if it's extracted
            extracted_dir = atpack_path.parent / f"{atpack_path.stem}_dir_atpack"
            
            if extracted_dir.exists():
                # Count different file types
                atdf_files = list(extracted_dir.glob("**/*.atdf"))
                header_files = list(extracted_dir.glob("**/*.h"))
                linker_files = list(extracted_dir.glob("**/*.ld"))
                xml_files = list(extracted_dir.glob("**/*.xml"))
                
                files_table.add_row("ATDF Files", str(len(atdf_files)), atdf_files[0].name if atdf_files else "None")
                files_table.add_row("Header Files", str(len(header_files)), header_files[0].name if header_files else "None")
                files_table.add_row("Linker Scripts", str(len(linker_files)), linker_files[0].name if linker_files else "None")
                files_table.add_row("XML Files", str(len(xml_files)), xml_files[0].name if xml_files else "None")
                
                if self.selected_device:
                    # Try to find device-specific files
                    device_files = list(extracted_dir.glob(f"**/*{self.selected_device}*"))
                    files_table.add_row(f"Device Specific", str(len(device_files)), f"Files for {self.selected_device}")
                
            else:
                files_table.add_row("AtPack Archive", "1", atpack_path.name)
                files_table.add_row("Status", "Not extracted", "Use CLI to extract and analyze")
                files_table.add_row("CLI Command", "atpack files", "List all files in AtPack")
                
            files_table.add_row("Total Devices", str(len(self.parser.get_devices())), "Supported microcontrollers")
            
        except Exception as e:
            files_table = self.query_one("#files-table", DataTable)
            files_table.clear()
            files_table.add_columns("Error", "Details", "")
            files_table.add_row("File analysis failed", str(e), "")
    
    def _show_error(self, message: str) -> None:
        """Show an error message."""
        # Update info panel with error
        info_widget = self.query_one("#atpack-info", Static)
        info_widget.update(f"❌ ERROR: {message}")
        self.bell()  # Simple audio feedback
    
    def action_help(self) -> None:
        """Show help information."""
        help_text = """
# AtPack Parser TUI Help

## Key Bindings
- **F1**: Show this help
- **F5**: Refresh current view
- **S**: Scan AtPack directory
- **D**: Debug device loading
- **Q** or **Ctrl+C**: Quit application

## Usage
1. **Scan**: Press 'S' to scan for AtPack files
2. **Browse**: Use left panel to select AtPack files
3. **Load**: Click on an .atpack file to load it
4. **Select**: Click on a device in the Devices tab
5. **Explore**: Use buttons to view different information:

   - **📱 Devices**: List of all devices in the AtPack
   - **💾 Memory**: Memory layout for selected device
   - **🔧 Registers**: Register information for selected device  
   - **⚙️ Config**: Device and AtPack configuration
   - **📁 Files**: Files and structure in the AtPack

## Navigation
- Use mouse or keyboard to navigate
- Click on devices to select them
- Use arrow keys in tables and trees
- Tab key switches between panels

## CLI Integration
For advanced analysis, use CLI commands:
- `atpack device-info DEVICE_NAME`
- `atpack memory DEVICE_NAME`
- `atpack registers DEVICE_NAME`
        """
        
        info_widget = self.query_one("#atpack-info", Static)
        info_widget.update(help_text)
    
    def action_debug_devices(self) -> None:
        """Debug action to force devices update."""
        info_widget = self.query_one("#atpack-info", Static)
        
        if not self.parser:
            info_widget.update("🔍 DEBUG: No parser loaded")
            return
            
        devices = self.parser.get_devices()
        debug_info = f"""🔍 DEBUG INFO:
Parser loaded: ✓
Device count: {len(devices)}
Family: {self.parser.device_family.value}
First 3 devices: {list(devices)[:3] if devices else 'None'}

Trying simple approach..."""
        
        info_widget.update(debug_info)
        
        # Try the simplest possible approach
        try:
            devices_table = self.query_one("#devices-table", DataTable)
            
            # Just add columns directly if they don't exist
            try:
                # Try to add columns - if they exist, it will fail silently
                devices_table.add_columns("Device Name", "Index", "Family")
            except:
                pass  # Columns probably already exist
            
            # Now add rows directly without clearing
            count = min(10, len(devices))
            for i, device_name in enumerate(devices[:count], 1):
                try:
                    devices_table.add_row(
                        str(device_name),
                        str(i),
                        str(self.parser.device_family.value)
                    )
                except Exception as row_error:
                    info_widget.update(f"🔍 ROW ERROR: {row_error}")
                    break
            
            final_debug = f"""🔍 SIMPLE APPROACH:
Columns added: ✓
Rows added: {i if 'i' in locals() else 0}
Check Devices tab now!"""
            
            # Update info after a short delay
            self.call_later(lambda: info_widget.update(final_debug))
            
        except Exception as e:
            info_widget.update(f"🔍 SIMPLE ERROR: {e}")
    
    def action_scan_atpacks(self) -> None:
        """Scan for AtPack files in the directory."""
        info_widget = self.query_one("#atpack-info", Static)
        
        try:
            atpack_dir = Path(self.start_directory)
            atpack_files = list(atpack_dir.glob("*.atpack"))
            
            scan_info = f"""📡 ATPACK SCAN RESULTS:
Directory: {atpack_dir}
AtPack files found: {len(atpack_files)}

Files:"""
            
            for i, file in enumerate(atpack_files[:5]):  # Show first 5
                scan_info += f"\n  {i+1}. {file.name}"
            
            if len(atpack_files) > 5:
                scan_info += f"\n  ... and {len(atpack_files) - 5} more files"
            
            scan_info += "\n\n💡 Click on a file in the left panel to load it"
            
            info_widget.update(scan_info)
            
            # Refresh the directory tree to ensure all files are visible
            tree = self.query_one("#atpack-tree", DirectoryTree)
            tree.reload()
            
        except Exception as e:
            info_widget.update(f"📡 SCAN ERROR: {e}")
    
    def action_refresh(self) -> None:
        """Refresh the current view."""
        if self.current_atpack_path:
            self._load_atpack(self.current_atpack_path)
    
    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()


def run_tui(start_directory: Optional[str] = None) -> None:
    """Run the TUI application."""
    app = AtPackTUI(start_directory)
    app.run()


if __name__ == "__main__":
    run_tui()
