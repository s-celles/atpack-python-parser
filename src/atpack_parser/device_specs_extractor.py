"""Device specifications extractor for AtPack files."""

from typing import List, Optional
from lxml import etree

from .models import DeviceSpecs, GprSector
from .parser.xml import XmlParser
from .parser.atpack import AtPackParser
from .models import DeviceFamily
from pathlib import Path


class DeviceSpecsExtractor:
    """Extract comprehensive device specifications from AtPack files."""
    
    def __init__(self, xml_content: str):
        """Initialize with XML content."""
        self.parser = XmlParser(xml_content)
    
    def extract_specs(self, device_name: Optional[str] = None) -> DeviceSpecs:
        """Extract device specifications from PIC file."""
        # Get device element
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
            raise ValueError(f"Device '{device_name}' not found in PIC file")
        
        device_element = device_elements[0]
        
        # Extract device name
        name = (
            self.parser.get_attr(device_element, "name")
            or self.parser.get_attr(device_element, "{http://crownking/edc}name")
            or device_element.get("{http://crownking/edc}name")
            or device_name
            or "Unknown"
        )
        
        # Extract architecture and series
        arch = self.parser.get_attr(device_element, "arch", "")
        series = None
        if arch:
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
        
        specs = DeviceSpecs(
            device_name=name,
            f_cpu="User configurable",  # PIC devices typically have configurable oscillators
            architecture="PIC",
            series=series
        )
        
        # Extract program memory size (Flash)
        self._extract_program_memory(device_element, specs)
        
        # Extract RAM size from GPR sectors
        self._extract_ram_memory(device_element, specs)
        
        # Extract EEPROM information
        self._extract_eeprom_memory(device_element, specs)
        
        # Extract configuration memory
        self._extract_config_memory(device_element, specs)
        
        return specs
    
    def _extract_program_memory(self, device_element: etree._Element, specs: DeviceSpecs) -> None:
        """Extract program memory information."""
        program_space = self.parser.xpath(
            './/edc:ProgramSpace | .//*[local-name()="ProgramSpace"]', device_element
        )
        
        if not program_space:
            return
        
        max_flash = 0
        for ps in program_space:
            # Look for CodeSector elements
            code_sectors = self.parser.xpath(
                './/edc:CodeSector | .//*[local-name()="CodeSector"]', ps
            )
            for code_sector in code_sectors:
                # Skip shadow sectors (they are mirrors of other memory regions)
                shadow_ref = (
                    self.parser.get_attr(code_sector, "shadowidref")
                    or self.parser.get_attr(code_sector, "{http://crownking/edc}shadowidref")
                    or code_sector.get("{http://crownking/edc}shadowidref")
                )
                if shadow_ref is not None:
                    continue
                    
                begin_addr = self.parser.get_attr_hex(code_sector, "beginaddr", 0)
                end_addr = self.parser.get_attr_hex(code_sector, "endaddr", 0)
                sector_size = end_addr - begin_addr
                max_flash += sector_size
        
        specs.maximum_size = max_flash
    
    def _extract_ram_memory(self, device_element: etree._Element, specs: DeviceSpecs) -> None:
        """Extract RAM memory information including GPR sectors."""
        data_space = self.parser.xpath(
            './/edc:DataSpace | .//*[local-name()="DataSpace"]', device_element
        )
        
        if not data_space:
            return
        
        total_ram = 0
        gpr_sectors = []
        
        for ds in data_space:
            # Look for GPRDataSector elements (General Purpose Register sectors)
            gpr_data_sectors = self.parser.xpath(
                './/edc:GPRDataSector | .//*[local-name()="GPRDataSector"]', ds
            )
            
            for gpr_sector in gpr_data_sectors:
                # Skip shadow sectors (they are mirrors of other memory regions)
                # Check for shadowidref attribute with both namespace and local name approaches
                shadow_ref = (
                    self.parser.get_attr(gpr_sector, "shadowidref")
                    or self.parser.get_attr(gpr_sector, "{http://crownking/edc}shadowidref")
                    or gpr_sector.get("{http://crownking/edc}shadowidref")
                )
                if shadow_ref is not None:
                    continue
                
                begin_addr = self.parser.get_attr_hex(gpr_sector, "beginaddr", 0)
                end_addr = self.parser.get_attr_hex(gpr_sector, "endaddr", 0)
                sector_size = end_addr - begin_addr
                bank = self.parser.get_attr(gpr_sector, "bank", "0")
                
                if sector_size > 0:
                    total_ram += sector_size
                    
                    gpr_info = GprSector(
                        name=f"GPR_BANK{bank}",
                        start_addr=begin_addr,
                        end_addr=end_addr,
                        size=sector_size,
                        bank=bank
                    )
                    gpr_sectors.append(gpr_info)
        
        specs.maximum_ram_size = total_ram
        specs.gpr_total_size = total_ram
        specs.gpr_sectors = gpr_sectors
    
    def _extract_eeprom_memory(self, device_element: etree._Element, specs: DeviceSpecs) -> None:
        """Extract EEPROM memory information."""
        # EEPROM is typically in ProgramSpace for PIC devices
        program_space = self.parser.xpath(
            './/edc:ProgramSpace | .//*[local-name()="ProgramSpace"]', device_element
        )
        
        for ps in program_space:
            eeprom_sectors = self.parser.xpath(
                './/edc:EEDataSector | .//*[local-name()="EEDataSector"]', ps
            )
            
            for eeprom_sector in eeprom_sectors:
                eeprom_begin = self.parser.get_attr_hex(eeprom_sector, "beginaddr", 0)
                eeprom_end = self.parser.get_attr_hex(eeprom_sector, "endaddr", 0)
                
                if eeprom_end > eeprom_begin:
                    specs.eeprom_addr = f"0x{eeprom_begin:04X}"
                    specs.eeprom_size = eeprom_end - eeprom_begin
                    break  # Take the first EEPROM sector found
    
    def _extract_config_memory(self, device_element: etree._Element, specs: DeviceSpecs) -> None:
        """Extract configuration memory information."""
        program_space = self.parser.xpath(
            './/edc:ProgramSpace | .//*[local-name()="ProgramSpace"]', device_element
        )
        
        for ps in program_space:
            config_sectors = self.parser.xpath(
                './/edc:ConfigFuseSector | .//*[local-name()="ConfigFuseSector"]', ps
            )
            
            for config_sector in config_sectors:
                config_begin = self.parser.get_attr_hex(config_sector, "beginaddr", 0)
                config_end = self.parser.get_attr_hex(config_sector, "endaddr", 0)
                
                if config_end > config_begin:
                    specs.config_addr = f"0x{config_begin:04X}"
                    specs.config_size = config_end - config_begin
                    break  # Take the first config sector found


