"""Tests for utility functions."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.core import HomeAssistant


class TestGetChargerProp:
    """Test GetChargerProp function."""

    def test_get_existing_property(self, mock_charger: MagicMock) -> None:
        """Test getting an existing property."""
        from custom_components.wattpilot.utils import GetChargerProp

        mock_charger.allProps = {"test_prop": "test_value"}
        result = GetChargerProp(mock_charger, "test_prop")
        assert result == "test_value"

    def test_get_missing_property_returns_default(
        self, mock_charger: MagicMock
    ) -> None:
        """Test getting a missing property returns default."""
        from custom_components.wattpilot.utils import GetChargerProp

        mock_charger.allProps = {}
        result = GetChargerProp(mock_charger, "missing_prop", "default_value")
        assert result == "default_value"

    def test_get_none_property_returns_default(self, mock_charger: MagicMock) -> None:
        """Test getting None property returns default."""
        from custom_components.wattpilot.utils import GetChargerProp

        mock_charger.allProps = {"test_prop": None}
        result = GetChargerProp(mock_charger, "test_prop", "default_value")
        assert result == "default_value"

    def test_get_from_charger_without_allprops(self) -> None:
        """Test getting from charger without allProps."""
        from custom_components.wattpilot.utils import GetChargerProp

        charger = MagicMock(spec=[])
        result = GetChargerProp(charger, "test_prop", "default_value")
        assert result == "default_value"


class TestAsyncGetChargerProp:
    """Test async_GetChargerProp function."""

    async def test_async_get_existing_property(self, mock_charger: MagicMock) -> None:
        """Test async getting an existing property."""
        from custom_components.wattpilot.utils import async_GetChargerProp

        mock_charger.allProps = {"test_prop": "test_value"}
        result = await async_GetChargerProp(mock_charger, "test_prop")
        assert result == "test_value"

    async def test_async_get_missing_property_returns_default(
        self, mock_charger: MagicMock
    ) -> None:
        """Test async getting a missing property returns default."""
        from custom_components.wattpilot.utils import async_GetChargerProp

        mock_charger.allProps = {}
        result = await async_GetChargerProp(
            mock_charger, "missing_prop", "default_value"
        )
        assert result == "default_value"

    async def test_async_get_none_property_returns_default(
        self, mock_charger: MagicMock
    ) -> None:
        """Test async getting None property returns default."""
        from custom_components.wattpilot.utils import async_GetChargerProp

        mock_charger.allProps = {"test_prop": None}
        result = await async_GetChargerProp(mock_charger, "test_prop", "default_value")
        assert result == "default_value"


class TestAsyncSetChargerProp:
    """Test async_SetChargerProp function."""

    async def test_async_set_existing_property(self, mock_charger: MagicMock) -> None:
        """Test async setting an existing property."""
        from custom_components.wattpilot.utils import async_SetChargerProp

        mock_charger.allProps = {"test_prop": "old_value"}
        mock_charger.send_update = MagicMock()

        result = await async_SetChargerProp(mock_charger, "test_prop", "new_value")
        assert result is True
        mock_charger.send_update.assert_called_once()

    async def test_async_set_missing_property_without_force(
        self, mock_charger: MagicMock
    ) -> None:
        """Test async setting a missing property without force returns False."""
        from custom_components.wattpilot.utils import async_SetChargerProp

        mock_charger.allProps = {}
        mock_charger.send_update = MagicMock()

        result = await async_SetChargerProp(mock_charger, "missing_prop", "value")
        assert result is False
        mock_charger.send_update.assert_not_called()

    async def test_async_set_missing_property_with_force(
        self, mock_charger: MagicMock
    ) -> None:
        """Test async setting a missing property with force succeeds."""
        from custom_components.wattpilot.utils import async_SetChargerProp

        mock_charger.allProps = {}
        mock_charger.send_update = MagicMock()

        result = await async_SetChargerProp(
            mock_charger, "missing_prop", "value", force=True
        )
        assert result is True
        mock_charger.send_update.assert_called_once()


class TestPropertyUpdateHandler:
    """Test PropertyUpdateHandler function."""

    async def test_property_update_handler_updates_coordinator(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_config_entry_data: dict,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test property update handler updates coordinator."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.const import DOMAIN
        from custom_components.wattpilot.types import WattpilotRuntimeData
        from custom_components.wattpilot.utils import async_PropertyUpdateHandler

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

        await async_PropertyUpdateHandler(hass, entry, "test_prop", "test_value")
        mock_coordinator.async_handle_property_update.assert_called_once_with(
            "test_prop", "test_value"
        )

    async def test_property_update_handler_fires_event(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_config_entry_data: dict,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test property update handler fires event for EVENT_PROPS."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.const import DOMAIN, EVENT_PROPS_ID
        from custom_components.wattpilot.types import WattpilotRuntimeData
        from custom_components.wattpilot.utils import async_PropertyUpdateHandler

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

        # Test with an event property (e.g., "ftt" or "cak")
        with patch.object(hass.bus, "fire") as mock_fire:
            await async_PropertyUpdateHandler(hass, entry, "ftt", "test_value")
            mock_fire.assert_called_once()
            call_args = mock_fire.call_args[0]
            assert call_args[0] == EVENT_PROPS_ID


class TestAsyncGetDataStoreFromDeviceID:
    """Test async_GetDataStoreFromDeviceID function."""

    async def test_get_data_store_success(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_config_entry_data: dict,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test getting data store from device ID."""
        from homeassistant.config_entries import ConfigEntry
        from homeassistant.helpers import device_registry as dr

        from custom_components.wattpilot.const import DOMAIN
        from custom_components.wattpilot.types import WattpilotRuntimeData
        from custom_components.wattpilot.utils import async_GetDataStoreFromDeviceID

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

        # Create a mock device
        device_registry = dr.async_get(hass)
        device = device_registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={(DOMAIN, "12345678")},
            name="Test Wattpilot",
        )

        with patch.object(hass.config_entries, "async_get_entry", return_value=entry):
            result = await async_GetDataStoreFromDeviceID(hass, device.id)
            assert result is not None
            assert result["runtime_data"] == runtime_data

    async def test_get_data_store_device_not_found(
        self,
        hass: HomeAssistant,
    ) -> None:
        """Test getting data store with invalid device ID."""
        from custom_components.wattpilot.utils import async_GetDataStoreFromDeviceID

        result = await async_GetDataStoreFromDeviceID(hass, "invalid_device_id")
        assert result is None


