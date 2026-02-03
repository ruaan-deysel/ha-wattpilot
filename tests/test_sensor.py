"""Tests for the sensor platform."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest
import yaml

# Path to the sensor.yaml configuration
SENSOR_YAML_PATH = (
    Path(__file__).parent.parent / "custom_components/wattpilot/sensor.yaml"
)


def load_sensor_config() -> dict[str, Any]:
    """Load the sensor YAML configuration."""
    with SENSOR_YAML_PATH.open() as f:
        return yaml.safe_load(f)


def get_sensor_by_id(sensor_id: str) -> dict[str, Any] | None:
    """Get a sensor configuration by its ID."""
    config = load_sensor_config()
    return next(
        (s for s in config["sensor"] if s.get("id") == sensor_id),
        None,
    )


class TestSensorYamlConfiguration:
    """Test sensor YAML configuration."""

    def test_eto_sensor_has_correct_device_class(self) -> None:
        """Test eto sensor has energy device class for Energy Dashboard."""
        eto_sensor = get_sensor_by_id("eto")

        assert eto_sensor is not None
        assert eto_sensor.get("device_class") == "energy"
        assert eto_sensor.get("state_class") == "total_increasing"
        assert eto_sensor.get("unit_of_measurement") == "Wh"

    def test_nrg_sensor_has_correct_device_class(self) -> None:
        """Test nrg sensor has power device class for Energy Dashboard."""
        nrg_sensor = get_sensor_by_id("nrg")

        assert nrg_sensor is not None
        assert nrg_sensor.get("device_class") == "power"
        assert nrg_sensor.get("state_class") == "measurement"
        assert nrg_sensor.get("unit_of_measurement") == "W"

    def test_wh_sensor_has_correct_device_class(self) -> None:
        """Test wh (session energy) sensor has correct config for Energy Dashboard."""
        wh_sensor = get_sensor_by_id("wh")

        assert wh_sensor is not None
        assert wh_sensor.get("device_class") == "energy"
        assert wh_sensor.get("state_class") == "total_increasing"
        assert wh_sensor.get("unit_of_measurement") == "Wh"

    def test_all_sensors_have_required_fields(self) -> None:
        """Test all sensors have required id field."""
        config = load_sensor_config()

        for sensor in config["sensor"]:
            assert "id" in sensor, f"Sensor missing 'id': {sensor}"

    def test_energy_sensors_have_state_class(self) -> None:
        """Test all energy sensors have state_class for statistics."""
        config = load_sensor_config()

        energy_sensors = [
            s for s in config["sensor"] if s.get("device_class") == "energy"
        ]

        for sensor in energy_sensors:
            assert sensor.get("state_class") in ["total", "total_increasing"], (
                f"Energy sensor '{sensor.get('id')}' missing or invalid state_class"
            )

    def test_power_sensors_have_state_class(self) -> None:
        """Test all power sensors have state_class for statistics."""
        config = load_sensor_config()

        power_sensors = [
            s for s in config["sensor"] if s.get("device_class") == "power"
        ]

        for sensor in power_sensors:
            assert sensor.get("state_class") == "measurement", (
                f"Power sensor '{sensor.get('id')}' should have state_class=measurement"
            )


class TestSensorEntity:
    """Test sensor entity functionality."""

    @pytest.fixture
    def mock_charger(self) -> MagicMock:
        """Create a mock charger instance."""
        charger = MagicMock()
        charger.serial = "12345678"
        charger.name = "Test Wattpilot"
        charger.firmware = "40.7"
        charger.connected = True
        charger.allPropsInitialized = True
        charger.allProps = {
            "car": 1,
            "amp": 6,
            "eto": 12345,
            "wh": 1000,
            "nrg": [
                230.0,
                231.0,
                229.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                1500.0,
                0.0,
                0.0,
                0.0,
                0.0,
            ],
            "onv": "40.7",
        }
        charger.AccessState = "open"
        charger.carConnected = "no car"
        return charger

    def test_sensor_yaml_loads_successfully(self) -> None:
        """Test that sensor.yaml loads without errors."""
        config = load_sensor_config()

        assert "sensor" in config
        assert len(config["sensor"]) > 0

    def test_sensor_ids_are_unique(self) -> None:
        """Test that all sensor IDs are unique (except for namespaced ones)."""
        config = load_sensor_config()

        # Collect IDs with their UIDs for uniqueness
        id_uid_pairs = []
        for sensor in config["sensor"]:
            uid = sensor.get("uid", sensor.get("id"))
            id_uid_pairs.append(uid)

        # Check for duplicates
        seen: set[str] = set()
        duplicates = []
        for item in id_uid_pairs:
            if item in seen:
                duplicates.append(item)
            seen.add(item)

        assert len(duplicates) == 0, f"Duplicate sensor UIDs found: {duplicates}"


class TestEnergyDashboardCompatibility:
    """Test Energy Dashboard compatibility for EV charger sensors."""

    def test_total_energy_sensor_compatible(self) -> None:
        """Test total energy sensor is compatible with Energy Dashboard device consumption."""
        eto_sensor = get_sensor_by_id("eto")

        # Energy Dashboard requires:
        # - device_class: energy
        # - state_class: total or total_increasing
        # - unit: cal, Gcal, GJ, GWh, J, kcal, kJ, kWh, Mcal, MJ, MWh, mWh, TWh, Wh
        valid_energy_units = [
            "cal",
            "Gcal",
            "GJ",
            "GWh",
            "J",
            "kcal",
            "kJ",
            "kWh",
            "Mcal",
            "MJ",
            "MWh",
            "mWh",
            "TWh",
            "Wh",
        ]

        assert eto_sensor is not None
        assert eto_sensor.get("device_class") == "energy"
        assert eto_sensor.get("state_class") in ["total", "total_increasing"]
        assert eto_sensor.get("unit_of_measurement") in valid_energy_units

    def test_power_sensor_compatible(self) -> None:
        """Test power sensor is compatible with Energy Dashboard device power."""
        nrg_sensor = get_sensor_by_id("nrg")

        # Energy Dashboard power tracking requires:
        # - device_class: power
        # - state_class: measurement
        # - unit: GW, kW, MW, mW, TW, W
        valid_power_units = ["GW", "kW", "MW", "mW", "TW", "W"]

        assert nrg_sensor is not None
        assert nrg_sensor.get("device_class") == "power"
        assert nrg_sensor.get("state_class") == "measurement"
        assert nrg_sensor.get("unit_of_measurement") in valid_power_units

    def test_session_energy_sensor_available(self) -> None:
        """Test session energy sensor is available for per-session tracking."""
        wh_sensor = get_sensor_by_id("wh")

        assert wh_sensor is not None
        assert wh_sensor.get("device_class") == "energy"
        assert wh_sensor.get("state_class") == "total_increasing"

    def test_energy_dashboard_documentation_in_description(self) -> None:
        """Test that Energy Dashboard sensors mention their purpose in description."""
        eto_sensor = get_sensor_by_id("eto")
        nrg_sensor = get_sensor_by_id("nrg")

        assert eto_sensor is not None
        assert nrg_sensor is not None

        # Check descriptions mention Energy Dashboard
        eto_desc = eto_sensor.get("description", "").lower()
        nrg_desc = nrg_sensor.get("description", "").lower()

        assert "energy dashboard" in eto_desc, (
            "eto sensor description should mention Energy Dashboard"
        )
        assert "energy dashboard" in nrg_desc, (
            "nrg sensor description should mention Energy Dashboard"
        )
