"""Services for the Fronius Wattpilot integration."""

from __future__ import annotations

import asyncio
import datetime
import functools
import logging
from typing import TYPE_CHECKING, Any, Final, cast

from homeassistant.const import (
    CONF_API_KEY,
    CONF_DEVICE_ID,
    CONF_EXTERNAL_URL,
    CONF_PARAMS,
    CONF_TRIGGER_TIME,
)

from .const import (
    CONF_CLOUD_API,
    DOMAIN,
)
from .utils import (
    async_ConnectCharger,
    async_GetChargerFromDeviceID,
    async_GetDataStoreFromDeviceID,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant, ServiceCall

_LOGGER: Final = logging.getLogger(__name__)


async def async_registerService(hass: HomeAssistant, name: str, service) -> None:
    """Register a service if it does not already exist"""
    try:
        _LOGGER.debug("%s - async_registerService: %s", DOMAIN, name)
        if not hass.services.has_service(DOMAIN, name):
            hass.services.async_register(DOMAIN, name, functools.partial(service, hass))
        else:
            _LOGGER.debug(
                "%s - async_registerServic: service already exists: %s", DOMAIN, name
            )
    except Exception as e:
        _LOGGER.error(
            "%s - async_registerService: failed: %s (%s.%s)",
            DOMAIN,
            str(e),
            e.__class__.__module__,
            type(e).__name__,
        )


async def async_service_SetNextTrip(hass: HomeAssistant, call: ServiceCall) -> None:
    """Service to set the next trip departure time."""
    try:
        device_id = call.data.get(CONF_DEVICE_ID, None)
        trigger_time = call.data.get(CONF_TRIGGER_TIME, None)
        if device_id is None:
            _LOGGER.error(
                "%s - async_service_SetNextTrip: %s is a required parameter",
                DOMAIN,
                CONF_DEVICE_ID,
            )
            return
        if trigger_time is None:
            _LOGGER.error(
                "%s - async_service_SetNextTrip: %s is a required parameter",
                DOMAIN,
                CONF_TRIGGER_TIME,
            )
            return

        charger = await async_GetChargerFromDeviceID(hass, device_id)
        if charger is None:
            _LOGGER.error(
                "%s - async_service_SetNextTrip: unable to get charger for: %s",
                DOMAIN,
                CONF_DEVICE_ID,
            )
            return

        # Parse HH:MM:SS string to datetime.time for the API
        parts = [int(p) for p in trigger_time.split(":")]
        departure = datetime.time(*parts)

        _LOGGER.debug(
            "%s - async_service_SetNextTrip: setting departure %s for charger: %s",
            DOMAIN,
            departure,
            charger.name,
        )
        await charger.set_next_trip(departure)

    except Exception as e:
        _LOGGER.error(
            "%s - async_service_SetNextTrip: %s failed: %s (%s.%s)",
            DOMAIN,
            call,
            str(e),
            e.__class__.__module__,
            type(e).__name__,
        )


async def async_service_SetGoECloud(hass: HomeAssistant, call: ServiceCall) -> None:
    """Service to enable or disable the go-e cloud API."""
    try:
        device_id = call.data.get(CONF_DEVICE_ID, None)
        api_state = call.data.get(CONF_CLOUD_API, None)
        if device_id is None:
            _LOGGER.error(
                "%s - async_service_SetGoECloud: %s is a required parameter",
                DOMAIN,
                CONF_DEVICE_ID,
            )
            return
        if api_state is None:
            _LOGGER.error(
                "%s - async_service_SetGoECloud: %s is a required parameter",
                DOMAIN,
                CONF_CLOUD_API,
            )
            return

        entry_data = await async_GetDataStoreFromDeviceID(hass, device_id)
        if entry_data is None:
            _LOGGER.error(
                "%s - async_service_SetGoECloud: unable to get entry data for: %s",
                DOMAIN,
                CONF_DEVICE_ID,
            )
            return

        charger = await async_GetChargerFromDeviceID(hass, device_id)
        if charger is None:
            _LOGGER.error(
                "%s - async_service_SetGoECloud: unable to get charger for: %s",
                DOMAIN,
                CONF_DEVICE_ID,
            )
            return

        if api_state is True:
            _LOGGER.debug("%s - async_service_SetGoECloud: Enabling cloud api", DOMAIN)
            cloud_info = await charger.enable_cloud_api()
            entry_data[CONF_API_KEY] = cloud_info.api_key
            entry_data[CONF_EXTERNAL_URL] = cloud_info.url
            _LOGGER.info(
                "%s - async_service_SetGoECloud: %s cloud API enabled (key: %s, url: %s)",
                DOMAIN,
                charger.name,
                cloud_info.api_key,
                cloud_info.url,
            )
        else:
            _LOGGER.debug(
                "%s - async_service_SetGoECloud: %s disabling cloud api",
                DOMAIN,
                charger.name,
            )
            await charger.disable_cloud_api()
            entry_data[CONF_API_KEY] = False
            _LOGGER.info(
                "%s - async_service_SetGoECloud: %s DISABLED cloud API",
                DOMAIN,
                charger.name,
            )

    except Exception as e:
        _LOGGER.error(
            "%s - async_service_SetGoECloud: %s failed: %s (%s.%s)",
            DOMAIN,
            call,
            str(e),
            e.__class__.__module__,
            type(e).__name__,
        )


async def async_service_ReConnectCharger(
    hass: HomeAssistant, call: ServiceCall
) -> bool:
    """Service to reconnect to the charger."""
    try:
        device_id = call.data.get(CONF_DEVICE_ID, None)
        if device_id is None:
            _LOGGER.error(
                "%s - async_service_ReConnectCharger: %s is a required parameter",
                DOMAIN,
                CONF_DEVICE_ID,
            )
            return False

        entry_data = await async_GetDataStoreFromDeviceID(hass, device_id)
        if entry_data is None:
            _LOGGER.error(
                "%s - async_service_ReConnectCharger: unable to get entry data for: %s",
                DOMAIN,
                CONF_DEVICE_ID,
            )
            return False

        charger = await async_GetChargerFromDeviceID(hass, device_id)
        if charger is None:
            _LOGGER.error(
                "%s - async_service_ReConnectCharger: unable to get charger for: %s",
                DOMAIN,
                CONF_DEVICE_ID,
            )
            return False

        if charger.connected:
            await charger.disconnect()
            await asyncio.sleep(1)

        result = await async_ConnectCharger(device_id, entry_data[CONF_PARAMS], charger)
        if not result:
            return False
        charger = cast("Any", result)
        _LOGGER.info(
            "%s - async_service_ReConnectCharger: Charger reconnected: %s",
            DOMAIN,
            charger.name,
        )
        return True

    except Exception as e:
        _LOGGER.error(
            "%s - async_service_ReConnectCharger: %s failed: %s (%s.%s)",
            DOMAIN,
            call,
            str(e),
            e.__class__.__module__,
            type(e).__name__,
        )
        return False


async def async_service_DisconnectCharger(
    hass: HomeAssistant, call: ServiceCall
) -> bool:
    """Service to disconnect from the charger."""
    try:
        device_id = call.data.get(CONF_DEVICE_ID, None)
        if device_id is None:
            _LOGGER.error(
                "%s - async_service_DisconnectCharger: %s is a required parameter",
                DOMAIN,
                CONF_DEVICE_ID,
            )
            return False

        charger = await async_GetChargerFromDeviceID(hass, device_id)
        if charger is None:
            _LOGGER.error(
                "%s - async_service_DisconnectCharger: unable to get charger for: %s",
                DOMAIN,
                CONF_DEVICE_ID,
            )
            return False

        await charger.disconnect()
        _LOGGER.info(
            "%s - async_service_DisconnectCharger: Charger disconnected: %s",
            DOMAIN,
            charger.name,
        )
        return True

    except Exception as e:
        _LOGGER.error(
            "%s - async_service_DisconnectCharger: %s failed: %s (%s.%s)",
            DOMAIN,
            call,
            str(e),
            e.__class__.__module__,
            type(e).__name__,
        )
        return False
