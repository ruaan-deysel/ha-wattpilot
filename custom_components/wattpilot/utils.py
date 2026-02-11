"""Helper functions for Fronius Wattpilot."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Final

from homeassistant.const import (
    CONF_FRIENDLY_NAME,
    CONF_IP_ADDRESS,
    CONF_PARAMS,
    CONF_PASSWORD,
)
from homeassistant.helpers import device_registry as dr
from wattpilot_api import Wattpilot

from .const import (
    CONF_CHARGER,
    CONF_CLOUD,
    CONF_CONNECTION,
    CONF_LOCAL,
    CONF_PUSH_ENTITIES,
    CONF_SERIAL,
    DEFAULT_NAME,
    DOMAIN,
    EVENT_PROPS,
    EVENT_PROPS_ID,
)

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

_LOGGER: Final = logging.getLogger(__name__)


async def async_property_update_handler(
    hass: HomeAssistant, entry: ConfigEntry, identifier: str, value: str
) -> None:
    """Async callback for charger property updates, dispatches to entities."""
    await _async_handle_property_update(hass, entry, identifier, value)


async def _async_handle_property_update(
    hass: HomeAssistant, entry: ConfigEntry, identifier: str, value: str
) -> None:
    """Async: handle charger property updates."""
    try:
        entry_id = getattr(entry, "entry_id", DOMAIN)
        runtime_data = getattr(entry, "runtime_data", None)
        if runtime_data is None:
            _LOGGER.error(
                "%s - _async_handle_property_update: runtime_data missing for entry",
                entry_id,
            )
            return

        # Notify coordinator of property update
        coordinator = getattr(runtime_data, "coordinator", None)
        if coordinator is not None:
            coordinator.async_handle_property_update(identifier, value)

        entity = runtime_data.push_entities.get(identifier)
        if entity is not None:
            hass.async_create_task(entity.async_local_push(value))

        if identifier in EVENT_PROPS:
            params = runtime_data.params or {}
            charger_id = str(
                params.get(
                    CONF_FRIENDLY_NAME, params.get(CONF_IP_ADDRESS, DEFAULT_NAME)
                )
            )
            data = {
                "charger_id": charger_id,
                "entry_id": entry_id,
                "property": identifier,
                "value": value,
            }
            hass.bus.fire(EVENT_PROPS_ID, data)
    except Exception:
        _LOGGER.exception(
            "%s - _async_handle_property_update: Could not execute async",
            entry_id,
        )


async def async_GetChargerProp(
    charger: Any, identifier: str, default: Any | None = None
) -> Any:
    """Async: return the value of a charger attribute."""
    try:
        if not hasattr(charger, "all_properties"):
            _LOGGER.error(
                "%s - async_GetChargerProp: missing all_properties: %s", DOMAIN, charger
            )
            return default
        if identifier is None or identifier not in charger.all_properties:
            _LOGGER.error(
                "%s - async_GetChargerProp: Charger does not have property: %s",
                DOMAIN,
                identifier,
            )
            return default
        if charger.all_properties[identifier] is None and default is not None:
            return default
        return charger.all_properties[identifier]
    except Exception:
        _LOGGER.exception("%s - async_GetChargerProp: Could not get property", DOMAIN)
        return default


def GetChargerProp(
    charger: Any, identifier: str | None = None, default: Any | None = None
) -> Any:
    """Return the value of a charger attribute."""
    try:
        if not hasattr(charger, "all_properties"):
            _LOGGER.error(
                "%s - GetChargerProp: missing all_properties: %s", DOMAIN, charger
            )
            return default
        if identifier is None or identifier not in charger.all_properties:
            _LOGGER.error(
                "%s - GetChargerProp: Charger does not have property: %s",
                DOMAIN,
                identifier,
            )
            return default
        if charger.all_properties[identifier] is None and default is not None:
            return default
        return charger.all_properties[identifier]
    except Exception:
        _LOGGER.exception("%s - GetChargerProp: Could not get property", DOMAIN)
        return default


async def async_SetChargerProp(
    charger: Any,
    identifier: str | None = None,
    value: Any | None = None,
) -> bool:
    """
    Async: set the value of a charger property.

    Type coercion is handled automatically by wattpilot-api.
    """
    try:
        if identifier is None:
            _LOGGER.error(
                "%s - async_SetChargerProp: property name has to be defined", DOMAIN
            )
            return False
        if value is None:
            _LOGGER.error(
                "%s - async_SetChargerProp: A value parameter is required: %s=%s",
                DOMAIN,
                identifier,
                value,
            )
            return False

        _LOGGER.debug(
            "%s - async_SetChargerProp: Send property update to charger: %s=%s",
            DOMAIN,
            identifier,
            value,
        )
        await charger.set_property(identifier, value)
    except Exception:
        _LOGGER.exception("%s - async_SetChargerProp: Could not set property", DOMAIN)
        return False
    return True


async def async_GetDataStoreFromDeviceID(
    hass: HomeAssistant, device_id: str
) -> dict[str, Any] | None:
    """Async: return the data store for a specific device_id."""
    try:
        _LOGGER.debug(
            "%s - async_GetDataStoreFromDeviceID: receiving device: %s",
            DOMAIN,
            device_id,
        )
        device_registry = dr.async_get(hass)
        device = device_registry.async_get(device_id)
        if device is None:
            _LOGGER.error(
                "%s - async_GetDataStoreFromDeviceID: device not found: %s",
                DOMAIN,
                device_id,
            )
            return None

        _LOGGER.debug(
            "%s - async_GetDataStoreFromDeviceID: get data store for config entry",
            DOMAIN,
        )
        for entry_id in device.config_entries:
            entry = hass.config_entries.async_get_entry(entry_id)
            if entry is None or entry.domain != DOMAIN:
                continue
            runtime_data = getattr(entry, "runtime_data", None)
            if runtime_data is None:
                continue
            return {
                CONF_CHARGER: runtime_data.charger,
                CONF_PUSH_ENTITIES: runtime_data.push_entities,
                CONF_PARAMS: runtime_data.params,
                "entry": entry,
                "runtime_data": runtime_data,
            }

        _LOGGER.error(
            "%s - async_GetDataStoreFromDeviceID: Unable to receive data store: %s",
            DOMAIN,
            device_id,
        )
    except Exception:
        _LOGGER.exception(
            "%s - async_GetDataStoreFromDeviceID: Could not get data store", DOMAIN
        )
    return None


async def async_GetChargerFromDeviceID(hass: HomeAssistant, device_id: str) -> Any:
    """Async: return the charger object for a specific device_id."""
    try:
        _LOGGER.debug(
            "%s - async_GetChargerFromDeviceID: receiving device: %s",
            DOMAIN,
            device_id,
        )
        device_registry = dr.async_get(hass)
        device = device_registry.async_get(device_id)
        if device is None:
            _LOGGER.error(
                "%s - async_GetChargerFromDeviceID: device not found: %s",
                DOMAIN,
                device_id,
            )
            return None

        _LOGGER.debug(
            "%s - async_GetChargerFromDeviceID: get charger object for entry",
            DOMAIN,
        )
        charger: Any | None = None
        for entry_id in device.config_entries:
            entry = hass.config_entries.async_get_entry(entry_id)
            if entry is None or entry.domain != DOMAIN:
                continue
            runtime_data = getattr(entry, "runtime_data", None)
            if runtime_data is None:
                continue
            charger = runtime_data.charger
            break
        if charger is None:
            _LOGGER.error(
                "%s - async_GetChargerFromDeviceID: Unable to identify charger for device: %s",
                DOMAIN,
                device_id,
            )
            return None

        _LOGGER.debug(
            "%s - async_GetChargerFromDeviceID: return charger object", DOMAIN
        )
        return charger
    except Exception:
        _LOGGER.exception(
            "%s - async_GetChargerFromDeviceID: Could not get charger", DOMAIN
        )
    return None


async def async_ConnectCharger(
    entry_or_device_id: str, data: dict[str, Any], charger: Any | None = None
) -> Any | bool:
    """Async: connect charger and handle connection errors."""
    try:
        con = data.get(CONF_CONNECTION, CONF_LOCAL)
        if charger is None and con == CONF_LOCAL:
            charger_id = data.get(CONF_IP_ADDRESS)
            _LOGGER.debug(
                "%s - async_ConnectCharger: Connecting %s charger by ip: %s",
                entry_or_device_id,
                CONF_LOCAL,
                charger_id,
            )
            charger = Wattpilot(
                host=charger_id,
                password=data.get(CONF_PASSWORD),
                serial=charger_id,
                cloud=False,
            )
        elif charger is None and con == CONF_CLOUD:
            charger_id = data.get(CONF_SERIAL)
            _LOGGER.debug(
                "%s - async_ConnectCharger: Connecting %s charger by serial: %s",
                entry_or_device_id,
                CONF_CLOUD,
                charger_id,
            )
            charger = Wattpilot(
                host=charger_id,
                password=data.get(CONF_PASSWORD),
                serial=charger_id,
                cloud=True,
            )
        elif charger is not None:
            charger_id = charger.name
            _LOGGER.debug(
                "%s - async_ConnectCharger: Reconnect existing charger: %s",
                entry_or_device_id,
                charger.name,
            )
        else:
            charger_id = "unknown"
            _LOGGER.warning(
                "%s - async_ConnectCharger: Unknown or empty connection type: %s",
                entry_or_device_id,
                con,
            )
        if charger is None:
            return False
        await charger.connect()
    except Exception:
        _LOGGER.exception(
            "%s - async_ConnectCharger: Connecting charger failed", entry_or_device_id
        )
        return False

    _LOGGER.debug(
        "%s - async_ConnectCharger: Charger connected: %s",
        entry_or_device_id,
        charger.name,
    )
    return charger


async def async_DisconnectCharger(entry_or_device_id: str, charger: Any) -> None:
    """Async: disconnect charger and handle connection errors."""
    try:
        _LOGGER.debug(
            "%s - async_DisconnectCharger: disconnect charger: %s",
            entry_or_device_id,
            charger,
        )
        await charger.disconnect()
    except Exception:
        _LOGGER.exception(
            "%s - async_DisconnectCharger: Disconnect charger failed",
            entry_or_device_id,
        )
