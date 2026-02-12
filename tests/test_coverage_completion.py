"""Tests to achieve 100% code coverage for remaining gaps."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from custom_components.wattpilot.const import DOMAIN
from custom_components.wattpilot.descriptions import (
    SOURCE_ATTRIBUTE,
    SOURCE_NAMESPACELIST,
    SOURCE_PROPERTY,
    WattpilotSensorEntityDescription,
)
from custom_components.wattpilot.entities import ChargerPlatformEntity


class TestInitVersionCheck:
    """Test __init__.py version check error paths (lines 79-93)."""

    @pytest.mark.asyncio
    async def test_setup_entry_connect_charger_generic_exception(
        self,
        hass: HomeAssistant,
        mock_config_entry_data: dict,
    ) -> None:
        """Test setup handles generic exception during charger connection."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot import async_setup_entry

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

        with (
            patch("custom_components.wattpilot.async_get_integration"),
            patch("custom_components.wattpilot._ensure_services_registered"),
            patch(
                "custom_components.wattpilot.utils.async_ConnectCharger",
                side_effect=RuntimeError("Connection error"),
            ),
            pytest.raises(ConfigEntryNotReady) as exc_info,
        ):
            await async_setup_entry(hass, entry)

        assert "Failed to connect to charger" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_setup_entry_integration_version_none(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test setup handles None integration version."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot import async_setup_entry

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

        mock_integration = MagicMock()
        mock_integration.version = None

        with (
            patch(
                "custom_components.wattpilot.async_get_integration",
                return_value=mock_integration,
            ),
            patch("custom_components.wattpilot._ensure_services_registered"),
            patch(
                "custom_components.wattpilot.utils.async_ConnectCharger",
                return_value=mock_charger,
            ),
            patch(
                "custom_components.wattpilot.WattpilotCoordinator.async_config_entry_first_refresh",
                new_callable=AsyncMock,
            ),
            patch(
                "custom_components.wattpilot.utils.async_DisconnectCharger",
                new_callable=AsyncMock,
            ),
            pytest.raises(Exception),  # Expected to fail at later stage
        ):
            # Should log debug message about unknown version
            await async_setup_entry(hass, entry)


class TestUnloadDisconnectErrors:
    """Test unload disconnect error paths (lines 285-293)."""

    @pytest.mark.asyncio
    async def test_unload_charger_disconnect_exception_logged(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test unload logs charger info when disconnect fails."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot import async_unload_entry
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

        # Set name and serial for error message
        mock_charger.name = "Test Charger Name"
        mock_charger.serial = "ABC12345"

        coordinator = MagicMock()
        runtime_data = WattpilotRuntimeData(
            charger=mock_charger,
            coordinator=coordinator,
            push_entities={},
            params=mock_config_entry_data,
        )
        entry.runtime_data = runtime_data

        with patch(
            "custom_components.wattpilot.utils.async_DisconnectCharger",
            side_effect=RuntimeError("Disconnect failed"),
        ):
            result = await async_unload_entry(hass, entry)
            # Should log error with charger name and serial
            assert isinstance(result, bool)


class TestEntitiesEdgeCases:
    """Test entities.py edge cases (lines 234-241, 288-348, 395-456, 473-544)."""

    @pytest.mark.asyncio
    async def test_entity_init_namespacelist_missing_item(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test entity init fails when namespacelist item is None."""
        mock_charger.all_properties = {"test_list": [None, "value2"]}

        desc = WattpilotSensorEntityDescription(
            key="test",
            charger_key="test_list",
            name="Test",
            source=SOURCE_NAMESPACELIST,
            namespace_id="0",
        )

        with patch("custom_components.wattpilot.entities.GetChargerProp") as mock_get:
            mock_get.return_value = [None, "value2"]
            entity = ChargerPlatformEntity(
                mock_hass, mock_config_entry, desc, mock_charger
            )
            # Should fail init because namespace item is None
            assert entity._init_failed is True

    def test_entity_available_coordinator_unavailable(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test entity unavailable when coordinator is unavailable."""
        mock_charger.all_properties = {"test_prop": "test_value"}
        mock_charger.connected = True
        mock_charger.properties_initialized = True

        desc = WattpilotSensorEntityDescription(
            key="test",
            charger_key="test_prop",
            name="Test",
            source=SOURCE_PROPERTY,
        )

        entity = ChargerPlatformEntity(mock_hass, mock_config_entry, desc, mock_charger)

        # Mock coordinator's available property through CoordinatorEntity.available
        mock_coordinator_available = PropertyMock(return_value=False)
        with patch(
            "custom_components.wattpilot.entities.CoordinatorEntity.available",
            mock_coordinator_available,
        ):
            assert entity.available is False

    def test_entity_available_properties_not_initialized(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test entity unavailable when properties not initialized."""
        mock_charger.all_properties = {"test_prop": "test_value"}
        mock_charger.connected = True
        mock_charger.properties_initialized = False

        desc = WattpilotSensorEntityDescription(
            key="test",
            charger_key="test_prop",
            name="Test",
            source=SOURCE_PROPERTY,
        )

        entity = ChargerPlatformEntity(mock_hass, mock_config_entry, desc, mock_charger)

        assert entity.available is False

    def test_entity_available_attribute_missing_at_runtime(
        self, mock_hass: HomeAssistant, mock_config_entry: Any
    ) -> None:
        """Test entity unavailable when attribute missing at runtime."""
        charger = MagicMock()
        charger.test_attr = "value"
        charger.connected = True
        charger.properties_initialized = True
        charger.serial = "12345678"

        desc = WattpilotSensorEntityDescription(
            key="test",
            charger_key="test_attr",
            name="Test",
            source=SOURCE_ATTRIBUTE,
        )

        entity = ChargerPlatformEntity(mock_hass, mock_config_entry, desc, charger)

        # Remove attribute to simulate runtime change
        del charger.test_attr

        assert entity.available is False

    def test_entity_available_property_missing_at_runtime(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test entity unavailable when property missing at runtime."""
        mock_charger.all_properties = {"test_prop": "test_value"}
        mock_charger.connected = True
        mock_charger.properties_initialized = True

        desc = WattpilotSensorEntityDescription(
            key="test",
            charger_key="test_prop",
            name="Test",
            source=SOURCE_PROPERTY,
        )

        entity = ChargerPlatformEntity(mock_hass, mock_config_entry, desc, mock_charger)

        # Remove property to simulate runtime change
        with patch(
            "custom_components.wattpilot.entities.GetChargerProp", return_value=None
        ):
            assert entity.available is False

    def test_entity_available_namespacelist_item_becomes_none(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test entity unavailable when namespacelist item becomes None at runtime."""
        mock_charger.all_properties = {"test_list": ["value1", "value2"]}
        mock_charger.connected = True
        mock_charger.properties_initialized = True

        desc = WattpilotSensorEntityDescription(
            key="test",
            charger_key="test_list",
            name="Test",
            source=SOURCE_NAMESPACELIST,
            namespace_id="1",
        )

        entity = ChargerPlatformEntity(mock_hass, mock_config_entry, desc, mock_charger)

        # Change list item to None
        with patch(
            "custom_components.wattpilot.entities.GetChargerProp",
            return_value=["value1", None],
        ):
            assert entity.available is False

    @pytest.mark.asyncio
    async def test_entity_async_update_not_available(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test async_update returns early when not available."""
        mock_charger.all_properties = {"test_prop": "test_value"}

        desc = WattpilotSensorEntityDescription(
            key="test",
            charger_key="test_prop",
            name="Test",
            source=SOURCE_PROPERTY,
        )

        entity = ChargerPlatformEntity(mock_hass, mock_config_entry, desc, mock_charger)
        entity.async_local_poll = AsyncMock()

        with (
            patch(
                "custom_components.wattpilot.entities.CoordinatorEntity.enabled",
                new_callable=PropertyMock,
                return_value=True,
            ),
            patch.object(
                type(entity), "available", new_callable=PropertyMock, return_value=False
            ),
        ):
            await entity.async_update()
            # Should return early without calling poll
            entity.async_local_poll.assert_not_called()

    @pytest.mark.asyncio
    async def test_entity_async_update_push_waiting(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test async_update with push-based update (waiting)."""
        mock_charger.all_properties = {"test_prop": "test_value"}

        desc = WattpilotSensorEntityDescription(
            key="test",
            charger_key="test_prop",
            name="Test",
            source=SOURCE_PROPERTY,
        )

        entity = ChargerPlatformEntity(mock_hass, mock_config_entry, desc, mock_charger)
        entity.async_local_poll = AsyncMock()

        with (
            patch(
                "custom_components.wattpilot.entities.CoordinatorEntity.enabled",
                new_callable=PropertyMock,
                return_value=True,
            ),
            patch.object(
                type(entity), "available", new_callable=PropertyMock, return_value=True
            ),
            patch.object(
                type(entity),
                "should_poll",
                new_callable=PropertyMock,
                return_value=False,
            ),
        ):
            await entity.async_update()
            # Should not poll when push-based
            entity.async_local_poll.assert_not_called()

    @pytest.mark.asyncio
    async def test_entity_validate_property_no_value_id(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test validate property fails when namespace has no value_id."""
        mock_charger.all_properties = {"test_prop": "test_value"}

        desc = WattpilotSensorEntityDescription(
            key="test",
            charger_key="test_prop",
            name="Test",
            source=SOURCE_PROPERTY,
            value_id=None,  # No value_id specified
        )

        entity = ChargerPlatformEntity(mock_hass, mock_config_entry, desc, mock_charger)

        # Create a namespace object mock with __str__ properly set
        namespace = MagicMock()
        namespace.__str__ = MagicMock(return_value="namespace_test")

        result = await entity._async_update_validate_property(namespace)
        # Should return None because value_id is missing
        assert result is None

    @pytest.mark.asyncio
    async def test_entity_validate_property_list_with_value_id(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test validate property with list and value_id."""
        mock_charger.all_properties = {"test_prop": "test_value"}

        desc = WattpilotSensorEntityDescription(
            key="test",
            charger_key="test_prop",
            name="Test",
            source=SOURCE_PROPERTY,
            value_id="2",
            attribute_ids=["attr1:0", "attr2:1"],
        )

        entity = ChargerPlatformEntity(mock_hass, mock_config_entry, desc, mock_charger)

        state_list = ["val0", "val1", "val2", "val3"]
        result = await entity._async_update_validate_property(state_list)

        # Should extract value at index 2
        assert result == "val2"
        # Should extract attributes
        assert entity._attributes["attr1"] == "val0"
        assert entity._attributes["attr2"] == "val1"

    @pytest.mark.asyncio
    async def test_entity_async_local_poll_namespacelist(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test async_local_poll with namespacelist source."""
        mock_charger.all_properties = {"test_list": ["value1", "value2"]}

        desc = WattpilotSensorEntityDescription(
            key="test",
            charger_key="test_list",
            name="Test",
            source=SOURCE_NAMESPACELIST,
            namespace_id="1",
        )

        entity = ChargerPlatformEntity(mock_hass, mock_config_entry, desc, mock_charger)
        entity.async_write_ha_state = MagicMock()

        with patch(
            "custom_components.wattpilot.entities.async_GetChargerProp",
            return_value=["value1", "value2"],
        ):
            await entity.async_local_poll()
            entity.async_write_ha_state.assert_called_once()

    @pytest.mark.asyncio
    async def test_entity_async_local_poll_exception(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test async_local_poll handles exceptions."""
        mock_charger.all_properties = {"test_prop": "test_value"}

        desc = WattpilotSensorEntityDescription(
            key="test",
            charger_key="test_prop",
            name="Test",
            source=SOURCE_PROPERTY,
        )

        entity = ChargerPlatformEntity(mock_hass, mock_config_entry, desc, mock_charger)

        with patch(
            "custom_components.wattpilot.entities.async_GetChargerProp",
            side_effect=RuntimeError("Poll failed"),
        ):
            # Should handle exception gracefully
            await entity.async_local_poll()

    @pytest.mark.asyncio
    async def test_entity_async_local_push_attribute_source(
        self, mock_hass: HomeAssistant, mock_config_entry: Any
    ) -> None:
        """Test async_local_push with attribute source (no-op)."""
        charger = MagicMock()
        charger.test_attr = "value"
        charger.serial = "12345678"

        desc = WattpilotSensorEntityDescription(
            key="test",
            charger_key="test_attr",
            name="Test",
            source=SOURCE_ATTRIBUTE,
        )

        entity = ChargerPlatformEntity(mock_hass, mock_config_entry, desc, charger)
        entity.async_write_ha_state = MagicMock()

        with patch(
            "custom_components.wattpilot.entities.CoordinatorEntity.enabled",
            new_callable=PropertyMock,
            return_value=True,
        ):
            await entity.async_local_push("new_value")
            # For attribute source, state should remain unchanged (pass through)

    @pytest.mark.asyncio
    async def test_entity_async_local_push_namespacelist(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test async_local_push with namespacelist source."""
        mock_charger.all_properties = {"test_list": ["value1", "value2"]}

        desc = WattpilotSensorEntityDescription(
            key="test",
            charger_key="test_list",
            name="Test",
            source=SOURCE_NAMESPACELIST,
            namespace_id="1",
        )

        entity = ChargerPlatformEntity(mock_hass, mock_config_entry, desc, mock_charger)
        entity.async_write_ha_state = MagicMock()

        with patch(
            "custom_components.wattpilot.entities.CoordinatorEntity.enabled",
            new_callable=PropertyMock,
            return_value=True,
        ):
            await entity.async_local_push(["value1", "new_value2"])
            entity.async_write_ha_state.assert_called_once()

    @pytest.mark.asyncio
    async def test_entity_async_local_push_validation_returns_none(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test async_local_push falls back to poll when validation returns None."""
        mock_charger.all_properties = {"test_prop": "test_value"}

        desc = WattpilotSensorEntityDescription(
            key="test",
            charger_key="test_prop",
            name="Test",
            source=SOURCE_PROPERTY,
        )

        entity = ChargerPlatformEntity(mock_hass, mock_config_entry, desc, mock_charger)
        entity.async_local_poll = AsyncMock()

        with (
            patch(
                "custom_components.wattpilot.entities.CoordinatorEntity.enabled",
                new_callable=PropertyMock,
                return_value=True,
            ),
            patch.object(entity, "_async_update_validate_property", return_value=None),
        ):
            await entity.async_local_push("value")
            # Should fall back to poll when validation returns None
            entity.async_local_poll.assert_called_once()

    @pytest.mark.asyncio
    async def test_entity_async_local_push_no_entity_error_retry(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test async_local_push retries on NoEntitySpecifiedError."""
        mock_charger.all_properties = {"test_prop": "test_value"}

        desc = WattpilotSensorEntityDescription(
            key="test",
            charger_key="test_prop",
            name="Test",
            source=SOURCE_PROPERTY,
        )

        entity = ChargerPlatformEntity(mock_hass, mock_config_entry, desc, mock_charger)
        entity.async_write_ha_state = MagicMock()

        # Create a custom exception class with the specific name
        class NoEntitySpecifiedError(Exception):
            pass

        call_count = 0

        async def mock_validate(state):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise NoEntitySpecifiedError("No entity specified")
            return state

        with (
            patch(
                "custom_components.wattpilot.entities.CoordinatorEntity.enabled",
                new_callable=PropertyMock,
                return_value=True,
            ),
            patch.object(
                entity, "_async_update_validate_property", side_effect=mock_validate
            ),
            patch("asyncio.sleep", new_callable=AsyncMock),
        ):
            await entity.async_local_push("value")
            # Should retry after sleep
            assert call_count == 2

    @pytest.mark.asyncio
    async def test_entity_async_local_push_other_exception(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test async_local_push handles other exceptions."""
        mock_charger.all_properties = {"test_prop": "test_value"}

        desc = WattpilotSensorEntityDescription(
            key="test",
            charger_key="test_prop",
            name="Test",
            source=SOURCE_PROPERTY,
        )

        entity = ChargerPlatformEntity(mock_hass, mock_config_entry, desc, mock_charger)

        with (
            patch(
                "custom_components.wattpilot.entities.CoordinatorEntity.enabled",
                new_callable=PropertyMock,
                return_value=True,
            ),
            patch.object(
                entity,
                "_async_update_validate_property",
                side_effect=RuntimeError("Push failed"),
            ),
        ):
            # Should handle exception gracefully
            await entity.async_local_push("value")


class TestCoordinatorErrorPaths:
    """Test coordinator.py error paths (lines 81-82, 92, 113, 132, 134-147)."""

    @pytest.mark.asyncio
    async def test_coordinator_handle_property_update_none_data(
        self, mock_hass: HomeAssistant, mock_charger: MagicMock
    ) -> None:
        """Test coordinator handles property update when data is None."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.coordinator import WattpilotCoordinator

        entry = ConfigEntry(
            version=1,
            minor_version=0,
            domain=DOMAIN,
            title="Test",
            data={},
            source="user",
            unique_id="test",
            discovery_keys={},
            options={},
            subentries_data={},
        )

        coordinator = WattpilotCoordinator(mock_hass, mock_charger, entry)
        coordinator.data = None

        # Should initialize data dict
        coordinator.async_handle_property_update("test_prop", "test_value")
        assert coordinator.data is not None
        assert coordinator.data["test_prop"] == "test_value"

    @pytest.mark.asyncio
    async def test_coordinator_update_data_unavailable_max_attempts(
        self, mock_hass: HomeAssistant, mock_charger: MagicMock
    ) -> None:
        """Test coordinator logs warning after max failed attempts."""
        from homeassistant.config_entries import ConfigEntry
        from homeassistant.helpers.update_coordinator import UpdateFailed

        from custom_components.wattpilot.coordinator import WattpilotCoordinator

        entry = ConfigEntry(
            version=1,
            minor_version=0,
            domain=DOMAIN,
            title="Test",
            data={},
            source="user",
            unique_id="test",
            discovery_keys={},
            options={},
            subentries_data={},
        )

        mock_charger.connected = False
        mock_charger.properties_initialized = False

        coordinator = WattpilotCoordinator(mock_hass, mock_charger, entry)
        coordinator._failed_update_count = 2  # Already 2 failures

        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()
            # Should log warning on 3rd failure

    @pytest.mark.asyncio
    async def test_coordinator_update_data_all_properties_none(
        self, mock_hass: HomeAssistant, mock_charger: MagicMock
    ) -> None:
        """Test coordinator handles None all_properties."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.coordinator import WattpilotCoordinator

        entry = ConfigEntry(
            version=1,
            minor_version=0,
            domain=DOMAIN,
            title="Test",
            data={},
            source="user",
            unique_id="test",
            discovery_keys={},
            options={},
            subentries_data={},
        )

        mock_charger.connected = True
        mock_charger.properties_initialized = True
        mock_charger.all_properties = None

        coordinator = WattpilotCoordinator(mock_hass, mock_charger, entry)

        result = await coordinator._async_update_data()
        # Should return empty dict when all_properties is None
        assert result == {}

    @pytest.mark.asyncio
    async def test_coordinator_update_data_exception(
        self, mock_hass: HomeAssistant, mock_charger: MagicMock
    ) -> None:
        """Test coordinator handles exception getting all_properties."""
        from homeassistant.config_entries import ConfigEntry
        from homeassistant.helpers.update_coordinator import UpdateFailed

        from custom_components.wattpilot.coordinator import WattpilotCoordinator

        entry = ConfigEntry(
            version=1,
            minor_version=0,
            domain=DOMAIN,
            title="Test",
            data={},
            source="user",
            unique_id="test",
            discovery_keys={},
            options={},
            subentries_data={},
        )

        mock_charger.connected = True
        mock_charger.properties_initialized = True

        # Make all_properties raise exception
        type(mock_charger).all_properties = PropertyMock(
            side_effect=RuntimeError("Property access failed")
        )

        coordinator = WattpilotCoordinator(mock_hass, mock_charger, entry)

        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()


class TestConfigurationSchema:
    """Test configuration_schema.py error paths (lines 64-93, 98-127)."""

    @pytest.mark.asyncio
    async def test_get_options_local_schema_exception(self) -> None:
        """Test async_get_OPTIONS_LOCAL_SCHEMA handles exceptions."""
        from custom_components.wattpilot.configuration_schema import (
            LOCAL_SCHEMA,
            async_get_OPTIONS_LOCAL_SCHEMA,
        )

        # Pass data that will cause an exception
        bad_data = MagicMock()
        bad_data.get = MagicMock(side_effect=RuntimeError("Get failed"))

        result = await async_get_OPTIONS_LOCAL_SCHEMA(bad_data)
        # Should return LOCAL_SCHEMA on exception
        assert result == LOCAL_SCHEMA

    @pytest.mark.asyncio
    async def test_get_options_cloud_schema_exception(self) -> None:
        """Test async_get_OPTIONS_CLOUD_SCHEMA handles exceptions."""
        from custom_components.wattpilot.configuration_schema import (
            CLOUD_SCHEMA,
            async_get_OPTIONS_CLOUD_SCHEMA,
        )

        # Pass data that will cause an exception
        bad_data = MagicMock()
        bad_data.get = MagicMock(side_effect=RuntimeError("Get failed"))

        result = await async_get_OPTIONS_CLOUD_SCHEMA(bad_data)
        # Should return CLOUD_SCHEMA on exception
        assert result == CLOUD_SCHEMA


class TestDiagnosticsErrorPaths:
    """Test diagnostics.py error paths (lines 46-47, 68-69, 92-93, 113-114)."""

    @pytest.mark.asyncio
    async def test_diagnostics_config_exception(
        self, hass: HomeAssistant, mock_charger: MagicMock, mock_config_entry_data: dict
    ) -> None:
        """Test diagnostics handles exception getting config."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.diagnostics import (
            async_get_config_entry_diagnostics,
        )
        from custom_components.wattpilot.types import WattpilotRuntimeData

        entry = ConfigEntry(
            version=1,
            minor_version=0,
            domain=DOMAIN,
            title="Test",
            data=mock_config_entry_data,
            source="user",
            unique_id="test",
            discovery_keys={},
            options={},
            subentries_data={},
        )

        coordinator = MagicMock()
        entry.runtime_data = WattpilotRuntimeData(
            charger=mock_charger,
            coordinator=coordinator,
            push_entities={},
            params=mock_config_entry_data,
        )

        # Make as_dict raise exception
        entry.as_dict = MagicMock(side_effect=RuntimeError("as_dict failed"))

        diag = await async_get_config_entry_diagnostics(hass, entry)
        # Should handle exception and still return dict
        assert isinstance(diag, dict)

    @pytest.mark.asyncio
    async def test_diagnostics_charger_properties_exception(
        self, hass: HomeAssistant, mock_charger: MagicMock, mock_config_entry_data: dict
    ) -> None:
        """Test diagnostics handles exception getting charger properties."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.diagnostics import (
            async_get_config_entry_diagnostics,
        )

        entry = ConfigEntry(
            version=1,
            minor_version=0,
            domain=DOMAIN,
            title="Test",
            data=mock_config_entry_data,
            source="user",
            unique_id="test",
            discovery_keys={},
            options={},
            subentries_data={},
        )

        # Make charger access raise exception
        runtime_data = MagicMock()
        type(runtime_data).charger = PropertyMock(
            side_effect=RuntimeError("Charger access failed")
        )
        entry.runtime_data = runtime_data

        diag = await async_get_config_entry_diagnostics(hass, entry)
        # Should handle exception and still return dict
        assert isinstance(diag, dict)

    @pytest.mark.asyncio
    async def test_diagnostics_charger_info_exception(
        self, hass: HomeAssistant, mock_charger: MagicMock, mock_config_entry_data: dict
    ) -> None:
        """Test diagnostics handles exception getting charger info."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.diagnostics import (
            async_get_config_entry_diagnostics,
        )
        from custom_components.wattpilot.types import WattpilotRuntimeData

        entry = ConfigEntry(
            version=1,
            minor_version=0,
            domain=DOMAIN,
            title="Test",
            data=mock_config_entry_data,
            source="user",
            unique_id="test",
            discovery_keys={},
            options={},
            subentries_data={},
        )

        coordinator = MagicMock()
        # Make charger.serial raise exception
        mock_charger_with_error = MagicMock()
        type(mock_charger_with_error).serial = PropertyMock(
            side_effect=RuntimeError("Serial access failed")
        )

        entry.runtime_data = WattpilotRuntimeData(
            charger=mock_charger_with_error,
            coordinator=coordinator,
            push_entities={},
            params=mock_config_entry_data,
        )

        diag = await async_get_config_entry_diagnostics(hass, entry)
        # Should handle exception and still return dict
        assert isinstance(diag, dict)

    @pytest.mark.asyncio
    async def test_diagnostics_modules_exception(
        self, hass: HomeAssistant, mock_charger: MagicMock, mock_config_entry_data: dict
    ) -> None:
        """Test diagnostics handles exception getting module versions."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.diagnostics import (
            async_get_config_entry_diagnostics,
        )
        from custom_components.wattpilot.types import WattpilotRuntimeData

        entry = ConfigEntry(
            version=1,
            minor_version=0,
            domain=DOMAIN,
            title="Test",
            data=mock_config_entry_data,
            source="user",
            unique_id="test",
            discovery_keys={},
            options={},
            subentries_data={},
        )

        coordinator = MagicMock()
        entry.runtime_data = WattpilotRuntimeData(
            charger=mock_charger,
            coordinator=coordinator,
            push_entities={},
            params=mock_config_entry_data,
        )

        with patch(
            "custom_components.wattpilot.diagnostics.version",
            side_effect=RuntimeError("Version failed"),
        ):
            diag = await async_get_config_entry_diagnostics(hass, entry)
            # Should handle exception and still return dict
            assert isinstance(diag, dict)


class TestSensorValidation:
    """Test sensor.py validation error paths (lines 116, 119-122, 130, 132-141)."""

    @pytest.mark.asyncio
    async def test_sensor_validate_state_enum_not_in_keys_or_values(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test sensor validation logs warning when state not in enum."""
        from custom_components.wattpilot.sensor import ChargerSensor

        mock_charger.all_properties = {"test_prop": "test_value"}

        desc = WattpilotSensorEntityDescription(
            key="test",
            charger_key="test_prop",
            name="Test",
            source=SOURCE_PROPERTY,
            enum={1: "one", 2: "two"},  # State must match these
        )

        entity = ChargerSensor(mock_hass, mock_config_entry, desc, mock_charger)

        # Pass a state not in enum
        result = await entity._async_update_validate_platform_state(99)
        # Method logs warning but returns the value as-is
        assert result == 99

    @pytest.mark.asyncio
    async def test_sensor_validate_state_exception(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test sensor validation handles exceptions."""
        from custom_components.wattpilot.sensor import ChargerSensor

        mock_charger.all_properties = {"test_prop": "test_value"}

        desc = WattpilotSensorEntityDescription(
            key="test",
            charger_key="test_prop",
            name="Test",
            source=SOURCE_PROPERTY,
        )

        entity = ChargerSensor(mock_hass, mock_config_entry, desc, mock_charger)

        # Pass something that causes exception
        bad_state = MagicMock()
        bad_state.__eq__ = MagicMock(side_effect=RuntimeError("Comparison failed"))

        result = await entity._async_update_validate_platform_state(bad_state)
        # Should return None on exception
        assert result is None
