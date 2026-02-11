"""Tests for the number platform."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from custom_components.wattpilot.descriptions import WattpilotNumberEntityDescription


def get_number_desc_by_key(charger_key: str) -> WattpilotNumberEntityDescription | None:
    """Get a number description by its charger_key."""
    from custom_components.wattpilot.descriptions import NUMBER_DESCRIPTIONS

    return next(
        (d for d in NUMBER_DESCRIPTIONS if d.charger_key == charger_key),
        None,
    )


class TestNumberDescriptions:
    """Test number entity descriptions."""

    def test_all_descriptions_have_charger_key(self) -> None:
        """Test all number descriptions have charger_key."""
        from custom_components.wattpilot.descriptions import NUMBER_DESCRIPTIONS

        for desc in NUMBER_DESCRIPTIONS:
            assert desc.charger_key, f"Number {desc.key} missing charger_key"

    def test_number_ids_are_unique(self) -> None:
        """Test that all number IDs (uid or charger_key) are unique."""
        from custom_components.wattpilot.descriptions import NUMBER_DESCRIPTIONS

        keys = [d.uid or d.charger_key for d in NUMBER_DESCRIPTIONS]
        seen: set[str] = set()
        duplicates = []
        for key in keys:
            if key in seen:
                duplicates.append(key)
            seen.add(key)

        assert not duplicates, f"Duplicate number UIDs found: {duplicates}"

    def test_max_charging_current_number_exists(self) -> None:
        """Test max_charging_current_11kw number is defined."""
        max_current = get_number_desc_by_key("amp")

        assert max_current is not None
        assert max_current.key == "max_charging_current_11kw"

    def test_all_descriptions_have_valid_min_max(self) -> None:
        """Test all number descriptions have valid min/max values."""
        from custom_components.wattpilot.descriptions import NUMBER_DESCRIPTIONS

        for desc in NUMBER_DESCRIPTIONS:
            if desc.native_min_value is not None and desc.native_max_value is not None:
                assert desc.native_min_value <= desc.native_max_value, (
                    f"Number {desc.key} has min ({desc.native_min_value}) > max ({desc.native_max_value})"
                )


class TestNumberEntity:
    """Test number entity functionality."""

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
            "amp": 16,
            "fsp": 50,
            "fte": 10.5,
        }
        charger.set_property = AsyncMock()
        charger.set_next_trip_energy = AsyncMock()
        return charger

    def test_number_descriptions_exist(self) -> None:
        """Test that number descriptions are defined."""
        from custom_components.wattpilot.descriptions import NUMBER_DESCRIPTIONS

        assert len(NUMBER_DESCRIPTIONS) > 0


class TestNumberPlatformSetup:
    """Test number platform setup."""

    @pytest.mark.asyncio
    async def test_async_setup_entry_success(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test successful number platform setup."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.const import DOMAIN
        from custom_components.wattpilot.number import async_setup_entry
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
            return_value=16.0,
        ):
            await async_setup_entry(hass, entry, async_add_entities)
            assert async_add_entities.called


class TestChargerNumber:
    """Test ChargerNumber entity class."""

    def _make_number_description(
        self, **overrides: Any
    ) -> WattpilotNumberEntityDescription:
        """Create a WattpilotNumberEntityDescription for testing."""
        from custom_components.wattpilot.descriptions import (
            SOURCE_PROPERTY,
            WattpilotNumberEntityDescription,
        )

        defaults = {
            "key": "test_number",
            "charger_key": "amp",
            "name": "Test Number",
            "source": SOURCE_PROPERTY,
            "native_min_value": 0,
            "native_max_value": 100,
            "native_step": 1,
        }
        defaults.update(overrides)
        return WattpilotNumberEntityDescription(**defaults)

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

    def test_number_init_success(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test number initialization succeeds."""
        from custom_components.wattpilot.number import ChargerNumber

        desc = self._make_number_description()
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp", return_value=16.0
        ):
            number = ChargerNumber(hass, entry, desc, mock_charger)
            assert number._init_failed is False
            assert number._attr_native_min_value == 0
            assert number._attr_native_max_value == 100
            assert number._attr_native_step == 1

    def test_number_native_value_handles_float(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test native_value property handles float values."""
        from custom_components.wattpilot.number import ChargerNumber

        desc = self._make_number_description()
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp", return_value=16.0
        ):
            number = ChargerNumber(hass, entry, desc, mock_charger)
            number._attr_native_value = 16.5
            assert number.native_value == 16.5

    def test_number_native_value_handles_list(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test native_value property extracts first value from list."""
        from custom_components.wattpilot.number import ChargerNumber

        desc = self._make_number_description()
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp", return_value=16.0
        ):
            number = ChargerNumber(hass, entry, desc, mock_charger)
            number._attr_native_value = [42.0, 10.0, 5.0]
            assert number.native_value == 42.0

    def test_number_native_value_handles_tuple(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test native_value property extracts first value from tuple."""
        from custom_components.wattpilot.number import ChargerNumber

        desc = self._make_number_description()
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp", return_value=16.0
        ):
            number = ChargerNumber(hass, entry, desc, mock_charger)
            number._attr_native_value = (25.5, 30.0)
            assert number.native_value == 25.5

    def test_number_native_value_handles_empty_list(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test native_value property handles empty list."""
        from custom_components.wattpilot.number import ChargerNumber

        desc = self._make_number_description()
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp", return_value=16.0
        ):
            number = ChargerNumber(hass, entry, desc, mock_charger)
            number._attr_native_value = []
            assert number.native_value is None

    def test_number_native_value_handles_none(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test native_value property handles None."""
        from custom_components.wattpilot.number import ChargerNumber

        desc = self._make_number_description()
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp", return_value=16.0
        ):
            number = ChargerNumber(hass, entry, desc, mock_charger)
            number._attr_native_value = None
            assert number.native_value is None

    def test_number_native_value_handles_invalid_type(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test native_value property handles invalid type conversions."""
        from custom_components.wattpilot.number import ChargerNumber

        desc = self._make_number_description()
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp", return_value=16.0
        ):
            number = ChargerNumber(hass, entry, desc, mock_charger)
            number._attr_native_value = "invalid"
            assert number.native_value is None

    @pytest.mark.asyncio
    async def test_validate_platform_state_converts_to_float(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test state validation converts value to float."""
        from custom_components.wattpilot.number import ChargerNumber

        desc = self._make_number_description()
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp", return_value=16.0
        ):
            number = ChargerNumber(hass, entry, desc, mock_charger)
            state = await number._async_update_validate_platform_state(42)
            assert state == 42.0
            assert number._attr_native_value == 42.0

    @pytest.mark.asyncio
    async def test_validate_platform_state_handles_list(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test state validation extracts first value from list."""
        from custom_components.wattpilot.number import ChargerNumber

        desc = self._make_number_description()
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp", return_value=16.0
        ):
            number = ChargerNumber(hass, entry, desc, mock_charger)
            state = await number._async_update_validate_platform_state([25.5, 10.0])
            assert state == 25.5
            assert number._attr_native_value == 25.5

    @pytest.mark.asyncio
    async def test_validate_platform_state_handles_empty_list(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test state validation handles empty list."""
        from custom_components.wattpilot.number import ChargerNumber

        desc = self._make_number_description()
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp", return_value=16.0
        ):
            number = ChargerNumber(hass, entry, desc, mock_charger)
            state = await number._async_update_validate_platform_state([])
            assert state is None

    @pytest.mark.asyncio
    async def test_validate_platform_state_handles_none(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test state validation handles None."""
        from custom_components.wattpilot.number import ChargerNumber

        desc = self._make_number_description()
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp", return_value=16.0
        ):
            number = ChargerNumber(hass, entry, desc, mock_charger)
            state = await number._async_update_validate_platform_state(None)
            assert state is None

    @pytest.mark.asyncio
    async def test_validate_platform_state_handles_invalid_value(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test state validation handles invalid values that can't be converted to float."""
        from custom_components.wattpilot.number import ChargerNumber

        desc = self._make_number_description()
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp", return_value=16.0
        ):
            number = ChargerNumber(hass, entry, desc, mock_charger)
            state = await number._async_update_validate_platform_state("invalid")
            assert state is None

    @pytest.mark.asyncio
    async def test_async_set_native_value_success(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test set_native_value succeeds."""
        from custom_components.wattpilot.number import ChargerNumber

        desc = self._make_number_description(charger_key="amp")
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with (
            patch(
                "custom_components.wattpilot.entities.GetChargerProp",
                return_value="amp",
            ),
            patch(
                "custom_components.wattpilot.number.async_SetChargerProp",
                new_callable=AsyncMock,
            ) as mock_set,
        ):
            number = ChargerNumber(hass, entry, desc, mock_charger)
            await number.async_set_native_value(20.0)

            mock_set.assert_called_once_with(mock_charger, "amp", 20.0)

    @pytest.mark.asyncio
    async def test_async_set_native_value_fte_uses_set_next_trip_energy(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test set_native_value for 'fte' identifier calls set_next_trip_energy."""
        from custom_components.wattpilot.number import ChargerNumber

        desc = self._make_number_description(charger_key="fte")
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp", return_value="fte"
        ):
            number = ChargerNumber(hass, entry, desc, mock_charger)
            await number.async_set_native_value(15.5)

            mock_charger.set_next_trip_energy.assert_called_once_with(15.5)

    @pytest.mark.asyncio
    async def test_async_set_native_value_handles_error(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test set_native_value handles errors gracefully."""
        from custom_components.wattpilot.number import ChargerNumber

        desc = self._make_number_description(charger_key="amp")
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with (
            patch(
                "custom_components.wattpilot.entities.GetChargerProp",
                return_value="amp",
            ),
            patch(
                "custom_components.wattpilot.number.async_SetChargerProp",
                new_callable=AsyncMock,
                side_effect=Exception("Test error"),
            ),
        ):
            number = ChargerNumber(hass, entry, desc, mock_charger)
            # Should not raise exception
            await number.async_set_native_value(20.0)

    def test_number_init_sets_min_max_step(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test number init properly sets min/max/step values."""
        from custom_components.wattpilot.number import ChargerNumber

        desc = self._make_number_description(
            native_min_value=5.0,
            native_max_value=50.0,
            native_step=0.5,
        )
        entry = self._make_entry(
            hass, mock_charger, mock_coordinator, mock_config_entry_data
        )

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp", return_value=16.0
        ):
            number = ChargerNumber(hass, entry, desc, mock_charger)
            assert number._attr_native_min_value == 5.0
            assert number._attr_native_max_value == 50.0
            assert number._attr_native_step == 0.5
