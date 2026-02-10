"""Update entities for the Fronius Wattpilot integration."""

from __future__ import annotations

import asyncio
import functools
import logging
import re
from typing import TYPE_CHECKING, Any, Final

from homeassistant.components.update import (
    UpdateEntity,
    UpdateEntityFeature,
)
from homeassistant.const import (
    CONF_FRIENDLY_NAME,
    CONF_IP_ADDRESS,
    CONF_TIMEOUT,
)
from packaging.version import Version

from .const import (
    DEFAULT_NAME,
    DEFAULT_TIMEOUT,
)
from .descriptions import (
    SOURCE_PROPERTY,
    UPDATE_DESCRIPTIONS,
    WattpilotUpdateEntityDescription,
)
from .entities import ChargerPlatformEntity, filter_descriptions
from .utils import (
    GetChargerProp,
    async_SetChargerProp,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .types import WattpilotConfigEntry

_LOGGER: Final = logging.getLogger(__name__)
PLATFORM = "update"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: WattpilotConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the update platform."""
    _LOGGER.debug("Setting up %s platform entry: %s", PLATFORM, entry.entry_id)

    charger = entry.runtime_data.charger
    push_entities = entry.runtime_data.push_entities
    charger_id = str(
        entry.data.get(
            CONF_FRIENDLY_NAME, entry.data.get(CONF_IP_ADDRESS, DEFAULT_NAME)
        )
    )

    descriptions = filter_descriptions(UPDATE_DESCRIPTIONS, charger, entry, charger_id)

    entities: list[ChargerUpdate] = []
    for desc in descriptions:
        entity = ChargerUpdate(hass, entry, desc, charger)
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


class ChargerUpdate(ChargerPlatformEntity, UpdateEntity):
    """Update class for Fronius Wattpilot integration."""

    _state_attr = "_attr_latest_version"
    _dummy_version = "0.0.1"
    _available_versions: dict[str, str] = {}
    entity_description: WattpilotUpdateEntityDescription

    def _init_platform_specific(self) -> None:
        """Platform specific init actions."""
        desc = self.entity_description
        _LOGGER.debug(
            "%s - %s: _init_platform_specific", self._charger_id, self._identifier
        )
        self._identifier_installed = desc.id_installed
        self._identifier_trigger = desc.id_trigger
        self._identifier_status = desc.id_status

        self._attr_installed_version = GetChargerProp(
            self._charger, self._identifier_installed, None
        )
        self._attr_latest_version = self._update_available_versions(
            None, return_latest=True
        )

        if self._identifier_trigger is not None:
            self._attr_supported_features |= UpdateEntityFeature.INSTALL
            self._attr_supported_features |= UpdateEntityFeature.SPECIFIC_VERSION
        _LOGGER.debug(
            "%s - %s: _init_platform_specific complete",
            self._charger_id,
            self._identifier,
        )

    def _update_available_versions(
        self, v_list: list[str] | str | None = None, *, return_latest: bool = False
    ) -> str | None:
        """Get the latest update version of available versions."""
        _LOGGER.debug(
            "%s - %s: _update_available_versions", self._charger_id, self._identifier
        )
        try:
            if v_list is None:
                v_list = GetChargerProp(self._charger, self._identifier, None)
            if (
                v_list is None
                and hasattr(self, "_attr_installed_version")
                and self._attr_installed_version is not None
            ):
                v_list = [self._attr_installed_version]
            elif v_list is None:
                v_list = [self._dummy_version]
            elif not isinstance(v_list, list):
                v_list = [v_list]
            self._available_versions = self._get_versions_dict(v_list)
            latest = list(self._available_versions.keys())
            latest.sort(key=Version)
            return latest[-1]
        except Exception:
            _LOGGER.exception(
                "%s - %s: _update_available_versions failed",
                self._charger_id,
                self._identifier,
            )
            if return_latest:
                return self._dummy_version
            return None

    def _get_versions_dict(self, v_list: list[str]) -> dict[str, str]:
        """Create a dict with clean and named versions."""
        _LOGGER.debug("%s - %s: _get_versions_dict", self._charger_id, self._identifier)
        try:
            versions: dict[str, str] = {}
            for v in v_list:
                c = (v.lower()).replace("x", "0")
                c = re.sub(
                    r"^(v|ver|vers|version)*\s*\.*\s*([0-9.x]*)\s*-?\s*((alpha|beta|dev|rc|post|a|b|release)+[0-9]*)?\s*.*$",
                    r"\2\3",
                    c,
                )
                versions[c] = v
            return versions
        except Exception:
            _LOGGER.exception(
                "%s - %s: _get_versions_dict failed",
                self._charger_id,
                self._identifier,
            )
            return {}

    async def async_install(
        self, version: str | None, *, backup: bool, **kwargs: Any
    ) -> None:
        """Trigger update install."""
        _ = backup
        _ = kwargs
        try:
            _LOGGER.debug(
                "%s - %s: async_install: update charger to: %s",
                self._charger_id,
                self._identifier,
                version,
            )
            if version is None:
                version = self._attr_latest_version
            if version is not None:
                v_name = self._available_versions.get(version, None)
            else:
                v_name = None
            if v_name is None:
                _LOGGER.error(
                    "%s - %s: async_install failed: version (%s) not in available: %s",
                    self._charger_id,
                    self._identifier,
                    version,
                    self._available_versions,
                )
                return
            _LOGGER.debug(
                "%s - %s: async_install: trigger charger update via: %s -> %s",
                self._charger_id,
                self._identifier,
                self._identifier_trigger,
                v_name,
            )
            await async_SetChargerProp(
                self._charger,
                self._identifier_trigger,
                v_name,
                force=True,
                force_type=self._set_type,
            )

            # Get timeout from config
            timeout = DEFAULT_TIMEOUT
            runtime_data = getattr(self._entry, "runtime_data", None)
            if runtime_data is not None:
                config_params = runtime_data.params or {}
                timeout = config_params.get(CONF_TIMEOUT, DEFAULT_TIMEOUT)
            timeout = timeout * 4

            timer = 0
            while timeout > timer and self._charger.connected:
                await asyncio.sleep(1)
                timer += 1
            if self._charger.connected:
                _LOGGER.error(
                    "%s - %s: async_install: timeout during update install: %s sec",
                    self._charger_id,
                    self._identifier,
                    timeout,
                )
                return
            _LOGGER.debug(
                "%s - %s: async_install: charger disconnected - waiting for reconnect",
                self._charger_id,
                self._identifier,
            )
            timer = 0
            while timeout > timer and not self._charger.connected:
                await asyncio.sleep(1)
                timer += 1
            if not self._charger.connected:
                _LOGGER.error(
                    "%s - %s: async_install: timeout during charger restart: %s sec",
                    self._charger_id,
                    self._identifier,
                    timeout,
                )
                return
        except Exception:
            _LOGGER.exception(
                "%s - %s: async_install failed", self._charger_id, self._identifier
            )

    async def _async_update_validate_platform_state(
        self, state: Any = None
    ) -> str | None:
        """Async: Validate the given state for update specific requirements."""
        _LOGGER.debug(
            "%s - %s: _async_update_validate_platform_state",
            self._charger_id,
            self._identifier,
        )
        self._attr_installed_version = GetChargerProp(
            self._charger, self._identifier_installed, None
        )
        state = await self.hass.async_add_executor_job(
            functools.partial(
                self._update_available_versions, state, return_latest=True
            )
        )
        _LOGGER.debug(
            "%s - %s: _async_update_validate_platform_state: state: %s",
            self._charger_id,
            self._identifier,
            state,
        )
        return state