def extract_device_specs_from_atpack(atpack_parser: AtPackParser, device_name: str) -> DeviceSpecs:
    """Extract device specifications from an AtPack parser instance."""
    if not isinstance(atpack_parser, AtPackParser):
        raise TypeError("Expected AtPackParser instance")
    
    if atpack_parser.device_family != DeviceFamily.PIC:
        raise ValueError("Device specifications extraction is currently only supported for PIC devices")
    
    # Find PIC file for device
    pic_files = atpack_parser.extractor.find_pic_files()
    
    pic_file = None
    for file_path in pic_files:
        file_name = Path(file_path).stem
        if file_name.upper() == device_name.upper():
            pic_file = file_path
            break
    
    if not pic_file:
        raise ValueError(f"PIC file for device '{device_name}' not found")
    
    # Read PIC file content
    pic_content = atpack_parser.extractor.read_file(pic_file)
    
    # Extract specifications
    extractor = DeviceSpecsExtractor(pic_content)
    return extractor.extract_specs(device_name)


def extract_all_device_specs_from_atpack(atpack_parser: AtPackParser) -> List[DeviceSpecs]:
    """Extract device specifications for all devices in an AtPack."""
    if not isinstance(atpack_parser, AtPackParser):
        raise TypeError("Expected AtPackParser instance")
    
    if atpack_parser.device_family != DeviceFamily.PIC:
        raise ValueError("Device specifications extraction is currently only supported for PIC devices")
    
    all_specs = []
    pic_files = atpack_parser.extractor.find_pic_files()
    
    for pic_file in pic_files:
        device_name = Path(pic_file).stem
        
        # Skip Application Support files that start with AC162
        if device_name.startswith("AC162"):
            continue
        
        try:
            pic_content = atpack_parser.extractor.read_file(pic_file)
            extractor = DeviceSpecsExtractor(pic_content)
            specs = extractor.extract_specs(device_name)
            all_specs.append(specs)
        except Exception as e:
            print(f"Warning: Failed to extract specs for {device_name}: {e}")
            continue
    
    # Sort by device name
    all_specs.sort(key=lambda x: x.device_name)
    return all_specs
