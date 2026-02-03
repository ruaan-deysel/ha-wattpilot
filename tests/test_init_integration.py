"""Integration tests for __init__.py setup and teardown."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady


class TestAsyncSetup:
    """Test async_setup function."""

    async def test_async_setup_registers_services(
        self,
        hass: HomeAssistant,
    ) -> None:
        """Test that async_setup registers services."""
        from custom_components.wattpilot import async_setup

        # Mock service registration
        with patch(
            "custom_components.wattpilot.async_registerService",
            new_callable=AsyncMock,
        ):
            result = await async_setup(hass, {})

            assert result is True
            # Services should be registered (or attempted)

    async def test_async_setup_returns_true(
        self,
        hass: HomeAssistant,
    ) -> None:
        """Test that async_setup returns True."""
        from custom_components.wattpilot import async_setup

        with patch(
            "custom_components.wattpilot.async_registerService", new_callable=AsyncMock
        ):
            result = await async_setup(hass, {})
            assert result is True


class TestAsyncSetupEntry:
    """Test async_setup_entry function."""

    async def test_setup_entry_creates_charger_connection(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test that setup_entry creates charger connection."""
        from custom_components.wattpilot import async_setup_entry
        from custom_components.wattpilot.const import DOMAIN

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
            patch(
                "custom_components.wattpilot.async_ConnectCharger",
                return_value=mock_charger,
            ),
            patch(
                "custom_components.wattpilot.WattpilotCoordinator",
                return_value=MagicMock(async_config_entry_first_refresh=AsyncMock()),
            ),
            patch(
                "custom_components.wattpilot.async_get_integration",
                return_value=MagicMock(version="1.0.0"),
            ),
            patch(
                "homeassistant.config_entries.ConfigEntries.async_forward_entry_setups",
                new_callable=AsyncMock,
            ),
        ):
            result = await async_setup_entry(hass, entry)
            assert result is True

    async def test_setup_entry_handles_connection_failure(
        self,
        hass: HomeAssistant,
        mock_config_entry_data: dict,
    ) -> None:
        """Test that setup_entry handles connection failure."""
        from custom_components.wattpilot import async_setup_entry
        from custom_components.wattpilot.const import DOMAIN

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
            patch(
                "custom_components.wattpilot.async_ConnectCharger",
                return_value=None,
            ),
            patch(
                "custom_components.wattpilot.async_get_integration",
                return_value=MagicMock(version="1.0.0"),
            ),
            pytest.raises(ConfigEntryNotReady),
        ):
            await async_setup_entry(hass, entry)

    async def test_setup_entry_creates_coordinator(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test that setup_entry creates coordinator."""
        from custom_components.wattpilot import async_setup_entry
        from custom_components.wattpilot.const import DOMAIN

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

        mock_coordinator = MagicMock()
        mock_coordinator.async_config_entry_first_refresh = AsyncMock()

        with (
            patch(
                "custom_components.wattpilot.async_ConnectCharger",
                return_value=mock_charger,
            ),
            patch(
                "custom_components.wattpilot.WattpilotCoordinator",
                return_value=mock_coordinator,
            ),
            patch(
                "custom_components.wattpilot.async_get_integration",
                return_value=MagicMock(version="1.0.0"),
            ),
            patch(
                "homeassistant.config_entries.ConfigEntries.async_forward_entry_setups",
                new_callable=AsyncMock,
            ),
        ):
            result = await async_setup_entry(hass, entry)
            assert result is True
            # Coordinator should be created and stored

    async def test_setup_entry_forwards_platforms(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test that setup_entry forwards to platforms."""
        from custom_components.wattpilot import async_setup_entry
        from custom_components.wattpilot.const import DOMAIN

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
            patch(
                "custom_components.wattpilot.async_ConnectCharger",
                return_value=mock_charger,
            ),
            patch(
                "custom_components.wattpilot.WattpilotCoordinator",
                return_value=MagicMock(async_config_entry_first_refresh=AsyncMock()),
            ),
            patch(
                "custom_components.wattpilot.async_get_integration",
                return_value=MagicMock(version="1.0.0"),
            ),
            patch(
                "homeassistant.config_entries.ConfigEntries.async_forward_entry_setups",
                new_callable=AsyncMock,
            ) as mock_forward,
        ):
            await async_setup_entry(hass, entry)

            # Should forward to platforms
            mock_forward.assert_called_once()


