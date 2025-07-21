"""Unit handling utilities using pint for consistent unit management and display."""

import pint
from typing import Union, Optional


# Create a unit registry instance
ureg = pint.UnitRegistry()
ureg.define("Hz = hertz")  # Ensure Hz is defined


def parse_frequency(frequency_str: str) -> pint.Quantity:
    """Parse a frequency string into a pint Quantity.

    Args:
        frequency_str: Frequency string like "4000000 Hz", "20 MHz", etc.

    Returns:
        pint.Quantity: The parsed frequency quantity
    """
    try:
        return ureg.Quantity(frequency_str)
    except (ValueError, pint.UndefinedUnitError):
        # Try to parse as number + Hz if no unit specified
        try:
            value = float(frequency_str.replace(" Hz", "").replace("Hz", ""))
            return ureg.Quantity(value, "Hz")
        except ValueError:
            # Fallback to original string
            return frequency_str


def format_frequency(frequency: Union[str, pint.Quantity], compact: bool = True) -> str:
    """Format frequency for display with appropriate units.

    Args:
        frequency: Frequency as string or pint Quantity
        compact: If True, use compact notation (MHz, kHz), else show full Hz

    Returns:
        str: Formatted frequency string
    """
    if isinstance(frequency, str):
        # Try to parse if it's a string
        if frequency == "N/A" or not frequency:
            return frequency

        # If it's already in a nice format (contains MHz, kHz, etc.), keep it
        if compact and any(unit in frequency for unit in [" MHz", " kHz", " GHz"]):
            return frequency

        freq_qty = parse_frequency(frequency)
    else:
        freq_qty = frequency

    if isinstance(freq_qty, str):
        # Could not parse, return as-is
        return freq_qty

    try:
        # Convert to appropriate units for display
        if compact:
            if freq_qty.magnitude >= 1_000_000:
                return f"{freq_qty.to('MHz'):~P.0f}"  # e.g., "20 MHz"
            elif freq_qty.magnitude >= 1_000:
                return f"{freq_qty.to('kHz'):~P.0f}"  # e.g., "4 kHz"
            else:
                return f"{freq_qty.to('Hz'):~P.0f}"  # e.g., "200 Hz"
        else:
            return f"{freq_qty:~P}"
    except (AttributeError, TypeError):
        # Fallback to string representation
        return str(freq_qty)


def parse_voltage(voltage_str: str) -> Union[pint.Quantity, str]:
    """Parse a voltage string into a pint Quantity.

    Args:
        voltage_str: Voltage string like "3.3V", "5.0 V", etc.

    Returns:
        Union[pint.Quantity, str]: The parsed voltage quantity or original string
    """
    if voltage_str == "N/A" or not voltage_str:
        return voltage_str

    try:
        return ureg.Quantity(voltage_str)
    except (ValueError, pint.UndefinedUnitError):
        # Try to parse as number + V if no unit specified
        try:
            value = float(voltage_str.replace("V", "").strip())
            return ureg.Quantity(value, "V")
        except ValueError:
            return voltage_str


def format_voltage(voltage: Union[str, pint.Quantity]) -> str:
    """Format voltage for display.

    Args:
        voltage: Voltage as string or pint Quantity

    Returns:
        str: Formatted voltage string
    """
    if isinstance(voltage, str):
        if voltage == "N/A" or not voltage:
            return voltage
        voltage_qty = parse_voltage(voltage)
    else:
        voltage_qty = voltage

    if isinstance(voltage_qty, str):
        return voltage_qty

    try:
        return f"{voltage_qty:~P.1f}"  # e.g., "3.3 V"
    except (AttributeError, TypeError):
        return str(voltage_qty)


def parse_voltage_range(voltage_range_str: str) -> str:
    """Parse and format a voltage range string using pint.

    Args:
        voltage_range_str: Voltage range string like "2.0V to 5.5V", "1.8V to 3.6V"

    Returns:
        str: Formatted voltage range string
    """
    if voltage_range_str == "N/A" or not voltage_range_str:
        return voltage_range_str

    # Handle range patterns like "X.XV to Y.YV"
    if " to " in voltage_range_str:
        try:
            parts = voltage_range_str.split(" to ")
            if len(parts) == 2:
                min_voltage = parse_voltage(parts[0].strip())
                max_voltage = parse_voltage(parts[1].strip())

                if hasattr(min_voltage, "magnitude") and hasattr(
                    max_voltage, "magnitude"
                ):
                    min_formatted = format_voltage(min_voltage)
                    max_formatted = format_voltage(max_voltage)
                    return f"{min_formatted} to {max_formatted}"
        except Exception:
            pass

    return voltage_range_str


