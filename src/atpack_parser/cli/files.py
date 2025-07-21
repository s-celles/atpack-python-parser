"""Files command group for AtPack CLI."""

import json
import zipfile
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.panel import Panel
from rich.table import Table

from .. import AtPackParser
from ..exceptions import AtPackError
from .common import AtPackPath, console

# Create files sub-command app
files_app = typer.Typer(name="files", help="📁 AtPack file management")


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


@files_app.command("extract")
def extract_atpack(
    atpack_path: AtPackPath,
    outdir: Annotated[
        Optional[Path], 
        typer.Option("--outdir", "-o", help="Output directory for extracted files")
    ] = None,
    overwrite: Annotated[
        bool, 
        typer.Option("--overwrite", help="Overwrite existing directory")
    ] = False,
):
    """📦 Extract an AtPack file to a directory."""
    try:
        # Validate input is a zip file
        if not atpack_path.is_file():
            console.print(f"[red]Error: {atpack_path} is not a file[/red]")
            raise typer.Exit(1)
            
        if not zipfile.is_zipfile(atpack_path):
            console.print(f"[red]Error: {atpack_path} is not a valid zip file[/red]")
            raise typer.Exit(1)

        # Determine output directory
        if outdir is None:
            # Infer from filename: remove .atpack extension and add _dir_atpack
            stem = atpack_path.stem
            if stem.endswith('.atpack'):
                stem = stem[:-7]  # Remove .atpack
            outdir = atpack_path.parent / f"{stem}_dir_atpack"
        
        # Check if output directory already exists
        if outdir.exists():
            if not overwrite:
                console.print(f"[red]Error: Output directory {outdir} already exists. Use --overwrite to replace it.[/red]")
                raise typer.Exit(1)
            else:
                console.print(f"[yellow]Warning: Overwriting existing directory {outdir}[/yellow]")
        
        # Create output directory
        outdir.mkdir(parents=True, exist_ok=True)
        
        # Extract the zip file
        with zipfile.ZipFile(atpack_path, 'r') as zf:
            console.print(f"[blue]Extracting {atpack_path} to {outdir}[/blue]")
            
            # Get list of files to extract
            file_list = zf.namelist()
            
            with console.status(f"Extracting {len(file_list)} files..."):
                zf.extractall(outdir)
            
            console.print(f"[green]✓ Successfully extracted {len(file_list)} files to {outdir}[/green]")
            
            # Show summary
            total_size = sum(info.file_size for info in zf.infolist() if not info.is_dir())
            console.print(f"[dim]Total size: {total_size:,} bytes[/dim]")

    except (OSError, zipfile.BadZipFile) as e:
        console.print(f"[red]Error extracting file: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        raise typer.Exit(1)
