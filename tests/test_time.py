"""Tests for the time platform."""

from __future__ import annotations

import datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from custom_components.wattpilot.descriptions import WattpilotTimeEntityDescription


def get_time_desc_by_key(charger_key: str) -> WattpilotTimeEntityDescription | None:
    """Get a time description by its charger_key."""
    from custom_components.wattpilot.descriptions import TIME_DESCRIPTIONS

    return next(
        (d for d in TIME_DESCRIPTIONS if d.charger_key == charger_key),
        None,
    )


class TestTimeDescriptions:
    """Test time entity descriptions."""

    def test_all_descriptions_have_charger_key(self) -> None:
        """Test all time descriptions have charger_key."""
        from custom_components.wattpilot.descriptions import TIME_DESCRIPTIONS

        for desc in TIME_DESCRIPTIONS:
            assert desc.charger_key, f"Time {desc.key} missing charger_key"

    def test_time_ids_are_unique(self) -> None:
        """Test that all time IDs (uid or charger_key) are unique."""
        from custom_components.wattpilot.descriptions import TIME_DESCRIPTIONS

        keys = [d.uid or d.charger_key for d in TIME_DESCRIPTIONS]
        seen: set[str] = set()
        duplicates = []
        for key in keys:
            if key in seen:
                duplicates.append(key)
            seen.add(key)

        assert not duplicates, f"Duplicate time UIDs found: {duplicates}"

    def test_next_trip_time_description_exists(self) -> None:
        """Test next_trip_time time description is defined."""
        desc = get_time_desc_by_key("ftt")

        assert desc is not None
        assert desc.key == "next_trip_time"

    def test_time_descriptions_exist(self) -> None:
        """Test that time descriptions are defined."""
        from custom_components.wattpilot.descriptions import TIME_DESCRIPTIONS

        assert len(TIME_DESCRIPTIONS) > 0


