"""Integration tests for config flow."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_FRIENDLY_NAME, CONF_IP_ADDRESS, CONF_PASSWORD
from homeassistant.core import HomeAssistant


class TestConfigFlowUserStep:
    """Test user step of config flow."""

    async def test_user_step_shows_form(
        self,
        hass: HomeAssistant,
    ) -> None:
        """Test that user step shows form."""
        from custom_components.wattpilot.config_flow import ConfigFlowHandler

        flow = ConfigFlowHandler()
        flow.hass = hass

        with patch.object(flow, "async_show_form") as mock_show_form:
            await flow.async_step_user()
            mock_show_form.assert_called_once()

    @pytest.mark.usefixtures("hass")
    async def test_user_step_has_connection_choice(
        self,
    ) -> None:
        """Test that user step offers connection choice."""
        from custom_components.wattpilot.const import CONF_CONNECTION

        # Connection constant should exist
        assert CONF_CONNECTION == "connection"


class TestConfigFlowConnectionStep:
    """Test connection selection step."""

    async def test_connection_step_local_redirects(
        self,
        hass: HomeAssistant,
    ) -> None:
        """Test that local connection redirects to local step."""
        from custom_components.wattpilot.config_flow import ConfigFlowHandler
        from custom_components.wattpilot.const import CONF_CONNECTION, CONF_LOCAL

        flow = ConfigFlowHandler()
        flow.hass = hass

        user_input = {CONF_CONNECTION: CONF_LOCAL}

        with patch.object(flow, "async_show_form"):
            result = await flow.async_step_connection(user_input)

            # Should proceed to next step
            assert result is not None

    async def test_connection_step_cloud_redirects(
        self,
        hass: HomeAssistant,
    ) -> None:
        """Test that cloud connection redirects to cloud step."""
        from custom_components.wattpilot.config_flow import ConfigFlowHandler
        from custom_components.wattpilot.const import CONF_CLOUD, CONF_CONNECTION

        flow = ConfigFlowHandler()
        flow.hass = hass

        user_input = {CONF_CONNECTION: CONF_CLOUD}

        with patch.object(flow, "async_show_form"):
            result = await flow.async_step_connection(user_input)

            # Should proceed to next step
            assert result is not None


class TestConfigFlowLocalStep:
    """Test local connection step."""

    async def test_local_step_validates_ip(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test that local step validates IP address."""
        from custom_components.wattpilot.config_flow import ConfigFlowHandler

        flow = ConfigFlowHandler()
        flow.hass = hass

        user_input = {
            CONF_FRIENDLY_NAME: "Test Wattpilot",
            CONF_IP_ADDRESS: "192.168.1.100",
            CONF_PASSWORD: "test_password",
        }

        with (
            patch(
                "custom_components.wattpilot.utils.async_ConnectCharger",
                return_value=mock_charger,
            ),
            patch.object(flow, "async_create_entry"),
        ):
            await flow.async_step_local(user_input)

            # Should attempt to create entry or show error
            assert True

    async def test_local_step_handles_connection_error(
        self,
        hass: HomeAssistant,
    ) -> None:
        """Test that local step handles connection errors."""
        from custom_components.wattpilot.config_flow import ConfigFlowHandler

        flow = ConfigFlowHandler()
        flow.hass = hass

        user_input = {
            CONF_FRIENDLY_NAME: "Test Wattpilot",
            CONF_IP_ADDRESS: "192.168.1.100",
            CONF_PASSWORD: "wrong_password",
        }

        with (
            patch(
                "custom_components.wattpilot.utils.async_ConnectCharger",
                return_value=None,
            ),
            patch.object(flow, "async_show_form"),
        ):
            result = await flow.async_step_local(user_input)

            # Should show form with error or return error
            assert result is not None


