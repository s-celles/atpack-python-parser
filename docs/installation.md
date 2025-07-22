# Installation

!!! info "AtPack Files Required"
    
    **AtPack files are NOT included** with this package due to licensing restrictions.
    
    You must download AtPack files separately from the official sources:
    
    - **PIC AtPacks**: [Microchip Packs Repository](https://packs.download.microchip.com/)
    - **ATMEL AtPacks (legacy)**: [Microchip Packs Repository](http://packs.download.atmel.com/)
    
    See the [Getting AtPack Files](#getting-atpack-files) section below for detailed instructions.

## Requirements

- Python 3.9 or higher
- Operating System: Windows, macOS, or Linux

## Install from PyPI

The easiest way to install AtPack Parser is from PyPI using pip:

```bash
pip install git+https://github.com/s-celles/atpack-python-parser
# or when (if) registered on PyPI
pip install atpack-parser
```

## Install from Source

If you want the latest development version or want to contribute:

```bash
git clone https://github.com/s-celles/atpack-python-parser.git
cd atpack-python-parser
pip install -e .
```

## Development Installation

For development work, install with development dependencies:

```bash
git clone https://github.com/s-celles/atpack-python-parser.git
cd atpack-python-parser
pip install -e ".[dev]"
```

This installs additional tools for:

- Testing (pytest, pytest-cov)
- Code formatting (black)
- Linting (ruff)
- Type checking (mypy)

## Verify Installation

After installation, verify that AtPack Parser is working correctly:

```bash
# Check CLI is available
atpack --help

# Check version
atpack --version
```

You can also test the Python API:

```python
import atpack_parser
print(f"AtPack Parser version: {atpack_parser.__version__}")
```

## Dependencies

AtPack Parser depends on the following packages:

- **typer** - CLI framework
- **lxml** - XML parsing
- **rich** - Terminal formatting
- **pydantic** - Data validation
- **pathlib** - Path handling

These are automatically installed when you install AtPack Parser.

## Troubleshooting

### Permission Issues

If you encounter permission issues during installation:

```bash
# Use --user flag to install for current user only
pip install --user atpack-parser

# Or use a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install atpack-parser
```

### Import Errors

If you get import errors, make sure you're using the correct Python environment:

```bash
# Check Python version
python --version

# Check installed packages
pip list | grep atpack
```

### XML Parser Issues

If you encounter XML parsing issues, you might need to install additional XML libraries:

```bash
# On Ubuntu/Debian
sudo apt-get install libxml2-dev libxslt-dev

# On macOS with Homebrew
brew install libxml2 libxslt

# Then reinstall lxml
pip uninstall lxml
pip install lxml
```

## Legal Notice

!!! warning "Important Legal Information"
    
    ### Trademark Notice
    - **ATMEL** and **Microchip** are registered trademarks of Microchip Technology Inc.
    - This project is **unofficial** and is **not supported, endorsed, or affiliated** with Microchip Technology Inc. or its subsidiaries.
    
    ### AtPack File Licensing
    - **AtPack files contain proprietary data** owned by Microchip Technology Inc.
    - AtPack files are subject to **individual licenses and terms of use** set by Microchip.
    - **AtPack files are NOT distributed** with this project due to licensing restrictions.
    - Users must **download AtPack files directly** from official Microchip sources.
    
    ### Disclaimer
    - This parser is provided **"as-is"** for educational and development purposes only.
    - The authors assume **no responsibility** for any misuse or license violations.
    - Users are responsible for **ensuring compliance** with all applicable licenses and terms of service.
    
    ### Recommended Usage
    - Use only for **personal development and learning**
    - Respect all **license terms** when using AtPack files
    - Obtain AtPack files only from **official sources**
    
    By using this software, you acknowledge that you have read and understood these legal notices.

## Getting AtPack Files

AtPack files contain device-specific information for microcontrollers and must be downloaded separately from official sources.

### Download Sources

**For PIC Microcontrollers:**

- Visit: [Microchip Packs Repository](https://packs.download.microchip.com/)
- Browse by device family (PIC16, PIC18, PIC24, dsPIC, PIC32, etc.)
- Download the `.atpack` files for your target devices

**For Legacy ATMEL Devices:**

- Visit: [ATMEL Packs Repository](http://packs.download.atmel.com/)
- Browse by device family (AVR, ARM, etc.)
- Download the `.atpack` files for your target devices
