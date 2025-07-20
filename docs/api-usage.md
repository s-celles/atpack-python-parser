# Python API

The AtPack Parser provides a comprehensive Python API for programmatic access to AtPack file contents.

## Basic Usage

### Importing the Library

```python
from atpack_parser import AtPackParser
from atpack_parser.models import Device, Register, MemorySegment
```

### Creating a Parser Instance

```python
# Parse an AtPack file
parser = AtPackParser("path/to/atpack.atpack")

# Or use pathlib.Path
from pathlib import Path
parser = AtPackParser(Path("path/to/atpack.atpack"))
```

### Getting Device Information

```python
# List all devices in the AtPack
devices = parser.get_devices()
print(f"Found {len(devices)} devices")

# Get a specific device
device = parser.get_device("PIC16F877")
if device:
    print(f"Device: {device.name}")
    print(f"Family: {device.family}")
    print(f"Architecture: {device.architecture}")
    # Access memory segments instead of direct flash/ram/eeprom properties
    for segment in device.memory_segments:
        print(f"{segment.name}: {segment.size} bytes at 0x{segment.start:04X}")
```

## Working with Device Data

### Device Properties

The `Device` model provides access to all device information:

```python
device = parser.get_device("ATmega16")

# Basic information
print(f"Name: {device.name}")
print(f"Family: {device.family}")
print(f"Architecture: {device.architecture}")
print(f"Package: {device.package}")

# Memory information
print(f"Flash: {device.flash_size} bytes")
print(f"RAM: {device.ram_size} bytes") 
print(f"EEPROM: {device.eeprom_size} bytes")

# Additional properties
print(f"Max frequency: {device.max_frequency} Hz")
print(f"Operating voltage: {device.voltage_min}V - {device.voltage_max}V")
print(f"Temperature range: {device.temp_min}°C - {device.temp_max}°C")
```

### Memory Layout

```python
# Get memory segments
memory_segments = parser.get_memory_layout("ATmega16")

for segment in memory_segments:
    print(f"Segment: {segment.name}")
    print(f"  Start: 0x{segment.start_address:04X}")
    print(f"  Size: {segment.size} bytes")
    print(f"  Type: {segment.type}")
    print(f"  Access: {segment.access}")
```

### Registers and Peripherals

```python
# Get all registers for a device
registers = parser.get_device_registers("ATmega16")

# Filter by peripheral
usart_registers = [r for r in registers if r.peripheral == "USART"]

for register in usart_registers:
    print(f"Register: {register.name}")
    print(f"  Address: 0x{register.address:04X}")
    print(f"  Size: {register.size} bytes")
    print(f"  Description: {register.description}")
    
    # Access bit fields
    for bitfield in register.bitfields:
        print(f"    Bit {bitfield.bit_range}: {bitfield.name}")
        print(f"      Description: {bitfield.description}")
```

### Fuse Bits

```python
# Get fuse information
fuses = parser.get_device_fuses("ATmega16")

for fuse in fuses:
    print(f"Fuse: {fuse.name}")
    print(f"  Address: 0x{fuse.address:04X}")
    print(f"  Default: 0x{fuse.default_value:02X}")
    
    # Fuse bit fields
    for field in fuse.bitfields:
        print(f"    Bits {field.bit_range}: {field.name}")
        print(f"      Values: {field.values}")
```

## Advanced Usage

### Error Handling

```python
from atpack_parser.exceptions import AtPackParseError, DeviceNotFoundError

try:
    parser = AtPackParser("invalid.atpack")
except AtPackParseError as e:
    print(f"Failed to parse AtPack: {e}")

try:
    device = parser.get_device("NonExistentDevice")
except DeviceNotFoundError as e:
    print(f"Device not found: {e}")
```

### Working with Multiple AtPacks

