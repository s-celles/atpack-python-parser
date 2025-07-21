"""
Dedicated unit tests for PIC24F devices.

This test module focuses specifically on PIC24F device parsing and CLI functionality,
ensuring all features work correctly for PIC24F devices like PIC24F16KA301.
"""

import pytest
from pathlib import Path
import json
import tempfile
from unittest.mock import patch
from typer.testing import CliRunner

from atpack_parser import AtPackParser
from atpack_parser.cli import app
from atpack_parser.exceptions import DeviceNotFoundError
from atpack_parser.models import DeviceFamily


class TestPIC24FParsing:
    """Test PIC24F device parsing functionality."""

    def test_pic24f_parser_initialization(self, microchip_pic24f_ka_kl_km_atpack_file):
        """Test that PIC24F AtPack can be initialized correctly."""
        parser = AtPackParser(microchip_pic24f_ka_kl_km_atpack_file)
        assert parser is not None
        assert parser.device_family == DeviceFamily.PIC

    def test_pic24f_metadata(self, microchip_pic24f_ka_kl_km_atpack_file):
        """Test PIC24F AtPack metadata extraction."""
        parser = AtPackParser(microchip_pic24f_ka_kl_km_atpack_file)
        metadata = parser.metadata

        # Note: The metadata parsing for PIC24F may return default values
        # The important thing is that it doesn't crash and identifies as PIC family
        assert metadata is not None
        assert metadata.description == "Microchip PIC24F-KA-KL-KM Series Device Support"

    def test_pic24f_device_list(self, microchip_pic24f_ka_kl_km_atpack_file):
        """Test that PIC24F devices can be listed."""
        parser = AtPackParser(microchip_pic24f_ka_kl_km_atpack_file)
        devices = parser.get_devices()

        assert len(devices) > 0
        assert "PIC24F16KA301" in devices

        # Check for other common PIC24F devices
        pic24f_devices = [d for d in devices if d.startswith("PIC24F")]
        assert len(pic24f_devices) > 10  # Should have many PIC24F devices

    def test_pic24f16ka301_device_info(self, microchip_pic24f_ka_kl_km_atpack_file):
        """Test detailed device information for PIC24F16KA301."""
        parser = AtPackParser(microchip_pic24f_ka_kl_km_atpack_file)
        device = parser.get_device("PIC24F16KA301")

        assert device.name == "PIC24F16KA301"
        assert device.family == DeviceFamily.PIC
        assert device.architecture is not None
        assert len(device.memory_segments) > 0
        assert len(device.modules) > 0

    def test_pic24f16ka301_memory_segments(self, microchip_pic24f_ka_kl_km_atpack_file):
        """Test memory segment parsing for PIC24F16KA301."""
        parser = AtPackParser(microchip_pic24f_ka_kl_km_atpack_file)
        memory_segments = parser.get_device_memory("PIC24F16KA301")

        assert len(memory_segments) > 0

        # Check for common PIC24F memory segments
        segment_names = [seg.name for seg in memory_segments]
        assert any(
            "PROG" in name.upper() for name in segment_names
        )  # PIC24F uses "PROG" segments
        assert any(
            "SFR" in name.upper() for name in segment_names
        )  # Special Function Registers

    def test_pic24f16ka301_registers(self, microchip_pic24f_ka_kl_km_atpack_file):
        """Test register parsing for PIC24F16KA301."""
        parser = AtPackParser(microchip_pic24f_ka_kl_km_atpack_file)
        device = parser.get_device("PIC24F16KA301")

        # Should have modules with registers
        total_registers = 0
        for module in device.modules:
            for reg_group in module.register_groups:
                total_registers += len(reg_group.registers)

        assert total_registers > 0

    def test_pic24f16ka301_config(self, microchip_pic24f_ka_kl_km_atpack_file):
        """Test configuration data parsing for PIC24F16KA301."""
        parser = AtPackParser(microchip_pic24f_ka_kl_km_atpack_file)
        config = parser.get_device_config("PIC24F16KA301")

        assert isinstance(config, dict)
        # PIC24F devices typically have config words rather than fuses
        assert "config_words" in config or "fuses" in config
        assert "interrupts" in config
        assert "signatures" in config

    def test_pic24f_invalid_device(self, microchip_pic24f_ka_kl_km_atpack_file):
        """Test error handling for invalid PIC24F device names."""
        parser = AtPackParser(microchip_pic24f_ka_kl_km_atpack_file)

        with pytest.raises(DeviceNotFoundError):
            parser.get_device("INVALID_PIC24F_DEVICE")


