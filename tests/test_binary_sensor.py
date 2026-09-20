"""Tests for the binary_sensor platform."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from custom_components.wattpilot.binary_sensor import (
    ChargerBinarySensor,
    async_setup_entry,
)
from custom_components.wattpilot.const import DOMAIN
from custom_components.wattpilot.descriptions import (
    BINARY_SENSOR_DESCRIPTIONS,
    WattpilotBinarySensorEntityDescription,
)
from custom_components.wattpilot.types import WattpilotRuntimeData


class TestBinarySensorDescriptions:
    """Test binary sensor entity descriptions."""

    def test_descriptions_exist(self) -> None:
        """Test that binary sensor descriptions are defined."""
        assert len(BINARY_SENSOR_DESCRIPTIONS) == 2

    def test_all_descriptions_have_charger_key(self) -> None:
        """Test all binary sensor descriptions have charger_key."""
        for desc in BINARY_SENSOR_DESCRIPTIONS:
            assert desc.charger_key, f"Binary sensor {desc.key} missing charger_key"

    def test_plug_connected_description(self) -> None:
        """Test plug_connected description properties."""
        desc = next(
            (d for d in BINARY_SENSOR_DESCRIPTIONS if d.key == "plug_connected"),
            None,
        )
        assert desc is not None
        assert desc.charger_key == "car"
        assert desc.device_class == BinarySensorDeviceClass.PLUG
        assert desc.on_values == {2, 3, 4}

    def test_charging_description(self) -> None:
        """Test charging description properties."""
        desc = next(
            (d for d in BINARY_SENSOR_DESCRIPTIONS if d.key == "charging"),
            None,
        )
        assert desc is not None
        assert desc.charger_key == "car"
        assert desc.device_class == BinarySensorDeviceClass.BATTERY_CHARGING
        assert desc.on_values == {2}


class TestBinarySensorPlatformSetup:
    """Test binary sensor platform setup."""

    @pytest.fixture
    def mock_charger(self) -> MagicMock:
        """Create a mock charger instance."""
        charger = MagicMock()
        charger.serial = "12345678"
        charger.name = "Test Wattpilot"
        charger.firmware = "40.7"
        charger.connected = True
        charger.properties_initialized = True
        charger.all_properties = {"car": 2}
        return charger

    @pytest.mark.asyncio
    async def test_async_setup_entry_success(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test successful binary sensor platform setup."""
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

        push_entities: dict[str, Any] = {}
        runtime_data = WattpilotRuntimeData(
            charger=mock_charger,
            coordinator=mock_coordinator,
            push_entities=push_entities,
            params=mock_config_entry_data,
        )
        entry.runtime_data = runtime_data

        async_add_entities = MagicMock()

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp",
            return_value=2,
        ):
            await async_setup_entry(hass, entry, async_add_entities)
            assert async_add_entities.called
            added_entities = async_add_entities.call_args[0][0]
            assert len(added_entities) == 2
            # Both plug_connected and charging use "car" so push_entities["car"] should be a list
            assert "car" in push_entities
            assert isinstance(push_entities["car"], list)
            assert len(push_entities["car"]) == 2

    @pytest.mark.asyncio
    async def test_async_setup_entry_with_existing_list(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test binary sensor setup when push_entities already has a list."""
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

        existing_entity = MagicMock()
        push_entities: dict[str, Any] = {"car": [existing_entity]}
        runtime_data = WattpilotRuntimeData(
            charger=mock_charger,
            coordinator=mock_coordinator,
            push_entities=push_entities,
            params=mock_config_entry_data,
        )
        entry.runtime_data = runtime_data

        async_add_entities = MagicMock()

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp",
            return_value=2,
        ):
            await async_setup_entry(hass, entry, async_add_entities)
            assert len(push_entities["car"]) == 3

    @pytest.mark.asyncio
    async def test_async_setup_entry_init_failed(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test binary sensor setup when entity init fails."""
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

        push_entities: dict[str, Any] = {}
        runtime_data = WattpilotRuntimeData(
            charger=mock_charger,
            coordinator=mock_coordinator,
            push_entities=push_entities,
            params=mock_config_entry_data,
        )
        entry.runtime_data = runtime_data

        async_add_entities = MagicMock()

        with patch(
            "custom_components.wattpilot.binary_sensor.ChargerBinarySensor.__init__",
            lambda self, *args, **kwargs: setattr(self, "_init_failed", True),
        ):
            await async_setup_entry(hass, entry, async_add_entities)
            assert not async_add_entities.called


class TestChargerBinarySensor:
    """Test ChargerBinarySensor entity functionality."""

    @pytest.fixture
    def mock_charger(self) -> MagicMock:
        """Create a mock charger instance."""
        charger = MagicMock()
        charger.serial = "12345678"
        charger.name = "Test Wattpilot"
        charger.firmware = "40.7"
        charger.connected = True
        charger.properties_initialized = True
        charger.all_properties = {"car": 2}
        return charger

    def test_init_platform_specific(
        self,
        hass: HomeAssistant,
        mock_config_entry: ConfigEntry,
        mock_charger: MagicMock,
    ) -> None:
        """Test platform specific initialization."""
        desc = WattpilotBinarySensorEntityDescription(
            key="plug_connected",
            charger_key="car",
            uid="plug_connected",
            device_class=BinarySensorDeviceClass.PLUG,
            on_values={2, 3, 4},
        )
        entity = ChargerBinarySensor(hass, mock_config_entry, desc, mock_charger)
        assert entity._attr_is_on is None
        assert entity._state_attr == "_attr_is_on"

    @pytest.mark.asyncio
    async def test_validate_platform_state_none(
        self,
        hass: HomeAssistant,
        mock_config_entry: ConfigEntry,
        mock_charger: MagicMock,
    ) -> None:
        """Test validation when state is None."""
        desc = WattpilotBinarySensorEntityDescription(
            key="test",
            charger_key="car",
            on_values={2, 3},
        )
        entity = ChargerBinarySensor(hass, mock_config_entry, desc, mock_charger)
        assert await entity._async_update_validate_platform_state(None) is None

    @pytest.mark.asyncio
    async def test_validate_platform_state_on_values_int(
        self,
        hass: HomeAssistant,
        mock_config_entry: ConfigEntry,
        mock_charger: MagicMock,
    ) -> None:
        """Test validation with integer on_values."""
        desc = WattpilotBinarySensorEntityDescription(
            key="test",
            charger_key="car",
            on_values={2, 3, 4},
        )
        entity = ChargerBinarySensor(hass, mock_config_entry, desc, mock_charger)
        assert await entity._async_update_validate_platform_state(2) is True
        assert await entity._async_update_validate_platform_state("3") is True
        assert await entity._async_update_validate_platform_state(1) is False
        assert await entity._async_update_validate_platform_state("1") is False

    @pytest.mark.asyncio
    async def test_validate_platform_state_on_values_string_fallback(
        self,
        hass: HomeAssistant,
        mock_config_entry: ConfigEntry,
        mock_charger: MagicMock,
    ) -> None:
        """Test validation with non-integer on_values."""
        desc = WattpilotBinarySensorEntityDescription(
            key="test",
            charger_key="status",
            on_values={"active", "charging"},
        )
        entity = ChargerBinarySensor(hass, mock_config_entry, desc, mock_charger)
        assert await entity._async_update_validate_platform_state("active") is True
        assert await entity._async_update_validate_platform_state("idle") is False

    @pytest.mark.asyncio
    async def test_validate_platform_state_bool_and_string_values(
        self,
        hass: HomeAssistant,
        mock_config_entry: ConfigEntry,
        mock_charger: MagicMock,
    ) -> None:
        """Test validation without on_values using standard bool/strings."""
        desc = WattpilotBinarySensorEntityDescription(
            key="test",
            charger_key="status",
        )
        entity = ChargerBinarySensor(hass, mock_config_entry, desc, mock_charger)
        assert await entity._async_update_validate_platform_state(True) is True
        assert await entity._async_update_validate_platform_state(False) is False
        assert await entity._async_update_validate_platform_state("true") is True
        assert await entity._async_update_validate_platform_state("1") is True
        assert await entity._async_update_validate_platform_state("ON") is True
        assert await entity._async_update_validate_platform_state("false") is False
        assert await entity._async_update_validate_platform_state("0") is False
        assert await entity._async_update_validate_platform_state("off") is False
        assert await entity._async_update_validate_platform_state("other") is None

    @pytest.mark.asyncio
    async def test_validate_platform_state_exception_handling(
        self,
        hass: HomeAssistant,
        mock_config_entry: ConfigEntry,
        mock_charger: MagicMock,
    ) -> None:
        """Test exception handling during validation."""
        desc = WattpilotBinarySensorEntityDescription(
            key="test",
            charger_key="car",
        )
        entity = ChargerBinarySensor(hass, mock_config_entry, desc, mock_charger)

        class FailingState:
            def __str__(self) -> str:
                raise RuntimeError("Boom")

        assert (
            await entity._async_update_validate_platform_state(FailingState()) is None
        )
