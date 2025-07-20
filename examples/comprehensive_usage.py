#!/usr/bin/env python3
"""
Comprehensive usage example for AtPack Parser

This script demonstrates all the key features of the atpack-parser library
for both ATMEL and PIC devices.
"""

import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from atpack_parser import AtPackParser
from atpack_parser.exceptions import DeviceNotFoundError


def demonstrate_atmel_parsing():
    """Demonstrate parsing ATMEL AtPack files."""
    print("🔵 ATMEL AtPack Parsing Demo")
    print("=" * 50)

    # Path to ATMEL AtPack (adjust as needed)
    atpack_path = (
        Path(__file__).parent.parent.parent
        / "public"
        / "atpacks"
        / "Atmel.ATmega_DFP.2.2.509_dir_atpack"
    )

    if not atpack_path.exists():
        print(f"❌ AtPack path not found: {atpack_path}")
        return

    try:
        # Initialize parser
        parser = AtPackParser(str(atpack_path))
        print(f"✅ Loaded AtPack from: {atpack_path.name}")

        # List all devices
        devices = parser.get_devices()
        print(f"📦 Found {len(devices)} devices")
        print(f"First 5 devices: {devices[:5]}")

        # Get detailed information for ATmega16
        device_name = "ATmega16"
        try:
            device = parser.get_device(device_name)
            print(f"\n🔌 Device: {device.name}")
            print(f"   Family: {device.family}")
            print(f"   Architecture: {device.architecture}")
            print(f"   Series: {device.series}")

            # Memory information
            print(f"\n💾 Memory Segments ({len(device.memory_segments)}):")
            for segment in device.memory_segments[:5]:  # Show first 5
                print(
                    f"   - {segment.name}: {segment.start:#06x} - {segment.size} bytes ({segment.type})"
                )

            # Module information
            print(f"\n🔧 Modules ({len(device.modules)}):")
            for module in device.modules[:5]:  # Show first 5
                reg_count = sum(
                    len(group.registers) for group in module.register_groups
                )
                print(
                    f"   - {module.name}: {len(module.register_groups)} groups, {reg_count} registers"
                )

            # Interrupts
            print(f"\n⚡ Interrupts ({len(device.interrupts)}):")
            for interrupt in device.interrupts[:5]:  # Show first 5
                print(f"   - {interrupt.name}: {interrupt.index}")

            # Signatures
            print(f"\n🔐 Signatures ({len(device.signatures)}):")
            for sig in device.signatures:
                print(f"   - {sig.name}: {sig.value}")

            # Enhanced ATMEL-specific information (if available)
            if hasattr(device, "package_variants") and device.package_variants:
                print(f"\n📦 Package Variants ({len(device.package_variants)}):")
                for variant in device.package_variants[:3]:
                    print(f"   - {variant.package}: {variant.pin_count} pins")

            if (
                hasattr(device, "programming_interfaces")
                and device.programming_interfaces
            ):
                print(
                    f"\n🔌 Programming Interfaces ({len(device.programming_interfaces)}):"
                )
                for interface in device.programming_interfaces:
                    print(f"   - {interface.name}: {interface.type}")

        except DeviceNotFoundError:
            print(f"❌ Device '{device_name}' not found in AtPack")

    except Exception as e:
        print(f"❌ Error parsing ATMEL AtPack: {e}")

    print("\n")


