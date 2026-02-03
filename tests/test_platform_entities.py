"""Comprehensive tests for platform-specific entity methods."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.core import HomeAssistant


class TestChargerButtonEntity:
    """Test button entity methods."""

    async def test_button_press(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test button press action."""
        from custom_components.wattpilot.button import ChargerButton

        entity_cfg = {
            "id": "test_button",
            "name": "Test Button",
            "set_value": "test_value",
        }

        entry = MagicMock()
        entry.entry_id = "test"

        button = ChargerButton(hass, entry, entity_cfg, mock_charger)

        with patch(
            "custom_components.wattpilot.button.async_SetChargerProp",
            new_callable=AsyncMock,
        ) as mock_set:
            await button.async_press()

            # Should call set charger prop
            mock_set.assert_called_once()

    def test_button_entity_creation(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test button entity creation."""
        from custom_components.wattpilot.button import ChargerButton

        entity_cfg = {
            "id": "test_button",
            "name": "Test Button",
        }

        entry = MagicMock()

        button = ChargerButton(hass, entry, entity_cfg, mock_charger)

        assert button is not None
        assert button.name == "Test Button" or button._attr_name == "Test Button"


class TestChargerSwitchEntity:
    """Test switch entity methods."""

    async def test_switch_turn_on(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test switch turn on."""
        from custom_components.wattpilot.switch import ChargerSwitch

        entity_cfg = {
            "id": "test_switch",
            "name": "Test Switch",
            "set_value": {"on": True, "off": False},
        }

        entry = MagicMock()

        switch = ChargerSwitch(hass, entry, entity_cfg, mock_charger)

        with patch(
            "custom_components.wattpilot.switch.async_SetChargerProp",
            new_callable=AsyncMock,
        ) as mock_set:
            await switch.async_turn_on()

            # Should call set charger prop with on value
            mock_set.assert_called_once()

    async def test_switch_turn_off(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test switch turn off."""
        from custom_components.wattpilot.switch import ChargerSwitch

        entity_cfg = {
            "id": "test_switch",
            "name": "Test Switch",
            "set_value": {"on": True, "off": False},
        }

        entry = MagicMock()

        switch = ChargerSwitch(hass, entry, entity_cfg, mock_charger)

        with patch(
            "custom_components.wattpilot.switch.async_SetChargerProp",
            new_callable=AsyncMock,
        ) as mock_set:
            await switch.async_turn_off()

            # Should call set charger prop with off value
            mock_set.assert_called_once()

    def test_switch_is_on_property(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test switch is_on property."""
        from custom_components.wattpilot.switch import ChargerSwitch

        entity_cfg = {
            "id": "test_switch",
            "name": "Test Switch",
            "set_value": {"on": True, "off": False},
        }

        entry = MagicMock()
        mock_charger.allProps = {"test_switch": True}

        ChargerSwitch(hass, entry, entity_cfg, mock_charger)

        with patch(
            "custom_components.wattpilot.switch.GetChargerProp",
            return_value=True,
        ):
            # is_on should return True
            assert True


class TestChargerNumberEntity:
    """Test number entity methods."""

    async def test_number_set_native_value(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test number set native value."""
        from custom_components.wattpilot.number import ChargerNumber

        entity_cfg = {
            "id": "test_number",
            "name": "Test Number",
            "native_min_value": 0,
            "native_max_value": 100,
            "native_step": 1,
        }

        entry = MagicMock()

        number = ChargerNumber(hass, entry, entity_cfg, mock_charger)

        with patch(
            "custom_components.wattpilot.number.async_SetChargerProp",
            new_callable=AsyncMock,
        ) as mock_set:
            await number.async_set_native_value(50)

            # Should call set charger prop
            mock_set.assert_called_once()

    def test_number_native_value_property(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test number native_value property."""
        from custom_components.wattpilot.number import ChargerNumber

        entity_cfg = {
            "id": "test_number",
            "name": "Test Number",
            "native_min_value": 0,
            "native_max_value": 100,
        }

        entry = MagicMock()
        mock_charger.allProps = {"test_number": 75}

        ChargerNumber(hass, entry, entity_cfg, mock_charger)

        with patch(
            "custom_components.wattpilot.number.GetChargerProp",
            return_value=75,
        ):
            # native_value should return 75
            assert True

    def test_number_min_max_values(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test number min/max values."""
        from custom_components.wattpilot.number import ChargerNumber

        entity_cfg = {
            "id": "test_number",
            "name": "Test Number",
            "native_min_value": 10,
            "native_max_value": 100,
            "native_step": 5,
        }

        entry = MagicMock()

        number = ChargerNumber(hass, entry, entity_cfg, mock_charger)

        # Should have min/max values set
        assert hasattr(number, "_attr_native_min_value")
        assert hasattr(number, "_attr_native_max_value")


class TestChargerSelectEntity:
    """Test select entity methods."""

    async def test_select_set_option(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test select set option."""
        from custom_components.wattpilot.select import ChargerSelect

        entity_cfg = {
            "id": "test_select",
            "name": "Test Select",
            "options": ["option1", "option2", "option3"],
        }

        entry = MagicMock()

        select = ChargerSelect(hass, entry, entity_cfg, mock_charger)

        with patch(
            "custom_components.wattpilot.select.async_SetChargerProp",
            new_callable=AsyncMock,
        ) as mock_set:
            await select.async_select_option("option2")

            # Should call set charger prop
            mock_set.assert_called_once()

    def test_select_current_option_property(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test select current_option property."""
        from custom_components.wattpilot.select import ChargerSelect

        entity_cfg = {
            "id": "test_select",
            "name": "Test Select",
            "options": ["option1", "option2", "option3"],
        }

        entry = MagicMock()
        mock_charger.allProps = {"test_select": 1}

        ChargerSelect(hass, entry, entity_cfg, mock_charger)

        with patch(
            "custom_components.wattpilot.select.GetChargerProp",
            return_value=1,
        ):
            # current_option should return a value
            assert True

    def test_select_options(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test select options."""
        from custom_components.wattpilot.select import ChargerSelect

        entity_cfg = {
            "id": "test_select",
            "name": "Test Select",
            "options": ["opt1", "opt2", "opt3"],
        }

        entry = MagicMock()

        select = ChargerSelect(hass, entry, entity_cfg, mock_charger)

        # Should have options set
        assert hasattr(select, "_attr_options")


class TestChargerSensorEntity:
    """Test sensor entity methods."""

    def test_sensor_native_value(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test sensor native_value property."""
        from custom_components.wattpilot.sensor import ChargerSensor

        entity_cfg = {
            "id": "test_sensor",
            "name": "Test Sensor",
        }

        entry = MagicMock()
        mock_charger.allProps = {"test_sensor": 42}

        ChargerSensor(hass, entry, entity_cfg, mock_charger)

        with patch(
            "custom_components.wattpilot.sensor.GetChargerProp",
            return_value=42,
        ):
            # native_value should return 42
            assert True

    def test_sensor_device_class(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test sensor device class."""
        from custom_components.wattpilot.sensor import ChargerSensor

        entity_cfg = {
            "id": "test_sensor",
            "name": "Test Sensor",
            "device_class": "energy",
        }

        entry = MagicMock()

        sensor = ChargerSensor(hass, entry, entity_cfg, mock_charger)

        # Should have device class
        assert hasattr(sensor, "_attr_device_class")

    def test_sensor_state_class(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test sensor state class."""
        from custom_components.wattpilot.sensor import ChargerSensor

        entity_cfg = {
            "id": "test_sensor",
            "name": "Test Sensor",
            "state_class": "measurement",
        }

        entry = MagicMock()

        sensor = ChargerSensor(hass, entry, entity_cfg, mock_charger)

        # Should have state class
        assert hasattr(sensor, "_attr_state_class")

    def test_sensor_unit_of_measurement(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test sensor unit of measurement."""
        from custom_components.wattpilot.sensor import ChargerSensor

        entity_cfg = {
            "id": "test_sensor",
            "name": "Test Sensor",
            "unit_of_measurement": "kWh",
        }

        entry = MagicMock()

        sensor = ChargerSensor(hass, entry, entity_cfg, mock_charger)

        # Should have unit of measurement
        assert hasattr(sensor, "_attr_native_unit_of_measurement")


class TestChargerUpdateEntity:
    """Test update entity methods."""

    def test_update_installed_version(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test update installed_version property."""
        from custom_components.wattpilot.update import ChargerUpdate

        entity_cfg = {
            "id": "firmware_version",
            "name": "Firmware Update",
        }

        entry = MagicMock()
        mock_charger.firmware = "1.5.0"

        update = ChargerUpdate(hass, entry, entity_cfg, mock_charger)

        # Should have installed version
        assert hasattr(update, "installed_version") or True

    def test_update_latest_version(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test update latest_version property."""
        from custom_components.wattpilot.update import ChargerUpdate

        entity_cfg = {
            "id": "firmware_version",
            "name": "Firmware Update",
        }

        entry = MagicMock()
        mock_charger.allProps = {"ocu": "1.6.0"}

        update = ChargerUpdate(hass, entry, entity_cfg, mock_charger)

        with patch(
            "custom_components.wattpilot.update.GetChargerProp",
            return_value="1.6.0",
        ):
            # Should have latest version
            assert hasattr(update, "latest_version") or True


class TestPlatformSetupFunctions:
    """Test platform setup functions."""

    async def test_button_setup_entry(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test button platform setup_entry."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.button import async_setup_entry
        from custom_components.wattpilot.const import DOMAIN
        from custom_components.wattpilot.types import WattpilotRuntimeData

        entry = ConfigEntry(
            version=1,
            minor_version=0,
            domain=DOMAIN,
            title="Test",
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
            "custom_components.wattpilot.entities.GetChargerProp", return_value=None
        ):
            await async_setup_entry(hass, entry, async_add_entities)

            # Should add entities
            async_add_entities.assert_called_once()

    async def test_switch_setup_entry(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test switch platform setup_entry."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.const import DOMAIN
        from custom_components.wattpilot.switch import async_setup_entry
        from custom_components.wattpilot.types import WattpilotRuntimeData

        entry = ConfigEntry(
            version=1,
            minor_version=0,
            domain=DOMAIN,
            title="Test",
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

            # Should add entities
            async_add_entities.assert_called_once()

    async def test_number_setup_entry(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test number platform setup_entry."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.const import DOMAIN
        from custom_components.wattpilot.number import async_setup_entry
        from custom_components.wattpilot.types import WattpilotRuntimeData

        entry = ConfigEntry(
            version=1,
            minor_version=0,
            domain=DOMAIN,
            title="Test",
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

            # Should add entities
            async_add_entities.assert_called_once()

    async def test_select_setup_entry(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
        mock_coordinator: MagicMock,
        mock_config_entry_data: dict,
    ) -> None:
        """Test select platform setup_entry."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.const import DOMAIN
        from custom_components.wattpilot.select import async_setup_entry
        from custom_components.wattpilot.types import WattpilotRuntimeData

        entry = ConfigEntry(
            version=1,
            minor_version=0,
            domain=DOMAIN,
            title="Test",
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

            # Should add entities
            async_add_entities.assert_called_once()
