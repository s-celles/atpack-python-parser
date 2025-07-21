# AtPack Files

This directory should contain AtPack files for testing, but these files are proprietary and cannot be distributed with the source code.

## Quick Setup

Use the provided download script to automatically download all required AtPack files:

```bash
# Download all AtPack files
python download_atpacks.py

# Or use Make target
make download-atpacks
```

## Required Files for Tests

To run the enhanced parser tests, you need to download the following AtPack files:

### ATMEL AtPack
- **File**: `Atmel.ATmega_DFP.2.2.509.atpack`
- **Source**: [Microchip Packs Repository](https://packs.download.microchip.com/)
- **Direct Download**: https://packs.download.microchip.com/Atmel.ATmega_DFP.2.2.509.atpack
- **Required for**: 
  - `tests/integration/test_atmel_atmega.py`

### PIC16F AtPack
- **File**: `Microchip.PIC16Fxxx_DFP.1.7.162.atpack`
- **Source**: [Microchip Packs Repository](https://packs.download.microchip.com/)
- **Direct Download**: https://packs.download.microchip.com/Microchip.PIC16Fxxx_DFP.1.7.162.atpack
- **Required for**: 
  - `tests/integration/test_microchip_pic16fxxx.py`
  - `tests/test_hierarchical_memory.py`

### PIC24F AtPack
- **File**: `Microchip.PIC24F-KA-KL-KM_DFP.1.5.253.atpack`
- **Source**: [Microchip Packs Repository](https://packs.download.microchip.com/)
- **Direct Download**: https://packs.download.microchip.com/Microchip.PIC24F-KA-KL-KM_DFP.1.5.253.atpack
- **Required for**: 
  - `tests/integration/test_microchip_pic24f-ka-kl-km.py`

## Download Script Usage

The `download_atpacks.py` script provides several options:

```bash
# List available files
python download_atpacks.py --list

# Download specific files
python download_atpacks.py --file atmega
python download_atpacks.py --file pic16f pic24f

# Force re-download existing files
python download_atpacks.py --force

# Download to custom directory
python download_atpacks.py --output /path/to/custom/dir

# Show help
python download_atpacks.py --help
```

## Manual Installation

If the download script doesn't work, you can manually download the files:

1. Download the required AtPack files from the links above
2. Place them in this `atpacks/` directory
3. The test files will automatically detect and use them

## Test Behavior

- **With AtPack files**: Tests will run normally and validate the parser functionality
- **Without AtPack files**: Tests will be automatically skipped with a clear message
- **In CI/CD**: The download script is used to fetch AtPack files before running tests

## CI Integration

For continuous integration, the download script is automatically run:

```yaml
# In GitHub Actions
- name: Download AtPack files for integration tests
  run: |
    python download_atpacks.py || echo "AtPack download failed, integration tests will be skipped"
```

This ensures the project can be built and tested in environments where the proprietary AtPack files are not available, while still providing comprehensive testing when they are present.
