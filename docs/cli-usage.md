# CLI Usage

The AtPack Parser provides a powerful command-line interface for working with AtPack files.

## Basic Command Structure

```bash
atpack [OPTIONS] COMMAND [ARGS]...
```

## Global Options

- `--help` - Show help message
- `--version` - Show version information

```
atpack --help

 Usage: atpack [OPTIONS] COMMAND [ARGS]...

 🔧 AtPack Parser - Parse AtPack files


╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --version             -v        Show version                                                                                                                                                                  │
│ --install-completion            Install completion for the current shell.                                                                                                                                     │
│ --show-completion               Show completion for the current shell, to copy it or customize the installation.                                                                                              │
│ --help                          Show this message and exit.                                                                                                                                                   │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ scan        🔍 Scan directory for AtPack files.                                                                                                                                                               │
│ help-tree   🌳 Show the complete command tree structure with examples.                                                                                                                                        │
│ help        ❓ Get interactive help for commands.                                                                                                                                                             │
│ files       📁 AtPack file management                                                                                                                                                                         │
│ devices     🔌 Device information                                                                                                                                                                             │
│ memory      💾 Memory information                                                                                                                                                                             │
│ registers   📋 Register information                                                                                                                                                                           │
│ config      ⚙️ Configuration information                                                                                                                                                                       │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## Help tree command

```

atpack help-tree
╭──────────────────────────────────────────────────────────────────────────────────────── 🌳 Command Tree with Examples ────────────────────────────────────────────────────────────────────────────────────────╮
│                                                                                                                                                                                                               │
│  🔧 atpack - AtPack Parser CLI                                                                                                                                                                                │
│  ├── 📁 files - AtPack file management                                                                                                                                                                        │
│  │   ├── list - List files in an AtPack                                                                                                                                                                       │
│  │   └── info - Show AtPack file information                                                                                                                                                                  │
│  ├── 🔌 devices - Device information                                                                                                                                                                          │
│  │   ├── list - List all devices                                                                                                                                                                              │
│  │   └── info - Show device details                                                                                                                                                                           │
│  ├── 💾 memory - Memory information                                                                                                                                                                           │
│  │   └── show - Show memory layout                                                                                                                                                                            │
│  ├── 📋 registers - Register information                                                                                                                                                                      │
│  │   ├── list - List registers                                                                                                                                                                                │
│  │   └── show - Show register details                                                                                                                                                                         │
│  ├── ⚙️ config - Configuration information                                                                                                                                                                     │
│  │   └── show - Show configuration information                                                                                                                                                                │
│  ├── 🔍 scan - Scan directory for AtPack files                                                                                                                                                                │
│  └── 🌳 help-tree - Show command tree structure                                                                                                                                                               │
│                                                                                                                                                                                                               │
│  📚 Usage Examples:                                                                                                                                                                                           │
│    atpack files list mypack.atpack                                                                                                                                                                            │
│    atpack files info mypack.atpack                                                                                                                                                                            │
│                                                                                                                                                                                                               │
│    atpack devices list mypack.atpack                                                                                                                                                                          │
│    atpack devices info ATmega16 mypack.atpack                                                                                                                                                                 │
│                                                                                                                                                                                                               │
│    atpack memory show ATmega16 mypack.atpack                                                                                                                                                                  │
│                                                                                                                                                                                                               │
│    atpack registers list ATmega16 mypack.atpack                                                                                                                                                               │
│    atpack registers list ATmega16 mypack.atpack --module GPIO                                                                                                                                                 │
│    atpack registers show ATmega16 PORTB mypack.atpack                                                                                                                                                         │
│                                                                                                                                                                                                               │
│    atpack config show PIC16F876A mypack.atpack                                                                                                                                                                │
│    atpack config show PIC16F876A mypack.atpack --type fuses                                                                                                                                                   │
│                                                                                                                                                                                                               │
│    atpack scan ./atpacks/ --format json                                                                                                                                                                       │
│                                                                                                                                                                                                               │
│                                                                                                                                                                                                               │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## Commands Overview

### Scan for AtPack Files in a Directory


```
atpack scan .\atpacks\
                            🔍 AtPack Files in atpacks
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━┓
┃ Path                                   ┃ Name    ┃ Vendor  ┃ Family   ┃ Devices ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━┩
│ Atmel.ATmega_DFP.2.2.509.atpack        │ Unknown │ Unknown │ 🔵 ATMEL │ 133     │
│ Microchip.PIC16Fxxx_DFP.1.7.162.atpack │ Unknown │ Unknown │ 🟡 PIC   │ 164     │
└────────────────────────────────────────┴─────────┴─────────┴──────────┴─────────┘

Found 2 AtPack files
```


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
```

Example:
```
atpack devices list .\atpacks\Microchip.PIC16Fxxx_DFP.1.7.162.atpack
         🟡 PIC Devices in
Microchip.PIC16Fxxx_DFP.1.7.162.atp
                ack
┏━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Device Name             ┃ Index ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━┩
│ AC162052_AS_PIC16F630   │ 1     │
│ AC162052_AS_PIC16F676   │ 2     │
│ AC162053_AS_PIC16F627A  │ 3     │
│ AC162053_AS_PIC16F628A  │ 4     │
...
│ PIC16LF876A             │ 161   │
│ PIC16LF877              │ 162   │
│ PIC16LF877A             │ 163   │
│ PIC16LF88               │ 164   │
└─────────────────────────┴───────┘

