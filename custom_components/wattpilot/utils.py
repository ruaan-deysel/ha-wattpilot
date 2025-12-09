"""Helper functions for Fronius Wattpilot."""

from __future__ import annotations

import asyncio
import importlib
import json
import logging
import sys
import types
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final

from homeassistant.const import (
    CONF_FRIENDLY_NAME,
    CONF_IP_ADDRESS,
    CONF_PARAMS,
    CONF_PASSWORD,
    CONF_TIMEOUT,
)
from homeassistant.helpers import device_registry as dr

from .const import (
    CONF_CHARGER,
    CONF_CLOUD,
    CONF_CONNECTION,
    CONF_DBG_PROPS,
    CONF_LOCAL,
    CONF_PUSH_ENTITIES,
    CONF_SERIAL,
    DEFAULT_NAME,
    DEFAULT_TIMEOUT,
    DOMAIN,
    EVENT_PROPS,
    EVENT_PROPS_ID,
)

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

_LOGGER: Final = logging.getLogger(__name__)


def _dynamic_load_module(
    modulename: str, subfolder: str = "src", initfile: str = "__init__.py"
) -> Any:
    """Try to load a module from local custom component; fall back to system."""
    try:
        _LOGGER.debug("%s - _dynamic_load_module: %s", DOMAIN, modulename)
        base_path = Path(__file__).parent
        local_module_path = base_path / modulename / subfolder
        local_init_path = local_module_path / modulename / initfile
        if local_init_path.exists():
            _LOGGER.debug(
                "%s - _dynamic_load_module: import local module: %s (%s)",
                DOMAIN,
                modulename,
                local_init_path,
            )
            if str(local_module_path) not in sys.path:
                sys.path.insert(0, str(local_module_path))
        else:
            _LOGGER.debug(
                "%s - _dynamic_load_module: import system wide module: %s",
                DOMAIN,
                modulename,
            )
        module = importlib.import_module(modulename)
    except (ImportError, OSError) as err:
        _LOGGER.exception(
            "%s - _dynamic_load_module: failed to import %s", DOMAIN, modulename
        )
        raise ImportError(f"failed to import module {modulename}") from err
    return module


wattpilot = _dynamic_load_module("wattpilot")
_LOGGER.debug(
    "%s - utils: imported module from: %s (%s)",
    DOMAIN,
    wattpilot.__file__,
    getattr(wattpilot, "__version__", "0.2.2?"),
)


async def async_ProgrammingDebug(obj: Any, show_all: bool = False) -> None:
    """Async: return all attributes of a specific object."""
    try:
        _LOGGER.debug("%s - async_ProgrammingDebug: %s", DOMAIN, obj)
        for attr in dir(obj):
            if attr.startswith("_") and not show_all:
                continue
            if hasattr(obj, attr):
                _LOGGER.debug(
                    "%s - async_ProgrammingDebug: %s = %s",
                    DOMAIN,
                    attr,
                    getattr(obj, attr),
                )
            await asyncio.sleep(0)
    except Exception:
        _LOGGER.exception("%s - async_ProgrammingDebug: failed", DOMAIN)


def ProgrammingDebug(obj: Any, show_all: bool = False) -> None:
    """Return all attributes of a specific object."""
    try:
        _LOGGER.debug("%s - ProgrammingDebug: %s", DOMAIN, obj)
        for attr in dir(obj):
            if attr.startswith("_") and not show_all:
                continue
            if hasattr(obj, attr):
                _LOGGER.debug(
                    "%s - ProgrammingDebug: %s = %s", DOMAIN, attr, getattr(obj, attr)
                )
    except Exception:
        _LOGGER.exception("%s - ProgrammingDebug: failed", DOMAIN)