```python
# Parse multiple AtPack files
atmel_parser = AtPackParser("Atmel.ATmega_DFP.2.2.509.atpack")
pic_parser = AtPackParser("Microchip.PIC16Fxxx_DFP.1.7.162.atpack")

# Get all devices from both
all_devices = []
all_devices.extend(atmel_parser.get_devices())
all_devices.extend(pic_parser.get_devices())

print(f"Total devices: {len(all_devices)}")
```

### Device Search and Filtering

```python
# Search devices by name pattern
import re

devices = parser.get_devices()

# Find all ATmega devices
atmega_devices = [d for d in devices if d.name.startswith("ATmega")]

# Find devices with specific flash size
flash_16k_devices = [d for d in devices if d.flash_size == 16384]

# Find devices by regex pattern
pattern = re.compile(r"ATmega\d{2}A?$")
matched_devices = [d for d in devices if pattern.match(d.name)]
```

### Data Export

```python
import json
from pathlib import Path

# Export device data to JSON
devices = parser.get_devices()
device_data = [
    {
        "name": d.name,
        "family": d.family,
        "flash_size": d.flash_size,
        "ram_size": d.ram_size,
    }
    for d in devices
]

with open("devices.json", "w") as f:
    json.dump(device_data, f, indent=2)

# Export register definitions
device = parser.get_device("ATmega16")
registers = parser.get_device_registers("ATmega16")

register_data = [
    {
        "name": r.name,
        "address": r.address,
        "size": r.size,
        "peripheral": r.peripheral,
        "bitfields": [
            {
                "name": bf.name,
                "bit_range": bf.bit_range,
                "description": bf.description
            }
            for bf in r.bitfields
        ]
    }
    for r in registers
]

with open(f"{device.name}_registers.json", "w") as f:
    json.dump(register_data, f, indent=2)
```

### Custom Processing

```python
# Create a device comparison report
def compare_devices(parser, device_names):
    comparison = {}
    
    for name in device_names:
        device = parser.get_device(name)
        if device:
            comparison[name] = {
                "flash": device.flash_size,
                "ram": device.ram_size,
                "eeprom": device.eeprom_size,
                "max_freq": device.max_frequency,
                "package": device.package
            }
    
    return comparison

# Compare ATmega devices
atmega_comparison = compare_devices(parser, ["ATmega16", "ATmega32", "ATmega64"])
for name, specs in atmega_comparison.items():
    print(f"{name}: Flash={specs['flash']}, RAM={specs['ram']}")
```

### Integration with Other Tools

```python
# Generate PlatformIO board definitions
def generate_platformio_board(device):
    board_config = {
        "build": {
            "mcu": device.name.lower(),
            "f_cpu": device.max_frequency,
            "core": "arduino"
        },
        "upload": {
            "maximum_size": device.flash_size,
            "maximum_ram_size": device.ram_size,
            "protocol": "avrisp"
        },
        "name": device.name
    }
    return board_config

# Generate board configs for all devices
devices = parser.get_devices()
board_configs = {d.name.lower(): generate_platformio_board(d) for d in devices}
```

## Performance Tips

### Lazy Loading

The parser uses lazy loading to improve performance:

```python
# This is fast - doesn't parse everything
parser = AtPackParser("large.atpack")

# This triggers parsing only when needed
devices = parser.get_devices()  # Parses device list
registers = parser.get_device_registers("ATmega16")  # Parses registers for this device
```

### Caching Results

```python
# Cache frequently accessed data
device_cache = {}

def get_cached_device(parser, name):
    if name not in device_cache:
        device_cache[name] = parser.get_device(name)
    return device_cache[name]
```

### Memory Management

```python
# For processing many AtPacks, consider memory usage
import gc

atpack_files = ["file1.atpack", "file2.atpack", "file3.atpack"]
all_devices = []

for file in atpack_files:
    parser = AtPackParser(file)
    devices = parser.get_devices()
    all_devices.extend(devices)
    
    # Clean up parser to free memory
    del parser
    gc.collect()
```
