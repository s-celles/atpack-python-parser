# API Reference

This page provides complete API documentation for AtPack Parser.

## Core Classes

### AtPackParser

The main parser class for working with AtPack files.

::: atpack_parser.parser.AtPackParser

### Device Models

Data models representing device information.

::: atpack_parser.models.Device

::: atpack_parser.models.MemorySegment

::: atpack_parser.models.Register

::: atpack_parser.models.RegisterBitfield

::: atpack_parser.models.Fuse

## Parser Modules

### ATDF Parser

For parsing ATMEL Device Files (ATDF format).

::: atpack_parser.parser.atdf.AtdfParser

### PIC Parser

For parsing Microchip PIC device files.

::: atpack_parser.parser.pic.PicParser

### PDSC Parser

For parsing Pack Description (PDSC) files.

::: atpack_parser.parser.pdsc.PdscParser

## Exceptions

### AtPackError

Base exception for parsing errors.

::: atpack_parser.exceptions.AtPackError

### DeviceNotFoundError

Exception raised when a device is not found.

::: atpack_parser.exceptions.DeviceNotFoundError

## CLI Interface

### Command Line Application

The CLI application built with Typer.

::: atpack_parser.cli

## Usage Examples

### Basic Parser Usage

```python
from atpack_parser import AtPackParser

# Initialize parser
parser = AtPackParser("path/to/atpack.atpack")

# Get devices
devices = parser.get_devices()
device = parser.get_device("PIC16F877")

# Get device data
registers = parser.get_device_registers("PIC16F877")
memory = parser.get_device_memory("PIC16F877")
```

### Error Handling

```python
from atpack_parser import AtPackParser
from atpack_parser.exceptions import AtPackError, DeviceNotFoundError

try:
    parser = AtPackParser("invalid.atpack")
    device = parser.get_device("NonExistentDevice")
except AtPackError as e:
    print(f"Parse error: {e}")
except DeviceNotFoundError as e:
    print(f"Device not found: {e}")
```

### Model Properties

#### Device Model

| Property | Type | Description |
|----------|------|-------------|
| `name` | `str` | Device name (e.g., "PIC16F877") |
| `family` | `DeviceFamily` | Device family (ATMEL/PIC) |
| `architecture` | `Optional[str]` | CPU architecture |
| `series` | `Optional[str]` | Device series |
| `memory_segments` | `List[MemorySegment]` | Memory layout |
| `modules` | `List[Module]` | Device modules/peripherals |
| `fuses` | `List[Fuse]` | Fuse configuration |

#### Register Model

| Property | Type | Description |
|----------|------|-------------|
| `name` | `str` | Register name (e.g., "PORTB") |
| `caption` | `Optional[str]` | Register description |
| `offset` | `int` | Register address offset |
| `size` | `int` | Register size in bytes |
| `mask` | `Optional[int]` | Register mask |
| `bitfields` | `List[RegisterBitfield]` | List of bit fields |
| `access` | `Optional[str]` | Access type (read/write) |

#### MemorySegment Model

| Property | Type | Description |
|----------|------|-------------|
| `name` | `str` | Segment name (e.g., "FLASH") |
| `start` | `int` | Starting address |
| `size` | `int` | Segment size in bytes |
| `type` | `Optional[str]` | Memory type |
| `access` | `Optional[str]` | Access permissions |

#### RegisterBitfield Model

| Property | Type | Description |
|----------|------|-------------|
| `name` | `str` | Bit field name |
| `caption` | `Optional[str]` | Bit field description |
| `mask` | `int` | Bit mask |
| `bit_offset` | `int` | Starting bit position |
| `bit_width` | `int` | Number of bits |
| `values` | `Optional[Dict[int, str]]` | Possible values |

## Method Reference

### AtPackParser Methods

#### `__init__(atpack_path: Union[str, Path])`

Initialize the parser with an AtPack file path.

**Parameters:**
- `atpack_path`: Path to the AtPack file

**Raises:**
- `FileNotFoundError`: If the file doesn't exist

#### `get_devices() -> List[str]`

Get all device names in the AtPack.

**Returns:**
- List of device names

#### `get_device(device_name: str) -> Device`

Get a specific device by name.

**Parameters:**
- `device_name`: Name of the device

**Returns:**
- Device object

**Raises:**
- `DeviceNotFoundError`: If device is not found

#### `get_device_registers(device_name: str) -> List[Register]`

Get all registers for a device.

**Parameters:**
- `device_name`: Name of the device

**Returns:**
- List of Register objects

#### `get_device_memory(device_name: str) -> List[MemorySegment]`

Get memory layout for a device.

**Parameters:**
- `device_name`: Name of the device

**Returns:**
- List of MemorySegment objects

## Version Information

To get version information:

```python
import atpack_parser
print(atpack_parser.__version__)
```

## Contributing

For information about contributing to the API, see the [Development](development.md) section.
