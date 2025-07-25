"""AtPack Parser - A library for parsing AtPack files."""

__version__ = "0.1.0"

from .exceptions import AtPackError, DeviceNotFoundError, ParseError
from .models import Device, Fuse, MemorySegment, Register, DeviceSpecs, GprSector
from .parser import AtPackParser
from .device_specs_extractor import (
    DeviceSpecsExtractor,
    extract_device_specs_from_atpack,
    extract_all_device_specs_from_atpack,
)

__all__ = [
    "AtPackParser",
    "Device",
    "Register",
    "MemorySegment",
    "Fuse",
    "DeviceSpecs",
    "GprSector",
    "DeviceSpecsExtractor",
    "extract_device_specs_from_atpack",
    "extract_all_device_specs_from_atpack",
    "AtPackError",
    "DeviceNotFoundError",
    "ParseError",
]
