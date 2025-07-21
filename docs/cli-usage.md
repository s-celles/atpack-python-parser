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
│  │   ├── info - Show AtPack file information                                                                                                                                                                  │
│  │   └── extract - Extract AtPack file                                                                                                                                                                        │
│  ├── 🔌 devices - Device information                                                                                                                                                                          │
│  │   ├── list - List all devices                                                                                                                                                                              │
│  │   ├── info - Show device details                                                                                                                                                                           │
│  │   └── search - Search devices by pattern                                                                                                                                                                   │
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
│    atpack files extract mypack.atpack                                                                                                                                                                         │
│                                                                                                                                                                                                               │
│    atpack devices list mypack.atpack                                                                                                                                                                          │
│    atpack devices info PIC16F877 mypack.atpack                                                                                                                                                                │
│    atpack devices search '*877*' mypack.atpack                                                                                                                                                                │
│                                                                                                                                                                                                               │
│    atpack memory show PIC16F877 mypack.atpack                                                                                                                                                                 │
│    atpack memory show PIC16F877 mypack.atpack --flat                                                                                                                                                          │
│                                                                                                                                                                                                               │
│    atpack registers list PIC16F877 mypack.atpack                                                                                                                                                              │
│    atpack registers list PIC16F877 mypack.atpack --module GPIO                                                                                                                                                │
│    atpack registers show PIC16F877 PORTB mypack.atpack                                                                                                                                                        │
│                                                                                                                                                                                                               │
│    atpack config show PIC16F877 mypack.atpack                                                                                                                                                                 │
│    atpack config show PIC16F877 mypack.atpack --type fuses                                                                                                                                                    │
│                                                                                                                                                                                                               │
│    atpack scan ./atpacks/ --format json                                                                                                                                                                       │
│                                                                                                                                                                                                               │
│                                                                                                                                                                                                               │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## Commands Overview

### Scan for AtPack Files in a Directory


```
atpack scan ./atpacks/
                            🔍 AtPack Files in atpacks
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━┓
┃ Path                                   ┃ Name    ┃ Vendor  ┃ Family   ┃ Devices ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━┩
│ Atmel.ATmega_DFP.2.2.509.atpack        │ Unknown │ Unknown │ 🔵 ATMEL │ 133     │
│ Microchip.PIC16Fxxx_DFP.1.7.162.atpack │ Unknown │ Unknown │ 🔴 PIC   │ 164     │
└────────────────────────────────────────┴─────────┴─────────┴──────────┴─────────┘

Found 2 AtPack files
```


### Files Commands

Work with AtPack files and directories:

#### Show information about a specific AtPack file

```
atpack files info /path/to/file.atpack
```

