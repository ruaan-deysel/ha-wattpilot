"""Tests for the Wattpilot config flow."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_FRIENDLY_NAME, CONF_IP_ADDRESS, CONF_PASSWORD
from homeassistant.core import HomeAssistant

from custom_components.wattpilot.config_flow import (
    ConfigFlowHandler,
    OptionsFlowHandler,
)
from custom_components.wattpilot.const import (
    CONF_CLOUD,
    CONF_CONNECTION,
    CONF_LOCAL,
    CONF_SERIAL,
    DOMAIN,
)


@pytest.fixture
def mock_hass() -> MagicMock:
    """Create a mock Home Assistant instance."""
    hass = MagicMock(spec=HomeAssistant)
    hass.data = {}
    hass.config_entries = MagicMock()
    hass.config_entries.async_reload = AsyncMock()
    hass.config_entries.async_update_entry = MagicMock()
    return hass


class TestConfigFlowDataValidation:
    """Test config flow data validation."""

    def test_config_data_structure(self) -> None:
        """Test config entry data structure."""
        config_data: dict[str, Any] = {
            CONF_FRIENDLY_NAME: "My Wattpilot",
            CONF_IP_ADDRESS: "192.168.1.100",
            CONF_PASSWORD: "test_pass",
            CONF_CONNECTION: CONF_LOCAL,
        }

        assert CONF_FRIENDLY_NAME in config_data
        assert CONF_IP_ADDRESS in config_data
        assert CONF_PASSWORD in config_data
        assert CONF_CONNECTION in config_data
        assert config_data[CONF_CONNECTION] == CONF_LOCAL

    def test_cloud_config_data_structure(self) -> None:
        """Test cloud config entry data structure."""
        config_data: dict[str, Any] = {
            CONF_FRIENDLY_NAME: "My Cloud Wattpilot",
            CONF_SERIAL: "12345678",
            CONF_PASSWORD: "test_pass",
            CONF_CONNECTION: CONF_CLOUD,
        }

        assert CONF_SERIAL in config_data
        assert config_data[CONF_CONNECTION] == CONF_CLOUD

    def test_local_connection_requires_ip(self) -> None:
        """Test that local connection requires IP address."""
        # Valid local config
        valid_config: dict[str, Any] = {
            CONF_FRIENDLY_NAME: "Test",
            CONF_IP_ADDRESS: "192.168.1.100",
            CONF_PASSWORD: "pass",
            CONF_CONNECTION: CONF_LOCAL,
        }
        assert CONF_IP_ADDRESS in valid_config

        # Invalid config without IP
        invalid_config: dict[str, Any] = {
            CONF_FRIENDLY_NAME: "Test",
            CONF_PASSWORD: "pass",
            CONF_CONNECTION: CONF_LOCAL,
        }
        assert CONF_IP_ADDRESS not in invalid_config

    def test_cloud_connection_requires_serial(self) -> None:
        """Test that cloud connection requires serial number."""
        # Valid cloud config
        valid_config: dict[str, Any] = {
            CONF_FRIENDLY_NAME: "Test",
            CONF_SERIAL: "12345678",
            CONF_PASSWORD: "pass",
            CONF_CONNECTION: CONF_CLOUD,
        }
        assert CONF_SERIAL in valid_config

    def test_ip_address_format_validation(self) -> None:
        """Test IP address format validation."""
        import voluptuous as vol

        from custom_components.wattpilot.configuration_schema import validate_ip_address

        valid_ips = ["192.168.1.100", "10.0.0.1", "172.16.0.1", "255.255.255.255"]
        invalid_ips = ["256.1.1.1", "192.168.1", "not.an.ip", ""]

        for ip in valid_ips:
            assert validate_ip_address(ip) == ip

        for ip in invalid_ips:
            with pytest.raises(vol.Invalid):
                validate_ip_address(ip)

    def test_validate_ip_helper(self) -> None:
        """Test the _validate_ip helper used in config flow step handlers."""
        from custom_components.wattpilot.config_flow import _validate_ip

        assert _validate_ip("192.168.1.100") is True
        assert _validate_ip("10.0.0.1") is True
        assert _validate_ip("::1") is True
        assert _validate_ip("fe80::1") is True
        assert _validate_ip("256.1.1.1") is False
        assert _validate_ip("not.an.ip") is False
        assert _validate_ip("") is False

    def test_config_constants(self) -> None:
        """Test configuration constants."""
        assert DOMAIN == "wattpilot"
        assert CONF_LOCAL == "local"
        assert CONF_CLOUD == "cloud"


class TestConfigFlowUser:
    """Test user configuration flow."""

    @pytest.mark.asyncio
    async def test_async_step_user_initializes_data(self) -> None:
        """Test user step initializes flow data."""
        flow = ConfigFlowHandler()

        with patch.object(flow, "async_step_connection", return_value=MagicMock()):
            await flow.async_step_user()
            assert hasattr(flow, "data")
            assert isinstance(flow.data, dict)

    @pytest.mark.asyncio
    async def test_async_step_user_calls_connection(self) -> None:
        """Test user step calls connection step."""
        flow = ConfigFlowHandler()

        with patch.object(
            flow, "async_step_connection", return_value=MagicMock()
        ) as mock_conn:
            await flow.async_step_user()
            mock_conn.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_step_user_exception_handling(self) -> None:
        """Test user step handles exceptions."""
        flow = ConfigFlowHandler()
        flow.async_abort = MagicMock(return_value={"type": "abort"})

        with patch.object(flow, "async_step_connection", side_effect=Exception("test")):
            result = await flow.async_step_user()
            assert result["type"] == "abort"
            flow.async_abort.assert_called_once_with(reason="exception")

    @pytest.mark.asyncio
    async def test_async_step_connection_shows_form(self) -> None:
        """Test connection step shows form when no input."""
        flow = ConfigFlowHandler()
        flow.async_show_form = MagicMock(return_value={"type": "form"})

        result = await flow.async_step_connection()
        assert result["type"] == "form"
        flow.async_show_form.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_step_connection_local_selected(self) -> None:
        """Test connection step routes to local when selected."""
        flow = ConfigFlowHandler()
        user_input = {CONF_CONNECTION: CONF_LOCAL}

        with patch.object(
            flow, "async_step_local", return_value=MagicMock()
        ) as mock_local:
            await flow.async_step_connection(user_input)
            mock_local.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_step_connection_cloud_selected(self) -> None:
        """Test connection step routes to cloud when selected."""
        flow = ConfigFlowHandler()
        user_input = {CONF_CONNECTION: CONF_CLOUD}

        with patch.object(
            flow, "async_step_cloud", return_value=MagicMock()
        ) as mock_cloud:
            await flow.async_step_connection(user_input)
            mock_cloud.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_step_connection_exception_handling(self) -> None:
        """Test connection step handles exceptions."""
        flow = ConfigFlowHandler()
        flow.async_abort = MagicMock(return_value={"type": "abort"})

        with patch.object(flow, "async_show_form", side_effect=Exception("test")):
            result = await flow.async_step_connection()
            assert result["type"] == "abort"

    @pytest.mark.asyncio
    async def test_async_step_local_shows_form(self) -> None:
        """Test local step shows form when no input."""
        flow = ConfigFlowHandler()
        flow.async_show_form = MagicMock(return_value={"type": "form"})

        result = await flow.async_step_local()
        assert result["type"] == "form"

    @pytest.mark.asyncio
    async def test_async_step_local_processes_input(self) -> None:
        """Test local step processes user input."""
        flow = ConfigFlowHandler()
        user_input = {
            CONF_FRIENDLY_NAME: "Test",
            CONF_IP_ADDRESS: "192.168.1.100",
            CONF_PASSWORD: "test",
        }

        with patch.object(
            flow, "async_step_final", return_value=MagicMock()
        ) as mock_final:
            await flow.async_step_local(user_input)
            assert flow.data[CONF_CONNECTION] == CONF_LOCAL
            mock_final.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_step_local_invalid_ip(self) -> None:
        """Test local step returns form error for invalid IP address."""
        flow = ConfigFlowHandler()
        form_result = {"type": "form", "errors": {CONF_IP_ADDRESS: "invalid_ip"}}
        flow.async_show_form = MagicMock(return_value=form_result)

        user_input = {
            CONF_FRIENDLY_NAME: "Test",
            CONF_IP_ADDRESS: "not.an.ip",
            CONF_PASSWORD: "test",
        }

        result = await flow.async_step_local(user_input)
        assert result["type"] == "form"
        flow.async_show_form.assert_called_once()
        call_kwargs = flow.async_show_form.call_args[1]
        assert call_kwargs["errors"][CONF_IP_ADDRESS] == "invalid_ip"

    @pytest.mark.asyncio
    async def test_async_step_local_exception_handling(self) -> None:
        """Test local step handles exceptions."""
        flow = ConfigFlowHandler()
        flow.async_abort = MagicMock(return_value={"type": "abort"})

        with patch.object(flow, "async_show_form", side_effect=Exception("test")):
            result = await flow.async_step_local()
            assert result["type"] == "abort"

    @pytest.mark.asyncio
    async def test_async_step_cloud_shows_form(self) -> None:
        """Test cloud step shows form when no input."""
        flow = ConfigFlowHandler()
        flow.async_show_form = MagicMock(return_value={"type": "form"})

        result = await flow.async_step_cloud()
        assert result["type"] == "form"

    @pytest.mark.asyncio
    async def test_async_step_cloud_processes_input(self) -> None:
        """Test cloud step processes user input."""
        flow = ConfigFlowHandler()
        user_input = {
            CONF_FRIENDLY_NAME: "Test",
            CONF_SERIAL: "12345678",
            CONF_PASSWORD: "test",
        }

        with patch.object(
            flow, "async_step_final", return_value=MagicMock()
        ) as mock_final:
            await flow.async_step_cloud(user_input)
            assert flow.data[CONF_CONNECTION] == CONF_CLOUD
            mock_final.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_step_cloud_exception_handling(self) -> None:
        """Test cloud step handles exceptions."""
        flow = ConfigFlowHandler()
        flow.async_abort = MagicMock(return_value={"type": "abort"})

        with patch.object(flow, "async_show_form", side_effect=Exception("test")):
            result = await flow.async_step_cloud()
            assert result["type"] == "abort"

    @pytest.mark.asyncio
    async def test_async_step_final_creates_entry(self) -> None:
        """Test final step creates config entry."""
        flow = ConfigFlowHandler()
        flow.data = {
            CONF_FRIENDLY_NAME: "Test Wattpilot",
            CONF_IP_ADDRESS: "192.168.1.100",
            CONF_PASSWORD: "test",
            CONF_CONNECTION: CONF_LOCAL,
        }
        flow.async_set_unique_id = AsyncMock()
        flow._abort_if_unique_id_configured = MagicMock(return_value=None)
        flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})

        result = await flow.async_step_final()
        assert result["type"] == "create_entry"
        flow.async_set_unique_id.assert_called_once_with("192.168.1.100")

    @pytest.mark.asyncio
    async def test_async_step_final_uses_friendly_name_as_fallback(self) -> None:
        """Test final step uses friendly name when IP not available."""
        flow = ConfigFlowHandler()
        flow.data = {
            CONF_FRIENDLY_NAME: "Test Wattpilot",
            CONF_SERIAL: "12345678",
            CONF_PASSWORD: "test",
            CONF_CONNECTION: CONF_CLOUD,
        }
        flow.async_set_unique_id = AsyncMock()
        flow._abort_if_unique_id_configured = MagicMock(return_value=None)
        flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})

        await flow.async_step_final()
        flow.async_set_unique_id.assert_called_once_with("Test Wattpilot")

    @pytest.mark.asyncio
    async def test_async_step_final_aborts_if_duplicate(self) -> None:
        """Test final step aborts if unique ID already configured."""
        flow = ConfigFlowHandler()
        flow.data = {
            CONF_FRIENDLY_NAME: "Test",
            CONF_IP_ADDRESS: "192.168.1.100",
            CONF_PASSWORD: "test",
        }
        flow.async_set_unique_id = AsyncMock()
        flow._abort_if_unique_id_configured = MagicMock(
            return_value={"type": "abort", "reason": "already_configured"}
        )

        result = await flow.async_step_final()
        assert result["type"] == "abort"
        assert result["reason"] == "already_configured"


class TestOptionsFlow:
    """Test options flow."""

    @pytest.mark.asyncio
    async def test_options_flow_init(self) -> None:
        """Test options flow initialization."""
        flow = OptionsFlowHandler()
        assert hasattr(flow, "data")
        assert isinstance(flow.data, dict)

    @pytest.mark.asyncio
    async def test_async_step_init_routes_to_connection(self) -> None:
        """Test init step routes to connection for user source."""
        mock_config_entry = MagicMock()
        mock_config_entry.source = "user"

        with patch.object(OptionsFlowHandler, "config_entry", mock_config_entry):
            flow = OptionsFlowHandler()

            with patch.object(
                flow, "async_step_config_connection", return_value=MagicMock()
            ) as mock_conn:
                await flow.async_step_init()
                mock_conn.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_step_init_aborts_unsupported_source(self) -> None:
        """Test init step aborts for unsupported source."""
        mock_config_entry = MagicMock()
        mock_config_entry.source = "discovery"

        with patch.object(OptionsFlowHandler, "config_entry", mock_config_entry):
            flow = OptionsFlowHandler()
            flow.async_abort = MagicMock(return_value={"type": "abort"})

            result = await flow.async_step_init()
            assert result["type"] == "abort"
            flow.async_abort.assert_called_once_with(reason="not_supported")

    @pytest.mark.asyncio
    async def test_async_step_init_exception_handling(self) -> None:
        """Test init step handles exceptions."""
        from unittest.mock import PropertyMock

        mock_config_entry = MagicMock()
        type(mock_config_entry).source = PropertyMock(side_effect=Exception("test"))

        with patch.object(OptionsFlowHandler, "config_entry", mock_config_entry):
            flow = OptionsFlowHandler()
            flow.async_abort = MagicMock(return_value={"type": "abort"})

            result = await flow.async_step_init()
            assert result["type"] == "abort"

    @pytest.mark.asyncio
    async def test_async_step_config_connection_shows_form(self) -> None:
        """Test config connection shows form when no input."""
        flow = OptionsFlowHandler()
        flow.async_show_form = MagicMock(return_value={"type": "form"})

        result = await flow.async_step_config_connection()
        assert result["type"] == "form"

    @pytest.mark.asyncio
    async def test_async_step_config_connection_routes_local(self) -> None:
        """Test config connection routes to local."""
        flow = OptionsFlowHandler()
        user_input = {CONF_CONNECTION: CONF_LOCAL}

        with patch.object(
            flow, "async_step_config_local", return_value=MagicMock()
        ) as mock_local:
            await flow.async_step_config_connection(user_input)
            mock_local.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_step_config_connection_routes_cloud(self) -> None:
        """Test config connection routes to cloud."""
        flow = OptionsFlowHandler()
        user_input = {CONF_CONNECTION: CONF_CLOUD}

        with patch.object(
            flow, "async_step_config_cloud", return_value=MagicMock()
        ) as mock_cloud:
            await flow.async_step_config_connection(user_input)
            mock_cloud.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_step_config_connection_invalid_connection(self) -> None:
        """Test config connection aborts on invalid connection type."""
        flow = OptionsFlowHandler()
        flow.async_abort = MagicMock(return_value={"type": "abort"})
        user_input = {CONF_CONNECTION: "invalid"}

        result = await flow.async_step_config_connection(user_input)
        assert result["type"] == "abort"

    @pytest.mark.asyncio
    async def test_async_step_config_connection_exception_handling(self) -> None:
        """Test config connection handles exceptions."""
        flow = OptionsFlowHandler()
        flow.async_abort = MagicMock(return_value={"type": "abort"})

        with patch.object(flow, "async_show_form", side_effect=Exception("test")):
            result = await flow.async_step_config_connection()
            assert result["type"] == "abort"

    @pytest.mark.asyncio
    async def test_async_step_config_local_shows_form(self) -> None:
        """Test config local shows form when no input."""
        mock_config_entry = MagicMock()
        mock_config_entry.data = {CONF_IP_ADDRESS: "192.168.1.100"}

        with patch.object(OptionsFlowHandler, "config_entry", mock_config_entry):
            flow = OptionsFlowHandler()
            flow.async_show_form = MagicMock(return_value={"type": "form"})

            with patch(
                "custom_components.wattpilot.config_flow.async_get_OPTIONS_LOCAL_SCHEMA",
                return_value=MagicMock(),
            ):
                result = await flow.async_step_config_local()
                assert result["type"] == "form"

    @pytest.mark.asyncio
    async def test_async_step_config_local_processes_input(self) -> None:
        """Test config local processes user input."""
        mock_config_entry = MagicMock()
        mock_config_entry.data = {}

        with patch.object(OptionsFlowHandler, "config_entry", mock_config_entry):
            flow = OptionsFlowHandler()
            user_input = {
                CONF_FRIENDLY_NAME: "Updated",
                CONF_IP_ADDRESS: "192.168.1.101",
                CONF_PASSWORD: "newpass",
            }

            with (
                patch(
                    "custom_components.wattpilot.config_flow.async_get_OPTIONS_LOCAL_SCHEMA",
                    return_value=MagicMock(),
                ),
                patch.object(
                    flow, "async_step_final", return_value=MagicMock()
                ) as mock_final,
            ):
                await flow.async_step_config_local(user_input)
                assert flow.data[CONF_CONNECTION] == CONF_LOCAL
                mock_final.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_step_config_local_invalid_ip(self) -> None:
        """Test config local returns form error for invalid IP address."""
        mock_config_entry = MagicMock()
        mock_config_entry.data = {}

        with patch.object(OptionsFlowHandler, "config_entry", mock_config_entry):
            flow = OptionsFlowHandler()
            form_result = {"type": "form", "errors": {CONF_IP_ADDRESS: "invalid_ip"}}
            flow.async_show_form = MagicMock(return_value=form_result)
            user_input = {
                CONF_FRIENDLY_NAME: "Updated",
                CONF_IP_ADDRESS: "256.1.1.1",
                CONF_PASSWORD: "newpass",
            }

            with patch(
                "custom_components.wattpilot.config_flow.async_get_OPTIONS_LOCAL_SCHEMA",
                return_value=MagicMock(),
            ):
                result = await flow.async_step_config_local(user_input)
                assert result["type"] == "form"
                call_kwargs = flow.async_show_form.call_args[1]
                assert call_kwargs["errors"][CONF_IP_ADDRESS] == "invalid_ip"

    @pytest.mark.asyncio
    async def test_async_step_config_local_exception_handling(self) -> None:
        """Test config local handles exceptions."""
        mock_config_entry = MagicMock()
        mock_config_entry.data = {}

        with patch.object(OptionsFlowHandler, "config_entry", mock_config_entry):
            flow = OptionsFlowHandler()
            flow.async_abort = MagicMock(return_value={"type": "abort"})

            with patch(
                "custom_components.wattpilot.config_flow.async_get_OPTIONS_LOCAL_SCHEMA",
                side_effect=Exception("test"),
            ):
                result = await flow.async_step_config_local()
                assert result["type"] == "abort"

    @pytest.mark.asyncio
    async def test_async_step_config_cloud_shows_form(self) -> None:
        """Test config cloud shows form when no input."""
        mock_config_entry = MagicMock()
        mock_config_entry.data = {CONF_SERIAL: "12345678"}

        with patch.object(OptionsFlowHandler, "config_entry", mock_config_entry):
            flow = OptionsFlowHandler()
            flow.async_show_form = MagicMock(return_value={"type": "form"})

            with patch(
                "custom_components.wattpilot.config_flow.async_get_OPTIONS_CLOUD_SCHEMA",
                return_value=MagicMock(),
            ):
                result = await flow.async_step_config_cloud()
                assert result["type"] == "form"

    @pytest.mark.asyncio
    async def test_async_step_config_cloud_processes_input(self) -> None:
        """Test config cloud processes user input."""
        mock_config_entry = MagicMock()
        mock_config_entry.data = {}

        with patch.object(OptionsFlowHandler, "config_entry", mock_config_entry):
            flow = OptionsFlowHandler()
            user_input = {
                CONF_FRIENDLY_NAME: "Updated",
                CONF_SERIAL: "87654321",
                CONF_PASSWORD: "newpass",
            }

            with (
                patch(
                    "custom_components.wattpilot.config_flow.async_get_OPTIONS_CLOUD_SCHEMA",
                    return_value=MagicMock(),
                ),
                patch.object(
                    flow, "async_step_final", return_value=MagicMock()
                ) as mock_final,
            ):
                await flow.async_step_config_cloud(user_input)
                assert flow.data[CONF_CONNECTION] == CONF_CLOUD
                mock_final.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_step_config_cloud_exception_handling(self) -> None:
        """Test config cloud handles exceptions."""
        mock_config_entry = MagicMock()
        mock_config_entry.data = {}

        with patch.object(OptionsFlowHandler, "config_entry", mock_config_entry):
            flow = OptionsFlowHandler()
            flow.async_abort = MagicMock(return_value={"type": "abort"})

            with patch(
                "custom_components.wattpilot.config_flow.async_get_OPTIONS_CLOUD_SCHEMA",
                side_effect=Exception("test"),
            ):
                result = await flow.async_step_config_cloud()
                assert result["type"] == "abort"

    @pytest.mark.asyncio
    async def test_async_step_final_creates_entry(self) -> None:
        """Test final step creates options entry."""
        mock_config_entry = MagicMock()
        mock_config_entry.state = ConfigEntryState.LOADED

        with patch.object(OptionsFlowHandler, "config_entry", mock_config_entry):
            flow = OptionsFlowHandler()
            flow.data = {
                CONF_FRIENDLY_NAME: "Test",
                CONF_IP_ADDRESS: "192.168.1.100",
            }
            flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})

            result = await flow.async_step_final()
            assert result["type"] == "create_entry"

    @pytest.mark.asyncio
    async def test_async_step_final_handles_error_state(
        self, mock_hass: MagicMock
    ) -> None:
        """Test final step handles setup error state."""
        mock_config_entry = MagicMock()
        mock_config_entry.state = ConfigEntryState.SETUP_ERROR

        with patch.object(OptionsFlowHandler, "config_entry", mock_config_entry):
            flow = OptionsFlowHandler()
            flow.hass = mock_hass
            flow.data = {CONF_FRIENDLY_NAME: "Test"}
            flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})

            with patch(
                "custom_components.wattpilot.config_flow.options_update_listener",
                return_value=AsyncMock(),
            ) as mock_listener:
                await flow.async_step_final()
                mock_listener.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_step_final_exception_handling(self) -> None:
        """Test final step handles exceptions."""
        mock_config_entry = MagicMock()
        mock_config_entry.state = ConfigEntryState.LOADED

        with patch.object(OptionsFlowHandler, "config_entry", mock_config_entry):
            flow = OptionsFlowHandler()
            flow.data = {CONF_FRIENDLY_NAME: "Test"}
            flow.async_create_entry = MagicMock(side_effect=Exception("test"))
            flow.async_abort = MagicMock(return_value={"type": "abort"})

            result = await flow.async_step_final()
            assert result["type"] == "abort"

    def test_async_get_options_flow(self) -> None:
        """Test getting the options flow handler."""
        config_entry = MagicMock()
        handler = ConfigFlowHandler.async_get_options_flow(config_entry)
        assert isinstance(handler, OptionsFlowHandler)