async def async_PropertyDebug(
    identifier: str, value: str, include_properties: bool | list[str]
) -> None:
    """Log properties if they change."""
    exclude_properties = [
        "efh",
        "efh32",
        "efh8",
        "ehs",
        "emhb",
        "fbuf_age",
        "fbuf_pAkku",
        "fbuf_pGrid",
        "fbuf_pPv",
        "fhz",
        "loc",
        "lps",
        "nrg",
        "rbt",
        "rcd",
        "rfb",
        "rssi",
        "tma",
        "tpcm",
        "utc",
        "fbuf_akkuSOC",
        "lpsc",
        "pvopt_averagePAkku",
        "pvopt_averagePGrid",
        "pvopt_averagePPv",
        "pvopt_deltaP",
    ]
    if (isinstance(include_properties, list) and identifier in include_properties) or (
        isinstance(include_properties, bool) and identifier not in exclude_properties
    ):
        _LOGGER.warning(
            "async_PropertyDebug: watch_properties: %s => %s ", identifier, value
        )


def PropertyUpdateHandler(
    hass: HomeAssistant, entry: ConfigEntry, identifier: str, value: str
) -> None:
    """Watches property updates and dispatches to entities."""
    try:
        asyncio.run_coroutine_threadsafe(
            async_PropertyUpdateHandler(hass, entry, identifier, value), hass.loop
        )
    except Exception:
        entry_id = getattr(entry, "entry_id", DOMAIN)
        _LOGGER.exception(
            "%s - PropertyUpdateHandler: Could not execute async",
            entry_id,
        )


async def async_PropertyUpdateHandler(
    hass: HomeAssistant, entry: ConfigEntry, identifier: str, value: str
) -> None:
    """Async: handle charger property updates."""
    try:
        entry_id = getattr(entry, "entry_id", DOMAIN)
        runtime_data = getattr(entry, "runtime_data", None)
        if runtime_data is None:
            _LOGGER.error(
                "%s - async_PropertyUpdateHandler: runtime_data missing for entry",
                entry_id,
            )
            return

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

        if runtime_data.debug_properties:
            hass.async_create_task(
                async_PropertyDebug(identifier, value, runtime_data.debug_properties)
            )
    except Exception:
        _LOGGER.exception(
            "%s - PropertyUpdateHandler: Could not execute async",
            entry_id,
        )


async def async_GetChargerProp(
    charger: Any, identifier: str, default: Any | None = None
) -> Any:
    """Async: return the value of a charger attribute."""
    try:
        if not hasattr(charger, "allProps"):
            _LOGGER.error(
                "%s - async_GetChargerProp: missing allProps: %s", DOMAIN, charger
            )
            return default
        if identifier is None or identifier not in charger.allProps:
            _LOGGER.error(
                "%s - async_GetChargerProp: Charger does not have property: %s",
                DOMAIN,
                identifier,
            )
            return default
        await asyncio.sleep(0)
        if charger.allProps[identifier] is None and default is not None:
            return default
        return charger.allProps[identifier]
    except Exception:
        _LOGGER.exception("%s - async_GetChargerProp: Could not get property", DOMAIN)
        return default


def GetChargerProp(
    charger: Any, identifier: str | None = None, default: Any | None = None
) -> Any:
    """Return the value of a charger attribute."""
    try:
        if not hasattr(charger, "allProps"):
            _LOGGER.error("%s - GetChargerProp: missing allProps: %s", DOMAIN, charger)
            return default
        if identifier is None or identifier not in charger.allProps:
            _LOGGER.error(
                "%s - GetChargerProp: Charger does not have property: %s",
                DOMAIN,
                identifier,
            )
            return default
        if charger.allProps[identifier] is None and default is not None:
            return default
        return charger.allProps[identifier]
    except Exception:
        _LOGGER.exception("%s - GetChargerProp: Could not get property", DOMAIN)
        return default


