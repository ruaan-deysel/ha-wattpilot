"""Tests for number platform."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.core import HomeAssistant


class TestNumberYamlConfiguration:
    """Test number YAML configuration."""

    def test_number_yaml_loads_successfully(self) -> None:
        """Test that number.yaml loads without errors."""
        from pathlib import Path

        import yaml

        yaml_path = (
            Path(__file__).parent.parent / "custom_components/wattpilot/number.yaml"
        )
        with yaml_path.open() as f:
            config = yaml.safe_load(f)

        assert "number" in config
        assert isinstance(config["number"], list)
        assert len(config["number"]) > 0

    def test_all_numbers_have_required_fields(self) -> None:
        """Test all numbers have required fields."""
        from pathlib import Path

        import yaml

        yaml_path = (
            Path(__file__).parent.parent / "custom_components/wattpilot/number.yaml"
        )
        with yaml_path.open() as f:
            config = yaml.safe_load(f)

        required_fields = ["id", "name"]
        for number in config["number"]:
            for field in required_fields:
                assert field in number, f"Number missing {field}: {number.get('id')}"


class TestNumberPlatformSetup:
    """Test number platform setup."""

    async def test_async_setup_entry(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_config_entry_data: dict,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test number platform setup."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.const import DOMAIN
        from custom_components.wattpilot.number import async_setup_entry
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

        async_add_entities = AsyncMock()

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp",
            return_value=10.0,
        ):
            await async_setup_entry(hass, entry, async_add_entities)
            assert async_add_entities.called


class TestWattpilotNumber:
    """Test WattpilotNumber entity."""

    async def test_number_set_value(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_config_entry_data: dict,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test number set value."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.const import DOMAIN
        from custom_components.wattpilot.number import ChargerNumber
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

        entity_cfg = {
            "id": "test_number_id",
            "name": "Test Number",
            "source": "property",
            "namespace_id": 0,
            "default_state": 0,
            "native_min_value": 0,
            "native_max_value": 100,
            "native_step": 1,
        }

        with (
            patch(
                "custom_components.wattpilot.entities.GetChargerProp",
                return_value=50.0,
            ),
            patch(
                "custom_components.wattpilot.number.async_SetChargerProp"
            ) as mock_set,
        ):
            number = ChargerNumber(hass, entry, entity_cfg, mock_charger)
            await number.async_set_native_value(75.0)
            mock_set.assert_called_once()

    def test_number_native_value_property(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_config_entry_data: dict,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test number native_value property."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.const import DOMAIN
        from custom_components.wattpilot.number import ChargerNumber
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

        entity_cfg = {
            "id": "test_number_id",
            "name": "Test Number",
            "source": "property",
            "namespace_id": 0,
            "default_state": 0,
            "native_min_value": 0,
            "native_max_value": 100,
            "native_step": 1,
        }

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp",
            return_value=42.0,
        ):
            number = ChargerNumber(hass, entry, entity_cfg, mock_charger)
            mock_coordinator.data = {"test": 42.0}
            # The native_value should come from the coordinator data
            assert number.native_value is not None
