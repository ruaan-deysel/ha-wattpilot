"""Tests for the sensor platform."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from custom_components.wattpilot.descriptions import WattpilotSensorEntityDescription


def get_sensor_desc_by_key(charger_key: str) -> WattpilotSensorEntityDescription | None:
    """Get a sensor description by its charger_key."""
    from custom_components.wattpilot.descriptions import SENSOR_DESCRIPTIONS

    return next(
        (d for d in SENSOR_DESCRIPTIONS if d.charger_key == charger_key),
        None,
    )


class TestSensorDescriptions:
    """Test sensor entity descriptions."""

    def test_eto_sensor_has_correct_device_class(self) -> None:
        """Test eto sensor has energy device class for Energy Dashboard."""
        eto = get_sensor_desc_by_key("eto")

        assert eto is not None
        assert eto.device_class == SensorDeviceClass.ENERGY
        assert eto.state_class == SensorStateClass.TOTAL_INCREASING
        assert eto.native_unit_of_measurement == "Wh"

    def test_nrg_sensor_has_correct_device_class(self) -> None:
        """Test nrg sensor has power device class for Energy Dashboard."""
        nrg = get_sensor_desc_by_key("nrg")

        assert nrg is not None
        assert nrg.device_class == SensorDeviceClass.POWER
        assert nrg.state_class == SensorStateClass.MEASUREMENT
        assert nrg.native_unit_of_measurement == "W"

    def test_wh_sensor_has_correct_device_class(self) -> None:
        """Test wh (session energy) sensor has correct config for Energy Dashboard."""
        wh = get_sensor_desc_by_key("wh")

        assert wh is not None
        assert wh.device_class == SensorDeviceClass.ENERGY
        assert wh.state_class == SensorStateClass.TOTAL_INCREASING
        assert wh.native_unit_of_measurement == "Wh"

    def test_all_descriptions_have_charger_key(self) -> None:
        """Test all sensor descriptions have charger_key."""
        from custom_components.wattpilot.descriptions import SENSOR_DESCRIPTIONS

        for desc in SENSOR_DESCRIPTIONS:
            assert desc.charger_key, f"Sensor {desc.key} missing charger_key"

    def test_energy_sensors_have_state_class(self) -> None:
        """Test all energy sensors have state_class for statistics."""
        from custom_components.wattpilot.descriptions import SENSOR_DESCRIPTIONS

        energy_sensors = [
            d for d in SENSOR_DESCRIPTIONS if d.device_class == SensorDeviceClass.ENERGY
        ]

        for desc in energy_sensors:
            assert desc.state_class in (
                SensorStateClass.TOTAL,
                SensorStateClass.TOTAL_INCREASING,
            ), f"Energy sensor '{desc.charger_key}' missing or invalid state_class"

    def test_power_sensors_have_state_class(self) -> None:
        """Test all power sensors have state_class for statistics."""
        from custom_components.wattpilot.descriptions import SENSOR_DESCRIPTIONS

        power_sensors = [
            d for d in SENSOR_DESCRIPTIONS if d.device_class == SensorDeviceClass.POWER
        ]

        for desc in power_sensors:
            assert desc.state_class == SensorStateClass.MEASUREMENT, (
                f"Power sensor '{desc.charger_key}' should have state_class=MEASUREMENT"
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

    def test_sensor_descriptions_exist(self) -> None:
        """Test that sensor descriptions are defined."""
        from custom_components.wattpilot.descriptions import SENSOR_DESCRIPTIONS

        assert len(SENSOR_DESCRIPTIONS) > 0

    def test_sensor_ids_are_unique(self) -> None:
        """Test that all sensor IDs (uid or charger_key) are unique."""
        from custom_components.wattpilot.descriptions import SENSOR_DESCRIPTIONS

        keys = [d.uid or d.charger_key for d in SENSOR_DESCRIPTIONS]
        seen: set[str] = set()
        duplicates = []
        for key in keys:
            if key in seen:
                duplicates.append(key)
            seen.add(key)

        assert not duplicates, f"Duplicate sensor UIDs found: {duplicates}"


class TestEnergyDashboardCompatibility:
    """Test Energy Dashboard compatibility for EV charger sensors."""

    def test_total_energy_sensor_compatible(self) -> None:
        """Test total energy sensor is compatible with Energy Dashboard device consumption."""
        eto = get_sensor_desc_by_key("eto")

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

        assert eto is not None
        assert eto.device_class == SensorDeviceClass.ENERGY
        assert eto.state_class in (
            SensorStateClass.TOTAL,
            SensorStateClass.TOTAL_INCREASING,
        )
        assert eto.native_unit_of_measurement in valid_energy_units

    def test_power_sensor_compatible(self) -> None:
        """Test power sensor is compatible with Energy Dashboard device power."""
        nrg = get_sensor_desc_by_key("nrg")

        valid_power_units = ["GW", "kW", "MW", "mW", "TW", "W"]

        assert nrg is not None
        assert nrg.device_class == SensorDeviceClass.POWER
        assert nrg.state_class == SensorStateClass.MEASUREMENT
        assert nrg.native_unit_of_measurement in valid_power_units

    def test_session_energy_sensor_available(self) -> None:
        """Test session energy sensor is available for per-session tracking."""
        wh = get_sensor_desc_by_key("wh")

        assert wh is not None
        assert wh.device_class == SensorDeviceClass.ENERGY
        assert wh.state_class == SensorStateClass.TOTAL_INCREASING

    def test_energy_dashboard_documentation_in_description(self) -> None:
        """Test that Energy Dashboard sensors mention their purpose in description."""
        eto = get_sensor_desc_by_key("eto")
        nrg = get_sensor_desc_by_key("nrg")

        assert eto is not None
        assert nrg is not None

        eto_desc = (eto.description_text or "").lower()
        nrg_desc = (nrg.description_text or "").lower()

        assert "energy dashboard" in eto_desc, (
            "eto sensor description should mention Energy Dashboard"
        )
        assert "energy dashboard" in nrg_desc, (
            "nrg sensor description should mention Energy Dashboard"
        )


class TestSensorPlatformSetup:
    """Test sensor platform setup."""

    async def test_async_setup_entry_success(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_config_entry_data: dict,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test successful sensor platform setup."""
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

        async_add_entities = AsyncMock()

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp",
            return_value=100.0,
        ):
            await async_setup_entry(hass, entry, async_add_entities)
            assert async_add_entities.called


