"""Select entities for the Fronius Wattpilot integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Final

from homeassistant.components.select import SelectEntity
from homeassistant.const import (
    CONF_FRIENDLY_NAME,
    CONF_IP_ADDRESS,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant

from .const import DEFAULT_NAME
from .descriptions import (
    SELECT_DESCRIPTIONS,
    SOURCE_PROPERTY,
    WattpilotSelectEntityDescription,
)
from .entities import ChargerPlatformEntity, filter_descriptions
from .utils import async_SetChargerProp

if TYPE_CHECKING:
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .types import WattpilotConfigEntry

_LOGGER: Final = logging.getLogger(__name__)
PLATFORM = "select"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: WattpilotConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the select platform."""
    _LOGGER.debug("Setting up %s platform entry: %s", PLATFORM, entry.entry_id)

    charger = entry.runtime_data.charger
    push_entities = entry.runtime_data.push_entities
    charger_id = str(
        entry.data.get(
            CONF_FRIENDLY_NAME, entry.data.get(CONF_IP_ADDRESS, DEFAULT_NAME)
        )
    )

    descriptions = filter_descriptions(SELECT_DESCRIPTIONS, charger, entry, charger_id)

    entities: list[ChargerSelect] = []
    for desc in descriptions:
        entity = ChargerSelect(hass, entry, desc, charger)
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


class ChargerSelect(ChargerPlatformEntity, SelectEntity):
    """Select class for Fronius Wattpilot integration."""

    _state_attr = "_attr_current_option"
    entity_description: WattpilotSelectEntityDescription

    def _init_platform_specific(self) -> None:
        """Platform specific init actions."""
        desc = self.entity_description
        if isinstance(desc.select_options, dict):
            self._opt_dict = desc.select_options
        elif desc.options_attribute is not None:
            self._opt_dict = getattr(
                self._charger, desc.options_attribute, STATE_UNKNOWN
            )
        else:
            self._opt_dict = STATE_UNKNOWN
        if isinstance(self._opt_dict, dict):
            self._attr_options = list(self._opt_dict.values())

    async def _async_update_validate_platform_state(
        self, state: Any = None
    ) -> str | None:
        """Async: Validate the given state for select specific requirements."""
        try:
            if not isinstance(self._opt_dict, dict):
                return None
            if state in list(self._opt_dict.keys()):
                state = self._opt_dict[state]
            elif state in list(self._opt_dict.values()):
                pass
            else:
                _LOGGER.error(
                    "%s - %s: _async_update_validate_platform_state failed: state %s not within options_id values: %s",
                    self._charger_id,
                    self._identifier,
                    state,
                    self._opt_dict,
                )
                state = STATE_UNKNOWN
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

    async def async_select_option(self, option: str) -> None:
        """Async: Change the selected option."""
        try:
            if not isinstance(self._opt_dict, dict):
                _LOGGER.error(
                    "%s - %s: async_select_option: options dict not available",
                    self._charger_id,
                    self._identifier,
                )
                return
            key = list(self._opt_dict.keys())[
                list(self._opt_dict.values()).index(option)
            ]
            if key is None:
                _LOGGER.error(
                    "%s - %s: async_select_option: option %s not within options_id keys: %s",
                    self._charger_id,
                    self._identifier,
                    option,
                    self._opt_dict,
                )
                return
            _LOGGER.debug(
                "%s - %s: async_select_option: save option key %s",
                self._charger_id,
                self._identifier,
                key,
            )
            await async_SetChargerProp(self._charger, self._identifier, key)
        except Exception as e:
            _LOGGER.error(
                "%s - %s: async_select_option failed: %s (%s.%s)",
                self._charger_id,
                self._identifier,
                str(e),
                e.__class__.__module__,
                type(e).__name__,
            )
