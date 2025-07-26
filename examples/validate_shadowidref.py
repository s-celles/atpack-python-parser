#!/usr/bin/env python3
"""
Validate device specifications extractor with shadowidref handling

This example validates that the device specifications extractor correctly
handles the edc:shadowidref attribute to avoid double-counting memory sectors.
"""

import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from atpack_parser import AtPackParser


def validate_shadowidref_handling():
    """Validate that shadowidref attributes are properly handled."""
    print("🧪 Validating shadowidref handling in device specifications extraction")
    print("=" * 70)

    # Path to PIC AtPack
    atpack_path = (
        Path(__file__).parent.parent
        / "atpacks"
        / "Microchip.PIC16Fxxx_DFP.1.7.162.atpack"
    )

    if not atpack_path.exists():
        print(f"❌ AtPack file not found: {atpack_path}")
        return

    try:
        # Initialize parser
        parser = AtPackParser(str(atpack_path))
        print(f"✅ Loaded AtPack from: {atpack_path.name}")

        # Validate devices that are known to have shadowidref attributes
        validation_devices = ["PIC16F877A", "PIC16F84A", "PIC16F628A", "PIC16F688"]

        for device_name in validation_devices:
            print(f"\n📋 Validating {device_name}:")

            try:
                # Extract specs using our new extractor
                specs = parser.get_device_specs(device_name)

                print(f"   💾 Program Memory: {specs.maximum_size} words")
                print(f"   🧠 Total RAM: {specs.maximum_ram_size} bytes")
                print(f"   💡 GPR Total: {specs.gpr_total_size} bytes")
                print(f"   🏦 GPR Banks: {len(specs.gpr_sectors)}")

                # Show GPR sectors details
                for sector in specs.gpr_sectors:
                    addr_range = f"0x{sector.start_addr:04X}-0x{sector.end_addr:04X}"
                    print(
                        f"      - {sector.name}: {addr_range} ({sector.size} bytes) [Bank {sector.bank}]"
                    )

                # Verify the specs make sense
                if specs.maximum_ram_size == 0:
                    print(
                        "   ⚠️  Warning: No RAM detected (possible shadowidref issue?)"
                    )
                elif specs.maximum_ram_size != specs.gpr_total_size:
                    print(
                        "   ⚠️  Warning: RAM size mismatch between maximum_ram_size and gpr_total_size"
                    )
                else:
                    print("   ✅ RAM extraction looks correct")

                if specs.eeprom_size > 0:
                    print(
                        f"   💽 EEPROM: {specs.eeprom_size} bytes @ {specs.eeprom_addr}"
                    )

                if specs.config_size > 0:
                    print(
                        f"   ⚙️  Config: {specs.config_size} bytes @ {specs.config_addr}"
                    )

            except Exception as e:
                print(f"   ❌ Failed to extract specs for {device_name}: {e}")

    except Exception as e:
        print(f"❌ Error in validation: {e}")


def compare_with_reference():
    """Compare our extraction with the reference CSV data."""
    print("\n\n🔍 Comparing with reference CSV data")
    print("=" * 50)

    # Load reference CSV data from atpack-python-get-specs project
    csv_path = (
        Path(__file__).parent.parent.parent
        / "atpack-python-get-specs"
        / "pic16_device_specs.csv"
    )

    if not csv_path.exists():
        print(f"❌ Reference CSV not found: {csv_path}")
        return

    # Parse reference data
    reference_data = {}
    try:
        import csv

        with open(csv_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                device_name = row["device_name"]
                reference_data[device_name] = {
                    "maximum_ram_size": int(row["maximum_ram_size"]),
                    "maximum_size": int(row["maximum_size"]),
                    "eeprom_size": int(row["eeprom_size"]),
                    "config_size": int(row["config_size"]),
                }
    except Exception as e:
        print(f"❌ Failed to load reference CSV: {e}")
        return

    print(f"✅ Loaded reference data for {len(reference_data)} devices")

    # Test our extractor against reference
    atpack_path = (
        Path(__file__).parent.parent
        / "atpacks"
        / "Microchip.PIC16Fxxx_DFP.1.7.162.atpack"
    )

    if not atpack_path.exists():
        print(f"❌ AtPack file not found: {atpack_path}")
        return

    try:
        parser = AtPackParser(str(atpack_path))

        # Validate a few key devices
        validation_devices = [
            "PIC16F877A",
            "PIC16F84A",
            "PIC16F628A",
            "PIC16F688",
            "PIC16F883",
        ]
        matches = 0
        mismatches = 0

        for device_name in validation_devices:
            if device_name not in reference_data:
                continue

            print(f"\n📊 Comparing {device_name}:")

            try:
                specs = parser.get_device_specs(device_name)
                ref = reference_data[device_name]

                # Compare key values
                comparisons = [
                    ("RAM Size", specs.maximum_ram_size, ref["maximum_ram_size"]),
                    ("Program Size", specs.maximum_size, ref["maximum_size"]),
                    ("EEPROM Size", specs.eeprom_size, ref["eeprom_size"]),
                    ("Config Size", specs.config_size, ref["config_size"]),
                ]

                device_matches = 0
                for name, our_val, ref_val in comparisons:
                    if our_val == ref_val:
                        print(f"   ✅ {name}: {our_val} (matches reference)")
                        device_matches += 1
                    else:
                        print(f"   ❌ {name}: {our_val} vs reference {ref_val}")

                if device_matches == len(comparisons):
                    matches += 1
                    print(f"   🎉 Perfect match for {device_name}!")
                else:
                    mismatches += 1
                    print(
                        f"   ⚠️  {device_matches}/{len(comparisons)} values match for {device_name}"
                    )

            except Exception as e:
                print(f"   ❌ Failed to extract specs for {device_name}: {e}")
                mismatches += 1

        print(
            f"\n📈 Summary: {matches} perfect matches, {mismatches} mismatches out of {len(validation_devices)} devices validated"
        )

        if matches == len(validation_devices):
            print(
                "🎉 All validations passed! shadowidref handling is working correctly."
            )
        elif matches > mismatches:
            print(
                "✅ Most validations passed. shadowidref handling appears to be working."
            )
        else:
            print(
                "⚠️  Many mismatches detected. May need to review shadowidref handling."
            )

    except Exception as e:
        print(f"❌ Error in comparison: {e}")


def main():
    """Main validation function."""
    validate_shadowidref_handling()
    compare_with_reference()


if __name__ == "__main__":
    main()