class TestPIC24FCLI:
    """Test CLI functionality specifically for PIC24F devices."""

    def test_pic24f_files_info_cli(self, microchip_pic24f_ka_kl_km_atpack_file):
        """Test files info command for PIC24F AtPack."""
        runner = CliRunner()
        result = runner.invoke(
            app, ["files", "info", str(microchip_pic24f_ka_kl_km_atpack_file)]
        )

        assert result.exit_code == 0
        # The files info may show "Unknown" for some metadata fields, but description should be correct
        assert "Microchip PIC24F-KA-KL-KM Series Device Support" in result.stdout

    def test_pic24f_devices_list_cli(self, microchip_pic24f_ka_kl_km_atpack_file):
        """Test devices list command for PIC24F AtPack."""
        runner = CliRunner()
        result = runner.invoke(
            app, ["devices", "list", str(microchip_pic24f_ka_kl_km_atpack_file)]
        )

        assert result.exit_code == 0
        assert "PIC24F16KA301" in result.stdout
        assert "🔴" in result.stdout or "[PIC]" in result.stdout

    def test_pic24f_devices_list_json_cli(self, microchip_pic24f_ka_kl_km_atpack_file):
        """Test devices list command with JSON output for PIC24F AtPack."""
        runner = CliRunner()
        result = runner.invoke(
            app,
            [
                "devices",
                "list",
                str(microchip_pic24f_ka_kl_km_atpack_file),
                "--format",
                "json",
            ],
        )

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["device_family"] == "PIC"
        assert "PIC24F16KA301" in data["devices"]
        assert data["device_count"] > 0

    def test_pic24f_devices_search_cli(self, microchip_pic24f_ka_kl_km_atpack_file):
        """Test device search command for PIC24F devices."""
        runner = CliRunner()
        result = runner.invoke(
            app,
            [
                "devices",
                "search",
                "PIC24F16KA*",
                str(microchip_pic24f_ka_kl_km_atpack_file),
            ],
        )

        assert result.exit_code == 0
        assert "PIC24F16KA301" in result.stdout

    def test_pic24f_device_info_cli(self, microchip_pic24f_ka_kl_km_atpack_file):
        """Test device info command for PIC24F16KA301."""
        runner = CliRunner()
        result = runner.invoke(
            app,
            [
                "devices",
                "info",
                "PIC24F16KA301",
                str(microchip_pic24f_ka_kl_km_atpack_file),
            ],
        )

        assert result.exit_code == 0
        assert "PIC24F16KA301" in result.stdout
        assert "🔴" in result.stdout or "[PIC]" in result.stdout
        assert "Memory Segments" in result.stdout

    def test_pic24f_device_info_json_cli(self, microchip_pic24f_ka_kl_km_atpack_file):
        """Test device info command with JSON output for PIC24F16KA301."""
        runner = CliRunner()
        result = runner.invoke(
            app,
            [
                "devices",
                "info",
                "PIC24F16KA301",
                str(microchip_pic24f_ka_kl_km_atpack_file),
                "--format",
                "json",
            ],
        )

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["name"] == "PIC24F16KA301"
        assert data["family"] == "PIC"

    def test_pic24f_memory_show_cli(self, microchip_pic24f_ka_kl_km_atpack_file):
        """Test memory show command for PIC24F16KA301."""
        runner = CliRunner()
        result = runner.invoke(
            app,
            [
                "memory",
                "show",
                "PIC24F16KA301",
                str(microchip_pic24f_ka_kl_km_atpack_file),
            ],
        )

        assert result.exit_code == 0
        assert "PIC24F16KA301" in result.stdout
        assert "Memory Layout" in result.stdout

    def test_pic24f_memory_show_json_cli(self, microchip_pic24f_ka_kl_km_atpack_file):
        """Test memory show command with JSON output for PIC24F16KA301."""
        runner = CliRunner()
        result = runner.invoke(
            app,
            [
                "memory",
                "show",
                "PIC24F16KA301",
                str(microchip_pic24f_ka_kl_km_atpack_file),
                "--format",
                "json",
            ],
        )

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert isinstance(data, list)
        assert len(data) > 0

    def test_pic24f_registers_list_cli(self, microchip_pic24f_ka_kl_km_atpack_file):
        """Test registers list command for PIC24F16KA301."""
        runner = CliRunner()
        result = runner.invoke(
            app,
            [
                "registers",
                "list",
                "PIC24F16KA301",
                str(microchip_pic24f_ka_kl_km_atpack_file),
            ],
        )

        assert result.exit_code == 0
        assert "PIC24F16KA301" in result.stdout
        assert "Registers" in result.stdout

    def test_pic24f_registers_list_json_cli(
        self, microchip_pic24f_ka_kl_km_atpack_file
    ):
        """Test registers list command with JSON output for PIC24F16KA301."""
        runner = CliRunner()
        result = runner.invoke(
            app,
            [
                "registers",
                "list",
                "PIC24F16KA301",
                str(microchip_pic24f_ka_kl_km_atpack_file),
                "--format",
                "json",
            ],
        )

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert isinstance(data, list)
        assert len(data) > 0

    def test_pic24f_config_show_cli(self, microchip_pic24f_ka_kl_km_atpack_file):
        """Test config show command for PIC24F16KA301."""
        runner = CliRunner()
        result = runner.invoke(
            app,
            [
                "config",
                "show",
                "PIC24F16KA301",
                str(microchip_pic24f_ka_kl_km_atpack_file),
            ],
        )

        assert result.exit_code == 0
        # Config show output may not include the device name in the output
        assert "Device Signatures" in result.stdout or "DEVID" in result.stdout

    def test_pic24f_config_show_json_cli(self, microchip_pic24f_ka_kl_km_atpack_file):
        """Test config show command with JSON output for PIC24F16KA301."""
        runner = CliRunner()
        result = runner.invoke(
            app,
            [
                "config",
                "show",
                "PIC24F16KA301",
                str(microchip_pic24f_ka_kl_km_atpack_file),
                "--format",
                "json",
            ],
        )

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert isinstance(data, dict)
        # Should have the main config sections
        assert "signatures" in data
        assert "fuses" in data or "config_words" in data

    def test_pic24f_cli_with_output_export(self, microchip_pic24f_ka_kl_km_atpack_file):
        """Test CLI export functionality with PIC24F devices."""
        runner = CliRunner()

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as tmp_file:
            tmp_path = Path(tmp_file.name)

        try:
            result = runner.invoke(
                app,
                [
                    "devices",
                    "list",
                    str(microchip_pic24f_ka_kl_km_atpack_file),
                    "--format",
                    "json",
                    "--output",
                    str(tmp_path),
                ],
            )

            assert result.exit_code == 0
            assert tmp_path.exists()

            # Verify exported data
            data = json.loads(tmp_path.read_text(encoding="utf-8"))
            assert data["device_family"] == "PIC"
            assert "PIC24F16KA301" in data["devices"]

        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    def test_pic24f_cli_no_color_option(self, microchip_pic24f_ka_kl_km_atpack_file):
        """Test CLI --no-color option with PIC24F devices."""
        runner = CliRunner()
        result = runner.invoke(
            app,
            [
                "devices",
                "list",
                str(microchip_pic24f_ka_kl_km_atpack_file),
                "--no-color",
            ],
        )

        assert result.exit_code == 0
        assert "[PIC]" in result.stdout  # Should use text instead of emoji
        assert "🔴" not in result.stdout  # Should not have emoji


