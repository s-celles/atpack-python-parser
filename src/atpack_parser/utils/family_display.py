"""
Utilities for device family display and formatting.
Provides consistent color/emoji schema matching atpack-ts-viewer conventions.
"""

from ..models import DeviceFamily


def get_family_emoji(family: DeviceFamily) -> str:
    """
    Get the emoji representation for a device family.
    Uses conventional colors matching the test expectations:
    - ATMEL: Blue -> 🔵
    - Microchip/PIC: Yellow -> 🔴

    Args:
        family: The device family

    Returns:
        str: Emoji representation of the family
    """
    emoji_map = {
        DeviceFamily.ATMEL: "🔵",  # Blue circle for ATMEL
        DeviceFamily.PIC: "🔴",  # Yellow circle for Microchip/PIC
    }
    return emoji_map.get(family, "❓")  # Question mark for unknown


def get_family_title(family: DeviceFamily) -> str:
    """
    Get the full title for a device family.

    Args:
        family: The device family

    Returns:
        str: Full title of the family
    """
    title_map = {
        DeviceFamily.ATMEL: "ATMEL Microcontroller",
        DeviceFamily.PIC: "Microchip PIC Microcontroller",
    }
    return title_map.get(family, "Unknown Family")


def format_family_display(family: DeviceFamily, include_name: bool = True) -> str:
    """
    Format a device family for display with emoji and optional name.

    Args:
        family: The device family
        include_name: Whether to include the family name

    Returns:
        str: Formatted family display string
    """
    emoji = get_family_emoji(family)
    if include_name:
        return f"{emoji} {family.value}"
    return emoji
