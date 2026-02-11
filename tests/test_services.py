"""Tests for service handlers."""

from __future__ import annotations

import datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.const import (
    CONF_API_KEY,
    CONF_DEVICE_ID,
    CONF_EXTERNAL_URL,
    CONF_PARAMS,
    CONF_TRIGGER_TIME,
)
from homeassistant.core import HomeAssistant

from custom_components.wattpilot.const import CONF_CLOUD_API, DOMAIN
from custom_components.wattpilot.services import (
    async_registerService,
    async_service_DisconnectCharger,
    async_service_ReConnectCharger,
    async_service_SetGoECloud,
    async_service_SetNextTrip,
)


class TestServiceRegistration:
    """Test async_registerService function."""

    @pytest.mark.asyncio
    async def test_register_service_success(self, mock_hass: HomeAssistant) -> None:
        """Test service registration when not already registered."""
        mock_hass.services.has_service = MagicMock(return_value=False)
        mock_hass.services.async_register = MagicMock()

        test_service = AsyncMock()
        await async_registerService(mock_hass, "test_service", test_service)

        mock_hass.services.has_service.assert_called_once_with(DOMAIN, "test_service")
        mock_hass.services.async_register.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_service_already_exists(
        self, mock_hass: HomeAssistant
    ) -> None:
        """Test service registration when already registered."""
        mock_hass.services.has_service = MagicMock(return_value=True)
        mock_hass.services.async_register = MagicMock()

        test_service = AsyncMock()
        await async_registerService(mock_hass, "test_service", test_service)

        mock_hass.services.has_service.assert_called_once_with(DOMAIN, "test_service")
        mock_hass.services.async_register.assert_not_called()

    @pytest.mark.asyncio
    async def test_register_service_exception(self, mock_hass: HomeAssistant) -> None:
        """Test service registration handles exceptions."""
        mock_hass.services.has_service = MagicMock(
            side_effect=Exception("Registration failed")
        )

        test_service = AsyncMock()
        # Should log error but not raise
        await async_registerService(mock_hass, "test_service", test_service)


class TestSetNextTrip:
    """Test async_service_SetNextTrip function."""

    @pytest.mark.asyncio
    async def test_set_next_trip_success(self, mock_hass: HomeAssistant) -> None:
        """Test set next trip with valid parameters."""
        call = MagicMock()
        call.data = {CONF_DEVICE_ID: "test_device", CONF_TRIGGER_TIME: "08:30:00"}

        mock_charger = MagicMock()
        mock_charger.set_next_trip = AsyncMock()
        mock_charger.name = "Test Charger"

        with patch(
            "custom_components.wattpilot.services.async_GetChargerFromDeviceID",
            return_value=mock_charger,
        ):
            await async_service_SetNextTrip(mock_hass, call)

            expected_time = datetime.time(8, 30, 0)
            mock_charger.set_next_trip.assert_called_once_with(expected_time)

    @pytest.mark.asyncio
    async def test_set_next_trip_missing_device_id(
        self, mock_hass: HomeAssistant
    ) -> None:
        """Test set next trip with missing device_id."""
        call_data = {CONF_TRIGGER_TIME: "08:30:00"}
        call = MagicMock()
        call.data = call_data

        # Should log error and return without raising
        await async_service_SetNextTrip(mock_hass, call)

    @pytest.mark.asyncio
    async def test_set_next_trip_missing_trigger_time(
        self, mock_hass: HomeAssistant
    ) -> None:
        """Test set next trip with missing trigger_time."""
        call_data = {CONF_DEVICE_ID: "test_device"}
        call = MagicMock()
        call.data = call_data

        # Should log error and return without raising
        await async_service_SetNextTrip(mock_hass, call)

    @pytest.mark.asyncio
    async def test_set_next_trip_charger_not_found(
        self, mock_hass: HomeAssistant
    ) -> None:
        """Test set next trip when charger not found."""
        call_data = {CONF_DEVICE_ID: "test_device", CONF_TRIGGER_TIME: "08:30:00"}
        call = MagicMock()
        call.data = call_data

        with patch(
            "custom_components.wattpilot.services.async_GetChargerFromDeviceID",
            return_value=None,
        ):
            # Should log error and return without raising
            await async_service_SetNextTrip(mock_hass, call)

    @pytest.mark.asyncio
    async def test_set_next_trip_time_parsing(self, mock_hass: HomeAssistant) -> None:
        """Test set next trip with various time formats."""
        test_cases = [
            ("08:30:00", datetime.time(8, 30, 0)),
            ("23:59:59", datetime.time(23, 59, 59)),
            ("00:00:00", datetime.time(0, 0, 0)),
        ]

        for time_str, expected_time in test_cases:
            call_data = {CONF_DEVICE_ID: "test_device", CONF_TRIGGER_TIME: time_str}
            call = MagicMock()
            call.data = call_data

            mock_charger = MagicMock()
            mock_charger.set_next_trip = AsyncMock()
            mock_charger.name = "Test Charger"

            with patch(
                "custom_components.wattpilot.services.async_GetChargerFromDeviceID",
                return_value=mock_charger,
            ):
                await async_service_SetNextTrip(mock_hass, call)
                mock_charger.set_next_trip.assert_called_with(expected_time)

    @pytest.mark.asyncio
    async def test_set_next_trip_exception(self, mock_hass: HomeAssistant) -> None:
        """Test set next trip handles exceptions."""
        call_data = {CONF_DEVICE_ID: "test_device", CONF_TRIGGER_TIME: "invalid"}
        call = MagicMock()
        call.data = call_data

        mock_charger = MagicMock()
        with patch(
            "custom_components.wattpilot.services.async_GetChargerFromDeviceID",
            return_value=mock_charger,
        ):
            # Should log error but not raise
            await async_service_SetNextTrip(mock_hass, call)


