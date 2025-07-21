"""Test configuration."""

import sys
import zipfile
from pathlib import Path
import pytest

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# AtPack file paths
ATPACKS_DIR = Path(__file__).parent.parent / "atpacks"
MICROCHIP_PIC16FXXX_ATPACK_FILE = ATPACKS_DIR / "Microchip.PIC16Fxxx_DFP.1.7.162.atpack"
MICROCHIP_PIC24F_KA_KL_KM_ATPACK_FILE = (
    ATPACKS_DIR / "Microchip.PIC24F-KA-KL-KM_DFP.1.5.253.atpack"
)
ATMEL_ATMEGA_ATPACK_FILE = ATPACKS_DIR / "Atmel.ATmega_DFP.2.2.509.atpack"


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
def microchip_pic16fxxx_atpack_file() -> Path:
    """Fixture that provides the PIC AtPack file path."""
    return MICROCHIP_PIC16FXXX_ATPACK_FILE


@pytest.fixture
def microchip_pic24f_ka_kl_km_atpack_file() -> Path:
    """Fixture that provides the PIC24F AtPack file path."""
    return MICROCHIP_PIC24F_KA_KL_KM_ATPACK_FILE


@pytest.fixture
def atmel_atmega_atpack_file() -> Path:
    """Fixture that provides the ATMEL AtPack file path."""
    return ATMEL_ATMEGA_ATPACK_FILE


@pytest.fixture
def microchip_pic16fxxx_edc_pic16f877_pic_content(
    microchip_pic16fxxx_atpack_file: Path,
) -> str:
    """Fixture that provides PIC16F877 content from the AtPack file."""
    skip_if_atpack_missing(microchip_pic16fxxx_atpack_file, "PIC")
    return read_from_atpack(microchip_pic16fxxx_atpack_file, "edc/PIC16F877.PIC", "PIC")


@pytest.fixture
def microchip_pic24f_ka_kl_km_content_fixture(
    microchip_pic24f_ka_kl_km_atpack_file: Path,
) -> Path:
    """Fixture that checks for PIC24F AtPack availability and returns path if available."""
    skip_if_atpack_missing(microchip_pic24f_ka_kl_km_atpack_file, "PIC24F")
    return microchip_pic24f_ka_kl_km_atpack_file


@pytest.fixture
def microchip_pic16fxxx_content_fixture(microchip_pic16fxxx_atpack_file: Path) -> Path:
    """Fixture that checks for PIC16Fxxx AtPack availability and returns path if available."""
    skip_if_atpack_missing(microchip_pic16fxxx_atpack_file, "PIC")
    return microchip_pic16fxxx_atpack_file


@pytest.fixture
def atmel_atmega_content_fixture(atmel_atmega_atpack_file: Path) -> Path:
    """Fixture that checks for ATMEL AtPack availability and returns path if available."""
    skip_if_atpack_missing(atmel_atmega_atpack_file, "ATMEL")
    return atmel_atmega_atpack_file


@pytest.fixture
def atmel_atmega_atmega16_atdf_content(atmel_atmega_atpack_file: Path) -> str:
    """Fixture that provides ATmega16 content from the AtPack file."""
    skip_if_atpack_missing(atmel_atmega_atpack_file, "ATMEL")
    return read_from_atpack(atmel_atmega_atpack_file, "atdf/ATmega16.atdf", "ATDF")
