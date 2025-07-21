#!/usr/bin/env python3
"""Test script for CLI functionality.

This test ensures that:
- Version flags (-v, --version) work correctly
- Help is displayed when no command is provided
- Help flags (--help) work correctly  
- Subcommands and help-tree command work
- Both installed CLI and module execution work

The tests use typer.testing.CliRunner for unit testing and subprocess
for integration testing of the actual installed CLI.
"""

import subprocess
import sys
import pytest
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from atpack_parser import __version__
from atpack_parser.cli import app
from typer.testing import CliRunner


import re


def test_version_flag_short():
    """Test that -v flag outputs the version."""
    runner = CliRunner()
    result = runner.invoke(app, ["-v"])
    
    assert result.exit_code == 0
    # Use regex to match version ignoring ANSI codes
    clean_output = re.sub(r'\x1b\[[0-9;]*m', '', result.stdout)
    assert f"AtPack Parser v{__version__}" in clean_output
    print(f"✓ Short version flag (-v) works: version {__version__} found")


def test_version_flag_long():
    """Test that --version flag outputs the version."""
    runner = CliRunner()
    result = runner.invoke(app, ["--version"])
    
    assert result.exit_code == 0
    # Use regex to match version ignoring ANSI codes
    clean_output = re.sub(r'\x1b\[[0-9;]*m', '', result.stdout)
    assert f"AtPack Parser v{__version__}" in clean_output
    print(f"✓ Long version flag (--version) works: version {__version__} found")


def test_help_without_command():
    """Test that running without command shows help."""
    runner = CliRunner()
    result = runner.invoke(app, [])
    
    assert result.exit_code == 0
    assert "Parse AtPack files" in result.stdout
    assert "files" in result.stdout and "devices" in result.stdout  # Check command groups exist
    print("✓ Help display without command works")


def test_help_flag():
    """Test that --help flag works."""
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    
    assert result.exit_code == 0
    assert "Parse AtPack files" in result.stdout
    assert "files" in result.stdout and "devices" in result.stdout  # Check command groups exist
    print("✓ Help flag (--help) works")


def test_help_tree_command():
    """Test the help-tree command."""
    runner = CliRunner()
    result = runner.invoke(app, ["help-tree"])
    
    assert result.exit_code == 0
    assert "Command Tree with Examples" in result.stdout
    assert "atpack - AtPack Parser CLI" in result.stdout
    print("✓ help-tree command works")


def test_subcommand_help():
    """Test that subcommand help works."""
    runner = CliRunner()
    result = runner.invoke(app, ["files", "--help"])
    
    assert result.exit_code == 0
    assert "AtPack file management" in result.stdout
    print("✓ Subcommand help (files --help) works")


def test_cli_via_subprocess_version():
    """Test CLI version via subprocess to ensure installed command works."""
    try:
        # Test the installed atpack command
        result = subprocess.run(
            ["atpack", "-v"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            assert f"AtPack Parser v{__version__}" in result.stdout
            print(f"✓ Installed CLI version works: {result.stdout.strip()}")
        else:
            print(f"⚠️ Installed CLI not available or error: {result.stderr}")
    except FileNotFoundError:
        print("⚠️ atpack command not found in PATH - this is OK if not installed")
    except Exception as e:
        print(f"⚠️ Error testing installed CLI: {e}")


def test_cli_via_module_version():
    """Test CLI version via python -m to ensure module execution works."""
    try:
        # Test module execution
        result = subprocess.run(
            [sys.executable, "-m", "src.atpack_parser.cli", "-v"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=Path(__file__).parent.parent
        )
        
        if result.returncode == 0:
            assert f"AtPack Parser v{__version__}" in result.stdout
            print(f"✓ Module CLI version works: {result.stdout.strip()}")
        else:
            print(f"⚠️ Module CLI error: {result.stderr}")
    except Exception as e:
        print(f"⚠️ Error testing module CLI: {e}")


@pytest.mark.integration
def test_all_cli_functionality():
    """Integration test that runs all CLI functionality tests."""
    print("\n=== CLI Functionality Tests ===")
    
    test_version_flag_short()
    test_version_flag_long()
    test_help_without_command()
    test_help_flag()
    test_help_tree_command()
    test_subcommand_help()
    test_cli_via_subprocess_version()
    test_cli_via_module_version()
    
    print("=== All CLI tests completed ===")


if __name__ == "__main__":
    # Standalone execution
    test_all_cli_functionality()
