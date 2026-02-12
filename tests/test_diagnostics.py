"""Tests for the Wattpilot diagnostics."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from .fixtures import get_charger_properties


class TestDiagnostics:
    """Test suite for diagnostics functionality."""

    @pytest.fixture
    def mock_hass(self) -> MagicMock:
        """Create a mock Home Assistant instance."""
        hass = MagicMock()
        hass.loop = MagicMock()
        hass.data = {}
        return hass

    @pytest.fixture
    def mock_charger(self) -> MagicMock:
        """Create a mock charger with all_properties."""
        charger = MagicMock()
        charger.serial = "12345678"
        charger.name = "Test Wattpilot"
        charger.firmware = "40.7"
        charger.connected = True
        charger.properties_initialized = True
        charger.all_properties = get_charger_properties()
        return charger

    @pytest.fixture
    def mock_entry(self, mock_charger: MagicMock) -> MagicMock:
        """Create a mock config entry with runtime_data."""
        entry = MagicMock()
        entry.entry_id = "test_entry_id"
        entry.data = {
            "friendly_name": "Test Wattpilot",
            "ip_address": "192.168.1.100",
            "password": "secret_password",
            "serial": "12345678",
        }
        entry.as_dict.return_value = {
            "entry_id": entry.entry_id,
            "data": entry.data,
            "options": {},
            "version": 1,
        }

        # Set up runtime_data with charger
        runtime_data = MagicMock()
        runtime_data.charger = mock_charger
        entry.runtime_data = runtime_data

        return entry

    @pytest.mark.asyncio
    async def test_diagnostics_returns_dict(
        self, mock_hass: MagicMock, mock_entry: MagicMock
    ) -> None:
        """Test that diagnostics returns a dictionary."""
        with patch(
            "custom_components.wattpilot.diagnostics.version", return_value="1.0.0"
        ):
            from custom_components.wattpilot.diagnostics import (
                async_get_config_entry_diagnostics,
            )

            result = await async_get_config_entry_diagnostics(mock_hass, mock_entry)

            assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_diagnostics_contains_config(
        self, mock_hass: MagicMock, mock_entry: MagicMock
    ) -> None:
        """Test that diagnostics contains config entry data."""
        with patch(
            "custom_components.wattpilot.diagnostics.version", return_value="1.0.0"
        ):
            from custom_components.wattpilot.diagnostics import (
                async_get_config_entry_diagnostics,
            )

            result = await async_get_config_entry_diagnostics(mock_hass, mock_entry)

            assert "config" in result

    @pytest.mark.asyncio
    async def test_diagnostics_redacts_sensitive_data(
        self, mock_hass: MagicMock, mock_entry: MagicMock
    ) -> None:
        """Test that diagnostics redacts sensitive information."""
        with patch(
            "custom_components.wattpilot.diagnostics.version", return_value="1.0.0"
        ):
            from custom_components.wattpilot.diagnostics import (
                async_get_config_entry_diagnostics,
            )

            result = await async_get_config_entry_diagnostics(mock_hass, mock_entry)

            # Check that password is redacted in config
            redacted_marker = "**REDACTED**"
            assert "config" in result
            assert "data" in result["config"]
            data = result["config"]["data"]
            assert "password" in data
            assert data["password"] == redacted_marker

    @pytest.mark.asyncio
    async def test_diagnostics_contains_charger_properties(
        self, mock_hass: MagicMock, mock_entry: MagicMock
    ) -> None:
        """Test that diagnostics contains charger properties."""
        with patch(
            "custom_components.wattpilot.diagnostics.version", return_value="1.0.0"
        ):
            from custom_components.wattpilot.diagnostics import (
                async_get_config_entry_diagnostics,
            )

            result = await async_get_config_entry_diagnostics(mock_hass, mock_entry)

            assert "charger_properties" in result
            assert isinstance(result["charger_properties"], dict)

    @pytest.mark.asyncio
    async def test_diagnostics_contains_charger_info(
        self, mock_hass: MagicMock, mock_entry: MagicMock
    ) -> None:
        """Test that diagnostics contains charger info."""
        with patch(
            "custom_components.wattpilot.diagnostics.version", return_value="1.0.0"
        ):
            from custom_components.wattpilot.diagnostics import (
                async_get_config_entry_diagnostics,
            )

            result = await async_get_config_entry_diagnostics(mock_hass, mock_entry)

            assert "charger_info" in result
            charger_info = result["charger_info"]
            assert charger_info["connected"] is True
            assert charger_info["firmware"] == "40.7"

    @pytest.mark.asyncio
    async def test_diagnostics_handles_missing_charger(
        self, mock_hass: MagicMock
    ) -> None:
        """Test diagnostics handles missing charger gracefully."""
        entry = MagicMock()
        entry.entry_id = "test_entry_id"
        entry.data = {"friendly_name": "Test"}
        entry.as_dict.return_value = {"entry_id": entry.entry_id, "data": entry.data}

        # Set runtime_data with no charger
        runtime_data = MagicMock()
        runtime_data.charger = None
        entry.runtime_data = runtime_data

        with patch(
            "custom_components.wattpilot.diagnostics.version", return_value="1.0.0"
        ):
            from custom_components.wattpilot.diagnostics import (
                async_get_config_entry_diagnostics,
            )

            result = await async_get_config_entry_diagnostics(mock_hass, entry)

            # Should still return a dict without crashing
            assert isinstance(result, dict)


class TestDiagnosticsRedaction:
    """Test redaction of sensitive data in diagnostics."""

    def test_redact_config_keys(self) -> None:
        """Test that REDACT_CONFIG contains expected keys."""
        from custom_components.wattpilot.diagnostics import REDACT_CONFIG

        assert "ip_address" in REDACT_CONFIG
        assert "password" in REDACT_CONFIG
        assert "serial" in REDACT_CONFIG

    def test_redact_allprops_keys(self) -> None:
        """Test that REDACT_ALLPROPS contains sensitive charger data keys."""
        from custom_components.wattpilot.diagnostics import REDACT_ALLPROPS

        # WiFi credentials and scan results should be redacted
        assert "wifis" in REDACT_ALLPROPS
        assert "scan" in REDACT_ALLPROPS
        # Security-related keys should be redacted
        assert "cak" in REDACT_ALLPROPS
        assert "ocppck" in REDACT_ALLPROPS
