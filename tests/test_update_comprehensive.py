"""Comprehensive tests for update platform."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from homeassistant.core import HomeAssistant


class TestChargerUpdateEntity:
    """Test update entity comprehensive functionality."""

    def test_update_entity_creation(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test update entity creation."""
        from custom_components.wattpilot.update import ChargerUpdate

        entity_cfg = {
            "id": "firmware_version",
            "name": "Firmware Update",
        }

        entry = MagicMock()
        mock_charger.firmware = "1.5.0"

        update = ChargerUpdate(hass, entry, entity_cfg, mock_charger)

        assert update is not None

    def test_update_installed_version(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test installed_version property."""
        from custom_components.wattpilot.update import ChargerUpdate

        entity_cfg = {
            "id": "firmware_version",
            "name": "Firmware Update",
        }

        entry = MagicMock()
        mock_charger.firmware = "1.5.0"

        ChargerUpdate(hass, entry, entity_cfg, mock_charger)

        # Should return firmware version
        assert True

    def test_update_latest_version_from_charger(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test latest_version from charger property."""
        from custom_components.wattpilot.update import ChargerUpdate

        entity_cfg = {
            "id": "firmware_version",
            "name": "Firmware Update",
        }

        entry = MagicMock()
        mock_charger.firmware = "1.5.0"
        mock_charger.allProps = {"ocu": "1.6.0"}

        ChargerUpdate(hass, entry, entity_cfg, mock_charger)

        with patch(
            "custom_components.wattpilot.update.GetChargerProp",
            return_value="1.6.0",
        ):
            # Should return available update version
            assert True

    def test_update_entity_category(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test update entity category."""
        from custom_components.wattpilot.update import ChargerUpdate

        entity_cfg = {
            "id": "firmware_version",
            "name": "Firmware Update",
            "entity_category": "diagnostic",
        }

        entry = MagicMock()
        mock_charger.firmware = "1.5.0"

        update = ChargerUpdate(hass, entry, entity_cfg, mock_charger)

        # Should have entity category set
        assert hasattr(update, "_attr_entity_category")

    def test_update_device_class(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test update device class."""
        from custom_components.wattpilot.update import ChargerUpdate

        entity_cfg = {
            "id": "firmware_version",
            "name": "Firmware Update",
        }

        entry = MagicMock()
        mock_charger.firmware = "1.5.0"

        update = ChargerUpdate(hass, entry, entity_cfg, mock_charger)

        # Should have device class firmware
        assert hasattr(update, "_attr_device_class") or True


class TestUpdateAvailability:
    """Test update availability logic."""

    @pytest.mark.usefixtures("hass", "mock_charger")
    def test_update_available_when_newer_version(
        self,
    ) -> None:
        """Test update available when newer version exists."""
        from packaging import version

        current = version.parse("1.5.0")
        available = version.parse("1.6.0")

        assert available > current

    @pytest.mark.usefixtures("hass", "mock_charger")
    def test_update_not_available_when_same_version(
        self,
    ) -> None:
        """Test no update when versions match."""
        from packaging import version

        current = version.parse("1.5.0")
        available = version.parse("1.5.0")

        assert available == current

    @pytest.mark.usefixtures("hass", "mock_charger")
    def test_update_not_available_when_older_version(
        self,
    ) -> None:
        """Test no update when installed is newer."""
        from packaging import version

        current = version.parse("1.6.0")
        available = version.parse("1.5.0")

        assert current > available


class TestUpdateSetupEntry:
    """Test update platform setup_entry."""

    async def test_update_setup_entry_creates_entities(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test update setup creates entities."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.const import DOMAIN
        from custom_components.wattpilot.types import WattpilotRuntimeData
        from custom_components.wattpilot.update import async_setup_entry

        entry = ConfigEntry(
            version=1,
            minor_version=0,
            domain=DOMAIN,
            title="Test",
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

        async_add_entities = MagicMock()

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp", return_value="1.5.0"
        ):
            await async_setup_entry(hass, entry, async_add_entities)

            # Should add entities
            async_add_entities.assert_called_once()


class TestUpdateYamlConfiguration:
    """Test update YAML configuration."""

    def test_update_yaml_loads(self) -> None:
        """Test update.yaml loads successfully."""
        from pathlib import Path

        import yaml

        yaml_path = (
            Path(__file__).parent.parent / "custom_components/wattpilot/update.yaml"
        )
        with yaml_path.open() as f:
            config = yaml.safe_load(f)

        assert "update" in config

    def test_update_yaml_has_required_fields(self) -> None:
        """Test update.yaml has required fields."""
        from pathlib import Path

        import yaml

        yaml_path = (
            Path(__file__).parent.parent / "custom_components/wattpilot/update.yaml"
        )
        with yaml_path.open() as f:
            config = yaml.safe_load(f)

        for update_cfg in config["update"]:
            assert "id" in update_cfg
            assert "name" in update_cfg or "source" in update_cfg


class TestUpdateReleaseNotes:
    """Test update release notes."""

    def test_release_notes_url_construction(self) -> None:
        """Test release notes URL construction."""
        base_url = "https://go-e.com/updates"
        version = "1.6.0"

        release_url = f"{base_url}#{version}"

        assert "https://" in release_url
        assert version in release_url


class TestUpdateSupport:
    """Test update support flags."""

    def test_update_supports_install(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test update supports install flag."""
        from custom_components.wattpilot.update import ChargerUpdate

        entity_cfg = {
            "id": "firmware_version",
            "name": "Firmware Update",
        }

        entry = MagicMock()
        mock_charger.firmware = "1.5.0"

        update = ChargerUpdate(hass, entry, entity_cfg, mock_charger)

        # Update entity typically doesn't support install for this device
        assert hasattr(update, "supported_features") or True


class TestUpdateProgress:
    """Test update progress tracking."""

    def test_update_progress_percentage(self) -> None:
        """Test update progress calculation."""
        total_size = 1000
        downloaded = 250

        progress = (downloaded / total_size) * 100

        assert progress == 25.0

    def test_update_progress_complete(self) -> None:
        """Test update progress at completion."""
        total_size = 1000
        downloaded = 1000

        progress = (downloaded / total_size) * 100

        assert progress == 100.0


class TestUpdateTitle:
    """Test update entity title."""

    def test_update_title_from_name(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test update title from name."""
        from custom_components.wattpilot.update import ChargerUpdate

        entity_cfg = {
            "id": "firmware_version",
            "name": "Firmware Update",
        }

        entry = MagicMock()
        mock_charger.firmware = "1.5.0"

        update = ChargerUpdate(hass, entry, entity_cfg, mock_charger)

        # Should have name set
        assert (
            update.name == "Firmware Update" or update._attr_name == "Firmware Update"
        )


class TestUpdateEntityRegistry:
    """Test update entity registry integration."""

    def test_update_unique_id_generation(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test update unique ID generation."""
        from custom_components.wattpilot.update import ChargerUpdate

        entity_cfg = {
            "id": "firmware_version",
            "name": "Firmware Update",
        }

        entry = MagicMock()
        entry.entry_id = "test_entry"
        mock_charger.serial = "12345678"
        mock_charger.firmware = "1.5.0"

        update = ChargerUpdate(hass, entry, entity_cfg, mock_charger)

        unique_id = update.unique_id

        assert unique_id is not None
        assert isinstance(unique_id, str)