Example:
```
atpack files info ./atpacks/Microchip.PIC16Fxxx_DFP.1.7.162.atpack
╭────────────────────────────────────────────────────── 📦 AtPack Information ──────────────────────────────────────────────────────╮
│ Name: Unknown                                                                                                                     │
│ Vendor: Unknown                                                                                                                   │
│ Version: 0.0.0                                                                                                                    │
│ Device Family: PIC                                                                                                                │
│ Description: Microchip PIC16Fxxx Series Device Support                                                                            │
│ URL: N/A                                                                                                                          │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

#### List all AtPack files in a directory

```bash
atpack files list /path/to/atpack/directory
```
Example:
```
atpack files list ./atpacks/Microchip.PIC16Fxxx_DFP.1.7.162.atpack
      Files in Microchip.PIC16Fxxx_DFP.1.7.162.atpack
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃ File Path                              ┃ Size            ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ edc/                                   │ 0 bytes         │
│ hwtools/                               │ 0 bytes         │
│ hwtools/mplab/                         │ 0 bytes         │
...
│ xc8/pic/include/proc/pic16lf877a.inc   │ 90,175 bytes    │
│ xc8/pic/include/proc/pic16lf88.h       │ 142,857 bytes   │
│ xc8/pic/include/proc/pic16lf88.inc     │ 80,519 bytes    │
└────────────────────────────────────────┴─────────────────┘
```

#### Extract files from an AtPack

```bash
atpack files extract /path/to/file.atpack
```

This command extracts all files from an AtPack archive to a directory. By default, it extracts to a directory named `{filename}_dir_atpack` where `{filename}` is the AtPack filename without the `.atpack` extension.

Example:
```bash
atpack files extract ./atpacks/Microchip.PIC16Fxxx_DFP.1.7.162.atpack
```

This would extract all files to `./atpacks/Microchip.PIC16Fxxx_DFP.1.7.162_dir_atpack/` directory.

You can specify a custom output directory:
```bash
atpack files extract ./atpacks/Microchip.PIC16Fxxx_DFP.1.7.162.atpack --outdir ./extracted_files/
```

Optional parameters:
- `--outdir` or `-o`: Specify output directory
- `--overwrite`: Overwrite existing directory if it exists

Example with options:
```bash
atpack files extract ./atpacks/Microchip.PIC16Fxxx_DFP.1.7.162.atpack --outdir ./my_extraction/ --overwrite
```

Example output:
```
atpack files extract ./atpacks/Microchip.PIC16Fxxx_DFP.1.7.162.atpack
Extracting Microchip.PIC16Fxxx_DFP.1.7.162.atpack to Microchip.PIC16Fxxx_DFP.1.7.162_dir_atpack
✓ Successfully extracted 3,847 files to Microchip.PIC16Fxxx_DFP.1.7.162_dir_atpack
Total size: 45,892,437 bytes
```

### Device Commands

Extract and display device information:

#### List all devices in an AtPack file

```bash
atpack devices list /path/to/file.atpack
```

Example:
```
atpack devices list ./atpacks/Microchip.PIC16Fxxx_DFP.1.7.162.atpack
         🔴 PIC Devices in
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

#### List all devices in an AtPack file matching a pattern

```bash
atpack search "*YourPattern*" /path/to/file.atpack
```

Example:
```
atpack devices search "*877*" ./atpacks/Microchip.PIC16Fxxx_DFP.1.7.162.atpack
🔴 PIC Devices matching
        '*877*'        
┏━━━━━━━━━━━━━┳━━━━━━━┓
┃ Device Name ┃ Index ┃
┡━━━━━━━━━━━━━╇━━━━━━━┩
│ PIC16F877   │ 1     │
│ PIC16F877A  │ 2     │
│ PIC16LF877  │ 3     │
│ PIC16LF877A │ 4     │
└─────────────┴───────┘
```

```bash
# Get detailed information about a specific device
atpack devices info DEVICE_NAME /path/to/file.atpack
```
Example:

```
atpack devices info PIC16F877 ./atpacks/Microchip.PIC16Fxxx_DFP.1.7.162.atpack
╭──────────────────────────────────────────────────────────────────────────────────────────── 🔌 Device: PIC16F877 ─────────────────────────────────────────────────────────────────────────────────────────────╮
│ Family: 🔴 PIC                                                                                                                                                                                                │
│ Architecture: PIC                                                                                                                                                                                             │
│ Series: PIC16                                                                                                                                                                                                 │
│ Memory Segments: 8                                                                                                                                                                                            │
│ Modules: 5                                                                                                                                                                                                    │
│ Interrupts: 17                                                                                                                                                                                                │
│ Signatures: 1                                                                                                                                                                                                 │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
                        💾 Memory Overview
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ Segment   ┃ Start Address ┃ End Address ┃ Size        ┃ Type    ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━┩
│ PROG1     │ 0x0000        │ 0x07FF      │ 2,048 bytes │ program │
│ SFR_BANK0 │ 0x0000        │ 0x001F      │ 32 bytes    │ sfr     │
│ SFR_BANK1 │ 0x0080        │ 0x009F      │ 32 bytes    │ sfr     │
│ SFR_BANK2 │ 0x0100        │ 0x010F      │ 16 bytes    │ sfr     │
│ SFR_BANK3 │ 0x0180        │ 0x018F      │ 16 bytes    │ sfr     │
│ PROG2     │ 0x0800        │ 0x0FFF      │ 2,048 bytes │ program │
│ PROG3     │ 0x1000        │ 0x17FF      │ 2,048 bytes │ program │
│ PROG4     │ 0x1800        │ 0x1FFF      │ 2,048 bytes │ program │
└───────────┴───────────────┴─────────────┴─────────────┴─────────┘
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

#### Typo in device name? No problem!

```
atpack devices info PIC16f877 ./atpacks/Microchip.PIC16Fxxx_DFP.1.7.162.atpack
Device not found: Device 'PIC16f877' not found or could not be parsed: Error parsing PIC file for 'PIC16f877': Device 'PIC16f877' not
found in PIC file