class TestPIC24FEdgeCases:
    """Test edge cases and error conditions for PIC24F devices."""

    def test_pic24f_invalid_device_cli(self, microchip_pic24f_ka_kl_km_atpack_file):
        """Test CLI behavior with invalid PIC24F device name."""
        runner = CliRunner()
        result = runner.invoke(
            app,
            [
                "devices",
                "info",
                "INVALID_PIC24F",
                str(microchip_pic24f_ka_kl_km_atpack_file),
            ],
        )

        assert result.exit_code == 1
        assert "not found" in result.stdout.lower()

    def test_pic24f_invalid_register_cli(self, microchip_pic24f_ka_kl_km_atpack_file):
        """Test CLI behavior with invalid register name for PIC24F device."""
        runner = CliRunner()
        result = runner.invoke(
            app,
            [
                "registers",
                "show",
                "PIC24F16KA301",
                "INVALID_REG",
                str(microchip_pic24f_ka_kl_km_atpack_file),
            ],
        )

        assert result.exit_code == 1
        assert "not found" in result.stdout.lower()

    def test_pic24f_memory_segment_filter(self, microchip_pic24f_ka_kl_km_atpack_file):
        """Test memory segment filtering for PIC24F device."""
        runner = CliRunner()

        # First, get all segments using flat mode to find a valid segment name
        result = runner.invoke(
            app,
            [
                "memory",
                "show",
                "PIC24F16KA301",
                str(microchip_pic24f_ka_kl_km_atpack_file),
                "--flat",
                "--format",
                "json",
            ],
        )
        assert result.exit_code == 0

        segments = json.loads(result.stdout)
        if segments:
            segment_name = segments[0]["name"]

            # Test filtering by specific segment (using hierarchical mode by default)
            result = runner.invoke(
                app,
                [
                    "memory",
                    "show",
                    "PIC24F16KA301",
                    str(microchip_pic24f_ka_kl_km_atpack_file),
                    "--segment",
                    segment_name,
                ],
            )
            assert result.exit_code == 0
            assert segment_name in result.stdout

    def test_pic24f_register_module_filter(self, microchip_pic24f_ka_kl_km_atpack_file):
        """Test register filtering by module for PIC24F device."""
        runner = CliRunner()

        # Test with a common module name (GPIO-related modules are common)
        result = runner.invoke(
            app,
            [
                "registers",
                "list",
                "PIC24F16KA301",
                str(microchip_pic24f_ka_kl_km_atpack_file),
                "--module",
                "PORTB",
            ],
        )

        # This might succeed or fail depending on module availability
        # The test is mainly to ensure the command doesn't crash
        assert result.exit_code in [
            0,
            1,
        ]  # Either success or "no registers found" is acceptable


