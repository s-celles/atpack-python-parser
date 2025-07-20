#!/usr/bin/env python3
"""
Development setup and testing script for AtPack Parser.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and print status."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(
            cmd, shell=True, check=True, capture_output=True, text=True
        )
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False


def main():
    """Main setup function."""
    print("🚀 AtPack Parser Development Setup")

    # Change to the project directory
    project_dir = Path(__file__).parent
    print(f"📁 Working directory: {project_dir}")

    # Install in development mode
    if not run_command("pip install -e .", "Installing package in development mode"):
        sys.exit(1)

    # Install development dependencies
    if not run_command(
        "pip install pytest pytest-cov black ruff mypy",
        "Installing development dependencies",
    ):
        print("⚠️  Development dependencies installation failed, continuing...")

    # Run basic tests
    print("\n🧪 Running basic tests...")

    # Test CLI help
    if run_command("atpack --help", "Testing CLI help command"):
        print("✅ CLI is working!")
    else:
        print("❌ CLI test failed")

    # Test with existing AtPack files if available
    atpack_dir = project_dir.parent / "public" / "atpacks"
    if atpack_dir.exists():
        print(f"\n📦 Testing with existing AtPack files in {atpack_dir}")

        # Find AtPack files
        atpack_files = []
        for pattern in ["*.atpack", "*_atpack"]:
            atpack_files.extend(atpack_dir.glob(pattern))

        if atpack_files:
            test_file = atpack_files[0]
            print(f"🔍 Testing with: {test_file}")

            # Test file info
            run_command(
                f'atpack files info "{test_file}"',
                f"Getting file info for {test_file.name}",
            )

            # Test device list
            run_command(
                f'atpack devices list "{test_file}"',
                f"Listing devices in {test_file.name}",
            )
        else:
            print("⚠️  No AtPack files found for testing")
    else:
        print(f"⚠️  AtPack directory not found: {atpack_dir}")

    # Test with examples
    example_file = project_dir / "examples" / "example_usage.py"
    if example_file.exists() and atpack_files:
        print("\n🎯 Testing example script...")
        run_command(
            f'python "{example_file}" "{atpack_files[0]}"', "Running example script"
        )

    print("\n🎉 Setup completed!")
    print("\n📚 Usage examples:")
    print("  atpack --help")
    print("  atpack scan ../public/atpacks")
    print("  atpack devices list path/to/file.atpack")
    print("  atpack devices info ATmega16 path/to/file.atpack")


if __name__ == "__main__":
    main()
