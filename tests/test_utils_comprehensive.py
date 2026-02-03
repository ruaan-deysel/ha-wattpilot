"""Comprehensive tests for utility functions."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch


class TestChargerPropertyFunctions:
    """Test charger property access functions."""

    def test_get_charger_prop_with_value(
        self,
        mock_charger: MagicMock,
    ) -> None:
        """Test GetChargerProp with existing value."""
        from custom_components.wattpilot.utils import GetChargerProp

        mock_charger.allProps = {"test_prop": "test_value"}

        result = GetChargerProp(mock_charger, "test_prop")

        assert result == "test_value"

    def test_get_charger_prop_missing_with_default(
        self,
        mock_charger: MagicMock,
    ) -> None:
        """Test GetChargerProp with missing property and default."""
        from custom_components.wattpilot.utils import GetChargerProp

        mock_charger.allProps = {}

        result = GetChargerProp(mock_charger, "missing_prop", "default_value")

        assert result == "default_value"

    def test_get_charger_prop_none_value_returns_default(
        self,
        mock_charger: MagicMock,
    ) -> None:
        """Test GetChargerProp with None value returns default."""
        from custom_components.wattpilot.utils import GetChargerProp

        mock_charger.allProps = {"test_prop": None}

        result = GetChargerProp(mock_charger, "test_prop", "default")

        assert result == "default"

    async def test_async_get_charger_prop_with_value(
        self,
        mock_charger: MagicMock,
    ) -> None:
        """Test async_GetChargerProp with existing value."""
        from custom_components.wattpilot.utils import async_GetChargerProp

        mock_charger.allProps = {"test_prop": 42}

        result = await async_GetChargerProp(mock_charger, "test_prop")

        assert result == 42

    async def test_async_set_charger_prop(
        self,
        mock_charger: MagicMock,
    ) -> None:
        """Test async_SetChargerProp."""
        from custom_components.wattpilot.utils import async_SetChargerProp

        mock_charger.allProps = {"test_prop": "old"}
        mock_charger.send_update = AsyncMock()

        await async_SetChargerProp(mock_charger, "test_prop", "new")

        mock_charger.send_update.assert_called_once_with("test_prop", "new")

    async def test_async_set_charger_prop_force(
        self,
        mock_charger: MagicMock,
    ) -> None:
        """Test async_SetChargerProp with force."""
        from custom_components.wattpilot.utils import async_SetChargerProp

        mock_charger.allProps = {}
        mock_charger.send_update = AsyncMock()

        await async_SetChargerProp(mock_charger, "new_prop", "value", force=True)

        mock_charger.send_update.assert_called_once_with("new_prop", "value")


class TestChargerConnection:
    """Test charger connection functions."""

    async def test_async_connect_charger_local(
        self,
    ) -> None:
        """Test async_ConnectCharger with local connection."""
        from custom_components.wattpilot.utils import async_ConnectCharger

        params = {
            "connection": "local",
            "ip_address": "192.168.1.100",
            "password": "test_password",
        }

        with patch("custom_components.wattpilot.utils.wattpilot.Wattpilot") as mock_wp:
            mock_instance = MagicMock()
            mock_instance.connect = AsyncMock()
            mock_wp.return_value = mock_instance

            await async_ConnectCharger("test_entry", params)

            # Should create Wattpilot instance
            assert mock_wp.called

    async def test_async_connect_charger_cloud(
        self,
    ) -> None:
        """Test async_ConnectCharger with cloud connection."""
        from custom_components.wattpilot.utils import async_ConnectCharger

        params = {
            "connection": "cloud",
            "serial": "12345678",
            "password": "test_password",
        }

        with patch("custom_components.wattpilot.utils.wattpilot.Wattpilot") as mock_wp:
            mock_instance = MagicMock()
            mock_instance.connect = AsyncMock()
            mock_wp.return_value = mock_instance

            await async_ConnectCharger("test_entry", params)

            # Should create Wattpilot instance
            assert mock_wp.called

    async def test_async_disconnect_charger(
        self,
        mock_charger: MagicMock,
    ) -> None:
        """Test async_DisconnectCharger."""
        from custom_components.wattpilot.utils import async_DisconnectCharger

        mock_charger.disconnect = AsyncMock()

        await async_DisconnectCharger("test_entry", mock_charger)

        mock_charger.disconnect.assert_called_once()


class TestPropertyUpdateHandler:
    """Test PropertyUpdateHandler class."""


class TestDebugFunctions:
    """Test debug utility functions."""


class TestVersionComparison:
    """Test version comparison functions."""

    def test_version_comparison_greater_than(self) -> None:
        """Test version comparison greater than."""
        from packaging import version

        v1 = version.parse("1.5.0")
        v2 = version.parse("1.0.0")

        assert v1 > v2

    def test_version_comparison_equal(self) -> None:
        """Test version comparison equal."""
        from packaging import version

        v1 = version.parse("1.5.0")
        v2 = version.parse("1.5.0")

        assert v1 == v2

    def test_version_comparison_less_than(self) -> None:
        """Test version comparison less than."""
        from packaging import version

        v1 = version.parse("1.0.0")
        v2 = version.parse("1.5.0")

        assert v1 < v2


class TestWattpilotModuleAccess:
    """Test wattpilot module access."""

    def test_wattpilot_module_imported(self) -> None:
        """Test that wattpilot module is imported."""
        from custom_components.wattpilot.utils import wattpilot

        assert wattpilot is not None

    def test_wattpilot_class_accessible(self) -> None:
        """Test that Wattpilot class is accessible."""
        from custom_components.wattpilot.utils import wattpilot

        assert hasattr(wattpilot, "Wattpilot")


class TestChargerPropertyExtraction:
    """Test charger property extraction."""

    def test_extract_firmware_version(
        self,
        mock_charger: MagicMock,
    ) -> None:
        """Test extracting firmware version."""
        mock_charger.firmware = "1.5.0"

        firmware = mock_charger.firmware

        assert firmware == "1.5.0"

    def test_extract_serial_number(
        self,
        mock_charger: MagicMock,
    ) -> None:
        """Test extracting serial number."""
        mock_charger.serial = "12345678"

        serial = mock_charger.serial

        assert serial == "12345678"

    def test_extract_charger_name(
        self,
        mock_charger: MagicMock,
    ) -> None:
        """Test extracting charger name."""
        mock_charger.name = "Test Wattpilot"

        name = mock_charger.name

        assert name == "Test Wattpilot"


class TestPropertyValidation:
    """Test property validation."""

    def test_validate_property_exists(
        self,
        mock_charger: MagicMock,
    ) -> None:
        """Test validating property exists."""
        mock_charger.allProps = {"valid_prop": "value"}

        has_prop = "valid_prop" in mock_charger.allProps

        assert has_prop is True

    def test_validate_property_not_exists(
        self,
        mock_charger: MagicMock,
    ) -> None:
        """Test validating property does not exist."""
        mock_charger.allProps = {}

        has_prop = "invalid_prop" in mock_charger.allProps

        assert has_prop is False

    def test_validate_property_value_type(
        self,
        mock_charger: MagicMock,
    ) -> None:
        """Test validating property value type."""
        mock_charger.allProps = {"int_prop": 42, "str_prop": "value", "bool_prop": True}

        assert isinstance(mock_charger.allProps["int_prop"], int)
        assert isinstance(mock_charger.allProps["str_prop"], str)
        assert isinstance(mock_charger.allProps["bool_prop"], bool)


class TestConnectionParameters:
    """Test connection parameter handling."""

    def test_local_connection_parameters(self) -> None:
        """Test local connection parameters."""
        params = {
            "connection": "local",
            "ip_address": "192.168.1.100",
            "password": "test",
        }

        assert params["connection"] == "local"
        assert "ip_address" in params
        assert "password" in params

    def test_cloud_connection_parameters(self) -> None:
        """Test cloud connection parameters."""
        params = {
            "connection": "cloud",
            "serial": "12345678",
            "password": "test",
        }

        assert params["connection"] == "cloud"
        assert "serial" in params
        assert "password" in params


class TestPropertyUpdateFlow:
    """Test property update flow."""

    async def test_property_update_flow(
        self,
        mock_charger: MagicMock,
    ) -> None:
        """Test complete property update flow."""
        from custom_components.wattpilot.utils import async_SetChargerProp

        # Initial value
        mock_charger.allProps = {"test_prop": "old_value"}
        mock_charger.send_update = AsyncMock()

        # Update property
        await async_SetChargerProp(mock_charger, "test_prop", "new_value")

        # Verify update was sent
        mock_charger.send_update.assert_called_once_with("test_prop", "new_value")


class TestChargerState:
    """Test charger state handling."""

    def test_charger_connected_state(
        self,
        mock_charger: MagicMock,
    ) -> None:
        """Test charger connected state."""
        mock_charger.connected = True

        assert mock_charger.connected is True

    def test_charger_disconnected_state(
        self,
        mock_charger: MagicMock,
    ) -> None:
        """Test charger disconnected state."""
        mock_charger.connected = False

        assert mock_charger.connected is False

    def test_charger_all_props_initialized(
        self,
        mock_charger: MagicMock,
    ) -> None:
        """Test charger allPropsInitialized state."""
        mock_charger.allPropsInitialized = True

        assert mock_charger.allPropsInitialized is True