class TestSetGoECloud:
    """Test async_service_SetGoECloud function."""

    @pytest.mark.asyncio
    async def test_enable_cloud_api_success(self, mock_hass: HomeAssistant) -> None:
        """Test enabling cloud API."""
        call_data = {CONF_DEVICE_ID: "test_device", CONF_CLOUD_API: True}
        call = MagicMock()
        call.data = call_data

        mock_charger = MagicMock()
        cloud_info = MagicMock()
        cloud_info.api_key = "test_api_key"
        cloud_info.url = "https://test.api"
        mock_charger.enable_cloud_api = AsyncMock(return_value=cloud_info)
        mock_charger.name = "Test Charger"

        entry_data = {
            CONF_PARAMS: {},
        }

        with (
            patch(
                "custom_components.wattpilot.services.async_GetDataStoreFromDeviceID",
                return_value=entry_data,
            ),
            patch(
                "custom_components.wattpilot.services.async_GetChargerFromDeviceID",
                return_value=mock_charger,
            ),
        ):
            await async_service_SetGoECloud(mock_hass, call)

            mock_charger.enable_cloud_api.assert_called_once()
            assert entry_data[CONF_API_KEY] == "test_api_key"
            assert entry_data[CONF_EXTERNAL_URL] == "https://test.api"

    @pytest.mark.asyncio
    async def test_disable_cloud_api_success(self, mock_hass: HomeAssistant) -> None:
        """Test disabling cloud API."""
        call_data = {CONF_DEVICE_ID: "test_device", CONF_CLOUD_API: False}
        call = MagicMock()
        call.data = call_data

        mock_charger = MagicMock()
        mock_charger.disable_cloud_api = AsyncMock()
        mock_charger.name = "Test Charger"

        entry_data = {
            CONF_PARAMS: {},
        }

        with (
            patch(
                "custom_components.wattpilot.services.async_GetDataStoreFromDeviceID",
                return_value=entry_data,
            ),
            patch(
                "custom_components.wattpilot.services.async_GetChargerFromDeviceID",
                return_value=mock_charger,
            ),
        ):
            await async_service_SetGoECloud(mock_hass, call)

            mock_charger.disable_cloud_api.assert_called_once()
            assert entry_data[CONF_API_KEY] is False

    @pytest.mark.asyncio
    async def test_set_goe_cloud_missing_device_id(
        self, mock_hass: HomeAssistant
    ) -> None:
        """Test set cloud with missing device_id."""
        call_data = {CONF_CLOUD_API: True}
        call = MagicMock()
        call.data = call_data

        # Should log error and return without raising
        await async_service_SetGoECloud(mock_hass, call)

    @pytest.mark.asyncio
    async def test_set_goe_cloud_missing_api_state(
        self, mock_hass: HomeAssistant
    ) -> None:
        """Test set cloud with missing api_state."""
        call_data = {CONF_DEVICE_ID: "test_device"}
        call = MagicMock()
        call.data = call_data

        # Should log error and return without raising
        await async_service_SetGoECloud(mock_hass, call)

    @pytest.mark.asyncio
    async def test_set_goe_cloud_entry_data_not_found(
        self, mock_hass: HomeAssistant
    ) -> None:
        """Test set cloud when entry data not found."""
        call_data = {CONF_DEVICE_ID: "test_device", CONF_CLOUD_API: True}
        call = MagicMock()
        call.data = call_data

        with patch(
            "custom_components.wattpilot.services.async_GetDataStoreFromDeviceID",
            return_value=None,
        ):
            # Should log error and return without raising
            await async_service_SetGoECloud(mock_hass, call)

    @pytest.mark.asyncio
    async def test_set_goe_cloud_charger_not_found(
        self, mock_hass: HomeAssistant
    ) -> None:
        """Test set cloud when charger not found."""
        call_data = {CONF_DEVICE_ID: "test_device", CONF_CLOUD_API: True}
        call = MagicMock()
        call.data = call_data

        entry_data = {CONF_PARAMS: {}}

        with (
            patch(
                "custom_components.wattpilot.services.async_GetDataStoreFromDeviceID",
                return_value=entry_data,
            ),
            patch(
                "custom_components.wattpilot.services.async_GetChargerFromDeviceID",
                return_value=None,
            ),
        ):
            # Should log error and return without raising
            await async_service_SetGoECloud(mock_hass, call)

    @pytest.mark.asyncio
    async def test_set_goe_cloud_exception(self, mock_hass: HomeAssistant) -> None:
        """Test set cloud handles exceptions."""
        call_data = {CONF_DEVICE_ID: "test_device", CONF_CLOUD_API: True}
        call = MagicMock()
        call.data = call_data

        with patch(
            "custom_components.wattpilot.services.async_GetDataStoreFromDeviceID",
            side_effect=Exception("test error"),
        ):
            # Should log error but not raise
            await async_service_SetGoECloud(mock_hass, call)


