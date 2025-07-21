# AtPack Parser

A Python library and CLI tool for parsing AtPack files with intelligent error handling and device suggestions.

## ✨ Key Features

- 📦 **Parse ATMEL and Microchip AtPack files** - Support for both ATDF and PIC formats
- 🎯 **Intelligent device name suggestions** - Fuzzy matching when device names are mistyped
- 💻 **Rich CLI interface** - Beautiful, hierarchical command structure with color output
- 🔧 **DRY architecture** - Consistent error handling across all commands
- 🐍 **Python API** - Full programmatic access for integration
- ✨ **MIT licensed dependencies** - No GPL dependencies, uses rapidfuzz for fuzzy matching

## 🚀 Quick Example

```bash
# Typo in device name? No problem!
$ atpack memory show PIC16f877 ./atpacks/Microchip.PIC16Fxxx_DFP.1.7.162.atpack

Device not found: Device 'PIC16f877' not found

Did you mean one of these devices?
  1. PIC16F877      ← Exact match (case difference)
  2. PIC16F877A     ← Similar device  
  3. PIC16F876      ← Same family
  4. PIC16F878      ← Same family
  5. PIC16F876A     ← Same family
```

## 📦 Installation

```bash
pip install git+https://github.com/s-celles/atpack-python-parser
```

## Legal Notice

⚠️ **IMPORTANT**: This project is unofficial and not affiliated with Microchip Technology Inc. ATMEL and Microchip are registered trademarks. AtPack files contain proprietary data and are not distributed with this project. Users must obtain AtPack files from official sources and comply with all applicable licenses.

## Documentation

For complete documentation, examples, and API reference, visit:

**📚 [https://s-celles.github.io/atpack-python-parser/](https://s-celles.github.io/atpack-python-parser/)**

## License

MIT License - see LICENSE file for details.
