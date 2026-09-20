"""Binary sensor entities for the Fronius Wattpilot integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Final

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
)
from homeassistant.const import (
    CONF_FRIENDLY_NAME,
    CONF_IP_ADDRESS,
)
from homeassistant.core import HomeAssistant

from .const import DEFAULT_NAME
from .descriptions import (
    BINARY_SENSOR_DESCRIPTIONS,
    SOURCE_PROPERTY,
    WattpilotBinarySensorEntityDescription,
)
from .entities import ChargerPlatformEntity, filter_descriptions

if TYPE_CHECKING:
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .types import WattpilotConfigEntry

_LOGGER: Final = logging.getLogger(__name__)
PLATFORM = "binary_sensor"
PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: WattpilotConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary_sensor platform."""
    _LOGGER.debug("Setting up %s platform entry: %s", PLATFORM, entry.entry_id)

    charger = entry.runtime_data.charger
    push_entities = entry.runtime_data.push_entities
    charger_id = str(
        entry.data.get(
            CONF_FRIENDLY_NAME, entry.data.get(CONF_IP_ADDRESS, DEFAULT_NAME)
        )
    )

    descriptions = filter_descriptions(
        BINARY_SENSOR_DESCRIPTIONS, charger, entry, charger_id
    )

    entities: list[ChargerBinarySensor] = []
    for desc in descriptions:
        entity = ChargerBinarySensor(hass, entry, desc, charger)
        if getattr(entity, "_init_failed", True):
            continue
        entities.append(entity)
        if entity._source == SOURCE_PROPERTY:
            if entity._identifier in push_entities:
                existing = push_entities[entity._identifier]
                if isinstance(existing, list):
                    existing.append(entity)
                else:
                    push_entities[entity._identifier] = [existing, entity]
            else:
                push_entities[entity._identifier] = entity

    _LOGGER.info(
        "%s - async_setup_entry: setup %s %s entities",
        entry.entry_id,
        len(entities),
        PLATFORM,
    )
    if entities:
        async_add_entities(entities)


class ChargerBinarySensor(ChargerPlatformEntity, BinarySensorEntity):
    """Binary sensor class for Fronius Wattpilot integration."""

    _state_attr = "_attr_is_on"
    entity_description: WattpilotBinarySensorEntityDescription

    def _init_platform_specific(self) -> None:
        """Platform specific init actions."""
        self._attr_is_on = None

    async def _async_update_validate_platform_state(
        self, state: Any = None
    ) -> bool | None:
        """Async: Validate the given state for binary sensor specific requirements."""
        try:
            if state is None:
                return None
            desc = self.entity_description
            if desc.on_values is not None:
                try:
                    int_val = int(state)
                    return int_val in desc.on_values
                except (ValueError, TypeError):
                    return state in desc.on_values
            if isinstance(state, bool):
                return state
            if str(state).lower() in ("true", "1", "on"):
                return True
            if str(state).lower() in ("false", "0", "off"):
                return False
            return None
        except Exception:
            _LOGGER.exception(
                "%s - %s: _async_update_validate_platform_state failed",
                self._charger_id,
                self._identifier,
            )
            return None
