#!/usr/bin/env python3
"""
Example usage of AtPack Parser library.

This example demonstrates how to use the AtPack parser to extract
information from ATMEL and Microchip AtPack files.
"""

import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from atpack_parser import AtPackParser, DeviceFamily


def main():
    """Main example function."""
    if len(sys.argv) < 2:
        print("Usage: python example.py <atpack_file_or_directory>")
        print(
            "Example: python example.py ../public/atpacks/Atmel.ATmega_DFP.2.2.509.atpack"
        )
        sys.exit(1)

    atpack_path = Path(sys.argv[1])

    try:
        # Initialize parser
        print(f"🔧 Parsing AtPack: {atpack_path}")
        parser = AtPackParser(atpack_path)

        # Get metadata
        metadata = parser.metadata
        print("\n📦 AtPack Information:")
        print(f"  Name: {metadata.name}")
        print(f"  Vendor: {metadata.vendor}")
        print(f"  Version: {metadata.version}")
        print(f"  Device Family: {parser.device_family.value}")

        # Get device list
        devices = parser.get_devices()
        print(f"\n📋 Found {len(devices)} devices:")

        # Show first few devices
        for i, device_name in enumerate(devices[:5]):
            print(f"  {i + 1:2}. {device_name}")

        if len(devices) > 5:
            print(f"     ... and {len(devices) - 5} more")

        if not devices:
            print("  No devices found!")
            return

        # Parse first device in detail
        device_name = devices[0]
        print(f"\n🔌 Analyzing device: {device_name}")

        try:
            device = parser.get_device(device_name)

            print(f"  Family: {device.family.value}")
            print(f"  Architecture: {device.architecture or 'N/A'}")
            print(f"  Memory segments: {len(device.memory_segments)}")
            print(f"  Modules: {len(device.modules)}")
            print(f"  Interrupts: {len(device.interrupts)}")

            # Show memory layout
            if device.memory_segments:
                print("\n💾 Memory Layout:")
                for seg in sorted(device.memory_segments, key=lambda x: x.start):
                    print(
                        f"  {seg.name:12} 0x{seg.start:04X} - 0x{seg.start + seg.size - 1:04X} ({seg.size:,} bytes)"
                    )

            # Show modules overview
            if device.modules:
                print("\n🔧 Modules Overview:")
                for module in device.modules[:10]:  # Show first 10 modules
                    reg_count = sum(len(rg.registers) for rg in module.register_groups)
                    print(
                        f"  {module.name:15} {len(module.register_groups)} register groups, {reg_count} registers"
                    )

                if len(device.modules) > 10:
                    print(f"  ... and {len(device.modules) - 10} more modules")

            # Show some registers
            registers = parser.get_device_registers(device_name)
            if registers:
                print(
                    f"\n📋 Registers Overview (showing first 10 of {len(registers)}):"
                )
                for reg in registers[:10]:
                    print(
                        f"  {reg.name:15} @ 0x{reg.offset:04X} ({reg.size} bytes, {len(reg.bitfields)} bitfields)"
                    )

            # Show configuration info for PIC devices
            if device.family == DeviceFamily.PIC:
                config = parser.get_device_config(device_name)
                if config["config_words"]:
                    print("\n⚙️ Configuration Words:")
                    for cw in config["config_words"][:5]:
                        print(
                            f"  {cw.name:12} @ 0x{cw.address:04X} = 0x{cw.default_value:04X}"
                        )

            # Show fuses for ATMEL devices
            if device.family == DeviceFamily.ATMEL:
                config = parser.get_device_config(device_name)
                if config["fuses"]:
                    print("\n🔒 Fuse Configuration:")
                    for fuse in config["fuses"]:
                        default = (
                            f"0x{fuse.default_value:02X}"
                            if fuse.default_value
                            else "N/A"
                        )
                        print(
                            f"  {fuse.name:10} @ 0x{fuse.offset:02X} = {default} ({len(fuse.bitfields)} bitfields)"
                        )

        except Exception as e:
            print(f"  ❌ Error parsing device '{device_name}': {e}")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