def format_voltage_range(
    vdd_min: Union[str, pint.Quantity], vdd_max: Union[str, pint.Quantity]
) -> str:
    """Format a voltage range for display.

    Args:
        vdd_min: Minimum voltage
        vdd_max: Maximum voltage

    Returns:
        str: Formatted voltage range string like "2.0V to 5.5V"
    """
    if isinstance(vdd_min, str) and (vdd_min == "N/A" or not vdd_min):
        return "N/A"
    if isinstance(vdd_max, str) and (vdd_max == "N/A" or not vdd_max):
        return "N/A"

    try:
        min_formatted = format_voltage(vdd_min)
        max_formatted = format_voltage(vdd_max)
        return f"{min_formatted} to {max_formatted}"
    except Exception:
        return "N/A"


def parse_temperature(temperature_str: str) -> Union[pint.Quantity, str]:
    """Parse a temperature string into a pint Quantity.

    Args:
        temperature_str: Temperature string like "25°C", "25 C", "77°F", etc.

    Returns:
        Union[pint.Quantity, str]: The parsed temperature quantity or original string
    """
    if temperature_str == "N/A" or not temperature_str:
        return temperature_str

    try:
        import re

        # Extract numeric value and unit
        match = re.search(r"([+-]?\d+(?:\.\d+)?)\s*([°]?[CcFf]?)", temperature_str)
        if match:
            value = float(match.group(1))
            unit_part = match.group(2).upper()

            # Handle temperature units - always interpret C as celsius, not coulomb
            if unit_part in ["C", "°C"]:
                return ureg.Quantity(value, "celsius")
            elif unit_part in ["F", "°F"]:
                return ureg.Quantity(value, "fahrenheit")
            else:
                # No unit specified, assume celsius
                return ureg.Quantity(value, "celsius")
        else:
            # Fallback to original behavior for other formats
            return ureg.Quantity(temperature_str.replace("°", " "))
    except (ValueError, pint.UndefinedUnitError):
        return temperature_str


def format_temperature(temperature: Union[str, pint.Quantity]) -> str:
    """Format temperature for display.

    Args:
        temperature: Temperature as string or pint Quantity

    Returns:
        str: Formatted temperature string like "25°C"
    """
    if isinstance(temperature, str):
        if temperature == "N/A" or not temperature:
            return temperature

        # If it already contains °C, keep it as-is
        if "°C" in temperature:
            return temperature

        temperature_qty = parse_temperature(temperature)
    else:
        temperature_qty = temperature

    if isinstance(temperature_qty, str):
        return temperature_qty

    try:
        # Format with degree symbol
        temp_c = temperature_qty.to("celsius")
        return f"{temp_c.magnitude:g}°C"
    except (AttributeError, TypeError, pint.UndefinedUnitError):
        return str(temperature_qty)


def parse_temperature_range(temp_range_str: str) -> str:
    """Parse and format a temperature range string using pint.

    Args:
        temp_range_str: Temperature range string like "-40°C to +85°C", "0 to 70°C"

    Returns:
        str: Formatted temperature range string
    """
    if temp_range_str == "N/A" or not temp_range_str:
        return temp_range_str

    # Handle range patterns like "X°C to Y°C" or "X to Y°C"
    if " to " in temp_range_str:
        try:
            parts = temp_range_str.split(" to ")
            if len(parts) == 2:
                min_temp = parse_temperature(parts[0].strip())
                max_temp = parse_temperature(parts[1].strip())

                if hasattr(min_temp, "magnitude") and hasattr(max_temp, "magnitude"):
                    min_formatted = format_temperature(min_temp)
                    max_formatted = format_temperature(max_temp)
                    return f"{min_formatted} to {max_formatted}"
        except Exception:
            pass

    # Handle individual temperature values that might not be ranges
    try:
        temp_qty = parse_temperature(temp_range_str)
        if hasattr(temp_qty, "magnitude"):
            return format_temperature(temp_qty)
    except Exception:
        pass

    return temp_range_str
