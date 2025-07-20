#!/usr/bin/env python3
"""
Comprehensive analysis of ATMEL AtPack files for PlatformIO board definition insights.

This script examines ATMEL ATDF files to identify what additional information
(beyond what we currently extract) could be useful for PlatformIO board definitions.
"""

import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List


class AtmelAtPackAnalyzer:
    """Analyzer for identifying useful ATMEL AtPack information for PlatformIO."""

    def __init__(self, atdf_file_path: str):
        self.atdf_file_path = Path(atdf_file_path)
        self.tree = ET.parse(atdf_file_path)
        self.root = self.tree.getroot()

        # ATDF files typically don't use namespaces, but let's be prepared
        self.ns = {}

    def analyze_all_information(self) -> Dict[str, Any]:
        """Analyze all available information in the ATDF file."""
        analysis = {
            "file_info": self._analyze_file_info(),
            "device_info": self._analyze_device_info(),
            "memory_architecture": self._analyze_memory_architecture(),
            "peripheral_info": self._analyze_peripheral_info(),
            "interrupt_system": self._analyze_interrupt_system(),
            "pinout_info": self._analyze_pinout_info(),
            "clock_system": self._analyze_clock_system(),
            "power_management": self._analyze_power_management(),
            "programming_interface": self._analyze_programming_interface(),
            "debug_interface": self._analyze_debug_interface(),
            "package_info": self._analyze_package_info(),
            "electrical_specs": self._analyze_electrical_specs(),
            "all_elements": self._catalog_all_elements(),
        }
        return analysis

    def _analyze_file_info(self) -> Dict[str, Any]:
        """Analyze basic file and device identification info."""
        info = {}

        # Root element attributes
        for attr, value in self.root.attrib.items():
            info[attr] = value

        return info

    def _analyze_device_info(self) -> Dict[str, Any]:
        """Analyze device-specific information."""
        info = {}

        # Look for device element
        device = self.root.find(".//device")
        if device is not None:
            info["device_attributes"] = dict(device.attrib)

            # Architecture info
            arch = device.get("architecture", "")
            if arch:
                info["architecture"] = arch

            # Family info
            family = device.get("family", "")
            if family:
                info["family"] = family

            # Series info
            series = device.get("series", "")
            if series:
                info["series"] = series

        # Look for variant information
        variants = self.root.findall(".//variant")
        if variants:
            info["variants"] = []
            for variant in variants:
                variant_info = dict(variant.attrib)
                info["variants"].append(variant_info)

        return info

    def _analyze_memory_architecture(self) -> Dict[str, Any]:
        """Analyze detailed memory architecture."""
        memory_info = {}

        # Address spaces
        address_spaces = self.root.findall(".//address-space")
        if address_spaces:
            memory_info["address_spaces"] = []
            for addr_space in address_spaces:
                space_info = dict(addr_space.attrib)

                # Memory segments within this address space
                segments = addr_space.findall(".//memory-segment")
                if segments:
                    space_info["segments"] = []
                    for segment in segments:
                        seg_info = dict(segment.attrib)
                        space_info["segments"].append(seg_info)

                memory_info["address_spaces"].append(space_info)

        # Property groups related to memory
        property_groups = self.root.findall(".//property-group[@name]")
        memory_properties = []
        for prop_group in property_groups:
            group_name = prop_group.get("name", "").lower()
            if any(
                mem_type in group_name
                for mem_type in ["memory", "flash", "sram", "eeprom"]
            ):
                group_info = {"name": prop_group.get("name"), "properties": []}

                properties = prop_group.findall(".//property")
                for prop in properties:
                    prop_info = dict(prop.attrib)
                    if prop.text:
                        prop_info["value"] = prop.text.strip()
                    group_info["properties"].append(prop_info)

                memory_properties.append(group_info)

        if memory_properties:
            memory_info["memory_properties"] = memory_properties

        return memory_info

    def _analyze_peripheral_info(self) -> Dict[str, Any]:
        """Analyze peripheral modules and their capabilities."""
        peripheral_info = {}

        # Find all modules
        modules = self.root.findall(".//module")
        if modules:
            peripheral_info["modules"] = []
            for module in modules:
                module_info = dict(module.attrib)

                # Module instances
                instances = module.findall(".//instance")
                if instances:
                    module_info["instances"] = []
                    for instance in instances:
                        inst_info = dict(instance.attrib)
                        module_info["instances"].append(inst_info)

                # Register groups
                reg_groups = module.findall(".//register-group")
                if reg_groups:
                    module_info["register_groups"] = []
                    for reg_group in reg_groups:
                        group_info = dict(reg_group.attrib)

                        # Registers in this group
                        registers = reg_group.findall(".//register")
                        if registers:
                            group_info["register_count"] = len(registers)
                            # Sample a few registers
                            group_info["sample_registers"] = []
                            for reg in registers[:3]:
                                reg_info = dict(reg.attrib)
                                group_info["sample_registers"].append(reg_info)

                        module_info["register_groups"].append(group_info)

                peripheral_info["modules"].append(module_info)

        return peripheral_info

    def _analyze_interrupt_system(self) -> Dict[str, Any]:
        """Analyze interrupt system configuration."""
        interrupt_info = {}

        # Find interrupt definitions
        interrupts = self.root.findall(".//interrupt")
        if interrupts:
            interrupt_info["interrupts"] = []
            for interrupt in interrupts:
                int_info = dict(interrupt.attrib)
                interrupt_info["interrupts"].append(int_info)

            interrupt_info["total_interrupts"] = len(interrupts)

        # Look for interrupt vector table information
        vectors = self.root.findall(".//vector")
        if vectors:
            interrupt_info["vectors"] = []
            for vector in vectors:
                vec_info = dict(vector.attrib)
                interrupt_info["vectors"].append(vec_info)

        return interrupt_info

    def _analyze_pinout_info(self) -> Dict[str, Any]:
        """Analyze pinout and pin functionality information."""
        pinout_info = {}

        # Find pinout information
        pinouts = self.root.findall(".//pinout")
        if pinouts:
            pinout_info["pinouts"] = []
            for pinout in pinouts:
                pinout_data = dict(pinout.attrib)

                # Pins in this pinout
                pins = pinout.findall(".//pin")
                if pins:
                    pinout_data["pin_count"] = len(pins)
                    pinout_data["pins"] = []

                    for pin in pins:
                        pin_info = dict(pin.attrib)
                        pinout_data["pins"].append(pin_info)

                pinout_info["pinouts"].append(pinout_data)

        # GPIO port information
        gpio_info = {}
        gpio_modules = [
            m
            for m in self.root.findall(".//module")
            if m.get("name", "").upper().startswith("PORT")
        ]
        if gpio_modules:
            gpio_info["gpio_ports"] = []
            for gpio_module in gpio_modules:
                port_info = dict(gpio_module.attrib)

                instances = gpio_module.findall(".//instance")
                if instances:
                    port_info["instances"] = [dict(inst.attrib) for inst in instances]

                gpio_info["gpio_ports"].append(port_info)

        if gpio_info:
            pinout_info["gpio_info"] = gpio_info

        return pinout_info

    def _analyze_clock_system(self) -> Dict[str, Any]:
        """Analyze clock system and oscillator information."""
        clock_info = {}

        # Look for clock-related modules
        clock_modules = []
        for module in self.root.findall(".//module"):
            module_name = module.get("name", "").upper()
            if any(
                clock_term in module_name
                for clock_term in ["CLK", "OSC", "CLOCK", "PLL"]
            ):
                module_info = dict(module.attrib)

                instances = module.findall(".//instance")
                if instances:
                    module_info["instances"] = [dict(inst.attrib) for inst in instances]

                clock_modules.append(module_info)

        if clock_modules:
            clock_info["clock_modules"] = clock_modules

        # Look for clock-related properties
        clock_properties = []
        for prop_group in self.root.findall(".//property-group"):
            group_name = prop_group.get("name", "").lower()
            if any(
                clock_term in group_name for clock_term in ["clock", "osc", "frequency"]
            ):
                group_info = {"name": prop_group.get("name"), "properties": []}

                properties = prop_group.findall(".//property")
                for prop in properties:
                    prop_info = dict(prop.attrib)
                    if prop.text:
                        prop_info["value"] = prop.text.strip()
                    group_info["properties"].append(prop_info)

                clock_properties.append(group_info)

        if clock_properties:
            clock_info["clock_properties"] = clock_properties

        return clock_info

    def _analyze_power_management(self) -> Dict[str, Any]:
        """Analyze power management capabilities."""
        power_info = {}

        # Look for power-related modules
        power_modules = []
        for module in self.root.findall(".//module"):
            module_name = module.get("name", "").upper()
            if any(
                power_term in module_name
                for power_term in ["PM", "POWER", "SLEEP", "SUPC"]
            ):
                module_info = dict(module.attrib)

                instances = module.findall(".//instance")
                if instances:
                    module_info["instances"] = [dict(inst.attrib) for inst in instances]

                power_modules.append(module_info)

        if power_modules:
            power_info["power_modules"] = power_modules

        # Look for power-related properties
        power_properties = []
        for prop_group in self.root.findall(".//property-group"):
            group_name = prop_group.get("name", "").lower()
            if any(
                power_term in group_name
                for power_term in ["power", "voltage", "supply"]
            ):
                group_info = {"name": prop_group.get("name"), "properties": []}

                properties = prop_group.findall(".//property")
                for prop in properties:
                    prop_info = dict(prop.attrib)
                    if prop.text:
                        prop_info["value"] = prop.text.strip()
                    group_info["properties"].append(prop_info)

                power_properties.append(group_info)

        if power_properties:
            power_info["power_properties"] = power_properties

        return power_info

    def _analyze_programming_interface(self) -> Dict[str, Any]:
        """Analyze programming and debugging interface information."""
        prog_info = {}

        # Look for programming-related interfaces
        interfaces = self.root.findall(".//interface")
        if interfaces:
            prog_interfaces = []
            for interface in interfaces:
                int_type = interface.get("type", "").lower()
                if any(
                    prog_term in int_type
                    for prog_term in ["jtag", "swd", "isp", "pdi", "updi"]
                ):
                    int_info = dict(interface.attrib)
                    prog_interfaces.append(int_info)

            if prog_interfaces:
                prog_info["programming_interfaces"] = prog_interfaces

        # Look for programming-related properties
        prog_properties = []
        for prop_group in self.root.findall(".//property-group"):
            group_name = prop_group.get("name", "").lower()
            if any(
                prog_term in group_name
                for prog_term in ["programming", "debug", "jtag", "swd"]
            ):
                group_info = {"name": prop_group.get("name"), "properties": []}

                properties = prop_group.findall(".//property")
                for prop in properties:
                    prop_info = dict(prop.attrib)
                    if prop.text:
                        prop_info["value"] = prop.text.strip()
                    group_info["properties"].append(prop_info)

                prog_properties.append(group_info)

        if prog_properties:
            prog_info["programming_properties"] = prog_properties

        return prog_info

    def _analyze_debug_interface(self) -> Dict[str, Any]:
        """Analyze debugging interface capabilities."""
        debug_info = {}

        # Look for debug-related modules
        debug_modules = []
        for module in self.root.findall(".//module"):
            module_name = module.get("name", "").upper()
            if any(
                debug_term in module_name
                for debug_term in ["DEBUG", "DBG", "JTAG", "SWD"]
            ):
                module_info = dict(module.attrib)

                instances = module.findall(".//instance")
                if instances:
                    module_info["instances"] = [dict(inst.attrib) for inst in instances]

                debug_modules.append(module_info)

        if debug_modules:
            debug_info["debug_modules"] = debug_modules

        return debug_info

    def _analyze_package_info(self) -> Dict[str, Any]:
        """Analyze package and physical form factor information."""
        package_info = {}

        # Look for package information in variants
        variants = self.root.findall(".//variant")
        if variants:
            packages = []
            for variant in variants:
                package = variant.get("package", "")
                pinout = variant.get("pinout", "")

                if package or pinout:
                    pkg_info = {"package": package, "pinout": pinout}

                    # Add other variant attributes
                    for attr, value in variant.attrib.items():
                        if attr not in ["package", "pinout"]:
                            pkg_info[attr] = value

                    packages.append(pkg_info)

            if packages:
                package_info["packages"] = packages

        return package_info

    def _analyze_electrical_specs(self) -> Dict[str, Any]:
        """Analyze electrical specifications and parameters."""
        electrical_info = {}

        # Look for electrical parameter properties
        electrical_properties = []
        for prop_group in self.root.findall(".//property-group"):
            group_name = prop_group.get("name", "").lower()
            if any(
                elec_term in group_name
                for elec_term in ["electrical", "timing", "speed", "frequency"]
            ):
                group_info = {"name": prop_group.get("name"), "properties": []}

                properties = prop_group.findall(".//property")
                for prop in properties:
                    prop_info = dict(prop.attrib)
                    if prop.text:
                        prop_info["value"] = prop.text.strip()
                    group_info["properties"].append(prop_info)

                electrical_properties.append(group_info)

        if electrical_properties:
            electrical_info["electrical_properties"] = electrical_properties

        return electrical_info

    def _catalog_all_elements(self) -> Dict[str, List[str]]:
        """Catalog all XML elements to identify anything we might have missed."""
        elements_catalog = {}

        def traverse_element(elem, path=""):
            tag = elem.tag
            current_path = f"{path}/{tag}" if path else tag

            if tag not in elements_catalog:
                elements_catalog[tag] = []

            if current_path not in elements_catalog[tag]:
                elements_catalog[tag].append(current_path)

            for child in elem:
                traverse_element(child, current_path)

        traverse_element(self.root)
        return elements_catalog