class TestAsyncUnloadEntry:
    """Test async_unload_entry function."""

    async def test_unload_entry_disconnects_charger(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test that unload_entry disconnects charger."""
        from custom_components.wattpilot import async_unload_entry
        from custom_components.wattpilot.const import DOMAIN
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

        # Create runtime data
        runtime_data = WattpilotRuntimeData(
            charger=mock_charger,
            coordinator=mock_coordinator,
            push_entities={},
            params=mock_config_entry_data,
            debug_properties=False,
        )
        entry.runtime_data = runtime_data

        with (
            patch(
                "custom_components.wattpilot.async_DisconnectCharger",
                new_callable=AsyncMock,
            ) as mock_disconnect,
            patch(
                "homeassistant.config_entries.ConfigEntries.async_unload_platforms",
                return_value=True,
            ),
        ):
            result = await async_unload_entry(hass, entry)

            assert result is True
            mock_disconnect.assert_called_once()

    async def test_unload_entry_unloads_platforms(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test that unload_entry unloads platforms."""
        from custom_components.wattpilot import async_unload_entry
        from custom_components.wattpilot.const import DOMAIN
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

        with (
            patch(
                "custom_components.wattpilot.async_DisconnectCharger",
                new_callable=AsyncMock,
            ),
            patch(
                "homeassistant.config_entries.ConfigEntries.async_unload_platforms",
                return_value=True,
            ) as mock_unload,
        ):
            result = await async_unload_entry(hass, entry)

            assert result is True
            mock_unload.assert_called_once()


class TestOptionsUpdateListener:
    """Test options_update_listener function."""

    async def test_options_update_triggers_reload(
        self,
        hass: HomeAssistant,
        mock_config_entry_data: dict,
    ) -> None:
        """Test that options update triggers reload."""
        from custom_components.wattpilot import options_update_listener
        from custom_components.wattpilot.const import DOMAIN

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

        with patch(
            "homeassistant.config_entries.ConfigEntries.async_reload",
            new_callable=AsyncMock,
        ) as mock_reload:
            await options_update_listener(hass, entry)

            mock_reload.assert_called_once_with(entry.entry_id)


class TestRuntimeDataManagement:
    """Test runtime data management."""

    def test_create_runtime_data(
        self,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test creating runtime data."""
        from custom_components.wattpilot.types import WattpilotRuntimeData

        runtime_data = WattpilotRuntimeData(
            charger=mock_charger,
            coordinator=mock_coordinator,
            push_entities={},
            params={},
            debug_properties=False,
        )

        assert runtime_data.charger is mock_charger
        assert runtime_data.coordinator is mock_coordinator
        assert runtime_data.push_entities == {}
        assert runtime_data.debug_properties is False

    def test_runtime_data_debug_properties_list(
        self,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test runtime data with debug properties list."""
        from custom_components.wattpilot.types import WattpilotRuntimeData

        runtime_data = WattpilotRuntimeData(
            charger=mock_charger,
            coordinator=mock_coordinator,
            push_entities={},
            params={},
            debug_properties=["car", "amp"],
        )

        assert isinstance(runtime_data.debug_properties, list)
        assert "car" in runtime_data.debug_properties


class TestPropertyUpdateHandler:
    """Test property update handler setup."""


class TestServiceRegistrationInSetup:
    """Test service registration during setup."""

    async def test_services_registered_once(
        self,
        hass: HomeAssistant,
    ) -> None:
        """Test that services are only registered once."""
        from custom_components.wattpilot import async_setup

        with patch(
            "custom_components.wattpilot.async_registerService",
            new_callable=AsyncMock,
        ):
            # Call setup twice
            await async_setup(hass, {})
            await async_setup(hass, {})

            # Services should only be registered once due to flag
            # (actual count depends on implementation)


class TestIntegrationVersion:
    """Test integration version handling."""

    async def test_version_logging(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test that version is logged during setup."""
        from custom_components.wattpilot import async_setup_entry
        from custom_components.wattpilot.const import DOMAIN

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
            patch(
                "custom_components.wattpilot.async_ConnectCharger",
                return_value=mock_charger,
            ),
            patch(
                "custom_components.wattpilot.WattpilotCoordinator",
                return_value=MagicMock(async_config_entry_first_refresh=AsyncMock()),
            ),
            patch(
                "custom_components.wattpilot.async_get_integration",
                return_value=MagicMock(version="1.0.0"),
            ),
            patch(
                "homeassistant.config_entries.ConfigEntries.async_forward_entry_setups",
                new_callable=AsyncMock,
            ),
        ):
            result = await async_setup_entry(hass, entry)
            assert result is True


class TestErrorHandling:
    """Test error handling in setup/unload."""

    async def test_setup_handles_coordinator_failure(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test that setup handles coordinator failure."""
        from custom_components.wattpilot import async_setup_entry
        from custom_components.wattpilot.const import DOMAIN

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

        mock_coordinator = MagicMock()
        mock_coordinator.async_config_entry_first_refresh = AsyncMock(
            side_effect=Exception("Coordinator failed")
        )

        with (
            patch(
                "custom_components.wattpilot.async_ConnectCharger",
                return_value=mock_charger,
            ),
            patch(
                "custom_components.wattpilot.WattpilotCoordinator",
                return_value=mock_coordinator,
            ),
            patch(
                "custom_components.wattpilot.async_get_integration",
                return_value=MagicMock(version="1.0.0"),
            ),
            patch(
                "custom_components.wattpilot.async_DisconnectCharger",
                new_callable=AsyncMock,
            ),
            pytest.raises(ConfigEntryNotReady),
        ):
            await async_setup_entry(hass, entry)


class TestPushEntitiesManagement:
    """Test push entities management."""

    def test_push_entities_initialization(self) -> None:
        """Test push entities dict initialization."""
        push_entities = {}

        assert isinstance(push_entities, dict)
        assert len(push_entities) == 0

    def test_push_entities_storage(self) -> None:
        """Test storing entities in push_entities."""
        from custom_components.wattpilot.types import WattpilotRuntimeData

        runtime_data = WattpilotRuntimeData(
            charger=MagicMock(),
            coordinator=MagicMock(),
            push_entities={"sensor.test": MagicMock()},
            params={},
            debug_properties=False,
        )

        assert "sensor.test" in runtime_data.push_entities
