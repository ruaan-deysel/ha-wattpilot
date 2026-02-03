"""Tests for service handlers."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.core import HomeAssistant, ServiceCall


class TestServiceRegistration:
    """Test service registration."""

    async def test_async_register_service(
        self,
        hass: HomeAssistant,
    ) -> None:
        """Test service registration."""
        from custom_components.wattpilot.services import async_registerService

        service_handler = AsyncMock()

        await async_registerService(hass, "test_service", service_handler)

        # Service should be registered
        assert hass.services.has_service("wattpilot", "test_service")


class TestSetNextTripService:
    """Test set_next_trip service."""

    async def test_set_next_trip_success(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_config_entry_data: dict,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test set_next_trip service with valid data."""
        from homeassistant.config_entries import ConfigEntry
        from homeassistant.helpers import device_registry as dr

        from custom_components.wattpilot.const import DOMAIN
        from custom_components.wattpilot.services import async_service_SetNextTrip
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

        device_registry = dr.async_get(hass)
        device = device_registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={(DOMAIN, "12345678")},
            name="Test Wattpilot",
        )

        service_call = ServiceCall(
            domain=DOMAIN,
            service="set_next_trip",
            data={
                "device_id": device.id,
                "departure_time": "2024-01-01 08:00:00",
            },
        )

        with (
            patch.object(hass.config_entries, "async_get_entry", return_value=entry),
            patch(
                "custom_components.wattpilot.services.async_SetChargerProp"
            ) as mock_set,
        ):
            await async_service_SetNextTrip(hass, service_call)
            # Should have called async_SetChargerProp at least once
            assert mock_set.called


class TestDisconnectChargerService:
    """Test disconnect_charger service."""

    async def test_disconnect_charger_success(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_config_entry_data: dict,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test disconnect_charger service."""
        from homeassistant.config_entries import ConfigEntry
        from homeassistant.helpers import device_registry as dr

        from custom_components.wattpilot.const import DOMAIN
        from custom_components.wattpilot.services import async_service_DisconnectCharger
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

        device_registry = dr.async_get(hass)
        device = device_registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={(DOMAIN, "12345678")},
            name="Test Wattpilot",
        )

        service_call = ServiceCall(
            domain=DOMAIN,
            service="disconnect_charger",
            data={"device_id": device.id},
        )

        with (
            patch.object(hass.config_entries, "async_get_entry", return_value=entry),
            patch(
                "custom_components.wattpilot.services.async_DisconnectCharger"
            ) as mock_disconnect,
        ):
            await async_service_DisconnectCharger(hass, service_call)
            mock_disconnect.assert_called_once()


class TestReconnectChargerService:
    """Test reconnect_charger service."""

    async def test_reconnect_charger_success(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_config_entry_data: dict,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test reconnect_charger service."""
        from homeassistant.config_entries import ConfigEntry
        from homeassistant.helpers import device_registry as dr

        from custom_components.wattpilot.const import DOMAIN
        from custom_components.wattpilot.services import async_service_ReConnectCharger
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

        device_registry = dr.async_get(hass)
        device = device_registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={(DOMAIN, "12345678")},
            name="Test Wattpilot",
        )

        service_call = ServiceCall(
            domain=DOMAIN,
            service="reconnect_charger",
            data={"device_id": device.id},
        )

        with (
            patch.object(hass.config_entries, "async_get_entry", return_value=entry),
            patch(
                "custom_components.wattpilot.services.async_DisconnectCharger"
            ) as mock_disconnect,
            patch(
                "custom_components.wattpilot.services.async_ConnectCharger",
                return_value=mock_charger,
            ) as mock_connect,
        ):
            await async_service_ReConnectCharger(hass, service_call)
            mock_disconnect.assert_called_once()
            mock_connect.assert_called_once()


class TestSetDebugPropertiesService:
    """Test set_debug_properties service."""

    async def test_set_debug_properties_enable(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_config_entry_data: dict,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test set_debug_properties service enabling debug."""
        from homeassistant.config_entries import ConfigEntry
        from homeassistant.helpers import device_registry as dr

        from custom_components.wattpilot.const import DOMAIN
        from custom_components.wattpilot.services import (
            async_service_SetDebugProperties,
        )
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

        device_registry = dr.async_get(hass)
        device = device_registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={(DOMAIN, "12345678")},
            name="Test Wattpilot",
        )

        service_call = ServiceCall(
            domain=DOMAIN,
            service="set_debug_properties",
            data={"device_id": device.id, "enable": True},
        )

        with patch.object(hass.config_entries, "async_get_entry", return_value=entry):
            await async_service_SetDebugProperties(hass, service_call)
            # Debug properties should be enabled
            assert runtime_data.debug_properties is True

    async def test_set_debug_properties_disable(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_config_entry_data: dict,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test set_debug_properties service disabling debug."""
        from homeassistant.config_entries import ConfigEntry
        from homeassistant.helpers import device_registry as dr

        from custom_components.wattpilot.const import DOMAIN
        from custom_components.wattpilot.services import (
            async_service_SetDebugProperties,
        )
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
            debug_properties=True,
        )
        entry.runtime_data = runtime_data

        device_registry = dr.async_get(hass)
        device = device_registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={(DOMAIN, "12345678")},
            name="Test Wattpilot",
        )

        service_call = ServiceCall(
            domain=DOMAIN,
            service="set_debug_properties",
            data={"device_id": device.id, "enable": False},
        )

        with patch.object(hass.config_entries, "async_get_entry", return_value=entry):
            await async_service_SetDebugProperties(hass, service_call)
            # Debug properties should be disabled
            assert runtime_data.debug_properties is False
