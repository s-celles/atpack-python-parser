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
