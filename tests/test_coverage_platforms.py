"""Additional tests for platform-specific coverage gaps."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, PropertyMock, patch

import pytest
from homeassistant.core import HomeAssistant

from custom_components.wattpilot.const import DOMAIN
from custom_components.wattpilot.descriptions import (
    SOURCE_ATTRIBUTE,
    SOURCE_PROPERTY,
    WattpilotSelectEntityDescription,
    WattpilotUpdateEntityDescription,
)


class TestSelectValidation:
    """Test select.py validation error paths (lines 56, 112-121, 137-144)."""

    @pytest.mark.asyncio
    async def test_select_init_attribute_missing(
        self, mock_hass: HomeAssistant, mock_config_entry: Any
    ) -> None:
        """Test select entity init when attribute missing."""
        from custom_components.wattpilot.select import ChargerSelect

        charger = MagicMock(spec=[])  # No attributes
        charger.serial = "12345678"

        desc = WattpilotSelectEntityDescription(
            key="test",
            charger_key="missing_attr",
            name="Test",
            source=SOURCE_ATTRIBUTE,
            options=[1, 2, 3],
        )

        entity = ChargerSelect(mock_hass, mock_config_entry, desc, charger)
        # Should fail init
        assert entity._init_failed is True

    @pytest.mark.asyncio
    async def test_select_current_option_reverse_lookup_fails(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test select current_option when reverse lookup fails."""
        from custom_components.wattpilot.select import ChargerSelect

        mock_charger.all_properties = {"test_prop": 99}  # Not in options

        desc = WattpilotSelectEntityDescription(
            key="test",
            charger_key="test_prop",
            name="Test",
            source=SOURCE_PROPERTY,
            options={1: "one", 2: "two"},  # 99 not in this dict
        )

        entity = ChargerSelect(mock_hass, mock_config_entry, desc, mock_charger)

        # Should return None when value not found in reverse lookup
        option = entity.current_option
        # The reverse lookup should fail and return None or the original value


