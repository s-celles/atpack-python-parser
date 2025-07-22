# AtPack Parser Interactive Mode

Interactive mode provides an enhanced command-line interface with auto-completion, command history, and Rich interface for a better user experience.

## Installation

To use interactive mode, install prompt-toolkit:

```bash
pip install prompt-toolkit
# or
pip install atpack-parser[interactive]
```

## Launch

```bash
atpack interactive
```

## Features

### 🎯 Auto-completion
- Type the beginning of a command and press TAB for auto-completion
- Navigate with up/down arrows through command history

### 🎨 Rich Interface
- Colored and formatted tables
- Clear information panels
- Colored status messages

### 📝 History
- All commands are saved in session history
- Navigate with ↑/↓

## Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `help` | Show help | `help` |
| `scan [dir]` | Scan directory for AtPack files | `scan ./atpacks` |
| `load <file>` | Load an AtPack file | `load mypack.atpack` |
| `devices` | List all devices | `devices` |
| `select <device>` | Select a device | `select PIC16F877` |
| `device-info` | Info about selected device | `device-info` |
| `memory` | Device memory layout | `memory` |
| `registers` | Device registers | `registers` |
| `status` | Session status | `status` |
| `clear` | Clear screen | `clear` |
| `exit/quit` | Exit session | `exit` |

## Typical Workflow

1. **Start** : `atpack interactive`

```
╭───────── Interactive Session ─────────╮
│ 🔧 AtPack Parser - Interactive Mode   │
│ Type 'help' to see available commands │
│ Type 'exit' to quit                   │
╰───────────────────────────────────────╯
```

and see the help menu

```
atpack ❯ help
                            Available Commands
┏━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃ Command         ┃ Description                      ┃ Example            ┃
┡━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│ help            │ Show this help                   │ help               │
│ scan            │ Scan directory for AtPack files  │ scan ./atpacks     │
│ load <file>     │ Load an AtPack file              │ load mypack.atpack │
│ devices         │ List all devices                 │ devices            │
│ select <device> │ Select a device                  │ select ATmega328P  │
│ device-info     │ Show selected device information │ device-info        │
│ memory          │ Show device memory layout        │ memory             │
│ registers       │ Show device registers            │ registers          │
│ files           │ Show files in AtPack             │ files              │
│ config          │ Show AtPack configuration        │ config             │
│ status          │ Show session status              │ status             │
│ clear           │ Clear screen                     │ clear              │
│ exit/quit       │ Exit session                     │ exit               │
└─────────────────┴──────────────────────────────────┴────────────────────┘
```

2. **Auto-scan** : The `./atpacks` directory is automatically scanned

```
atpack ❯ scan
Scanning directory: ./atpacks
                     AtPack Files Found (3)
┏━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ No. ┃ File                                         ┃ Size    ┃
┡━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━┩
│ 1   │ Atmel.ATmega_DFP.2.2.509.atpack              │ 31.8 MB │
│ 2   │ Microchip.PIC16Fxxx_DFP.1.7.162.atpack       │ 5.8 MB  │
│ 3   │ Microchip.PIC24F-KA-KL-KM_DFP.1.5.253.atpack │ 4.8 MB  │
└─────┴──────────────────────────────────────────────┴─────────┘
```

3. **Load** : `load mypack.atpack` (or interactive selection)

```
atpack ❯ load
Available AtPack files:
  1. Atmel.ATmega_DFP.2.2.509.atpack
  2. Microchip.PIC16Fxxx_DFP.1.7.162.atpack
  3. Microchip.PIC24F-KA-KL-KM_DFP.1.5.253.atpack
Select a file (number or name)
[1/2/3/Atmel.ATmega_DFP.2.2.509.atpack/Microchip.PIC16Fxxx_DFP.1.7.162.atpack/Microchip.PIC24F-KA-KL-KM_DFP.1.5.253.atpa
ck]: 2
✅ AtPack loaded successfully!
Family: PIC
Devices: 164
```

4. **Navigate** : `devices` to see devices

