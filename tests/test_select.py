"""Tests for select platform."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.core import HomeAssistant


class TestSelectYamlConfiguration:
    """Test select YAML configuration."""

    def test_select_yaml_loads_successfully(self) -> None:
        """Test that select.yaml loads without errors."""
        from pathlib import Path

        import yaml

        yaml_path = (
            Path(__file__).parent.parent / "custom_components/wattpilot/select.yaml"
        )
        with yaml_path.open() as f:
            config = yaml.safe_load(f)

        assert "select" in config
        assert isinstance(config["select"], list)
        assert len(config["select"]) > 0

    def test_all_selects_have_required_fields(self) -> None:
        """Test all selects have required fields."""
        from pathlib import Path

        import yaml

        yaml_path = (
            Path(__file__).parent.parent / "custom_components/wattpilot/select.yaml"
        )
        with yaml_path.open() as f:
            config = yaml.safe_load(f)

        required_fields = ["id", "name"]
        for select in config["select"]:
            for field in required_fields:
                assert field in select, f"Select missing {field}: {select.get('id')}"

    def test_all_selects_have_options(self) -> None:
        """Test all selects have options defined."""
        from pathlib import Path

        import yaml

        yaml_path = (
            Path(__file__).parent.parent / "custom_components/wattpilot/select.yaml"
        )
        with yaml_path.open() as f:
            config = yaml.safe_load(f)

        for select in config["select"]:
            assert "options" in select or "enum" in select, (
                f"Select missing options: {select.get('id')}"
            )


class TestSelectPlatformSetup:
    """Test select platform setup."""

    async def test_async_setup_entry(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_config_entry_data: dict,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test select platform setup."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.const import DOMAIN
        from custom_components.wattpilot.select import async_setup_entry
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
            return_value="option1",
        ):
            await async_setup_entry(hass, entry, async_add_entities)
            assert async_add_entities.called


class TestWattpilotSelect:
    """Test WattpilotSelect entity."""

    async def test_select_set_option(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_config_entry_data: dict,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test select set option."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.const import DOMAIN
        from custom_components.wattpilot.select import ChargerSelect
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
            "id": "test_select_id",
            "name": "Test Select",
            "source": "property",
            "namespace_id": 0,
            "default_state": "option1",
            "options": ["option1", "option2", "option3"],
        }

        with (
            patch(
                "custom_components.wattpilot.entities.GetChargerProp",
                return_value="option1",
            ),
            patch(
                "custom_components.wattpilot.select.async_SetChargerProp"
            ) as mock_set,
        ):
            select = ChargerSelect(hass, entry, entity_cfg, mock_charger)
            await select.async_select_option("option2")
            mock_set.assert_called_once()

    def test_select_current_option_property(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_config_entry_data: dict,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test select current_option property."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.const import DOMAIN
        from custom_components.wattpilot.select import ChargerSelect
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
            "id": "test_select_id",
            "name": "Test Select",
            "source": "property",
            "namespace_id": 0,
            "default_state": "option1",
            "options": ["option1", "option2", "option3"],
        }

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp",
            return_value="option2",
        ):
            select = ChargerSelect(hass, entry, entity_cfg, mock_charger)
            mock_coordinator.data = {"test": "option2"}
            # The current_option should be available
            assert select.current_option is not None