class TestTimePlatformSetup:
    """Test time platform setup."""

    @pytest.mark.asyncio
    async def test_async_setup_entry_success(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test successful time platform setup."""
        from custom_components.wattpilot.const import DOMAIN
        from custom_components.wattpilot.time import async_setup_entry
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
            return_value=25200,
        ):
            await async_setup_entry(hass, entry, async_add_entities)
            assert async_add_entities.called


class TestChargerTime:
    """Test ChargerTime entity class."""

    def _make_time_description(
        self, **overrides: Any
    ) -> WattpilotTimeEntityDescription:
        """Create a WattpilotTimeEntityDescription for testing."""
        from custom_components.wattpilot.descriptions import (
            SOURCE_PROPERTY,
            WattpilotTimeEntityDescription,
        )

        defaults = {
            "key": "next_trip_time",
            "charger_key": "ftt",
            "name": "Next Trip Time",
            "source": SOURCE_PROPERTY,
        }
        defaults.update(overrides)
        return WattpilotTimeEntityDescription(**defaults)

    def _make_entry(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> ConfigEntry:
        """Create a ConfigEntry with runtime data."""
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

    def test_time_init_success(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test time entity initialization succeeds."""
        from custom_components.wattpilot.time import ChargerTime

        desc = self._make_time_description()
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp", return_value=25200
        ):
            time_entity = ChargerTime(hass, entry, desc, mock_charger)
            assert time_entity._init_failed is False

    def test_time_native_value_returns_none_when_unset(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test native_value returns None when not set."""
        from custom_components.wattpilot.time import ChargerTime

        desc = self._make_time_description()
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp", return_value=25200
        ):
            time_entity = ChargerTime(hass, entry, desc, mock_charger)
            time_entity._attr_native_value = None
            assert time_entity.native_value is None

    def test_time_native_value_returns_time_when_set(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test native_value returns the set time."""
        from custom_components.wattpilot.time import ChargerTime

        desc = self._make_time_description()
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp", return_value=25200
        ):
            time_entity = ChargerTime(hass, entry, desc, mock_charger)
            expected = datetime.time(7, 0, 0)
            time_entity._attr_native_value = expected
            assert time_entity.native_value == expected

    @pytest.mark.asyncio
    async def test_validate_platform_state_converts_seconds_to_time(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test state validation converts seconds since midnight to datetime.time."""
        from custom_components.wattpilot.time import ChargerTime

        desc = self._make_time_description()
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp", return_value=25200
        ):
            time_entity = ChargerTime(hass, entry, desc, mock_charger)
            # 25200 seconds = 7 hours = 07:00:00
            state = await time_entity._async_update_validate_platform_state(25200)
            assert state == datetime.time(7, 0, 0)

    @pytest.mark.asyncio
    async def test_validate_platform_state_handles_various_times(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test state validation converts various seconds values correctly."""
        from custom_components.wattpilot.time import ChargerTime

        desc = self._make_time_description()
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp", return_value=25200
        ):
            time_entity = ChargerTime(hass, entry, desc, mock_charger)

            # 0 seconds = midnight
            assert await time_entity._async_update_validate_platform_state(
                0
            ) == datetime.time(0, 0, 0)

            # 3661 seconds = 1h 1m 1s
            assert await time_entity._async_update_validate_platform_state(
                3661
            ) == datetime.time(1, 1, 1)

            # 86399 seconds = 23:59:59
            assert await time_entity._async_update_validate_platform_state(
                86399
            ) == datetime.time(23, 59, 59)

    @pytest.mark.asyncio
    async def test_validate_platform_state_handles_none(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test state validation handles None input."""
        from custom_components.wattpilot.time import ChargerTime

        desc = self._make_time_description()
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp", return_value=25200
        ):
            time_entity = ChargerTime(hass, entry, desc, mock_charger)
            state = await time_entity._async_update_validate_platform_state(None)
            assert state is None

    @pytest.mark.asyncio
    async def test_validate_platform_state_handles_invalid(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test state validation handles invalid input."""
        from custom_components.wattpilot.time import ChargerTime

        desc = self._make_time_description()
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp", return_value=25200
        ):
            time_entity = ChargerTime(hass, entry, desc, mock_charger)
            state = await time_entity._async_update_validate_platform_state("invalid")
            assert state is None

    @pytest.mark.asyncio
    async def test_validate_platform_state_wraps_overflow(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test state validation wraps values >= 86400 (full day modulo)."""
        from custom_components.wattpilot.time import ChargerTime

        desc = self._make_time_description()
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp", return_value=25200
        ):
            time_entity = ChargerTime(hass, entry, desc, mock_charger)
            # 86400 + 3600 = 90000 -> 3600 = 01:00:00
            state = await time_entity._async_update_validate_platform_state(90000)
            assert state == datetime.time(1, 0, 0)

    @pytest.mark.asyncio
    async def test_async_set_value_calls_set_next_trip(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test async_set_value calls charger.set_next_trip."""
        from custom_components.wattpilot.time import ChargerTime

        mock_charger.set_next_trip = AsyncMock()
        desc = self._make_time_description()
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp", return_value=25200
        ):
            time_entity = ChargerTime(hass, entry, desc, mock_charger)
            new_time = datetime.time(8, 30, 0)
            await time_entity.async_set_value(new_time)
            mock_charger.set_next_trip.assert_called_once_with(new_time)

    @pytest.mark.asyncio
    async def test_async_set_value_handles_exception(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test async_set_value handles exceptions gracefully."""
        from custom_components.wattpilot.time import ChargerTime

        mock_charger.set_next_trip = AsyncMock(side_effect=Exception("Connection lost"))
        desc = self._make_time_description()
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp", return_value=25200
        ):
            time_entity = ChargerTime(hass, entry, desc, mock_charger)
            new_time = datetime.time(8, 30, 0)
            # Should not raise
            await time_entity.async_set_value(new_time)
