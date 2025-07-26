"""Device specifications models for extracted AtPack data.

This module provides data models for representing comprehensive device specifications
extracted from Microchip AtPack files. The models include detailed memory layout
information, CPU characteristics, and General Purpose Register (GPR) sectors.

Key Features:
- Complete device memory specifications
- EEPROM and configuration memory details
- GPR sector mapping with bank information
- Support for shadowidref attribute handling to avoid double-counting
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class DeviceSpecs:
    """Comprehensive device specifications extracted from AtPack files.

    This class represents the complete memory and architectural specifications
    for a microcontroller device as defined in AtPack XML files. It includes
    all major memory regions and their characteristics.

    Attributes:
        device_name: The official device name (e.g., "PIC16F84A")
        f_cpu: CPU frequency specification (usually configurable for PICs)
        maximum_ram_size: Total RAM size in bytes including all GPR regions
        maximum_size: Program memory size (Flash) in words or bytes
        eeprom_addr: EEPROM memory start address (hexadecimal string)
        eeprom_size: EEPROM size in bytes (0 if no EEPROM)
        config_addr: Configuration memory start address (hexadecimal string)
        config_size: Configuration memory size in bytes
        gpr_total_size: Total General Purpose Register size in bytes
        gpr_sectors: List of individual GPR memory sectors with bank info
        architecture: Device architecture family (e.g., "PIC16")
        series: Device series within architecture (e.g., "PIC16F")
    """

    device_name: str  # Official device identifier
    f_cpu: Optional[str] = None  # CPU frequency (configurable for most PICs)
    maximum_ram_size: int = 0  # Total RAM size in bytes
    maximum_size: int = 0  # Program memory size (Flash) in words or bytes
    eeprom_addr: Optional[str] = None  # EEPROM start address (hex string)
    eeprom_size: int = 0  # EEPROM size in bytes
    config_addr: Optional[str] = None  # Configuration memory start address (hex)
    config_size: int = 0  # Configuration memory size in bytes
    gpr_total_size: int = 0  # Total General Purpose Register size in bytes
    gpr_sectors: list = None  # List of GPR memory sectors (GprSector objects)
    architecture: Optional[str] = None  # Device architecture family
    series: Optional[str] = None  # Device series within architecture

    def __post_init__(self):
        """Initialize empty lists and perform validation.

        This method is automatically called after object initialization
        to set up default values for mutable attributes and ensure
        data consistency.
        """
        if self.gpr_sectors is None:
            self.gpr_sectors = []


@dataclass
class GprSector:
    """General Purpose Register memory sector information.

    Represents a single GPR memory sector with its address range and
    bank assignment. GPR sectors are the primary user-accessible RAM
    regions in PIC microcontrollers.

    Note: Sectors with shadowidref attributes are memory mirrors and
    should not be counted toward total memory calculations to avoid
    double-counting the same physical memory.

    Attributes:
        name: Descriptive name of the GPR sector (e.g., "GPR0", "GPR1")
        start_addr: Starting address of the sector (integer)
        end_addr: Ending address of the sector (integer, inclusive)
        size: Size of the sector in bytes (end_addr - start_addr + 1)
        bank: Memory bank designation (e.g., "0", "1", "2", etc.)
    """

    name: str  # Sector name identifier
    start_addr: int  # Starting address (integer)
    end_addr: int  # Ending address (integer, inclusive)
    size: int  # Sector size in bytes
    bank: Optional[str] = None  # Memory bank designation
