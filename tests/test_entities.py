"""Tests for base entity classes."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from homeassistant.core import HomeAssistant


class TestChargerPlatformEntity:
    """Test ChargerPlatformEntity base class."""

    def test_entity_initialization(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_config_entry_data: dict,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test entity initializes correctly."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.const import DOMAIN
        from custom_components.wattpilot.entities import ChargerPlatformEntity
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
            debug_properties=False,
        )
        entry.runtime_data = runtime_data

        entity_cfg = {
            "id": "test_sensor_id",
            "name": "Test Sensor",
            "source": "property",
            "namespace_id": 0,
            "default_state": None,
        }

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp",
            return_value="test_value",
        ):
            entity = ChargerPlatformEntity(hass, entry, entity_cfg, mock_charger)

            assert entity._charger == mock_charger
            assert entity._identifier == "test"
            assert entity._source == "property"
            assert entity._namespace_id == 0

    def test_entity_device_info(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_config_entry_data: dict,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test entity device_info property."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.const import DOMAIN
        from custom_components.wattpilot.entities import ChargerPlatformEntity
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
            debug_properties=False,
        )
        entry.runtime_data = runtime_data

        entity_cfg = {
            "id": "test_sensor_id",
            "name": "Test Sensor",
            "source": "property",
            "namespace_id": 0,
            "default_state": None,
        }

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp",
            return_value="test_value",
        ):
            entity = ChargerPlatformEntity(hass, entry, entity_cfg, mock_charger)
            device_info = entity.device_info

            assert device_info["identifiers"] == {(DOMAIN, mock_charger.serial)}
            assert device_info["name"] == mock_charger.name
            assert device_info["manufacturer"] == mock_charger.manufacturer
            assert device_info["model"] == mock_charger.devicetype
            assert device_info["sw_version"] == mock_charger.firmware

    def test_entity_available_property(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_config_entry_data: dict,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test entity available property."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.const import DOMAIN
        from custom_components.wattpilot.entities import ChargerPlatformEntity
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
            debug_properties=False,
        )
        entry.runtime_data = runtime_data

        entity_cfg = {
            "id": "test_sensor_id",
            "name": "Test Sensor",
            "source": "property",
            "namespace_id": 0,
            "default_state": None,
        }

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp",
            return_value="test_value",
        ):
            entity = ChargerPlatformEntity(hass, entry, entity_cfg, mock_charger)

            # Mock coordinator as available
            mock_coordinator.available = True
            assert entity.available is True

            # Mock coordinator as unavailable
            mock_coordinator.available = False
            assert entity.available is False

    def test_entity_firmware_filtering(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_config_entry_data: dict,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test entity firmware version filtering."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.const import DOMAIN
        from custom_components.wattpilot.entities import ChargerPlatformEntity
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
            debug_properties=False,
        )
        entry.runtime_data = runtime_data

        # Entity requires firmware >= 41.0
        entity_cfg = {
            "id": "test_sensor_id",
            "name": "Test Sensor",
            "source": "property",
            "namespace_id": 0,
            "default_state": None,
            "firmware": ">=41.0",
        }

        # Mock charger has firmware 40.7 (below requirement)
        mock_charger.firmware = "40.7"

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp",
            return_value="test_value",
        ):
            entity = ChargerPlatformEntity(hass, entry, entity_cfg, mock_charger)
            # Entity should be marked as init_failed
            assert entity._init_failed is True

    def test_entity_connection_filtering(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_config_entry_data: dict,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test entity connection type filtering."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.const import DOMAIN
        from custom_components.wattpilot.entities import ChargerPlatformEntity
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
            debug_properties=False,
        )
        entry.runtime_data = runtime_data

        # Entity only supports local connection
        entity_cfg = {
            "id": "test_sensor_id",
            "name": "Test Sensor",
            "source": "property",
            "namespace_id": 0,
            "default_state": None,
            "connection": "local",
        }

        # Config entry has cloud connection
        entry.data = {**mock_config_entry_data, "connection": "cloud"}

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp",
            return_value="test_value",
        ):
            entity = ChargerPlatformEntity(hass, entry, entity_cfg, mock_charger)
            # Entity should be marked as init_failed
            assert entity._init_failed is True
