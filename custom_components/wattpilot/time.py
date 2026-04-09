"""Time entities for the Fronius Wattpilot integration."""

from __future__ import annotations

import datetime
import logging
from typing import TYPE_CHECKING, Any, Final

from homeassistant.components.time import TimeEntity
from homeassistant.const import (
    CONF_FRIENDLY_NAME,
    CONF_IP_ADDRESS,
)
from homeassistant.core import HomeAssistant

from .const import DEFAULT_NAME
from .descriptions import (
    SOURCE_PROPERTY,
    TIME_DESCRIPTIONS,
    WattpilotTimeEntityDescription,
)
from .entities import ChargerPlatformEntity, filter_descriptions

if TYPE_CHECKING:
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .types import WattpilotConfigEntry

_LOGGER: Final = logging.getLogger(__name__)
PLATFORM = "time"

_SECONDS_PER_HOUR: Final = 3600
_SECONDS_PER_MINUTE: Final = 60
_SECONDS_PER_DAY: Final = 86400


async def async_setup_entry(
    hass: HomeAssistant,
    entry: WattpilotConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the time platform."""
    _LOGGER.debug("Setting up %s platform entry: %s", PLATFORM, entry.entry_id)

    charger = entry.runtime_data.charger
    push_entities = entry.runtime_data.push_entities
    charger_id = str(
        entry.data.get(
            CONF_FRIENDLY_NAME, entry.data.get(CONF_IP_ADDRESS, DEFAULT_NAME)
        )
    )

    descriptions = filter_descriptions(TIME_DESCRIPTIONS, charger, entry, charger_id)

    entities: list[ChargerTime] = []
    for desc in descriptions:
        entity = ChargerTime(hass, entry, desc, charger)
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


class ChargerTime(ChargerPlatformEntity, TimeEntity):
    """Time class for Fronius Wattpilot integration."""

    _state_attr = "_attr_native_value"
    entity_description: WattpilotTimeEntityDescription

    @property
    def native_value(self) -> datetime.time | None:
        """Return the current time value."""
        return self._attr_native_value  # type: ignore[return-value]

    async def _async_update_validate_platform_state(
        self, state: Any = None
    ) -> datetime.time | None:
        """Async: Validate and convert seconds-since-midnight to datetime.time."""
        try:
            if state is None:
                return None
            seconds = int(state) % _SECONDS_PER_DAY
            hour = seconds // _SECONDS_PER_HOUR
            remaining = seconds % _SECONDS_PER_HOUR
            minute = remaining // _SECONDS_PER_MINUTE
            second = remaining % _SECONDS_PER_MINUTE
            return datetime.time(hour, minute, second)
        except (TypeError, ValueError) as e:
            _LOGGER.warning(
                "%s - %s: _async_update_validate_platform_state failed to convert state to time: %s (%s)",
                self._charger_id,
                self._identifier,
                state,
                e,
            )
            return None

    async def async_set_value(self, value: datetime.time) -> None:
        """Async: Set the departure time for the next trip."""
        try:
            _LOGGER.debug(
                "%s - %s: async_set_value: value was changed to: %s",
                self._charger_id,
                self._identifier,
                value,
            )
            await self._charger.set_next_trip(value)
        except Exception as e:
            _LOGGER.error(
                "%s - %s: async_set_value failed: %s (%s.%s)",
                self._charger_id,
                self._identifier,
                str(e),
                e.__class__.__module__,
                type(e).__name__,
            )
