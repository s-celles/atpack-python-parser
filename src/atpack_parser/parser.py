"""Main AtPack parser that handles both ATMEL and Microchip formats."""

from pathlib import Path
from typing import Any, Dict, List, Optional

from .atdf_parser import AtdfParser
from .exceptions import (
    DeviceNotFoundError,
    ParseError,
    UnsupportedFormatError,
)
from .models import AtPackMetadata, Device, DeviceFamily
from .pdsc_parser import PdscParser
from .pic_parser import PicParser
from .xml_utils import AtPackExtractor


class AtPackParser:
    """Main parser for AtPack files."""

    def __init__(self, atpack_path: str | Path):
        """Initialize parser with AtPack file path."""
        self.atpack_path = Path(atpack_path)
        self.extractor = AtPackExtractor(self.atpack_path)
        self._metadata: Optional[AtPackMetadata] = None
        self._device_family: Optional[DeviceFamily] = None
        self._device_cache: Dict[str, Device] = {}

    @property
    def metadata(self) -> AtPackMetadata:
        """Get AtPack metadata."""
        if self._metadata is None:
            self._metadata = self._parse_metadata()
        return self._metadata

    @property
    def device_family(self) -> DeviceFamily:
        """Get detected device family."""
        if self._device_family is None:
            self._device_family = self._detect_device_family()
        return self._device_family

    def get_devices(self) -> List[str]:
        """Get list of all device names in the AtPack."""
        try:
            # Try to get from PDSC first
            pdsc_files = self.extractor.find_pdsc_files()
            if pdsc_files:
                pdsc_content = self.extractor.read_file(pdsc_files[0])
                pdsc_parser = PdscParser(pdsc_content)
                devices = pdsc_parser.list_devices()
                if devices:
                    return devices

            # Fallback: scan device files directly
            if self.device_family == DeviceFamily.ATMEL:
                atdf_files = self.extractor.find_atdf_files()
                devices = []
                for atdf_file in atdf_files:
                    device_name = Path(atdf_file).stem
                    devices.append(device_name)
                return sorted(devices)

            elif self.device_family == DeviceFamily.PIC:
                pic_files = self.extractor.find_pic_files()
                devices = []
                for pic_file in pic_files:
                    device_name = Path(pic_file).stem
                    devices.append(device_name)
                return sorted(devices)

            else:
                raise UnsupportedFormatError(
                    f"Unsupported device family: {self.device_family}"
                )

        except Exception as e:
            raise ParseError(f"Error getting device list: {e}")

    def get_device(self, device_name: str) -> Device:
        """Get detailed information for a specific device."""
        if device_name in self._device_cache:
            return self._device_cache[device_name]

        try:
            device = self._parse_device(device_name)
            self._device_cache[device_name] = device
            return device

        except Exception as e:
            raise DeviceNotFoundError(
                f"Device '{device_name}' not found or could not be parsed: {e}"
            )

    def get_device_registers(self, device_name: str) -> List[Any]:
        """Get registers for a specific device."""
        device = self.get_device(device_name)
        registers = []

        for module in device.modules:
            for reg_group in module.register_groups:
                registers.extend(reg_group.registers)

        return sorted(registers, key=lambda x: x.offset)

    def get_device_memory(self, device_name: str) -> List[Any]:
        """Get memory segments for a specific device."""
        device = self.get_device(device_name)
        return sorted(device.memory_segments, key=lambda x: x.start)

    def get_device_config(self, device_name: str) -> Dict[str, Any]:
        """Get configuration information for a specific device."""
        device = self.get_device(device_name)

        config = {
            "fuses": device.fuses,
            "config_words": device.config_words,
            "interrupts": device.interrupts,
            "signatures": device.signatures,
        }

        return config

    def list_files(self, pattern: Optional[str] = None) -> List[str]:
        """List files in the AtPack."""
        return self.extractor.list_files(pattern)

    def read_file(self, file_path: str) -> str:
        """Read a file from the AtPack."""
        return self.extractor.read_file(file_path)

    def _parse_metadata(self) -> AtPackMetadata:
        """Parse AtPack metadata from PDSC file."""
        pdsc_files = self.extractor.find_pdsc_files()

        if not pdsc_files:
            # Create minimal metadata
            return AtPackMetadata(
                name=self.atpack_path.stem,
                description=f"AtPack from {self.atpack_path.name}",
                vendor="Unknown",
                version="0.0.0",
            )

        try:
            pdsc_content = self.extractor.read_file(pdsc_files[0])
            pdsc_parser = PdscParser(pdsc_content)
            return pdsc_parser.parse_metadata()

        except Exception:
            # Return minimal metadata if parsing fails
            return AtPackMetadata(
                name=self.atpack_path.stem,
                description=f"AtPack from {self.atpack_path.name}",
                vendor="Unknown",
                version="0.0.0",
            )

    def _detect_device_family(self) -> DeviceFamily:
        """Detect device family from AtPack contents."""
        try:
            # Try PDSC first
            pdsc_files = self.extractor.find_pdsc_files()
            if pdsc_files:
                pdsc_content = self.extractor.read_file(pdsc_files[0])
                pdsc_parser = PdscParser(pdsc_content)
                family = pdsc_parser.detect_device_family()
                if family != DeviceFamily.UNSUPPORTED:
                    return family

            # Check file types
            atdf_files = self.extractor.find_atdf_files()
            pic_files = self.extractor.find_pic_files()

            if atdf_files and not pic_files:
                return DeviceFamily.ATMEL
            elif pic_files and not atdf_files:
                return DeviceFamily.PIC
            elif atdf_files and pic_files:
                # Both present - prefer ATMEL if more ATDF files
                if len(atdf_files) >= len(pic_files):
                    return DeviceFamily.ATMEL
                else:
                    return DeviceFamily.PIC

            return DeviceFamily.UNSUPPORTED

        except Exception:
            return DeviceFamily.UNSUPPORTED

    def _parse_device(self, device_name: str) -> Device:
        """Parse device information."""
        if self.device_family == DeviceFamily.ATMEL:
            return self._parse_atmel_device(device_name)
        elif self.device_family == DeviceFamily.PIC:
            return self._parse_pic_device(device_name)
        else:
            raise UnsupportedFormatError(
                f"Unsupported device family: {self.device_family}"
            )

    def _parse_atmel_device(self, device_name: str) -> Device:
        """Parse ATMEL device from ATDF file."""
        # Find ATDF file for device
        atdf_files = self.extractor.find_atdf_files()

        atdf_file = None
        for file_path in atdf_files:
            file_name = Path(file_path).stem
            if file_name.upper() == device_name.upper():
                atdf_file = file_path
                break

        if not atdf_file:
            raise DeviceNotFoundError(f"ATDF file for device '{device_name}' not found")

        try:
            atdf_content = self.extractor.read_file(atdf_file)
            atdf_parser = AtdfParser(atdf_content)
            return atdf_parser.parse_device(device_name)

        except Exception as e:
            raise ParseError(f"Error parsing ATDF file for '{device_name}': {e}")

    def _parse_pic_device(self, device_name: str) -> Device:
        """Parse PIC device from .pic file."""
        # Find PIC file for device
        pic_files = self.extractor.find_pic_files()

        pic_file = None
        for file_path in pic_files:
            file_name = Path(file_path).stem
            if file_name.upper() == device_name.upper():
                pic_file = file_path
                break

        if not pic_file:
            raise DeviceNotFoundError(f"PIC file for device '{device_name}' not found")

        try:
            pic_content = self.extractor.read_file(pic_file)
            pic_parser = PicParser(pic_content)
            return pic_parser.parse_device(device_name)

        except Exception as e:
            raise ParseError(f"Error parsing PIC file for '{device_name}': {e}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert AtPack to dictionary representation."""
        return {
            "metadata": self.metadata.model_dump(),
            "device_family": self.device_family.value,
            "devices": self.get_devices(),
            "file_path": str(self.atpack_path),
        }