Did you mean one of these devices?
  1. PIC16F877
  2. PIC16F87
  3. PIC16F877A
  4. PIC16LF877
  5. PIC16LF877A
  6. PIC16F677
  7. PIC16F687
  8. PIC16F767
  9. PIC16F777
  10. PIC16F871
  11. PIC16F876
  12. PIC16F887
  13. PIC16LF77
  14. PIC16LF87
  15. PIC16LF871
```

### Memory Commands

Analyze device memory layout:

```bash
# Show hierarchical memory map for a device (default)
atpack memory show DEVICE_NAME /path/to/file.atpack
```
Example:
```
atpack memory show PIC16F877 ./atpacks/Microchip.PIC16Fxxx_DFP.1.7.162.atpack
                                       💾 Memory Layout: PIC16F877 (Hierarchical)
┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Memory Space/Segment ┃ Start Address ┃ End Address ┃ Size  ┃ Type         ┃ Page Size ┃ Description                  ┃
┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 📁 ProgramSpace      │ N/A           │ N/A         │ N/A   │ ProgramSpace │ N/A       │ Container with 10 segment(s) │
│   └── PROG1          │ 0x0000        │ 0x07FF      │ 2,048 │ program      │ N/A       │ ROM code space - page0       │
│   └── PROG2          │ 0x0800        │ 0x0FFF      │ 2,048 │ program      │ N/A       │ ROM code space - page1       │
│   └── PROG3          │ 0x1000        │ 0x17FF      │ 2,048 │ program      │ N/A       │ ROM code space - page2       │
│   └── PROG4          │ 0x1800        │ 0x1FFF      │ 2,048 │ program      │ N/A       │ ROM code space - page3       │
│   └── IDLOCS         │ 0x2000        │ 0x2003      │ 4     │ userid       │ N/A       │ ID locations                 │
│   └── TEST           │ 0x2000        │ 0x20FF      │ 256   │ test         │ N/A       │ N/A                          │
│   └── DEBUG          │ 0x2004        │ 0x2004      │ 1     │ debug        │ N/A       │ N/A                          │
│   └── DEVICEID       │ 0x2006        │ 0x2006      │ 1     │ deviceid     │ N/A       │ N/A                          │
│   └── CONFIG         │ 0x2007        │ 0x2007      │ 1     │ config       │ N/A       │ N/A                          │
│   └── DEEPROM        │ 0x2100        │ 0x21FF      │ 256   │ eeprom       │ N/A       │ Data EEPROM                  │
│ 📁 DataSpace         │ 0x0000        │ 0x01FF      │ 512   │ DataSpace    │ N/A       │ Container with 4 segment(s)  │
│   └── SFR_BANK0      │ 0x0000        │ 0x001F      │ 32    │ sfr          │ N/A       │ N/A                          │
│   └── SFR_BANK1      │ 0x0080        │ 0x009F      │ 32    │ sfr          │ N/A       │ N/A                          │
│   └── SFR_BANK2      │ 0x0100        │ 0x010F      │ 16    │ sfr          │ N/A       │ N/A                          │
│   └── SFR_BANK3      │ 0x0180        │ 0x018F      │ 16    │ sfr          │ N/A       │ N/A                          │
└──────────────────────┴───────────────┴─────────────┴───────┴──────────────┴───────────┴──────────────────────────────┘
```

```bash
# Show flat memory map for a device
atpack memory show DEVICE_NAME /path/to/file.atpack --flat
```
Example:
```
atpack memory show PIC16F877 ./atpacks/Microchip.PIC16Fxxx_DFP.1.7.162.atpack --flat
                           💾 Memory Layout: PIC16F877 (Flat)
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃ Segment   ┃ Start Address ┃ End Address ┃ Size  ┃ Type    ┃ Page Size ┃ Address Space ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
│ PROG1     │ 0x0000        │ 0x07FF      │ 2,048 │ program │ N/A       │ program       │
│ SFR_BANK0 │ 0x0000        │ 0x001F      │ 32    │ sfr     │ N/A       │ data          │
│ SFR_BANK1 │ 0x0080        │ 0x009F      │ 32    │ sfr     │ N/A       │ data          │
│ SFR_BANK2 │ 0x0100        │ 0x010F      │ 16    │ sfr     │ N/A       │ data          │
│ SFR_BANK3 │ 0x0180        │ 0x018F      │ 16    │ sfr     │ N/A       │ data          │
│ PROG2     │ 0x0800        │ 0x0FFF      │ 2,048 │ program │ N/A       │ program       │
│ PROG3     │ 0x1000        │ 0x17FF      │ 2,048 │ program │ N/A       │ program       │
│ PROG4     │ 0x1800        │ 0x1FFF      │ 2,048 │ program │ N/A       │ program       │
└───────────┴───────────────┴─────────────┴───────┴─────────┴───────────┴───────────────┘
```

### Register Commands

Work with device registers and peripherals:

#### List all registers for a device

```bash
atpack registers list DEVICE_NAME /path/to/file.atpack
```

Example:
```
atpack registers list PIC16F877 ./atpacks/Microchip.PIC16Fxxx_DFP.1.7.162.atpack
                  📋 Registers: PIC16F877
