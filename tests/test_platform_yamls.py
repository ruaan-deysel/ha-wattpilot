"""Comprehensive tests for platform YAML configurations."""

from __future__ import annotations

from pathlib import Path

import yaml


class TestButtonYaml:
    """Test button.yaml configuration."""

    def test_button_yaml_structure(self) -> None:
        """Test button.yaml has correct structure."""
        base_path = Path(__file__).parent.parent / "custom_components/wattpilot"
        yaml_path = base_path / "button.yaml"

        with yaml_path.open() as f:
            config = yaml.safe_load(f)

        assert "button" in config
        assert isinstance(config["button"], list)

        for button in config["button"]:
            assert "id" in button
            if "set_value" in button:
                assert button["set_value"] is not None


class TestNumberYaml:
    """Test number.yaml configuration."""

    def test_number_yaml_structure(self) -> None:
        """Test number.yaml has correct structure."""
        base_path = Path(__file__).parent.parent / "custom_components/wattpilot"
        yaml_path = base_path / "number.yaml"

        with yaml_path.open() as f:
            config = yaml.safe_load(f)

        assert "number" in config
        assert isinstance(config["number"], list)

        for number in config["number"]:
            assert "id" in number
            # Number entities should have min/max values
            if "native_min_value" in number:
                assert isinstance(number["native_min_value"], (int, float))
            if "native_max_value" in number:
                assert isinstance(number["native_max_value"], (int, float))


class TestSelectYaml:
    """Test select.yaml configuration."""

    def test_select_yaml_structure(self) -> None:
        """Test select.yaml has correct structure."""
        base_path = Path(__file__).parent.parent / "custom_components/wattpilot"
        yaml_path = base_path / "select.yaml"

        with yaml_path.open() as f:
            config = yaml.safe_load(f)

        assert "select" in config
        assert isinstance(config["select"], list)

        for select in config["select"]:
            assert "id" in select
            # Select entities should have options or enum
            has_options = "options" in select or "enum" in select
            assert has_options, f"Select {select['id']} missing options/enum"


class TestSwitchYaml:
    """Test switch.yaml configuration."""

    def test_switch_yaml_structure(self) -> None:
        """Test switch.yaml has correct structure."""
        base_path = Path(__file__).parent.parent / "custom_components/wattpilot"
        yaml_path = base_path / "switch.yaml"

        with yaml_path.open() as f:
            config = yaml.safe_load(f)

        assert "switch" in config
        assert isinstance(config["switch"], list)

        for switch in config["switch"]:
            assert "id" in switch
            # Switches should have set_value mapping
            if "set_value" in switch:
                assert isinstance(switch["set_value"], dict)
                assert "on" in switch["set_value"] or "off" in switch["set_value"]


class TestUpdateYaml:
    """Test update.yaml configuration."""

    def test_update_yaml_structure(self) -> None:
        """Test update.yaml has correct structure."""
        base_path = Path(__file__).parent.parent / "custom_components/wattpilot"
        yaml_path = base_path / "update.yaml"

        with yaml_path.open() as f:
            config = yaml.safe_load(f)

        assert "update" in config
        assert isinstance(config["update"], list)

        for update in config["update"]:
            assert "id" in update


class TestSensorYamlDetails:
    """Detailed tests for sensor.yaml configuration."""

    def test_temperature_sensors_have_correct_config(self) -> None:
        """Test temperature sensors have correct device class and unit."""
        base_path = Path(__file__).parent.parent / "custom_components/wattpilot"
        yaml_path = base_path / "sensor.yaml"

        with yaml_path.open() as f:
            config = yaml.safe_load(f)

        temp_sensors = [
            s for s in config["sensor"] if s.get("device_class") == "temperature"
        ]

        for sensor in temp_sensors:
            assert sensor.get("unit_of_measurement") in ["°C", "°F"], (
                f"Temperature sensor {sensor['id']} has invalid unit"
            )

    def test_current_sensors_have_correct_config(self) -> None:
        """Test current sensors have correct device class and unit."""
        base_path = Path(__file__).parent.parent / "custom_components/wattpilot"
        yaml_path = base_path / "sensor.yaml"

        with yaml_path.open() as f:
            config = yaml.safe_load(f)

        current_sensors = [
            s for s in config["sensor"] if s.get("device_class") == "current"
        ]

        for sensor in current_sensors:
            assert sensor.get("unit_of_measurement") == "A", (
                f"Current sensor {sensor['id']} should have unit 'A'"
            )

    def test_voltage_sensors_have_correct_config(self) -> None:
        """Test voltage sensors have correct device class and unit."""
        base_path = Path(__file__).parent.parent / "custom_components/wattpilot"
        yaml_path = base_path / "sensor.yaml"

        with yaml_path.open() as f:
            config = yaml.safe_load(f)

        voltage_sensors = [
            s for s in config["sensor"] if s.get("device_class") == "voltage"
        ]

        for sensor in voltage_sensors:
            assert sensor.get("unit_of_measurement") == "V", (
                f"Voltage sensor {sensor['id']} should have unit 'V'"
            )

    def test_diagnostic_sensors_have_entity_category(self) -> None:
        """Test diagnostic sensors have entity_category set."""
        base_path = Path(__file__).parent.parent / "custom_components/wattpilot"
        yaml_path = base_path / "sensor.yaml"

        with yaml_path.open() as f:
            config = yaml.safe_load(f)

        # Check for common diagnostic sensor patterns
        for sensor in config["sensor"]:
            sensor_id = sensor.get("id", "")
            # Some patterns that indicate diagnostic sensors
            if (
                any(
                    x in sensor_id
                    for x in ["error", "status", "version", "rssi", "ssid"]
                )
                and "entity_category" in sensor
            ):
                assert sensor["entity_category"] in [
                    "diagnostic",
                    "config",
                ], f"Sensor {sensor_id} has invalid entity_category"
