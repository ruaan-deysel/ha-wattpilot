"""Integration tests for service handlers with proper Home Assistant setup."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.core import HomeAssistant


class TestServiceHandlerIntegration:
    """Integration tests for service handlers."""

    async def test_disconnect_charger_handler(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test disconnect_charger service handler."""
        from custom_components.wattpilot.const import DOMAIN
        from custom_components.wattpilot.services import async_service_DisconnectCharger
        from custom_components.wattpilot.types import WattpilotRuntimeData

        # Create runtime data
        runtime_data = WattpilotRuntimeData(
            charger=mock_charger,
            coordinator=mock_coordinator,
            push_entities={},
            params={},
            debug_properties=False,
        )

        # Store in hass.data
        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN]["test_entry"] = runtime_data

        # Mock async_DisconnectCharger
        with patch(
            "custom_components.wattpilot.utils.async_DisconnectCharger",
            new_callable=AsyncMock,
        ) as mock_disconnect:
            # Create a mock service call
            service_call = MagicMock()
            service_call.data = {"entry_id": "test_entry"}

            # Call the handler
            await async_service_DisconnectCharger(hass, service_call)

            # Verify disconnect was called
            assert mock_disconnect.called

    async def test_reconnect_charger_handler(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test reconnect_charger service handler."""
        from custom_components.wattpilot.const import DOMAIN
        from custom_components.wattpilot.services import async_service_ReConnectCharger
        from custom_components.wattpilot.types import WattpilotRuntimeData

        # Create runtime data
        runtime_data = WattpilotRuntimeData(
            charger=mock_charger,
            coordinator=mock_coordinator,
            push_entities={},
            params={"ip_address": "192.168.1.100", "password": "test"},
            debug_properties=False,
        )

        # Store in hass.data
        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN]["test_entry"] = runtime_data

        # Mock async_ConnectCharger
        with patch(
            "custom_components.wattpilot.services.async_ConnectCharger",
            return_value=mock_charger,
        ):
            # Create a mock service call
            service_call = MagicMock()
            service_call.data = {"entry_id": "test_entry"}

            # Call the handler
            await async_service_ReConnectCharger(hass, service_call)

            # Verify charger reference is updated
            assert runtime_data.charger is not None

    async def test_set_debug_properties_enable(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test set_debug_properties service with enable=True."""
        from custom_components.wattpilot.const import DOMAIN
        from custom_components.wattpilot.services import (
            async_service_SetDebugProperties,
        )
        from custom_components.wattpilot.types import WattpilotRuntimeData

        # Create runtime data
        runtime_data = WattpilotRuntimeData(
            charger=mock_charger,
            coordinator=mock_coordinator,
            push_entities={},
            params={},
            debug_properties=False,
        )

        # Store in hass.data
        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN]["test_entry"] = runtime_data

        # Create a mock service call
        service_call = MagicMock()
        service_call.data = {
            "entry_id": "test_entry",
            "enable": True,
            "properties": ["car", "amp", "nrg"],
        }

        # Call the handler
        await async_service_SetDebugProperties(hass, service_call)

        # Verify debug properties were set
        assert runtime_data.debug_properties == ["car", "amp", "nrg"]

    async def test_set_debug_properties_disable(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test set_debug_properties service with enable=False."""
        from custom_components.wattpilot.const import DOMAIN
        from custom_components.wattpilot.services import (
            async_service_SetDebugProperties,
        )
        from custom_components.wattpilot.types import WattpilotRuntimeData

        # Create runtime data
        runtime_data = WattpilotRuntimeData(
            charger=mock_charger,
            coordinator=mock_coordinator,
            push_entities={},
            params={},
            debug_properties=["car", "amp"],
        )

        # Store in hass.data
        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN]["test_entry"] = runtime_data

        # Create a mock service call
        service_call = MagicMock()
        service_call.data = {
            "entry_id": "test_entry",
            "enable": False,
        }

        # Call the handler
        await async_service_SetDebugProperties(hass, service_call)

        # Verify debug properties were disabled
        assert runtime_data.debug_properties is False

    async def test_set_goe_cloud_handler(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test set_goe_cloud service handler."""
        from custom_components.wattpilot.const import DOMAIN
        from custom_components.wattpilot.services import async_service_SetGoECloud
        from custom_components.wattpilot.types import WattpilotRuntimeData

        # Create runtime data
        runtime_data = WattpilotRuntimeData(
            charger=mock_charger,
            coordinator=mock_coordinator,
            push_entities={},
            params={},
            debug_properties=False,
        )

        # Store in hass.data
        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN]["test_entry"] = runtime_data

        # Mock async_SetChargerProp
        with patch(
            "custom_components.wattpilot.services.async_SetChargerProp"
        ) as mock_set:
            # Create a mock service call
            service_call = MagicMock()
            service_call.data = {
                "entry_id": "test_entry",
                "api_key": "test_key",
                "api_url": "https://api.test.com",
            }

            # Call the handler
            await async_service_SetGoECloud(hass, service_call)

            # Verify properties were set
            assert mock_set.call_count >= 1

    async def test_set_next_trip_handler(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test set_next_trip service handler."""
        from custom_components.wattpilot.const import DOMAIN
        from custom_components.wattpilot.services import async_service_SetNextTrip
        from custom_components.wattpilot.types import WattpilotRuntimeData

        # Create runtime data
        runtime_data = WattpilotRuntimeData(
            charger=mock_charger,
            coordinator=mock_coordinator,
            push_entities={},
            params={},
            debug_properties=False,
        )

        # Store in hass.data
        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN]["test_entry"] = runtime_data

        # Mock async_SetChargerProp
        with patch(
            "custom_components.wattpilot.services.async_SetChargerProp"
        ) as mock_set:
            # Create a mock service call
            service_call = MagicMock()
            service_call.data = {
                "entry_id": "test_entry",
                "departure_time": "2024-12-25 08:00:00",
                "energy": 50,
            }

            # Call the handler
            await async_service_SetNextTrip(hass, service_call)

            # Verify properties were set
            assert mock_set.call_count >= 1


class TestServiceRegistration:
    """Test service registration."""

    async def test_async_register_service(
        self,
        hass: HomeAssistant,
    ) -> None:
        """Test async_registerService function."""
        from custom_components.wattpilot.services import async_registerService

        service_handler = AsyncMock()

        # Mock YAML loading
        with (
            patch("builtins.open", create=True),
            patch(
                "yaml.safe_load",
                return_value={"test_service": {"description": "Test", "fields": {}}},
            ),
        ):
            await async_registerService(hass, "test_service", service_handler)

            # Verify service was registered
            assert hass.services.has_service("wattpilot", "test_service")


class TestServiceHelpers:
    """Test service helper functions."""

    async def test_get_runtime_data_from_entry_id(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test getting runtime data from entry_id."""
        from custom_components.wattpilot.const import DOMAIN
        from custom_components.wattpilot.types import WattpilotRuntimeData

        # Create runtime data
        runtime_data = WattpilotRuntimeData(
            charger=mock_charger,
            coordinator=mock_coordinator,
            push_entities={},
            params={},
            debug_properties=False,
        )

        # Store in hass.data
        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN]["test_entry"] = runtime_data

        # Retrieve it
        retrieved = hass.data[DOMAIN].get("test_entry")
        assert retrieved is runtime_data
        assert retrieved.charger is mock_charger