┏━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━┳━━━━━━━━┳━━━━━━━━━━━┓
┃ Module ┃ Register   ┃ Offset ┃ Size ┃ Access ┃ Bitfields ┃
┡━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━╇━━━━━━━━╇━━━━━━━━━━━┩
│ BANK0  │ INDF       │ 0x0000 │ 1    │ R      │ 1         │
│ CORE   │ WREG       │ 0x0000 │ 1    │ RW     │ 0         │
│ BANK0  │ TMR0       │ 0x0001 │ 1    │ RW     │ 1         │
...
│ BANK2  │ EEADRH     │ 0x010F │ 1    │ R      │ 1         │
│ BANK3  │ EECON1     │ 0x018C │ 1    │ R      │ 5         │
│ BANK3  │ EECON2     │ 0x018D │ 1    │ W      │ 1         │
└────────┴────────────┴────────┴──────┴────────┴───────────┘
```


#### Show details for a specific register
```bash
atpack registers show DEVICE_NAME REGISTER_NAME /path/to/file.atpack
```

Example:
```
atpack registers show PIC16F877 OPTION_REG ./atpacks/Microchip.PIC16Fxxx_DFP.1.7.162.atpack
╭─────────────────────────────────────────────────────────────────────────────────────────── 📋 Register: OPTION_REG ───────────────────────────────────────────────────────────────────────────────────────────╮
│ Name: OPTION_REG                                                                                                                                                                                              │
│ Caption: OPTION_REG                                                                                                                                                                                           │
│ Offset: 0x0081                                                                                                                                                                                                │
│ Size: 1 bytes                                                                                                                                                                                                 │
│ Access: RW                                                                                                                                                                                                    │
│ Mask: N/A                                                                                                                                                                                                     │
│ Initial Value: N/A                                                                                                                                                                                            │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
                 🔧 Bitfields