def analyze_atmel_for_platformio(atdf_file: str) -> Dict[str, Any]:
    """Analyze ATDF file specifically for PlatformIO board definition insights."""
    analyzer = AtmelAtPackAnalyzer(atdf_file)
    full_analysis = analyzer.analyze_all_information()

    # Identify what would be useful for PlatformIO specifically
    platformio_useful = {
        "currently_extracted_by_our_parser": {
            "device_name": "Yes - from device identification",
            "series_family": "Yes - from device attributes",
            "memory_segments": "Yes - address spaces and segments",
            "registers": "Yes - peripheral register definitions",
            "interrupts": "Yes - interrupt definitions",
            "modules": "Yes - peripheral module information",
        },
        "additionally_useful_for_platformio": {
            "clock_system": {
                "found": bool(full_analysis.get("clock_system")),
                "usefulness": "High - for clock configuration and PLL setup",
                "data": full_analysis.get("clock_system", {}),
            },
            "pinout_mapping": {
                "found": bool(full_analysis.get("pinout_info")),
                "usefulness": "High - for pin mapping and GPIO configuration",
                "data": full_analysis.get("pinout_info", {}),
            },
            "programming_interfaces": {
                "found": bool(full_analysis.get("programming_interface")),
                "usefulness": "High - for upload protocol selection (JTAG, SWD, ISP)",
                "data": full_analysis.get("programming_interface", {}),
            },
            "package_variants": {
                "found": bool(full_analysis.get("package_info")),
                "usefulness": "Medium-High - for pin count validation and package selection",
                "data": full_analysis.get("package_info", {}),
            },
            "power_management": {
                "found": bool(full_analysis.get("power_management")),
                "usefulness": "Medium - for power-aware configuration",
                "data": full_analysis.get("power_management", {}),
            },
            "debug_capabilities": {
                "found": bool(full_analysis.get("debug_interface")),
                "usefulness": "Medium - for debugger configuration",
                "data": full_analysis.get("debug_interface", {}),
            },
            "electrical_specifications": {
                "found": bool(full_analysis.get("electrical_specs")),
                "usefulness": "Medium - for timing and frequency validation",
                "data": full_analysis.get("electrical_specs", {}),
            },
            "peripheral_capabilities": {
                "found": bool(full_analysis.get("peripheral_info")),
                "usefulness": "Medium - enhanced peripheral detection and configuration",
                "data": full_analysis.get("peripheral_info", {}),
            },
        },
        "missing_but_potentially_useful": {
            "bootloader_info": "Critical for upload protocol selection - may need external sources",
            "maximum_frequencies": "Important for performance validation - may be in electrical specs",
            "temperature_ranges": "Useful for environmental specifications",
            "power_consumption": "Useful for low-power design validation",
        },
        "all_available_elements": full_analysis.get("all_elements", {}),
    }

    return platformio_useful


