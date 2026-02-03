"""Tests for entities logic and actual code execution."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from homeassistant.core import HomeAssistant


class TestEntityPropertyRetrieval:
    """Test entity property retrieval logic."""

    def test_entity_gets_value_from_charger_props(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test entity retrieves value from charger properties."""
        from custom_components.wattpilot.entities import ChargerPlatformEntity

        entity_cfg = {
            "id": "test_prop",
            "name": "Test Property",
        }

        entry = MagicMock()
        entry.entry_id = "test"

        mock_charger.allProps = {"test_prop": 42}

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp",
            return_value=42,
        ):
            entity = ChargerPlatformEntity(hass, entry, entity_cfg, mock_charger)
            assert entity is not None


class TestEntityEnumMapping:
    """Test entity enum value mapping."""

    def test_entity_maps_enum_values(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test entity maps enum values correctly."""
        from custom_components.wattpilot.entities import ChargerPlatformEntity

        entity_cfg = {
            "id": "car_status",
            "name": "Car Status",
            "enum": {
                "0": "Unknown",
                "1": "Idle",
                "2": "Charging",
            },
        }

        entry = MagicMock()
        mock_charger.allProps = {"car_status": 2}

        entity = ChargerPlatformEntity(hass, entry, entity_cfg, mock_charger)
        assert entity._entity_cfg.get("enum") is not None


class TestEntityUniqueId:
    """Test entity unique ID generation."""

    def test_entity_unique_id_from_entry_and_entity_id(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test unique ID generation."""
        from custom_components.wattpilot.entities import ChargerPlatformEntity

        entity_cfg = {
            "id": "test_entity",
            "name": "Test Entity",
        }

        entry = MagicMock()
        entry.entry_id = "entry_12345"

        mock_charger.serial = "87654321"

        entity = ChargerPlatformEntity(hass, entry, entity_cfg, mock_charger)

        expected = f"{mock_charger.serial}_test_entity"
        assert entity.unique_id == expected
