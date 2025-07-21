# AtPack Files

This directory should contain AtPack files for testing, but these files are proprietary and cannot be distributed with the source code.

## Required Files for Tests

To run the enhanced parser tests, you need to download the following AtPack files:

### ATMEL AtPack
- **File**: `Atmel.ATmega_DFP.2.2.509.atpack`
- **Source**: [Microchip Packs Repository](https://packs.download.microchip.com/)
- **Direct Download**: https://packs.download.microchip.com/Microchip.ATmega_DFP.2.2.509.atpack
- **Required for**: `tests/test_enhanced_atmel.py`

### PIC AtPack
- **File**: `Microchip.PIC16Fxxx_DFP.1.7.162.atpack`
- **Source**: [Microchip Packs Repository](https://packs.download.microchip.com/)
- **Direct Download**: https://packs.download.microchip.com/Microchip.PIC16Fxxx_DFP.1.7.162.atpack
- **Required for**: `tests/test_enhanced_pic.py`

## Installation

1. Download the required AtPack files from the links above
2. Place them in this `atpacks/` directory
3. The test files will automatically detect and use them

## Test Behavior

- **With AtPack files**: Tests will run normally and validate the parser functionality
- **Without AtPack files**: Tests will be automatically skipped with a clear message
- **In CI/CD**: Tests will be skipped since AtPack files cannot be committed to the repository

This ensures the project can be built and tested in environments where the proprietary AtPack files are not available.