class TestAsyncGetChargerFromDeviceID:
    """Test async_GetChargerFromDeviceID function."""

    async def test_get_charger_success(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_config_entry_data: dict,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test getting charger from device ID."""
        from homeassistant.config_entries import ConfigEntry
        from homeassistant.helpers import device_registry as dr

        from custom_components.wattpilot.const import DOMAIN
        from custom_components.wattpilot.types import WattpilotRuntimeData
        from custom_components.wattpilot.utils import async_GetChargerFromDeviceID

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

        device_registry = dr.async_get(hass)
        device = device_registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={(DOMAIN, "12345678")},
            name="Test Wattpilot",
        )

        with patch.object(hass.config_entries, "async_get_entry", return_value=entry):
            result = await async_GetChargerFromDeviceID(hass, device.id)
            assert result == mock_charger

    async def test_get_charger_device_not_found(
        self,
        hass: HomeAssistant,
    ) -> None:
        """Test getting charger with invalid device ID."""
        from custom_components.wattpilot.utils import async_GetChargerFromDeviceID

        result = await async_GetChargerFromDeviceID(hass, "invalid_device_id")
        assert result is None


class TestDebugFunctions:
    """Test debug utility functions."""

    async def test_async_programming_debug(self) -> None:
        """Test async_ProgrammingDebug function."""
        from custom_components.wattpilot.utils import async_ProgrammingDebug

        test_obj = MagicMock()
        test_obj.test_attr = "test_value"

        # Should not raise an exception
        await async_ProgrammingDebug(test_obj)

    def test_programming_debug(self) -> None:
        """Test ProgrammingDebug function."""
        from custom_components.wattpilot.utils import ProgrammingDebug

        test_obj = MagicMock()
        test_obj.test_attr = "test_value"

        # Should not raise an exception
        ProgrammingDebug(test_obj)

    async def test_async_property_debug(self) -> None:
        """Test async_PropertyDebug function."""
        from custom_components.wattpilot.utils import async_PropertyDebug

        # Test with list of properties
        await async_PropertyDebug("test_prop", "test_value", ["test_prop"])

        # Test with boolean True (should log non-excluded properties)
        await async_PropertyDebug("test_prop", "test_value", True)

        # Test with excluded property
        await async_PropertyDebug("rssi", "test_value", True)


class TestDynamicLoadModule:
    """Test dynamic module loading."""

    def test_wattpilot_module_loaded(self) -> None:
        """Test that wattpilot module was loaded."""
        from custom_components.wattpilot.utils import wattpilot

        assert wattpilot is not None
        assert hasattr(wattpilot, "__file__")


class TestAsyncConnectCharger:
    """Test async_ConnectCharger function."""

    async def test_connect_charger_local(
        self,
        mock_charger: MagicMock,
    ) -> None:
        """Test connecting to charger via local connection."""
        from custom_components.wattpilot.utils import async_ConnectCharger

        config = {
            "connection": "local",
            "ip_address": "192.168.1.100",
            "password": "test_password",
        }

        with patch(
            "custom_components.wattpilot.utils.wattpilot.Wattpilot",
            return_value=mock_charger,
        ):
            result = await async_ConnectCharger("test_entry_id", config)
            assert result is not None


class TestAsyncDisconnectCharger:
    """Test async_DisconnectCharger function."""

    async def test_disconnect_charger(
        self,
        mock_charger: MagicMock,
    ) -> None:
        """Test disconnecting from charger."""
        from custom_components.wattpilot.utils import async_DisconnectCharger

        mock_charger.disconnect = AsyncMock()

        await async_DisconnectCharger("test_entry_id", mock_charger)
        mock_charger.disconnect.assert_called_once()
