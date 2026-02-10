"""Sensor entities for the Fronius Wattpilot integration."""

from __future__ import annotations

import html
import logging
from typing import TYPE_CHECKING, Any, Final

from homeassistant.components.sensor import (
    SensorEntity,
)
from homeassistant.components.sensor.const import UNIT_CONVERTERS
from homeassistant.const import (
    CONF_FRIENDLY_NAME,
    CONF_IP_ADDRESS,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant

from .const import DEFAULT_NAME
from .descriptions import (
    SENSOR_DESCRIPTIONS,
    SOURCE_PROPERTY,
    WattpilotSensorEntityDescription,
)
from .entities import ChargerPlatformEntity, filter_descriptions

if TYPE_CHECKING:
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .types import WattpilotConfigEntry

_LOGGER: Final = logging.getLogger(__name__)
PLATFORM = "sensor"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: WattpilotConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    _LOGGER.debug("Setting up %s platform entry: %s", PLATFORM, entry.entry_id)

    charger = entry.runtime_data.charger
    push_entities = entry.runtime_data.push_entities
    charger_id = str(
        entry.data.get(
            CONF_FRIENDLY_NAME, entry.data.get(CONF_IP_ADDRESS, DEFAULT_NAME)
        )
    )

    descriptions = filter_descriptions(SENSOR_DESCRIPTIONS, charger, entry, charger_id)

    entities: list[ChargerSensor] = []
    for desc in descriptions:
        entity = ChargerSensor(hass, entry, desc, charger)
        if getattr(entity, "_init_failed", True):
            continue
        entities.append(entity)
        if entity._source == SOURCE_PROPERTY:
            push_entities[entity._identifier] = entity

    _LOGGER.info(
        "%s - async_setup_entry: setup %s %s entities",
        entry.entry_id,
        len(entities),
        PLATFORM,
    )
    if entities:
        async_add_entities(entities)


class ChargerSensor(ChargerPlatformEntity, SensorEntity):
    """Sensor class for Fronius Wattpilot integration."""

    _state_attr = "_attr_native_value"
    entity_description: WattpilotSensorEntityDescription

    def _init_platform_specific(self) -> None:
        """Platform specific init actions."""
        desc = self.entity_description

        # Set native unit of measurement from description
        self._attr_native_unit_of_measurement = desc.native_unit_of_measurement

        # Set suggested unit of measurement if valid for the device class
        if desc.device_class is not None:
            unit_converter = UNIT_CONVERTERS.get(desc.device_class)
            if (
                unit_converter is not None
                and self._attr_native_unit_of_measurement in unit_converter.VALID_UNITS
            ):
                self._attr_suggested_unit_of_measurement = (
                    desc.native_unit_of_measurement
                )

        # Enum mapping for display values
        if desc.enum is not None:
            self._state_enum = dict(desc.enum)

        # HTML unescape flag
        if desc.html_unescape:
            self._html_unescape = True

    async def _async_update_validate_platform_state(
        self, state: Any = None
    ) -> Any | None:
        """Async: Validate the given state for sensor specific requirements."""
        try:
            if state is None or state == "None":
                state = STATE_UNKNOWN
            elif hasattr(self, "_html_unescape") and self._html_unescape:
                state = html.unescape(state)
            elif not hasattr(self, "_state_enum"):
                pass
            elif state in list(self._state_enum.keys()):
                state = self._state_enum[state]
            elif state in list(self._state_enum.values()):
                pass
            else:
                _LOGGER.warning(
                    "%s - %s: _async_update_validate_platform_state failed: state %s not within enum values: %s",
                    self._charger_id,
                    self._identifier,
                    state,
                    self._state_enum,
                )
            if self._attr_native_unit_of_measurement is not None:
                self._attr_native_value = state
            return state
        except Exception as e:
            _LOGGER.error(
                "%s - %s: _async_update_validate_platform_state failed: %s (%s.%s)",
                self._charger_id,
                self._identifier,
                str(e),
                e.__class__.__module__,
                type(e).__name__,
            )
            return None
