"""Tests for switch platform."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.core import HomeAssistant


class TestSwitchYamlConfiguration:
    """Test switch YAML configuration."""

    def test_switch_yaml_loads_successfully(self) -> None:
        """Test that switch.yaml loads without errors."""
        from pathlib import Path

        import yaml

        yaml_path = (
            Path(__file__).parent.parent / "custom_components/wattpilot/switch.yaml"
        )
        with yaml_path.open() as f:
            config = yaml.safe_load(f)

        assert "switch" in config
        assert isinstance(config["switch"], list)
        assert len(config["switch"]) > 0

    def test_all_switches_have_required_fields(self) -> None:
        """Test all switches have required fields."""
        from pathlib import Path

        import yaml

        yaml_path = (
            Path(__file__).parent.parent / "custom_components/wattpilot/switch.yaml"
        )
        with yaml_path.open() as f:
            config = yaml.safe_load(f)

        required_fields = ["id", "name"]
        for switch in config["switch"]:
            for field in required_fields:
                assert field in switch, f"Switch missing {field}: {switch.get('id')}"

    def test_switch_ids_are_unique(self) -> None:
        """Test all switch IDs are unique."""
        from pathlib import Path

        import yaml

        yaml_path = (
            Path(__file__).parent.parent / "custom_components/wattpilot/switch.yaml"
        )
        with yaml_path.open() as f:
            config = yaml.safe_load(f)

        switch_ids = [s["id"] for s in config["switch"]]
        assert len(switch_ids) == len(set(switch_ids)), "Duplicate switch IDs found"


class TestSwitchPlatformSetup:
    """Test switch platform setup."""

    async def test_async_setup_entry(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_config_entry_data: dict,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test switch platform setup."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.const import DOMAIN
        from custom_components.wattpilot.switch import async_setup_entry
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
            return_value="test_value",
        ):
            await async_setup_entry(hass, entry, async_add_entities)
            # At least one entity should be added
            assert async_add_entities.called


class TestWattpilotSwitch:
    """Test WattpilotSwitch entity."""

    async def test_switch_turn_on(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_config_entry_data: dict,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test switch turn on."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.const import DOMAIN
        from custom_components.wattpilot.switch import ChargerSwitch
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
            "id": "test_switch_id",
            "name": "Test Switch",
            "source": "property",
            "namespace_id": 0,
            "default_state": False,
            "set_value": {"on": True, "off": False},
        }

        with (
            patch(
                "custom_components.wattpilot.entities.GetChargerProp",
                return_value=False,
            ),
            patch(
                "custom_components.wattpilot.switch.async_SetChargerProp"
            ) as mock_set,
        ):
            switch = ChargerSwitch(hass, entry, entity_cfg, mock_charger)
            await switch.async_turn_on()
            mock_set.assert_called_once()

    async def test_switch_turn_off(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_config_entry_data: dict,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test switch turn off."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.const import DOMAIN
        from custom_components.wattpilot.switch import ChargerSwitch
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
            "id": "test_switch_id",
            "name": "Test Switch",
            "source": "property",
            "namespace_id": 0,
            "default_state": False,
            "set_value": {"on": True, "off": False},
        }

        with (
            patch(
                "custom_components.wattpilot.entities.GetChargerProp",
                return_value=True,
            ),
            patch(
                "custom_components.wattpilot.switch.async_SetChargerProp"
            ) as mock_set,
        ):
            switch = ChargerSwitch(hass, entry, entity_cfg, mock_charger)
            await switch.async_turn_off()
            mock_set.assert_called_once()

    def test_switch_is_on_property(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_config_entry_data: dict,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test switch is_on property."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.const import DOMAIN
        from custom_components.wattpilot.switch import ChargerSwitch
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
            "id": "test_switch_id",
            "name": "Test Switch",
            "source": "property",
            "namespace_id": 0,
            "default_state": False,
            "set_value": {"on": True, "off": False},
        }

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp",
            return_value=True,
        ):
            switch = ChargerSwitch(hass, entry, entity_cfg, mock_charger)
            mock_coordinator.data = {"test": True}
            assert switch.is_on is True