class TestReconnectCharger:
    """Test async_service_ReConnectCharger function."""

    @pytest.mark.asyncio
    async def test_reconnect_charger_success(self, mock_hass: HomeAssistant) -> None:
        """Test reconnect charger with valid parameters."""
        call_data = {CONF_DEVICE_ID: "test_device"}
        call = MagicMock()
        call.data = call_data

        mock_charger = MagicMock()
        mock_charger.connected = True
        mock_charger.disconnect = AsyncMock()
        mock_charger.name = "Test Charger"

        entry_data = {CONF_PARAMS: {"test": "value"}}

        with (
            patch(
                "custom_components.wattpilot.services.async_GetDataStoreFromDeviceID",
                return_value=entry_data,
            ),
            patch(
                "custom_components.wattpilot.services.async_GetChargerFromDeviceID",
                return_value=mock_charger,
            ),
            patch(
                "custom_components.wattpilot.services.async_ConnectCharger",
                return_value=mock_charger,
            ) as mock_connect,
            patch(
                "custom_components.wattpilot.services.asyncio.sleep",
                new_callable=AsyncMock,
            ),
        ):
            result = await async_service_ReConnectCharger(mock_hass, call)

            assert result is True
            mock_charger.disconnect.assert_called_once()
            mock_connect.assert_called_once()

    @pytest.mark.asyncio
    async def test_reconnect_charger_already_disconnected(
        self, mock_hass: HomeAssistant
    ) -> None:
        """Test reconnect charger when already disconnected."""
        call_data = {CONF_DEVICE_ID: "test_device"}
        call = MagicMock()
        call.data = call_data

        mock_charger = MagicMock()
        mock_charger.connected = False
        mock_charger.disconnect = AsyncMock()
        mock_charger.name = "Test Charger"

        entry_data = {CONF_PARAMS: {"test": "value"}}

        with (
            patch(
                "custom_components.wattpilot.services.async_GetDataStoreFromDeviceID",
                return_value=entry_data,
            ),
            patch(
                "custom_components.wattpilot.services.async_GetChargerFromDeviceID",
                return_value=mock_charger,
            ),
            patch(
                "custom_components.wattpilot.services.async_ConnectCharger",
                return_value=mock_charger,
            ),
        ):
            result = await async_service_ReConnectCharger(mock_hass, call)

            assert result is True
            mock_charger.disconnect.assert_not_called()

    @pytest.mark.asyncio
    async def test_reconnect_charger_missing_device_id(
        self, mock_hass: HomeAssistant
    ) -> None:
        """Test reconnect charger with missing device_id."""
        call_data: dict[str, Any] = {}
        call = MagicMock()
        call.data = call_data

        result = await async_service_ReConnectCharger(mock_hass, call)
        assert result is False

    @pytest.mark.asyncio
    async def test_reconnect_charger_entry_data_not_found(
        self, mock_hass: HomeAssistant
    ) -> None:
        """Test reconnect charger when entry data not found."""
        call_data = {CONF_DEVICE_ID: "test_device"}
        call = MagicMock()
        call.data = call_data

        with patch(
            "custom_components.wattpilot.services.async_GetDataStoreFromDeviceID",
            return_value=None,
        ):
            result = await async_service_ReConnectCharger(mock_hass, call)
            assert result is False

    @pytest.mark.asyncio
    async def test_reconnect_charger_charger_not_found(
        self, mock_hass: HomeAssistant
    ) -> None:
        """Test reconnect charger when charger not found."""
        call_data = {CONF_DEVICE_ID: "test_device"}
        call = MagicMock()
        call.data = call_data

        entry_data = {CONF_PARAMS: {}}

        with (
            patch(
                "custom_components.wattpilot.services.async_GetDataStoreFromDeviceID",
                return_value=entry_data,
            ),
            patch(
                "custom_components.wattpilot.services.async_GetChargerFromDeviceID",
                return_value=None,
            ),
        ):
            result = await async_service_ReConnectCharger(mock_hass, call)
            assert result is False

    @pytest.mark.asyncio
    async def test_reconnect_charger_connection_fails(
        self, mock_hass: HomeAssistant
    ) -> None:
        """Test reconnect charger when connection fails."""
        call_data = {CONF_DEVICE_ID: "test_device"}
        call = MagicMock()
        call.data = call_data

        mock_charger = MagicMock()
        mock_charger.connected = False
        entry_data = {CONF_PARAMS: {}}

        with (
            patch(
                "custom_components.wattpilot.services.async_GetDataStoreFromDeviceID",
                return_value=entry_data,
            ),
            patch(
                "custom_components.wattpilot.services.async_GetChargerFromDeviceID",
                return_value=mock_charger,
            ),
            patch(
                "custom_components.wattpilot.services.async_ConnectCharger",
                return_value=False,
            ),
        ):
            result = await async_service_ReConnectCharger(mock_hass, call)
            assert result is False

    @pytest.mark.asyncio
    async def test_reconnect_charger_exception(self, mock_hass: HomeAssistant) -> None:
        """Test reconnect charger handles exceptions."""
        call_data = {CONF_DEVICE_ID: "test_device"}
        call = MagicMock()
        call.data = call_data

        with patch(
            "custom_components.wattpilot.services.async_GetDataStoreFromDeviceID",
            side_effect=Exception("test error"),
        ):
            result = await async_service_ReConnectCharger(mock_hass, call)
            assert result is False