Total: 164 devices
```


```bash
# Get detailed information about a specific device
atpack devices info DEVICE_NAME /path/to/file.atpack
```
Example:
```
atpack devices info PIC16F877 .\atpacks\Microchip.PIC16Fxxx_DFP.1.7.162.atpack
╭──────────────────────────────────────────────────────────────────────────────────────────── 🔌 Device: PIC16F877 ─────────────────────────────────────────────────────────────────────────────────────────────╮
│ Family: 🟡 PIC                                                                                                                                                                                                │
│ Architecture: PIC                                                                                                                                                                                             │
│ Series: PIC16                                                                                                                                                                                                 │
│ Memory Segments: 8                                                                                                                                                                                            │
│ Modules: 5                                                                                                                                                                                                    │
│ Interrupts: 17                                                                                                                                                                                                │
│ Signatures: 1                                                                                                                                                                                                 │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
              💾 Memory Overview
┏━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ Segment   ┃ Start  ┃ Size        ┃ Type    ┃
┡━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━┩
│ PROG1     │ 0x0000 │ 2,048 bytes │ program │
│ SFR_BANK0 │ 0x0000 │ 32 bytes    │ sfr     │
│ SFR_BANK1 │ 0x0080 │ 32 bytes    │ sfr     │
│ SFR_BANK2 │ 0x0100 │ 16 bytes    │ sfr     │
│ SFR_BANK3 │ 0x0180 │ 16 bytes    │ sfr     │
│ PROG2     │ 0x0800 │ 2,048 bytes │ program │
│ PROG3     │ 0x1000 │ 2,048 bytes │ program │
│ PROG4     │ 0x1800 │ 2,048 bytes │ program │
└───────────┴────────┴─────────────┴─────────┘
             🔧 Modules Overview
┏━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃ Module ┃ Register Groups ┃ Total Registers ┃
┡━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ BANK0  │ 1               │ 32              │
│ BANK1  │ 1               │ 17              │
│ BANK2  │ 1               │ 4               │
│ BANK3  │ 1               │ 2               │
│ CORE   │ 1               │ 1               │
└────────┴─────────────────┴─────────────────┘
```

### Memory Commands

Analyze device memory layout:

```bash
# Show memory map for a device
atpack memory show DEVICE_NAME /path/to/file.atpack
```

### Register Commands

Work with device registers and peripherals:

```bash
# List all registers for a device
atpack registers list DEVICE_NAME /path/to/file.atpack

# Show details for a specific register
atpack registers show DEVICE_NAME REGISTER_NAME /path/to/file.atpack

# Filter registers by module
atpack registers list DEVICE_NAME /path/to/file.atpack --module MODULE_NAME
```

### Configuration Commands

Extract device configuration information:

```bash
# Show all configuration information for a device
atpack config show DEVICE_NAME /path/to/file.atpack

# Show specific configuration type (fuses, config, interrupts, signatures)
atpack config show DEVICE_NAME /path/to/file.atpack --type fuses
```

## Detailed Examples

### Working with ATMEL AtPacks

```bash
# List all ATmega devices
atpack devices list Atmel.ATmega_DFP.2.2.509.atpack

# Get ATmega16 information
atpack devices info ATmega16 Atmel.ATmega_DFP.2.2.509.atpack

# Show ATmega16 memory layout
atpack memory show ATmega16 Atmel.ATmega_DFP.2.2.509.atpack

# List ATmega16 registers
atpack registers list ATmega16 Atmel.ATmega_DFP.2.2.509.atpack

# Show specific register details
atpack registers show ATmega16 PORTB Atmel.ATmega_DFP.2.2.509.atpack

# Show configuration information
atpack config show ATmega16 Atmel.ATmega_DFP.2.2.509.atpack
```

### Working with Microchip AtPacks

```bash
# Work with a PIC AtPack
atpack devices list Microchip.PIC16Fxxx_DFP.1.7.162.atpack

# Get PIC16F877A information  
atpack devices info PIC16F877A Microchip.PIC16Fxxx_DFP.1.7.162.atpack

# Show memory layout
atpack memory show PIC16F877A Microchip.PIC16Fxxx_DFP.1.7.162.atpack

# Show registers
atpack registers list PIC16F877A Microchip.PIC16Fxxx_DFP.1.7.162.atpack

# Show fuses and configuration
atpack config show PIC16F877A Microchip.PIC16Fxxx_DFP.1.7.162.atpack --type fuses
```

### Output Formatting

Most commands support JSON output format:

```bash
# JSON output
atpack devices info ATmega16 file.atpack --format json
atpack devices list file.atpack --format json
atpack memory show ATmega16 file.atpack --format json
atpack registers list ATmega16 file.atpack --format json
atpack config show ATmega16 file.atpack --format json
```

### Filtering Options

Some commands provide filtering options:

```bash
# Filter registers by module
atpack registers list ATmega16 file.atpack --module GPIO

# Show specific configuration types
atpack config show PIC16F877A file.atpack --type fuses
atpack config show PIC16F877A file.atpack --type interrupts
atpack config show PIC16F877A file.atpack --type signatures
```

## Pipeline Integration

The CLI JSON output works well in scripts and pipelines:

```bash
# Count devices in an AtPack
atpack devices list file.atpack --format json | jq length

# Extract device names only
atpack devices list file.atpack --format json | jq -r '.devices[]'

# Get basic device information
atpack scan ./atpacks/ --format json | jq '.[] | {name, family, device_count}'
```

## Getting Help

Use `--help` with any command to get detailed usage information:

```bash
atpack --help
atpack help-tree          # Show complete command structure
atpack help               # Interactive help
atpack devices --help
atpack devices info --help
```
