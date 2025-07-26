#!/usr/bin/env python3
"""
Final demonstration of device specifications extraction with shadowidref handling

This example shows the complete functionality for extracting device specifications
from AtPack files with proper shadowidref handling to avoid double-counting memory regions.
"""

import sys
import json
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from atpack_parser import AtPackParser


def demonstrate_complete_extraction():
    """Complete demonstration of device specifications extraction."""
    print("🚀 Complete Device Specifications Extraction Demo")
    print("=" * 60)
    print("Features:")
    print("  ✅ shadowidref-aware parsing")
    print("  ✅ f_cpu, maximum_ram_size, maximum_size extraction")
    print("  ✅ EEPROM address and size")
    print("  ✅ Configuration memory details")
    print("  ✅ Detailed GPR (General Purpose Register) information")
    print()

    # Path to PIC AtPack
    atpack_path = (
        Path(__file__).parent.parent
        / "atpacks"
        / "Microchip.PIC16Fxxx_DFP.1.7.162.atpack"
    )

    if not atpack_path.exists():
        print(f"❌ AtPack file not found: {atpack_path}")
        print("Please ensure you have the AtPack file in the correct location.")
        return

    try:
        # Initialize parser
        parser = AtPackParser(str(atpack_path))
        print(f"✅ Loaded AtPack: {atpack_path.name}")
        print(f"🏷️  Device family: {parser.device_family.value}")
        print()

        # Demonstrate single device extraction
        device_name = "PIC16F877A"
        print(f"📋 Extracting specifications for {device_name}:")
        print("-" * 50)

        specs = parser.get_device_specs(device_name)

        print(f"Device Name: {specs.device_name}")
        print(f"Architecture: {specs.architecture}")
        print(f"Series: {specs.series}")
        print(f"CPU Frequency: {specs.f_cpu}")
        print()

        print("Memory Information:")
        print(f"  📦 Program Memory (Flash): {specs.maximum_size:,} words")
        print(f"  🧠 Total RAM: {specs.maximum_ram_size:,} bytes")
        print(f"  💡 GPR Total: {specs.gpr_total_size:,} bytes")
        print()

        if specs.eeprom_size > 0:
            print(f"  💽 EEPROM: {specs.eeprom_size} bytes @ {specs.eeprom_addr}")
        else:
            print(f"  💽 EEPROM: Not available")

        if specs.config_size > 0:
            print(
                f"  ⚙️  Config Memory: {specs.config_size} bytes @ {specs.config_addr}"
            )
        else:
            print(f"  ⚙️  Config Memory: Not available")
        print()

        print(f"🏦 GPR Memory Banks ({len(specs.gpr_sectors)} sectors):")
        for sector in specs.gpr_sectors:
            addr_range = f"0x{sector.start_addr:04X}-0x{sector.end_addr:04X}"
            print(
                f"  - {sector.name}: {addr_range} ({sector.size} bytes) [Bank {sector.bank}]"
            )
        print()

        # Demonstrate bulk extraction
        print("📊 Bulk extraction sample (first 5 devices):")
        print("-" * 50)

        all_specs = parser.get_all_device_specs()
        print(f"✅ Extracted specifications for {len(all_specs)} devices total")
        print()

        print("Sample of extracted devices:")
        for i, spec in enumerate(all_specs[:5]):
            eeprom_info = f"{spec.eeprom_size}B" if spec.eeprom_size > 0 else "None"
            gpr_banks = len(spec.gpr_sectors)
            print(
                f"  {i + 1}. {spec.device_name:<12} - Flash: {spec.maximum_size:4d}W, RAM: {spec.maximum_ram_size:3d}B, EEPROM: {eeprom_info:<5}, GPR Banks: {gpr_banks}"
            )
        print()

        # Show memory size distribution
        print("💾 Memory Size Distribution:")
        print("-" * 30)

        ram_sizes = {}
        flash_sizes = {}

        for spec in all_specs:
            ram_size = spec.maximum_ram_size
            flash_size = spec.maximum_size

            ram_sizes[ram_size] = ram_sizes.get(ram_size, 0) + 1
            flash_sizes[flash_size] = flash_sizes.get(flash_size, 0) + 1

        print("Common RAM sizes:")
        for size in sorted(ram_sizes.keys()):
            count = ram_sizes[size]
            print(f"  {size:3d} bytes: {count:2d} devices")

        print("\nCommon Flash sizes:")
        for size in sorted(flash_sizes.keys()):
            count = flash_sizes[size]
            print(f"  {size:5d} words: {count:2d} devices")
        print()

        # Show devices with EEPROM
        eeprom_devices = [spec for spec in all_specs if spec.eeprom_size > 0]
        print(f"💽 Devices with EEPROM: {len(eeprom_devices)}/{len(all_specs)}")

        eeprom_sizes = {}
        for spec in eeprom_devices:
            size = spec.eeprom_size
            eeprom_sizes[size] = eeprom_sizes.get(size, 0) + 1

        print("EEPROM size distribution:")
        for size in sorted(eeprom_sizes.keys()):
            count = eeprom_sizes[size]
            print(f"  {size:3d} bytes: {count:2d} devices")
        print()

        # Export sample
        output_file = Path("sample_device_specs.json")
        sample_data = [spec.model_dump() for spec in all_specs[:10]]

        with open(output_file, "w") as f:
            json.dump(sample_data, f, indent=2)

        print(f"💾 Exported sample data (first 10 devices) to {output_file}")
        print()

        print("✅ Demonstration completed successfully!")
        print()
        print("Key features demonstrated:")
        print("  🔍 shadowidref attribute handling (avoids double-counting)")
        print("  📊 Comprehensive memory specifications")
        print("  🏦 Detailed GPR sector analysis")
        print("  💽 EEPROM and configuration memory detection")
        print("  📈 Bulk processing capabilities")
        print("  💾 JSON export functionality")

    except Exception as e:
        print(f"❌ Error in demonstration: {e}")
        import traceback

        traceback.print_exc()


def show_cli_usage():
    """Show CLI usage examples."""
    print("\n\n📚 CLI Usage Examples")
    print("=" * 40)
    print()
    print("Extract specifications for a single device:")
    print("  atpack devices specs PIC16F877A path/to/atpack.atpack")
    print()
    print("Extract with detailed GPR information:")
    print("  atpack devices specs PIC16F877A path/to/atpack.atpack --show-gpr")
    print()
    print("Export to JSON:")
    print(
        "  atpack devices specs PIC16F877A path/to/atpack.atpack --format json --output specs.json"
    )
    print()
    print("Export to CSV:")
    print(
        "  atpack devices specs PIC16F877A path/to/atpack.atpack --format csv --output specs.csv"
    )
    print()
    print("Other useful commands:")
    print("  atpack devices list path/to/atpack.atpack")
    print("  atpack devices info PIC16F877A path/to/atpack.atpack")
    print("  atpack devices pinout PIC16F877A path/to/atpack.atpack")
    print()


def main():
    """Main demonstration function."""
    demonstrate_complete_extraction()
    show_cli_usage()


if __name__ == "__main__":
    main()
