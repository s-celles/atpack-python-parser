# Device Specifications Extraction

This module provides comprehensive device specifications extraction from AtPack files, specifically designed for PIC microcontrollers. It extracts critical information including f_cpu, memory sizes, EEPROM details, configuration memory, and GPR (General Purpose Register) information.

## Key Features

### ✅ Advanced Memory Analysis
The extractor provides comprehensive analysis of all memory regions including proper handling of memory shadows and mirrors.

### ✅ shadowidref-aware parsing
The extractor properly handles the `edc:shadowidref` attribute to avoid double-counting memory regions that are mirrors of other memory areas.

### 📊 Comprehensive Memory Analysis
- **Program Memory (Flash)**: Size in words
- **RAM Memory**: Total size in bytes with detailed GPR sector breakdown
- **EEPROM**: Address and size (when available)
- **Configuration Memory**: Address and size
- **GPR Sectors**: Detailed breakdown by memory bank

### 🏦 GPR (General Purpose Register) Details
Provides detailed information about GPR memory sectors including:
- Memory bank assignments
- Start and end addresses
- Individual sector sizes
- Bank-specific organization

## Usage

### Python API

#### Single Device Extraction
```python
from atpack_parser import AtPackParser

# Initialize parser
parser = AtPackParser("path/to/atpack.atpack")

# Extract specifications for a specific device
specs = parser.get_device_specs("PIC16F877A")

print(f"Device: {specs.device_name}")
print(f"Program Memory: {specs.maximum_size} words")
print(f"Total RAM: {specs.maximum_ram_size} bytes")
print(f"GPR Total: {specs.gpr_total_size} bytes")

# GPR sector details
for sector in specs.gpr_sectors:
    print(f"  {sector.name}: 0x{sector.start_addr:04X}-0x{sector.end_addr:04X} ({sector.size} bytes)")
```

#### Bulk Extraction
```python
# Extract specifications for all devices
all_specs = parser.get_all_device_specs()

print(f"Extracted specs for {len(all_specs)} devices")

# Export to JSON
import json
specs_data = [spec.model_dump() for spec in all_specs]
with open('device_specs.json', 'w') as f:
    json.dump(specs_data, f, indent=2)
```

### Command Line Interface

#### Basic Usage
```bash
# Extract specifications for a single device
atpack devices specs PIC16F877A path/to/atpack.atpack

# Show detailed GPR information
atpack devices specs PIC16F877A path/to/atpack.atpack --show-gpr
```

#### Export Options
```bash
# Export to JSON
atpack devices specs PIC16F877A path/to/atpack.atpack --format json --output specs.json

# Export to CSV
atpack devices specs PIC16F877A path/to/atpack.atpack --format csv --output specs.csv
```

## Data Model

### DeviceSpecs
The main specifications data structure:

```python
@dataclass
class DeviceSpecs:
    device_name: str
    f_cpu: Optional[str] = None  # CPU frequency (configurable for most PICs)
    maximum_ram_size: int = 0  # Total RAM size in bytes
    maximum_size: int = 0  # Program memory size (Flash) in words
    eeprom_addr: Optional[str] = None  # EEPROM start address
    eeprom_size: int = 0  # EEPROM size in bytes
    config_addr: Optional[str] = None  # Configuration memory start address
    config_size: int = 0  # Configuration memory size in bytes
    gpr_total_size: int = 0  # Total General Purpose Register size in bytes
    gpr_sectors: List[GprSector] = []  # List of GPR memory sectors
    architecture: Optional[str] = None
    series: Optional[str] = None
```

### GprSector
GPR memory sector information:

```python
@dataclass
class GprSector:
    name: str
    start_addr: int
    end_addr: int
    size: int
    bank: Optional[str] = None
```

## shadowidref Handling

The `edc:shadowidref` attribute in PIC files indicates memory sectors that are mirrors or shadows of other memory regions. These should not be counted toward the total memory size to avoid double-counting.

The extractor automatically:
1. Detects `shadowidref` attributes on memory sectors
2. Skips sectors with `shadowidref` when calculating totals
3. Only counts actual physical memory regions

Example in XML:
```xml
<edc:GPRDataSector edc:beginaddr="0x20" edc:endaddr="0x6F" edc:bank="0"/>
<edc:GPRDataSector edc:beginaddr="0x70" edc:endaddr="0x7F" edc:bank="0" edc:shadowidref="GPR_BANK0_20_6F"/>
```

In this case, the second sector would be skipped as it's a shadow of the first.

## Examples

See the `examples/` directory for complete usage examples:

- `extract_device_specs.py` - Basic usage and CSV export
- `validate_shadowidref.py` - Validation of shadowidref handling
- `complete_specs_demo.py` - Comprehensive demonstration

## Compatibility

This feature is currently supported for:
- ✅ PIC microcontrollers (Microchip AtPack files)
- ❌ ATMEL microcontrollers (not yet implemented)

## Output Format

The extracted data uses a standardized CSV format for compatibility and interchange:

| Field | Description |
|-------|-------------|
| device_name | Device name (e.g., "PIC16F877A") |
| f_cpu | CPU frequency ("User configurable" for most PICs) |
| maximum_ram_size | Total RAM in bytes |
| maximum_size | Program memory in words |
| eeprom_addr | EEPROM start address (e.g., "0x2100") |
| eeprom_size | EEPROM size in bytes |
| config_addr | Config memory start address (e.g., "0x2007") |
| config_size | Config memory size in bytes |
| gpr_total_size | Total GPR memory in bytes |
| architecture | Architecture ("PIC") |
| series | Series (e.g., "PIC16") |
