"""Tests for the button platform."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from custom_components.wattpilot.descriptions import WattpilotButtonEntityDescription


def get_button_desc_by_key(charger_key: str) -> WattpilotButtonEntityDescription | None:
    """Get a button description by its charger_key."""
    from custom_components.wattpilot.descriptions import BUTTON_DESCRIPTIONS

    return next(
        (d for d in BUTTON_DESCRIPTIONS if d.charger_key == charger_key),
        None,
    )


class TestButtonDescriptions:
    """Test button entity descriptions."""

    def test_all_descriptions_have_charger_key(self) -> None:
        """Test all button descriptions have charger_key."""
        from custom_components.wattpilot.descriptions import BUTTON_DESCRIPTIONS

        for desc in BUTTON_DESCRIPTIONS:
            assert desc.charger_key, f"Button {desc.key} missing charger_key"

    def test_all_descriptions_have_set_value(self) -> None:
        """Test all button descriptions have set_value."""
        from custom_components.wattpilot.descriptions import BUTTON_DESCRIPTIONS

        for desc in BUTTON_DESCRIPTIONS:
            assert desc.set_value is not None, f"Button {desc.key} missing set_value"

    def test_button_ids_are_unique(self) -> None:
        """Test that all button IDs (uid or charger_key) are unique."""
        from custom_components.wattpilot.descriptions import BUTTON_DESCRIPTIONS

        keys = [d.uid or d.charger_key for d in BUTTON_DESCRIPTIONS]
        seen: set[str] = set()
        duplicates = []
        for key in keys:
            if key in seen:
                duplicates.append(key)
            seen.add(key)

        assert not duplicates, f"Duplicate button UIDs found: {duplicates}"

    def test_start_charging_button_exists(self) -> None:
        """Test start_charging button is defined."""
        start_charging = get_button_desc_by_key("frc")

        assert start_charging is not None
        assert start_charging.set_value == 0

    def test_stop_charging_button_exists(self) -> None:
        """Test stop_charging button is defined."""
        from custom_components.wattpilot.descriptions import BUTTON_DESCRIPTIONS

        stop_charging = next(
            (
                d
                for d in BUTTON_DESCRIPTIONS
                if d.charger_key == "frc" and d.set_value == 1
            ),
            None,
        )

        assert stop_charging is not None
        assert stop_charging.set_value == 1


class TestButtonEntity:
    """Test button entity functionality."""

    @pytest.fixture
    def mock_charger(self) -> MagicMock:
        """Create a mock charger instance."""
        charger = MagicMock()
        charger.serial = "12345678"
        charger.name = "Test Wattpilot"
        charger.firmware = "40.7"
        charger.connected = True
        charger.properties_initialized = True
        charger.all_properties = {
            "frc": 0,
            "rst": 0,
            "trx": 0,
        }
        charger.set_property = AsyncMock()
        return charger

    def test_button_descriptions_exist(self) -> None:
        """Test that button descriptions are defined."""
        from custom_components.wattpilot.descriptions import BUTTON_DESCRIPTIONS

        assert len(BUTTON_DESCRIPTIONS) > 0


class TestButtonPlatformSetup:
    """Test button platform setup."""

    @pytest.mark.asyncio
    async def test_async_setup_entry_success(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test successful button platform setup."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.button import async_setup_entry
        from custom_components.wattpilot.const import DOMAIN
        from custom_components.wattpilot.types import WattpilotRuntimeData

        entry = ConfigEntry(
            version=1,
            minor_version=0,
            domain=DOMAIN,
            title="Test Wattpilot",
            data=mock_config_entry_data,
            source="user",
            unique_id="12345678",
            discovery_keys={},
            options={},
            subentries_data={},
        )

        runtime_data = WattpilotRuntimeData(
            charger=mock_charger,
            coordinator=mock_coordinator,
            push_entities={},
            params=mock_config_entry_data,
        )
        entry.runtime_data = runtime_data

        async_add_entities = MagicMock()

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp",
            return_value=100.0,
        ):
            await async_setup_entry(hass, entry, async_add_entities)
            assert async_add_entities.called


class TestChargerButton:
    """Test ChargerButton entity class."""

    def _make_button_description(
        self, **overrides: Any
    ) -> WattpilotButtonEntityDescription:
        """Create a WattpilotButtonEntityDescription for testing."""
        from custom_components.wattpilot.descriptions import (
            SOURCE_NONE,
            WattpilotButtonEntityDescription,
        )

        defaults = {
            "key": "test_button",
            "charger_key": "frc",
            "name": "Test Button",
            "source": SOURCE_NONE,
            "set_value": 0,
        }
        defaults.update(overrides)
        return WattpilotButtonEntityDescription(**defaults)

    def _make_entry(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> ConfigEntry:
        """Create a ConfigEntry with runtime data."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.const import DOMAIN
        from custom_components.wattpilot.types import WattpilotRuntimeData

        entry = ConfigEntry(
            version=1,
            minor_version=0,
            domain=DOMAIN,
            title="Test Wattpilot",
            data=mock_config_entry_data,
            source="user",
            unique_id="12345678",
            discovery_keys={},
            options={},
            subentries_data={},
        )

        runtime_data = WattpilotRuntimeData(
            charger=mock_charger,
            coordinator=mock_coordinator,
            push_entities={},
            params=mock_config_entry_data,
        )
        entry.runtime_data = runtime_data
        return entry

    def test_button_init_fails_without_set_value(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test button initialization fails when set_value is missing."""
        from custom_components.wattpilot.button import ChargerButton

        desc = self._make_button_description(set_value=None)
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp", return_value="frc"
        ):
            button = ChargerButton(hass, entry, desc, mock_charger)
            assert button._init_failed is True

    def test_button_init_success_with_set_value(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test button initialization succeeds with set_value."""
        from custom_components.wattpilot.button import ChargerButton

        desc = self._make_button_description(set_value=0)
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp", return_value="frc"
        ):
            button = ChargerButton(hass, entry, desc, mock_charger)
            assert button._init_failed is False

    @pytest.mark.asyncio
    async def test_async_press_success(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test button press succeeds."""
        from custom_components.wattpilot.button import ChargerButton

        desc = self._make_button_description(charger_key="frc", set_value=0)
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with (
            patch(
                "custom_components.wattpilot.entities.GetChargerProp",
                return_value="frc",
            ),
            patch(
                "custom_components.wattpilot.button.async_SetChargerProp",
                new_callable=AsyncMock,
            ) as mock_set,
        ):
            button = ChargerButton(hass, entry, desc, mock_charger)
            await button.async_press()

            mock_set.assert_called_once_with(mock_charger, "frc", 0)

    @pytest.mark.asyncio
    async def test_async_press_handles_error(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test button press handles errors gracefully."""
        from custom_components.wattpilot.button import ChargerButton

        desc = self._make_button_description(charger_key="frc", set_value=0)
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with (
            patch(
                "custom_components.wattpilot.entities.GetChargerProp",
                return_value="frc",
            ),
            patch(
                "custom_components.wattpilot.button.async_SetChargerProp",
                new_callable=AsyncMock,
                side_effect=Exception("Test error"),
            ),
        ):
            button = ChargerButton(hass, entry, desc, mock_charger)
            # Should not raise exception
            await button.async_press()

    @pytest.mark.asyncio
    async def test_async_local_poll_does_nothing(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test button local_poll does nothing (no state for buttons)."""
        from custom_components.wattpilot.button import ChargerButton

        desc = self._make_button_description()
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp", return_value="frc"
        ):
            button = ChargerButton(hass, entry, desc, mock_charger)
            # Should complete without errors
            await button.async_local_poll()