async def async_SetChargerProp(
    charger: Any,
    identifier: str | None = None,
    value: Any | None = None,
    force: bool = False,
    force_type: str | None = None,
) -> bool:
    """Async: set the value of a charger attribute."""
    try:
        if not hasattr(charger, "allProps"):
            _LOGGER.error(
                "%s - async_SetChargerProp: missing allProps: %s", DOMAIN, charger
            )
            return False
        if identifier is None:
            _LOGGER.error(
                "%s - async_SetChargerProp: property name has to be defined", DOMAIN
            )
            return False
        if identifier not in charger.allProps and not force:
            _LOGGER.error(
                "%s - async_SetChargerProp: Charger does not have property: %s",
                DOMAIN,
                identifier,
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

        if force_type is not None:
            force_type = str(force_type).lower()

        _LOGGER.debug(
            "%s - async_SetChargerProp: Prepare new property value: %s=%s",
            DOMAIN,
            identifier,
            value,
        )
        if force_type == "str":
            v = str(value)
        elif str(value).lower() in ["false", "true"] or force_type == "bool":
            v = json.loads(str(value).lower())
        elif str(value).isnumeric() or force_type == "int":
            v = int(value)
        elif str(value).isdecimal() or force_type == "float":
            v = float(value)
        elif type(value) is types.SimpleNamespace:
            _LOGGER.warning(
                "%s - async_SetChargerProp: namespace set is untested: %s=%s",
                DOMAIN,
                identifier,
                value,
            )
            v = value.__dict__
        else:
            v = str(value)

        _LOGGER.debug(
            "%s - async_SetChargerProp: Send property update to charger: %s=%s",
            DOMAIN,
            identifier,
            v,
        )
        charger.send_update(identifier, v)
        await asyncio.sleep(0)
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
            await asyncio.sleep(0)
            return {
                CONF_CHARGER: runtime_data.charger,
                CONF_PUSH_ENTITIES: runtime_data.push_entities,
                CONF_PARAMS: runtime_data.params,
                CONF_DBG_PROPS: runtime_data.debug_properties,
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
            await asyncio.sleep(0)
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
            charger = wattpilot.Wattpilot(
                ip=charger_id,
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
            charger = wattpilot.Wattpilot(
                ip=charger_id,
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
        charger.connect()
    except Exception:
        _LOGGER.exception(
            "%s - async_ConnectCharger: Connecting charger failed", entry_or_device_id
        )
        return False

    try:
        _LOGGER.debug(
            "%s - async_ConnectCharger: ensure charger is ready: %s",
            entry_or_device_id,
            charger_id,
        )
        timer = 0
        timeout = data.get(CONF_TIMEOUT, DEFAULT_TIMEOUT)
        while timeout > timer and not (
            charger.connected and charger.allPropsInitialized
        ):
            await asyncio.sleep(1)
            timer += 1
        if not charger.connected:
            _LOGGER.error(
                "%s - async_ConnectCharger: timeout - charger not connected: %s (%s sec)",
                entry_or_device_id,
                charger.connected,
                timeout,
            )
            _LOGGER.error(
                "%s - async_ConnectCharger: restart charger via Wattpilot app",
                entry_or_device_id,
            )
            return False
        if not charger.allPropsInitialized:
            _LOGGER.error(
                "%s - async_ConnectCharger: timeout - charger not initialized: %s (%s sec)",
                entry_or_device_id,
                charger.allPropsInitialized,
                timeout,
            )
            return False
        if not timeout > timer:
            _LOGGER.error(
                "%s - async_ConnectCharger: Timeout - unknown reason: %s sec",
                entry_or_device_id,
                timeout,
            )
            return False
    except Exception:
        _LOGGER.exception(
            "%s - async_ConnectCharger: Initialize charger failed",
            entry_or_device_id,
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
        if hasattr(charger, "disconnect") and callable(charger.disconnect):
            charger.disconnect()
        else:  # temporary workaround until wattpilot exposes disconnect
            charger._wsapp.close()
            charger._connected = False
    except Exception:
        _LOGGER.exception(
            "%s - async_DisconnectCharger: Disconnect charger failed",
            entry_or_device_id,
        )
