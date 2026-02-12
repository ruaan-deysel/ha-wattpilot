"""Tests for the select platform."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_UNKNOWN
from homeassistant.core import HomeAssistant

from custom_components.wattpilot.descriptions import WattpilotSelectEntityDescription


def get_select_desc_by_key(charger_key: str) -> WattpilotSelectEntityDescription | None:
    """Get a select description by its charger_key."""
    from custom_components.wattpilot.descriptions import SELECT_DESCRIPTIONS

    return next(
        (d for d in SELECT_DESCRIPTIONS if d.charger_key == charger_key),
        None,
    )


class TestSelectDescriptions:
    """Test select entity descriptions."""

    def test_all_descriptions_have_charger_key(self) -> None:
        """Test all select descriptions have charger_key."""
        from custom_components.wattpilot.descriptions import SELECT_DESCRIPTIONS

        for desc in SELECT_DESCRIPTIONS:
            assert desc.charger_key, f"Select {desc.key} missing charger_key"

    def test_select_ids_are_unique(self) -> None:
        """Test that all select IDs (uid or charger_key) are unique."""
        from custom_components.wattpilot.descriptions import SELECT_DESCRIPTIONS

        keys = [d.uid or d.charger_key for d in SELECT_DESCRIPTIONS]
        seen: set[str] = set()
        duplicates = []
        for key in keys:
            if key in seen:
                duplicates.append(key)
            seen.add(key)

        assert not duplicates, f"Duplicate select UIDs found: {duplicates}"

    def test_all_descriptions_have_options_source(self) -> None:
        """Test all select descriptions have either select_options or options_attribute."""
        from custom_components.wattpilot.descriptions import SELECT_DESCRIPTIONS

        for desc in SELECT_DESCRIPTIONS:
            assert (
                desc.select_options is not None or desc.options_attribute is not None
            ), f"Select {desc.key} missing both select_options and options_attribute"

    def test_charging_mode_select_exists(self) -> None:
        """Test charging_mode select is defined."""
        charging_mode = get_select_desc_by_key("lmo")

        assert charging_mode is not None
        assert charging_mode.key == "charging_mode"


class TestSelectEntity:
    """Test select entity functionality."""

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
            "lmo": 3,
            "cus": 0,
        }
        charger.set_property = AsyncMock()

        # Configure getattr to return load_modes dict or MagicMock for missing attributes
        def mock_getattr(obj, name, default=None):
            if name == "load_modes":
                return {1: "Default", 2: "Eco", 3: "Next Trip"}
            if name == "missing_attribute":
                return default
            return MagicMock()

        charger.configure_mock(load_modes={1: "Default", 2: "Eco", 3: "Next Trip"})
        return charger

    def test_select_descriptions_exist(self) -> None:
        """Test that select descriptions are defined."""
        from custom_components.wattpilot.descriptions import SELECT_DESCRIPTIONS

        assert len(SELECT_DESCRIPTIONS) > 0


class TestSelectPlatformSetup:
    """Test select platform setup."""

    @pytest.mark.asyncio
    async def test_async_setup_entry_success(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test successful select platform setup."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.const import DOMAIN
        from custom_components.wattpilot.select import async_setup_entry
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
            return_value=3,
        ):
            await async_setup_entry(hass, entry, async_add_entities)
            assert async_add_entities.called


class TestChargerSelect:
    """Test ChargerSelect entity class."""

    def _make_select_description(
        self, **overrides: Any
    ) -> WattpilotSelectEntityDescription:
        """Create a WattpilotSelectEntityDescription for testing."""
        from custom_components.wattpilot.descriptions import (
            SOURCE_PROPERTY,
            WattpilotSelectEntityDescription,
        )

        defaults = {
            "key": "test_select",
            "charger_key": "lmo",
            "name": "Test Select",
            "source": SOURCE_PROPERTY,
            "select_options": {1: "Option 1", 2: "Option 2", 3: "Option 3"},
            "options_attribute": None,
        }
        defaults.update(overrides)
        return WattpilotSelectEntityDescription(**defaults)

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

    def test_select_init_success_with_dict_options(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test select initialization succeeds with dict options."""
        from custom_components.wattpilot.select import ChargerSelect

        desc = self._make_select_description()
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp", return_value=3
        ):
            select = ChargerSelect(hass, entry, desc, mock_charger)
            assert select._init_failed is False
            assert select._opt_dict == {1: "Option 1", 2: "Option 2", 3: "Option 3"}
            assert select._attr_options == ["Option 1", "Option 2", "Option 3"]

    def test_select_init_success_with_attribute_options(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test select initialization succeeds with options from charger attribute."""
        from custom_components.wattpilot.select import ChargerSelect

        # Create a special mock charger that properly returns the load_modes dict
        charger_with_modes = MagicMock()
        charger_with_modes.serial = "12345678"
        charger_with_modes.name = "Test Wattpilot"
        charger_with_modes.firmware = "40.7"
        charger_with_modes.load_modes = {1: "Default", 2: "Eco", 3: "Next Trip"}

        desc = self._make_select_description(
            select_options=None,
            options_attribute="load_modes",
        )
        entry = self._make_entry(
            hass, charger_with_modes, mock_coordinator, mock_config_entry_data
        )

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp", return_value=3
        ):
            select = ChargerSelect(hass, entry, desc, charger_with_modes)
            assert select._init_failed is False
            assert select._opt_dict == {1: "Default", 2: "Eco", 3: "Next Trip"}
            assert select._attr_options == ["Default", "Eco", "Next Trip"]

    def test_select_init_handles_missing_attribute(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test select initialization handles missing charger attribute."""
        from custom_components.wattpilot.select import ChargerSelect

        # Create a charger without the missing_attribute
        mock_charger_no_attr = MagicMock(spec=["serial", "name", "firmware"])
        mock_charger_no_attr.serial = "12345678"
        mock_charger_no_attr.name = "Test Wattpilot"
        mock_charger_no_attr.firmware = "40.7"

        desc = self._make_select_description(
            select_options=None,
            options_attribute="missing_attribute",
        )
        entry = self._make_entry(
            hass, mock_charger_no_attr, mock_coordinator, mock_config_entry_data
        )

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp", return_value=3
        ):
            select = ChargerSelect(hass, entry, desc, mock_charger_no_attr)
            assert select._opt_dict == STATE_UNKNOWN

    @pytest.mark.asyncio
    async def test_validate_platform_state_converts_key_to_value(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test state validation converts API key to display value."""
        from custom_components.wattpilot.select import ChargerSelect

        desc = self._make_select_description()
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp", return_value=3
        ):
            select = ChargerSelect(hass, entry, desc, mock_charger)
            state = await select._async_update_validate_platform_state(2)
            assert state == "Option 2"

    @pytest.mark.asyncio
    async def test_validate_platform_state_keeps_existing_value(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test state validation keeps value if already in values list."""
        from custom_components.wattpilot.select import ChargerSelect

        desc = self._make_select_description()
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp", return_value=3
        ):
            select = ChargerSelect(hass, entry, desc, mock_charger)
            state = await select._async_update_validate_platform_state("Option 3")
            assert state == "Option 3"

    @pytest.mark.asyncio
    async def test_validate_platform_state_returns_unknown_for_invalid_key(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test state validation returns UNKNOWN for invalid key."""
        from custom_components.wattpilot.select import ChargerSelect

        desc = self._make_select_description()
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp", return_value=3
        ):
            select = ChargerSelect(hass, entry, desc, mock_charger)
            state = await select._async_update_validate_platform_state(999)
            assert state == STATE_UNKNOWN

    @pytest.mark.asyncio
    async def test_validate_platform_state_returns_none_for_non_dict_options(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test state validation returns None when options is not a dict."""
        from custom_components.wattpilot.select import ChargerSelect

        desc = self._make_select_description(
            select_options=None,
            options_attribute=None,
        )
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp", return_value=3
        ):
            select = ChargerSelect(hass, entry, desc, mock_charger)
            select._opt_dict = STATE_UNKNOWN
            state = await select._async_update_validate_platform_state(1)
            assert state is None

    @pytest.mark.asyncio
    async def test_validate_platform_state_handles_exception(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test state validation handles exceptions gracefully."""
        from custom_components.wattpilot.select import ChargerSelect

        desc = self._make_select_description()
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp", return_value=3
        ):
            select = ChargerSelect(hass, entry, desc, mock_charger)
            # Make _opt_dict.keys() raise an exception
            select._opt_dict = MagicMock()
            select._opt_dict.keys = MagicMock(side_effect=Exception("Test error"))
            state = await select._async_update_validate_platform_state(1)
            assert state is None

    @pytest.mark.asyncio
    async def test_async_select_option_success(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test select_option succeeds."""
        from custom_components.wattpilot.select import ChargerSelect

        desc = self._make_select_description(charger_key="lmo")
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with (
            patch(
                "custom_components.wattpilot.entities.GetChargerProp",
                return_value="lmo",
            ),
            patch(
                "custom_components.wattpilot.select.async_SetChargerProp",
                new_callable=AsyncMock,
            ) as mock_set,
        ):
            select = ChargerSelect(hass, entry, desc, mock_charger)
            await select.async_select_option("Option 2")

            mock_set.assert_called_once_with(mock_charger, "lmo", 2)

    @pytest.mark.asyncio
    async def test_async_select_option_handles_invalid_option(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test select_option handles invalid option gracefully."""
        from custom_components.wattpilot.select import ChargerSelect

        desc = self._make_select_description(charger_key="lmo")
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with (
            patch(
                "custom_components.wattpilot.entities.GetChargerProp",
                return_value="lmo",
            ),
            patch(
                "custom_components.wattpilot.select.async_SetChargerProp",
                new_callable=AsyncMock,
            ) as mock_set,
        ):
            select = ChargerSelect(hass, entry, desc, mock_charger)
            # This should handle the ValueError from index() gracefully
            await select.async_select_option("Invalid Option")

            # Should not have called set since option is invalid
            mock_set.assert_not_called()

    @pytest.mark.asyncio
    async def test_async_select_option_handles_non_dict_options(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test select_option handles non-dict options gracefully."""
        from custom_components.wattpilot.select import ChargerSelect

        desc = self._make_select_description(
            charger_key="lmo",
            select_options=None,
            options_attribute=None,
        )
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with (
            patch(
                "custom_components.wattpilot.entities.GetChargerProp",
                return_value="lmo",
            ),
            patch(
                "custom_components.wattpilot.select.async_SetChargerProp",
                new_callable=AsyncMock,
            ) as mock_set,
        ):
            select = ChargerSelect(hass, entry, desc, mock_charger)
            select._opt_dict = STATE_UNKNOWN
            await select.async_select_option("Option 1")

            # Should not have called set since options not available
            mock_set.assert_not_called()

    @pytest.mark.asyncio
    async def test_async_select_option_handles_error(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test select_option handles errors gracefully."""
        from custom_components.wattpilot.select import ChargerSelect

        desc = self._make_select_description(charger_key="lmo")
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with (
            patch(
                "custom_components.wattpilot.entities.GetChargerProp",
                return_value="lmo",
            ),
            patch(
                "custom_components.wattpilot.select.async_SetChargerProp",
                new_callable=AsyncMock,
                side_effect=Exception("Test error"),
            ),
        ):
            select = ChargerSelect(hass, entry, desc, mock_charger)
            # Should not raise exception
            await select.async_select_option("Option 2")

    @pytest.mark.asyncio
    async def test_async_select_option_reverse_lookup(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test select_option correctly performs reverse lookup from value to key."""
        from custom_components.wattpilot.select import ChargerSelect

        desc = self._make_select_description(
            charger_key="lmo",
            select_options={10: "First", 20: "Second", 30: "Third"},
        )
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with (
            patch(
                "custom_components.wattpilot.entities.GetChargerProp",
                return_value="lmo",
            ),
            patch(
                "custom_components.wattpilot.select.async_SetChargerProp",
                new_callable=AsyncMock,
            ) as mock_set,
        ):
            select = ChargerSelect(hass, entry, desc, mock_charger)
            await select.async_select_option("Second")

            # Should send the key (20) not the value ("Second")
            mock_set.assert_called_once_with(mock_charger, "lmo", 20)
