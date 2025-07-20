#!/usr/bin/env python3
"""
Enhanced debug script to test the new PlatformIO-useful information extraction.
"""

import zipfile
from pathlib import Path
import pytest
from src.atpack_parser.pic_parser import PicParser


@pytest.mark.integration
@pytest.mark.atpack_required
def test_enhanced_pic_parser():
    """Test the enhanced PIC parser with PlatformIO-useful information."""

    atpack_file = Path(__file__).parent.parent / "atpacks" / "Microchip.PIC16Fxxx_DFP.1.7.162.atpack"
    pic_file = "edc/PIC16F876A.PIC"

    # Skip test if atpack file is not available (e.g., in CI)
    if not atpack_file.exists():
        warning_msg = (
            f"⚠️  PIC AtPack file not available: {atpack_file}\n"
            f"   This integration test requires AtPack files.\n"
            f"   See atpacks/README.md for download instructions.\n"
            f"   Test will be SKIPPED."
        )
        print(warning_msg)
        pytest.skip(f"AtPack file not available: {atpack_file}")

    print("=== Enhanced PIC Parser Test ===\n")

    # Read the PIC file from the .atpack zip archive
    try:
        with zipfile.ZipFile(atpack_file, 'r') as zip_file:
            with zip_file.open(pic_file) as f:
                pic_content = f.read().decode('utf-8')
    except (zipfile.BadZipFile, KeyError) as e:
        warning_msg = (
            f"⚠️  Could not read PIC file from AtPack: {e}\n"
            f"   The AtPack file may be corrupted or have a different structure.\n"
            f"   Test will be SKIPPED."
        )
        print(warning_msg)
        pytest.skip(f"Could not read PIC file from atpack: {e}")

    # Parse the device
    parser = PicParser(pic_content)
    device = parser.parse_device("PIC16F876A")

    print(f"Device: {device.name}")
    print(f"Family: {device.family}")
    print(f"Series: {device.series}")
    print(f"Architecture: {device.architecture}")
    print()

    # Power specifications
    if device.power_specs:
        print("=== Power Specifications ===")
        ps = device.power_specs
        if ps.vdd_min or ps.vdd_max:
            print(f"VDD Range: {ps.vdd_min}V - {ps.vdd_max}V")
        if ps.vdd_nominal:
            print(f"VDD Nominal: {ps.vdd_nominal}V")
        if ps.vpp_min or ps.vpp_max:
            print(f"VPP Range: {ps.vpp_min}V - {ps.vpp_max}V")
        if ps.has_high_voltage_mclr is not None:
            print(f"High Voltage MCLR: {ps.has_high_voltage_mclr}")
        print()
    else:
        print("=== Power Specifications ===")
        print("No power specifications found")
        print()

    # Oscillator configurations
    if device.oscillator_configs:
        print("=== Oscillator Configurations ===")
        for osc in device.oscillator_configs:
            print(f"  {osc.name}: {osc.description}")
            if osc.legacy_alias:
                print(f"    Legacy: {osc.legacy_alias}")
            if osc.when_condition:
                print(f"    Condition: {osc.when_condition}")
        print()
    else:
        print("=== Oscillator Configurations ===")
        print("No oscillator configurations found")
        print()

    # Programming interface
    if device.programming_interface:
        print("=== Programming Interface ===")
        pi = device.programming_interface
        if pi.memory_technology:
            print(f"Memory Technology: {pi.memory_technology}")
        if pi.erase_algorithm:
            print(f"Erase Algorithm: {pi.erase_algorithm}")
        if pi.has_low_voltage_programming is not None:
            print(f"Low Voltage Programming: {pi.has_low_voltage_programming}")
        if pi.low_voltage_threshold:
            print(f"LVP Threshold: {pi.low_voltage_threshold}V")
        if pi.programming_tries:
            print(f"Programming Tries: {pi.programming_tries}")

        if pi.wait_times:
            print("Programming Wait Times:")
            for op, timing in pi.wait_times.items():
                print(f"  {op}: {timing['time']} {timing['units']}")

        if pi.row_sizes:
            print("Programming Row Sizes:")
            for op, size in pi.row_sizes.items():
                print(f"  {op}: {size} words")
        print()
    else:
        print("=== Programming Interface ===")
        print("No programming interface info found")
        print()

    # Pinout information
    if device.pinout:
        print("=== Pinout Information ===")
        print(f"Total pins: {len(device.pinout)}")

        pin_type_counts = {}
        for pin in device.pinout:
            pin_type = pin.pin_type or "unknown"
            pin_type_counts[pin_type] = pin_type_counts.get(pin_type, 0) + 1

        print("Pin types:", pin_type_counts)

        print("\nSample pins:")
        for i, pin in enumerate(device.pinout[:5]):
            func_names = [f.name for f in pin.alternative_functions]
            print(
                f"  Pin {pin.physical_pin}: {pin.primary_function} "
                f"({pin.pin_type}) - Functions: {', '.join(func_names)}"
            )

        if len(device.pinout) > 5:
            print(f"  ... and {len(device.pinout) - 5} more pins")
        print()
    else:
        print("=== Pinout Information ===")
        print("No pinout information found")
        print()

    # Debug capabilities
    if device.debug_capabilities:
        print("=== Debug Capabilities ===")
        dc = device.debug_capabilities
        if dc.hardware_breakpoint_count:
            print(f"Hardware Breakpoints: {dc.hardware_breakpoint_count}")
        if dc.has_data_capture is not None:
            print(f"Data Capture: {dc.has_data_capture}")
        if dc.id_byte:
            print(f"ID Byte: {dc.id_byte}")
        print()
    else:
        print("=== Debug Capabilities ===")
        print("No debug capabilities found")
        print()

    # Architecture information
    if device.architecture_info:
        print("=== Architecture Information ===")
        ai = device.architecture_info
        if ai.instruction_set:
            print(f"Instruction Set: {ai.instruction_set}")
        if ai.hardware_stack_depth:
            print(f"Hardware Stack Depth: {ai.hardware_stack_depth}")
        if ai.code_word_size:
            print(f"Code Word Size: {ai.code_word_size} bytes")
        if ai.data_word_size:
            print(f"Data Word Size: {ai.data_word_size} bytes")
        print()
    else:
        print("=== Architecture Information ===")
        print("No architecture information found")
        print()

    # Detected peripherals
    if device.detected_peripherals:
        print("=== Detected Peripherals ===")
        for peripheral in device.detected_peripherals:
            print(f"  - {peripheral}")
        print()
    else:
        print("=== Detected Peripherals ===")
        print("No peripherals detected")
        print()

    # Summary for PlatformIO
    print("=== PlatformIO Board Definition Usefulness ===")
    useful_info = []

    if device.power_specs and (
        device.power_specs.vdd_min or device.power_specs.vdd_max
    ):
        useful_info.append("✓ Power supply voltage ranges")

    if device.oscillator_configs:
        useful_info.append("✓ Oscillator configuration options")

    if device.programming_interface:
        useful_info.append("✓ Programming interface specifications")

    if device.pinout:
        useful_info.append("✓ Complete pinout with alternative functions")

    if device.debug_capabilities:
        useful_info.append("✓ Hardware debugging capabilities")

    if device.architecture_info and device.architecture_info.instruction_set:
        useful_info.append("✓ Instruction set identification")

    if device.detected_peripherals:
        useful_info.append("✓ Peripheral detection for library compatibility")

    if useful_info:
        print("Found useful information for PlatformIO board definitions:")
        for info in useful_info:
            print(f"  {info}")
    else:
        print("No additional useful information found beyond basic device specs")

    print(f"\nTotal additional fields extracted: {len(useful_info)}")


if __name__ == "__main__":
    test_enhanced_pic_parser()
