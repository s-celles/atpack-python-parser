"""PDSC (Package Description) parser for AtPack metadata."""

from typing import List, Optional

from ..models import AtPackMetadata, DeviceFamily
from .xml import XmlParser


class PdscParser:
    """Parser for PDSC files containing AtPack metadata."""

    def __init__(self, xml_content: str):
        """Initialize with XML content."""
        self.parser = XmlParser(xml_content)

    def parse_metadata(self) -> AtPackMetadata:
        """Parse AtPack metadata from PDSC."""
        # Get package information
        package_name = self.parser.xpath_text("//package/@name", "Unknown")
        description = self.parser.xpath_text("//package/description/text()", "")
        vendor = self.parser.xpath_text("//package/@vendor", "Unknown")
        version = self.parser.xpath_text("//package/@version", "0.0.0")
        url = self.parser.xpath_text("//package/@url", "")

        return AtPackMetadata(
            name=package_name or "Unknown",
            description=description,
            vendor=vendor,
            version=version,
            url=url,
        )

    def list_devices(self) -> List[str]:
        """List all device names mentioned in PDSC."""
        device_names = []

        # Look for device definitions
        devices = self.parser.xpath("//devices/family/device/@Dname")
        device_names.extend([name for name in devices if isinstance(name, str)])

        # Also look for subfamily devices
        subfamily_devices = self.parser.xpath(
            "//devices/family/subFamily/device/@Dname"
        )
        device_names.extend(
            [name for name in subfamily_devices if isinstance(name, str)]
        )

        # Look for variant devices
        variant_devices = self.parser.xpath("//devices/family/device/variant/@Dvariant")
        device_names.extend([name for name in variant_devices if isinstance(name, str)])

        # Remove duplicates and sort
        return sorted(list(set(device_names)))

    def get_device_info(self, device_name: str) -> Optional[dict]:
        """Get basic device information from PDSC."""
        # Look for device by name
        device_elements = self.parser.xpath(
            f'//device[@Dname="{device_name}"] | //variant[@Dvariant="{device_name}"]'
        )

        if not device_elements:
            return None

        device_elem = device_elements[0]

        # Get family information
        family_elem = device_elem
        while family_elem is not None and family_elem.tag != "family":
            family_elem = family_elem.getparent()

        family_name = ""
        if family_elem is not None:
            family_name = self.parser.get_attr(family_elem, "Dfamily", "")

        # Extract device information
        processor = self.parser.get_attr(device_elem, "Dcore", "")
        clock = self.parser.get_attr(device_elem, "Dclock", "")
        flash_size = self.parser.get_attr(device_elem, "Dflash", "")
        ram_size = self.parser.get_attr(device_elem, "Dram", "")
        package = self.parser.get_attr(device_elem, "Dpackage", "")

        return {
            "name": device_name,
            "family": family_name,
            "processor": processor,
            "clock": clock,
            "flash_size": flash_size,
            "ram_size": ram_size,
            "package": package,
        }

    def detect_device_family(self) -> DeviceFamily:
        """Detect device family from PDSC content."""
        # Check vendor
        vendor = self.parser.xpath_text("//package/@vendor", "").upper()

        if "ATMEL" in vendor:
            return DeviceFamily.ATMEL
        elif "MICROCHIP" in vendor:
            # Could be either ATMEL (acquired by Microchip) or PIC
            # Check device families or processor types
            processors = self.parser.xpath("//device/@Dcore")
            families = self.parser.xpath("//family/@Dfamily")

            # Check for typical ATMEL processors
            atmel_processors = ["ARM", "AVR", "Cortex"]
            for proc in processors:
                if isinstance(proc, str):
                    for atmel_proc in atmel_processors:
                        if atmel_proc in proc.upper():
                            return DeviceFamily.ATMEL

            # Check for typical ATMEL families
            atmel_families = ["AVR", "SAM", "MEGA", "TINY"]
            for family in families:
                if isinstance(family, str):
                    for atmel_fam in atmel_families:
                        if atmel_fam in family.upper():
                            return DeviceFamily.ATMEL

            # Default to PIC for Microchip
            return DeviceFamily.PIC

        return DeviceFamily.UNSUPPORTED

    def get_file_references(self) -> dict:
        """Get file references from PDSC."""
        files = {"atdf": [], "pic": [], "headers": [], "docs": []}

        # Look for file elements
        file_elements = self.parser.xpath("//files/file")

        for file_elem in file_elements:
            file_name = self.parser.get_attr(file_elem, "name", "")
            file_category = self.parser.get_attr(file_elem, "category", "")

            if file_name:
                if file_name.lower().endswith(".atdf"):
                    files["atdf"].append(file_name)
                elif file_name.lower().endswith(".pic"):
                    files["pic"].append(file_name)
                elif file_category in ["header", "include"]:
                    files["headers"].append(file_name)
                elif file_category in ["doc", "documentation"]:
                    files["docs"].append(file_name)

        return files
