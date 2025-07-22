"""AtPackExtractor class for extracting files from AtPack archives."""

from pathlib import Path
import zipfile
import os
from typing import Dict, List, Optional
from .exceptions import ParseError


class AtPackExtractor:
    """Extract files from AtPack archives."""

    def __init__(self, atpack_path: Path):
        """Initialize with AtPack file path."""
        self.atpack_path = Path(atpack_path)
        if not self.atpack_path.exists():
            raise FileNotFoundError(f"AtPack file not found: {atpack_path}")

    def is_directory(self) -> bool:
        """Check if the path is a directory (extracted AtPack)."""
        return self.atpack_path.is_dir()

    def is_zip_file(self) -> bool:
        """Check if the path is a ZIP file."""
        return self.atpack_path.is_file() and zipfile.is_zipfile(self.atpack_path)

    def list_files(self, pattern: Optional[str] = None) -> List[str]:
        """List files in AtPack."""
        if self.is_directory():
            files = []
            for root, _, filenames in os.walk(self.atpack_path):
                for filename in filenames:
                    rel_path = os.path.relpath(
                        os.path.join(root, filename), self.atpack_path
                    )
                    if pattern is None or pattern in rel_path:
                        files.append(rel_path.replace("\\", "/"))
            return files
        elif self.is_zip_file():
            with zipfile.ZipFile(self.atpack_path, "r") as zf:
                files = zf.namelist()
                if pattern:
                    files = [f for f in files if pattern in f]
                return files
        else:
            raise ParseError(f"Unsupported AtPack format: {self.atpack_path}")

    def read_file(self, file_path: str) -> str:
        """Read file content from AtPack."""
        if self.is_directory():
            full_path = self.atpack_path / file_path
            if not full_path.exists():
                raise FileNotFoundError(f"File not found in AtPack: {file_path}")
            return full_path.read_text(encoding="utf-8", errors="ignore")
        elif self.is_zip_file():
            with zipfile.ZipFile(self.atpack_path, "r") as zf:
                try:
                    return zf.read(file_path).decode("utf-8", errors="ignore")
                except KeyError:
                    raise FileNotFoundError(f"File not found in AtPack: {file_path}")
        else:
            raise ParseError(f"Unsupported AtPack format: {self.atpack_path}")

    def find_files(self, extensions: List[str]) -> Dict[str, List[str]]:
        """Find files with specific extensions."""
        result = {ext: [] for ext in extensions}

        all_files = self.list_files()
        for file_path in all_files:
            for ext in extensions:
                if file_path.lower().endswith(ext.lower()):
                    result[ext].append(file_path)

        return result

    def find_pdsc_files(self) -> List[str]:
        """Find PDSC files (package description)."""
        return [f for f in self.list_files() if f.lower().endswith(".pdsc")]

    def find_atdf_files(self) -> List[str]:
        """Find ATDF files (ATMEL device files)."""
        return [f for f in self.list_files() if f.lower().endswith(".atdf")]

    def find_pic_files(self) -> List[str]:
        """Find PIC files (Microchip device files)."""
        return [f for f in self.list_files() if f.lower().endswith(".pic")]
