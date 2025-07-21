"""Pydantic models for AtPack data structures."""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class DeviceFamily(str, Enum):
    """Device family types."""

    ATMEL = "ATMEL"
    PIC = "PIC"
    UNSUPPORTED = "UNSUPPORTED"


class ElectricalParameter(BaseModel):
    """Electrical parameter specification."""

    name: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    typical_value: Optional[float] = None
    nominal_value: Optional[float] = None
    unit: Optional[str] = None
    conditions: Optional[str] = None


class PowerSpecification(BaseModel):
    """Power supply specifications for PIC devices."""

    vdd_min: Optional[float] = None
    vdd_max: Optional[float] = None
    vdd_nominal: Optional[float] = None
    vdd_min_default: Optional[float] = None
    vdd_max_default: Optional[float] = None
    vpp_min: Optional[float] = None  # Programming voltage
    vpp_max: Optional[float] = None
    vpp_default: Optional[float] = None
    has_high_voltage_mclr: Optional[bool] = None


class OscillatorConfig(BaseModel):
    """Oscillator configuration option for PIC devices."""

    name: str
    description: str
    config_value: Optional[str] = None
    config_mask: Optional[str] = None
    when_condition: Optional[str] = None
    c_name: Optional[str] = None
    legacy_alias: Optional[str] = None


class ProgrammingInterface(BaseModel):
    """Programming interface specifications."""

    erase_algorithm: Optional[str] = None
    has_low_voltage_programming: Optional[bool] = None
    low_voltage_threshold: Optional[float] = None
    memory_technology: Optional[str] = None
    programming_tries: Optional[int] = None
    has_row_erase_command: Optional[bool] = None

    # Programming wait times
    wait_times: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    row_sizes: Dict[str, int] = Field(default_factory=dict)


class PinFunction(BaseModel):
    """Pin function/alternative name."""

    name: str
    description: Optional[str] = None


class PinInfo(BaseModel):
    """Pin information including alternative functions."""

    physical_pin: Optional[int] = None
    primary_function: Optional[str] = None
    alternative_functions: List[PinFunction] = Field(default_factory=list)
    pin_type: Optional[str] = None  # digital, analog, power, etc.


class DebugCapabilities(BaseModel):
    """Debug and hardware tool capabilities."""

    hardware_breakpoint_count: Optional[int] = None
    has_data_capture: Optional[bool] = None
    id_byte: Optional[str] = None


class ArchitectureInfo(BaseModel):
    """Device architecture information."""

    instruction_set: Optional[str] = None
    hardware_stack_depth: Optional[int] = None
    code_word_size: Optional[int] = None
    data_word_size: Optional[int] = None


class AtmelPackageVariant(BaseModel):
    """ATMEL package variant information."""

    package: str
    pinout: str
    order_code: Optional[str] = None
    temp_min: Optional[float] = None
    temp_max: Optional[float] = None
    speed_max: Optional[int] = None  # Hz
    vcc_min: Optional[float] = None
    vcc_max: Optional[float] = None


class AtmelPinoutInfo(BaseModel):
    """ATMEL pinout information."""

    name: str
    caption: Optional[str] = None
    pin_count: int
    pins: List[Dict[str, str]] = Field(default_factory=list)  # position -> pad mapping


class AtmelProgrammingInterface(BaseModel):
    """ATMEL programming interface specifications."""

    name: str
    interface_type: str
    properties: Dict[str, Any] = Field(default_factory=dict)


class AtmelClockInfo(BaseModel):
    """ATMEL clock system information."""

    clock_modules: List[Dict[str, Any]] = Field(default_factory=list)
    clock_properties: List[Dict[str, Any]] = Field(default_factory=list)
    max_frequency: Optional[int] = None


class AtmelGpioInfo(BaseModel):
    """ATMEL GPIO port information."""

    port_name: str
    instances: List[Dict[str, Any]] = Field(default_factory=list)
    pin_count: Optional[int] = None


class MemorySegment(BaseModel):
    """Memory segment information."""

    name: str
    start: int
    size: int
    type: Optional[str] = None
    page_size: Optional[int] = None
    section: Optional[str] = None
    address_space: Optional[str] = None
    parent_name: Optional[str] = None  # Name of parent container (e.g., "ProgramSpace", "DataSpace")
    children: List["MemorySegment"] = Field(default_factory=list)  # Child segments
    level: int = 0  # Hierarchy level (0=top level, 1=child, etc.)


class MemorySpace(BaseModel):
    """Memory space/container information for hierarchical memory layout."""
    
    name: str
    space_type: str  # "ProgramSpace", "DataSpace", "EEDataSpace", "address-space", etc.
    start: Optional[int] = None
    size: Optional[int] = None
    segments: List[MemorySegment] = Field(default_factory=list)


