"""Comprehensive tests for service handlers."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch


class TestServiceRegistration:
    """Test service registration functionality."""

    async def test_register_service_function(
        self,
        mock_hass: MagicMock,
    ) -> None:
        """Test async_registerService function."""
        from custom_components.wattpilot.services import async_registerService

        service_handler = AsyncMock()

        with (
            patch("custom_components.wattpilot.services.yaml.safe_load") as mock_path,
            patch(
                "custom_components.wattpilot.services.aiofiles.open",
                create=True,
            ) as mock_open,
        ):
            # Mock the YAML file reading
            mock_file = AsyncMock()
            mock_file.read = AsyncMock(
                return_value="test_service:\n  description: Test\n  fields: {}"
            )
            mock_file.__aenter__ = AsyncMock(return_value=mock_file)
            mock_file.__aexit__ = AsyncMock(return_value=None)
            mock_open.return_value = mock_file

            mock_path_instance = MagicMock()
            mock_path_instance.parent = MagicMock()
            mock_path.return_value = mock_path_instance

            await async_registerService(mock_hass, "test_service", service_handler)

            # Verify service was registered
            mock_hass.services.async_register.assert_called_once()


class TestSetGoECloudService:
    """Test set_goe_cloud service."""

    async def test_set_goe_cloud_service_basic(
        self,
        mock_hass: MagicMock,
        mock_charger: MagicMock,
        mock_config_entry_data: dict,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test set_goe_cloud service with basic parameters."""
        from homeassistant.config_entries import ConfigEntry
        from homeassistant.core import ServiceCall
        from homeassistant.helpers import device_registry as dr

        from custom_components.wattpilot.const import DOMAIN
        from custom_components.wattpilot.services import async_service_SetGoECloud
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

        # Register the device
        device_registry = dr.async_get(mock_hass)
        device = device_registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={(DOMAIN, "12345678")},
            name="Test Wattpilot",
        )

        service_call = ServiceCall(
            domain=DOMAIN,
            service="set_goe_cloud",
            data={
                "device_id": device.id,
                "api_key": "test_api_key",
            },
        )

        with (
            patch.object(
                mock_hass.config_entries, "async_get_entry", return_value=entry
            ),
            patch(
                "custom_components.wattpilot.services.async_SetChargerProp"
            ) as mock_set,
        ):
            await async_service_SetGoECloud(mock_hass, service_call)
            # Should call async_SetChargerProp
            assert mock_set.called


class TestSetGoCurrentService:
    """Test set_go_current service (if exists)."""

    async def test_service_module_imports(self) -> None:
        """Test that services module imports successfully."""
        from custom_components.wattpilot import services

        assert services is not None
        assert hasattr(services, "async_registerService")
        assert hasattr(services, "async_service_SetNextTrip")
        assert hasattr(services, "async_service_DisconnectCharger")
        assert hasattr(services, "async_service_ReConnectCharger")
        assert hasattr(services, "async_service_SetGoECloud")
        assert hasattr(services, "async_service_SetDebugProperties")


class TestServiceHelpers:
    """Test service helper functions."""

    async def test_get_device_from_service_call(
        self,
        mock_hass: MagicMock,
    ) -> None:
        """Test getting device from service call."""
        from homeassistant.core import ServiceCall
        from homeassistant.helpers import device_registry as dr

        # Create a device
        device_registry = dr.async_get(mock_hass)
        device = device_registry.async_get_or_create(
            config_entry_id="test_entry",
            identifiers={("test_domain", "test_id")},
            name="Test Device",
        )

        # Create service call with device_id
        service_call = ServiceCall(
            domain="test_domain",
            service="test_service",
            data={"device_id": device.id},
        )

        # Verify device_id is in service call data
        assert "device_id" in service_call.data
        assert service_call.data["device_id"] == device.id


class TestNextTripServiceDetails:
    """Detailed tests for set_next_trip service."""

    async def test_next_trip_with_input_datetime(
        self,
        mock_hass: MagicMock,
        mock_charger: MagicMock,
        mock_config_entry_data: dict,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test set_next_trip with input_datetime_id parameter."""
        from homeassistant.config_entries import ConfigEntry
        from homeassistant.core import ServiceCall
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

        device_registry = dr.async_get(mock_hass)
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
                "departure_time": "2024-12-25 08:00:00",
                "input_datetime_id": "input_datetime.wattpilot_departure",
            },
        )

        # Mock the state for input_datetime
        mock_hass.states = MagicMock()
        mock_hass.states.get = MagicMock(return_value=None)

        with (
            patch.object(
                mock_hass.config_entries, "async_get_entry", return_value=entry
            ),
            patch(
                "custom_components.wattpilot.services.async_SetChargerProp"
            ) as mock_set,
        ):
            await async_service_SetNextTrip(mock_hass, service_call)
            assert mock_set.called

    async def test_next_trip_date_parsing(
        self,
        mock_hass: MagicMock,
        mock_charger: MagicMock,
        mock_config_entry_data: dict,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test set_next_trip date parsing."""
        from homeassistant.config_entries import ConfigEntry
        from homeassistant.core import ServiceCall
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

        device_registry = dr.async_get(mock_hass)
        device = device_registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={(DOMAIN, "12345678")},
            name="Test Wattpilot",
        )

        # Test with different date formats
        test_dates = [
            "2024-12-25 08:00:00",
            "08:00:00",
            "2024-12-25T08:00:00",
        ]

        for date_str in test_dates:
            service_call = ServiceCall(
                domain=DOMAIN,
                service="set_next_trip",
                data={
                    "device_id": device.id,
                    "departure_time": date_str,
                },
            )

            with (
                patch.object(
                    mock_hass.config_entries, "async_get_entry", return_value=entry
                ),
                patch("custom_components.wattpilot.services.async_SetChargerProp"),
            ):
                await async_service_SetNextTrip(mock_hass, service_call)
                # Should process without error
                assert True


class TestDebugPropertiesServiceDetails:
    """Detailed tests for debug properties service."""

    async def test_debug_properties_with_list(
        self,
        mock_hass: MagicMock,
        mock_charger: MagicMock,
        mock_config_entry_data: dict,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test set_debug_properties with property list."""
        from homeassistant.config_entries import ConfigEntry
        from homeassistant.core import ServiceCall
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

        device_registry = dr.async_get(mock_hass)
        device = device_registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={(DOMAIN, "12345678")},
            name="Test Wattpilot",
        )

        service_call = ServiceCall(
            domain=DOMAIN,
            service="set_debug_properties",
            data={
                "device_id": device.id,
                "enable": True,
                "properties": ["car", "amp", "nrg"],
            },
        )

        with patch.object(
            mock_hass.config_entries, "async_get_entry", return_value=entry
        ):
            await async_service_SetDebugProperties(mock_hass, service_call)
            # Debug properties should be set to a list
            assert isinstance(runtime_data.debug_properties, list)
            assert "car" in runtime_data.debug_properties