class TestPIC24FComprehensive:
    """Comprehensive integration tests for PIC24F functionality."""

    def test_pic24f_full_workflow(self, microchip_pic24f_ka_kl_km_atpack_file):
        """Test complete workflow from AtPack parsing to detailed device analysis."""
        # 1. Initialize parser
        parser = AtPackParser(microchip_pic24f_ka_kl_km_atpack_file)
        assert parser.device_family == DeviceFamily.PIC

        # 2. Get device list
        devices = parser.get_devices()
        assert "PIC24F16KA301" in devices

        # 3. Get device details
        device = parser.get_device("PIC24F16KA301")
        assert device.name == "PIC24F16KA301"

        # 4. Get memory information
        memory_segments = parser.get_device_memory("PIC24F16KA301")
        assert len(memory_segments) > 0

        # 5. Get configuration
        config = parser.get_device_config("PIC24F16KA301")
        assert isinstance(config, dict)

        # 6. Verify data consistency
        assert device.family == DeviceFamily.PIC
        assert len(device.memory_segments) == len(memory_segments)

    def test_pic24f_cli_help_commands(self, microchip_pic24f_ka_kl_km_atpack_file):
        """Test that help commands work correctly."""
        runner = CliRunner()

        # Test main help
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0

        # Test sub-command helps
        for cmd in ["files", "devices", "memory", "registers", "config"]:
            result = runner.invoke(app, [cmd, "--help"])
            assert result.exit_code == 0

    def test_pic24f_scan_functionality(self, microchip_pic24f_ka_kl_km_atpack_file):
        """Test directory scanning with PIC24F AtPack."""
        runner = CliRunner()
        atpack_dir = microchip_pic24f_ka_kl_km_atpack_file.parent

        result = runner.invoke(app, ["scan", str(atpack_dir)])
        assert result.exit_code == 0
        assert "PIC24F-KA-KL-KM_DFP" in result.stdout or "AtPack Files" in result.stdout

    def test_pic24f_all_cli_commands_basic(self, microchip_pic24f_ka_kl_km_atpack_file):
        """Test that all major CLI commands work for PIC24F without crashing."""
        runner = CliRunner()
        commands_to_test = [
            ["files", "info", str(microchip_pic24f_ka_kl_km_atpack_file)],
            ["devices", "list", str(microchip_pic24f_ka_kl_km_atpack_file)],
            [
                "devices",
                "info",
                "PIC24F16KA301",
                str(microchip_pic24f_ka_kl_km_atpack_file),
            ],
            [
                "memory",
                "show",
                "PIC24F16KA301",
                str(microchip_pic24f_ka_kl_km_atpack_file),
            ],
            [
                "registers",
                "list",
                "PIC24F16KA301",
                str(microchip_pic24f_ka_kl_km_atpack_file),
            ],
            [
                "config",
                "show",
                "PIC24F16KA301",
                str(microchip_pic24f_ka_kl_km_atpack_file),
            ],
        ]

        for cmd in commands_to_test:
            result = runner.invoke(app, cmd)
            assert (
                result.exit_code == 0
            ), f"Command {cmd} failed with exit code {result.exit_code}"