class RegisterBitfield(BaseModel):
    """Register bitfield information."""

    name: str
    caption: Optional[str] = None
    mask: int
    bit_offset: int
    bit_width: int
    values: Optional[Dict[int, str]] = None


class Register(BaseModel):
    """Register information."""

    name: str
    caption: Optional[str] = None
    offset: int
    size: int
    mask: Optional[int] = None
    initial_value: Optional[int] = None
    access: Optional[str] = None
    bitfields: List[RegisterBitfield] = Field(default_factory=list)


class RegisterGroup(BaseModel):
    """Register group information."""

    name: str
    caption: Optional[str] = None
    registers: List[Register] = Field(default_factory=list)


class Module(BaseModel):
    """Device module/peripheral information."""

    name: str
    caption: Optional[str] = None
    register_groups: List[RegisterGroup] = Field(default_factory=list)


class FuseBitfield(BaseModel):
    """Fuse bitfield information."""

    name: str
    description: Optional[str] = None
    bit_offset: int
    bit_width: int
    values: Optional[Dict[int, str]] = None


class Fuse(BaseModel):
    """Fuse configuration."""

    name: str
    offset: int
    size: int
    mask: Optional[int] = None
    default_value: Optional[int] = None
    bitfields: List[FuseBitfield] = Field(default_factory=list)


class Interrupt(BaseModel):
    """Interrupt information."""

    index: int
    name: str
    caption: Optional[str] = None


class DeviceSignature(BaseModel):
    """Device signature information."""

    name: str
    address: Optional[int] = None
    value: int


class ElectricalParameter(BaseModel):
    """Electrical parameter information."""

    name: str
    group: str
    caption: Optional[str] = None
    description: Optional[str] = None
    min_value: Optional[float] = None
    typical_value: Optional[float] = None
    max_value: Optional[float] = None
    unit: Optional[str] = None
    conditions: Optional[str] = None


class ConfigWord(BaseModel):
    """Configuration word for PIC devices."""

    name: str
    address: int
    default_value: int
    mask: int
    bitfields: List[RegisterBitfield] = Field(default_factory=list)


class Device(BaseModel):
    """Device information."""

    name: str
    family: DeviceFamily
    architecture: Optional[str] = None
    series: Optional[str] = None

    # Memory information
    memory_segments: List[MemorySegment] = Field(default_factory=list)
    memory_spaces: List[MemorySpace] = Field(default_factory=list)  # Hierarchical memory layout

    # Modules and peripherals
    modules: List[Module] = Field(default_factory=list)

    # Configuration
    fuses: List[Fuse] = Field(default_factory=list)
    config_words: List[ConfigWord] = Field(default_factory=list)

    # Other information
    interrupts: List[Interrupt] = Field(default_factory=list)
    signatures: List[DeviceSignature] = Field(default_factory=list)
    electrical_parameters: List[ElectricalParameter] = Field(default_factory=list)

    # PIC-specific information (useful for PlatformIO board definitions)
    power_specs: Optional[PowerSpecification] = None
    oscillator_configs: List[OscillatorConfig] = Field(default_factory=list)
    programming_interface: Optional[ProgrammingInterface] = None
    pinout: List[PinInfo] = Field(default_factory=list)
    debug_capabilities: Optional[DebugCapabilities] = None
    architecture_info: Optional[ArchitectureInfo] = None
    detected_peripherals: List[str] = Field(default_factory=list)

    # ATMEL-specific information (useful for PlatformIO board definitions)
    atmel_package_variants: List[AtmelPackageVariant] = Field(default_factory=list)
    atmel_pinouts: List[AtmelPinoutInfo] = Field(default_factory=list)
    atmel_programming_interfaces: List[AtmelProgrammingInterface] = Field(
        default_factory=list
    )
    atmel_clock_info: Optional[AtmelClockInfo] = None
    atmel_gpio_info: List[AtmelGpioInfo] = Field(default_factory=list)

    # Additional metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AtPackMetadata(BaseModel):
    """AtPack file metadata."""

    name: str
    description: Optional[str] = None
    vendor: Optional[str] = None
    version: Optional[str] = None
    url: Optional[str] = None


class AtPack(BaseModel):
    """Complete AtPack information."""

    metadata: AtPackMetadata
    devices: List[Device] = Field(default_factory=list)
    device_family: DeviceFamily = DeviceFamily.UNSUPPORTED


# Forward reference for self-referential MemorySegment
MemorySegment.model_rebuild()
