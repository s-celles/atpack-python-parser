"""XML parsing utilities using lxml and XPath."""

import os
import zipfile
from pathlib import Path
from typing import Dict, List, Optional

from lxml import etree

from ..exceptions import ParseError


class XmlParser:
    """XML parser with XPath utilities."""

    def __init__(self, xml_content: str):
        """Initialize parser with XML content."""
        try:
            self.tree = etree.fromstring(xml_content.encode("utf-8"))

            # Extract namespaces from the root element
            self.namespaces = {}
            for prefix, uri in self.tree.nsmap.items():
                if prefix is not None:  # Skip default namespace
                    self.namespaces[prefix] = uri

            # Add common namespaces if not present
            if "edc" not in self.namespaces:
                self.namespaces["edc"] = "http://crownking/edc"

        except etree.XMLSyntaxError as e:
            raise ParseError(f"Invalid XML content: {e}")

    def xpath(
        self, expression: str, context_element: Optional[etree._Element] = None
    ) -> List[etree._Element]:
        """Execute XPath query and return elements."""
        try:
            context = context_element if context_element is not None else self.tree
            result = context.xpath(expression, namespaces=self.namespaces)
            if isinstance(result, list):
                return [elem for elem in result if isinstance(elem, etree._Element)]
            return []
        except etree.XPathEvalError as e:
            raise ParseError(f"XPath error: {e}")

    def xpath_text(
        self, expression: str, default: Optional[str] = None
    ) -> Optional[str]:
        """Execute XPath query and return text content."""
        result = self.tree.xpath(expression, namespaces=self.namespaces)
        if result and isinstance(result[0], str):
            return result[0]
        elif result and hasattr(result[0], "text"):
            return result[0].text
        return default

    def get_attr(
        self, element: etree._Element, attr_name: str, default: Optional[str] = None
    ) -> Optional[str]:
        """Get attribute value from element, trying both namespaced and non-namespaced versions."""
        # Try without namespace first
        value = element.get(attr_name)
        if value is not None:
            return value

        # Try with each registered namespace
        for prefix, namespace in self.namespaces.items():
            if prefix:  # Skip empty prefix
                namespaced_attr = f"{{{namespace}}}{attr_name}"
                value = element.get(namespaced_attr)
                if value is not None:
                    return value

        return default

    def get_attr_int(
        self, element: etree._Element, attr_name: str, default: int = 0
    ) -> int:
        """Get integer attribute value from element."""
        value = self.get_attr(element, attr_name, str(default))
        try:
            return int(value, 16) if value.startswith("0x") else int(value)
        except (ValueError, TypeError):
            return default

    def get_attr_hex(
        self, element: etree._Element, attr_name: str, default: int = 0
    ) -> int:
        """Get hex attribute value from element."""
        value = self.get_attr(element, attr_name, f"0x{default:x}")
        try:
            return int(value, 16) if value.startswith("0x") else int(value, 16)
        except (ValueError, TypeError):
            return default


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
