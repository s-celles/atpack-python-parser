#!/usr/bin/env python3
"""Test script to debug the PIC parser issue."""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from atpack_parser import AtPackParser


def test_pic_parsing():
    atpack_path = os.path.join(os.path.dirname(__file__), "..", "atpacks", "Microchip.PIC16Fxxx_DFP.1.7.162.atpack")

    print(f"Testing AtPack: {atpack_path}")

    try:
        parser = AtPackParser(atpack_path)

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
    test_pic_parsing()