┏━━━━━━━━┳━━━━━━┳━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Name   ┃ Bits ┃ Mask ┃ Description ┃ Values ┃
┡━━━━━━━━╇━━━━━━╇━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━┩
│ PS     │ 2:0  │ 0x07 │ PS          │ N/A    │
│ ├─ PS0 │ 0    │ 0x01 │ PS0         │ N/A    │
│ ├─ PS1 │ 1    │ 0x02 │ PS1         │ N/A    │
│ ├─ PS2 │ 2    │ 0x04 │ PS2         │ N/A    │
│ PSA    │ 3    │ 0x08 │ PSA         │ N/A    │
│ T0SE   │ 4    │ 0x10 │ T0SE        │ N/A    │
│ T0CS   │ 5    │ 0x20 │ T0CS        │ N/A    │
│ INTEDG │ 6    │ 0x40 │ INTEDG      │ N/A    │
│ nRBPU  │ 7    │ 0x80 │ nRBPU       │ N/A    │
└────────┴──────┴──────┴─────────────┴────────┘
```

# Filter registers by module
```bash
atpack registers list DEVICE_NAME /path/to/file.atpack --module MODULE_NAME
```

Example:
```
atpack registers list PIC16F877 ./atpacks/Microchip.PIC16Fxxx_DFP.1.7.162.atpack --module CORE
          📋 Registers: PIC16F877 (Module: CORE)
┏━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━┳━━━━━━┳━━━━━━━━┳━━━━━━━━━━━┓
┃ Module ┃ Register ┃ Offset ┃ Size ┃ Access ┃ Bitfields ┃
┡━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━╇━━━━━━╇━━━━━━━━╇━━━━━━━━━━━┩
│ CORE   │ WREG     │ 0x0000 │ 1    │ RW     │ 0         │
└────────┴──────────┴────────┴──────┴────────┴───────────┘
```

### Configuration Commands

Extract device configuration information:

```bash
# Show all configuration information for a device
atpack config show DEVICE_NAME /path/to/file.atpack
```

Example:
```
atpack config show PIC16F877 ./atpacks/Microchip.PIC16Fxxx_DFP.1.7.162.atpack
            ⚡ Interrupts
┏━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ Index ┃ Name     ┃ Description    ┃
┡━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ 0     │ AD_INT   │ AD Interrupt   │
│ 1     │ BCL_INT  │ BCL Interrupt  │
│ 2     │ CCP1_INT │ CCP1 Interrupt │
│ 3     │ CCP2_INT │ CCP2 Interrupt │
│ 4     │ EE_INT   │ EE Interrupt   │
│ 5     │ G_INT    │ G Interrupt    │
│ 6     │ INTE_INT │ INTE Interrupt │
│ 7     │ PE_INT   │ PE Interrupt   │
│ 8     │ PSP_INT  │ PSP Interrupt  │
│ 9     │ RB_INT   │ RB Interrupt   │
│ 10    │ RC_INT   │ RC Interrupt   │
│ 11    │ SSP_INT  │ SSP Interrupt  │
│ 12    │ T0_INT   │ T0 Interrupt   │
│ 13    │ TMR0_INT │ TMR0 Interrupt │
│ 14    │ TMR1_INT │ TMR1 Interrupt │
│ 15    │ TMR2_INT │ TMR2 Interrupt │
│ 16    │ TX_INT   │ TX Interrupt   │
└───────┴──────────┴────────────────┘
       ✍️ Device Signatures
┏━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━┓
┃ Name        ┃ Address ┃ Value ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━┩
│ DEVID_DEVID │ 0x2006  │ 0x9A0 │
└─────────────┴─────────┴───────┘
```


# Show specific configuration type (fuses, config, interrupts, signatures)
```bash
atpack config show DEVICE_NAME /path/to/file.atpack --type fuses
```

### Output Formatting

Most commands support JSON output format:

```bash
# JSON output
atpack devices info PIC16F877 file.atpack --format json
atpack devices list file.atpack --format json
atpack memory show PIC16F877 file.atpack --format json
atpack registers list PIC16F877 file.atpack --format json
atpack config show PIC16F877 file.atpack --format json
```

### Filtering Options

Some commands provide filtering options:

```bash
# Filter registers by module
atpack registers list PIC16F877 file.atpack --module GPIO

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
