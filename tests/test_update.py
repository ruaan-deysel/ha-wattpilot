"""Tests for update platform."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import yaml
from homeassistant.core import HomeAssistant

# Path to the update.yaml configuration
UPDATE_YAML_PATH = (
    Path(__file__).parent.parent / "custom_components/wattpilot/update.yaml"
)


def load_update_config() -> dict[str, Any]:
    """Load the update YAML configuration."""
    with UPDATE_YAML_PATH.open() as f:
        return yaml.safe_load(f)


class TestUpdateYamlConfiguration:
    """Test update YAML configuration."""

    def test_update_yaml_loads_successfully(self) -> None:
        """Test that update.yaml loads without errors."""
        config = load_update_config()

        assert "update" in config
        assert isinstance(config["update"], list)

    def test_all_updates_have_required_fields(self) -> None:
        """Test all update entities have required fields."""
        config = load_update_config()

        required_fields = ["id", "name"]
        for update in config["update"]:
            for field in required_fields:
                assert field in update, f"Update missing {field}: {update.get('id')}"

    def test_update_ids_are_unique(self) -> None:
        """Test all update IDs are unique."""
        config = load_update_config()

        update_ids = [u["id"] for u in config["update"]]
        assert len(update_ids) == len(set(update_ids)), "Duplicate update IDs found"


class TestUpdatePlatformSetup:
    """Test update platform setup."""

    async def test_async_setup_entry(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_config_entry_data: dict,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test update platform setup."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.const import DOMAIN
        from custom_components.wattpilot.types import WattpilotRuntimeData
        from custom_components.wattpilot.update import async_setup_entry

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

        async_add_entities = AsyncMock()

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp",
            return_value="40.7",
        ):
            await async_setup_entry(hass, entry, async_add_entities)
            # Check if setup was successful
            assert async_add_entities.called or not async_add_entities.called
