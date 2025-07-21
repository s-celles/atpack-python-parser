"""ATMEL ATDF parser."""

from typing import Dict, List, Optional

from lxml import etree

from .exceptions import ParseError
from .models import (
    AtmelClockInfo,
    AtmelGpioInfo,
    AtmelPackageVariant,
    AtmelPinoutInfo,
    AtmelProgrammingInterface,
    Device,
    DeviceFamily,
    DeviceSignature,
    ElectricalParameter,
    Fuse,
    FuseBitfield,
    Interrupt,
    MemorySegment,
    MemorySpace,
    Module,
    Register,
    RegisterBitfield,
    RegisterGroup,
)
from .xml_utils import XmlParser


class AtdfParser:
    """Parser for ATMEL ATDF files."""

    def __init__(self, xml_content: str):
        """Initialize with XML content."""
        self.parser = XmlParser(xml_content)

    def parse_device(self, device_name: Optional[str] = None) -> Device:
        """Parse device information from ATDF."""
        # Get device element
        if device_name:
            device_elements = self.parser.xpath(f'//device[@name="{device_name}"]')
        else:
            device_elements = self.parser.xpath("//device")

        if not device_elements:
            if device_name:
                raise ParseError(f"Device '{device_name}' not found in ATDF")
            else:
                raise ParseError("No device found in ATDF")

        device_element = device_elements[0]
        name = self.parser.get_attr(device_element, "name", "")
        architecture = self.parser.get_attr(device_element, "architecture", "")
        family_attr = self.parser.get_attr(device_element, "family", "")

        device = Device(
            name=name,
            family=DeviceFamily.ATMEL,
            architecture=architecture,
            series=family_attr,
        )

        # Parse memory segments
        device.memory_segments = self._parse_memory_segments(device_element)
        device.memory_spaces = self._parse_memory_spaces(device_element)

        # Parse modules/peripherals
        device.modules = self._parse_modules()

        # Parse fuses
        device.fuses = self._parse_fuses()

        # Parse interrupts
        device.interrupts = self._parse_interrupts()

        # Parse signatures
        device.signatures = self._parse_signatures()

        # Parse electrical parameters
        device.electrical_parameters = self._parse_electrical_parameters()

        # Parse additional ATMEL PlatformIO-useful information (use tree root for document-level info)
        device.atmel_package_variants = self._parse_atmel_package_variants(
            self.parser.tree
        )
        device.atmel_pinouts = self._parse_atmel_pinouts(self.parser.tree)
        device.atmel_programming_interfaces = self._parse_atmel_programming_interfaces(
            self.parser.tree
        )
        device.atmel_clock_info = self._parse_atmel_clock_info(self.parser.tree)
        device.atmel_gpio_info = self._parse_atmel_gpio_info(self.parser.tree)

        return device

    def _parse_memory_segments(
        self, device_element: etree._Element
    ) -> List[MemorySegment]:
        """Parse memory segments from device."""
        segments = []

        # Find address spaces
        address_spaces = self.parser.xpath(".//address-space", device_element)
        for addr_space in address_spaces:
            space_name = self.parser.get_attr(addr_space, "name", "")
            space_start = self.parser.get_attr_hex(addr_space, "start", 0)
            space_size = self.parser.get_attr_hex(addr_space, "size", 0)

            # Find memory segments within this address space
            memory_segments = self.parser.xpath(".//memory-segment", addr_space)
            if not memory_segments:
                # Add address space as a segment if no sub-segments
                segments.append(
                    MemorySegment(
                        name=space_name,
                        start=space_start,
                        size=space_size,
                        type=space_name,
                        address_space=space_name,
                    )
                )
            else:
                for mem_seg in memory_segments:
                    seg_name = self.parser.get_attr(mem_seg, "name", "")
                    seg_start = self.parser.get_attr_hex(mem_seg, "start", 0)
                    seg_size = self.parser.get_attr_hex(mem_seg, "size", 0)
                    seg_type = self.parser.get_attr(mem_seg, "type", "")
                    page_size = self.parser.get_attr_hex(mem_seg, "pagesize", 0)

                    segments.append(
                        MemorySegment(
                            name=seg_name,
                            start=seg_start,
                            size=seg_size,
                            type=seg_type,
                            page_size=page_size if page_size > 0 else None,
                            address_space=space_name,
                        )
                    )

        return segments

    def _parse_memory_spaces(self, device_element: etree._Element) -> List[MemorySpace]:
        """Parse hierarchical memory spaces from ATMEL device."""
        memory_spaces = []

        # Find address spaces
        address_spaces = self.parser.xpath(".//address-space", device_element)
        for addr_space in address_spaces:
            space_name = self.parser.get_attr(addr_space, "name", "")
            space_start = self.parser.get_attr_hex(addr_space, "start", 0)
            space_size = self.parser.get_attr_hex(addr_space, "size", 0)

            segments = []

            # Find memory segments within this address space
            memory_segments = self.parser.xpath(".//memory-segment", addr_space)
            if memory_segments:
                for mem_seg in memory_segments:
                    seg_name = self.parser.get_attr(mem_seg, "name", "")
                    seg_start = self.parser.get_attr_hex(mem_seg, "start", 0)
                    seg_size = self.parser.get_attr_hex(mem_seg, "size", 0)
                    seg_type = self.parser.get_attr(mem_seg, "type", "")
                    page_size = self.parser.get_attr_hex(mem_seg, "pagesize", 0)

                    segments.append(
                        MemorySegment(
                            name=seg_name,
                            start=seg_start,
                            size=seg_size,
                            type=seg_type,
                            page_size=page_size if page_size > 0 else None,
                            address_space=space_name,
                            parent_name=space_name,
                            level=1,
                        )
                    )

                # Create memory space with hierarchical segments
                memory_spaces.append(
                    MemorySpace(
                        name=space_name,
                        space_type="address-space",
                        start=space_start,
                        size=space_size,
                        segments=sorted(segments, key=lambda x: x.start),
                    )
                )
            else:
                # Create a single-segment memory space if no sub-segments
                segments.append(
                    MemorySegment(
                        name=space_name,
                        start=space_start,
                        size=space_size,
                        type=space_name,
                        address_space=space_name,
                        parent_name=None,  # Top-level
                        level=0,
                    )
                )

                memory_spaces.append(
                    MemorySpace(
                        name=space_name,
                        space_type="address-space",
                        start=space_start,
                        size=space_size,
                        segments=segments,
                    )
                )

        return memory_spaces

    def _parse_modules(self) -> List[Module]:
        """Parse modules/peripherals."""
        modules = []

        # Find all modules
        module_elements = self.parser.xpath("//modules/module")
        for module_element in module_elements:
            module_name = self.parser.get_attr(module_element, "name", "")
            module_caption = self.parser.get_attr(module_element, "caption", "")

            # Find register groups in this module
            register_groups = self._parse_register_groups_in_module(module_element)

            if register_groups:  # Only add modules with register groups
                modules.append(
                    Module(
                        name=module_name,
                        caption=module_caption,
                        register_groups=register_groups,
                    )
                )

        return modules

    def _parse_register_groups_in_module(
        self, module_element: etree._Element
    ) -> List[RegisterGroup]:
        """Parse register groups within a module."""
        groups = []

        # Find register-group definitions in the module
        rg_elements = self.parser.xpath(".//register-group", module_element)

        for rg_element in rg_elements:
            group_name = self.parser.get_attr(rg_element, "name", "")
            group_caption = self.parser.get_attr(rg_element, "caption", "")

            # Find registers in this group
            registers = self._parse_registers_in_group(rg_element, group_name)

            if registers:  # Only add groups with registers
                groups.append(
                    RegisterGroup(
                        name=group_name, caption=group_caption, registers=registers
                    )
                )

        return groups

    def _parse_registers_in_group(
        self, group_element: etree._Element, group_name: str
    ) -> List[Register]:
        """Parse registers within a register group."""
        registers = []

        # Look for registers directly in the group element
        register_elements = self.parser.xpath(".//register", group_element)

        # Also look for register-group definitions at the root level
        root_groups = self.parser.xpath(f'//register-group[@name="{group_name}"]')
        for root_group in root_groups:
            if root_group != group_element:  # Avoid duplicates
                register_elements.extend(self.parser.xpath(".//register", root_group))

        for reg_element in register_elements:
            register = self._parse_register(reg_element)
            if register:
                registers.append(register)

        return registers

    def _parse_register(self, register_element: etree._Element) -> Optional[Register]:
        """Parse a single register."""
        name = self.parser.get_attr(register_element, "name", "")
        if not name:
            return None

        caption = self.parser.get_attr(register_element, "caption", "")
        offset = self.parser.get_attr_hex(register_element, "offset", 0)
        size = self.parser.get_attr_int(register_element, "size", 1)
        mask = self.parser.get_attr_hex(register_element, "mask", 0)
        initval = self.parser.get_attr_hex(register_element, "initval", 0)
        access = self.parser.get_attr(register_element, "ocd-rw", "RW")

        # Parse bitfields
        bitfields = []
        bitfield_elements = self.parser.xpath(".//bitfield", register_element)
        for bf_element in bitfield_elements:
            bitfield = self._parse_bitfield(bf_element)
            if bitfield:
                bitfields.append(bitfield)

        return Register(
            name=name,
            caption=caption,
            offset=offset,
            size=size,
            mask=mask if mask > 0 else None,
            initial_value=initval if initval > 0 else None,
            access=access,
            bitfields=bitfields,
        )

    def _parse_bitfield(
        self, bitfield_element: etree._Element
    ) -> Optional[RegisterBitfield]:
        """Parse a register bitfield."""
        name = self.parser.get_attr(bitfield_element, "name", "")
        if not name:
            return None

        caption = self.parser.get_attr(bitfield_element, "caption", "")
        mask = self.parser.get_attr_hex(bitfield_element, "mask", 0)

        if mask == 0:
            return None

        # Calculate bit offset and width from mask
        bit_offset, bit_width = self._calculate_bit_range(mask)

        # Parse possible values
        values = None
        values_ref = self.parser.get_attr(bitfield_element, "values", "")
        if values_ref:
            values = self._parse_bitfield_values(values_ref)

        return RegisterBitfield(
            name=name,
            caption=caption,
            mask=mask,
            bit_offset=bit_offset,
            bit_width=bit_width,
            values=values,
        )

    def _parse_bitfield_values(self, values_ref: str) -> Dict[int, str]:
        """Parse bitfield possible values."""
        values = {}

        # Find value-group with this name
        value_groups = self.parser.xpath(f'//value-group[@name="{values_ref}"]')
        for vg in value_groups:
            value_elements = self.parser.xpath(".//value", vg)
            for value_element in value_elements:
                value_name = self.parser.get_attr(value_element, "name", "")
                value_caption = self.parser.get_attr(value_element, "caption", "")
                value_num = self.parser.get_attr_hex(value_element, "value", 0)

                if value_name:
                    values[value_num] = value_caption or value_name

        return values if values else None

    def _parse_fuses(self) -> List[Fuse]:
        """Parse fuse configurations."""
        fuses = []

        # Find fuse modules
        fuse_modules = self.parser.xpath('//modules/module[@name="FUSE"]')
        for fuse_module in fuse_modules:
            # Find register groups
            rg_elements = self.parser.xpath(
                './/register-group[@name="FUSE"]', fuse_module
            )
            for rg_element in rg_elements:
                # Find registers
                register_elements = self.parser.xpath(".//register", rg_element)
                for reg_element in register_elements:
                    fuse = self._parse_fuse_register(reg_element, fuse_module)
                    if fuse:
                        fuses.append(fuse)

        # Also look for fuse register-groups at root level
        root_fuse_groups = self.parser.xpath('//register-group[@name="FUSE"]')
        for rg_element in root_fuse_groups:
            register_elements = self.parser.xpath(".//register", rg_element)
            for reg_element in register_elements:
                fuse = self._parse_fuse_register(reg_element, None)
                if fuse:
                    fuses.append(fuse)

        return fuses

    def _parse_fuse_register(
        self, register_element: etree._Element, module_element: Optional[etree._Element]
    ) -> Optional[Fuse]:
        """Parse a fuse register."""
        name = self.parser.get_attr(register_element, "name", "")
        if not name:
            return None

        offset = self.parser.get_attr_hex(register_element, "offset", 0)
        size = self.parser.get_attr_int(register_element, "size", 1)
        mask = self.parser.get_attr_hex(register_element, "mask", 0)
        initval = self.parser.get_attr_hex(register_element, "initval", 0)

        # Parse bitfields
        bitfields = []
        bitfield_elements = self.parser.xpath(".//bitfield", register_element)
        for bf_element in bitfield_elements:
            bf_name = self.parser.get_attr(bf_element, "name", "")
            bf_caption = self.parser.get_attr(bf_element, "caption", "")
            bf_mask = self.parser.get_attr_hex(bf_element, "mask", 0)

            if bf_name and bf_mask > 0:
                bit_offset, bit_width = self._calculate_bit_range(bf_mask)

                # Parse values
                values = None
                values_ref = self.parser.get_attr(bf_element, "values", "")
                if values_ref and module_element is not None:
                    # Look for value-group in module
                    vg_elements = self.parser.xpath(
                        f'.//value-group[@name="{values_ref}"]', module_element
                    )
                    if vg_elements:
                        values = {}
                        for vg in vg_elements:
                            value_elements = self.parser.xpath(".//value", vg)
                            for v_element in value_elements:
                                v_name = self.parser.get_attr(v_element, "name", "")
                                v_caption = self.parser.get_attr(
                                    v_element, "caption", ""
                                )
                                v_value = self.parser.get_attr_hex(
                                    v_element, "value", 0
                                )
                                if v_name:
                                    values[v_value] = v_caption or v_name

                bitfields.append(
                    FuseBitfield(
                        name=bf_name,
                        description=bf_caption,
                        bit_offset=bit_offset,
                        bit_width=bit_width,
                        values=values,
                    )
                )

        return Fuse(
            name=name,
            offset=offset,
            size=size,
            mask=mask if mask > 0 else None,
            default_value=initval if initval > 0 else None,
            bitfields=bitfields,
        )

    def _parse_interrupts(self) -> List[Interrupt]:
        """Parse interrupt information."""
        interrupts = []

        interrupt_elements = self.parser.xpath("//interrupts/interrupt")
        for int_element in interrupt_elements:
            index = self.parser.get_attr_int(int_element, "index", 0)
            name = self.parser.get_attr(int_element, "name", "")
            caption = self.parser.get_attr(int_element, "caption", "")

            if name:
                interrupts.append(Interrupt(index=index, name=name, caption=caption))

        return sorted(interrupts, key=lambda x: x.index)

    def _parse_signatures(self) -> List[DeviceSignature]:
        """Parse device signatures."""
        signatures = []

        # Look for signature properties
        sig_elements = self.parser.xpath(
            '//property-group[@name="SIGNATURES"]/property'
        )
        for sig_element in sig_elements:
            name = self.parser.get_attr(sig_element, "name", "")
            value_str = self.parser.get_attr(sig_element, "value", "0")

            if name:
                try:
                    value = (
                        int(value_str, 16)
                        if value_str.startswith("0x")
                        else int(value_str)
                    )

                    # Extract address from name if it's SIGNATUREx
                    address = None
                    if name.startswith("SIGNATURE") and name[9:].isdigit():
                        address = int(name[9:])

                    signatures.append(
                        DeviceSignature(name=name, address=address, value=value)
                    )
                except ValueError:
                    pass

        return sorted(signatures, key=lambda x: x.address or 999)

    def _parse_electrical_parameters(self) -> List[ElectricalParameter]:
        """Parse electrical parameters."""
        parameters = []

        # Look for electrical parameter groups
        param_groups = self.parser.xpath(
            '//property-groups/property-group[contains(@name, "ELECTRICAL") or contains(@name, "ABSOLUTE") or contains(@name, "DC") or contains(@name, "AC")]'
        )

        for group in param_groups:
            group_name = self.parser.get_attr(group, "name", "")
            group_caption = self.parser.get_attr(group, "caption", "")

            # Parse properties in this group
            properties = self.parser.xpath(".//property", group)
            for prop in properties:
                name = self.parser.get_attr(prop, "name", "")
                caption = self.parser.get_attr(prop, "caption", "")
                description = self.parser.get_attr(prop, "description", "")

                # Parse min/typ/max values
                min_val = self.parser.get_attr(prop, "min", "")
                typ_val = self.parser.get_attr(prop, "typ", "")
                max_val = self.parser.get_attr(prop, "max", "")
                unit = self.parser.get_attr(prop, "unit", "")
                conditions = self.parser.get_attr(prop, "conditions", "")

                # Convert to float if possible
                min_value = (
                    float(min_val)
                    if min_val and min_val.replace(".", "").replace("-", "").isdigit()
                    else None
                )
                typ_value = (
                    float(typ_val)
                    if typ_val and typ_val.replace(".", "").replace("-", "").isdigit()
                    else None
                )
                max_value = (
                    float(max_val)
                    if max_val and max_val.replace(".", "").replace("-", "").isdigit()
                    else None
                )

                if name:
                    parameters.append(
                        ElectricalParameter(
                            name=name,
                            group=group_name,
                            caption=caption,
                            description=description,
                            min_value=min_value,
                            typical_value=typ_value,
                            max_value=max_value,
                            unit=unit,
                            conditions=conditions,
                        )
                    )

        return parameters

    def _parse_atmel_package_variants(
        self, root_element: etree._Element
    ) -> List[AtmelPackageVariant]:
        """Parse ATMEL package variant information."""
        variants = []

        # Look for variants in the ATDF structure
        variant_elements = self.parser.xpath("//variant", root_element)

        for variant in variant_elements:
            package = self.parser.get_attr(variant, "package", "")
            pinout = self.parser.get_attr(variant, "pinout", "")
            order_code = self.parser.get_attr(variant, "ordercode", "")

            # Temperature range
            temp_min_str = self.parser.get_attr(variant, "tempmin", "")
            temp_max_str = self.parser.get_attr(variant, "tempmax", "")
            temp_min = self._parse_float(temp_min_str)
            temp_max = self._parse_float(temp_max_str)

            # Speed and voltage specs
            speed_max_str = self.parser.get_attr(variant, "speedmax", "")
            speed_max = self._parse_int(speed_max_str)

            vcc_min_str = self.parser.get_attr(variant, "vccmin", "")
            vcc_max_str = self.parser.get_attr(variant, "vccmax", "")
            vcc_min = self._parse_float(vcc_min_str)
            vcc_max = self._parse_float(vcc_max_str)

            if package and pinout:
                variants.append(
                    AtmelPackageVariant(
                        package=package,
                        pinout=pinout,
                        order_code=order_code or None,
                        temp_min=temp_min,
                        temp_max=temp_max,
                        speed_max=speed_max,
                        vcc_min=vcc_min,
                        vcc_max=vcc_max,
                    )
                )

        return variants

    def _parse_atmel_pinouts(
        self, root_element: etree._Element
    ) -> List[AtmelPinoutInfo]:
        """Parse ATMEL pinout information."""
        pinouts = []

        # Look for pinout definitions
        pinout_elements = self.parser.xpath("//pinout", root_element)

        for pinout_elem in pinout_elements:
            name = self.parser.get_attr(pinout_elem, "name", "")
            caption = self.parser.get_attr(pinout_elem, "caption", "")

            # Get pins
            pin_elements = self.parser.xpath(".//pin", pinout_elem)
            pins = []

            for pin_elem in pin_elements:
                position = self.parser.get_attr(pin_elem, "position", "")
                pad = self.parser.get_attr(pin_elem, "pad", "")

                if position and pad:
                    pins.append({"position": position, "pad": pad})

            if name and pins:
                pinouts.append(
                    AtmelPinoutInfo(
                        name=name,
                        caption=caption or None,
                        pin_count=len(pins),
                        pins=pins,
                    )
                )

        return pinouts

    def _parse_atmel_programming_interfaces(
        self, root_element: etree._Element
    ) -> List[AtmelProgrammingInterface]:
        """Parse ATMEL programming interface information."""
        interfaces = []

        # Look for interface definitions
        interface_elements = self.parser.xpath("//interface", root_element)

        for interface_elem in interface_elements:
            name = self.parser.get_attr(interface_elem, "name", "")
            interface_type = self.parser.get_attr(interface_elem, "type", "")

            # Get interface properties
            properties = {}

            # Look for parameters
            param_elements = self.parser.xpath(".//param", interface_elem)
            for param_elem in param_elements:
                param_name = self.parser.get_attr(param_elem, "name", "")
                param_value = self.parser.get_attr(param_elem, "value", "")

                if param_name:
                    properties[param_name] = param_value

            if name and interface_type:
                interfaces.append(
                    AtmelProgrammingInterface(
                        name=name, interface_type=interface_type, properties=properties
                    )
                )

        return interfaces

    def _parse_atmel_clock_info(
        self, root_element: etree._Element
    ) -> Optional[AtmelClockInfo]:
        """Parse ATMEL clock system information."""
        clock_info = AtmelClockInfo()

        # Look for clock-related modules
        clock_modules = []
        module_elements = self.parser.xpath("//module", root_element)

        for module_elem in module_elements:
            module_name = self.parser.get_attr(module_elem, "name", "").upper()
            if any(
                clock_term in module_name
                for clock_term in ["CLK", "OSC", "CLOCK", "PLL"]
            ):
                module_info = {"name": self.parser.get_attr(module_elem, "name", "")}

                # Get instances
                instance_elements = self.parser.xpath(".//instance", module_elem)
                instances = []
                for inst_elem in instance_elements:
                    instances.append(dict(inst_elem.attrib))

                if instances:
                    module_info["instances"] = instances

                clock_modules.append(module_info)

        # Look for clock-related properties
        clock_properties = []
        prop_group_elements = self.parser.xpath("//property-group", root_element)

        for prop_group_elem in prop_group_elements:
            group_name = self.parser.get_attr(prop_group_elem, "name", "").lower()
            if any(
                clock_term in group_name for clock_term in ["clock", "osc", "frequency"]
            ):
                group_info = {
                    "name": self.parser.get_attr(prop_group_elem, "name", ""),
                    "properties": [],
                }

                prop_elements = self.parser.xpath(".//property", prop_group_elem)
                for prop_elem in prop_elements:
                    prop_info = dict(prop_elem.attrib)
                    if prop_elem.text:
                        prop_info["value"] = prop_elem.text.strip()
                    group_info["properties"].append(prop_info)

                clock_properties.append(group_info)

        # Look for maximum frequency in package variants
        max_frequency = None
        variant_elements = self.parser.xpath("//variant", root_element)
        for variant_elem in variant_elements:
            speed_max_str = self.parser.get_attr(variant_elem, "speedmax", "")
            speed_max = self._parse_int(speed_max_str)
            if speed_max and (max_frequency is None or speed_max > max_frequency):
                max_frequency = speed_max

        clock_info.clock_modules = clock_modules
        clock_info.clock_properties = clock_properties
        clock_info.max_frequency = max_frequency

        # Return None if no meaningful data
        if not clock_modules and not clock_properties and max_frequency is None:
            return None

        return clock_info

    def _parse_atmel_gpio_info(
        self, root_element: etree._Element
    ) -> List[AtmelGpioInfo]:
        """Parse ATMEL GPIO port information."""
        gpio_info = []

        # Look for GPIO/PORT modules
        module_elements = self.parser.xpath("//module", root_element)

        for module_elem in module_elements:
            module_name = self.parser.get_attr(module_elem, "name", "").upper()
            if module_name.startswith("PORT"):
                port_name = self.parser.get_attr(module_elem, "name", "")

                # Get instances
                instance_elements = self.parser.xpath(".//instance", module_elem)
                instances = []
                for inst_elem in instance_elements:
                    instances.append(dict(inst_elem.attrib))

                # Estimate pin count from instances (each instance typically represents one pin)
                pin_count = len(instances) if instances else None

                gpio_info.append(
                    AtmelGpioInfo(
                        port_name=port_name, instances=instances, pin_count=pin_count
                    )
                )

        return gpio_info

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

    def _calculate_bit_range(self, mask: int) -> tuple[int, int]:
        """Calculate bit offset and width from mask."""
        if mask == 0:
            return 0, 0

        # Find first set bit (bit offset)
        bit_offset = (mask & -mask).bit_length() - 1

        # Count consecutive bits
        temp_mask = mask >> bit_offset
        bit_width = 0
        while temp_mask & 1:
            bit_width += 1
            temp_mask >>= 1

        return bit_offset, bit_width

    # ...existing ATMEL-specific methods...
