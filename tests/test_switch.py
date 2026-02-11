"""Tests for the switch platform."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_OFF, STATE_ON, STATE_UNKNOWN
from homeassistant.core import HomeAssistant

from custom_components.wattpilot.descriptions import WattpilotSwitchEntityDescription


def get_switch_desc_by_key(charger_key: str) -> WattpilotSwitchEntityDescription | None:
    """Get a switch description by its charger_key."""
    from custom_components.wattpilot.descriptions import SWITCH_DESCRIPTIONS

    return next(
        (d for d in SWITCH_DESCRIPTIONS if d.charger_key == charger_key),
        None,
    )


class TestSwitchDescriptions:
    """Test switch entity descriptions."""

    def test_all_descriptions_have_charger_key(self) -> None:
        """Test all switch descriptions have charger_key."""
        from custom_components.wattpilot.descriptions import SWITCH_DESCRIPTIONS

        for desc in SWITCH_DESCRIPTIONS:
            assert desc.charger_key, f"Switch {desc.key} missing charger_key"

    def test_switch_ids_are_unique(self) -> None:
        """Test that all switch IDs (uid or charger_key) are unique."""
        from custom_components.wattpilot.descriptions import SWITCH_DESCRIPTIONS

        keys = [d.uid or d.charger_key for d in SWITCH_DESCRIPTIONS]
        seen: set[str] = set()
        duplicates = []
        for key in keys:
            if key in seen:
                duplicates.append(key)
            seen.add(key)

        assert not duplicates, f"Duplicate switch UIDs found: {duplicates}"

    def test_lock_level_selection_switch_exists(self) -> None:
        """Test lock_level_selection switch is defined."""
        lock_level = get_switch_desc_by_key("bac")

        assert lock_level is not None
        assert lock_level.key == "lock_level_selection"

    def test_invert_field_is_boolean(self) -> None:
        """Test that invert field is a boolean in all descriptions."""
        from custom_components.wattpilot.descriptions import SWITCH_DESCRIPTIONS

        for desc in SWITCH_DESCRIPTIONS:
            assert isinstance(desc.invert, bool), (
                f"Switch {desc.key} invert field is not boolean"
            )


class TestSwitchEntity:
    """Test switch entity functionality."""

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
            "alw": True,
            "acs": False,
            "sdp": True,
        }
        charger.set_property = AsyncMock()
        return charger

    def test_switch_descriptions_exist(self) -> None:
        """Test that switch descriptions are defined."""
        from custom_components.wattpilot.descriptions import SWITCH_DESCRIPTIONS

        assert len(SWITCH_DESCRIPTIONS) > 0


class TestSwitchPlatformSetup:
    """Test switch platform setup."""

    @pytest.mark.asyncio
    async def test_async_setup_entry_success(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test successful switch platform setup."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.const import DOMAIN
        from custom_components.wattpilot.switch import async_setup_entry
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
            return_value=True,
        ):
            await async_setup_entry(hass, entry, async_add_entities)
            assert async_add_entities.called


class TestChargerSwitch:
    """Test ChargerSwitch entity class."""

    def _make_switch_description(
        self, **overrides: Any
    ) -> WattpilotSwitchEntityDescription:
        """Create a WattpilotSwitchEntityDescription for testing."""
        from custom_components.wattpilot.descriptions import (
            SOURCE_PROPERTY,
            WattpilotSwitchEntityDescription,
        )

        defaults = {
            "key": "test_switch",
            "charger_key": "alw",
            "name": "Test Switch",
            "source": SOURCE_PROPERTY,
            "invert": False,
        }
        defaults.update(overrides)
        return WattpilotSwitchEntityDescription(**defaults)

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

    def test_switch_init_success(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test switch initialization succeeds."""
        from custom_components.wattpilot.switch import ChargerSwitch

        desc = self._make_switch_description()
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp", return_value=True
        ):
            switch = ChargerSwitch(hass, entry, desc, mock_charger)
            assert switch._init_failed is False
            assert switch._internal_state == STATE_UNKNOWN

    def test_switch_is_on_returns_none_for_unknown(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test is_on returns None for unknown state."""
        from custom_components.wattpilot.switch import ChargerSwitch

        desc = self._make_switch_description()
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp", return_value=True
        ):
            switch = ChargerSwitch(hass, entry, desc, mock_charger)
            assert switch._internal_state == STATE_UNKNOWN
            assert switch.is_on is None

    def test_switch_is_on_returns_true_for_on_state(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test is_on returns True for ON state."""
        from custom_components.wattpilot.switch import ChargerSwitch

        desc = self._make_switch_description()
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp", return_value=True
        ):
            switch = ChargerSwitch(hass, entry, desc, mock_charger)
            switch._internal_state = STATE_ON
            assert switch.is_on is True

    def test_switch_is_on_returns_false_for_off_state(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test is_on returns False for OFF state."""
        from custom_components.wattpilot.switch import ChargerSwitch

        desc = self._make_switch_description()
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp", return_value=True
        ):
            switch = ChargerSwitch(hass, entry, desc, mock_charger)
            switch._internal_state = STATE_OFF
            assert switch.is_on is False

    @pytest.mark.asyncio
    async def test_validate_platform_state_converts_true_string_to_on(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test state validation converts 'true' string to STATE_ON."""
        from custom_components.wattpilot.switch import ChargerSwitch

        desc = self._make_switch_description()
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp", return_value=True
        ):
            switch = ChargerSwitch(hass, entry, desc, mock_charger)
            state = await switch._async_update_validate_platform_state("true")
            assert state == STATE_ON

    @pytest.mark.asyncio
    async def test_validate_platform_state_converts_false_string_to_off(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test state validation converts 'false' string to STATE_OFF."""
        from custom_components.wattpilot.switch import ChargerSwitch

        desc = self._make_switch_description()
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp", return_value=True
        ):
            switch = ChargerSwitch(hass, entry, desc, mock_charger)
            state = await switch._async_update_validate_platform_state("false")
            assert state == STATE_OFF

    @pytest.mark.asyncio
    async def test_validate_platform_state_inverts_on_when_invert_true(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test state validation inverts STATE_ON to STATE_OFF when invert is True."""
        from custom_components.wattpilot.switch import ChargerSwitch

        desc = self._make_switch_description(invert=True)
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp", return_value=True
        ):
            switch = ChargerSwitch(hass, entry, desc, mock_charger)
            state = await switch._async_update_validate_platform_state(STATE_ON)
            assert state == STATE_OFF

    @pytest.mark.asyncio
    async def test_validate_platform_state_inverts_off_when_invert_true(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test state validation inverts STATE_OFF to STATE_ON when invert is True."""
        from custom_components.wattpilot.switch import ChargerSwitch

        desc = self._make_switch_description(invert=True)
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp", return_value=True
        ):
            switch = ChargerSwitch(hass, entry, desc, mock_charger)
            state = await switch._async_update_validate_platform_state(STATE_OFF)
            assert state == STATE_ON

    @pytest.mark.asyncio
    async def test_validate_platform_state_handles_invalid_state(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test state validation returns STATE_UNKNOWN for invalid states."""
        from custom_components.wattpilot.switch import ChargerSwitch

        desc = self._make_switch_description()
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp", return_value=True
        ):
            switch = ChargerSwitch(hass, entry, desc, mock_charger)
            state = await switch._async_update_validate_platform_state("invalid")
            assert state == STATE_UNKNOWN

    @pytest.mark.asyncio
    async def test_validate_platform_state_handles_exception(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test state validation handles exceptions gracefully."""
        from custom_components.wattpilot.switch import ChargerSwitch

        desc = self._make_switch_description()
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp", return_value=True
        ):
            switch = ChargerSwitch(hass, entry, desc, mock_charger)
            # Pass an object that will raise an exception when str() is called
            mock_obj = MagicMock()
            mock_obj.__str__ = MagicMock(side_effect=Exception("Test error"))
            state = await switch._async_update_validate_platform_state(mock_obj)
            assert state is None

    @pytest.mark.asyncio
    async def test_async_turn_on_success(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test switch turn_on succeeds."""
        from custom_components.wattpilot.switch import ChargerSwitch

        desc = self._make_switch_description(charger_key="alw", invert=False)
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with (
            patch(
                "custom_components.wattpilot.entities.GetChargerProp",
                return_value="alw",
            ),
            patch(
                "custom_components.wattpilot.switch.async_SetChargerProp",
                new_callable=AsyncMock,
            ) as mock_set,
        ):
            switch = ChargerSwitch(hass, entry, desc, mock_charger)
            await switch.async_turn_on()

            mock_set.assert_called_once_with(mock_charger, "alw", True)

    @pytest.mark.asyncio
    async def test_async_turn_on_with_invert(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test switch turn_on with invert=True sends False."""
        from custom_components.wattpilot.switch import ChargerSwitch

        desc = self._make_switch_description(charger_key="alw", invert=True)
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with (
            patch(
                "custom_components.wattpilot.entities.GetChargerProp",
                return_value="alw",
            ),
            patch(
                "custom_components.wattpilot.switch.async_SetChargerProp",
                new_callable=AsyncMock,
            ) as mock_set,
        ):
            switch = ChargerSwitch(hass, entry, desc, mock_charger)
            await switch.async_turn_on()

            mock_set.assert_called_once_with(mock_charger, "alw", False)

    @pytest.mark.asyncio
    async def test_async_turn_on_handles_error(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test switch turn_on handles errors gracefully."""
        from custom_components.wattpilot.switch import ChargerSwitch

        desc = self._make_switch_description(charger_key="alw")
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with (
            patch(
                "custom_components.wattpilot.entities.GetChargerProp",
                return_value="alw",
            ),
            patch(
                "custom_components.wattpilot.switch.async_SetChargerProp",
                new_callable=AsyncMock,
                side_effect=Exception("Test error"),
            ),
        ):
            switch = ChargerSwitch(hass, entry, desc, mock_charger)
            # Should not raise exception
            await switch.async_turn_on()

    @pytest.mark.asyncio
    async def test_async_turn_off_success(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test switch turn_off succeeds."""
        from custom_components.wattpilot.switch import ChargerSwitch

        desc = self._make_switch_description(charger_key="alw", invert=False)
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with (
            patch(
                "custom_components.wattpilot.entities.GetChargerProp",
                return_value="alw",
            ),
            patch(
                "custom_components.wattpilot.switch.async_SetChargerProp",
                new_callable=AsyncMock,
            ) as mock_set,
        ):
            switch = ChargerSwitch(hass, entry, desc, mock_charger)
            await switch.async_turn_off()

            mock_set.assert_called_once_with(mock_charger, "alw", False)

    @pytest.mark.asyncio
    async def test_async_turn_off_with_invert(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test switch turn_off with invert=True sends True."""
        from custom_components.wattpilot.switch import ChargerSwitch

        desc = self._make_switch_description(charger_key="alw", invert=True)
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with (
            patch(
                "custom_components.wattpilot.entities.GetChargerProp",
                return_value="alw",
            ),
            patch(
                "custom_components.wattpilot.switch.async_SetChargerProp",
                new_callable=AsyncMock,
            ) as mock_set,
        ):
            switch = ChargerSwitch(hass, entry, desc, mock_charger)
            await switch.async_turn_off()

            mock_set.assert_called_once_with(mock_charger, "alw", True)

    @pytest.mark.asyncio
    async def test_async_turn_off_handles_error(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test switch turn_off handles errors gracefully."""
        from custom_components.wattpilot.switch import ChargerSwitch

        desc = self._make_switch_description(charger_key="alw")
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with (
            patch(
                "custom_components.wattpilot.entities.GetChargerProp",
                return_value="alw",
            ),
            patch(
                "custom_components.wattpilot.switch.async_SetChargerProp",
                new_callable=AsyncMock,
                side_effect=Exception("Test error"),
            ),
        ):
            switch = ChargerSwitch(hass, entry, desc, mock_charger)
            # Should not raise exception
            await switch.async_turn_off()