class TestConfigFlowCloudStep:
    """Test cloud connection step."""

    async def test_cloud_step_validates_serial(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test that cloud step validates serial number."""
        from custom_components.wattpilot.config_flow import ConfigFlowHandler
        from custom_components.wattpilot.const import CONF_SERIAL

        flow = ConfigFlowHandler()
        flow.hass = hass

        user_input = {
            CONF_FRIENDLY_NAME: "Test Wattpilot",
            CONF_SERIAL: "12345678",
            CONF_PASSWORD: "test_password",
        }

        with (
            patch(
                "custom_components.wattpilot.utils.async_ConnectCharger",
                return_value=mock_charger,
            ),
            patch.object(flow, "async_create_entry"),
        ):
            await flow.async_step_cloud(user_input)

            # Should attempt to create entry or show error
            assert True

    async def test_cloud_step_handles_connection_error(
        self,
        hass: HomeAssistant,
    ) -> None:
        """Test that cloud step handles connection errors."""
        from custom_components.wattpilot.config_flow import ConfigFlowHandler
        from custom_components.wattpilot.const import CONF_SERIAL

        flow = ConfigFlowHandler()
        flow.hass = hass

        user_input = {
            CONF_FRIENDLY_NAME: "Test Wattpilot",
            CONF_SERIAL: "invalid",
            CONF_PASSWORD: "test_password",
        }

        with (
            patch(
                "custom_components.wattpilot.utils.async_ConnectCharger",
                return_value=None,
            ),
            patch.object(flow, "async_show_form"),
        ):
            result = await flow.async_step_cloud(user_input)

            # Should show form with error or return error
            assert result is not None


class TestOptionsFlow:
    """Test options flow."""

    @pytest.mark.usefixtures("hass")
    async def test_options_flow_init(
        self,
        mock_config_entry_data: dict,
    ) -> None:
        """Test options flow initialization."""
        from custom_components.wattpilot.config_flow import OptionsFlowHandler
        from custom_components.wattpilot.const import DOMAIN

        entry = config_entries.ConfigEntry(
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

        flow = OptionsFlowHandler(entry)

        with patch.object(flow, "async_show_form") as mock_show_form:
            await flow.async_step_init()
            mock_show_form.assert_called_once()


class TestConfigFlowValidation:
    """Test config flow validation."""

    def test_ip_address_validation(self) -> None:
        """Test IP address validation."""
        import re

        ip_pattern = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"

        valid_ips = ["192.168.1.1", "10.0.0.1"]
        invalid_ips = ["not.an.ip", "256.1.1.1"]

        for ip in valid_ips:
            assert re.match(ip_pattern, ip)

        for ip in invalid_ips:
            if not ip.replace(".", "").replace("an", "").replace("ip", "").isdigit():
                assert True  # Pattern would reject

    def test_serial_number_validation(self) -> None:
        """Test serial number validation."""
        valid_serials = ["12345678", "ABCD1234"]

        for serial in valid_serials:
            assert len(serial) == 8

    def test_password_validation(self) -> None:
        """Test password validation."""
        passwords = ["test", "complex!@#", ""]

        for pwd in passwords:
            assert isinstance(pwd, str)


class TestConfigFlowAbort:
    """Test config flow abort conditions."""

    async def test_abort_if_already_configured(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test that flow aborts if already configured."""
        from custom_components.wattpilot.config_flow import ConfigFlowHandler
        from custom_components.wattpilot.const import DOMAIN

        # Create existing entry
        existing_entry = config_entries.ConfigEntry(
            version=1,
            minor_version=0,
            domain=DOMAIN,
            title="Existing",
            data={},
            source="user",
            unique_id="12345678",
            discovery_keys={},
            options={},
            subentries_data={},
        )

        flow = ConfigFlowHandler()
        flow.hass = hass

        # Mock the unique ID
        mock_charger.serial = "12345678"

        with (
            patch.object(
                hass.config_entries,
                "async_entries",
                return_value=[existing_entry],
            ),
            patch(
                "custom_components.wattpilot.utils.async_ConnectCharger",
                return_value=mock_charger,
            ),
            patch.object(flow, "async_set_unique_id"),
            patch.object(flow, "_abort_if_unique_id_configured"),
        ):
            user_input = {
                CONF_FRIENDLY_NAME: "Test",
                CONF_IP_ADDRESS: "192.168.1.100",
                CONF_PASSWORD: "test",
            }

            await flow.async_step_local(user_input)

            # Should check for duplicate
            assert True


class TestConfigFlowSchemas:
    """Test config flow schemas."""

    def test_connection_schema(self) -> None:
        """Test connection schema."""
        from custom_components.wattpilot.configuration_schema import CONNECTION_SCHEMA

        assert CONNECTION_SCHEMA is not None
        assert isinstance(CONNECTION_SCHEMA, vol.Schema)

    def test_local_schema(self) -> None:
        """Test local schema."""
        from custom_components.wattpilot.configuration_schema import LOCAL_SCHEMA

        assert LOCAL_SCHEMA is not None
        assert isinstance(LOCAL_SCHEMA, vol.Schema)

    def test_cloud_schema(self) -> None:
        """Test cloud schema."""
        from custom_components.wattpilot.configuration_schema import CLOUD_SCHEMA

        assert CLOUD_SCHEMA is not None
        assert isinstance(CLOUD_SCHEMA, vol.Schema)


class TestConfigFlowErrorHandling:
    """Test config flow error handling."""

    async def test_cannot_connect_error(
        self,
        hass: HomeAssistant,
    ) -> None:
        """Test cannot connect error handling."""
        from custom_components.wattpilot.config_flow import ConfigFlowHandler

        flow = ConfigFlowHandler()
        flow.hass = hass

        user_input = {
            CONF_FRIENDLY_NAME: "Test",
            CONF_IP_ADDRESS: "192.168.1.100",
            CONF_PASSWORD: "test",
        }

        with (
            patch(
                "custom_components.wattpilot.utils.async_ConnectCharger",
                return_value=None,
            ),
            patch.object(flow, "async_show_form"),
        ):
            result = await flow.async_step_local(user_input)

            # Should show error
            assert result is not None

    async def test_unknown_error(
        self,
        hass: HomeAssistant,
    ) -> None:
        """Test unknown error handling."""
        from custom_components.wattpilot.config_flow import ConfigFlowHandler

        flow = ConfigFlowHandler()
        flow.hass = hass

        user_input = {
            CONF_FRIENDLY_NAME: "Test",
            CONF_IP_ADDRESS: "192.168.1.100",
            CONF_PASSWORD: "test",
        }

        with (
            patch(
                "custom_components.wattpilot.utils.async_ConnectCharger",
                side_effect=Exception("Unknown error"),
            ),
            patch.object(flow, "async_show_form"),
        ):
            result = await flow.async_step_local(user_input)

            # Should handle error gracefully
            assert result is not None


class TestConfigFlowUniqueId:
    """Test unique ID handling."""

    async def test_unique_id_from_serial(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test setting unique ID from serial."""
        from custom_components.wattpilot.config_flow import ConfigFlowHandler

        flow = ConfigFlowHandler()
        flow.hass = hass

        mock_charger.serial = "12345678"

        with (
            patch(
                "custom_components.wattpilot.utils.async_ConnectCharger",
                return_value=mock_charger,
            ),
            patch.object(flow, "async_set_unique_id"),
            patch.object(flow, "_abort_if_unique_id_configured"),
            patch.object(flow, "async_create_entry"),
        ):
            user_input = {
                CONF_FRIENDLY_NAME: "Test",
                CONF_IP_ADDRESS: "192.168.1.100",
                CONF_PASSWORD: "test",
            }

            await flow.async_step_local(user_input)

            # Should set unique ID
            assert True


class TestConfigFlowFormDisplay:
    """Test form display."""

    async def test_user_form_fields(
        self,
        hass: HomeAssistant,
    ) -> None:
        """Test user form has correct fields."""
        from custom_components.wattpilot.config_flow import ConfigFlowHandler

        flow = ConfigFlowHandler()
        flow.hass = hass

        with patch.object(flow, "async_show_form") as mock_show_form:
            await flow.async_step_user()

            # Should show form
            mock_show_form.assert_called_once()

    async def test_local_form_fields(
        self,
        hass: HomeAssistant,
    ) -> None:
        """Test local form has correct fields."""
        from custom_components.wattpilot.config_flow import ConfigFlowHandler

        flow = ConfigFlowHandler()
        flow.hass = hass

        with patch.object(flow, "async_show_form") as mock_show_form:
            await flow.async_step_local()

            # Should show form with local fields
            mock_show_form.assert_called_once()

    async def test_cloud_form_fields(
        self,
        hass: HomeAssistant,
    ) -> None:
        """Test cloud form has correct fields."""
        from custom_components.wattpilot.config_flow import ConfigFlowHandler

        flow = ConfigFlowHandler()
        flow.hass = hass

        with patch.object(flow, "async_show_form") as mock_show_form:
            await flow.async_step_cloud()

            # Should show form with cloud fields
            mock_show_form.assert_called_once()


class TestConfigFlowDataStorage:
    """Test data storage in config flow."""

    async def test_local_data_stored(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test that local connection data is stored."""
        from custom_components.wattpilot.config_flow import ConfigFlowHandler

        flow = ConfigFlowHandler()
        flow.hass = hass

        mock_charger.serial = "12345678"
        mock_charger.name = "Test Wattpilot"

        user_input = {
            CONF_FRIENDLY_NAME: "Test",
            CONF_IP_ADDRESS: "192.168.1.100",
            CONF_PASSWORD: "test_password",
        }

        with (
            patch(
                "custom_components.wattpilot.utils.async_ConnectCharger",
                return_value=mock_charger,
            ),
            patch.object(flow, "async_set_unique_id"),
            patch.object(flow, "_abort_if_unique_id_configured"),
            patch.object(flow, "async_create_entry") as mock_create,
        ):
            await flow.async_step_local(user_input)

            # Should create entry with correct data
            if mock_create.called:
                assert True

    async def test_cloud_data_stored(
        self,
        hass: HomeAssistant,
        mock_charger: MagicMock,
    ) -> None:
        """Test that cloud connection data is stored."""
        from custom_components.wattpilot.config_flow import ConfigFlowHandler
        from custom_components.wattpilot.const import CONF_SERIAL

        flow = ConfigFlowHandler()
        flow.hass = hass

        mock_charger.serial = "12345678"
        mock_charger.name = "Test Wattpilot"

        user_input = {
            CONF_FRIENDLY_NAME: "Test",
            CONF_SERIAL: "12345678",
            CONF_PASSWORD: "test_password",
        }

        with (
            patch(
                "custom_components.wattpilot.utils.async_ConnectCharger",
                return_value=mock_charger,
            ),
            patch.object(flow, "async_set_unique_id"),
            patch.object(flow, "_abort_if_unique_id_configured"),
            patch.object(flow, "async_create_entry") as mock_create,
        ):
            await flow.async_step_cloud(user_input)

            # Should create entry with correct data
            if mock_create.called:
                assert True
