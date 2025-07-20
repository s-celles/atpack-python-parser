"""Microchip PIC parser."""

from typing import Dict, List, Optional

from lxml import etree

from .exceptions import ParseError
from .models import (
    ArchitectureInfo,
    ConfigWord,
    DebugCapabilities,
    Device,
    DeviceFamily,
    DeviceSignature,
    Interrupt,
    MemorySegment,
    Module,
    OscillatorConfig,
    PinFunction,
    PinInfo,
    PowerSpecification,
    ProgrammingInterface,
    Register,
    RegisterBitfield,
    RegisterGroup,
)
from .xml_utils import XmlParser


class PicParser:
    """Parser for Microchip PIC files."""

    def __init__(self, xml_content: str):
        """Initialize with XML content."""
        self.parser = XmlParser(xml_content)

    def parse_device(self, device_name: Optional[str] = None) -> Device:
        """Parse device information from PIC file."""
        # Get device element - try with and without namespace
        if device_name:
            device_elements = self.parser.xpath(f'//edc:PIC[@edc:name="{device_name}"]')
            if not device_elements:
                device_elements = self.parser.xpath(
                    f'//*[local-name()="PIC" and @*[local-name()="name"]="{device_name}"]'
                )
        else:
            device_elements = self.parser.xpath("//edc:PIC")
            if not device_elements:
                device_elements = self.parser.xpath('//*[local-name()="PIC"]')

        if not device_elements:
            if device_name:
                raise ParseError(f"Device '{device_name}' not found in PIC file")
            else:
                raise ParseError("No device found in PIC file")

        device_element = device_elements[0]

        # Extract device name - try namespace and local name approaches
        name = (
            self.parser.get_attr(device_element, "name")
            or self.parser.get_attr(device_element, "{http://crownking/edc}name")
            or device_element.get("{http://crownking/edc}name")
            or ""
        )

        if not name and device_name:
            name = device_name

        # Extract series from architecture attribute
        arch = self.parser.get_attr(device_element, "arch", "")
        series = None
        if arch:
            # Convert arch like "16xxxx" to "PIC16"
            if arch.startswith("16"):
                series = "PIC16"
            elif arch.startswith("18"):
                series = "PIC18"
            elif arch.startswith("12"):
                series = "PIC12"
            elif arch.startswith("10"):
                series = "PIC10"
            else:
                series = f"PIC{arch}"

        device = Device(
            name=name, family=DeviceFamily.PIC, architecture="PIC", series=series
        )

        # Parse memory segments
        device.memory_segments = self._parse_memory_segments(device_element)

        # Parse modules/peripherals
        device.modules = self._parse_modules(device_element)

        # Parse configuration words
        device.config_words = self._parse_config_words(device_element)

        # Parse interrupts
        device.interrupts = self._parse_interrupts(device_element)

        # Parse signatures/device IDs
        device.signatures = self._parse_signatures(device_element)

        # Additional metadata
        device.metadata = self._extract_metadata(device_element)

        # Parse additional PlatformIO-useful information
        device.power_specs = self._parse_power_specifications(device_element)
        device.oscillator_configs = self._parse_oscillator_configurations(
            device_element
        )
        device.programming_interface = self._parse_programming_interface(device_element)
        device.pinout = self._parse_pinout_info(device_element)
        device.debug_capabilities = self._parse_debug_capabilities(device_element)
        device.architecture_info = self._parse_architecture_info(device_element)
        device.detected_peripherals = self._detect_peripherals(device_element)

        return device

    def _parse_memory_segments(
        self, device_element: etree._Element
    ) -> List[MemorySegment]:
        """Parse memory segments from PIC device."""
        segments = []

        # Parse ProgramSpace - contains CodeSector elements for program memory
        program_space = self.parser.xpath(
            './/edc:ProgramSpace | .//*[local-name()="ProgramSpace"]', device_element
        )
        for ps in program_space:
            # Parse CodeSector elements
            code_sectors = self.parser.xpath(
                './/edc:CodeSector | .//*[local-name()="CodeSector"]', ps
            )
            for cs in code_sectors:
                start = self.parser.get_attr_hex(cs, "beginaddr", 0)
                end = self.parser.get_attr_hex(cs, "endaddr", 0)
                name = self.parser.get_attr(cs, "sectionname", "PROG")

                if end > start:
                    size = end - start
                    segments.append(
                        MemorySegment(
                            name=name,
                            start=start,
                            size=size,
                            type="program",
                            address_space="program",
                        )
                    )

        # Parse DataSpace - contains SFRDataSector and other data memory
        data_space = self.parser.xpath(
            './/edc:DataSpace | .//*[local-name()="DataSpace"]', device_element
        )
        for ds in data_space:
            # Parse SFRDataSector elements
            sfr_sectors = self.parser.xpath(
                './/edc:SFRDataSector | .//*[local-name()="SFRDataSector"]', ds
            )
            for sfr in sfr_sectors:
                start = self.parser.get_attr_hex(sfr, "beginaddr", 0)
                end = self.parser.get_attr_hex(sfr, "endaddr", 0)
                bank = self.parser.get_attr(sfr, "bank", "0")

                if end > start:
                    size = end - start
                    segments.append(
                        MemorySegment(
                            name=f"SFR_BANK{bank}",
                            start=start,
                            size=size,
                            type="sfr",
                            address_space="data",
                        )
                    )

            # Parse general DataSector elements
            data_sectors = self.parser.xpath(
                './/edc:DataSector | .//*[local-name()="DataSector"]', ds
            )
            for ds_elem in data_sectors:
                start = self.parser.get_attr_hex(ds_elem, "beginaddr", 0)
                end = self.parser.get_attr_hex(ds_elem, "endaddr", 0)
                name = self.parser.get_attr(ds_elem, "sectionname", "DATA")

                if end > start:
                    size = end - start
                    segments.append(
                        MemorySegment(
                            name=name,
                            start=start,
                            size=size,
                            type="data",
                            address_space="data",
                        )
                    )

        # Parse EEDataSpace for EEPROM
        ee_space = self.parser.xpath(
            './/edc:EEDataSpace | .//*[local-name()="EEDataSpace"]', device_element
        )
        for es in ee_space:
            ee_sectors = self.parser.xpath(
                './/edc:EESector | .//*[local-name()="EESector"]', es
            )
            for ee in ee_sectors:
                start = self.parser.get_attr_hex(ee, "beginaddr", 0)
                end = self.parser.get_attr_hex(ee, "endaddr", 0)

                if end > start:
                    size = end - start
                    segments.append(
                        MemorySegment(
                            name="EEPROM",
                            start=start,
                            size=size,
                            type="eeprom",
                            address_space="eeprom",
                        )
                    )

        return segments

    def _parse_modules(self, device_element: etree._Element) -> List[Module]:
        """Parse modules from PIC device SFR definitions."""
        modules = []

        # Find all SFRDataSector elements which contain the register definitions
        sfr_data_sectors = self.parser.xpath(
            './/edc:SFRDataSector | .//*[local-name()="SFRDataSector"]', device_element
        )

        for sfr_sector in sfr_data_sectors:
            bank = self.parser.get_attr(sfr_sector, "bank", "0")

            # Get all SFRDef elements in this sector
            sfr_defs = self.parser.xpath(
                './/edc:SFRDef | .//*[local-name()="SFRDef"]', sfr_sector
            )

            if sfr_defs:
                # Parse all registers in this bank
                all_registers = []
                for sfr_def in sfr_defs:
                    registers = self._parse_sfr_registers(sfr_def)
                    all_registers.extend(registers)

                if all_registers:
                    # Group registers by module - use bank as the module name for now
                    module_name = f"BANK{bank}"
                    register_group = RegisterGroup(
                        name=f"SFR_BANK{bank}",
                        caption=f"SFR Bank {bank}",
                        registers=all_registers,
                    )

                    module = Module(
                        name=module_name,
                        caption=f"Register Bank {bank}",
                        register_groups=[register_group],
                    )

                    modules.append(module)

        # Also look for NMMR (Non-Memory Mapped Registers)
        nmmr_places = self.parser.xpath(
            './/edc:NMMRPlace | .//*[local-name()="NMMRPlace"]', device_element
        )
        for nmmr_place in nmmr_places:
            sfr_defs = self.parser.xpath(
                './/edc:SFRDef | .//*[local-name()="SFRDef"]', nmmr_place
            )

            if sfr_defs:
                all_registers = []
                for sfr_def in sfr_defs:
                    registers = self._parse_sfr_registers(sfr_def)
                    all_registers.extend(registers)

                if all_registers:
                    register_group = RegisterGroup(
                        name="CORE", caption="Core Registers", registers=all_registers
                    )

                    module = Module(
                        name="CORE",
                        caption="Core Registers",
                        register_groups=[register_group],
                    )

                    modules.append(module)

        return modules

    def _parse_sfr_registers(self, sfr_def: etree._Element) -> List[Register]:
        """Parse a single register from an SFRDef element."""
        registers = []

        # Get basic register information
        reg_name = self.parser.get_attr(sfr_def, "name", "UNKNOWN")
        reg_addr = self.parser.get_attr_hex(sfr_def, "_addr", 0)
        access_pattern = self.parser.get_attr(sfr_def, "access", "nnnnnnnn")
        width = self.parser.get_attr_hex(sfr_def, "nzwidth", 0x8)
        description = self.parser.get_attr(sfr_def, "desc", "")

        # Parse bitfields from SFRFieldDef elements in SFRMode sections
        bitfields = []
        sfr_modes = self.parser.xpath(
            './/edc:SFRMode | .//*[local-name()="SFRMode"]', sfr_def
        )

        # Process DS.0 mode first (main definitions with proper masks)
        main_bitfields = {}
        for mode in sfr_modes:
            mode_id = self.parser.get_attr(mode, "id", "")
            if mode_id == "DS.0":
                field_defs = self.parser.xpath(
                    './/edc:SFRFieldDef | .//*[local-name()="SFRFieldDef"]', mode
                )

                current_bit_pos = 0  # Track sequential bit position for DS.0 mode

                for field_def in field_defs:
                    field_name = self.parser.get_attr(field_def, "name", "")
                    field_mask = self.parser.get_attr_hex(field_def, "mask", 0)
                    field_width = self.parser.get_attr_hex(field_def, "nzwidth", 1)
                    field_desc = self.parser.get_attr(field_def, "desc", "")

                    if field_name and field_mask > 0:
                        # For DS.0 mode, calculate bit position from mask
                        # But for single-bit masks (0x1), use sequential positioning
                        if field_mask == 0x1:
                            # Single bit field - use current position and calculate proper mask
                            bit_pos = current_bit_pos
                            actual_mask = 1 << bit_pos
                        else:
                            # Multi-bit field - use the provided mask
                            bit_pos = 0
                            temp_mask = field_mask
                            while temp_mask and (temp_mask & 1) == 0:
                                bit_pos += 1
                                temp_mask >>= 1
                            actual_mask = field_mask

                        bitfield = RegisterBitfield(
                            name=field_name,
                            caption=field_desc or field_name,
                            mask=actual_mask,
                            bit_offset=bit_pos,
                            bit_width=field_width,
                        )
                        bitfields.append(bitfield)
                        main_bitfields[field_name] = bitfield

                        current_bit_pos += field_width

        # Process other modes (like LT.0) for individual bit aliases
        for mode in sfr_modes:
            mode_id = self.parser.get_attr(mode, "id", "")
            if mode_id != "DS.0":  # Skip the main mode we already processed
                field_defs = self.parser.xpath(
                    './/edc:SFRFieldDef | .//*[local-name()="SFRFieldDef"]', mode
                )
                adjust_points = self.parser.xpath(
                    './/edc:AdjustPoint | .//*[local-name()="AdjustPoint"]', mode
                )

                current_bit_pos = 0  # Track current bit position for this mode

                # Build a list of all elements (fields and adjust points) in document order
                mode_elements = []
                for child in mode:
                    if child.tag.endswith("SFRFieldDef") or "SFRFieldDef" in child.tag:
                        mode_elements.append(("field", child))
                    elif (
                        child.tag.endswith("AdjustPoint") or "AdjustPoint" in child.tag
                    ):
                        mode_elements.append(("adjust", child))

                for elem_type, elem in mode_elements:
                    if elem_type == "adjust":
                        # Handle AdjustPoint to skip bits
                        offset = self.parser.get_attr_hex(elem, "offset", 1)
                        current_bit_pos += offset
                    elif elem_type == "field":
                        field_name = self.parser.get_attr(elem, "name", "")
                        field_mask = self.parser.get_attr_hex(elem, "mask", 0)
                        field_width = self.parser.get_attr_hex(elem, "nzwidth", 1)
                        field_desc = self.parser.get_attr(elem, "desc", "")

                        if field_name and field_mask > 0:
                            # For individual bit aliases, use sequential positioning
                            # but only if we don't already have this field from DS.0 mode
                            if field_name not in main_bitfields:
                                # Create proper mask based on current bit position
                                actual_mask = (
                                    field_mask << current_bit_pos
                                    if field_mask == 1
                                    else field_mask
                                )

                                bitfield = RegisterBitfield(
                                    name=field_name,
                                    caption=field_desc or field_name,
                                    mask=actual_mask,
                                    bit_offset=current_bit_pos,
                                    bit_width=field_width,
                                )
                                bitfields.append(bitfield)

                            current_bit_pos += field_width

        # Create the register
        if reg_addr > 0 or reg_name in [
            "WREG",
            "INDF",
        ]:  # Include special registers at address 0
            # Determine access mode from access pattern
            access_mode = "RW"  # Default
            if "r" in access_pattern.lower() and "w" not in access_pattern.lower():
                access_mode = "R"
            elif "w" in access_pattern.lower() and "r" not in access_pattern.lower():
                access_mode = "W"
            elif "-" in access_pattern:
                access_mode = "R"  # Read-only for unmapped bits

            register = Register(
                name=reg_name,
                caption=description or reg_name,
                offset=reg_addr,
                size=width // 8 if width >= 8 else 1,
                access=access_mode,
                bitfields=bitfields,
            )
            registers.append(register)

        return registers

    def _parse_config_words(self, device_element: etree._Element) -> List[ConfigWord]:
        """Parse configuration words from PIC device."""
        config_words = []

        # Look for configuration word definitions
        config_defs = self.parser.xpath(
            './/edc:ConfigDef | .//*[local-name()="ConfigDef"]', device_element
        )

        for config_def in config_defs:
            # Parse individual configuration words
            config_elements = self.parser.xpath(
                './/edc:ConfigWord | .//*[local-name()="ConfigWord"]', config_def
            )

            for config_elem in config_elements:
                addr = self.parser.get_attr_hex(config_elem, "addr", 0)
                default_val = self.parser.get_attr_hex(config_elem, "default", 0)
                mask = self.parser.get_attr_hex(config_elem, "mask", 0xFFFF)
                name = self.parser.get_attr(config_elem, "name", f"CONFIG{addr:04X}")

                # Parse configuration fields
                bitfields = []
                config_fields = self.parser.xpath(
                    './/edc:ConfigField | .//*[local-name()="ConfigField"]', config_elem
                )

                for field in config_fields:
                    field_name = self.parser.get_attr(field, "name", "")
                    field_mask = self.parser.get_attr_hex(field, "mask", 0)
                    field_desc = self.parser.get_attr(field, "desc", "")

                    if field_name and field_mask:
                        bit_offset, bit_width = self._calculate_bit_range(field_mask)

                        # Parse field values
                        values = {}
                        field_values = self.parser.xpath(
                            './/edc:ConfigValue | .//*[local-name()="ConfigValue"]',
                            field,
                        )
                        for value_elem in field_values:
                            val_name = self.parser.get_attr(value_elem, "name", "")
                            val_value = self.parser.get_attr_hex(value_elem, "value", 0)
                            val_desc = self.parser.get_attr(value_elem, "desc", "")

                            if val_name:
                                values[val_value] = val_desc or val_name

                        bitfield = RegisterBitfield(
                            name=field_name,
                            caption=field_desc or field_name,
                            mask=field_mask,
                            bit_offset=bit_offset,
                            bit_width=bit_width,
                            values=values if values else None,
                        )
                        bitfields.append(bitfield)

                if addr > 0:
                    config_words.append(
                        ConfigWord(
                            name=name,
                            address=addr,
                            default_value=default_val,
                            mask=mask,
                            bitfields=bitfields,
                        )
                    )

        return sorted(config_words, key=lambda x: x.address)

    def _parse_interrupts(self, device_element: etree._Element) -> List[Interrupt]:
        """Parse interrupt information from PIC device."""
        interrupts = []

        # Look for explicit interrupt definitions first
        int_defs = self.parser.xpath(
            './/edc:InterruptDef | .//*[local-name()="InterruptDef"]', device_element
        )

        for int_def in int_defs:
            int_elements = self.parser.xpath(
                './/edc:Interrupt | .//*[local-name()="Interrupt"]', int_def
            )

            for int_elem in int_elements:
                name = self.parser.get_attr(int_elem, "name", "")
                vector = self.parser.get_attr_int(int_elem, "vector", 0)
                desc = self.parser.get_attr(int_elem, "desc", "")

                if name:
                    interrupts.append(
                        Interrupt(index=vector, name=name, caption=desc or name)
                    )

        # If no explicit interrupts found, try to infer from common PIC interrupt registers
        if not interrupts:
            # Look for PIE (Peripheral Interrupt Enable) registers to infer interrupts
            sfr_data_sectors = self.parser.xpath(
                './/edc:SFRDataSector | .//*[local-name()="SFRDataSector"]',
                device_element,
            )

            interrupt_sources = set()

            for sfr_sector in sfr_data_sectors:
                sfr_defs = self.parser.xpath(
                    './/edc:SFRDef | .//*[local-name()="SFRDef"]', sfr_sector
                )

                for sfr_def in sfr_defs:
                    reg_name = self.parser.get_attr(sfr_def, "name", "")

                    # Check for interrupt-related registers
                    if reg_name in ["PIE1", "PIE2", "PIE3", "PIE4", "INTCON"]:
                        # Parse the bitfields to find interrupt enable bits
                        sfr_modes = self.parser.xpath(
                            './/edc:SFRMode | .//*[local-name()="SFRMode"]', sfr_def
                        )

                        for mode in sfr_modes:
                            field_defs = self.parser.xpath(
                                './/edc:SFRFieldDef | .//*[local-name()="SFRFieldDef"]',
                                mode,
                            )

                            for field_def in field_defs:
                                field_name = self.parser.get_attr(field_def, "name", "")

                                # Common PIC interrupt enable bit patterns
                                if (
                                    field_name.endswith("IE")
                                    or field_name.endswith("EN")
                                    or field_name
                                    in ["GIE", "PEIE", "T0IE", "INTE", "RBIE"]
                                ):
                                    # Map enable bit to interrupt name
                                    int_name = field_name.replace("IE", "").replace(
                                        "EN", ""
                                    )
                                    if int_name == "GI":
                                        int_name = "GLOBAL"
                                    elif int_name == "PEI":
                                        int_name = "PERIPHERAL"
                                    elif int_name == "T0I":
                                        int_name = "TIMER0"
                                    elif int_name == "INT":
                                        int_name = "EXTERNAL"
                                    elif int_name == "RBI":
                                        int_name = "PORTB_CHANGE"

                                    if int_name:
                                        interrupt_sources.add(int_name)

            # Create interrupt objects from the discovered sources
            for i, int_name in enumerate(sorted(interrupt_sources)):
                interrupts.append(
                    Interrupt(
                        index=i, name=f"{int_name}_INT", caption=f"{int_name} Interrupt"
                    )
                )

        return sorted(interrupts, key=lambda x: x.index)

    def _parse_signatures(
        self, device_element: etree._Element
    ) -> List[DeviceSignature]:
        """Parse device signatures from PIC device."""
        signatures = []

        # Look for DeviceIDSector elements
        device_id_sectors = self.parser.xpath(
            './/edc:DeviceIDSector | .//*[local-name()="DeviceIDSector"]',
            device_element,
        )

        for device_id_sector in device_id_sectors:
            addr = self.parser.get_attr_hex(device_id_sector, "beginaddr", 0)
            value = self.parser.get_attr_hex(device_id_sector, "value", 0)
            mask = self.parser.get_attr_hex(device_id_sector, "mask", 0xFFFF)
            region_id = self.parser.get_attr(device_id_sector, "regionid", "devid")

            if value > 0:
                signatures.append(
                    DeviceSignature(
                        address=addr,
                        value=value,
                        mask=mask,
                        name=f"DEVID_{region_id.upper()}",
                    )
                )

        return signatures

    def _extract_metadata(self, device_element: etree._Element) -> Dict[str, any]:
        """Extract additional device metadata."""
        metadata = {}

        # Device specifications
        specs = self.parser.xpath(
            './/edc:DeviceSpecs | .//*[local-name()="DeviceSpecs"]', device_element
        )
        for spec in specs:
            # Stack depth
            stack_depth = self.parser.get_attr_int(spec, "stackdepth", 0)
            if stack_depth > 0:
                metadata["stack_depth"] = stack_depth

            # CPU architecture details
            cpu_arch = self.parser.get_attr(spec, "arch", "")
            if cpu_arch:
                metadata["cpu_architecture"] = cpu_arch

        # Power specifications
        power_specs = self.parser.xpath(
            './/edc:PowerSpecs | .//*[local-name()="PowerSpecs"]', device_element
        )
        for power_spec in power_specs:
            supply_voltage = self.parser.get_attr(power_spec, "supply", "")
            if supply_voltage:
                metadata["supply_voltage"] = supply_voltage

        return metadata

    def _parse_power_specifications(
        self, device_element: etree._Element
    ) -> Optional[PowerSpecification]:
        """Parse power supply specifications from PIC device."""
        # Look for Power element
        power_elem = device_element.find(
            ".//edc:Power", {"edc": "http://crownking/edc"}
        )
        if power_elem is None:
            power_elem = device_element.find('.//*[local-name()="Power"]')

        if power_elem is None:
            return None

        power_spec = PowerSpecification()

        # High voltage MCLR capability
        has_hv_mclr = self.parser.get_attr(power_elem, "hashighvoltagemclr2", "")
        if has_hv_mclr:
            power_spec.has_high_voltage_mclr = has_hv_mclr.lower() == "true"

        # VDD specifications
        vdd_elem = power_elem.find(".//edc:VDD", {"edc": "http://crownking/edc"})
        if vdd_elem is None:
            vdd_elem = power_elem.find('.//*[local-name()="VDD"]')

        if vdd_elem is not None:
            power_spec.vdd_min = self._parse_float(
                self.parser.get_attr(vdd_elem, "minvoltage", "")
            )
            power_spec.vdd_max = self._parse_float(
                self.parser.get_attr(vdd_elem, "maxvoltage", "")
            )
            power_spec.vdd_nominal = self._parse_float(
                self.parser.get_attr(vdd_elem, "nominalvoltage", "")
            )
            power_spec.vdd_min_default = self._parse_float(
                self.parser.get_attr(vdd_elem, "mindefaultvoltage", "")
            )
            power_spec.vdd_max_default = self._parse_float(
                self.parser.get_attr(vdd_elem, "maxdefaultvoltage", "")
            )

        # VPP specifications (programming voltage)
        vpp_elem = power_elem.find(".//edc:VPP", {"edc": "http://crownking/edc"})
        if vpp_elem is None:
            vpp_elem = power_elem.find('.//*[local-name()="VPP"]')

        if vpp_elem is not None:
            power_spec.vpp_min = self._parse_float(
                self.parser.get_attr(vpp_elem, "minvoltage", "")
            )
            power_spec.vpp_max = self._parse_float(
                self.parser.get_attr(vpp_elem, "maxvoltage", "")
            )
            power_spec.vpp_default = self._parse_float(
                self.parser.get_attr(vpp_elem, "defaultvoltage", "")
            )

        # Return None if no meaningful data was found
        if not any(
            [
                power_spec.vdd_min,
                power_spec.vdd_max,
                power_spec.vdd_nominal,
                power_spec.vpp_min,
                power_spec.vpp_max,
                power_spec.vpp_default,
            ]
        ):
            return None

        return power_spec

    def _parse_oscillator_configurations(
        self, device_element: etree._Element
    ) -> List[OscillatorConfig]:
        """Parse oscillator configuration options from config words."""
        osc_configs = []

        # Look for configuration words with oscillator settings
        config_sectors = device_element.findall(
            ".//edc:ConfigFuseSector", {"edc": "http://crownking/edc"}
        )
        if not config_sectors:
            config_sectors = device_element.findall(
                './/*[local-name()="ConfigFuseSector"]'
            )

        for sector in config_sectors:
            dcr_defs = sector.findall(".//edc:DCRDef", {"edc": "http://crownking/edc"})
            if not dcr_defs:
                dcr_defs = sector.findall('.//*[local-name()="DCRDef"]')

            for dcr in dcr_defs:
                modes = dcr.findall(".//edc:DCRMode", {"edc": "http://crownking/edc"})
                if not modes:
                    modes = dcr.findall('.//*[local-name()="DCRMode"]')

                for mode in modes:
                    fields = mode.findall(
                        ".//edc:DCRFieldDef", {"edc": "http://crownking/edc"}
                    )
                    if not fields:
                        fields = mode.findall('.//*[local-name()="DCRFieldDef"]')

                    for field in fields:
                        field_name = self.parser.get_attr(field, "name", "")

                        # Check if this is an oscillator-related field
                        if "FOSC" in field_name or "OSC" in field_name.upper():
                            field_desc = self.parser.get_attr(field, "desc", "")
                            field_mask = self.parser.get_attr(field, "mask", "")

                            # Get semantic options for this field
                            semantics = field.findall(
                                ".//edc:DCRFieldSemantic",
                                {"edc": "http://crownking/edc"},
                            )
                            if not semantics:
                                semantics = field.findall(
                                    './/*[local-name()="DCRFieldSemantic"]'
                                )

                            for semantic in semantics:
                                osc_name = self.parser.get_attr(semantic, "cname", "")
                                osc_desc = self.parser.get_attr(semantic, "desc", "")
                                when_cond = self.parser.get_attr(semantic, "when", "")

                                if osc_name:
                                    # Look for legacy aliases
                                    legacy_alias = None
                                    aliases = semantic.findall(
                                        ".//edc:LegacyAlias",
                                        {"edc": "http://crownking/edc"},
                                    )
                                    if not aliases:
                                        aliases = semantic.findall(
                                            './/*[local-name()="LegacyAlias"]'
                                        )

                                    if aliases:
                                        legacy_alias = self.parser.get_attr(
                                            aliases[0], "cname", ""
                                        )

                                    osc_config = OscillatorConfig(
                                        name=osc_name,
                                        description=osc_desc or osc_name,
                                        config_mask=field_mask,
                                        when_condition=when_cond,
                                        c_name=osc_name,
                                        legacy_alias=legacy_alias,
                                    )
                                    osc_configs.append(osc_config)

        return osc_configs

    def _parse_programming_interface(
        self, device_element: etree._Element
    ) -> Optional[ProgrammingInterface]:
        """Parse programming interface specifications."""
        # Look for Programming element
        prog_elem = device_element.find(
            ".//edc:Programming", {"edc": "http://crownking/edc"}
        )
        if prog_elem is None:
            prog_elem = device_element.find('.//*[local-name()="Programming"]')

        if prog_elem is None:
            return None

        prog_interface = ProgrammingInterface()

        # Basic programming attributes
        prog_interface.erase_algorithm = self.parser.get_attr(
            prog_elem, "erasealgo", ""
        )
        prog_interface.memory_technology = self.parser.get_attr(
            prog_elem, "memtech", ""
        )

        has_lvp = self.parser.get_attr(prog_elem, "haslvp2", "")
        if has_lvp:
            prog_interface.has_low_voltage_programming = has_lvp.lower() == "true"

        lvp_thresh = self._parse_float(self.parser.get_attr(prog_elem, "lvpthresh", ""))
        if lvp_thresh:
            prog_interface.low_voltage_threshold = lvp_thresh

        tries = self._parse_int(self.parser.get_attr(prog_elem, "tries", ""))
        if tries:
            prog_interface.programming_tries = tries

        has_row_erase = self.parser.get_attr(prog_elem, "hasrowerasecmd", "")
        if has_row_erase:
            prog_interface.has_row_erase_command = has_row_erase.lower() == "true"

        # Parse programming wait times
        wait_times = prog_elem.findall(
            ".//edc:ProgrammingWaitTime", {"edc": "http://crownking/edc"}
        )
        if not wait_times:
            wait_times = prog_elem.findall('.//*[local-name()="ProgrammingWaitTime"]')

        for wait_elem in wait_times:
            prog_op = self.parser.get_attr(wait_elem, "progop", "")
            time_val = self._parse_int(self.parser.get_attr(wait_elem, "time", ""))
            time_units = self.parser.get_attr(wait_elem, "timeunits", "")

            if prog_op and time_val:
                prog_interface.wait_times[prog_op] = {
                    "time": time_val,
                    "units": time_units or "us",
                }

        # Parse programming row sizes
        row_sizes = prog_elem.findall(
            ".//edc:ProgrammingRowSize", {"edc": "http://crownking/edc"}
        )
        if not row_sizes:
            row_sizes = prog_elem.findall('.//*[local-name()="ProgrammingRowSize"]')

        for row_elem in row_sizes:
            prog_op = self.parser.get_attr(row_elem, "progop", "")
            nz_size = self._parse_int(self.parser.get_attr(row_elem, "nzsize", ""))

            if prog_op and nz_size:
                prog_interface.row_sizes[prog_op] = nz_size

        return prog_interface

    def _parse_pinout_info(self, device_element: etree._Element) -> List[PinInfo]:
        """Parse pinout and pin functionality information."""
        pins = []

        # Look for PinList element
        pin_list = device_element.find(
            ".//edc:PinList", {"edc": "http://crownking/edc"}
        )
        if pin_list is None:
            pin_list = device_element.find('.//*[local-name()="PinList"]')

        if pin_list is None:
            return pins

        # Get PPS (Peripheral Pin Select) flavor
        pps_flavor = self.parser.get_attr(pin_list, "ppsflavor", "")

        pin_elements = pin_list.findall(".//edc:Pin", {"edc": "http://crownking/edc"})
        if not pin_elements:
            pin_elements = pin_list.findall('.//*[local-name()="Pin"]')

        for pin_num, pin_elem in enumerate(pin_elements, 1):
            pin_info = PinInfo(physical_pin=pin_num)

            # Get virtual pins (pin functions)
            virtual_pins = pin_elem.findall(
                ".//edc:VirtualPin", {"edc": "http://crownking/edc"}
            )
            if not virtual_pins:
                virtual_pins = pin_elem.findall('.//*[local-name()="VirtualPin"]')

            functions = []
            primary_func = None

            for vpin in virtual_pins:
                func_name = self.parser.get_attr(vpin, "name", "")
                if func_name:
                    func = PinFunction(name=func_name)
                    functions.append(func)

                    if primary_func is None:
                        primary_func = func_name

                    # Categorize pin type
                    if not pin_info.pin_type:
                        if func_name in ["VDD", "VSS"]:
                            pin_info.pin_type = "power"
                        elif func_name in ["MCLR", "VPP"]:
                            pin_info.pin_type = "control"
                        elif func_name.startswith("AN") or "VREF" in func_name:
                            pin_info.pin_type = "analog"
                        elif func_name.startswith("OSC"):
                            pin_info.pin_type = "oscillator"
                        elif func_name.startswith("PGC") or func_name.startswith("PGD"):
                            pin_info.pin_type = "programming"
                        else:
                            pin_info.pin_type = "digital"

            pin_info.primary_function = primary_func
            pin_info.alternative_functions = functions
            pins.append(pin_info)

        return pins

    def _parse_debug_capabilities(
        self, device_element: etree._Element
    ) -> Optional[DebugCapabilities]:
        """Parse debug and hardware tool capabilities."""
        # Look for Breakpoints element
        bp_elem = device_element.find(
            ".//edc:Breakpoints", {"edc": "http://crownking/edc"}
        )
        if bp_elem is None:
            bp_elem = device_element.find('.//*[local-name()="Breakpoints"]')

        if bp_elem is None:
            return None

        debug_caps = DebugCapabilities()

        # Hardware breakpoint count
        hwbp_count = self._parse_int(self.parser.get_attr(bp_elem, "hwbpcount", ""))
        if hwbp_count:
            debug_caps.hardware_breakpoint_count = hwbp_count

        # Data capture capability
        has_data_capture = self.parser.get_attr(bp_elem, "hasdatacapture", "")
        if has_data_capture:
            debug_caps.has_data_capture = has_data_capture.lower() == "true"

        # ID byte
        id_byte = self.parser.get_attr(bp_elem, "idbyte", "")
        if id_byte:
            debug_caps.id_byte = id_byte

        return debug_caps

    def _parse_architecture_info(
        self, device_element: etree._Element
    ) -> Optional[ArchitectureInfo]:
        """Parse device architecture information."""
        arch_info = ArchitectureInfo()

        # Look for InstructionSet element
        instr_elem = device_element.find(
            ".//edc:InstructionSet", {"edc": "http://crownking/edc"}
        )
        if instr_elem is None:
            instr_elem = device_element.find('.//*[local-name()="InstructionSet"]')

        if instr_elem is not None:
            instr_set_id = self.parser.get_attr(instr_elem, "instructionsetid", "")
            if instr_set_id:
                arch_info.instruction_set = instr_set_id

        # Look for MemTraits element for hardware stack info
        mem_traits = device_element.find(
            ".//edc:MemTraits", {"edc": "http://crownking/edc"}
        )
        if mem_traits is None:
            mem_traits = device_element.find('.//*[local-name()="MemTraits"]')

        if mem_traits is not None:
            hwstack = self._parse_int(
                self.parser.get_attr(mem_traits, "hwstackdepth", "")
            )
            if hwstack:
                arch_info.hardware_stack_depth = hwstack

            # Code memory traits for word sizes
            code_traits = mem_traits.find(
                ".//edc:CodeMemTraits", {"edc": "http://crownking/edc"}
            )
            if code_traits is None:
                code_traits = mem_traits.find('.//*[local-name()="CodeMemTraits"]')

            if code_traits is not None:
                word_size = self._parse_int(
                    self.parser.get_attr(code_traits, "wordsize", "")
                )
                if word_size:
                    arch_info.code_word_size = word_size

            # Data memory traits
            data_traits = mem_traits.find(
                ".//edc:DataMemTraits", {"edc": "http://crownking/edc"}
            )
            if data_traits is None:
                data_traits = mem_traits.find('.//*[local-name()="DataMemTraits"]')

            if data_traits is not None:
                word_size = self._parse_int(
                    self.parser.get_attr(data_traits, "wordsize", "")
                )
                if word_size:
                    arch_info.data_word_size = word_size

        # Return None if no meaningful data was found
        if not any(
            [
                arch_info.instruction_set,
                arch_info.hardware_stack_depth,
                arch_info.code_word_size,
                arch_info.data_word_size,
            ]
        ):
            return None

        return arch_info

    def _detect_peripherals(self, device_element: etree._Element) -> List[str]:
        """Detect available peripherals from register definitions."""
        peripherals = set()

        # Extract peripheral info from SFR definitions
        sfr_defs = device_element.findall(
            ".//edc:SFRDef", {"edc": "http://crownking/edc"}
        )
        if not sfr_defs:
            sfr_defs = device_element.findall('.//*[local-name()="SFRDef"]')

        for sfr in sfr_defs:
            name = self.parser.get_attr(sfr, "name", "")
            if name:
                # Identify peripheral type from register name
                name_upper = name.upper()
                if any(
                    name_upper.startswith(timer)
                    for timer in [
                        "TMR",
                        "T0CON",
                        "T1CON",
                        "T2CON",
                        "T3CON",
                        "T4CON",
                        "T5CON",
                    ]
                ):
                    peripherals.add("TIMER")
                elif name_upper.startswith("CCP") or name_upper.startswith("PWM"):
                    peripherals.add("CCP_PWM")
                elif any(
                    name_upper.startswith(adc) for adc in ["ADC", "ADCON", "ADRES"]
                ):
                    peripherals.add("ADC")
                elif any(name_upper.startswith(spi) for spi in ["SSP", "SPI"]):
                    peripherals.add("SPI")
                elif any(
                    name_upper.startswith(uart) for uart in ["USART", "UART", "EUSART"]
                ):
                    peripherals.add("UART")
                elif any(name_upper.startswith(i2c) for i2c in ["I2C", "MSSP"]):
                    peripherals.add("I2C")
                elif name_upper.startswith("CM") or "CMCON" in name_upper:
                    peripherals.add("COMPARATOR")
                elif name_upper in [
                    "PIE1",
                    "PIE2",
                    "PIE3",
                    "PIE4",
                    "PIR1",
                    "PIR2",
                    "PIR3",
                    "PIR4",
                    "INTCON",
                ]:
                    peripherals.add("INTERRUPT_CONTROLLER")
                elif any(
                    name_upper.startswith(gpio) for gpio in ["TRIS", "PORT", "LAT"]
                ):
                    peripherals.add("GPIO")
                elif name_upper.startswith("WDT") or name_upper == "WDTCON":
                    peripherals.add("WATCHDOG")
                elif any(
                    name_upper.startswith(eep) for eep in ["EECON", "EEDATA", "EEADR"]
                ):
                    peripherals.add("EEPROM")
                elif any(name_upper.startswith(osc) for osc in ["OSC", "CLOCK"]):
                    peripherals.add("OSCILLATOR")

        return sorted(list(peripherals))

    def _parse_float(self, value_str: str) -> Optional[float]:
        """Parse a string to float, return None if invalid."""
        if not value_str:
            return None
        try:
            return float(value_str)
        except (ValueError, TypeError):
            return None

    def _parse_int(self, value_str: str) -> Optional[int]:
        """Parse a string to int, return None if invalid."""
        if not value_str:
            return None
        try:
            return int(value_str)
        except (ValueError, TypeError):
            return None

    # ...existing methods...
