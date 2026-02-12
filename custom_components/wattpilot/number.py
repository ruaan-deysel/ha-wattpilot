"""Number entities for the Fronius Wattpilot integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Final

from homeassistant.components.number import NumberEntity
from homeassistant.components.number.const import UNIT_CONVERTERS
from homeassistant.const import (
    CONF_FRIENDLY_NAME,
    CONF_IP_ADDRESS,
)
from homeassistant.core import HomeAssistant

from .const import DEFAULT_NAME
from .descriptions import (
    NUMBER_DESCRIPTIONS,
    SOURCE_PROPERTY,
    WattpilotNumberEntityDescription,
)
from .entities import ChargerPlatformEntity, filter_descriptions
from .utils import async_SetChargerProp

if TYPE_CHECKING:
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .types import WattpilotConfigEntry

_LOGGER: Final = logging.getLogger(__name__)
PLATFORM = "number"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: WattpilotConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the number platform."""
    _LOGGER.debug("Setting up %s platform entry: %s", PLATFORM, entry.entry_id)

    charger = entry.runtime_data.charger
    push_entities = entry.runtime_data.push_entities
    charger_id = str(
        entry.data.get(
            CONF_FRIENDLY_NAME, entry.data.get(CONF_IP_ADDRESS, DEFAULT_NAME)
        )
    )

    descriptions = filter_descriptions(NUMBER_DESCRIPTIONS, charger, entry, charger_id)

    entities: list[ChargerNumber] = []
    for desc in descriptions:
        entity = ChargerNumber(hass, entry, desc, charger)
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


class ChargerNumber(ChargerPlatformEntity, NumberEntity):
    """Number class for Fronius Wattpilot integration."""

    _state_attr = "_attr_native_value"
    entity_description: WattpilotNumberEntityDescription

    def _init_platform_specific(self) -> None:
        """Platform specific init actions."""
        desc = self.entity_description

        self._attr_native_unit_of_measurement = desc.native_unit_of_measurement
        if desc.device_class is not None:
            unit_converter = UNIT_CONVERTERS.get(desc.device_class)
            if (
                unit_converter is not None
                and self._attr_native_unit_of_measurement in unit_converter.VALID_UNITS
            ):
                self._attr_suggested_unit_of_measurement = (
                    desc.native_unit_of_measurement
                )

        if desc.native_min_value is not None:
            self._attr_native_min_value = float(desc.native_min_value)
        if desc.native_max_value is not None:
            self._attr_native_max_value = float(desc.native_max_value)
        if desc.native_step is not None:
            self._attr_native_step = float(desc.native_step)
        if desc.mode is not None:
            self._attr_mode = desc.mode

    @property
    def native_value(self) -> float | None:
        """Return the current value, handling list/tuple values from charger."""
        value = self._attr_native_value
        if isinstance(value, list | tuple):
            value = value[0] if value else None
        if value is not None:
            try:
                return float(value)
            except (TypeError, ValueError):
                return None
        return None

    async def _async_update_validate_platform_state(
        self, state: Any = None
    ) -> float | None:
        """Async: Validate the given state for number specific requirements."""
        try:
            if isinstance(state, list | tuple):
                state = state[0] if state else None
            if state is not None:
                state = float(state)
                self._attr_native_value = state
            return state
        except (TypeError, ValueError, IndexError) as e:
            _LOGGER.warning(
                "%s - %s: _async_update_validate_platform_state failed to convert state to float: %s (%s)",
                self._charger_id,
                self._identifier,
                state,
                e,
            )
            return None

    async def async_set_native_value(self, value: float) -> None:
        """Async: Change the current value."""
        try:
            _LOGGER.debug(
                "%s - %s: async_set_native_value: value was changed to: %s",
                self._charger_id,
                self._identifier,
                value,
            )
            if self._identifier == "fte":
                await self._charger.set_next_trip_energy(value)
            else:
                await async_SetChargerProp(self._charger, self._identifier, value)
        except Exception as e:
            _LOGGER.error(
                "%s - %s: update failed: %s (%s.%s)",
                self._charger_id,
                self._identifier,
                str(e),
                e.__class__.__module__,
                type(e).__name__,
            )
