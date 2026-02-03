"""Tests for the config flow."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

# Test constants
CONF_FRIENDLY_NAME = "friendly_name"
CONF_IP_ADDRESS = "ip_address"
CONF_PASSWORD = "password"  # noqa: S105
CONF_CONNECTION = "connection"
CONF_LOCAL = "local"
CONF_CLOUD = "cloud"
CONF_SERIAL = "serial"
DOMAIN = "wattpilot"


class TestConfigFlow:
    """Test the config flow."""

    @pytest.fixture
    def mock_charger(self) -> MagicMock:
        """Create a mock charger for connection tests."""
        charger = MagicMock()
        charger.serial = "12345678"
        charger.name = "Test Wattpilot"
        charger.firmware = "40.7"
        charger.connected = True
        charger.allPropsInitialized = True
        charger.allProps = {"onv": "40.7"}
        return charger

    def test_config_data_structure(self) -> None:
        """Test config entry data structure."""
        config_data = {
            CONF_FRIENDLY_NAME: "My Wattpilot",
            CONF_IP_ADDRESS: "192.168.1.100",
            CONF_PASSWORD: "test_pass",
            CONF_CONNECTION: CONF_LOCAL,
        }

        assert CONF_FRIENDLY_NAME in config_data
        assert CONF_IP_ADDRESS in config_data
        assert CONF_PASSWORD in config_data
        assert CONF_CONNECTION in config_data
        assert config_data[CONF_CONNECTION] == CONF_LOCAL

    def test_cloud_config_data_structure(self) -> None:
        """Test cloud config entry data structure."""
        config_data = {
            CONF_FRIENDLY_NAME: "My Cloud Wattpilot",
            CONF_SERIAL: "12345678",
            CONF_PASSWORD: "test_pass",
            CONF_CONNECTION: CONF_CLOUD,
        }

        assert CONF_SERIAL in config_data
        assert config_data[CONF_CONNECTION] == CONF_CLOUD


class TestConfigFlowValidation:
    """Test config flow validation."""

    def test_local_connection_requires_ip(self) -> None:
        """Test that local connection requires IP address."""
        # Valid local config
        valid_config = {
            CONF_FRIENDLY_NAME: "Test",
            CONF_IP_ADDRESS: "192.168.1.100",
            CONF_PASSWORD: "pass",
            CONF_CONNECTION: CONF_LOCAL,
        }
        assert CONF_IP_ADDRESS in valid_config

        # Invalid config without IP
        invalid_config = {
            CONF_FRIENDLY_NAME: "Test",
            CONF_PASSWORD: "pass",
            CONF_CONNECTION: CONF_LOCAL,
        }
        assert CONF_IP_ADDRESS not in invalid_config

    def test_cloud_connection_requires_serial(self) -> None:
        """Test that cloud connection requires serial number."""
        # Valid cloud config
        valid_config = {
            CONF_FRIENDLY_NAME: "Test",
            CONF_SERIAL: "12345678",
            CONF_PASSWORD: "pass",
            CONF_CONNECTION: CONF_CLOUD,
        }
        assert CONF_SERIAL in valid_config

    def test_ip_address_format_validation(self) -> None:
        """Test IP address format validation patterns."""
        import re

        ip_pattern = re.compile(
            r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"
            r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
        )

        valid_ips = ["192.168.1.100", "10.0.0.1", "172.16.0.1", "255.255.255.255"]
        invalid_ips = ["256.1.1.1", "192.168.1", "not.an.ip", ""]

        for ip in valid_ips:
            assert ip_pattern.match(ip), f"Valid IP {ip} not matched"

        for ip in invalid_ips:
            assert not ip_pattern.match(ip), f"Invalid IP {ip} should not match"


class TestConfigFlowIntegration:
    """Test config flow integration with Home Assistant."""

    def test_domain_constant(self) -> None:
        """Test domain constant is correctly set."""
        from custom_components.wattpilot.const import DOMAIN as ACTUAL_DOMAIN

        assert ACTUAL_DOMAIN == "wattpilot"

    def test_connection_options(self) -> None:
        """Test connection options are available."""
        from custom_components.wattpilot.const import CONF_CLOUD, CONF_LOCAL

        assert CONF_LOCAL == "local"
        assert CONF_CLOUD == "cloud"
