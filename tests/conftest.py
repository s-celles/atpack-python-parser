"""Test configuration."""

import sys
import zipfile
from pathlib import Path
import pytest

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# AtPack file paths
ATPACKS_DIR = Path(__file__).parent.parent / "atpacks"
PIC_ATPACK_FILE = ATPACKS_DIR / "Microchip.PIC16Fxxx_DFP.1.7.162.atpack"
PIC24F_ATPACK_FILE = ATPACKS_DIR / "Microchip.PIC24F-KA-KL-KM_DFP.1.5.253.atpack"
ATMEL_ATPACK_FILE = ATPACKS_DIR / "Atmel.ATmega_DFP.2.2.509.atpack"


def _create_warning_msg(atpack_file: Path, vendor: str) -> str:
    """Create a standardized warning message for missing AtPack files."""
    return (
        f"⚠️  {vendor} AtPack file not available: {atpack_file}\n"
        f"   This integration test requires AtPack files.\n"
        f"   See atpacks/README.md for download instructions.\n"
        f"   Test will be SKIPPED."
    )


def _create_read_error_msg(error: Exception, file_type: str) -> str:
    """Create a standardized error message for AtPack read failures."""
    return (
        f"⚠️  Could not read {file_type} file from AtPack: {error}\n"
        f"   The AtPack file may be corrupted or have a different structure.\n"
        f"   Test will be SKIPPED."
    )


def skip_if_atpack_missing(atpack_file: Path, vendor: str) -> None:
    """Skip test if AtPack file is not available."""
    if not atpack_file.exists():
        warning_msg = _create_warning_msg(atpack_file, vendor)
        print(warning_msg)
        pytest.skip(f"AtPack file not available: {atpack_file}")


def read_from_atpack(atpack_file: Path, internal_file: str, file_type: str) -> str:
    """
    Read a file from an AtPack zip archive.
    
    Args:
        atpack_file: Path to the AtPack file
        internal_file: Path to the file inside the zip
        file_type: Type description for error messages
        
    Returns:
        Content of the file as string
        
    Raises:
        pytest.skip: If the file cannot be read
    """
    try:
        with zipfile.ZipFile(atpack_file, "r") as zip_file:
            with zip_file.open(internal_file) as f:
                return f.read().decode("utf-8")
    except (zipfile.BadZipFile, KeyError) as e:
        warning_msg = _create_read_error_msg(e, file_type)
        print(warning_msg)
        pytest.skip(f"Could not read {file_type} file from atpack: {e}")


@pytest.fixture
def pic_atpack_file() -> Path:
    """Fixture that provides the PIC AtPack file path."""
    return PIC_ATPACK_FILE


@pytest.fixture
def pic24f_atpack_file() -> Path:
    """Fixture that provides the PIC24F AtPack file path."""
    return PIC24F_ATPACK_FILE


@pytest.fixture
def atmel_atpack_file() -> Path:
    """Fixture that provides the ATMEL AtPack file path."""
    return ATMEL_ATPACK_FILE


@pytest.fixture
def pic_content(pic_atpack_file: Path) -> str:
    """Fixture that provides PIC16F876A content from the AtPack file."""
    skip_if_atpack_missing(pic_atpack_file, "PIC")
    return read_from_atpack(pic_atpack_file, "edc/PIC16F876A.PIC", "PIC")


@pytest.fixture
def pic24f_content(pic24f_atpack_file: Path) -> str:
    """Fixture that provides PIC24F content from the AtPack file."""
    skip_if_atpack_missing(pic24f_atpack_file, "PIC24F")
    return read_from_atpack(pic24f_atpack_file, "edc/PIC24F.PIC", "PIC24F")


@pytest.fixture
def atmel_content(atmel_atpack_file: Path) -> str:
    """Fixture that provides ATmega16 content from the AtPack file."""
    skip_if_atpack_missing(atmel_atpack_file, "ATMEL")
    return read_from_atpack(atmel_atpack_file, "atdf/ATmega16.atdf", "ATDF")
