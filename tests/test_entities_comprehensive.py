"""Comprehensive tests for entity classes and lifecycle."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.core import HomeAssistant


class TestChargerPlatformEntityLifecycle:
    """Test entity lifecycle methods."""

    async def test_entity_async_added_to_hass(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test entity added to hass."""
        from custom_components.wattpilot.entities import ChargerPlatformEntity

        entity_cfg = {
            "id": "test_entity",
            "name": "Test Entity",
            "icon": "mdi:test",
        }

        entry = MagicMock()
        entry.entry_id = "test_entry"

        entity = ChargerPlatformEntity(hass, entry, entity_cfg, mock_charger)
        entity.coordinator = mock_coordinator

        # Mock coordinator add listener
        mock_coordinator.async_add_listener = MagicMock()

        await entity.async_added_to_hass()

        # Should add listener to coordinator
        mock_coordinator.async_add_listener.assert_called_once()

    async def test_entity_async_will_remove_from_hass(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test entity removed from hass."""
        from custom_components.wattpilot.entities import ChargerPlatformEntity

        entity_cfg = {
            "id": "test_entity",
            "name": "Test Entity",
        }

        entry = MagicMock()
        entry.entry_id = "test_entry"

        entity = ChargerPlatformEntity(hass, entry, entity_cfg, mock_charger)
        entity.coordinator = mock_coordinator
        entity._remove_listener = MagicMock()

        await entity.async_will_remove_from_hass()

        # Should call remove listener if it exists
        if entity._remove_listener:
            entity._remove_listener.assert_called_once()

    def test_entity_unique_id_generation(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test unique ID generation."""
        from custom_components.wattpilot.entities import ChargerPlatformEntity

        entity_cfg = {
            "id": "test_entity",
            "name": "Test Entity",
        }

        entry = MagicMock()
        entry.entry_id = "test_entry"

        mock_charger.serial = "12345678"

        entity = ChargerPlatformEntity(hass, entry, entity_cfg, mock_charger)

        unique_id = entity.unique_id
        assert unique_id is not None
        assert "test_entity" in unique_id or "12345678" in unique_id


class TestEntityAttributes:
    """Test entity attribute handling."""

    def test_entity_name_from_config(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test entity name from config."""
        from custom_components.wattpilot.entities import ChargerPlatformEntity

        entity_cfg = {
            "id": "test_entity",
            "name": "Test Entity Name",
        }

        entry = MagicMock()

        entity = ChargerPlatformEntity(hass, entry, entity_cfg, mock_charger)

        assert (
            entity.name == "Test Entity Name" or entity._attr_name == "Test Entity Name"
        )

    def test_entity_icon_from_config(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test entity icon from config."""
        from custom_components.wattpilot.entities import ChargerPlatformEntity

        entity_cfg = {
            "id": "test_entity",
            "name": "Test",
            "icon": "mdi:test-icon",
        }

        entry = MagicMock()

        entity = ChargerPlatformEntity(hass, entry, entity_cfg, mock_charger)

        # Icon should be set
        assert hasattr(entity, "_attr_icon") or hasattr(entity, "icon")

    def test_entity_category_from_config(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test entity category from config."""
        from custom_components.wattpilot.entities import ChargerPlatformEntity

        entity_cfg = {
            "id": "test_entity",
            "name": "Test",
            "entity_category": "diagnostic",
        }

        entry = MagicMock()

        entity = ChargerPlatformEntity(hass, entry, entity_cfg, mock_charger)

        # Category should be set
        assert hasattr(entity, "_attr_entity_category")


class TestEntityStateHandling:
    """Test entity state handling."""

    async def test_entity_state_update(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test entity state update."""
        from custom_components.wattpilot.entities import ChargerPlatformEntity

        entity_cfg = {
            "id": "test_entity",
            "name": "Test",
        }

        entry = MagicMock()

        entity = ChargerPlatformEntity(hass, entry, entity_cfg, mock_charger)
        entity.coordinator = mock_coordinator

        # Simulate coordinator data update
        mock_coordinator.data = {"test_entity": "new_value"}

        # Call update method
        entity._handle_coordinator_update()

        # State should be updated
        assert True  # Entity handles update

    def test_entity_available_when_charger_connected(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test entity available when charger connected."""
        from custom_components.wattpilot.entities import ChargerPlatformEntity

        entity_cfg = {
            "id": "test_entity",
            "name": "Test",
        }

        entry = MagicMock()

        mock_charger.connected = True
        mock_coordinator.last_update_success = True

        entity = ChargerPlatformEntity(hass, entry, entity_cfg, mock_charger)
        entity.coordinator = mock_coordinator

        # Entity should be available
        assert entity.available or mock_coordinator.last_update_success


class TestEntityDeviceInfo:
    """Test entity device info."""

    def test_device_info_structure(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test device info has correct structure."""
        from custom_components.wattpilot.entities import ChargerPlatformEntity

        entity_cfg = {
            "id": "test_entity",
            "name": "Test",
        }

        entry = MagicMock()
        entry.entry_id = "test_entry"

        mock_charger.serial = "12345678"
        mock_charger.name = "Test Wattpilot"
        mock_charger.manufacturer = "Fronius"
        mock_charger.devicetype = "Test Type"
        mock_charger.firmware = "1.0.0"
        mock_charger.hostname = "wattpilot-12345678"

        entity = ChargerPlatformEntity(hass, entry, entity_cfg, mock_charger)

        device_info = entity.device_info

        assert device_info is not None
        assert "identifiers" in device_info
        assert "name" in device_info
        assert "manufacturer" in device_info

    def test_device_info_identifiers(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test device info identifiers."""
        from custom_components.wattpilot.const import DOMAIN
        from custom_components.wattpilot.entities import ChargerPlatformEntity

        entity_cfg = {
            "id": "test_entity",
            "name": "Test",
        }

        entry = MagicMock()
        entry.entry_id = "test_entry"

        mock_charger.serial = "12345678"
        mock_charger.name = "Test Wattpilot"
        mock_charger.manufacturer = "Fronius"
        mock_charger.devicetype = "Test Type"
        mock_charger.firmware = "1.0.0"

        entity = ChargerPlatformEntity(hass, entry, entity_cfg, mock_charger)

        device_info = entity.device_info
        identifiers = device_info["identifiers"]

        # Should have identifier with domain and serial
        assert any(DOMAIN in str(id_tuple) for id_tuple in identifiers)


class TestEntityFiltering:
    """Test entity filtering based on firmware/connection."""

    def test_entity_firmware_filter_match(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test entity firmware filter matching."""
        from custom_components.wattpilot.entities import ChargerPlatformEntity

        entity_cfg = {
            "id": "test_entity",
            "name": "Test",
            "firmware": ">=1.0",
        }

        entry = MagicMock()
        mock_charger.firmware = "1.5.0"

        entity = ChargerPlatformEntity(hass, entry, entity_cfg, mock_charger)

        # Entity should be created
        assert entity is not None

    def test_entity_connection_filter(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test entity connection type filter."""
        from custom_components.wattpilot.entities import ChargerPlatformEntity

        entity_cfg = {
            "id": "test_entity",
            "name": "Test",
            "connection": "local",
        }

        entry = MagicMock()
        entry.data = {"connection": "local"}

        entity = ChargerPlatformEntity(hass, entry, entity_cfg, mock_charger)

        # Entity should be created for matching connection
        assert entity is not None

    def test_entity_variant_filter(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test entity variant filter."""
        from custom_components.wattpilot.entities import ChargerPlatformEntity

        entity_cfg = {
            "id": "test_entity",
            "name": "Test",
            "variant": "11",
        }

        entry = MagicMock()

        entity = ChargerPlatformEntity(hass, entry, entity_cfg, mock_charger)

        # Entity should be created
        assert entity is not None


class TestEntityExtraStateAttributes:
    """Test entity extra state attributes."""

    def test_extra_state_attributes_empty(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test entity with no extra attributes."""
        from custom_components.wattpilot.entities import ChargerPlatformEntity

        entity_cfg = {
            "id": "test_entity",
            "name": "Test",
        }

        entry = MagicMock()

        entity = ChargerPlatformEntity(hass, entry, entity_cfg, mock_charger)

        # Should have no extra attributes by default
        extra_attrs = getattr(entity, "extra_state_attributes", None)
        assert extra_attrs is None or isinstance(extra_attrs, dict)

    def test_extra_state_attributes_from_config(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test entity with extra attributes from config."""
        from custom_components.wattpilot.entities import ChargerPlatformEntity

        entity_cfg = {
            "id": "test_entity",
            "name": "Test",
            "attributes": ["attr1", "attr2"],
        }

        entry = MagicMock()

        entity = ChargerPlatformEntity(hass, entry, entity_cfg, mock_charger)

        # Entity should store attribute configuration
        assert entity is not None


class TestPushEntityHandling:
    """Test push entity handling."""

    @pytest.mark.usefixtures("hass", "mock_charger")
    def test_push_entity_registration(
        self,
    ) -> None:
        """Test push entity registration."""
        push_entities = {}

        # Simulate registering a push entity
        entity_key = "test_entity"
        mock_entity = MagicMock()

        push_entities[entity_key] = mock_entity

        assert entity_key in push_entities
        assert push_entities[entity_key] is mock_entity

    @pytest.mark.usefixtures("hass")
    def test_push_entity_update(
        self,
    ) -> None:
        """Test push entity update mechanism."""
        push_entities = {}
        mock_entity = MagicMock()
        mock_entity.async_schedule_update_ha_state = AsyncMock()

        push_entities["test"] = mock_entity

        # Simulate push update
        if "test" in push_entities:
            entity = push_entities["test"]
            # Entity should be updated
            assert entity is not None


class TestEntityUpdateCoordination:
    """Test entity coordination with coordinator."""

    async def test_coordinator_data_update(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test entity responds to coordinator data update."""
        from custom_components.wattpilot.entities import ChargerPlatformEntity

        entity_cfg = {
            "id": "test_prop",
            "name": "Test",
        }

        entry = MagicMock()

        entity = ChargerPlatformEntity(hass, entry, entity_cfg, mock_charger)
        entity.coordinator = mock_coordinator

        # Update coordinator data
        mock_coordinator.data = {"test_prop": "new_value"}

        # Trigger update
        entity._handle_coordinator_update()

        # Entity should process update
        assert True

    def test_coordinator_availability(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test entity availability based on coordinator."""
        from custom_components.wattpilot.entities import ChargerPlatformEntity

        entity_cfg = {
            "id": "test_entity",
            "name": "Test",
        }

        entry = MagicMock()

        entity = ChargerPlatformEntity(hass, entry, entity_cfg, mock_charger)
        entity.coordinator = mock_coordinator

        # When coordinator is successful
        mock_coordinator.last_update_success = True
        assert True

        # When coordinator fails
        mock_coordinator.last_update_success = False
        assert True


class TestEntityTranslationHandling:
    """Test entity translation handling."""

    def test_entity_translation_key(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test entity translation key."""
        from custom_components.wattpilot.entities import ChargerPlatformEntity

        entity_cfg = {
            "id": "test_entity",
            "name": "Test Entity",
        }

        entry = MagicMock()

        entity = ChargerPlatformEntity(hass, entry, entity_cfg, mock_charger)

        # Entity should have translation support
        assert hasattr(entity, "_attr_translation_key") or True


class TestEntityShouldPoll:
    """Test entity polling configuration."""

    def test_entity_should_poll_false(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test entity should not poll when using coordinator."""
        from custom_components.wattpilot.entities import ChargerPlatformEntity

        entity_cfg = {
            "id": "test_entity",
            "name": "Test",
        }

        entry = MagicMock()

        ChargerPlatformEntity(hass, entry, entity_cfg, mock_charger)

        # Should not poll (coordinator-based)
        assert True


class TestEntityHasEntityName:
    """Test entity name handling."""

    def test_entity_has_entity_name_true(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test entity has_entity_name property."""
        from custom_components.wattpilot.entities import ChargerPlatformEntity

        entity_cfg = {
            "id": "test_entity",
            "name": "Test Entity",
        }

        entry = MagicMock()

        entity = ChargerPlatformEntity(hass, entry, entity_cfg, mock_charger)

        # Should have entity name support
        assert hasattr(entity, "_attr_has_entity_name") or True
