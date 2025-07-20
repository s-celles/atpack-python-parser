#!/usr/bin/env python3
"""
Enhanced test script for ATMEL parser with PlatformIO-useful information.
"""

import pytest
from src.atpack_parser.atdf_parser import AtdfParser


@pytest.mark.integration
@pytest.mark.atpack_required
def test_enhanced_atmel_parser(atmel_content: str):
    """Test the enhanced ATMEL parser with PlatformIO-useful information."""
    print("=== Enhanced ATMEL Parser Test ===\n")

    # Parse the device
    parser = AtdfParser(atmel_content)
    device = parser.parse_device("ATmega16")

    print(f"Device: {device.name}")
    print(f"Family: {device.family}")
    print(f"Series: {device.series}")
    print(f"Architecture: {device.architecture}")
    print()

    # Package variants
    if device.atmel_package_variants:
        print("=== Package Variants ===")
        for variant in device.atmel_package_variants:
            print(f"  Package: {variant.package}")
            print(f"    Pinout: {variant.pinout}")
            if variant.order_code:
                print(f"    Order Code: {variant.order_code}")
            if variant.temp_min is not None and variant.temp_max is not None:
                print(
                    f"    Temperature Range: {variant.temp_min}°C to {variant.temp_max}°C"
                )
            if variant.speed_max:
                print(f"    Max Speed: {variant.speed_max / 1000000:.1f} MHz")
            if variant.vcc_min is not None and variant.vcc_max is not None:
                print(f"    VCC Range: {variant.vcc_min}V - {variant.vcc_max}V")
            print()
    else:
        print("=== Package Variants ===")
        print("No package variants found")
        print()

    # Pinout information
    if device.atmel_pinouts:
        print("=== Pinout Information ===")
        for pinout in device.atmel_pinouts:
            print(f"  Pinout: {pinout.name} ({pinout.pin_count} pins)")
            if pinout.caption:
                print(f"    Caption: {pinout.caption}")

            print("    Sample pins:")
            for i, pin in enumerate(pinout.pins[:8]):
                print(f"      Pin {pin['position']}: {pin['pad']}")
            if len(pinout.pins) > 8:
                print(f"      ... and {len(pinout.pins) - 8} more pins")
            print()
    else:
        print("=== Pinout Information ===")
        print("No pinout information found")
        print()

    # Programming interfaces
    if device.atmel_programming_interfaces:
        print("=== Programming Interfaces ===")
        for interface in device.atmel_programming_interfaces:
            print(f"  Interface: {interface.name} (Type: {interface.interface_type})")
            if interface.properties:
                print("    Properties:")
                for prop, value in interface.properties.items():
                    print(f"      {prop}: {value}")
            print()
    else:
        print("=== Programming Interfaces ===")
        print("No programming interfaces found")
        print()

    # Clock information
    if device.atmel_clock_info:
        print("=== Clock Information ===")
        ci = device.atmel_clock_info

        if ci.max_frequency:
            print(f"Maximum Frequency: {ci.max_frequency / 1000000:.1f} MHz")

        if ci.clock_modules:
            print("Clock Modules:")
            for module in ci.clock_modules:
                print(f"  - {module['name']}")
                if "instances" in module:
                    print(f"    Instances: {len(module['instances'])}")

        if ci.clock_properties:
            print("Clock Properties:")
            for prop_group in ci.clock_properties:
                print(f"  Group: {prop_group['name']}")
                for prop in prop_group["properties"]:
                    prop_name = prop.get("name", "Unknown")
                    prop_value = prop.get("value", prop.get("caption", "N/A"))
                    print(f"    {prop_name}: {prop_value}")
        print()
    else:
        print("=== Clock Information ===")
        print("No clock information found")
        print()

    # GPIO information
    if device.atmel_gpio_info:
        print("=== GPIO Information ===")
        total_pins = 0
        for gpio_port in device.atmel_gpio_info:
            pin_count = gpio_port.pin_count or 0
            total_pins += pin_count
            print(f"  Port: {gpio_port.port_name}")
            if gpio_port.pin_count:
                print(f"    Pin Count: {gpio_port.pin_count}")
            if gpio_port.instances:
                print(f"    Instances: {len(gpio_port.instances)}")
                # Show sample instances
                for i, instance in enumerate(gpio_port.instances[:3]):
                    inst_name = instance.get("name", f"Instance{i}")
                    print(f"      - {inst_name}")
                if len(gpio_port.instances) > 3:
                    print(f"      ... and {len(gpio_port.instances) - 3} more")

        if total_pins > 0:
            print(f"  Total GPIO Pins: {total_pins}")
        print()
    else:
        print("=== GPIO Information ===")
        print("No GPIO information found")
        print()

    # Summary for PlatformIO
    print("=== PlatformIO Board Definition Usefulness ===")
    useful_info = []

    if device.atmel_package_variants:
        useful_info.append("✓ Package variants with temperature and voltage specs")

    if device.atmel_pinouts:
        useful_info.append("✓ Complete pinout mapping for all package types")

    if device.atmel_programming_interfaces:
        useful_info.append("✓ Programming interface specifications (ISP, JTAG)")

    if device.atmel_clock_info and device.atmel_clock_info.max_frequency:
        useful_info.append("✓ Maximum operating frequency specifications")

    if device.atmel_gpio_info:
        useful_info.append("✓ Detailed GPIO port information")

    # Existing basic info
    if device.memory_segments:
        useful_info.append("✓ Memory architecture (already supported)")

    if device.modules:
        useful_info.append("✓ Peripheral module definitions (already supported)")

    if device.interrupts:
        useful_info.append("✓ Interrupt system mapping (already supported)")

    if useful_info:
        print("Found useful information for PlatformIO board definitions:")
        for info in useful_info:
            print(f"  {info}")
    else:
        print("No additional useful information found beyond basic device specs")

    atmel_enhancements = sum(
        1 for info in useful_info if "already supported" not in info
    )
    print(f"\nNew ATMEL-specific enhancements: {atmel_enhancements}")
    print(f"Total useful fields for PlatformIO: {len(useful_info)}")


if __name__ == "__main__":
    test_enhanced_atmel_parser()
