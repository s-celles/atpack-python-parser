"""Utilities for extracting device specifications from configuration data."""

import json
from pathlib import Path
from typing import Any, Dict, Optional

from .units import (
    format_frequency,
    parse_frequency,
    parse_temperature_range,
    parse_voltage_range,
)

# Cache for loaded configuration data
_device_specs_cache: Optional[Dict[str, Any]] = None


def _load_device_specs() -> Dict[str, Any]:
    """Load device specifications from configuration file."""
    global _device_specs_cache

    if _device_specs_cache is None:
        # The data directory is parallel to the utils directory
        specs_file = Path(__file__).parent.parent / "data" / "pic_device_specs.json"
        if specs_file.exists():
            with open(specs_file, "r", encoding="utf-8") as f:
                _device_specs_cache = json.load(f)
        else:
            # Fallback empty config if file doesn't exist
            _device_specs_cache = {
                "oscillator_frequencies": {},
                "temperature_ranges": {},
                "device_defaults": {},
                "temperature_suffixes": {},
            }

    return _device_specs_cache


def get_max_frequency_from_oscillators(
    oscillator_configs, device_name: str = ""
) -> str:
    """Extract maximum frequency from oscillator configurations."""
    if not oscillator_configs:
        return "N/A"

    specs = _load_device_specs()
    osc_frequencies = specs.get("oscillator_frequencies", {})

    max_frequencies = []

    for osc in oscillator_configs:
        if hasattr(osc, "name"):
            osc_name = osc.name.upper()

            # Look up frequency for each oscillator type
            for osc_type, frequency in osc_frequencies.items():
                if osc_type in osc_name:
                    max_frequencies.append(frequency)
                    break

    if not max_frequencies:
        return "N/A"

    # Find the highest frequency using pint for proper unit handling
    max_freq = None
    max_freq_value = 0

    for freq_str in max_frequencies:
        freq_qty = parse_frequency(freq_str)
        if hasattr(freq_qty, "magnitude"):
            # Convert to Hz for comparison
            freq_hz = freq_qty.to("Hz").magnitude
            if freq_hz > max_freq_value:
                max_freq_value = freq_hz
                max_freq = freq_qty

    if max_freq:
        return format_frequency(max_freq)

    # Fallback to first frequency if parsing fails
    return format_frequency(max_frequencies[0])


def get_device_default_frequency(device_name: str) -> str:
    """Get default maximum frequency for a device based on its name/series."""
    specs = _load_device_specs()
    device_defaults = specs.get("device_defaults", {})

    device_upper = device_name.upper()

    # Check each device series pattern
    for series_pattern, defaults in device_defaults.items():
        if series_pattern in device_upper:
            freq_str = defaults.get("max_frequency", "N/A")
            if freq_str != "N/A":
                return format_frequency(freq_str)
            return freq_str

    return "N/A"


def get_temperature_range_from_device_name(device_name: str) -> str:
    """Extract temperature range from device name using suffix patterns."""
    specs = _load_device_specs()
    temp_suffixes = specs.get("temperature_suffixes", {})
    temp_ranges = specs.get("temperature_ranges", {})
    device_defaults = specs.get("device_defaults", {})

    device_upper = device_name.upper()

    # Check for temperature suffix patterns (e.g., E/, I/, C/)
    for suffix, range_type in temp_suffixes.items():
        patterns = [f"{suffix}/", f"{suffix}-", f"{suffix}P", f"{suffix}T"]
        if any(pattern in device_upper for pattern in patterns):
            temp_range = temp_ranges.get(range_type, "N/A")
            if temp_range != "N/A":
                return parse_temperature_range(temp_range)
            return temp_range

    # Fallback to device series default
    for series_pattern, defaults in device_defaults.items():
        if series_pattern in device_upper:
            range_type = defaults.get("temperature_range", "industrial")
            temp_range = temp_ranges.get(range_type, "N/A")
            if temp_range != "N/A":
                return parse_temperature_range(temp_range)
            return temp_range

    return "N/A"


def get_device_default_vdd_range(device_name: str) -> str:
    """Get default VDD range for a device based on its name/series."""
    specs = _load_device_specs()
    device_defaults = specs.get("device_defaults", {})

    device_upper = device_name.upper()

    # Check each device series pattern
    for series_pattern, defaults in device_defaults.items():
        if series_pattern in device_upper:
            vdd_range = defaults.get("vdd_range", "N/A")
            if vdd_range != "N/A":
                return parse_voltage_range(vdd_range)
            return vdd_range

    return "N/A"
