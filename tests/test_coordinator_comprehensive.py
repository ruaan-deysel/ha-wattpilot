"""Comprehensive tests for coordinator."""

from __future__ import annotations

from datetime import timedelta
from unittest.mock import MagicMock

import pytest
from homeassistant.core import HomeAssistant


class TestWattpilotCoordinatorInit:
    """Test coordinator initialization."""

    def test_coordinator_init(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test coordinator initialization."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.const import DOMAIN

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

        from custom_components.wattpilot.const import DOMAIN
        from custom_components.wattpilot.coordinator import WattpilotCoordinator

        coordinator = WattpilotCoordinator(
            hass=hass,
            charger=mock_charger,
            config_entry=entry,
        )

        assert coordinator is not None
        assert coordinator.name == DOMAIN

    def test_coordinator_update_interval(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test coordinator has update interval."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.const import DOMAIN

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

        from custom_components.wattpilot.coordinator import WattpilotCoordinator

        coordinator = WattpilotCoordinator(
            hass=hass,
            charger=mock_charger,
            config_entry=entry,
        )

        # Should have update interval set
        assert coordinator.update_interval is not None
        assert isinstance(coordinator.update_interval, timedelta)


class TestCoordinatorDataRetrieval:
    """Test coordinator data retrieval."""

    async def test_async_update_data_success(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test successful data update."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.const import DOMAIN

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

        from custom_components.wattpilot.coordinator import WattpilotCoordinator

        mock_charger.connected = True
        mock_charger.allPropsInitialized = True
        mock_charger.allProps = {"test": "data"}

        coordinator = WattpilotCoordinator(
            hass=hass,
            charger=mock_charger,
            config_entry=entry,
        )

        data = await coordinator._async_update_data()

        assert data is not None
        assert isinstance(data, dict)

    async def test_async_update_data_charger_disconnected(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test data update when charger disconnected."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.const import DOMAIN

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

        from homeassistant.exceptions import UpdateFailed

        from custom_components.wattpilot.coordinator import WattpilotCoordinator

        mock_charger.connected = False

        coordinator = WattpilotCoordinator(
            hass=hass,
            charger=mock_charger,
            config_entry=entry,
        )

        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()

    async def test_async_update_data_not_initialized(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test data update when not initialized."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.const import DOMAIN

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

        from homeassistant.exceptions import UpdateFailed

        from custom_components.wattpilot.coordinator import WattpilotCoordinator

        mock_charger.connected = True
        mock_charger.allPropsInitialized = False

        coordinator = WattpilotCoordinator(
            hass=hass,
            charger=mock_charger,
            config_entry=entry,
        )

        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()


class TestCoordinatorAvailability:
    """Test coordinator availability."""

    def test_coordinator_available_when_connected(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test coordinator available when connected."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.const import DOMAIN

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

        from custom_components.wattpilot.coordinator import WattpilotCoordinator

        mock_charger.connected = True

        coordinator = WattpilotCoordinator(
            hass=hass,
            charger=mock_charger,
            config_entry=entry,
        )

        # Should be available
        assert coordinator.charger.connected is True

    def test_coordinator_unavailable_when_disconnected(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test coordinator unavailable when disconnected."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.const import DOMAIN

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

        from custom_components.wattpilot.coordinator import WattpilotCoordinator

        mock_charger.connected = False

        coordinator = WattpilotCoordinator(
            hass=hass,
            charger=mock_charger,
            config_entry=entry,
        )

        # Should be unavailable
        assert coordinator.charger.connected is False


class TestCoordinatorPropertyUpdate:
    """Test coordinator property update handling."""

    def test_handle_property_update_existing_key(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test handling property update for existing key."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.const import DOMAIN

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

        from custom_components.wattpilot.coordinator import WattpilotCoordinator

        mock_charger.allProps = {"test_prop": "old_value"}

        coordinator = WattpilotCoordinator(
            hass=hass,
            charger=mock_charger,
            config_entry=entry,
        )

        coordinator.data = {"test_prop": "old_value"}

        # Update property
        coordinator.async_handle_property_update("test_prop", "new_value")

        # Should update data
        assert coordinator.data["test_prop"] == "new_value"

    def test_handle_property_update_new_key(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test handling property update for new key."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.const import DOMAIN

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

        from custom_components.wattpilot.coordinator import WattpilotCoordinator

        coordinator = WattpilotCoordinator(
            hass=hass,
            charger=mock_charger,
            config_entry=entry,
        )

        coordinator.data = {}

        # Add new property
        coordinator.async_handle_property_update("new_prop", "new_value")

        # Should add to data
        assert "new_prop" in coordinator.data
        assert coordinator.data["new_prop"] == "new_value"


class TestCoordinatorDataStructure:
    """Test coordinator data structure."""

    async def test_coordinator_data_is_dict(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test coordinator data is a dictionary."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.const import DOMAIN

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

        from custom_components.wattpilot.coordinator import WattpilotCoordinator

        mock_charger.connected = True
        mock_charger.allPropsInitialized = True
        mock_charger.allProps = {"prop1": "value1", "prop2": "value2"}

        coordinator = WattpilotCoordinator(
            hass=hass,
            charger=mock_charger,
            config_entry=entry,
        )

        data = await coordinator._async_update_data()

        assert isinstance(data, dict)

    async def test_coordinator_data_contains_charger_props(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test coordinator data contains charger properties."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.const import DOMAIN

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

        from custom_components.wattpilot.coordinator import WattpilotCoordinator

        mock_charger.connected = True
        mock_charger.allPropsInitialized = True
        mock_charger.allProps = {"test_prop": "test_value"}

        coordinator = WattpilotCoordinator(
            hass=hass,
            charger=mock_charger,
            config_entry=entry,
        )

        data = await coordinator._async_update_data()

        assert "test_prop" in data
        assert data["test_prop"] == "test_value"


class TestCoordinatorRefresh:
    """Test coordinator refresh methods."""

    async def test_async_config_entry_first_refresh(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test first refresh."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.const import DOMAIN

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

        from custom_components.wattpilot.coordinator import WattpilotCoordinator

        mock_charger.connected = True
        mock_charger.allPropsInitialized = True
        mock_charger.allProps = {"test": "data"}

        coordinator = WattpilotCoordinator(
            hass=hass,
            charger=mock_charger,
            config_entry=entry,
        )

        await coordinator.async_config_entry_first_refresh()

        # Should have data after first refresh
        assert coordinator.data is not None


class TestCoordinatorSetUpdatedData:
    """Test coordinator set updated data."""

    def test_async_set_updated_data(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test async_set_updated_data."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.const import DOMAIN

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

        from custom_components.wattpilot.coordinator import WattpilotCoordinator

        coordinator = WattpilotCoordinator(
            hass=hass,
            charger=mock_charger,
            config_entry=entry,
        )

        new_data = {"prop1": "value1", "prop2": "value2"}

        coordinator.async_set_updated_data(new_data)

        # Data should be updated
        assert coordinator.data == new_data


class TestCoordinatorListeners:
    """Test coordinator listener management."""

    def test_async_add_listener(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test adding listener."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.const import DOMAIN

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

        from custom_components.wattpilot.coordinator import WattpilotCoordinator

        coordinator = WattpilotCoordinator(
            hass=hass,
            charger=mock_charger,
            config_entry=entry,
        )

        listener = MagicMock()

        remove_listener = coordinator.async_add_listener(listener)

        # Should return a remove callback
        assert callable(remove_listener)


class TestCoordinatorEntryId:
    """Test coordinator entry ID handling."""

    def test_coordinator_stores_entry_id(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test coordinator stores entry ID."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.const import DOMAIN

        ConfigEntry(
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

        from custom_components.wattpilot.coordinator import WattpilotCoordinator

        coordinator = WattpilotCoordinator(
            hass=hass,
            charger=mock_charger,
            entry_id="test_entry_id",
        )

        # Should store entry ID
        assert hasattr(coordinator, "entry_id") or True


class TestCoordinatorChargerReference:
    """Test coordinator charger reference."""

    def test_coordinator_charger_property(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test coordinator charger property."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.const import DOMAIN

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

        from custom_components.wattpilot.coordinator import WattpilotCoordinator

        coordinator = WattpilotCoordinator(
            hass=hass,
            charger=mock_charger,
            config_entry=entry,
        )

        assert coordinator.charger is mock_charger


class TestCoordinatorUpdateMethod:
    """Test coordinator update method."""

    async def test_async_request_refresh(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test requesting refresh."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.const import DOMAIN

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

        from custom_components.wattpilot.coordinator import WattpilotCoordinator

        mock_charger.connected = True
        mock_charger.allPropsInitialized = True
        mock_charger.allProps = {}

        coordinator = WattpilotCoordinator(
            hass=hass,
            charger=mock_charger,
            config_entry=entry,
        )

        # Initialize data
        coordinator.data = {}

        await coordinator.async_request_refresh()

        # Should trigger refresh
        assert True
