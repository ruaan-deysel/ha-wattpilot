"""Switch entities for the Fronius Wattpilot integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Final

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import (
    CONF_FRIENDLY_NAME,
    CONF_IP_ADDRESS,
    STATE_OFF,
    STATE_ON,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant

from .const import DEFAULT_NAME
from .descriptions import (
    SOURCE_PROPERTY,
    SWITCH_DESCRIPTIONS,
    WattpilotSwitchEntityDescription,
)
from .entities import ChargerPlatformEntity, filter_descriptions
from .utils import async_SetChargerProp

if TYPE_CHECKING:
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .types import WattpilotConfigEntry

_LOGGER: Final = logging.getLogger(__name__)
PLATFORM = "switch"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: WattpilotConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the switch platform."""
    _LOGGER.debug("Setting up %s platform entry: %s", PLATFORM, entry.entry_id)

    charger = entry.runtime_data.charger
    push_entities = entry.runtime_data.push_entities
    charger_id = str(
        entry.data.get(
            CONF_FRIENDLY_NAME, entry.data.get(CONF_IP_ADDRESS, DEFAULT_NAME)
        )
    )

    descriptions = filter_descriptions(SWITCH_DESCRIPTIONS, charger, entry, charger_id)

    entities: list[ChargerSwitch] = []
    for desc in descriptions:
        entity = ChargerSwitch(hass, entry, desc, charger)
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


class ChargerSwitch(ChargerPlatformEntity, SwitchEntity):
    """Switch class for Fronius Wattpilot integration."""

    _state_attr = "_internal_state"
    entity_description: WattpilotSwitchEntityDescription

    def _init_platform_specific(self) -> None:
        """Platform specific init actions."""
        self._internal_state = STATE_UNKNOWN

    async def _async_update_validate_platform_state(
        self, state: Any = None
    ) -> str | None:
        """Async: Validate the given state for switch specific requirements."""
        try:
            if str(state) in [STATE_ON, STATE_OFF, STATE_UNKNOWN]:
                pass
            elif str(state).lower() == "true":
                state = STATE_ON
            elif str(state).lower() == "false":
                state = STATE_OFF
            else:
                _LOGGER.warning(
                    "%s - %s: _async_update_validate_platform_state failed: state %s not valid for switch platform",
                    self._charger_id,
                    self._identifier,
                    state,
                )
                state = STATE_UNKNOWN

            if state == STATE_ON and self.entity_description.invert:
                _LOGGER.debug(
                    "%s - %s: _async_update_validate_platform_state: invert state: %s -> %s",
                    self._charger_id,
                    self._identifier,
                    STATE_ON,
                    STATE_OFF,
                )
                state = STATE_OFF
            elif state == STATE_OFF and self.entity_description.invert:
                _LOGGER.debug(
                    "%s - %s: _async_update_validate_platform_state: invert state: %s -> %s",
                    self._charger_id,
                    self._identifier,
                    STATE_OFF,
                    STATE_ON,
                )
                state = STATE_ON
            return state
        except Exception:
            _LOGGER.exception(
                "%s - %s: _async_update_validate_platform_state failed",
                self._charger_id,
                self._identifier,
            )
            return None

    @property
    def is_on(self) -> bool | None:
        """Return true if entity is on."""
        if self._internal_state == STATE_UNKNOWN:
            return None
        return self._internal_state == STATE_ON

    async def async_turn_on(self, **_: Any) -> None:
        """Async: Turn entity on."""
        try:
            _LOGGER.debug(
                "%s - %s: async_turn_on",
                self._charger_id,
                self._identifier,
            )
            value = not self.entity_description.invert
            await async_SetChargerProp(self._charger, self._identifier, value)
        except Exception:
            _LOGGER.exception(
                "%s - %s: async_turn_on failed", self._charger_id, self._identifier
            )

    async def async_turn_off(self, **_: Any) -> None:
        """Async: Turn entity off."""
        try:
            _LOGGER.debug(
                "%s - %s: async_turn_off",
                self._charger_id,
                self._identifier,
            )
            value = self.entity_description.invert
            await async_SetChargerProp(self._charger, self._identifier, value)
        except Exception:
            _LOGGER.exception(
                "%s - %s: async_turn_off failed", self._charger_id, self._identifier
            )