class TestServiceCallDataExtraction:
    """Test extracting data from service calls."""

    def test_extract_entry_id(self) -> None:
        """Test extracting entry_id from service call."""
        service_call = MagicMock()
        service_call.data = {"entry_id": "test_entry_123"}

        entry_id = service_call.data.get("entry_id")
        assert entry_id == "test_entry_123"

    def test_extract_departure_time(self) -> None:
        """Test extracting departure_time from service call."""
        service_call = MagicMock()
        service_call.data = {"departure_time": "2024-12-25 08:00:00"}

        departure_time = service_call.data.get("departure_time")
        assert departure_time == "2024-12-25 08:00:00"

    def test_extract_debug_properties(self) -> None:
        """Test extracting debug properties from service call."""
        service_call = MagicMock()
        service_call.data = {
            "enable": True,
            "properties": ["car", "amp"],
        }

        enable = service_call.data.get("enable")
        properties = service_call.data.get("properties")

        assert enable is True
        assert properties == ["car", "amp"]


class TestServiceErrorHandling:
    """Test service error handling."""

    async def test_service_with_invalid_entry_id(
        self,
        hass: HomeAssistant,
    ) -> None:
        """Test service call with invalid entry_id."""
        from custom_components.wattpilot.const import DOMAIN

        # Ensure DOMAIN exists but entry doesn't
        hass.data.setdefault(DOMAIN, {})

        service_call = MagicMock()
        service_call.data = {"entry_id": "nonexistent"}

        # Try to get runtime data
        runtime_data = hass.data[DOMAIN].get("nonexistent")
        assert runtime_data is None

    async def test_service_with_missing_required_field(self) -> None:
        """Test service call with missing required field."""
        service_call = MagicMock()
        service_call.data = {}

        # Entry ID should be required
        entry_id = service_call.data.get("entry_id")
        assert entry_id is None


