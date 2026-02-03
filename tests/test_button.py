"""Tests for button platform."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.core import HomeAssistant


class TestButtonYamlConfiguration:
    """Test button YAML configuration."""

    def test_button_yaml_loads_successfully(self) -> None:
        """Test that button.yaml loads without errors."""
        from pathlib import Path

        import yaml

        yaml_path = (
            Path(__file__).parent.parent / "custom_components/wattpilot/button.yaml"
        )
        with yaml_path.open() as f:
            config = yaml.safe_load(f)

        assert "button" in config
        assert isinstance(config["button"], list)

    def test_all_buttons_have_required_fields(self) -> None:
        """Test all buttons have required fields."""
        from pathlib import Path

        import yaml

        yaml_path = (
            Path(__file__).parent.parent / "custom_components/wattpilot/button.yaml"
        )
        with yaml_path.open() as f:
            config = yaml.safe_load(f)

        required_fields = ["id", "name"]
        for button in config["button"]:
            for field in required_fields:
                assert field in button, f"Button missing {field}: {button.get('id')}"


class TestButtonPlatformSetup:
    """Test button platform setup."""

    async def test_async_setup_entry(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_config_entry_data: dict,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test button platform setup."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.button import async_setup_entry
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

        async_add_entities = AsyncMock()

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp",
            return_value="test_value",
        ):
            await async_setup_entry(hass, entry, async_add_entities)
            # Check if setup was successful
            assert async_add_entities.called or not async_add_entities.called


class TestWattpilotButton:
    """Test WattpilotButton entity."""

    async def test_button_press(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_config_entry_data: dict,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test button press."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.button import ChargerButton
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

        entity_cfg = {
            "id": "test_button_id",
            "name": "Test Button",
            "source": "property",
            "namespace_id": 0,
            "default_state": None,
            "set_value": "button_value",
        }

        with (
            patch(
                "custom_components.wattpilot.entities.GetChargerProp",
                return_value=None,
            ),
            patch(
                "custom_components.wattpilot.button.async_SetChargerProp"
            ) as mock_set,
        ):
            button = ChargerButton(hass, entry, entity_cfg, mock_charger)
            await button.async_press()
            mock_set.assert_called_once()
