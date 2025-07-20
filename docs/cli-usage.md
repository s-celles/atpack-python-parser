# CLI Usage

The AtPack Parser provides a powerful command-line interface for working with AtPack files.

## Basic Command Structure

```bash
atpack [OPTIONS] COMMAND [ARGS]...
```

## Global Options

- `--help` - Show help message
- `--version` - Show version information

## Commands Overview

### Files Commands

Work with AtPack files and directories:

```bash
# List all AtPack files in a directory
atpack files list /path/to/atpack/directory

# Show information about a specific AtPack file
atpack files info /path/to/file.atpack
```

### Device Commands

Extract and display device information:

```bash
# List all devices in an AtPack file
atpack devices list /path/to/file.atpack

# Get detailed information about a specific device
atpack devices info DEVICE_NAME /path/to/file.atpack

# Search for devices by name pattern
atpack devices search "ATmega*" /path/to/file.atpack
```

### Memory Commands

Analyze device memory layout:

```bash
# Show memory map for a device
atpack memory DEVICE_NAME /path/to/file.atpack

# Show specific memory segment
atpack memory DEVICE_NAME /path/to/file.atpack --segment flash

# Export memory layout to file
atpack memory DEVICE_NAME /path/to/file.atpack --output memory.json
```

### Register Commands

Work with device registers and peripherals:

```bash
# List all registers for a device
atpack registers DEVICE_NAME /path/to/file.atpack

# Show specific peripheral registers
atpack registers DEVICE_NAME /path/to/file.atpack --peripheral USART

# Export registers to file
atpack registers DEVICE_NAME /path/to/file.atpack --output registers.json
```

### Fuse Commands

Extract fuse bit information:

```bash
# Show fuse configuration for a device
atpack fuses DEVICE_NAME /path/to/file.atpack

# Export fuse information
atpack fuses DEVICE_NAME /path/to/file.atpack --output fuses.json
```

## Detailed Examples

### Working with ATMEL AtPacks

```bash
# Download an ATMEL AtPack (example)
wget http://packs.download.atmel.com/Atmel.ATmega_DFP.2.2.509.atpack

# List all ATmega devices
atpack devices list Atmel.ATmega_DFP.2.2.509.atpack

# Get ATmega16 information
atpack devices info ATmega16 Atmel.ATmega_DFP.2.2.509.atpack

# Show ATmega16 memory layout
atpack memory ATmega16 Atmel.ATmega_DFP.2.2.509.atpack

# List ATmega16 registers
atpack registers ATmega16 Atmel.ATmega_DFP.2.2.509.atpack
```

### Working with Microchip AtPacks

```bash
# Work with a PIC AtPack
atpack devices list Microchip.PIC16Fxxx_DFP.1.7.162.atpack

# Get PIC16F877A information  
atpack devices info PIC16F877A Microchip.PIC16Fxxx_DFP.1.7.162.atpack

# Show memory layout
atpack memory PIC16F877A Microchip.PIC16Fxxx_DFP.1.7.162.atpack
```

### Batch Operations

```bash
# Process all AtPacks in a directory
for pack in *.atpack; do
    echo "Processing $pack"
    atpack devices list "$pack" > "${pack%.atpack}_devices.txt"
done
```

### Output Formatting

The CLI supports rich terminal output with colors and tables. You can control the output format:

```bash
# JSON output
atpack devices info ATmega16 file.atpack --format json

# Plain text output (no colors)
atpack devices info ATmega16 file.atpack --no-color

# Verbose output
atpack devices info ATmega16 file.atpack --verbose
```

### Export Options

Most commands support exporting data to files:

```bash
# Export device list to JSON
atpack devices list file.atpack --output devices.json

# Export to CSV
atpack devices list file.atpack --output devices.csv --format csv

# Export to XML
atpack registers ATmega16 file.atpack --output registers.xml --format xml
```

## Advanced Usage

### Pipeline Integration

The CLI is designed to work well in scripts and pipelines:

```bash
# Count devices in an AtPack
atpack devices list file.atpack --format json | jq length

# Extract device names only
atpack devices list file.atpack --format json | jq -r '.[].name'

# Find devices with specific memory size
atpack devices list file.atpack --format json | jq '.[] | select(.flash_size == 16384)'
```

### Configuration Files

You can create configuration files to avoid repeating common options:

```bash
# Create ~/.atpack_config.yaml
default_format: json
output_directory: ./exports
verbose: true
```

## Error Handling

The CLI provides helpful error messages:

- **File not found** - Clear message about missing AtPack files
- **Invalid device** - Suggestions for similar device names
- **Parse errors** - Details about XML parsing issues
- **Permission errors** - Instructions for resolving access issues

## Getting Help

Use `--help` with any command to get detailed usage information:

```bash
atpack --help
atpack devices --help
atpack devices info --help
```
