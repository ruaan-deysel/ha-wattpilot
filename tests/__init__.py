"""Tests for the Fronius Wattpilot integration."""

from __future__ import annotations

from unittest.mock import MagicMock

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_FRIENDLY_NAME, CONF_IP_ADDRESS, CONF_PASSWORD
from homeassistant.core import HomeAssistant

from custom_components.wattpilot.const import CONF_CONNECTION, CONF_LOCAL, DOMAIN


async def setup_wattpilot_integration(
    hass: HomeAssistant, mock_charger: MagicMock | None = None
) -> ConfigEntry:
    """Set up the Wattpilot integration."""
    if mock_charger is None:
        # Create a basic mock charger
        mock_charger = MagicMock()
        mock_charger.allPropsInitialized = True
        mock_charger.connected = True
        mock_charger.name = "Test Wattpilot"
        mock_charger.serial = "12345678"
        mock_charger.firmware = "40.7"
        mock_charger.allProps = {}

    # Return a minimal ConfigEntry for testing
    entry = MagicMock(spec=ConfigEntry)
    entry.entry_id = "test_entry"
    entry.title = "Test Wattpilot"
    entry.domain = DOMAIN
    entry.data = {
        CONF_FRIENDLY_NAME: "Test Wattpilot",
        CONF_IP_ADDRESS: "192.168.1.100",
        CONF_PASSWORD: "test_password",
        CONF_CONNECTION: CONF_LOCAL,
    }
    entry.unique_id = "12345678"

    return entry
