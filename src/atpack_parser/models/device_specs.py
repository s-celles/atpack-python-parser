"""Device specifications models for extracted AtPack data."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class DeviceSpecs:
    """Comprehensive device specifications extracted from AtPack files."""
    
    device_name: str
    f_cpu: Optional[str] = None  # CPU frequency (configurable for most PICs)
    maximum_ram_size: int = 0  # Total RAM size in bytes
    maximum_size: int = 0  # Program memory size (Flash) in words or bytes
    eeprom_addr: Optional[str] = None  # EEPROM start address
    eeprom_size: int = 0  # EEPROM size in bytes
    config_addr: Optional[str] = None  # Configuration memory start address
    config_size: int = 0  # Configuration memory size in bytes
    gpr_total_size: int = 0  # Total General Purpose Register size in bytes
    gpr_sectors: list = None  # List of GPR memory sectors
    architecture: Optional[str] = None
    series: Optional[str] = None
    
    def __post_init__(self):
        """Initialize empty lists."""
        if self.gpr_sectors is None:
            self.gpr_sectors = []


@dataclass
class GprSector:
    """General Purpose Register memory sector information."""
    
    name: str
    start_addr: int
    end_addr: int
    size: int
    bank: Optional[str] = None