if __name__ == "__main__":
    atdf_file_path = r"c:\Users\scelles\git\github\s-celles\atpack-ts-viewer\public\atpacks\Atmel.ATmega_DFP.2.2.509_dir_atpack\atdf\ATmega16.atdf"

    print("=== ATMEL AtPack Analysis for PlatformIO Board Definitions ===\n")

    analysis = analyze_atmel_for_platformio(atdf_file_path)

    print("Currently Extracted by Our Parser:")
    for item, status in analysis["currently_extracted_by_our_parser"].items():
        print(f"  ✓ {item.replace('_', ' ').title()}: {status}")

    print("\nAdditionally Useful Information Found:")
    for category, info in analysis["additionally_useful_for_platformio"].items():
        found_indicator = "✓" if info["found"] else "✗"
        print(
            f"  {found_indicator} {category.replace('_', ' ').title()}: {info['usefulness']}"
        )
        if info["found"] and info["data"]:
            print(f"    Sample data keys: {list(info['data'].keys())}")

    print("\nMissing but Potentially Useful:")
    for item, description in analysis["missing_but_potentially_useful"].items():
        print(f"  - {item.replace('_', ' ').title()}: {description}")

    print("\nAll XML Elements Found in ATDF File:")
    elements = analysis["all_available_elements"]
    for element_type in sorted(elements.keys()):
        print(f"  - {element_type} ({len(elements[element_type])} occurrences)")

    print("\nDetailed analysis saved to 'atmel_analysis.json'")

    # Save detailed analysis to file
    with open("atmel_analysis.json", "w") as f:
        json.dump(analysis, f, indent=2)