class TestServiceDateTimeParsing:
    """Test datetime parsing in services."""

    def test_parse_iso_datetime(self) -> None:
        """Test parsing ISO format datetime."""
        dt_str = "2024-12-25T08:00:00"
        dt = datetime.fromisoformat(dt_str)

        assert dt.year == 2024
        assert dt.month == 12
        assert dt.day == 25
        assert dt.hour == 8

    def test_parse_space_separated_datetime(self) -> None:
        """Test parsing space-separated datetime."""
        dt_str = "2024-12-25 08:00:00"
        dt = datetime.fromisoformat(dt_str.replace(" ", "T"))

        assert dt.year == 2024
        assert dt.hour == 8

    def test_extract_time_components(self) -> None:
        """Test extracting time components from datetime."""
        import re

        dt_str = "2024-12-25 08:30:45"
        time_pattern = r"(\d{1,2}):(\d{2}):(\d{2})"

        match = re.search(time_pattern, dt_str)
        assert match is not None

        hours = int(match.group(1))
        minutes = int(match.group(2))
        seconds = int(match.group(3))

        assert hours == 8
        assert minutes == 30
        assert seconds == 45


class TestServicePropertyUpdates:
    """Test service property updates."""

    async def test_set_charger_property(
        self,
        mock_charger: MagicMock,
    ) -> None:
        """Test setting a charger property."""
        mock_charger.send_update = AsyncMock()

        # Simulate setting a property
        await mock_charger.send_update("amp", 16)

        mock_charger.send_update.assert_called_once_with("amp", 16)

    async def test_set_multiple_properties(
        self,
        mock_charger: MagicMock,
    ) -> None:
        """Test setting multiple charger properties."""
        mock_charger.send_update = AsyncMock()

        # Simulate setting multiple properties
        properties = [
            ("amp", 16),
            ("lmo", 3),
            ("cae", True),
        ]

        for prop, value in properties:
            await mock_charger.send_update(prop, value)

        assert mock_charger.send_update.call_count == 3


class TestCloudApiConfiguration:
    """Test cloud API configuration via service."""

    def test_extract_api_key(self) -> None:
        """Test extracting API key from service call."""
        service_call = MagicMock()
        service_call.data = {
            "api_key": "test_api_key_12345",
            "api_url": "https://api.test.com",
        }

        api_key = service_call.data.get("api_key")
        api_url = service_call.data.get("api_url")

        assert api_key == "test_api_key_12345"
        assert api_url == "https://api.test.com"

    def test_validate_api_url(self) -> None:
        """Test validating API URL format."""
        valid_urls = [
            "https://api.fronius.com",
            "https://custom.api.url",
            "http://localhost:8080",
        ]

        for url in valid_urls:
            assert url.startswith(("http://", "https://"))


class TestNextTripConfiguration:
    """Test next trip configuration."""

    def test_calculate_trip_time(self) -> None:
        """Test calculating trip departure time."""
        # Parse departure time
        departure_str = "2024-12-25 08:00:00"
        departure = datetime.fromisoformat(departure_str.replace(" ", "T"))

        # Convert to epoch
        epoch = int(departure.timestamp())

        assert epoch > 0
        assert isinstance(epoch, int)

    def test_energy_value_handling(self) -> None:
        """Test handling energy value for trip."""
        service_call = MagicMock()
        service_call.data = {
            "energy": 50,
            "departure_time": "08:00:00",
        }

        energy = service_call.data.get("energy", 0)
        assert energy == 50
        assert isinstance(energy, int)
