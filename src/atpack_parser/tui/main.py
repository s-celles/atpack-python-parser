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
    Markdown,
    Static,
    TabbedContent,
    TabPane,
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
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("ctrl+c", "quit", "Quit"),
        Binding("f1", "help", "Help"),
        Binding("f5", "refresh", "Refresh"),
    ]

    def __init__(self):
        super().__init__()
        self.parser: Optional[AtPackParser] = None
        self.current_atpack_path: Optional[Path] = None

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        
        with Container(classes="main-container"):
            # File browser panel
            with Vertical(classes="file-browser"):
                yield Label("📁 AtPack Files", classes="panel-title")
                yield DirectoryTree("./atpacks/", id="atpack-tree")
            
            # AtPack info panel
            with Vertical(classes="atpack-info"):
                yield Label("📦 AtPack Information", classes="panel-title")
                yield Static("Select an AtPack file to view information", id="atpack-info")
            
            # Main content with tabs
            with Vertical(classes="main-content"):
                with TabbedContent(initial="devices"):
                    with TabPane("Devices", id="devices"):
                        yield DataTable(id="devices-table")
                    with TabPane("Memory", id="memory"):
                        yield DataTable(id="memory-table")
                    with TabPane("Registers", id="registers"):
                        yield DataTable(id="registers-table")
                    with TabPane("Config", id="config"):
                        yield DataTable(id="config-table")
                    with TabPane("Files", id="files"):
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
        # Devices table
        devices_table = self.query_one("#devices-table", DataTable)
        devices_table.add_columns("Device Name", "Index", "Family")
        
        # Memory table
        memory_table = self.query_one("#memory-table", DataTable)
        memory_table.add_columns("Segment", "Start", "End", "Size", "Type")
        
        # Registers table
        registers_table = self.query_one("#registers-table", DataTable)
        registers_table.add_columns("Module", "Register", "Offset", "Size", "Access")
        
        # Config table
        config_table = self.query_one("#config-table", DataTable)
        config_table.add_columns("Type", "Name", "Description")
        
        # Files table
        files_table = self.query_one("#files-table", DataTable)
        files_table.add_columns("File Path", "Size")

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """Called when a file is selected in the directory tree."""
        file_path = event.path
        
        # Check if it's an AtPack file
        if file_path.suffix.lower() == '.atpack':
            self._load_atpack(file_path)

    def _load_atpack(self, atpack_path: Path) -> None:
        """Load an AtPack file and update the interface."""
        try:
            self.parser = AtPackParser(atpack_path)
            self.current_atpack_path = atpack_path
            
            # Update AtPack info
            self._update_atpack_info()
            
            # Update all tabs
            self._update_devices_tab()
            self._update_memory_tab()
            self._update_registers_tab()
            self._update_config_tab()
            self._update_files_tab()
            
        except AtPackError as e:
            self._show_error(f"Error loading AtPack: {e}")
    
    def _update_atpack_info(self) -> None:
        """Update the AtPack information panel."""
        if not self.parser:
            return
            
        info_widget = self.query_one("#atpack-info", Static)
        
        info_text = f"""
**File**: {self.current_atpack_path.name}
**Family**: {self.parser.device_family.value}
**Devices**: {len(self.parser.get_all_devices())}
**Description**: AtPack file information
        """
        
        info_widget.update(Markdown(info_text))
    
    def _update_devices_tab(self) -> None:
        """Update the devices table."""
        if not self.parser:
            return
            
        devices_table = self.query_one("#devices-table", DataTable)
        devices_table.clear()
        
        try:
            devices = self.parser.get_all_devices()
            for i, device_name in enumerate(devices, 1):
                devices_table.add_row(
                    device_name,
                    str(i),
                    self.parser.device_family.value
                )
        except Exception as e:
            self._show_error(f"Error loading devices: {e}")
    
    def _update_memory_tab(self) -> None:
        """Update the memory table."""
        # This would require selecting a specific device first
        memory_table = self.query_one("#memory-table", DataTable)
        memory_table.clear()
        memory_table.add_row("Select a device first", "", "", "", "")
    
    def _update_registers_tab(self) -> None:
        """Update the registers table."""
        # This would require selecting a specific device first
        registers_table = self.query_one("#registers-table", DataTable)
        registers_table.clear()
        registers_table.add_row("Select a device first", "", "", "", "")
    
    def _update_config_tab(self) -> None:
        """Update the config table."""
        # This would require selecting a specific device first
        config_table = self.query_one("#config-table", DataTable)
        config_table.clear()
        config_table.add_row("Select a device first", "", "")
    
    def _update_files_tab(self) -> None:
        """Update the files table."""
        if not self.parser:
            return
            
        files_table = self.query_one("#files-table", DataTable)
        files_table.clear()
        
        try:
            # This would need a method to list files in the AtPack
            files_table.add_row("Feature coming soon...", "")
        except Exception as e:
            self._show_error(f"Error loading files: {e}")
    
    def _show_error(self, message: str) -> None:
        """Show an error message."""
        # You could implement a notification system or modal dialog
        self.bell()  # Simple audio feedback for now
    
    def action_help(self) -> None:
        """Show help information."""
        help_text = """
# AtPack Parser TUI Help

## Key Bindings
- **F1**: Show this help
- **F5**: Refresh current view
- **Q** or **Ctrl+C**: Quit application

## Usage
1. Browse AtPack files in the left panel
2. Click on an .atpack file to load it
3. Use the tabs to view different information:
   - **Devices**: List of all devices in the AtPack
   - **Memory**: Memory layout (select device first)
   - **Registers**: Register information (select device first)
   - **Config**: Configuration data (select device first)
   - **Files**: Files in the AtPack archive

## Navigation
- Use mouse or keyboard to navigate
- Use Tab to switch between panels
- Use arrow keys in tables and trees
        """
        
        # You would implement a proper help modal here
        pass
    
    def action_refresh(self) -> None:
        """Refresh the current view."""
        if self.current_atpack_path:
            self._load_atpack(self.current_atpack_path)
    
    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()


def run_tui() -> None:
    """Run the TUI application."""
    app = AtPackTUI()
    app.run()


if __name__ == "__main__":
    run_tui()