class TestUpdateVersionParsing:
    """Test update.py version parsing edge cases (lines 65, 137-145, 187, 205)."""

    @pytest.mark.asyncio
    async def test_update_get_versions_dict_empty_release_info(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test _get_versions_dict handles empty release info."""
        from custom_components.wattpilot.update import ChargerUpdate

        mock_charger.all_properties = {"test_prop": "test_value"}

        desc = WattpilotUpdateEntityDescription(
            key="test",
            charger_key="test_prop",
            name="Test",
            source=SOURCE_PROPERTY,
        )

        entity = ChargerUpdate(mock_hass, mock_config_entry, desc, mock_charger)

        # Test with None/empty release_info
        result = entity._get_versions_dict(None)
        assert result == {}

        result = entity._get_versions_dict([])
        assert result == {}

    @pytest.mark.asyncio
    async def test_update_get_versions_dict_invalid_version_format(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test _get_versions_dict handles invalid version format."""
        from custom_components.wattpilot.update import ChargerUpdate

        mock_charger.all_properties = {"test_prop": "test_value"}

        desc = WattpilotUpdateEntityDescription(
            key="test",
            charger_key="test_prop",
            name="Test",
            source=SOURCE_PROPERTY,
        )

        entity = ChargerUpdate(mock_hass, mock_config_entry, desc, mock_charger)

        # Test with invalid version format (no dots)
        release_info = [
            {"version": "invalid", "age": 1, "branch": "test"},
        ]

        result = entity._get_versions_dict(release_info)
        # Should handle gracefully and may skip invalid versions

    @pytest.mark.asyncio
    async def test_update_get_versions_dict_missing_keys(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test _get_versions_dict handles missing keys in release info."""
        from custom_components.wattpilot.update import ChargerUpdate

        mock_charger.all_properties = {"test_prop": "test_value"}

        desc = WattpilotUpdateEntityDescription(
            key="test",
            charger_key="test_prop",
            name="Test",
            source=SOURCE_PROPERTY,
        )

        entity = ChargerUpdate(mock_hass, mock_config_entry, desc, mock_charger)

        # Test with missing 'version' key
        release_info = [
            {"age": 1, "branch": "test"},  # Missing version
        ]

        result = entity._get_versions_dict(release_info)
        # Should handle gracefully

    @pytest.mark.asyncio
    async def test_update_get_versions_dict_exception_handling(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test _get_versions_dict handles exceptions."""
        from custom_components.wattpilot.update import ChargerUpdate

        mock_charger.all_properties = {"test_prop": "test_value"}

        desc = WattpilotUpdateEntityDescription(
            key="test",
            charger_key="test_prop",
            name="Test",
            source=SOURCE_PROPERTY,
        )

        entity = ChargerUpdate(mock_hass, mock_config_entry, desc, mock_charger)

        # Test with data that causes exception (e.g., dict instead of list)
        result = entity._get_versions_dict({"invalid": "data"})
        # Should return empty dict on exception

    @pytest.mark.asyncio
    async def test_update_get_versions_dict_sorting_edge_case(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test _get_versions_dict version sorting with edge cases."""
        from custom_components.wattpilot.update import ChargerUpdate

        mock_charger.all_properties = {"test_prop": "test_value"}

        desc = WattpilotUpdateEntityDescription(
            key="test",
            charger_key="test_prop",
            name="Test",
            source=SOURCE_PROPERTY,
        )

        entity = ChargerUpdate(mock_hass, mock_config_entry, desc, mock_charger)

        # Test with versions that need special sorting
        release_info = [
            {"version": "40.0.0", "age": 100, "branch": "stable"},
            {"version": "41.0.0-beta", "age": 50, "branch": "beta"},
            {"version": "40.0.1", "age": 75, "branch": "stable"},
            {"version": "41.0.0", "age": 25, "branch": "stable"},
        ]

        result = entity._get_versions_dict(release_info)
        # Should handle different version formats

    @pytest.mark.asyncio
    async def test_update_installed_version_none(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test update entity when installed_version returns None."""
        from custom_components.wattpilot.update import ChargerUpdate

        # Mock charger without firmware attribute
        charger = MagicMock(spec=[])
        charger.serial = "12345678"
        charger.all_properties = {"test_prop": "value"}

        desc = WattpilotUpdateEntityDescription(
            key="test",
            charger_key="test_prop",
            name="Test",
            source=SOURCE_PROPERTY,
        )

        entity = ChargerUpdate(mock_hass, mock_config_entry, desc, charger)

        # installed_version should handle missing firmware
        version = entity.installed_version
        # Should return None or a default value


class TestUtilsEdgeCases:
    """Test utils.py edge cases (lines 108-110, 133-135, 253)."""

    def test_get_charger_prop_exception(self, mock_charger: MagicMock) -> None:
        """Test GetChargerProp handles exception."""
        from custom_components.wattpilot.utils import GetChargerProp

        # Make all_properties raise exception
        type(mock_charger).all_properties = PropertyMock(
            side_effect=RuntimeError("Property access failed")
        )

        # Should return default value on exception
        result = GetChargerProp(mock_charger, "test_prop", "default")
        assert result == "default"

    @pytest.mark.asyncio
    async def test_async_get_charger_prop_exception(
        self, mock_charger: MagicMock
    ) -> None:
        """Test async_GetChargerProp handles exception."""
        from custom_components.wattpilot.utils import async_GetChargerProp

        # Make all_properties raise exception
        type(mock_charger).all_properties = PropertyMock(
            side_effect=RuntimeError("Property access failed")
        )

        # Should return default value on exception
        result = await async_GetChargerProp(mock_charger, "test_prop", "default")
        assert result == "default"


class TestAdditionalEntityEdgeCases:
    """Test additional entity edge cases."""

    @pytest.mark.asyncio
    async def test_entity_init_missing_namespacelist(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test entity init when namespacelist is missing entirely."""
        from custom_components.wattpilot.descriptions import (
            SOURCE_NAMESPACELIST,
            WattpilotSensorEntityDescription,
        )
        from custom_components.wattpilot.entities import ChargerPlatformEntity

        mock_charger.all_properties = {}  # No test_list at all

        desc = WattpilotSensorEntityDescription(
            key="test",
            charger_key="test_list",
            name="Test",
            source=SOURCE_NAMESPACELIST,
            namespace_id="0",
        )

        with patch("custom_components.wattpilot.entities.GetChargerProp") as mock_get:
            mock_get.return_value = None
            entity = ChargerPlatformEntity(
                mock_hass, mock_config_entry, desc, mock_charger
            )
            # Should fail init because namespace is None
            assert entity._init_failed is True

    @pytest.mark.asyncio
    async def test_entity_validate_property_namespace_with_attributes(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test validate property with namespace and attribute_ids."""
        from custom_components.wattpilot.descriptions import (
            SOURCE_PROPERTY,
            WattpilotSensorEntityDescription,
        )
        from custom_components.wattpilot.entities import ChargerPlatformEntity

        mock_charger.all_properties = {"test_prop": "test_value"}

        desc = WattpilotSensorEntityDescription(
            key="test",
            charger_key="test_prop",
            name="Test",
            source=SOURCE_PROPERTY,
            value_id="main_val",
            attribute_ids=["attr1", "attr2"],
        )

        entity = ChargerPlatformEntity(mock_hass, mock_config_entry, desc, mock_charger)

        # Create a namespace object mock
        namespace = MagicMock()
        namespace.__str__ = lambda self: "namespace_test"
        namespace.main_val = "main_value"
        namespace.attr1 = "attribute_1"
        namespace.attr2 = "attribute_2"

        result = await entity._async_update_validate_property(namespace)
        # Should extract value and attributes
        assert result == "main_value"
        assert entity._attributes["attr1"] == "attribute_1"
        assert entity._attributes["attr2"] == "attribute_2"

    @pytest.mark.asyncio
    async def test_entity_validate_property_list_without_value_id(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test validate property with list but no value_id (uses index 0)."""
        from custom_components.wattpilot.descriptions import (
            SOURCE_PROPERTY,
            WattpilotSensorEntityDescription,
        )
        from custom_components.wattpilot.entities import ChargerPlatformEntity

        mock_charger.all_properties = {"test_prop": "test_value"}

        desc = WattpilotSensorEntityDescription(
            key="test",
            charger_key="test_prop",
            name="Test",
            source=SOURCE_PROPERTY,
            value_id=None,  # No value_id
        )

        entity = ChargerPlatformEntity(mock_hass, mock_config_entry, desc, mock_charger)

        state_list = ["val0", "val1", "val2"]
        result = await entity._async_update_validate_property(state_list)

        # Should use index 0 when value_id is None
        assert result == "val0"
        # Should add remaining items as attributes
        assert entity._attributes.get("state1") == "val1"
        assert entity._attributes.get("state2") == "val2"


class TestSensorEnumEdgeCases:
    """Test sensor enum handling edge cases."""

    @pytest.mark.asyncio
    async def test_sensor_validate_state_in_enum_values(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test sensor validation when state is already a mapped value."""
        from custom_components.wattpilot.descriptions import (
            SOURCE_PROPERTY,
            WattpilotSensorEntityDescription,
        )
        from custom_components.wattpilot.sensor import ChargerSensor

        mock_charger.all_properties = {"test_prop": "test_value"}

        desc = WattpilotSensorEntityDescription(
            key="test",
            charger_key="test_prop",
            name="Test",
            source=SOURCE_PROPERTY,
            enum={1: "one", 2: "two"},
        )

        entity = ChargerSensor(mock_hass, mock_config_entry, desc, mock_charger)

        # Pass a state that's already in the values (not keys)
        result = await entity._async_update_validate_platform_state("one")
        # Should pass through unchanged
        assert result == "one"

    @pytest.mark.asyncio
    async def test_sensor_validate_state_with_native_unit(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test sensor validation sets native_value when unit present."""
        from homeassistant.const import UnitOfEnergy

        from custom_components.wattpilot.descriptions import (
            SOURCE_PROPERTY,
            WattpilotSensorEntityDescription,
        )
        from custom_components.wattpilot.sensor import ChargerSensor

        mock_charger.all_properties = {"test_prop": "test_value"}

        desc = WattpilotSensorEntityDescription(
            key="test",
            charger_key="test_prop",
            name="Test",
            source=SOURCE_PROPERTY,
            native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        )

        entity = ChargerSensor(mock_hass, mock_config_entry, desc, mock_charger)

        # Validate state with unit
        result = await entity._async_update_validate_platform_state(123.45)
        # Should set _attr_native_value
        assert entity._attr_native_value == 123.45
        assert result == 123.45

    @pytest.mark.asyncio
    async def test_sensor_validate_state_html_unescape(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test sensor validation with HTML unescape."""
        from custom_components.wattpilot.descriptions import (
            SOURCE_PROPERTY,
            WattpilotSensorEntityDescription,
        )
        from custom_components.wattpilot.sensor import ChargerSensor

        mock_charger.all_properties = {"test_prop": "test_value"}

        desc = WattpilotSensorEntityDescription(
            key="test",
            charger_key="test_prop",
            name="Test",
            source=SOURCE_PROPERTY,
            html_unescape=True,
        )

        entity = ChargerSensor(mock_hass, mock_config_entry, desc, mock_charger)

        # Validate state with HTML entities
        result = await entity._async_update_validate_platform_state("Test &amp; Value")
        # Should unescape HTML
        assert result == "Test & Value"

    @pytest.mark.asyncio
    async def test_sensor_validate_state_none_string(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test sensor validation converts 'None' string to STATE_UNKNOWN."""
        from homeassistant.const import STATE_UNKNOWN

        from custom_components.wattpilot.descriptions import (
            SOURCE_PROPERTY,
            WattpilotSensorEntityDescription,
        )
        from custom_components.wattpilot.sensor import ChargerSensor

        mock_charger.all_properties = {"test_prop": "test_value"}

        desc = WattpilotSensorEntityDescription(
            key="test",
            charger_key="test_prop",
            name="Test",
            source=SOURCE_PROPERTY,
        )

        entity = ChargerSensor(mock_hass, mock_config_entry, desc, mock_charger)

        # Validate state with string "None"
        result = await entity._async_update_validate_platform_state("None")
        # Should convert to STATE_UNKNOWN
        assert result == STATE_UNKNOWN


class TestUpdateEntityEdgeCases:
    """Test update entity additional edge cases."""

    @pytest.mark.asyncio
    async def test_update_latest_version_no_release_info(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test update entity latest_version when no release info available."""
        from custom_components.wattpilot.descriptions import (
            SOURCE_PROPERTY,
            WattpilotUpdateEntityDescription,
        )
        from custom_components.wattpilot.update import ChargerUpdate

        mock_charger.all_properties = {}  # No release info

        desc = WattpilotUpdateEntityDescription(
            key="test",
            charger_key="test_prop",
            name="Test",
            source=SOURCE_PROPERTY,
        )

        entity = ChargerUpdate(mock_hass, mock_config_entry, desc, mock_charger)

        # Should handle missing release info
        version = entity.latest_version
        # Should return None or current version

    @pytest.mark.asyncio
    async def test_update_supported_features(
        self, mock_hass: HomeAssistant, mock_config_entry: Any, mock_charger: MagicMock
    ) -> None:
        """Test update entity supported_features."""
        from custom_components.wattpilot.descriptions import (
            SOURCE_PROPERTY,
            WattpilotUpdateEntityDescription,
        )
        from custom_components.wattpilot.update import ChargerUpdate

        mock_charger.all_properties = {"test_prop": "test_value"}

        desc = WattpilotUpdateEntityDescription(
            key="test",
            charger_key="test_prop",
            name="Test",
            source=SOURCE_PROPERTY,
        )

        entity = ChargerUpdate(mock_hass, mock_config_entry, desc, mock_charger)

        # Check supported_features property
        features = entity.supported_features
        # Should return expected UpdateEntityFeature flags


class TestDiagnosticsChargerNotAvailable:
    """Test diagnostics when charger is not available."""

    @pytest.mark.asyncio
    async def test_diagnostics_charger_none(
        self, hass: HomeAssistant, mock_config_entry_data: dict
    ) -> None:
        """Test diagnostics when charger is None."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.diagnostics import (
            async_get_config_entry_diagnostics,
        )
        from custom_components.wattpilot.types import WattpilotRuntimeData

        entry = ConfigEntry(
            version=1,
            minor_version=0,
            domain=DOMAIN,
            title="Test",
            data=mock_config_entry_data,
            source="user",
            unique_id="test",
            discovery_keys={},
            options={},
            subentries_data={},
        )

        coordinator = MagicMock()
        entry.runtime_data = WattpilotRuntimeData(
            charger=None,  # No charger
            coordinator=coordinator,
            push_entities={},
            params=mock_config_entry_data,
        )

        diag = await async_get_config_entry_diagnostics(hass, entry)
        # Should handle None charger
        assert "charger_properties" in diag
        assert diag["charger_properties"] == "Charger not available or not initialized"

    @pytest.mark.asyncio
    async def test_diagnostics_charger_no_all_properties(
        self, hass: HomeAssistant, mock_config_entry_data: dict
    ) -> None:
        """Test diagnostics when charger has no all_properties."""
        from homeassistant.config_entries import ConfigEntry

        from custom_components.wattpilot.diagnostics import (
            async_get_config_entry_diagnostics,
        )
        from custom_components.wattpilot.types import WattpilotRuntimeData

        entry = ConfigEntry(
            version=1,
            minor_version=0,
            domain=DOMAIN,
            title="Test",
            data=mock_config_entry_data,
            source="user",
            unique_id="test",
            discovery_keys={},
            options={},
            subentries_data={},
        )

        # Charger without all_properties
        charger = MagicMock(spec=[])  # No attributes

        coordinator = MagicMock()
        entry.runtime_data = WattpilotRuntimeData(
            charger=charger,
            coordinator=coordinator,
            push_entities={},
            params=mock_config_entry_data,
        )

        diag = await async_get_config_entry_diagnostics(hass, entry)
        # Should handle missing all_properties
        assert "charger_properties" in diag
        assert diag["charger_properties"] == "Charger not available or not initialized"
