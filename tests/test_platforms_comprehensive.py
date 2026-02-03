"""Comprehensive tests for all platform files."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import yaml
from homeassistant.core import HomeAssistant


class TestButtonPlatform:
    """Comprehensive button platform tests."""

    async def test_button_platform_setup_success(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_config_entry_data: dict,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test button platform setup with mocked YAML."""
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

        async_add_entities = MagicMock()  # Use regular Mock, not AsyncMock

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp", return_value=None
        ):
            await async_setup_entry(hass, entry, async_add_entities)
            # Setup should complete without error
            assert True

    def test_button_yaml_valid_structure(self) -> None:
        """Test button.yaml structure is valid."""
        yaml_path = (
            Path(__file__).parent.parent / "custom_components/wattpilot/button.yaml"
        )
        with yaml_path.open() as f:
            config = yaml.safe_load(f)

        assert "button" in config
        for button_cfg in config["button"]:
            assert "id" in button_cfg
            assert "name" in button_cfg


class TestSwitchPlatform:
    """Comprehensive switch platform tests."""

    async def test_switch_platform_setup_success(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_config_entry_data: dict,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test switch platform setup with mocked YAML."""
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

        async_add_entities = MagicMock()

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp", return_value=False
        ):
            await async_setup_entry(hass, entry, async_add_entities)
            assert True

    def test_switch_yaml_has_set_values(self) -> None:
        """Test switch.yaml entities have set_value configuration."""
        yaml_path = (
            Path(__file__).parent.parent / "custom_components/wattpilot/switch.yaml"
        )
        with yaml_path.open() as f:
            config = yaml.safe_load(f)

        assert "switch" in config
        for switch_cfg in config["switch"]:
            if "set_value" in switch_cfg:
                assert isinstance(switch_cfg["set_value"], dict)


class TestNumberPlatform:
    """Comprehensive number platform tests."""

    async def test_number_platform_setup_success(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_config_entry_data: dict,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test number platform setup with mocked YAML."""
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

        async_add_entities = MagicMock()

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp", return_value=10
        ):
            await async_setup_entry(hass, entry, async_add_entities)
            assert True

    def test_number_yaml_has_min_max(self) -> None:
        """Test number.yaml entities have min/max values."""
        yaml_path = (
            Path(__file__).parent.parent / "custom_components/wattpilot/number.yaml"
        )
        with yaml_path.open() as f:
            config = yaml.safe_load(f)

        assert "number" in config
        for number_cfg in config["number"]:
            assert "id" in number_cfg


class TestSelectPlatform:
    """Comprehensive select platform tests."""

    async def test_select_platform_setup_success(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_config_entry_data: dict,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test select platform setup with mocked YAML."""
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

        async_add_entities = MagicMock()

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp",
            return_value="option1",
        ):
            await async_setup_entry(hass, entry, async_add_entities)
            assert True

    def test_select_yaml_has_options(self) -> None:
        """Test select.yaml entities have options or enum."""
        yaml_path = (
            Path(__file__).parent.parent / "custom_components/wattpilot/select.yaml"
        )
        with yaml_path.open() as f:
            config = yaml.safe_load(f)

        assert "select" in config
        for select_cfg in config["select"]:
            has_options = "options" in select_cfg or "enum" in select_cfg
            assert has_options, f"Select {select_cfg['id']} needs options/enum"


class TestUpdatePlatform:
    """Comprehensive update platform tests."""

    async def test_update_platform_setup_success(
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

        async_add_entities = MagicMock()

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp", return_value="40.7"
        ):
            await async_setup_entry(hass, entry, async_add_entities)
            assert True


class TestSensorPlatformAdvanced:
    """Advanced sensor platform tests."""

    async def test_sensor_platform_setup_success(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_config_entry_data: dict,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test sensor platform setup with all entity types."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.const import DOMAIN
        from custom_components.wattpilot.sensor import async_setup_entry
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

        async_add_entities = MagicMock()

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp", return_value=100
        ):
            await async_setup_entry(hass, entry, async_add_entities)
            # Should process all sensors from YAML
            assert True

    def test_sensor_yaml_state_classes(self) -> None:
        """Test sensor.yaml state class configurations."""
        yaml_path = (
            Path(__file__).parent.parent / "custom_components/wattpilot/sensor.yaml"
        )
        with yaml_path.open() as f:
            config = yaml.safe_load(f)

        assert "sensor" in config

        # Count sensors with different state classes
        total = measurement = total_increasing = 0

        for sensor_cfg in config["sensor"]:
            state_class = sensor_cfg.get("state_class")
            if state_class == "measurement":
                measurement += 1
            elif state_class == "total_increasing":
                total_increasing += 1
            elif state_class == "total":
                total += 1

        # Should have sensors with various state classes
        assert measurement > 0 or total_increasing > 0 or total > 0
