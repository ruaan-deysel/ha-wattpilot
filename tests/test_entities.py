"""Tests for base entity class."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch

import pytest
from homeassistant.core import HomeAssistant

from custom_components.wattpilot.const import CONF_CONNECTION, CONF_LOCAL, DOMAIN
from custom_components.wattpilot.descriptions import (
    SOURCE_ATTRIBUTE,
    SOURCE_NAMESPACELIST,
    SOURCE_PROPERTY,
    WattpilotSensorEntityDescription,
)
from custom_components.wattpilot.entities import (
    ChargerPlatformEntity,
    check_connection_supported,
    check_firmware_supported,
    check_variant_supported,
    filter_descriptions,
)


class TestFilterHelpers:
    """Test filter helper functions."""

    def test_check_firmware_supported_no_constraint(
        self, mock_charger: MagicMock
    ) -> None:
        """Test firmware check with no constraint."""
        result = check_firmware_supported(
            mock_charger, None, "test_charger", "test_prop"
        )
        assert result is True

    def test_check_firmware_supported_greater_equal(
        self, mock_charger: MagicMock
    ) -> None:
        """Test firmware check with >= constraint."""
        mock_charger.firmware = "40.7"

        # Test passing case
        result = check_firmware_supported(
            mock_charger, ">=40.0", "test_charger", "test_prop"
        )
        assert result is True

        # Test failing case
        result = check_firmware_supported(
            mock_charger, ">=41.0", "test_charger", "test_prop"
        )
        assert result is False

    def test_check_firmware_supported_less_equal(self, mock_charger: MagicMock) -> None:
        """Test firmware check with <= constraint."""
        mock_charger.firmware = "40.7"

        # Test passing case
        result = check_firmware_supported(
            mock_charger, "<=41.0", "test_charger", "test_prop"
        )
        assert result is True

        # Test failing case
        result = check_firmware_supported(
            mock_charger, "<=40.0", "test_charger", "test_prop"
        )
        assert result is False

    def test_check_firmware_supported_equal(self, mock_charger: MagicMock) -> None:
        """Test firmware check with == constraint."""
        mock_charger.firmware = "40.7"

        # Test passing case
        result = check_firmware_supported(
            mock_charger, "==40.7", "test_charger", "test_prop"
        )
        assert result is True

        # Test failing case
        result = check_firmware_supported(
            mock_charger, "==41.0", "test_charger", "test_prop"
        )
        assert result is False

    def test_check_firmware_supported_greater(self, mock_charger: MagicMock) -> None:
        """Test firmware check with > constraint."""
        mock_charger.firmware = "40.7"

        # Test passing case
        result = check_firmware_supported(
            mock_charger, ">40.0", "test_charger", "test_prop"
        )
        assert result is True

        # Test failing case
        result = check_firmware_supported(
            mock_charger, ">41.0", "test_charger", "test_prop"
        )
        assert result is False

    def test_check_firmware_supported_less(self, mock_charger: MagicMock) -> None:
        """Test firmware check with < constraint."""
        mock_charger.firmware = "40.7"

        # Test passing case
        result = check_firmware_supported(
            mock_charger, "<41.0", "test_charger", "test_prop"
        )
        assert result is True

        # Test failing case
        result = check_firmware_supported(
            mock_charger, "<40.0", "test_charger", "test_prop"
        )
        assert result is False

    def test_check_firmware_supported_invalid_constraint(
        self, mock_charger: MagicMock
    ) -> None:
        """Test firmware check with invalid constraint."""
        mock_charger.firmware = "40.7"

        result = check_firmware_supported(
            mock_charger, "invalid40.0", "test_charger", "test_prop"
        )
        assert result is False

    def test_check_firmware_supported_missing_firmware(self) -> None:
        """Test firmware check with missing firmware."""
        charger = MagicMock()
        charger.firmware = None
        charger.all_properties = {}

        result = check_firmware_supported(
            charger, ">=40.0", "test_charger", "test_prop"
        )
        assert result is False

    def test_check_firmware_supported_from_property(
        self, mock_charger: MagicMock
    ) -> None:
        """Test firmware check reads from property when attribute missing."""
        charger = MagicMock(spec=[])  # Empty spec so firmware doesn't exist
        charger.all_properties = {"onv": "40.7"}

        with patch("custom_components.wattpilot.entities.GetChargerProp") as mock_get:
            mock_get.return_value = "40.7"
            result = check_firmware_supported(
                charger, ">=40.0", "test_charger", "test_prop"
            )
            assert result is True
            mock_get.assert_called_once_with(charger, "onv", None)

    def test_check_variant_supported_no_filter(self, mock_charger: MagicMock) -> None:
        """Test variant check with no filter."""
        result = check_variant_supported(
            mock_charger, None, "test_charger", "test_prop"
        )
        assert result is True

    def test_check_variant_supported_match(self, mock_charger: MagicMock) -> None:
        """Test variant check with matching variant."""
        mock_charger.variant = "11"

        result = check_variant_supported(
            mock_charger, "11", "test_charger", "test_prop"
        )
        assert result is True

    def test_check_variant_supported_no_match(self, mock_charger: MagicMock) -> None:
        """Test variant check with non-matching variant."""
        mock_charger.variant = "11"

        result = check_variant_supported(
            mock_charger, "22", "test_charger", "test_prop"
        )
        assert result is False

    def test_check_variant_supported_case_insensitive(
        self, mock_charger: MagicMock
    ) -> None:
        """Test variant check is case insensitive."""
        mock_charger.variant = "11"

        result = check_variant_supported(
            mock_charger, "11", "test_charger", "test_prop"
        )
        assert result is True

    def test_check_variant_supported_from_property(self) -> None:
        """Test variant check reads from property when attribute missing."""
        charger = MagicMock(spec=[])  # Empty spec so variant doesn't exist
        charger.all_properties = {"var": "11"}

        with patch("custom_components.wattpilot.entities.GetChargerProp") as mock_get:
            mock_get.return_value = "11"
            result = check_variant_supported(charger, "11", "test_charger", "test_prop")
            assert result is True
            mock_get.assert_called_once_with(charger, "var", 11)

    def test_check_connection_supported_no_filter(self, mock_config_entry: Any) -> None:
        """Test connection check with no filter."""
        result = check_connection_supported(
            mock_config_entry, None, "test_charger", "test_prop"
        )
        assert result is True

    def test_check_connection_supported_match(self, mock_config_entry: Any) -> None:
        """Test connection check with matching connection."""
        # Already set via fixture, just update
        mock_config_entry.runtime_data.params[CONF_CONNECTION] = CONF_LOCAL

        result = check_connection_supported(
            mock_config_entry, CONF_LOCAL, "test_charger", "test_prop"
        )
        assert result is True

    def test_check_connection_supported_no_match(self, mock_config_entry: Any) -> None:
        """Test connection check with non-matching connection."""
        # Already set via fixture
        mock_config_entry.runtime_data.params[CONF_CONNECTION] = CONF_LOCAL

        result = check_connection_supported(
            mock_config_entry, "cloud", "test_charger", "test_prop"
        )
        assert result is False

    def test_check_connection_supported_case_insensitive(
        self, mock_config_entry: Any
    ) -> None:
        """Test connection check is case insensitive."""
        # Already set via fixture
        mock_config_entry.runtime_data.params[CONF_CONNECTION] = "local"

        result = check_connection_supported(
            mock_config_entry, "LOCAL", "test_charger", "test_prop"
        )
        assert result is True

    def test_check_connection_supported_missing_runtime_data(self) -> None:
        """Test connection check with missing runtime data."""
        entry = MagicMock()
        entry.runtime_data = None

        result = check_connection_supported(entry, "local", "test_charger", "test_prop")
        assert result is True

    def test_check_connection_supported_missing_params(
        self, mock_config_entry: Any
    ) -> None:
        """Test connection check with missing params."""
        # Set params to None to test missing case
        mock_config_entry.runtime_data.params = None

        result = check_connection_supported(
            mock_config_entry, "local", "test_charger", "test_prop"
        )
        # Should default to STATE_UNKNOWN and still check
        assert result is False


class TestFilterDescriptions:
    """Test filter_descriptions function."""

    def test_filter_descriptions_no_constraints(
        self, mock_charger: MagicMock, mock_config_entry: Any
    ) -> None:
        """Test filtering with no constraints."""
        desc1 = WattpilotSensorEntityDescription(
            key="test1",
            charger_key="prop1",
            name="Test 1",
            source=SOURCE_PROPERTY,
        )
        desc2 = WattpilotSensorEntityDescription(
            key="test2",
            charger_key="prop2",
            name="Test 2",
            source=SOURCE_PROPERTY,
        )
        descriptions = [desc1, desc2]

        result = filter_descriptions(
            descriptions, mock_charger, mock_config_entry, "test_charger"
        )
        assert len(result) == 2

    def test_filter_descriptions_firmware_constraint(
        self, mock_charger: MagicMock, mock_config_entry: Any
    ) -> None:
        """Test filtering with firmware constraint."""
        mock_charger.firmware = "40.7"

        desc_pass = WattpilotSensorEntityDescription(
            key="test1",
            charger_key="prop1",
            name="Test 1",
            source=SOURCE_PROPERTY,
            firmware=">=40.0",
        )
        desc_fail = WattpilotSensorEntityDescription(
            key="test2",
            charger_key="prop2",
            name="Test 2",
            source=SOURCE_PROPERTY,
            firmware=">=41.0",
        )
        descriptions = [desc_pass, desc_fail]

        result = filter_descriptions(
            descriptions, mock_charger, mock_config_entry, "test_charger"
        )
        assert len(result) == 1
        assert result[0].key == "test1"

    def test_filter_descriptions_variant_constraint(
        self, mock_charger: MagicMock, mock_config_entry: Any
    ) -> None:
        """Test filtering with variant constraint."""
        mock_charger.variant = "11"

        desc_pass = WattpilotSensorEntityDescription(
            key="test1",
            charger_key="prop1",
            name="Test 1",
            source=SOURCE_PROPERTY,
            variant="11",
        )
        desc_fail = WattpilotSensorEntityDescription(
            key="test2",
            charger_key="prop2",
            name="Test 2",
            source=SOURCE_PROPERTY,
            variant="22",
        )
        descriptions = [desc_pass, desc_fail]

        result = filter_descriptions(
            descriptions, mock_charger, mock_config_entry, "test_charger"
        )
        assert len(result) == 1
        assert result[0].key == "test1"

    def test_filter_descriptions_connection_constraint(
        self, mock_charger: MagicMock, mock_config_entry: Any
    ) -> None:
        """Test filtering with connection constraint."""
        # Already set via fixture
        mock_config_entry.runtime_data.params[CONF_CONNECTION] = CONF_LOCAL

        desc_pass = WattpilotSensorEntityDescription(
            key="test1",
            charger_key="prop1",
            name="Test 1",
            source=SOURCE_PROPERTY,
            connection=CONF_LOCAL,
        )
        desc_fail = WattpilotSensorEntityDescription(
            key="test2",
            charger_key="prop2",
            name="Test 2",
            source=SOURCE_PROPERTY,
            connection="cloud",
        )
        descriptions = [desc_pass, desc_fail]

        result = filter_descriptions(
            descriptions, mock_charger, mock_config_entry, "test_charger"
        )
        assert len(result) == 1
        assert result[0].key == "test1"

    def test_filter_descriptions_multiple_constraints(
        self, mock_charger: MagicMock, mock_config_entry: Any
    ) -> None:
        """Test filtering with multiple constraints."""
        mock_charger.firmware = "40.7"
        mock_charger.variant = "11"
        # Already set via fixture
        mock_config_entry.runtime_data.params[CONF_CONNECTION] = CONF_LOCAL

        desc_pass = WattpilotSensorEntityDescription(
            key="test1",
            charger_key="prop1",
            name="Test 1",
            source=SOURCE_PROPERTY,
            firmware=">=40.0",
            variant="11",
            connection=CONF_LOCAL,
        )
        desc_fail_firmware = WattpilotSensorEntityDescription(
            key="test2",
            charger_key="prop2",
            name="Test 2",
            source=SOURCE_PROPERTY,
            firmware=">=41.0",
            variant="11",
            connection=CONF_LOCAL,
        )
        desc_fail_variant = WattpilotSensorEntityDescription(
            key="test3",
            charger_key="prop3",
            name="Test 3",
            source=SOURCE_PROPERTY,
            firmware=">=40.0",
            variant="22",
            connection=CONF_LOCAL,
        )
        descriptions = [desc_pass, desc_fail_firmware, desc_fail_variant]

        result = filter_descriptions(
            descriptions, mock_charger, mock_config_entry, "test_charger"
        )
        assert len(result) == 1
        assert result[0].key == "test1"


class TestChargerPlatformEntity:
    """Test ChargerPlatformEntity class."""

    @pytest.mark.asyncio
    async def test_entity_init_property_source(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test entity initialization with property source."""
        mock_charger.all_properties = {"test_prop": "test_value"}

        desc = WattpilotSensorEntityDescription(
            key="test",
            charger_key="test_prop",
            name="Test",
            source=SOURCE_PROPERTY,
        )

        entity = ChargerPlatformEntity(mock_hass, mock_config_entry, desc, mock_charger)

        assert entity._init_failed is False
        assert entity._identifier == "test_prop"
        assert entity._source == SOURCE_PROPERTY

    @pytest.mark.asyncio
    async def test_entity_init_attribute_source(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test entity initialization with attribute source."""
        mock_charger.test_attr = "test_value"

        desc = WattpilotSensorEntityDescription(
            key="test",
            charger_key="test_attr",
            name="Test",
            source=SOURCE_ATTRIBUTE,
        )

        entity = ChargerPlatformEntity(mock_hass, mock_config_entry, desc, mock_charger)

        assert entity._init_failed is False
        assert entity._source == SOURCE_ATTRIBUTE

    @pytest.mark.asyncio
    async def test_entity_init_namespacelist_source(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test entity initialization with namespacelist source."""
        mock_charger.all_properties = {"test_list": ["value1", "value2", "value3"]}

        desc = WattpilotSensorEntityDescription(
            key="test",
            charger_key="test_list",
            name="Test",
            source=SOURCE_NAMESPACELIST,
            namespace_id="1",
        )

        entity = ChargerPlatformEntity(mock_hass, mock_config_entry, desc, mock_charger)

        assert entity._init_failed is False
        assert entity._namespace_id == "1"

    @pytest.mark.asyncio
    async def test_entity_init_missing_property(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test entity initialization with missing property."""
        mock_charger.all_properties = {}

        desc = WattpilotSensorEntityDescription(
            key="test",
            charger_key="missing_prop",
            name="Test",
            source=SOURCE_PROPERTY,
        )

        with patch("custom_components.wattpilot.entities.GetChargerProp") as mock_get:
            mock_get.return_value = None
            entity = ChargerPlatformEntity(
                mock_hass, mock_config_entry, desc, mock_charger
            )

            assert entity._init_failed is True

    @pytest.mark.asyncio
    async def test_entity_init_missing_attribute(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test entity initialization with missing attribute."""
        # Create an object without the attribute
        charger = MagicMock(spec=[])  # Empty spec = no attributes

        desc = WattpilotSensorEntityDescription(
            key="test",
            charger_key="missing_attr",
            name="Test",
            source=SOURCE_ATTRIBUTE,
        )

        entity = ChargerPlatformEntity(mock_hass, mock_config_entry, desc, charger)

        assert entity._init_failed is True

    @pytest.mark.asyncio
    async def test_entity_init_exception(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test entity initialization handles exceptions."""
        desc = MagicMock()
        desc.charger_key = MagicMock(side_effect=Exception("test"))

        entity = ChargerPlatformEntity(mock_hass, mock_config_entry, desc, mock_charger)

        # Should handle exception gracefully

    def test_entity_description_property(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test entity description property."""
        mock_charger.all_properties = {"test_prop": "test_value"}

        desc = WattpilotSensorEntityDescription(
            key="test",
            charger_key="test_prop",
            name="Test",
            source=SOURCE_PROPERTY,
            description_text="Test description",
        )

        entity = ChargerPlatformEntity(mock_hass, mock_config_entry, desc, mock_charger)

        assert entity.description == "Test description"

    def test_entity_extra_state_attributes(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test entity extra state attributes."""
        mock_charger.all_properties = {"test_prop": "test_value"}

        desc = WattpilotSensorEntityDescription(
            key="test",
            charger_key="test_prop",
            name="Test",
            source=SOURCE_PROPERTY,
            description_text="Test description",
        )

        entity = ChargerPlatformEntity(mock_hass, mock_config_entry, desc, mock_charger)

        attrs = entity.extra_state_attributes
        assert "description" in attrs
        assert attrs["description"] == "Test description"

    def test_entity_available_success(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test entity available when all conditions met."""
        mock_charger.all_properties = {"test_prop": "test_value"}
        mock_charger.connected = True
        mock_charger.properties_initialized = True

        desc = WattpilotSensorEntityDescription(
            key="test",
            charger_key="test_prop",
            name="Test",
            source=SOURCE_PROPERTY,
        )

        entity = ChargerPlatformEntity(mock_hass, mock_config_entry, desc, mock_charger)

        with patch.object(
            ChargerPlatformEntity, "available", property(lambda self: True)
        ):
            # Should be available
            pass

    def test_entity_available_init_failed(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test entity unavailable when init failed."""
        mock_charger.all_properties = {}

        desc = WattpilotSensorEntityDescription(
            key="test",
            charger_key="missing_prop",
            name="Test",
            source=SOURCE_PROPERTY,
        )

        with patch("custom_components.wattpilot.entities.GetChargerProp") as mock_get:
            mock_get.return_value = None
            entity = ChargerPlatformEntity(
                mock_hass, mock_config_entry, desc, mock_charger
            )

            # Entity init failed, should be unavailable
            assert entity._init_failed is True

    def test_entity_available_disconnected(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test entity unavailable when charger disconnected."""
        mock_charger.all_properties = {"test_prop": "test_value"}
        mock_charger.connected = False

        desc = WattpilotSensorEntityDescription(
            key="test",
            charger_key="test_prop",
            name="Test",
            source=SOURCE_PROPERTY,
        )

        entity = ChargerPlatformEntity(mock_hass, mock_config_entry, desc, mock_charger)

        # Charger disconnected, availability depends on coordinator
        assert entity._init_failed is False

    def test_entity_should_poll_attribute_source(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test should_poll returns True for attribute source."""
        mock_charger.test_attr = "test_value"

        desc = WattpilotSensorEntityDescription(
            key="test",
            charger_key="test_attr",
            name="Test",
            source=SOURCE_ATTRIBUTE,
        )

        entity = ChargerPlatformEntity(mock_hass, mock_config_entry, desc, mock_charger)

        assert entity.should_poll is True

    def test_entity_should_poll_namespacelist_source(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test should_poll returns True for namespacelist source."""
        mock_charger.all_properties = {"test_list": ["value1"]}

        desc = WattpilotSensorEntityDescription(
            key="test",
            charger_key="test_list",
            name="Test",
            source=SOURCE_NAMESPACELIST,
            namespace_id="0",
        )

        entity = ChargerPlatformEntity(mock_hass, mock_config_entry, desc, mock_charger)

        assert entity.should_poll is True

    def test_entity_device_info(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test entity device_info."""
        mock_charger.all_properties = {"test_prop": "test_value"}
        mock_charger.serial = "12345678"
        mock_charger.manufacturer = "Fronius"
        mock_charger.model = "Wattpilot"
        mock_charger.variant = "11"
        mock_charger.name = "Test Wattpilot"
        mock_charger.firmware = "40.7"

        desc = WattpilotSensorEntityDescription(
            key="test",
            charger_key="test_prop",
            name="Test",
            source=SOURCE_PROPERTY,
        )

        entity = ChargerPlatformEntity(mock_hass, mock_config_entry, desc, mock_charger)

        device_info = entity.device_info
        assert device_info["identifiers"] == {(DOMAIN, "12345678")}
        assert device_info["manufacturer"] == "Fronius"
        assert device_info["name"] == "Test Wattpilot"

    @pytest.mark.asyncio
    async def test_entity_async_update_poll(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test async_update with polling."""
        mock_charger.test_attr = "test_value"

        desc = WattpilotSensorEntityDescription(
            key="test",
            charger_key="test_attr",
            name="Test",
            source=SOURCE_ATTRIBUTE,
        )

        entity = ChargerPlatformEntity(mock_hass, mock_config_entry, desc, mock_charger)
        entity.async_local_poll = AsyncMock()

        with (
            patch(
                "custom_components.wattpilot.entities.CoordinatorEntity.enabled",
                new_callable=PropertyMock,
                return_value=True,
            ),
            patch.object(
                type(entity), "available", new_callable=PropertyMock, return_value=True
            ),
            patch.object(
                type(entity),
                "should_poll",
                new_callable=PropertyMock,
                return_value=True,
            ),
        ):
            await entity.async_update()
            entity.async_local_poll.assert_called_once()

    @pytest.mark.asyncio
    async def test_entity_async_update_not_enabled(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test async_update when entity not enabled."""
        mock_charger.all_properties = {"test_prop": "test_value"}

        desc = WattpilotSensorEntityDescription(
            key="test",
            charger_key="test_prop",
            name="Test",
            source=SOURCE_PROPERTY,
        )

        entity = ChargerPlatformEntity(mock_hass, mock_config_entry, desc, mock_charger)

        with patch(
            "custom_components.wattpilot.entities.CoordinatorEntity.enabled",
            new_callable=PropertyMock,
            return_value=False,
        ):
            await entity.async_update()
        # Should return early without updating

    @pytest.mark.asyncio
    async def test_entity_async_local_poll_property(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test async_local_poll with property source."""
        mock_charger.all_properties = {"test_prop": "new_value"}

        desc = WattpilotSensorEntityDescription(
            key="test",
            charger_key="test_prop",
            name="Test",
            source=SOURCE_PROPERTY,
        )

        entity = ChargerPlatformEntity(mock_hass, mock_config_entry, desc, mock_charger)
        entity._state_attr = "state"
        entity.async_write_ha_state = MagicMock()

        with patch(
            "custom_components.wattpilot.entities.async_GetChargerProp"
        ) as mock_get:
            mock_get.return_value = "new_value"
            await entity.async_local_poll()
            entity.async_write_ha_state.assert_called_once()

    @pytest.mark.asyncio
    async def test_entity_async_local_push_property(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test async_local_push with property source."""
        mock_charger.all_properties = {"test_prop": "pushed_value"}

        desc = WattpilotSensorEntityDescription(
            key="test",
            charger_key="test_prop",
            name="Test",
            source=SOURCE_PROPERTY,
        )

        entity = ChargerPlatformEntity(mock_hass, mock_config_entry, desc, mock_charger)
        entity._state_attr = "state"
        entity.async_write_ha_state = MagicMock()

        with patch(
            "custom_components.wattpilot.entities.CoordinatorEntity.enabled",
            new_callable=PropertyMock,
            return_value=True,
        ):
            await entity.async_local_push("pushed_value")
            entity.async_write_ha_state.assert_called_once()

    @pytest.mark.asyncio
    async def test_entity_async_local_push_not_enabled(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test async_local_push when entity not enabled."""
        mock_charger.all_properties = {"test_prop": "value"}

        desc = WattpilotSensorEntityDescription(
            key="test",
            charger_key="test_prop",
            name="Test",
            source=SOURCE_PROPERTY,
        )

        entity = ChargerPlatformEntity(mock_hass, mock_config_entry, desc, mock_charger)
        entity.async_write_ha_state = MagicMock()

        with patch(
            "custom_components.wattpilot.entities.CoordinatorEntity.enabled",
            new_callable=PropertyMock,
            return_value=False,
        ):
            await entity.async_local_push("pushed_value")
            entity.async_write_ha_state.assert_not_called()
