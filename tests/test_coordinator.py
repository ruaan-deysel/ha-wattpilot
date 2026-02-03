"""Tests for the WattpilotCoordinator."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock, patch

import pytest

from .fixtures import get_charger_properties

if TYPE_CHECKING:
    from collections.abc import Generator


class TestWattpilotCoordinator:
    """Test suite for WattpilotCoordinator."""

    @pytest.fixture
    def mock_hass(self) -> MagicMock:
        """Create a mock Home Assistant instance."""
        hass = MagicMock()
        hass.loop = MagicMock()
        hass.data = {}
        hass.async_create_task = MagicMock()
        return hass

    @pytest.fixture
    def mock_entry(self) -> MagicMock:
        """Create a mock config entry."""
        entry = MagicMock()
        entry.entry_id = "test_entry_id"
        entry.data = {"friendly_name": "Test Wattpilot"}
        return entry

    @pytest.fixture
    def mock_charger(self) -> MagicMock:
        """Create a mock charger."""
        charger = MagicMock()
        charger.serial = "12345678"
        charger.name = "Test Wattpilot"
        charger.firmware = "40.7"
        charger.connected = True
        charger.allPropsInitialized = True
        charger.allProps = get_charger_properties()
        return charger

    @pytest.fixture
    def coordinator(
        self, mock_hass: MagicMock, mock_entry: MagicMock, mock_charger: MagicMock
    ) -> Generator[Any]:
        """Create a coordinator instance with mocked dependencies."""
        with patch(
            "custom_components.wattpilot.coordinator.DataUpdateCoordinator.__init__",
            return_value=None,
        ):
            from custom_components.wattpilot.coordinator import WattpilotCoordinator

            coord = WattpilotCoordinator(mock_hass, mock_charger, mock_entry)
            # Manually set attributes that would be set by parent __init__
            coord.hass = mock_hass
            coord.data = mock_charger.allProps
            coord.last_update_success = True
            coord.async_set_updated_data = MagicMock()
            coord._listeners = {}  # Required for async_update_listeners
            coord.async_update_listeners = MagicMock()  # Mock the listener update
            yield coord

    def test_coordinator_init(
        self, mock_hass: MagicMock, mock_entry: MagicMock, mock_charger: MagicMock
    ) -> None:
        """Test coordinator initialization."""
        with patch(
            "custom_components.wattpilot.coordinator.DataUpdateCoordinator.__init__",
            return_value=None,
        ):
            from custom_components.wattpilot.coordinator import WattpilotCoordinator

            coord = WattpilotCoordinator(mock_hass, mock_charger, mock_entry)
            assert coord.charger == mock_charger
            assert coord.charger_serial == mock_charger.serial

    def test_charger_property(self, coordinator: Any) -> None:
        """Test charger property accessor."""
        assert coordinator.charger is not None

    def test_available_when_connected(
        self, coordinator: Any, mock_charger: MagicMock
    ) -> None:
        """Test availability when charger is connected and initialized."""
        mock_charger.connected = True
        mock_charger.allPropsInitialized = True
        assert coordinator.available is True

    def test_unavailable_when_disconnected(
        self, coordinator: Any, mock_charger: MagicMock
    ) -> None:
        """Test unavailability when charger is disconnected."""
        mock_charger.connected = False
        assert coordinator.available is False

    def test_unavailable_when_not_initialized(
        self, coordinator: Any, mock_charger: MagicMock
    ) -> None:
        """Test unavailability when properties not initialized."""
        mock_charger.connected = True
        mock_charger.allPropsInitialized = False
        assert coordinator.available is False

    def test_handle_property_update(
        self, coordinator: Any, mock_charger: MagicMock
    ) -> None:
        """Test handling property updates."""
        # Store original data reference
        coordinator.data = dict(mock_charger.allProps)

        coordinator.async_handle_property_update("amp", 10)

        # Verify data was updated
        assert coordinator.data["amp"] == 10

        # Verify async_update_listeners was called
        coordinator.async_update_listeners.assert_called_once()

    def test_handle_property_update_with_new_key(
        self, coordinator: Any, mock_charger: MagicMock
    ) -> None:
        """Test handling property updates with a new key."""
        # Store original data reference
        coordinator.data = dict(mock_charger.allProps)

        coordinator.async_handle_property_update("new_prop", "new_value")

        assert coordinator.data["new_prop"] == "new_value"
        coordinator.async_update_listeners.assert_called_once()


class TestCoordinatorDataFlow:
    """Test data flow through the coordinator."""

    @pytest.fixture
    def mock_hass(self) -> MagicMock:
        """Create a mock Home Assistant instance."""
        hass = MagicMock()
        hass.loop = MagicMock()
        return hass

    @pytest.fixture
    def mock_charger(self) -> MagicMock:
        """Create a mock charger with allProps."""
        charger = MagicMock()
        charger.connected = True
        charger.allPropsInitialized = True
        charger.allProps = get_charger_properties()
        return charger

    def test_data_contains_charger_properties(self, mock_charger: MagicMock) -> None:
        """Test that coordinator data contains charger properties."""
        properties = mock_charger.allProps
        assert "amp" in properties
        assert "eto" in properties
        assert "car" in properties
        assert "nrg" in properties

    def test_energy_values_in_data(self, mock_charger: MagicMock) -> None:
        """Test that energy values are present in data."""
        properties = mock_charger.allProps
        assert properties["eto"] == 12345000  # Total energy in Wh
        assert properties["wh"] == 1000  # Session energy in Wh

    def test_current_settings_in_data(self, mock_charger: MagicMock) -> None:
        """Test that current settings are present in data."""
        properties = mock_charger.allProps
        assert properties["amp"] == 6  # Requested current
        assert properties["ama"] == 16  # Max current limit


class TestCoordinatorAsync:
    """Test async methods of the coordinator."""

    @pytest.fixture
    def mock_hass(self) -> MagicMock:
        """Create a mock Home Assistant instance."""
        hass = MagicMock()
        hass.loop = MagicMock()
        return hass

    @pytest.fixture
    def mock_entry(self) -> MagicMock:
        """Create a mock config entry."""
        entry = MagicMock()
        entry.entry_id = "test_entry_id"
        return entry

    @pytest.fixture
    def mock_charger(self) -> MagicMock:
        """Create a mock charger."""
        charger = MagicMock()
        charger.serial = "12345678"
        charger.name = "Test Wattpilot"
        charger.connected = True
        charger.allPropsInitialized = True
        charger.allProps = get_charger_properties()
        return charger

    @pytest.mark.asyncio
    async def test_async_refresh_returns_data(
        self, mock_hass: MagicMock, mock_entry: MagicMock, mock_charger: MagicMock
    ) -> None:
        """Test that _async_update_data returns charger properties."""
        with patch(
            "custom_components.wattpilot.coordinator.DataUpdateCoordinator.__init__",
            return_value=None,
        ):
            from custom_components.wattpilot.coordinator import WattpilotCoordinator

            coord = WattpilotCoordinator(mock_hass, mock_charger, mock_entry)

            data = await coord._async_update_data()
            assert data == mock_charger.allProps

    @pytest.mark.asyncio
    async def test_async_refresh_raises_on_disconnect(
        self, mock_hass: MagicMock, mock_entry: MagicMock, mock_charger: MagicMock
    ) -> None:
        """Test that _async_update_data raises when disconnected."""
        from homeassistant.helpers.update_coordinator import UpdateFailed

        with patch(
            "custom_components.wattpilot.coordinator.DataUpdateCoordinator.__init__",
            return_value=None,
        ):
            from custom_components.wattpilot.coordinator import WattpilotCoordinator

            mock_charger.connected = False
            coord = WattpilotCoordinator(mock_hass, mock_charger, mock_entry)

            with pytest.raises(UpdateFailed):
                await coord._async_update_data()
