"""Tests for utility functions."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.const import CONF_IP_ADDRESS, CONF_PASSWORD
from homeassistant.core import HomeAssistant

from custom_components.wattpilot.const import (
    CONF_CLOUD,
    CONF_CONNECTION,
    CONF_LOCAL,
    CONF_SERIAL,
    DOMAIN,
)
from custom_components.wattpilot.utils import (
    GetChargerProp,
    async_ConnectCharger,
    async_DisconnectCharger,
    async_GetChargerFromDeviceID,
    async_GetChargerProp,
    async_GetDataStoreFromDeviceID,
    async_property_update_handler,
    async_SetChargerProp,
)


class TestPropertyUpdateHandler:
    """Test async_property_update_handler function."""

    @pytest.mark.asyncio
    async def test_property_update_handler_success(
        self, mock_hass: HomeAssistant, mock_config_entry: Any
    ) -> None:
        """Test property update handler with valid entry."""
        # Already setup via fixture
        await async_property_update_handler(
            mock_hass, mock_config_entry, "test_prop", "test_value"
        )
        mock_config_entry.runtime_data.coordinator.async_handle_property_update.assert_called_once_with(
            "test_prop", "test_value"
        )

    @pytest.mark.asyncio
    async def test_property_update_handler_with_entity(
        self, mock_hass: HomeAssistant, mock_config_entry: Any
    ) -> None:
        """Test property update handler dispatches to entity."""
        entity = MagicMock()
        entity.async_local_push = AsyncMock()

        # Add entity to push_entities
        mock_config_entry.runtime_data.push_entities["test_prop"] = entity

        mock_hass.async_create_task = MagicMock(side_effect=lambda coro: coro)

        await async_property_update_handler(
            mock_hass, mock_config_entry, "test_prop", "test_value"
        )
        entity.async_local_push.assert_called_once()

    @pytest.mark.asyncio
    async def test_property_update_handler_fires_event(
        self, mock_hass: HomeAssistant, mock_config_entry: Any
    ) -> None:
        """Test property update handler fires event for EVENT_PROPS."""
        # Update params via fixture
        mock_config_entry.runtime_data.params["friendly_name"] = "Test Charger"

        with patch("custom_components.wattpilot.utils.EVENT_PROPS", ["test_prop"]):
            await async_property_update_handler(
                mock_hass, mock_config_entry, "test_prop", "test_value"
            )
            mock_hass.bus.fire.assert_called_once()

    @pytest.mark.asyncio
    async def test_property_update_handler_missing_runtime_data(
        self, mock_hass: HomeAssistant, mock_config_entry: Any
    ) -> None:
        """Test property update handler with missing runtime data."""
        mock_config_entry.runtime_data = None

        # Should log error but not raise
        await async_property_update_handler(
            mock_hass, mock_config_entry, "test_prop", "test_value"
        )

    @pytest.mark.asyncio
    async def test_property_update_handler_exception(
        self, mock_hass: HomeAssistant, mock_config_entry: Any
    ) -> None:
        """Test property update handler handles exceptions."""
        mock_config_entry.runtime_data.coordinator.async_handle_property_update = (
            MagicMock(side_effect=Exception("test error"))
        )

        # Should log exception but not raise
        await async_property_update_handler(
            mock_hass, mock_config_entry, "test_prop", "test_value"
        )


class TestChargerPropertyAccess:
    """Test GetChargerProp and async_GetChargerProp functions."""

    def test_get_charger_prop_success(self, mock_charger: MagicMock) -> None:
        """Test GetChargerProp returns property value."""
        mock_charger.all_properties = {"frc": 1, "amp": 16}

        result = GetChargerProp(mock_charger, "frc")
        assert result == 1

    def test_get_charger_prop_with_default(self, mock_charger: MagicMock) -> None:
        """Test GetChargerProp returns default for missing property."""
        mock_charger.all_properties = {}

        result = GetChargerProp(mock_charger, "missing_prop", "default")
        assert result == "default"

    def test_get_charger_prop_none_value_uses_default(
        self, mock_charger: MagicMock
    ) -> None:
        """Test GetChargerProp returns default when property is None."""
        mock_charger.all_properties = {"test": None}

        result = GetChargerProp(mock_charger, "test", "fallback")
        assert result == "fallback"

    def test_get_charger_prop_missing_all_properties(self) -> None:
        """Test GetChargerProp with charger missing all_properties."""
        charger = MagicMock(spec=[])

        result = GetChargerProp(charger, "test", "default")
        assert result == "default"

    def test_get_charger_prop_none_identifier(self, mock_charger: MagicMock) -> None:
        """Test GetChargerProp with None identifier."""
        result = GetChargerProp(mock_charger, None, "default")
        assert result == "default"

    def test_get_charger_prop_exception(self, mock_charger: MagicMock) -> None:
        """Test GetChargerProp handles exceptions."""
        mock_charger.all_properties = MagicMock(side_effect=Exception("test"))

        result = GetChargerProp(mock_charger, "test", "default")
        assert result == "default"

    @pytest.mark.asyncio
    async def test_async_get_charger_prop_success(
        self, mock_charger: MagicMock
    ) -> None:
        """Test async_GetChargerProp returns property value."""
        mock_charger.all_properties = {"frc": 1, "amp": 16}

        result = await async_GetChargerProp(mock_charger, "frc")
        assert result == 1

    @pytest.mark.asyncio
    async def test_async_get_charger_prop_with_default(
        self, mock_charger: MagicMock
    ) -> None:
        """Test async_GetChargerProp returns default for missing property."""
        mock_charger.all_properties = {}

        result = await async_GetChargerProp(mock_charger, "missing", "default")
        assert result == "default"

    @pytest.mark.asyncio
    async def test_async_get_charger_prop_none_value_uses_default(
        self, mock_charger: MagicMock
    ) -> None:
        """Test async_GetChargerProp returns default when property is None."""
        mock_charger.all_properties = {"test": None}

        result = await async_GetChargerProp(mock_charger, "test", "fallback")
        assert result == "fallback"

    @pytest.mark.asyncio
    async def test_async_get_charger_prop_missing_all_properties(self) -> None:
        """Test async_GetChargerProp with charger missing all_properties."""
        charger = MagicMock(spec=[])

        result = await async_GetChargerProp(charger, "test", "default")
        assert result == "default"

    @pytest.mark.asyncio
    async def test_async_get_charger_prop_none_identifier(
        self, mock_charger: MagicMock
    ) -> None:
        """Test async_GetChargerProp with None identifier."""
        result = await async_GetChargerProp(mock_charger, None, "default")
        assert result == "default"

    @pytest.mark.asyncio
    async def test_async_get_charger_prop_exception(
        self, mock_charger: MagicMock
    ) -> None:
        """Test async_GetChargerProp handles exceptions."""
        mock_charger.all_properties = MagicMock(side_effect=Exception("test"))

        result = await async_GetChargerProp(mock_charger, "test", "default")
        assert result == "default"


class TestChargerPropertySetter:
    """Test async_SetChargerProp function."""

    @pytest.mark.asyncio
    async def test_set_charger_prop_success(self, mock_charger: MagicMock) -> None:
        """Test async_SetChargerProp sets property."""
        result = await async_SetChargerProp(mock_charger, "frc", 1)
        assert result is True
        mock_charger.set_property.assert_called_once_with("frc", 1)

    @pytest.mark.asyncio
    async def test_set_charger_prop_none_identifier(
        self, mock_charger: MagicMock
    ) -> None:
        """Test async_SetChargerProp with None identifier."""
        result = await async_SetChargerProp(mock_charger, None, 1)
        assert result is False
        mock_charger.set_property.assert_not_called()

    @pytest.mark.asyncio
    async def test_set_charger_prop_none_value(self, mock_charger: MagicMock) -> None:
        """Test async_SetChargerProp with None value."""
        result = await async_SetChargerProp(mock_charger, "frc", None)
        assert result is False
        mock_charger.set_property.assert_not_called()

    @pytest.mark.asyncio
    async def test_set_charger_prop_exception(self, mock_charger: MagicMock) -> None:
        """Test async_SetChargerProp handles exceptions."""
        mock_charger.set_property = AsyncMock(side_effect=Exception("test"))

        result = await async_SetChargerProp(mock_charger, "frc", 1)
        assert result is False


class TestDeviceRegistry:
    """Test device registry utility functions."""

    @pytest.mark.asyncio
    async def test_get_data_store_from_device_id_success(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test async_GetDataStoreFromDeviceID returns data store."""
        device = MagicMock()
        device.config_entries = {mock_config_entry.entry_id}

        # Already setup via fixture
        with (
            patch(
                "custom_components.wattpilot.utils.dr.async_get"
            ) as mock_get_registry,
        ):
            mock_registry = MagicMock()
            mock_registry.async_get = MagicMock(return_value=device)
            mock_get_registry.return_value = mock_registry

            mock_hass.config_entries.async_get_entry = MagicMock(
                return_value=mock_config_entry
            )

            result = await async_GetDataStoreFromDeviceID(mock_hass, "test_device_id")

            assert result is not None
            assert "entry" in result
            assert "runtime_data" in result

    @pytest.mark.asyncio
    async def test_get_data_store_from_device_id_device_not_found(
        self, mock_hass: HomeAssistant
    ) -> None:
        """Test async_GetDataStoreFromDeviceID with device not found."""
        with patch(
            "custom_components.wattpilot.utils.dr.async_get"
        ) as mock_get_registry:
            mock_registry = MagicMock()
            mock_registry.async_get = MagicMock(return_value=None)
            mock_get_registry.return_value = mock_registry

            result = await async_GetDataStoreFromDeviceID(mock_hass, "test_device_id")
            assert result is None

    @pytest.mark.asyncio
    async def test_get_data_store_from_device_id_no_matching_entry(
        self, mock_hass: HomeAssistant
    ) -> None:
        """Test async_GetDataStoreFromDeviceID with no matching config entry."""
        device = MagicMock()
        device.config_entries = {"other_entry_id"}

        with patch(
            "custom_components.wattpilot.utils.dr.async_get"
        ) as mock_get_registry:
            mock_registry = MagicMock()
            mock_registry.async_get = MagicMock(return_value=device)
            mock_get_registry.return_value = mock_registry

            mock_hass.config_entries.async_get_entry = MagicMock(return_value=None)

            result = await async_GetDataStoreFromDeviceID(mock_hass, "test_device_id")
            assert result is None

    @pytest.mark.asyncio
    async def test_get_data_store_from_device_id_wrong_domain(
        self, mock_hass: HomeAssistant, mock_config_entry: Any
    ) -> None:
        """Test async_GetDataStoreFromDeviceID skips wrong domain."""
        device = MagicMock()
        device.config_entries = {mock_config_entry.entry_id}

        wrong_entry = MagicMock()
        wrong_entry.domain = "other_domain"

        with patch(
            "custom_components.wattpilot.utils.dr.async_get"
        ) as mock_get_registry:
            mock_registry = MagicMock()
            mock_registry.async_get = MagicMock(return_value=device)
            mock_get_registry.return_value = mock_registry

            mock_hass.config_entries.async_get_entry = MagicMock(
                return_value=wrong_entry
            )

            result = await async_GetDataStoreFromDeviceID(mock_hass, "test_device_id")
            assert result is None

    @pytest.mark.asyncio
    async def test_get_data_store_from_device_id_no_runtime_data(
        self, mock_hass: HomeAssistant, mock_config_entry: Any
    ) -> None:
        """Test async_GetDataStoreFromDeviceID with missing runtime data."""
        device = MagicMock()
        device.config_entries = {mock_config_entry.entry_id}

        entry_no_data = MagicMock()
        entry_no_data.domain = DOMAIN
        entry_no_data.runtime_data = None

        with patch(
            "custom_components.wattpilot.utils.dr.async_get"
        ) as mock_get_registry:
            mock_registry = MagicMock()
            mock_registry.async_get = MagicMock(return_value=device)
            mock_get_registry.return_value = mock_registry

            mock_hass.config_entries.async_get_entry = MagicMock(
                return_value=entry_no_data
            )

            result = await async_GetDataStoreFromDeviceID(mock_hass, "test_device_id")
            assert result is None

    @pytest.mark.asyncio
    async def test_get_data_store_from_device_id_exception(
        self, mock_hass: HomeAssistant
    ) -> None:
        """Test async_GetDataStoreFromDeviceID handles exceptions."""
        with patch(
            "custom_components.wattpilot.utils.dr.async_get",
            side_effect=Exception("test"),
        ):
            result = await async_GetDataStoreFromDeviceID(mock_hass, "test_device_id")
            assert result is None

    @pytest.mark.asyncio
    async def test_get_charger_from_device_id_success(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test async_GetChargerFromDeviceID returns charger."""
        device = MagicMock()
        device.config_entries = {mock_config_entry.entry_id}

        # Already setup via fixture
        with patch(
            "custom_components.wattpilot.utils.dr.async_get"
        ) as mock_get_registry:
            mock_registry = MagicMock()
            mock_registry.async_get = MagicMock(return_value=device)
            mock_get_registry.return_value = mock_registry

            mock_hass.config_entries.async_get_entry = MagicMock(
                return_value=mock_config_entry
            )

            result = await async_GetChargerFromDeviceID(mock_hass, "test_device_id")
            assert result == mock_charger

    @pytest.mark.asyncio
    async def test_get_charger_from_device_id_device_not_found(
        self, mock_hass: HomeAssistant
    ) -> None:
        """Test async_GetChargerFromDeviceID with device not found."""
        with patch(
            "custom_components.wattpilot.utils.dr.async_get"
        ) as mock_get_registry:
            mock_registry = MagicMock()
            mock_registry.async_get = MagicMock(return_value=None)
            mock_get_registry.return_value = mock_registry

            result = await async_GetChargerFromDeviceID(mock_hass, "test_device_id")
            assert result is None

    @pytest.mark.asyncio
    async def test_get_charger_from_device_id_no_charger(
        self, mock_hass: HomeAssistant, mock_config_entry: Any
    ) -> None:
        """Test async_GetChargerFromDeviceID with no charger found."""
        device = MagicMock()
        device.config_entries = {mock_config_entry.entry_id}

        entry_no_charger = MagicMock()
        entry_no_charger.domain = DOMAIN
        entry_no_charger.runtime_data = None

        with patch(
            "custom_components.wattpilot.utils.dr.async_get"
        ) as mock_get_registry:
            mock_registry = MagicMock()
            mock_registry.async_get = MagicMock(return_value=device)
            mock_get_registry.return_value = mock_registry

            mock_hass.config_entries.async_get_entry = MagicMock(
                return_value=entry_no_charger
            )

            result = await async_GetChargerFromDeviceID(mock_hass, "test_device_id")
            assert result is None

    @pytest.mark.asyncio
    async def test_get_charger_from_device_id_exception(
        self, mock_hass: HomeAssistant
    ) -> None:
        """Test async_GetChargerFromDeviceID handles exceptions."""
        with patch(
            "custom_components.wattpilot.utils.dr.async_get",
            side_effect=Exception("test"),
        ):
            result = await async_GetChargerFromDeviceID(mock_hass, "test_device_id")
            assert result is None


class TestChargerConnection:
    """Test charger connection functions."""

    @pytest.mark.asyncio
    async def test_connect_charger_local_success(self) -> None:
        """Test async_ConnectCharger for local connection."""
        data = {
            CONF_CONNECTION: CONF_LOCAL,
            CONF_IP_ADDRESS: "192.168.1.100",
            CONF_PASSWORD: "test_pass",
        }

        mock_charger = MagicMock()
        mock_charger.connect = AsyncMock()
        mock_charger.name = "Test Charger"

        with patch(
            "custom_components.wattpilot.utils.Wattpilot"
        ) as mock_wattpilot_class:
            mock_wattpilot_class.return_value = mock_charger

            result = await async_ConnectCharger("test_entry", data)

            assert result == mock_charger
            mock_wattpilot_class.assert_called_once_with(
                host="192.168.1.100",
                password="test_pass",
                serial="192.168.1.100",
                cloud=False,
            )
            mock_charger.connect.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_charger_cloud_success(self) -> None:
        """Test async_ConnectCharger for cloud connection."""
        data = {
            CONF_CONNECTION: CONF_CLOUD,
            CONF_SERIAL: "12345678",
            CONF_PASSWORD: "test_pass",
        }

        mock_charger = MagicMock()
        mock_charger.connect = AsyncMock()
        mock_charger.name = "Test Charger"

        with patch(
            "custom_components.wattpilot.utils.Wattpilot"
        ) as mock_wattpilot_class:
            mock_wattpilot_class.return_value = mock_charger

            result = await async_ConnectCharger("test_entry", data)

            assert result == mock_charger
            mock_wattpilot_class.assert_called_once_with(
                host="12345678",
                password="test_pass",
                serial="12345678",
                cloud=True,
            )
            mock_charger.connect.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_charger_reconnect_existing(self) -> None:
        """Test async_ConnectCharger with existing charger (reconnect)."""
        data = {CONF_CONNECTION: CONF_LOCAL, CONF_IP_ADDRESS: "192.168.1.100"}

        existing_charger = MagicMock()
        existing_charger.connect = AsyncMock()
        existing_charger.name = "Existing Charger"

        result = await async_ConnectCharger("test_entry", data, existing_charger)

        assert result == existing_charger
        existing_charger.connect.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_charger_unknown_connection_type(self) -> None:
        """Test async_ConnectCharger with unknown connection type."""
        data = {CONF_CONNECTION: "invalid"}

        result = await async_ConnectCharger("test_entry", data)
        assert result is False

    @pytest.mark.asyncio
    async def test_connect_charger_exception(self) -> None:
        """Test async_ConnectCharger handles exceptions."""
        data = {
            CONF_CONNECTION: CONF_LOCAL,
            CONF_IP_ADDRESS: "192.168.1.100",
            CONF_PASSWORD: "test_pass",
        }

        with patch(
            "custom_components.wattpilot.utils.Wattpilot",
            side_effect=Exception("Connection failed"),
        ):
            result = await async_ConnectCharger("test_entry", data)
            assert result is False

    @pytest.mark.asyncio
    async def test_disconnect_charger_success(self, mock_charger: MagicMock) -> None:
        """Test async_DisconnectCharger successfully disconnects."""
        await async_DisconnectCharger("test_entry", mock_charger)
        mock_charger.disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_disconnect_charger_exception(self, mock_charger: MagicMock) -> None:
        """Test async_DisconnectCharger handles exceptions."""
        mock_charger.disconnect = AsyncMock(side_effect=Exception("Disconnect failed"))

        # Should log exception but not raise
        await async_DisconnectCharger("test_entry", mock_charger)
