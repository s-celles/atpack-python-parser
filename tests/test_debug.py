#!/usr/bin/env python3
"""Test script to debug the PIC parser issue."""

import sys
import pytest
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from atpack_parser import AtPackParser

# Import helpers conditionally for pytest vs standalone execution
try:
    from .conftest import skip_if_atpack_missing, PIC_ATPACK_FILE
except ImportError:
    # Standalone execution - define helpers locally
    def skip_if_atpack_missing(atpack_file: Path, vendor: str) -> None:
        if not atpack_file.exists():
            print(f"⚠️ {vendor} AtPack file not found: {atpack_file}")
            print("See atpacks/README.md for download instructions.")
            exit(1)
    
    PIC_ATPACK_FILE = Path(__file__).parent.parent / "atpacks" / "Microchip.PIC16Fxxx_DFP.1.7.162.atpack"


@pytest.mark.integration
@pytest.mark.atpack_required
def test_pic_parsing(pic_atpack_file: Path = None):
    """Debug test for PIC parsing functionality."""
    # Use provided fixture or fallback to direct path for standalone execution
    atpack_file = pic_atpack_file if pic_atpack_file is not None else PIC_ATPACK_FILE
    skip_if_atpack_missing(atpack_file, "PIC")
    
    print(f"Testing AtPack: {atpack_file}")

    try:
        parser = AtPackParser(atpack_file)

        print(f"Device family detected: {parser.device_family}")
        print(f"Metadata: {parser.metadata.name}")

        # Get all devices
        devices = parser.get_devices()
        print(f"Found {len(devices)} devices")

        # Check if PIC16F876A is in the list
        if "PIC16F876A" in devices:
            print("✓ PIC16F876A found in device list")
        else:
            print("✗ PIC16F876A NOT found in device list")
            print("Available devices:")
            for device in devices[:10]:  # Show first 10
                print(f"  - {device}")
            if len(devices) > 10:
                print(f"  ... and {len(devices) - 10} more")

        # Try to get the specific device
        device_name = "PIC16F876A"
        print(f"\nTrying to parse device: {device_name}")

        try:
            device = parser.get_device(device_name)
            print(f"✓ Successfully parsed device: {device.name}")
            print(f"  Family: {device.family}")
            print(f"  Architecture: {device.architecture}")
            print(f"  Memory segments: {len(device.memory_segments)}")
            print(f"  Modules: {len(device.modules)}")
        except Exception as e:
            print(f"✗ Error parsing device: {e}")

            # Debug: list all PIC files
            print("\nDebug: Listing all PIC files:")
            pic_files = parser.extractor.find_pic_files()
            for pic_file in pic_files[:10]:
                file_name = Path(pic_file).stem
                print(f"  - {pic_file} -> stem: {file_name}")
            if len(pic_files) > 10:
                print(f"  ... and {len(pic_files) - 10} more")

    except Exception as e:
        print(f"Error initializing parser: {e}")


if __name__ == "__main__":
    # Standalone execution
    test_pic_parsing()
