#!/usr/bin/env python3
"""
Comprehensive analysis of PIC AtPack files for PlatformIO board definition insights.

This script examines PIC AtPack files to identify what additional information
(beyond what we currently extract) could be useful for PlatformIO board definitions.
"""

import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List


class PicAtPackAnalyzer:
    """Analyzer for identifying useful PIC AtPack information for PlatformIO."""

    def __init__(self, pic_file_path: str):
        self.pic_file_path = Path(pic_file_path)
        self.tree = ET.parse(pic_file_path)
        self.root = self.tree.getroot()

        # Define namespace map for PIC files
        self.ns = {"edc": "http://crownking/edc"}

    def analyze_all_information(self) -> Dict[str, Any]:
        """Analyze all available information in the PIC file."""
        analysis = {
            "file_info": self._analyze_file_info(),
            "device_info": self._analyze_device_info(),
            "power_info": self._analyze_power_info(),
            "programming_info": self._analyze_programming_info(),
            "memory_architecture": self._analyze_memory_architecture(),
            "pinout_info": self._analyze_pinout_info(),
            "oscillator_config": self._analyze_oscillator_config(),
            "peripherals": self._analyze_peripherals(),
            "interrupt_system": self._analyze_interrupt_system(),
            "debug_features": self._analyze_debug_features(),
            "electrical_specs": self._analyze_electrical_specs(),
            "packaging_info": self._analyze_packaging_info(),
            "clock_info": self._analyze_clock_info(),
            "all_elements": self._catalog_all_elements(),
        }
        return analysis

    def _analyze_file_info(self) -> Dict[str, Any]:
        """Analyze basic file and device identification info."""
        info = {}

        # Root element attributes
        for attr, value in self.root.attrib.items():
            clean_attr = attr.replace("{http://crownking/edc}", "edc:")
            info[clean_attr] = value

        return info

    def _analyze_device_info(self) -> Dict[str, Any]:
        """Analyze device-specific information."""
        info = {}

        # Look for processor/architecture info
        arch_def = self.root.find(".//edc:ArchDef", self.ns)
        if arch_def is not None:
            info["architecture"] = {}
            for attr, value in arch_def.attrib.items():
                clean_attr = attr.replace("{http://crownking/edc}", "edc:")
                info["architecture"][clean_attr] = value

        # Memory traits
        mem_traits = self.root.find(".//edc:MemTraits", self.ns)
        if mem_traits is not None:
            info["memory_traits"] = {}
            for attr, value in mem_traits.attrib.items():
                clean_attr = attr.replace("{http://crownking/edc}", "edc:")
                info["memory_traits"][clean_attr] = value

        # Instruction set
        instr_set = self.root.find(".//edc:InstructionSet", self.ns)
        if instr_set is not None:
            info["instruction_set"] = {}
            for attr, value in instr_set.attrib.items():
                clean_attr = attr.replace("{http://crownking/edc}", "edc:")
                info["instruction_set"][clean_attr] = value

        return info

    def _analyze_power_info(self) -> Dict[str, Any]:
        """Analyze power supply and voltage information."""
        power_info = {}

        power_elem = self.root.find(".//edc:Power", self.ns)
        if power_elem is not None:
            power_info["power_attributes"] = {}
            for attr, value in power_elem.attrib.items():
                clean_attr = attr.replace("{http://crownking/edc}", "edc:")
                power_info["power_attributes"][clean_attr] = value

            # VDD info
            vdd_elem = power_elem.find(".//edc:VDD", self.ns)
            if vdd_elem is not None:
                power_info["vdd"] = {}
                for attr, value in vdd_elem.attrib.items():
                    clean_attr = attr.replace("{http://crownking/edc}", "edc:")
                    power_info["vdd"][clean_attr] = value

            # VPP info (programming voltage)
            vpp_elem = power_elem.find(".//edc:VPP", self.ns)
            if vpp_elem is not None:
                power_info["vpp"] = {}
                for attr, value in vpp_elem.attrib.items():
                    clean_attr = attr.replace("{http://crownking/edc}", "edc:")
                    power_info["vpp"][clean_attr] = value

        return power_info

    def _analyze_programming_info(self) -> Dict[str, Any]:
        """Analyze programming and debug interface information."""
        prog_info = {}

        prog_elem = self.root.find(".//edc:Programming", self.ns)
        if prog_elem is not None:
            prog_info["programming_attributes"] = {}
            for attr, value in prog_elem.attrib.items():
                clean_attr = attr.replace("{http://crownking/edc}", "edc:")
                prog_info["programming_attributes"][clean_attr] = value

            # Programming wait times
            wait_times = []
            for wait_elem in prog_elem.findall(".//edc:ProgrammingWaitTime", self.ns):
                wait_time = {}
                for attr, value in wait_elem.attrib.items():
                    clean_attr = attr.replace("{http://crownking/edc}", "edc:")
                    wait_time[clean_attr] = value
                wait_times.append(wait_time)
            if wait_times:
                prog_info["wait_times"] = wait_times

            # Programming row sizes
            row_sizes = []
            for row_elem in prog_elem.findall(".//edc:ProgrammingRowSize", self.ns):
                row_size = {}
                for attr, value in row_elem.attrib.items():
                    clean_attr = attr.replace("{http://crownking/edc}", "edc:")
                    row_size[clean_attr] = value
                row_sizes.append(row_size)
            if row_sizes:
                prog_info["row_sizes"] = row_sizes

        # Breakpoint capabilities
        bp_elem = self.root.find(".//edc:Breakpoints", self.ns)
        if bp_elem is not None:
            prog_info["breakpoints"] = {}
            for attr, value in bp_elem.attrib.items():
                clean_attr = attr.replace("{http://crownking/edc}", "edc:")
                prog_info["breakpoints"][clean_attr] = value

        return prog_info

    def _analyze_memory_architecture(self) -> Dict[str, Any]:
        """Analyze detailed memory architecture."""
        memory_info = {}

        # Program space analysis
        prog_space = self.root.find(".//edc:ProgramSpace", self.ns)
        if prog_space is not None:
            memory_info["program_space"] = {}

            # Code sectors
            code_sectors = []
            for sector in prog_space.findall(".//edc:CodeSector", self.ns):
                sector_info = {}
                for attr, value in sector.attrib.items():
                    clean_attr = attr.replace("{http://crownking/edc}", "edc:")
                    sector_info[clean_attr] = value
                code_sectors.append(sector_info)
            if code_sectors:
                memory_info["program_space"]["code_sectors"] = code_sectors

            # Configuration sectors
            config_sectors = []
            for sector in prog_space.findall(".//edc:ConfigFuseSector", self.ns):
                sector_info = {}
                for attr, value in sector.attrib.items():
                    clean_attr = attr.replace("{http://crownking/edc}", "edc:")
                    sector_info[clean_attr] = value
                config_sectors.append(sector_info)
            if config_sectors:
                memory_info["program_space"]["config_sectors"] = config_sectors

            # Device ID sectors
            devid_sectors = []
            for sector in prog_space.findall(".//edc:DeviceIDSector", self.ns):
                sector_info = {}
                for attr, value in sector.attrib.items():
                    clean_attr = attr.replace("{http://crownking/edc}", "edc:")
                    sector_info[clean_attr] = value
                devid_sectors.append(sector_info)
            if devid_sectors:
                memory_info["program_space"]["device_id_sectors"] = devid_sectors

        # Data space analysis
        data_space = self.root.find(".//edc:DataSpace", self.ns)
        if data_space is not None:
            memory_info["data_space"] = {}

            # SFR sectors
            sfr_sectors = []
            for sector in data_space.findall(".//edc:SFRDataSector", self.ns):
                sector_info = {}
                for attr, value in sector.attrib.items():
                    clean_attr = attr.replace("{http://crownking/edc}", "edc:")
                    sector_info[clean_attr] = value
                sfr_sectors.append(sector_info)
            if sfr_sectors:
                memory_info["data_space"]["sfr_sectors"] = sfr_sectors

            # GPR sectors
            gpr_sectors = []
            for sector in data_space.findall(".//edc:GPRDataSector", self.ns):
                sector_info = {}
                for attr, value in sector.attrib.items():
                    clean_attr = attr.replace("{http://crownking/edc}", "edc:")
                    sector_info[clean_attr] = value
                gpr_sectors.append(sector_info)
            if gpr_sectors:
                memory_info["data_space"]["gpr_sectors"] = gpr_sectors

        return memory_info

    def _analyze_pinout_info(self) -> Dict[str, Any]:
        """Analyze pinout and pin functionality information."""
        pinout_info = {}

        pin_list = self.root.find(".//edc:PinList", self.ns)
        if pin_list is not None:
            pinout_info["attributes"] = {}
            for attr, value in pin_list.attrib.items():
                clean_attr = attr.replace("{http://crownking/edc}", "edc:")
                pinout_info["attributes"][clean_attr] = value

            pins = []
            for pin_elem in pin_list.findall(".//edc:Pin", self.ns):
                pin_info = {}
                pin_info["attributes"] = {}
                for attr, value in pin_elem.attrib.items():
                    clean_attr = attr.replace("{http://crownking/edc}", "edc:")
                    pin_info["attributes"][clean_attr] = value

                # Virtual pins (alternative functions)
                virtual_pins = []
                for vpin in pin_elem.findall(".//edc:VirtualPin", self.ns):
                    vpin_info = {}
                    for attr, value in vpin.attrib.items():
                        clean_attr = attr.replace("{http://crownking/edc}", "edc:")
                        vpin_info[clean_attr] = value
                    virtual_pins.append(vpin_info)
                if virtual_pins:
                    pin_info["virtual_pins"] = virtual_pins

                pins.append(pin_info)

            if pins:
                pinout_info["pins"] = pins

        return pinout_info

    def _analyze_oscillator_config(self) -> Dict[str, Any]:
        """Analyze oscillator and clock configuration options."""
        osc_info = {}

        # Look for configuration words related to oscillator
        config_sectors = self.root.findall(".//edc:ConfigFuseSector", self.ns)
        for sector in config_sectors:
            dcr_defs = sector.findall(".//edc:DCRDef", self.ns)
            for dcr in dcr_defs:
                modes = dcr.findall(".//edc:DCRMode", self.ns)
                for mode in modes:
                    fields = mode.findall(".//edc:DCRFieldDef", self.ns)
                    for field in fields:
                        field_name = field.get(f"{{{self.ns['edc']}}}name", "")
                        if "FOSC" in field_name or "OSC" in field_name.upper():
                            if "oscillator_configs" not in osc_info:
                                osc_info["oscillator_configs"] = []

                            field_info = {}
                            for attr, value in field.attrib.items():
                                clean_attr = attr.replace(
                                    "{http://crownking/edc}", "edc:"
                                )
                                field_info[clean_attr] = value

                            # Get semantic options
                            semantics = []
                            for semantic in field.findall(
                                ".//edc:DCRFieldSemantic", self.ns
                            ):
                                sem_info = {}
                                for attr, value in semantic.attrib.items():
                                    clean_attr = attr.replace(
                                        "{http://crownking/edc}", "edc:"
                                    )
                                    sem_info[clean_attr] = value
                                semantics.append(sem_info)
                            if semantics:
                                field_info["semantics"] = semantics

                            osc_info["oscillator_configs"].append(field_info)

        return osc_info

    def _analyze_peripherals(self) -> Dict[str, Any]:
        """Analyze peripheral information from register definitions."""
        peripheral_info = {}

        # Extract peripheral info from SFR definitions
        sfr_defs = self.root.findall(".//edc:SFRDef", self.ns)
        peripherals = set()

        for sfr in sfr_defs:
            name = sfr.get(f"{{{self.ns['edc']}}}name", "")
            if name:
                # Try to identify peripheral type from register name
                if name.startswith("TMR"):
                    peripherals.add("TIMER")
                elif name.startswith("CCP"):
                    peripherals.add("CCP")
                elif name.startswith("ADC") or "ADCON" in name or "ADRES" in name:
                    peripherals.add("ADC")
                elif name.startswith("SSP") or name == "SSPCON" or name == "SSPBUF":
                    peripherals.add("SSP")
                elif name.startswith("USART") or name in [
                    "TXREG",
                    "RCREG",
                    "TXSTA",
                    "RCSTA",
                ]:
                    peripherals.add("USART")
                elif name.startswith("CM") or "CMCON" in name:
                    peripherals.add("COMPARATOR")
                elif "INT" in name or name.startswith("PIE") or name.startswith("PIR"):
                    peripherals.add("INTERRUPT")
                elif name.startswith("T0") or name == "OPTION_REG":
                    peripherals.add("TIMER0")
                elif name.startswith("T1"):
                    peripherals.add("TIMER1")
                elif name.startswith("T2"):
                    peripherals.add("TIMER2")

        peripheral_info["detected_peripherals"] = list(peripherals)

        return peripheral_info

    def _analyze_interrupt_system(self) -> Dict[str, Any]:
        """Analyze interrupt system configuration."""
        interrupt_info = {}

        # Look for interrupt-related registers
        interrupt_regs = []
        sfr_defs = self.root.findall(".//edc:SFRDef", self.ns)

        for sfr in sfr_defs:
            name = sfr.get(f"{{{self.ns['edc']}}}name", "")
            if name and (
                "INT" in name or name.startswith("PIE") or name.startswith("PIR")
            ):
                reg_info = {}
                for attr, value in sfr.attrib.items():
                    clean_attr = attr.replace("{http://crownking/edc}", "edc:")
                    reg_info[clean_attr] = value
                interrupt_regs.append(reg_info)

        if interrupt_regs:
            interrupt_info["interrupt_registers"] = interrupt_regs

        return interrupt_info

    def _analyze_debug_features(self) -> Dict[str, Any]:
        """Analyze debugging and hardware tool capabilities."""
        debug_info = {}

        # Breakpoint info (already covered in programming)
        bp_elem = self.root.find(".//edc:Breakpoints", self.ns)
        if bp_elem is not None:
            debug_info["breakpoints"] = {}
            for attr, value in bp_elem.attrib.items():
                clean_attr = attr.replace("{http://crownking/edc}", "edc:")
                debug_info["breakpoints"][clean_attr] = value

        return debug_info

    def _analyze_electrical_specs(self) -> Dict[str, Any]:
        """Analyze electrical specifications and parameters."""
        electrical_info = {}

        # Power specs already covered in _analyze_power_info
        # Look for other electrical parameters in properties
        properties = self.root.findall(".//edc:Property", self.ns)
        electrical_properties = []

        for prop in properties:
            prop_info = {}
            for attr, value in prop.attrib.items():
                clean_attr = attr.replace("{http://crownking/edc}", "edc:")
                prop_info[clean_attr] = value
            electrical_properties.append(prop_info)

        if electrical_properties:
            electrical_info["properties"] = electrical_properties

        return electrical_info

    def _analyze_packaging_info(self) -> Dict[str, Any]:
        """Analyze package and physical form factor information."""
        package_info = {}

        # This information might be in the PDSC file rather than PIC file
        # For now, note that this is typically found elsewhere
        package_info["note"] = "Package information typically found in PDSC file"

        return package_info

    def _analyze_clock_info(self) -> Dict[str, Any]:
        """Analyze clock system information."""
        clock_info = {}

        # Look for clock-related configuration
        # This overlaps with oscillator config but focuses on internal clock systems
        mem_traits = self.root.find(".//edc:MemTraits", self.ns)
        if mem_traits is not None:
            # Hardware stack depth can indicate clock/timing constraints
            hwstack = mem_traits.get(f"{{{self.ns['edc']}}}hwstackdepth", "")
            if hwstack:
                clock_info["hardware_stack_depth"] = hwstack

        return clock_info

    def _catalog_all_elements(self) -> Dict[str, List[str]]:
        """Catalog all XML elements to identify anything we might have missed."""
        elements_catalog = {}

        def traverse_element(elem, path=""):
            tag = elem.tag.replace("{http://crownking/edc}", "edc:")
            current_path = f"{path}/{tag}" if path else tag

            if tag not in elements_catalog:
                elements_catalog[tag] = []

            if current_path not in elements_catalog[tag]:
                elements_catalog[tag].append(current_path)

            for child in elem:
                traverse_element(child, current_path)

        traverse_element(self.root)
        return elements_catalog


