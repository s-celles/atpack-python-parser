#!/usr/bin/env python3
"""
Simple usage example for AtPack Parser

This script shows the basic usage patterns for the atpack-parser library.
"""

import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from atpack_parser import AtPackParser


def main():
    """Simple example of using AtPack Parser."""

    # Example 1: Parse ATMEL AtPack
    print("Example 1: ATMEL Device")
    print("-" * 30)

    atmel_path = (
        Path(__file__).parent.parent.parent
        / "public"
        / "atpacks"
        / "Atmel.ATmega_DFP.2.2.509_dir_atpack"
    )

    if atmel_path.exists():
        parser = AtPackParser(str(atmel_path))

        # Get all devices
        devices = parser.get_devices()
        print(f"Found {len(devices)} ATMEL devices")

        # Get specific device
        device = parser.get_device("ATmega16")
        print(f"Device: {device.name}")
        print(f"Family: {device.family}")
        print(f"Architecture: {device.architecture}")
        print(f"Memory segments: {len(device.memory_segments)}")
        print(f"Modules: {len(device.modules)}")
        print()

    # Example 2: Parse PIC AtPack
    print("Example 2: PIC Device")
    print("-" * 30)

    pic_path = (
        Path(__file__).parent.parent.parent
        / "public"
        / "atpacks"
        / "Microchip.PIC16Fxxx_DFP.1.7.162_dir_atpack"
    )

    if pic_path.exists():
        parser = AtPackParser(str(pic_path))

        # Get all devices
        devices = parser.get_devices()
        print(f"Found {len(devices)} PIC devices")

        # Get specific device
        device = parser.get_device("PIC16F876A")
        print(f"Device: {device.name}")
        print(f"Family: {device.family}")
        print(f"Architecture: {device.architecture}")
        print(f"Memory segments: {len(device.memory_segments)}")
        print(f"Modules: {len(device.modules)}")
        print()

    # Example 3: Access registers
    print("Example 3: Device Registers")
    print("-" * 30)

    if atmel_path.exists():
        parser = AtPackParser(str(atmel_path))
        registers = parser.get_device_registers("ATmega16")

        print(f"ATmega16 has {len(registers)} registers")

        # Find some interesting registers
        portb_regs = [r for r in registers if r.name.startswith("PORTB")]
        if portb_regs:
            reg = portb_regs[0]
            print(f"Register: {reg.name} at offset {reg.offset:#06x}")
            if reg.bitfields:
                print(f"  Bitfields: {[bf.name for bf in reg.bitfields]}")


if __name__ == "__main__":
    main()
