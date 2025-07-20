# AtPack Parser

A Python library and CLI tool for parsing AtPack files.

!!! warning "Legal Notice"
    
    **Important Legal Information**
    
    - This project is **unofficial** and is **not supported, endorsed, or affiliated** with Microchip Technology Inc., ATMEL Corporation, or any of their subsidiaries.
    - **ATMEL** and **Microchip** are registered trademarks of Microchip Technology Inc.
    - **AtPack files contain proprietary data** and are subject to their own individual licenses and terms of use.
    - **AtPack files are NOT distributed** with this project due to licensing restrictions.
    - Users must **obtain AtPack files directly** from the official Microchip Packs Repository.
    - This parser is provided "as-is" for **educational and development purposes** only.
    - The authors of this project assume **no responsibility** for any misuse or license violations.
    
    Please ensure you comply with all applicable licenses and terms of service when using AtPack files.

!!! warning
    This project is currently in active development. APIs may change between versions.

!!! info "AI-Generated Content Notice"
    A significant portion of this project's content (including code, documentation, and examples) has been generated using AI assistance. Please review all code and documentation carefully before use in production environments. We recommend thorough testing and validation of any AI-generated components.

## Overview

AtPack Parser is a comprehensive Python library that enables you to extract and analyze information from AtPack files. These files contain detailed information about microcontrollers including device specifications, memory layouts, registers, peripherals, and fuse settings. Currently, AtPack Parser supports (at least partially) ATDF (ATMEL) and PIC formats (Microchip).

## Key Features

- 📦 **Parse ATMEL and Microchip AtPack files** - Support for both ATDF and PIC formats
- 🔍 **Extract device information** - Get detailed specs, memory layouts, registers, and fuses  
- 💻 **Command-line interface** - Easy-to-use CLI with hierarchical commands
- 🐍 **Python API** - Full programmatic access for integration into your projects
- ✨ **Rich output** - Beautiful formatting with colors and tables
- 📊 **Export capabilities** - Generate reports and data exports

## Quick Start

### Installation

```bash
pip install git+https://github.com/s-celles/atpack-python-parser
# or when (if) registered on PyPI
pip install atpack-parser
```

### Basic Usage

#### CLI
```bash
# List all devices in an AtPack file
atpack devices list path/to/atpack.atpack

# Get detailed device information
atpack devices info PIC16F877 path/to/atpack.atpack

# Show memory layout
atpack memory PIC16F877 path/to/atpack.atpack
```

#### Python API
```python
from atpack_parser import AtPackParser

# Parse an AtPack file
parser = AtPackParser("path/to/atpack.atpack")

# Get device information
device = parser.get_device("PIC16F877")
print(f"Device: {device.name}")
print(f"Family: {device.family}")
print(f"Architecture: {device.architecture}")

# Access memory segments
for segment in device.memory_segments:
    print(f"{segment.name}: {segment.size} bytes at 0x{segment.start:04X}")
```

## Supported Formats

- **ATMEL AtPack files** (.atpack) - Uses ATDF (ATMEL Device File) format
- **Microchip AtPack files** (.atpack) - Uses PIC format for newer Microchip devices

## Use Cases

- **Firmware Development** - Extract register definitions and memory maps
- **Hardware Analysis** - Understand device capabilities and peripherals  
- **Tool Development** - Build development tools that need device information
- **Documentation** - Generate device documentation and specifications
- **PlatformIO Integration** - Generate board definitions and configurations

## Getting Help

- 📖 Browse the [documentation sections](installation.md) for detailed guides
- 🔧 Check out the [examples](examples.md) for common usage patterns
- 📚 Refer to the [API reference](api-reference.md) for complete API documentation
- 🐛 Report issues on [GitHub](https://github.com/s-celles/atpack-python-parser/issues)