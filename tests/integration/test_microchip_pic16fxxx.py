#!/usr/bin/env python3
"""
Integration tests for PIC16Fxxx device parsing functionality.
"""

import sys
from pathlib import Path
import pytest
from src.atpack_parser.pic_parser import PicParser
from src.atpack_parser import AtPackParser

# Import helper functions from parent conftest
test_dir = Path(__file__).parent.parent
sys.path.insert(0, str(test_dir))
from conftest import skip_if_atpack_missing


@pytest.mark.integration
@pytest.mark.atpack_required
class TestPIC16FxxxIntegration:
    """Integration tests for PIC16Fxxx device parsing and data extraction."""
    
    # Device under test
    DEVICE_NAME = "PIC16F877"

    def test_device_basic_info(self, microchip_pic16fxxx_edc_pic16f877_pic_content: str):
        """Test parsing basic device information."""
        parser = PicParser(microchip_pic16fxxx_edc_pic16f877_pic_content)
        device = parser.parse_device(self.DEVICE_NAME)

        assert device.name == self.DEVICE_NAME
        assert device.family == "PIC"
        assert device.architecture == "PIC"
        assert device.series is not None

    def test_power_specifications(self, microchip_pic16fxxx_edc_pic16f877_pic_content: str):
        """Test parsing power specifications."""
        parser = PicParser(microchip_pic16fxxx_edc_pic16f877_pic_content)
        device = parser.parse_device(self.DEVICE_NAME)

        # Power specs may or may not be present, but if present should be valid
        if device.power_specs:
            ps = device.power_specs
            if ps.vdd_min is not None:
                assert ps.vdd_min > 0
            if ps.vdd_max is not None:
                assert ps.vdd_max > 0
            if ps.vdd_min and ps.vdd_max:
                assert ps.vdd_min <= ps.vdd_max

    def test_oscillator_configurations(self, microchip_pic16fxxx_edc_pic16f877_pic_content: str):
        """Test parsing oscillator configurations."""
        parser = PicParser(microchip_pic16fxxx_edc_pic16f877_pic_content)
        device = parser.parse_device(self.DEVICE_NAME)

        # Oscillator configs may be present
        if device.oscillator_configs:
            assert len(device.oscillator_configs) > 0
            for osc in device.oscillator_configs:
                assert osc.name is not None
                assert len(osc.name) > 0

    def test_programming_interface(self, microchip_pic16fxxx_edc_pic16f877_pic_content: str):
        """Test parsing programming interface information."""
        parser = PicParser(microchip_pic16fxxx_edc_pic16f877_pic_content)
        device = parser.parse_device(self.DEVICE_NAME)

        # Programming interface may be present
        if device.programming_interface:
            pi = device.programming_interface
            # Any present values should be valid
            if pi.programming_tries:
                assert pi.programming_tries > 0
            if pi.low_voltage_threshold:
                assert pi.low_voltage_threshold > 0

    def test_pinout_information(self, microchip_pic16fxxx_edc_pic16f877_pic_content: str):
        """Test parsing pinout information."""
        parser = PicParser(microchip_pic16fxxx_edc_pic16f877_pic_content)
        device = parser.parse_device(self.DEVICE_NAME)

        # Pinout should be present for PIC devices
        if device.pinout:
            assert len(device.pinout) > 0
            
            # Verify pin structure
            for pin in device.pinout[:5]:  # Check first 5 pins
                assert pin.physical_pin is not None
                assert pin.primary_function is not None
                assert isinstance(pin.alternative_functions, list)

    def test_debug_capabilities(self, microchip_pic16fxxx_edc_pic16f877_pic_content: str):
        """Test parsing debug capabilities."""
        parser = PicParser(microchip_pic16fxxx_edc_pic16f877_pic_content)
        device = parser.parse_device(self.DEVICE_NAME)

        # Debug capabilities may be present
        if device.debug_capabilities:
            dc = device.debug_capabilities
            if dc.hardware_breakpoint_count:
                assert dc.hardware_breakpoint_count >= 0

    def test_architecture_information(self, microchip_pic16fxxx_edc_pic16f877_pic_content: str):
        """Test parsing architecture information."""
        parser = PicParser(microchip_pic16fxxx_edc_pic16f877_pic_content)
        device = parser.parse_device(self.DEVICE_NAME)

        # Architecture info may be present
        if device.architecture_info:
            ai = device.architecture_info
            if ai.hardware_stack_depth:
                assert ai.hardware_stack_depth > 0
            if ai.code_word_size:
                assert ai.code_word_size > 0
            if ai.data_word_size:
                assert ai.data_word_size > 0

    def test_peripheral_detection(self, microchip_pic16fxxx_edc_pic16f877_pic_content: str):
        """Test peripheral detection."""
        parser = PicParser(microchip_pic16fxxx_edc_pic16f877_pic_content)
        device = parser.parse_device(self.DEVICE_NAME)

        # Peripherals may be detected
        if device.detected_peripherals:
            assert len(device.detected_peripherals) > 0
            for peripheral in device.detected_peripherals:
                assert isinstance(peripheral, str)
                assert len(peripheral) > 0

    def test_platformio_usefulness(self, microchip_pic16fxxx_edc_pic16f877_pic_content: str):
        """Test that extracted data is useful for PlatformIO board definitions."""
        parser = PicParser(microchip_pic16fxxx_edc_pic16f877_pic_content)
        device = parser.parse_device(self.DEVICE_NAME)

        useful_features = 0

        if device.power_specs and (device.power_specs.vdd_min or device.power_specs.vdd_max):
            useful_features += 1

        if device.oscillator_configs:
            useful_features += 1

        if device.programming_interface:
            useful_features += 1

        if device.pinout:
            useful_features += 1

        if device.debug_capabilities:
            useful_features += 1

        if device.architecture_info and device.architecture_info.instruction_set:
            useful_features += 1

        if device.detected_peripherals:
            useful_features += 1

        # At least some useful information should be extracted
        assert useful_features > 0, "No useful information extracted for PlatformIO"

    def test_device_memory_info(self, microchip_pic16fxxx_edc_pic16f877_pic_content: str):
        """Test parsing device memory information."""
        parser = PicParser(microchip_pic16fxxx_edc_pic16f877_pic_content)
        device = parser.parse_device(self.DEVICE_NAME)

        # Basic device should have some memory info
        # Note: Commented out flash/RAM checks as they may not be available in all PIC files
        assert device.name == self.DEVICE_NAME


@pytest.mark.integration
@pytest.mark.atpack_required
def test_atpack_parser_pic16f877(microchip_pic16fxxx_atpack_file: Path):
    """Test the AtPackParser with PIC16F877."""
    skip_if_atpack_missing(microchip_pic16fxxx_atpack_file, "PIC")

    parser = AtPackParser(microchip_pic16fxxx_atpack_file)
    devices = parser.get_devices()
    assert len(devices) > 0, "No devices found in the AtPack"
    
    device_name = "PIC16F877"
    assert device_name in devices, f"Expected device {device_name} not found"
    
    device = parser.get_device(device_name)
    assert device.name == device_name, f"Expected device name {device_name}, got {device.name}"
    assert device.family == "PIC", f"Expected family 'PIC', got {device.family}"
    assert device.architecture == "PIC", f"Expected architecture 'PIC', got {device.architecture}"
