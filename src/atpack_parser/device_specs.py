"""Device specifications extractor functions.

This module provides convenience functions for extracting device specifications
from AtPack files. The actual implementation has been integrated into PicParser
for better code organization and to eliminate code duplication.
"""

from typing import List, Optional
from pathlib import Path

from .models import DeviceSpecs, GprSector
from .parser.pic import PicParser
from .parser.atpack import AtPackParser
from .models import DeviceFamily


def extract_device_specs_from_xml(
    xml_content: str, device_name: Optional[str] = None
) -> DeviceSpecs:
    """Extract device specifications from PIC XML content.

    This function uses the PicParser.extract_device_specs() method internally.

    Args:
        xml_content: Raw XML content from PIC file
        device_name: Optional device name to search for

    Returns:
        DeviceSpecs: Comprehensive device specifications
    """
    parser = PicParser(xml_content)
    return parser.extract_device_specs(device_name)


def extract_device_specs_from_atpack(
    atpack_parser: AtPackParser, device_name: str
) -> DeviceSpecs:
    """Extract device specifications from an AtPack parser instance.

    Args:
        atpack_parser: AtPackParser instance
        device_name: Name of the device to extract specs for

    Returns:
        DeviceSpecs: Comprehensive device specifications

    Raises:
        TypeError: If atpack_parser is not an AtPackParser instance
        ValueError: If device family is not PIC or device not found
    """
    if not isinstance(atpack_parser, AtPackParser):
        raise TypeError("Expected AtPackParser instance")

    if atpack_parser.device_family != DeviceFamily.PIC:
        raise ValueError(
            "Device specifications extraction is currently only supported for PIC devices"
        )

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

    # Extract specifications using PicParser
    return extract_device_specs_from_xml(pic_content, device_name)


def extract_all_device_specs_from_atpack(
    atpack_parser: AtPackParser,
) -> List[DeviceSpecs]:
    """Extract device specifications for all devices in an AtPack.

    Args:
        atpack_parser: AtPackParser instance

    Returns:
        List[DeviceSpecs]: List of device specifications for all devices

    Raises:
        TypeError: If atpack_parser is not an AtPackParser instance
        ValueError: If device family is not PIC
    """
    if not isinstance(atpack_parser, AtPackParser):
        raise TypeError("Expected AtPackParser instance")

    if atpack_parser.device_family != DeviceFamily.PIC:
        raise ValueError(
            "Device specifications extraction is currently only supported for PIC devices"
        )

    all_specs = []
    pic_files = atpack_parser.extractor.find_pic_files()

    for pic_file in pic_files:
        device_name = Path(pic_file).stem

        # Skip Application Support files that start with AC162
        if device_name.startswith("AC162"):
            continue

        try:
            pic_content = atpack_parser.extractor.read_file(pic_file)
            specs = extract_device_specs_from_xml(pic_content, device_name)
            all_specs.append(specs)
        except Exception as e:
            print(f"Warning: Failed to extract specs for {device_name}: {e}")
            continue

    # Sort by device name
    all_specs.sort(key=lambda x: x.device_name)
    return all_specs


# Backward compatibility class
class DeviceSpecsExtractor:
    """Extract comprehensive device specifications from AtPack files.

    This class is deprecated and provided only for backward compatibility.
    Use extract_device_specs_from_xml() function instead.
    The functionality has been integrated into PicParser for better code organization.
    """

    def __init__(self, xml_content: str):
        """Initialize with XML content.

        Args:
            xml_content: Raw XML content from PIC file
        """
        self.xml_content = xml_content

    def extract_specs(self, device_name: Optional[str] = None) -> DeviceSpecs:
        """Extract device specifications from PIC file.

        This method is deprecated. Use extract_device_specs_from_xml() function instead.

        Args:
            device_name: Optional device name to search for

        Returns:
            DeviceSpecs: Comprehensive device specifications
        """
        return extract_device_specs_from_xml(self.xml_content, device_name)
