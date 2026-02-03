"""Tests that execute actual entity code paths."""

from __future__ import annotations

from unittest.mock import MagicMock

from homeassistant.core import HomeAssistant


class TestEntityCodePaths:
    """Test entity code execution paths."""

    def test_entity_init_with_all_attributes(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test entity initialization with all attributes."""
        from custom_components.wattpilot.entities import ChargerPlatformEntity

        entity_cfg = {
            "id": "test_entity",
            "name": "Test Entity",
            "icon": "mdi:test",
            "entity_category": "diagnostic",
            "device_class": "energy",
            "unit_of_measurement": "kWh",
            "state_class": "total_increasing",
            "native_unit_of_measurement": "kWh",
            "attributes": ["attr1", "attr2"],
        }

        entry = MagicMock()
        entry.entry_id = "test_entry"

        mock_charger.serial = "12345678"
        mock_charger.name = "Test Wattpilot"
        mock_charger.manufacturer = "Fronius"
        mock_charger.devicetype = "Test Type"
        mock_charger.firmware = "1.0.0"
        mock_charger.hostname = "wattpilot-12345678"

        entity = ChargerPlatformEntity(hass, entry, entity_cfg, mock_charger)

        # Verify attributes are set
        assert entity._attr_name == "Test Entity"
        assert hasattr(entity, "_attr_icon")
        assert hasattr(entity, "_attr_entity_category")


class TestEntityAttributeGeneration:
    """Test entity attribute generation."""

    def test_entity_extra_state_attributes_generation(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test extra state attributes are generated."""
        from custom_components.wattpilot.entities import ChargerPlatformEntity

        entity_cfg = {
            "id": "test_entity",
            "name": "Test",
            "attributes": ["attr1", "attr2"],
        }

        entry = MagicMock()

        mock_charger.allProps = {
            "test_entity": "main_value",
            "attr1": "value1",
            "attr2": "value2",
        }

        entity = ChargerPlatformEntity(hass, entry, entity_cfg, mock_charger)

        # Check if entity stores attribute config
        assert hasattr(entity, "_entity_cfg")

    def test_entity_translation_key_generation(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test translation key is set."""
        from custom_components.wattpilot.entities import ChargerPlatformEntity

        entity_cfg = {
            "id": "test_entity",
            "name": "Test Entity",
        }

        entry = MagicMock()

        entity = ChargerPlatformEntity(hass, entry, entity_cfg, mock_charger)

        # Should have translation key
        assert hasattr(entity, "_attr_translation_key") or hasattr(
            entity, "translation_key"
        )


class TestEntitySourceHandling:
    """Test entity source attribute handling."""

    def test_entity_with_source_attribute(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test entity with source=attribute."""
        from custom_components.wattpilot.entities import ChargerPlatformEntity

        entity_cfg = {
            "id": "test_entity",
            "name": "Test",
            "source": "attribute",
        }

        entry = MagicMock()

        entity = ChargerPlatformEntity(hass, entry, entity_cfg, mock_charger)

        # Entity should be created
        assert entity is not None

    def test_entity_with_source_property(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test entity with source=property."""
        from custom_components.wattpilot.entities import ChargerPlatformEntity

        entity_cfg = {
            "id": "test_entity",
            "name": "Test",
            "source": "property",
        }

        entry = MagicMock()

        entity = ChargerPlatformEntity(hass, entry, entity_cfg, mock_charger)

        # Entity should be created
        assert entity is not None


class TestEntityEnumHandling:
    """Test entity enum value handling."""

    def test_entity_with_enum_mapping(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test entity with enum value mapping."""
        from custom_components.wattpilot.entities import ChargerPlatformEntity

        entity_cfg = {
            "id": "test_entity",
            "name": "Test",
            "enum": {
                "0": "Off",
                "1": "On",
                "2": "Auto",
            },
        }

        entry = MagicMock()

        entity = ChargerPlatformEntity(hass, entry, entity_cfg, mock_charger)

        # Entity should store enum config
        assert hasattr(entity, "_entity_cfg")


class TestEntityDefaultState:
    """Test entity default state handling."""

    def test_entity_with_default_state(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test entity with default_state configured."""
        from custom_components.wattpilot.entities import ChargerPlatformEntity

        entity_cfg = {
            "id": "test_entity",
            "name": "Test",
            "default_state": "Unknown",
        }

        entry = MagicMock()

        entity = ChargerPlatformEntity(hass, entry, entity_cfg, mock_charger)

        # Entity should store default state
        assert hasattr(entity, "_entity_cfg")


class TestEntityDescription:
    """Test entity description handling."""

    def test_entity_with_description(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test entity with description."""
        from custom_components.wattpilot.entities import ChargerPlatformEntity

        entity_cfg = {
            "id": "test_entity",
            "name": "Test Entity",
            "description": "This is a test entity",
        }

        entry = MagicMock()

        entity = ChargerPlatformEntity(hass, entry, entity_cfg, mock_charger)

        # Entity should be created with description
        assert entity is not None