```
atpack[Microchip.PIC16Fxxx_DFP.1.7.162] ❯ devices
            Devices (Page 1/9)
┏━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ No. ┃ Device                  ┃ Status ┃
┡━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━┩
│ 1   │ AC162052_AS_PIC16F630   │        │
│ 2   │ AC162052_AS_PIC16F676   │        │
│ 3   │ AC162053_AS_PIC16F627A  │        │
│ 4   │ AC162053_AS_PIC16F628A  │        │
│ 5   │ AC162053_AS_PIC16F648A  │        │
│ 6   │ AC162053_AS_PIC16LF627A │        │
│ 7   │ AC162053_AS_PIC16LF628A │        │
│ 8   │ AC162053_AS_PIC16LF648A │        │
│ 9   │ AC162054_AS_PIC16F716   │        │
│ 10  │ AC162055_AS_PIC16F684   │        │
│ 11  │ AC162056_AS_PIC16F688   │        │
│ 12  │ AC162057_AS_PIC16F636   │        │
│ 13  │ AC162059_AS_PIC16F505   │        │
│ 14  │ AC162060_AS_PIC16F785   │        │
│ 15  │ AC162060_AS_PIC16HV785  │        │
│ 16  │ AC162061_AS_PIC16F631   │        │
│ 17  │ AC162061_AS_PIC16F677   │        │
│ 18  │ AC162061_AS_PIC16F685   │        │
│ 19  │ AC162061_AS_PIC16F687   │        │
│ 20  │ AC162061_AS_PIC16F689   │        │
└─────┴─────────────────────────┴────────┘
Actions: (n)ext, (q)uit [n/q]:
```

5. **Select** : `select PIC16F877`

```
atpack[Microchip.PIC16Fxxx_DFP.1.7.162] ❯ select PIC16F877
✅ Device selected: PIC16F877
atpack[Microchip.PIC16Fxxx_DFP.1.7.162](PIC16F877) ❯ device-info
```

6. **Analyze** : `device-info`, `memory`, `registers`

```
atpack[Microchip.PIC16Fxxx_DFP.1.7.162](PIC16F877) ❯ device-info
╭───────────────────────────────────────────────── Device Information ─────────────────────────────────────────────────╮
│ Device: PIC16F877                                                                                                    │
│ Family: PIC                                                                                                          │
│ Architecture: PIC                                                                                                    │
│ Package: Not specified                                                                                               │
│ Flash Size: Not specified                                                                                            │
│ RAM Size: Not specified                                                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

```
atpack[Microchip.PIC16Fxxx_DFP.1.7.162](PIC16F877) ❯ memory
               Memory Layout - PIC16F877
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ Segment   ┃ Start Address ┃ Size       ┃ Description ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ PROG1     │ 0x0000        │ 2048 bytes │             │
│ SFR_BANK0 │ 0x0000        │ 32 bytes   │             │
│ SFR_BANK1 │ 0x0080        │ 32 bytes   │             │
│ SFR_BANK2 │ 0x0100        │ 16 bytes   │             │
│ SFR_BANK3 │ 0x0180        │ 16 bytes   │             │
│ PROG2     │ 0x0800        │ 2048 bytes │             │
│ PROG3     │ 0x1000        │ 2048 bytes │             │
│ PROG4     │ 0x1800        │ 2048 bytes │             │
└───────────┴───────────────┴────────────┴─────────────
```

...

7. **Exit** : `exit`

## Interactive Selection

### File Loading
If you type `load` without arguments, interactive mode offers:
- List of available AtPack files
- Selection by number or filename
- Automatic loading if only one file found

### Device Selection
The `select` command supports:
- **Exact match** : `select PIC16F877`
- **Partial match** : `select 16F877A` (finds PIC16F877A)
- **Multiple selection** : If multiple matches, interactive choice
```
❯ select 877
Multiple matches found (4):
  1. PIC16F877
  2. PIC16F877A
  3. PIC16LF877
  4. PIC16LF877A
```

## Usage Examples

### Simple Session
```
atpack interactive
❯ scan
❯ load 1
❯ devices
❯ select PIC16F877
❯ memory
❯ exit
```

### Device Search
```
❯ devices 16F877
❯ select PIC16F877
❯ device-info
```

### Contextual Navigation
The prompt shows the current context:
```
atpack ❯ load mypack.atpack
atpack[mypack] ❯ select ATmega328P
atpack[mypack](ATmega328P) ❯ memory
```

## Keyboard Shortcuts

- **Tab** : Auto-completion
- **↑/↓** : Command history
- **Ctrl+C** : Interrupt (with confirmation)
- **Ctrl+D** : Quit
- **Escape** : Cancel current input

## Error Handling

Interactive mode intelligently handles errors:
- Clear colored error messages
- Alternative command suggestions
- Confirmation before destructive actions
- Graceful error recovery

## Advantages vs Standard CLI

| Aspect | Standard CLI | Interactive Mode |
|--------|--------------|------------------|
| Commands | `atpack devices list file.atpack` | `devices` (in context) |
| Auto-completion | No | Yes |
| History | Shell only | Integrated |
| Interface | Plain text | Rich/colored |
| Selection | Repetitive arguments | Persistent context |
| Navigation | Long commands | Fast navigation |