def demonstrate_pic_parsing():
    """Demonstrate parsing PIC AtPack files."""
    print("🟡 PIC AtPack Parsing Demo")
    print("=" * 50)

    # Path to PIC AtPack (adjust as needed)
    atpack_path = (
        Path(__file__).parent.parent.parent
        / "public"
        / "atpacks"
        / "Microchip.PIC16Fxxx_DFP.1.7.162_dir_atpack"
    )

    if not atpack_path.exists():
        print(f"❌ AtPack path not found: {atpack_path}")
        return

    try:
        # Initialize parser
        parser = AtPackParser(str(atpack_path))
        print(f"✅ Loaded AtPack from: {atpack_path.name}")

        # List all devices
        devices = parser.get_devices()
        print(f"📦 Found {len(devices)} devices")
        print(f"First 5 devices: {devices[:5]}")

        # Get detailed information for PIC16F876A
        device_name = "PIC16F876A"
        try:
            device = parser.get_device(device_name)
            print(f"\n🔌 Device: {device.name}")
            print(f"   Family: {device.family}")
            print(f"   Architecture: {device.architecture}")
            print(f"   Series: {device.series}")

            # Memory information
            print(f"\n💾 Memory Segments ({len(device.memory_segments)}):")
            for segment in device.memory_segments:
                print(
                    f"   - {segment.name}: {segment.start:#06x} - {segment.size} bytes ({segment.type})"
                )

            # Module information
            print(f"\n🔧 Modules ({len(device.modules)}):")
            for module in device.modules:
                reg_count = sum(
                    len(group.registers) for group in module.register_groups
                )
                print(
                    f"   - {module.name}: {len(module.register_groups)} groups, {reg_count} registers"
                )

            # Interrupts
            print(f"\n⚡ Interrupts ({len(device.interrupts)}):")
            for interrupt in device.interrupts[:5]:  # Show first 5
                print(f"   - {interrupt.name}: {interrupt.index}")

            # Signatures
            print(f"\n🔐 Signatures ({len(device.signatures)}):")
            for sig in device.signatures:
                print(f"   - {sig.name}: {sig.value}")

            # Enhanced PIC-specific information (if available)
            if hasattr(device, "power_specification") and device.power_specification:
                power = device.power_specification
                print("\n⚡ Power Specification:")
                print(f"   - VDD: {power.vdd_min}V - {power.vdd_max}V")
                print(
                    f"   - Current: {power.current_sleep}μA (sleep), {power.current_active}mA (active)"
                )

            if hasattr(device, "oscillator_configs") and device.oscillator_configs:
                print(f"\n🔄 Oscillator Configs ({len(device.oscillator_configs)}):")
                for osc in device.oscillator_configs[:3]:
                    print(f"   - {osc.name}: {osc.frequency_range}")

            if (
                hasattr(device, "programming_interface")
                and device.programming_interface
            ):
                prog = device.programming_interface
                print("\n🔌 Programming Interface:")
                print(f"   - Type: {prog.type}")
                print(f"   - Voltage: {prog.voltage}")
                print(f"   - Pins: {', '.join(prog.pins) if prog.pins else 'N/A'}")

        except DeviceNotFoundError:
            print(f"❌ Device '{device_name}' not found in AtPack")

    except Exception as e:
        print(f"❌ Error parsing PIC AtPack: {e}")


def demonstrate_register_access():
    """Demonstrate accessing device registers."""
    print("🔧 Register Access Demo")
    print("=" * 50)

    # Use ATMEL example
    atpack_path = (
        Path(__file__).parent.parent.parent
        / "public"
        / "atpacks"
        / "Atmel.ATmega_DFP.2.2.509_dir_atpack"
    )

    if not atpack_path.exists():
        print(f"❌ AtPack path not found: {atpack_path}")
        return

    try:
        parser = AtPackParser(str(atpack_path))
        device_name = "ATmega16"

        # Get device registers
        registers = parser.get_device_registers(device_name)
        print(f"📋 Found {len(registers)} registers for {device_name}")

        # Show some interesting registers
        timer_regs = [
            r for r in registers if "TIMER" in r.name.upper() or "TCN" in r.name.upper()
        ]
        if timer_regs:
            print(f"\n⏰ Timer Registers ({len(timer_regs)}):")
            for reg in timer_regs[:5]:
                print(f"   - {reg.name}: {reg.offset:#06x} ({reg.size} bytes)")
                if reg.bitfields:
                    print(
                        f"     Bitfields: {', '.join([bf.name for bf in reg.bitfields[:3]])}"
                    )

        # Show GPIO registers
        gpio_regs = [
            r
            for r in registers
            if "PORT" in r.name.upper()
            or "DDR" in r.name.upper()
            or "PIN" in r.name.upper()
        ]
        if gpio_regs:
            print(f"\n🔌 GPIO Registers ({len(gpio_regs)}):")
            for reg in gpio_regs[:5]:
                print(f"   - {reg.name}: {reg.offset:#06x}")

    except Exception as e:
        print(f"❌ Error accessing registers: {e}")


def main():
    """Main demonstration function."""
    print("🚀 AtPack Parser - Comprehensive Usage Demo")
    print("=" * 60)
    print()

    # Demonstrate ATMEL parsing
    demonstrate_atmel_parsing()

    # Demonstrate PIC parsing
    demonstrate_pic_parsing()

    # Demonstrate register access
    demonstrate_register_access()

    print("✅ Demo completed!")
    print("\n💡 Try using the CLI for more interactive exploration:")
    print("   python -m atpack_parser.cli devices list <atpack_path>")
    print("   python -m atpack_parser.cli devices info <device_name> <atpack_path>")
    print("   python -m atpack_parser.cli registers <device_name> <atpack_path>")


if __name__ == "__main__":
    main()