class TestDisconnectCharger:
    """Test async_service_DisconnectCharger function."""

    @pytest.mark.asyncio
    async def test_disconnect_charger_success(self, mock_hass: HomeAssistant) -> None:
        """Test disconnect charger with valid parameters."""
        call_data = {CONF_DEVICE_ID: "test_device"}
        call = MagicMock()
        call.data = call_data

        mock_charger = MagicMock()
        mock_charger.disconnect = AsyncMock()
        mock_charger.name = "Test Charger"

        with patch(
            "custom_components.wattpilot.services.async_GetChargerFromDeviceID",
            return_value=mock_charger,
        ):
            result = await async_service_DisconnectCharger(mock_hass, call)

            assert result is True
            mock_charger.disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_disconnect_charger_missing_device_id(
        self, mock_hass: HomeAssistant
    ) -> None:
        """Test disconnect charger with missing device_id."""
        call_data: dict[str, Any] = {}
        call = MagicMock()
        call.data = call_data

        result = await async_service_DisconnectCharger(mock_hass, call)
        assert result is False

    @pytest.mark.asyncio
    async def test_disconnect_charger_charger_not_found(
        self, mock_hass: HomeAssistant
    ) -> None:
        """Test disconnect charger when charger not found."""
        call_data = {CONF_DEVICE_ID: "test_device"}
        call = MagicMock()
        call.data = call_data

        with patch(
            "custom_components.wattpilot.services.async_GetChargerFromDeviceID",
            return_value=None,
        ):
            result = await async_service_DisconnectCharger(mock_hass, call)
            assert result is False

    @pytest.mark.asyncio
    async def test_disconnect_charger_exception(self, mock_hass: HomeAssistant) -> None:
        """Test disconnect charger handles exceptions."""
        call_data = {CONF_DEVICE_ID: "test_device"}
        call = MagicMock()
        call.data = call_data

        mock_charger = MagicMock()
        mock_charger.disconnect = AsyncMock(side_effect=Exception("test error"))
        mock_charger.name = "Test Charger"

        with patch(
            "custom_components.wattpilot.services.async_GetChargerFromDeviceID",
            return_value=mock_charger,
        ):
            result = await async_service_DisconnectCharger(mock_hass, call)
            assert result is False