class TestChargerSensor:
    """Test ChargerSensor entity class."""

    def _make_sensor_description(
        self, **overrides: Any
    ) -> WattpilotSensorEntityDescription:
        """Create a WattpilotSensorEntityDescription for testing."""
        from custom_components.wattpilot.descriptions import (
            SOURCE_PROPERTY,
            WattpilotSensorEntityDescription,
        )

        defaults = {
            "key": "test_sensor",
            "charger_key": "test_prop",
            "source": SOURCE_PROPERTY,
        }
        defaults.update(overrides)
        return WattpilotSensorEntityDescription(**defaults)

    def _make_entry(
        self,
        mock_config_entry_data: dict[str, Any],
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
    ) -> ConfigEntry:
        """Create a ConfigEntry with runtime data."""
        from homeassistant.config_entries import ConfigEntry

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
        return entry

    def test_sensor_device_class_conversion(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_config_entry_data: dict,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test sensor device_class is set from description."""
        from homeassistant.components.sensor import SensorDeviceClass

        from custom_components.wattpilot.sensor import ChargerSensor

        entry = self._make_entry(mock_config_entry_data, mock_charger, mock_coordinator)
        desc = self._make_sensor_description(
            key="test_power",
            charger_key="test_power_sensor_id",
            device_class=SensorDeviceClass.POWER,
            native_unit_of_measurement="W",
            state_class=SensorStateClass.MEASUREMENT,
        )

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp",
            return_value=1000.0,
        ):
            sensor = ChargerSensor(hass, entry, desc, mock_charger)
            assert sensor.device_class == SensorDeviceClass.POWER

    async def test_sensor_state_validation_with_enum(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_config_entry_data: dict,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test sensor state validation with enum mapping."""
        from custom_components.wattpilot.sensor import ChargerSensor

        entry = self._make_entry(mock_config_entry_data, mock_charger, mock_coordinator)
        desc = self._make_sensor_description(
            key="test_enum",
            charger_key="test_enum_sensor_id",
            default_state="idle",
            enum={0: "idle", 1: "charging", 2: "complete"},
        )

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp",
            return_value=1,
        ):
            sensor = ChargerSensor(hass, entry, desc, mock_charger)
            validated_state = await sensor._async_update_validate_platform_state(1)
            assert validated_state == "charging"

    async def test_sensor_state_validation_html_unescape(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_config_entry_data: dict,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test sensor state validation with HTML unescaping."""
        from custom_components.wattpilot.sensor import ChargerSensor

        entry = self._make_entry(mock_config_entry_data, mock_charger, mock_coordinator)
        desc = self._make_sensor_description(
            key="test_html",
            charger_key="test_html_sensor_id",
            default_state="",
            html_unescape=True,
        )

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp",
            return_value="&lt;test&gt;",
        ):
            sensor = ChargerSensor(hass, entry, desc, mock_charger)
            validated_state = await sensor._async_update_validate_platform_state(
                "&lt;test&gt;"
            )
            assert validated_state == "<test>"

    async def test_sensor_state_validation_none_returns_unknown(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_config_entry_data: dict,
        mock_coordinator: MagicMock,
    ) -> None:
        """Test sensor state validation returns UNKNOWN for None."""
        from homeassistant.const import STATE_UNKNOWN

        from custom_components.wattpilot.sensor import ChargerSensor

        entry = self._make_entry(mock_config_entry_data, mock_charger, mock_coordinator)
        desc = self._make_sensor_description(
            key="test_none",
            charger_key="test_sensor_id",
            default_state=None,
        )

        with patch(
            "custom_components.wattpilot.entities.GetChargerProp",
            return_value=None,
        ):
            sensor = ChargerSensor(hass, entry, desc, mock_charger)
            sensor._attr_native_unit_of_measurement = None
            validated_state = await sensor._async_update_validate_platform_state(None)
            assert validated_state == STATE_UNKNOWN