def analyze_for_platformio(pic_file: str) -> Dict[str, Any]:
    """Analyze PIC file specifically for PlatformIO board definition insights."""
    analyzer = PicAtPackAnalyzer(pic_file)
    full_analysis = analyzer.analyze_all_information()

    # Identify what would be useful for PlatformIO specifically
    platformio_useful = {
        "currently_extracted_by_our_parser": {
            "device_name": "Yes - from device identification",
            "series": "Yes - from architecture attribute",
            "memory_segments": "Yes - program/data space sectors",
            "registers": "Yes - SFR definitions",
            "interrupts": "Yes - inferred from interrupt registers",
            "config_words": "Yes - from configuration sectors",
            "device_signatures": "Yes - from DeviceID sectors",
        },
        "additionally_useful_for_platformio": {
            "power_supply_specs": {
                "found": bool(full_analysis.get("power_info")),
                "usefulness": "High - for voltage validation and power management",
                "data": full_analysis.get("power_info", {}),
            },
            "oscillator_configurations": {
                "found": bool(full_analysis.get("oscillator_config")),
                "usefulness": "High - for clock configuration in build system",
                "data": full_analysis.get("oscillator_config", {}),
            },
            "programming_interface": {
                "found": bool(full_analysis.get("programming_info")),
                "usefulness": "High - for programmer configuration (ICSP, etc.)",
                "data": full_analysis.get("programming_info", {}),
            },
            "pinout_mapping": {
                "found": bool(full_analysis.get("pinout_info")),
                "usefulness": "Medium-High - for pin mapping and alternative functions",
                "data": full_analysis.get("pinout_info", {}),
            },
            "peripheral_detection": {
                "found": bool(full_analysis.get("peripherals")),
                "usefulness": "Medium - for library compatibility and feature flags",
                "data": full_analysis.get("peripherals", {}),
            },
            "debug_capabilities": {
                "found": bool(full_analysis.get("debug_features")),
                "usefulness": "Medium - for debugger configuration",
                "data": full_analysis.get("debug_features", {}),
            },
            "electrical_properties": {
                "found": bool(full_analysis.get("electrical_specs")),
                "usefulness": "Low-Medium - for design validation",
                "data": full_analysis.get("electrical_specs", {}),
            },
        },
        "missing_but_potentially_useful": {
            "package_types": "Typically found in PDSC - useful for pin count validation",
            "maximum_clock_frequency": "May be in datasheet references - useful for timing",
            "flash_erase_write_cycles": "Useful for bootloader considerations",
            "temperature_ranges": "Useful for environmental specifications",
            "bootloader_info": "Critical for upload protocol selection",
        },
        "all_available_elements": full_analysis.get("all_elements", {}),
    }

    return platformio_useful


if __name__ == "__main__":
    pic_file_path = r"c:\Users\scelles\git\github\s-celles\atpack-ts-viewer\public\atpacks\Microchip.PIC16Fxxx_DFP.1.7.162_dir_atpack\edc\PIC16F876A.PIC"

    print("=== PIC AtPack Analysis for PlatformIO Board Definitions ===\n")

    analysis = analyze_for_platformio(pic_file_path)

    print("Currently Extracted by Our Parser:")
    for item, status in analysis["currently_extracted_by_our_parser"].items():
        print(f"  ✓ {item}: {status}")

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

    print("\nAll XML Elements Found in PIC File:")
    elements = analysis["all_available_elements"]
    for element_type in sorted(elements.keys()):
        print(f"  - {element_type} ({len(elements[element_type])} occurrences)")

    print("\nDetailed analysis saved to 'pic_analysis.json'")

    # Save detailed analysis to file
    with open("pic_analysis.json", "w") as f:
        json.dump(analysis, f, indent=2)
