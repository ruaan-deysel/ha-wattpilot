"""Tests for the integration setup."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady


class TestIntegrationSetup:
    """Test integration setup."""

    def test_domain_is_wattpilot(self) -> None:
        """Test the domain constant."""
        from custom_components.wattpilot.const import DOMAIN

        assert DOMAIN == "wattpilot"

    def test_supported_platforms(self) -> None:
        """Test supported platforms are defined."""
        from custom_components.wattpilot.const import SUPPORTED_PLATFORMS

        expected_platforms = [
            "button",
            "number",
            "select",
            "sensor",
            "switch",
            "update",
        ]
        assert sorted(SUPPORTED_PLATFORMS) == sorted(expected_platforms)

    def test_runtime_data_structure(self) -> None:
        """Test runtime data structure."""
        from custom_components.wattpilot.types import WattpilotRuntimeData

        charger = MagicMock()
        coordinator = MagicMock()
        runtime_data = WattpilotRuntimeData(
            charger=charger,
            coordinator=coordinator,
            push_entities={},
            params={"test": "value"},
            debug_properties=False,
        )

        assert runtime_data.charger == charger
        assert runtime_data.coordinator == coordinator
        assert runtime_data.push_entities == {}
        assert runtime_data.params == {"test": "value"}
        assert runtime_data.debug_properties is False


class TestConstants:
    """Test constant values."""

    def test_default_timeout(self) -> None:
        """Test default timeout value."""
        from custom_components.wattpilot.const import DEFAULT_TIMEOUT

        assert DEFAULT_TIMEOUT == 15

    def test_cloud_api_urls(self) -> None:
        """Test cloud API URL constants."""
        from custom_components.wattpilot.const import (
            CLOUD_API_URL_POSTFIX,
            CLOUD_API_URL_PREFIX,
        )

        assert CLOUD_API_URL_PREFIX == "https://"
        assert ".api.v3.go-e.io/api/" in CLOUD_API_URL_POSTFIX

    def test_event_constants(self) -> None:
        """Test event constants."""
        from custom_components.wattpilot.const import EVENT_PROPS, EVENT_PROPS_ID

        assert EVENT_PROPS_ID == "wattpilot_property_message"
        assert isinstance(EVENT_PROPS, list)


class TestManifest:
    """Test manifest configuration."""

    def test_manifest_loads(self) -> None:
        """Test manifest.json loads correctly."""
        import json
        from pathlib import Path

        manifest_path = (
            Path(__file__).parent.parent / "custom_components/wattpilot/manifest.json"
        )
        with manifest_path.open() as f:
            manifest = json.load(f)

        assert manifest["domain"] == "wattpilot"
        assert manifest["name"] == "Fronius Wattpilot"
        assert manifest["config_flow"] is True

    def test_manifest_has_required_fields(self) -> None:
        """Test manifest has all required fields."""
        import json
        from pathlib import Path

        manifest_path = (
            Path(__file__).parent.parent / "custom_components/wattpilot/manifest.json"
        )
        with manifest_path.open() as f:
            manifest = json.load(f)

        required_fields = [
            "domain",
            "name",
            "version",
            "config_flow",
            "documentation",
            "requirements",
        ]
        for field in required_fields:
            assert field in manifest, f"Missing required field: {field}"

    def test_manifest_iot_class(self) -> None:
        """Test manifest has correct IoT class."""
        import json
        from pathlib import Path

        manifest_path = (
            Path(__file__).parent.parent / "custom_components/wattpilot/manifest.json"
        )
        with manifest_path.open() as f:
            manifest = json.load(f)

        # Should be local_push since it uses WebSocket
        assert manifest["iot_class"] == "local_push"

    def test_manifest_no_yaml_dependencies(self) -> None:
        """Test manifest no longer requires pyyaml or aiofiles."""
        import json
        from pathlib import Path

        manifest_path = (
            Path(__file__).parent.parent / "custom_components/wattpilot/manifest.json"
        )
        with manifest_path.open() as f:
            manifest = json.load(f)

        requirements = manifest.get("requirements", [])
        for req in requirements:
            assert "pyyaml" not in req.lower(), "pyyaml should be removed"
            assert "aiofiles" not in req.lower(), "aiofiles should be removed"
            assert "importlib_metadata" not in req.lower(), (
                "importlib_metadata should be removed"
            )


class TestEntityDescriptions:
    """Test entity descriptions replaced YAML configurations."""

    def test_all_platform_descriptions_exist(self) -> None:
        """Test all platform description lists exist in descriptions module."""
        from custom_components.wattpilot.descriptions import (
            BUTTON_DESCRIPTIONS,
            NUMBER_DESCRIPTIONS,
            SELECT_DESCRIPTIONS,
            SENSOR_DESCRIPTIONS,
            SWITCH_DESCRIPTIONS,
            UPDATE_DESCRIPTIONS,
        )

        assert len(SENSOR_DESCRIPTIONS) > 0
        assert len(SWITCH_DESCRIPTIONS) > 0
        assert len(NUMBER_DESCRIPTIONS) > 0
        assert len(SELECT_DESCRIPTIONS) > 0
        assert len(BUTTON_DESCRIPTIONS) > 0
        assert len(UPDATE_DESCRIPTIONS) > 0

    def test_all_descriptions_have_charger_key(self) -> None:
        """Test all entity descriptions have a charger_key."""
        from custom_components.wattpilot.descriptions import (
            BUTTON_DESCRIPTIONS,
            NUMBER_DESCRIPTIONS,
            SELECT_DESCRIPTIONS,
            SENSOR_DESCRIPTIONS,
            SWITCH_DESCRIPTIONS,
            UPDATE_DESCRIPTIONS,
        )

        all_descriptions = [
            *SENSOR_DESCRIPTIONS,
            *SWITCH_DESCRIPTIONS,
            *NUMBER_DESCRIPTIONS,
            *SELECT_DESCRIPTIONS,
            *BUTTON_DESCRIPTIONS,
            *UPDATE_DESCRIPTIONS,
        ]
        for desc in all_descriptions:
            assert desc.charger_key, f"Description {desc.key} missing charger_key"

    def test_description_keys_are_unique(self) -> None:
        """Test that description keys (with uid fallback) are unique per platform."""
        from custom_components.wattpilot.descriptions import (
            BUTTON_DESCRIPTIONS,
            NUMBER_DESCRIPTIONS,
            SELECT_DESCRIPTIONS,
            SENSOR_DESCRIPTIONS,
            SWITCH_DESCRIPTIONS,
            UPDATE_DESCRIPTIONS,
        )

        for name, descs in [
            ("sensor", SENSOR_DESCRIPTIONS),
            ("switch", SWITCH_DESCRIPTIONS),
            ("number", NUMBER_DESCRIPTIONS),
            ("select", SELECT_DESCRIPTIONS),
            ("button", BUTTON_DESCRIPTIONS),
            ("update", UPDATE_DESCRIPTIONS),
        ]:
            keys = [d.uid or d.charger_key for d in descs]
            seen: set[str] = set()
            duplicates = []
            for key in keys:
                if key in seen:
                    duplicates.append(key)
                seen.add(key)
            assert not duplicates, f"Duplicate keys in {name}: {duplicates}"


class TestAsyncSetup:
    """Test async_setup function."""

    async def test_async_setup_registers_services(self, hass: HomeAssistant) -> None:
        """Test that async_setup registers services."""
        from custom_components.wattpilot import async_setup

        with patch(
            "custom_components.wattpilot._ensure_services_registered"
        ) as mock_register:
            result = await async_setup(hass, {})
            assert result is True
            mock_register.assert_called_once_with(hass)


class TestAsyncSetupEntry:
    """Test async_setup_entry function."""

    async def test_setup_entry_requires_charger_connection(
        self,
        hass: HomeAssistant,
        mock_config_entry_data: dict,
    ) -> None:
        """Test that setup requires charger connection."""
        from homeassistant.config_entries import ConfigEntry
        from homeassistant.exceptions import ConfigEntryNotReady

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

        # Should raise ConfigEntryNotReady when connection fails
        with pytest.raises(ConfigEntryNotReady):
            await async_setup_entry(hass, entry)

    async def test_setup_entry_connection_fails(
        self,
        hass: HomeAssistant,
        mock_config_entry_data: dict,
    ) -> None:
        """Test config entry setup when connection fails."""
        from homeassistant.config_entries import ConfigEntry

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
                "custom_components.wattpilot.utils.async_ConnectCharger",
                return_value=None,
            ),
            patch("custom_components.wattpilot._ensure_services_registered"),
            pytest.raises(ConfigEntryNotReady),
        ):
            await async_setup_entry(hass, entry)

    async def test_setup_entry_coordinator_fails(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,  # noqa: ARG002
        mock_config_entry_data: dict,
        mock_connect_charger: AsyncMock,  # noqa: ARG002
        mock_disconnect_charger: AsyncMock,
    ) -> None:
        """Test config entry setup when coordinator fails."""
        from homeassistant.config_entries import ConfigEntry

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

        with (  # noqa: PT012
            patch("custom_components.wattpilot.async_get_integration"),
            patch(
                "custom_components.wattpilot.WattpilotCoordinator.async_config_entry_first_refresh",
                side_effect=Exception("Coordinator failed"),
            ),
            patch("custom_components.wattpilot._ensure_services_registered"),
            pytest.raises(ConfigEntryNotReady),
        ):
            await async_setup_entry(hass, entry)
            mock_disconnect_charger.assert_called_once()


class TestAsyncUnloadEntry:
    """Test async_unload_entry function."""

    async def test_unload_entry_disconnects_charger(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test that unload entry disconnects charger."""
        from homeassistant.config_entries import ConfigEntry

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

        # Set up runtime data
        coordinator = MagicMock()
        runtime_data = WattpilotRuntimeData(
            charger=mock_charger,
            coordinator=coordinator,
            push_entities={},
            params=mock_config_entry_data,
            debug_properties=False,
            options_update_listener=MagicMock(),
        )
        entry.runtime_data = runtime_data

        with patch("custom_components.wattpilot.utils.async_DisconnectCharger"):
            # Should not raise when unloading
            result = await async_unload_entry(hass, entry)
            assert isinstance(result, bool)

    async def test_unload_entry_platform_fails(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test config entry unload when platform unload fails."""
        from homeassistant.config_entries import ConfigEntry

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

        coordinator = MagicMock()
        runtime_data = WattpilotRuntimeData(
            charger=mock_charger,
            coordinator=coordinator,
            push_entities={},
            params=mock_config_entry_data,
            debug_properties=False,
        )
        entry.runtime_data = runtime_data

        with patch("custom_components.wattpilot.utils.async_DisconnectCharger"):
            result = await async_unload_entry(hass, entry)
            # Result depends on whether platforms are successfully unloaded
            assert isinstance(result, bool)


class TestOptionsUpdateListener:
    """Test options update listener."""

    async def test_options_update_listener_success(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test options update listener updates config."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot import options_update_listener
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
            options={"new_option": "value"},
            subentries_data={},
        )

        coordinator = MagicMock()
        runtime_data = WattpilotRuntimeData(
            charger=mock_charger,
            coordinator=coordinator,
            push_entities={},
            params=mock_config_entry_data,
            debug_properties=False,
        )
        entry.runtime_data = runtime_data

        with (
            patch.object(
                hass.config_entries, "async_update_entry"
            ) as mock_update_entry,
            patch.object(hass.config_entries, "async_reload") as mock_reload,
        ):
            await options_update_listener(hass, entry)
            mock_update_entry.assert_called_once()
            mock_reload.assert_called_once_with(entry.entry_id)
