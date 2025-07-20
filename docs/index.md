# AtPack Parser

A Python library and CLI tool for parsing ATMEL and Microchip AtPack files.

## Overview

AtPack Parser is a comprehensive Python library that enables you to extract and analyze information from ATMEL and Microchip AtPack files. These files contain detailed information about microcontrollers including device specifications, memory layouts, registers, peripherals, and fuse settings.

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
print(f"Device: {device.name}, Family: {device.family}")
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