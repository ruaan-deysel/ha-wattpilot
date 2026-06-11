"""Button entities for the Fronius Wattpilot integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Final

from homeassistant.components.button import ButtonEntity
from homeassistant.const import (
    CONF_FRIENDLY_NAME,
    CONF_IP_ADDRESS,
)
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from .const import DEFAULT_NAME
from .descriptions import (
    BUTTON_DESCRIPTIONS,
    WattpilotButtonEntityDescription,
)
from .entities import ChargerPlatformEntity, filter_descriptions
from .utils import async_SetChargerProp

if TYPE_CHECKING:
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .types import WattpilotConfigEntry

_LOGGER: Final = logging.getLogger(__name__)
PLATFORM = "button"
PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: WattpilotConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the button platform."""
    _LOGGER.debug("Setting up %s platform entry: %s", PLATFORM, entry.entry_id)

    charger = entry.runtime_data.charger
    charger_id = str(
        entry.data.get(
            CONF_FRIENDLY_NAME, entry.data.get(CONF_IP_ADDRESS, DEFAULT_NAME)
        )
    )

    descriptions = filter_descriptions(BUTTON_DESCRIPTIONS, charger, entry, charger_id)

    entities: list[ChargerButton] = []
    for desc in descriptions:
        entity = ChargerButton(hass, entry, desc, charger)
        if getattr(entity, "_init_failed", True):
            continue
        entities.append(entity)

    _LOGGER.info(
        "%s - async_setup_entry: setup %s %s entities",
        entry.entry_id,
        len(entities),
        PLATFORM,
    )
    if entities:
        async_add_entities(entities)


class ChargerButton(ChargerPlatformEntity, ButtonEntity):
    """Button class for Fronius Wattpilot integration."""

    entity_description: WattpilotButtonEntityDescription

    def _init_platform_specific(self) -> None:
        """Platform specific init actions."""
        if self.entity_description.set_value is None:
            _LOGGER.error(
                "%s - %s: __init__: Required 'set_value' missing in description",
                self._charger_id,
                self._identifier,
            )
            self._init_failed = True

    async def async_added_to_hass(self) -> None:
        """
        Discard invalid restored state from older integration versions.

        Older versions wrote the raw charger property value (e.g. frc=0/1/2)
        into the button state, which HA restores and renders as a bogus
        'pressed N days ago' timestamp.
        """
        await super().async_added_to_hass()
        state = self.state
        if state is not None and dt_util.parse_datetime(state) is None:
            _LOGGER.debug(
                "%s - %s: discarding invalid restored button state: %s",
                self._charger_id,
                self._identifier,
                state,
            )
            # ButtonEntity caches its state; reset both the cache and the
            # underlying last-pressed value (name-mangled private attribute).
            self.__dict__.pop("state", None)
            self._ButtonEntity__last_pressed_isoformat = None
            self.async_write_ha_state()

    async def async_local_poll(self) -> None:
        """Async: Poll the latest data and states from the entity."""
        # No state required for ButtonEntity

    async def async_press(self) -> None:
        """Async: Handle button press."""
        try:
            await async_SetChargerProp(
                self._charger,
                self._identifier,
                self.entity_description.set_value,
            )
        except Exception as e:
            _LOGGER.error(
                "%s - %s: update failed: %s (%s.%s)",
                self._charger_id,
                self._identifier,
                str(e),
                e.__class__.__module__,
                type(e).__name__,
            )
