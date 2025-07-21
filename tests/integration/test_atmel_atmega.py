#!/usr/bin/env python3
"""
Integration tests for ATMEL parser functionality.
"""

import pytest
from src.atpack_parser.atdf_parser import AtdfParser
from src.atpack_parser.models import DeviceFamily


class TestAtmelATmega16Integration:
    """Integration tests for ATmega16 device parsing."""

    @pytest.fixture
    def atmega16_device(self, atmel_atmega_atmega16_atdf_content):
        """Parse ATmega16 device from ATDF content."""
        parser = AtdfParser(atmel_atmega_atmega16_atdf_content)
        return parser.parse_device("ATmega16")

    @pytest.mark.integration
    @pytest.mark.atpack_required
    def test_atmega16_basic_device_info(self, atmega16_device):
        """Test basic device information parsing."""
        device = atmega16_device
        
        # Basic device properties
        assert device.name == "ATmega16"
        assert device.family == DeviceFamily.ATMEL
        assert device.architecture is not None
        assert device.series is not None

    @pytest.mark.integration
    @pytest.mark.atpack_required
    def test_atmega16_memory_segments(self, atmega16_device):
        """Test memory segment parsing."""
        device = atmega16_device
        
        # Should have memory segments
        assert len(device.memory_segments) > 0
        
        # Check for common ATmega16 memory segments
        segment_names = [seg.name.upper() for seg in device.memory_segments]
        
        # ATmega16 should have these memory types
        assert any("FLASH" in name or "PROG" in name for name in segment_names), "Should have program memory"
        assert any("SRAM" in name or "RAM" in name or "DATA" in name for name in segment_names), "Should have SRAM"
        assert any("EEPROM" in name for name in segment_names), "Should have EEPROM"

    @pytest.mark.integration
    @pytest.mark.atpack_required
    def test_atmega16_modules_and_registers(self, atmega16_device):
        """Test module and register parsing."""
        device = atmega16_device
        
        # Should have modules
        assert len(device.modules) > 0
        
        # Should have registers across modules
        total_registers = sum(
            len(rg.registers) 
            for module in device.modules 
            for rg in module.register_groups
        )
        assert total_registers > 0, "Should have registers defined"

    @pytest.mark.integration
    @pytest.mark.atpack_required
    def test_atmega16_interrupts(self, atmega16_device):
        """Test interrupt vector parsing."""
        device = atmega16_device
        
        # ATmega16 should have interrupt vectors
        assert len(device.interrupts) > 0
        
        # Check for some common ATmega16 interrupts
        interrupt_names = [irq.name.upper() for irq in device.interrupts]
        assert any("RESET" in name for name in interrupt_names), "Should have RESET vector"

    @pytest.mark.integration
    @pytest.mark.atpack_required
    def test_atmega16_package_variants(self, atmega16_device):
        """Test ATMEL-specific package variant parsing."""
        device = atmega16_device
        
        if device.atmel_package_variants:
            # Validate package variant structure
            for variant in device.atmel_package_variants:
                assert variant.package is not None, "Package name should be defined"
                assert variant.pinout is not None, "Pinout should be defined"
                
                # Temperature ranges should be valid if present
                if variant.temp_min is not None and variant.temp_max is not None:
                    assert variant.temp_min < variant.temp_max, "Temperature range should be valid"
                
                # Voltage ranges should be valid if present
                if variant.vcc_min is not None and variant.vcc_max is not None:
                    assert variant.vcc_min < variant.vcc_max, "Voltage range should be valid"
                    assert variant.vcc_min > 0, "Minimum voltage should be positive"

    @pytest.mark.integration
    @pytest.mark.atpack_required
    def test_atmega16_pinout_information(self, atmega16_device):
        """Test ATMEL-specific pinout parsing."""
        device = atmega16_device
        
        if device.atmel_pinouts:
            # Validate pinout structure
            for pinout in device.atmel_pinouts:
                assert pinout.name is not None, "Pinout should have a name"
                assert pinout.pin_count > 0, "Pinout should have pins"
                assert len(pinout.pins) > 0, "Pinout should contain pin data"
                
                # Validate pin structure
                for pin in pinout.pins[:5]:  # Check first 5 pins
                    assert "position" in pin, "Pin should have position"
                    assert "pad" in pin, "Pin should have pad name"
                    assert isinstance(pin["position"], (int, str)), "Position should be int or str"

    @pytest.mark.integration
    @pytest.mark.atpack_required
    def test_atmega16_programming_interfaces(self, atmega16_device):
        """Test ATMEL-specific programming interface parsing."""
        device = atmega16_device
        
        if device.atmel_programming_interfaces:
            # Validate programming interface structure
            for interface in device.atmel_programming_interfaces:
                assert interface.name is not None, "Interface should have a name"
                assert interface.interface_type is not None, "Interface should have a type"
                
                # Common interface types for ATmega16
                valid_types = ["isp", "jtag", "spi", "parallel", "hvpp", "megajtag"]
                assert any(vtype in interface.interface_type.lower() for vtype in valid_types), \
                    f"Interface type '{interface.interface_type}' should be recognized"

    @pytest.mark.integration
    @pytest.mark.atpack_required
    def test_atmega16_clock_information(self, atmega16_device):
        """Test ATMEL-specific clock information parsing."""
        device = atmega16_device
        
        if device.atmel_clock_info:
            clock_info = device.atmel_clock_info
            
            # Maximum frequency should be reasonable for ATmega16
            if clock_info.max_frequency:
                assert clock_info.max_frequency > 0, "Max frequency should be positive"
                assert clock_info.max_frequency <= 20_000_000, "Max frequency should be realistic for ATmega16"
            
            # Clock modules should have valid structure
            if clock_info.clock_modules:
                for module in clock_info.clock_modules:
                    assert "name" in module, "Clock module should have a name"
            
            # Clock properties should have valid structure
            if clock_info.clock_properties:
                for prop_group in clock_info.clock_properties:
                    assert "name" in prop_group, "Property group should have a name"
                    assert "properties" in prop_group, "Property group should have properties"

    @pytest.mark.integration
    @pytest.mark.atpack_required
    def test_atmega16_gpio_information(self, atmega16_device):
        """Test ATMEL-specific GPIO information parsing."""
        device = atmega16_device
        
        if device.atmel_gpio_info:
            total_pins = 0
            port_names = []
            
            for gpio_port in device.atmel_gpio_info:
                assert gpio_port.port_name is not None, "GPIO port should have a name"
                port_names.append(gpio_port.port_name)
                
                if gpio_port.pin_count:
                    assert gpio_port.pin_count > 0, "Pin count should be positive"
                    total_pins += gpio_port.pin_count
                
                # Validate instances structure
                if gpio_port.instances:
                    for instance in gpio_port.instances:
                        assert isinstance(instance, dict), "Instance should be a dictionary"
            
            # ATmega16 typically has ports A, B, C, D, but may be named differently in ATDF
            # Just check that we found some GPIO ports
            assert len(port_names) > 0, f"Should find some GPIO ports, found: {port_names}"

    @pytest.mark.integration
    @pytest.mark.atpack_required
    def test_atmega16_comprehensive_data_coverage(self, atmega16_device):
        """Test comprehensive data coverage for PlatformIO board definitions."""
        device = atmega16_device
        
        # Count available data types
        data_coverage = {
            "basic_info": bool(device.name and device.family),
            "memory_segments": len(device.memory_segments) > 0,
            "modules": len(device.modules) > 0,
            "interrupts": len(device.interrupts) > 0,
            "package_variants": bool(device.atmel_package_variants),
            "pinouts": bool(device.atmel_pinouts),
            "programming_interfaces": bool(device.atmel_programming_interfaces),
            "clock_info": bool(device.atmel_clock_info),
            "gpio_info": bool(device.atmel_gpio_info),
        }
        
        # Basic requirements
        assert data_coverage["basic_info"], "Should have basic device info"
        assert data_coverage["memory_segments"], "Should have memory segments"
        assert data_coverage["modules"], "Should have peripheral modules"
        
        # ATMEL-specific enhancements should provide additional value
        atmel_specific_count = sum([
            data_coverage["package_variants"],
            data_coverage["pinouts"],
            data_coverage["programming_interfaces"],
            data_coverage["clock_info"],
            data_coverage["gpio_info"],
        ])
        
        # Should have at least some ATMEL-specific data
        assert atmel_specific_count > 0, "Should have ATMEL-specific enhancements beyond basic parsing"
        
        # Calculate coverage percentage
        total_coverage = sum(data_coverage.values())
        coverage_percentage = (total_coverage / len(data_coverage)) * 100
        
        # Should have good coverage for a comprehensive device definition
        assert coverage_percentage >= 60, f"Should have at least 60% data coverage, got {coverage_percentage:.1f}%"
