"""Base entities for the Fronius Wattpilot integration."""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any, Final

from homeassistant.const import STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from packaging.version import InvalidVersion, Version

from .const import (
    CONF_CONNECTION,
    DOMAIN,
)
from .descriptions import (
    SOURCE_ATTRIBUTE,
    SOURCE_NAMESPACELIST,
    SOURCE_PROPERTY,
    WattpilotDescriptionMixin,
)
from .utils import (
    GetChargerProp,
    async_GetChargerProp,
)

if TYPE_CHECKING:
    from .types import WattpilotConfigEntry

_LOGGER: Final = logging.getLogger(__name__)

PARALLEL_UPDATES = 1


def check_firmware_supported(
    charger: Any,
    firmware_constraint: str | None,
    charger_id: str,
    identifier: str,
) -> bool:
    """Return whether the current charger firmware satisfies the constraint."""
    if firmware_constraint is None:
        return True
    fw = getattr(charger, "firmware", GetChargerProp(charger, "onv", None))
    if fw is None:
        _LOGGER.error(
            "%s - %s: check_firmware_supported: Cannot identify charger firmware",
            charger_id,
            identifier,
        )
        return False
    try:
        if firmware_constraint[:2] == ">=":
            version_str = firmware_constraint[2:]
            if not version_str:
                msg = "Empty version string"
                raise InvalidVersion(msg)
            result = Version(fw) >= Version(version_str)
        elif firmware_constraint[:2] == "<=":
            version_str = firmware_constraint[2:]
            if not version_str:
                msg = "Empty version string"
                raise InvalidVersion(msg)
            result = Version(fw) <= Version(version_str)
        elif firmware_constraint[:2] == "==":
            version_str = firmware_constraint[2:]
            if not version_str:
                msg = "Empty version string"
                raise InvalidVersion(msg)
            result = Version(fw) == Version(version_str)
        elif firmware_constraint[:1] == ">":
            version_str = firmware_constraint[1:]
            if not version_str:
                msg = "Empty version string"
                raise InvalidVersion(msg)
            result = Version(fw) > Version(version_str)
        elif firmware_constraint[:1] == "<":
            version_str = firmware_constraint[1:]
            if not version_str:
                msg = "Empty version string"
                raise InvalidVersion(msg)
            result = Version(fw) < Version(version_str)
        else:
            _LOGGER.error(
                "%s - %s: check_firmware_supported: Invalid firmware constraint: %s",
                charger_id,
                identifier,
                firmware_constraint,
            )
            return False
    except InvalidVersion:
        _LOGGER.error(
            "%s - %s: check_firmware_supported: Invalid version in constraint: %s",
            charger_id,
            identifier,
            firmware_constraint,
        )
        return False
    _LOGGER.debug(
        "%s - %s: check_firmware_supported (%s%s -> %s)",
        charger_id,
        identifier,
        fw,
        firmware_constraint,
        result,
    )
    return result


def check_variant_supported(
    charger: Any,
    variant_filter: str | None,
    charger_id: str,
    identifier: str,
) -> bool:
    """Return whether the current charger variant matches the filter."""
    if variant_filter is None:
        return True
    variant = getattr(charger, "variant", GetChargerProp(charger, "var", 11))
    result = str(variant).upper() == str(variant_filter).upper()
    _LOGGER.debug(
        "%s - %s: check_variant_supported (%s=%s -> %s)",
        charger_id,
        identifier,
        variant,
        variant_filter,
        result,
    )
    return result


def check_connection_supported(
    entry: WattpilotConfigEntry,
    connection_filter: str | None,
    charger_id: str,
    identifier: str,
) -> bool:
    """Return whether the current connection type matches the filter."""
    if connection_filter is None:
        return True
    runtime_data = getattr(entry, "runtime_data", None)
    if runtime_data is None:
        return True
    config_params = runtime_data.params or {}
    connection = config_params.get(CONF_CONNECTION, STATE_UNKNOWN)
    result = str(connection).upper() == str(connection_filter).upper()
    _LOGGER.debug(
        "%s - %s: check_connection_supported (%s=%s -> %s)",
        charger_id,
        identifier,
        connection,
        connection_filter,
        result,
    )
    return result


def filter_descriptions[T: WattpilotDescriptionMixin](
    descriptions: list[T],
    charger: Any,
    entry: WattpilotConfigEntry,
    charger_id: str,
) -> list[T]:
    """Filter entity descriptions by firmware, variant and connection constraints."""
    result: list[T] = []
    for desc in descriptions:
        identifier = desc.charger_key
        if not check_firmware_supported(charger, desc.firmware, charger_id, identifier):
            _LOGGER.debug(
                "%s - %s: Skipped (firmware constraint: %s)",
                charger_id,
                identifier,
                desc.firmware,
            )
            continue
        if not check_variant_supported(charger, desc.variant, charger_id, identifier):
            _LOGGER.debug(
                "%s - %s: Skipped (variant filter: %s)",
                charger_id,
                identifier,
                desc.variant,
            )
            continue
        if not check_connection_supported(
            entry, desc.connection, charger_id, identifier
        ):
            _LOGGER.debug(
                "%s - %s: Skipped (connection filter: %s)",
                charger_id,
                identifier,
                desc.connection,
            )
            continue
        result.append(desc)
    return result


class ChargerPlatformEntity(CoordinatorEntity["WattpilotCoordinator"]):
    """Base class for Fronius Wattpilot integration."""

    _attr_has_entity_name = True
    _state_attr = "state"

    def __init__(
        self,
        hass: HomeAssistant,
        entry: WattpilotConfigEntry,
        description: WattpilotDescriptionMixin,
        charger: Any,
    ) -> None:
        """Initialize the object."""
        coordinator = entry.runtime_data.coordinator
        super().__init__(coordinator)

        # Set _init_failed early so it's available even if exceptions occur
        self._init_failed = True

        try:
            self._charger_id = str(getattr(charger, "serial", entry.entry_id))
            self._identifier = description.charger_key
            _LOGGER.debug("%s - %s: __init__", self._charger_id, self._identifier)

            self._charger = charger
            self._source = description.source
            self._namespace_id = description.namespace_id
            self._default_state = description.default_state
            self._set_type = description.set_type
            self.entity_description = description  # type: ignore[assignment]

            self._entry = entry
            self.hass = hass

            # Validate the charger actually has the property/attribute
            if self._source == SOURCE_ATTRIBUTE and not hasattr(
                self._charger, self._identifier
            ):
                _LOGGER.error(
                    "%s - %s: __init__: Charger does not have attribute: %s (maybe a property?)",
                    self._charger_id,
                    self._identifier,
                    self._identifier,
                )
                return
            if self._source == SOURCE_PROPERTY:
                # Use sentinel to detect missing properties (None might be a valid value)
                sentinel = object()
                prop_value = GetChargerProp(self._charger, self._identifier, sentinel)
                if prop_value is sentinel:
                    _LOGGER.warning(
                        "%s - %s: __init__: Charger does not have property: %s (maybe an attribute?)",
                        self._charger_id,
                        self._identifier,
                        self._identifier,
                    )
                    return
            if self._source == SOURCE_NAMESPACELIST:
                ns_val = GetChargerProp(
                    self._charger, self._identifier, self._default_state
                )
                try:
                    ns_idx = int(self._namespace_id)
                except (TypeError, ValueError):
                    _LOGGER.error(
                        "%s - %s: __init__: Invalid namespacelist index: %s[%s]",
                        self._charger_id,
                        self._identifier,
                        self._identifier,
                        self._namespace_id,
                    )
                    return
                if (
                    not isinstance(ns_val, (list, tuple))
                    or ns_idx < 0
                    or ns_idx >= len(ns_val)
                    or ns_val[ns_idx] is None
                ):
                    _LOGGER.error(
                        "%s - %s: __init__: Charger does not have namespacelist item: %s[%s]",
                        self._charger_id,
                        self._identifier,
                        self._identifier,
                        self._namespace_id,
                    )
                    return

            self._init_failed = False

            self._attributes: dict[str, Any] = {}
            self._attributes["description"] = description.description_text
            setattr(
                self,
                self._state_attr,
                description.default_state,
            )

            self._init_platform_specific()

            uid = description.uid or description.charger_key
            self._attr_unique_id = f"{self._charger_id}-{uid}"
            if self._init_failed:
                return
        except Exception as e:
            _LOGGER.error(
                "%s - %s: __init__ failed: %s (%s.%s)",
                getattr(self, "_charger_id", "unknown"),
                getattr(self, "_identifier", "unknown"),
                str(e),
                e.__class__.__module__,
                type(e).__name__,
            )
            return

    def _init_platform_specific(self) -> None:
        """Platform specific init actions."""

    @property
    def description(self) -> str | None:
        """Return the description of the entity."""
        return self._attributes.get("description", None)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes of the entity."""
        return self._attributes

    @property
    def available(self) -> bool:
        """Return if device is available."""
        # Use getattr for _charger_id and _identifier in case init failed early
        charger_id = getattr(self, "_charger_id", "unknown")
        identifier = getattr(self, "_identifier", "unknown")

        if not super().available:
            _LOGGER.debug(
                "%s - %s: available: false because coordinator unavailable",
                charger_id,
                identifier,
            )
            return False
        if getattr(self, "_init_failed", True):
            _LOGGER.debug(
                "%s - %s: available: false because entity init not complete",
                charger_id,
                identifier,
            )
            return False
        if not getattr(self._charger, "connected", True):
            _LOGGER.debug(
                "%s - %s: available: false because charger disconnected",
                charger_id,
                identifier,
            )
            return False
        if not getattr(self._charger, "properties_initialized", True):
            _LOGGER.debug(
                "%s - %s: available: false because not all properties initialized",
                charger_id,
                identifier,
            )
            return False
        if self._source == SOURCE_ATTRIBUTE and not hasattr(
            self._charger, self._identifier
        ):
            _LOGGER.debug(
                "%s - %s: available: false because unknown attribute",
                charger_id,
                identifier,
            )
            return False
        if (
            self._source == SOURCE_PROPERTY
            and GetChargerProp(self._charger, self._identifier, self._default_state)
            is None
        ):
            _LOGGER.debug(
                "%s - %s: available: false because unknown property",
                charger_id,
                identifier,
            )
            return False
        if self._source == SOURCE_NAMESPACELIST:
            ns_val = GetChargerProp(
                self._charger, self._identifier, self._default_state
            )
            # Treat non-list/tuple as unavailable
            if not isinstance(ns_val, (list, tuple)):
                _LOGGER.debug(
                    "%s - %s: available: false because namespacelist is not a list/tuple: %s[%s]",
                    charger_id,
                    identifier,
                    self._namespace_id,
                    type(ns_val).__name__,
                )
                return False
            try:
                ns_idx = int(self._namespace_id)
            except (TypeError, ValueError):
                ns_idx = -1
            if ns_idx < 0 or ns_idx >= len(ns_val) or ns_val[ns_idx] is None:
                _LOGGER.debug(
                    "%s - %s: available: false because unknown namespacelist item: %s",
                    self._charger_id,
                    self._identifier,
                    self._namespace_id,
                )
                return False
        return True

    @property
    def should_poll(self) -> bool:
        """Return True if polling is needed."""
        if self._source == SOURCE_ATTRIBUTE:
            return True
        if self._source == SOURCE_NAMESPACELIST:
            return True
        return getattr(self, self._state_attr, STATE_UNKNOWN) == (
            self._default_state if self._default_state is not None else STATE_UNKNOWN
        )

    @property
    def device_info(self) -> DeviceInfo:
        """Return a device description for device registry."""
        serial = getattr(self._charger, "serial", None)
        model = getattr(self._charger, "model", None)
        variant = getattr(self._charger, "variant", None)
        # Use entry_id as fallback if serial is missing to avoid collisions
        device_id = serial or self._entry.entry_id
        return DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            manufacturer=getattr(self._charger, "manufacturer", None),
            model=model,
            name=getattr(
                self._charger,
                "name",
                getattr(self._charger, "hostname", None),
            ),
            sw_version=getattr(self._charger, "firmware", None),
            hw_version=f"{variant} KW" if variant else None,
        )

    async def async_update(self) -> None:
        """Async: Get latest data and states for the entity."""
        try:
            if not self.enabled:
                return
            if not self.available:
                return
            if self.should_poll:
                _LOGGER.debug(
                    "%s - %s: async_update via poll",
                    self._charger_id,
                    self._identifier,
                )
                await self.async_local_poll()
            else:
                _LOGGER.debug(
                    "%s - %s: async_update via push - waiting",
                    self._charger_id,
                    self._identifier,
                )
        except Exception as e:
            _LOGGER.error(
                "%s - %s: async_update failed: %s (%s.%s)",
                self._charger_id,
                self._identifier,
                str(e),
                e.__class__.__module__,
                type(e).__name__,
            )

    async def _async_update_validate_property(self, state: Any = None) -> Any | None:
        """Async: Validate the given state, set attributes if necessary and return new state."""
        desc = self.entity_description
        try:
            if str(state).startswith("namespace"):
                _LOGGER.debug(
                    "%s - %s: _async_update_validate_property: process namespace value",
                    self._charger_id,
                    self._identifier,
                )
                namespace = state
                if desc.value_id is None:
                    _LOGGER.error(
                        "%s - %s: _async_update_validate_property failed: "
                        "please specify 'value_id' for state value",
                        self._charger_id,
                        self._identifier,
                    )
                    return None
                state = getattr(namespace, str(desc.value_id), STATE_UNKNOWN)
                for attr_id in desc.attribute_ids or []:
                    self._attributes[attr_id] = getattr(
                        namespace, attr_id, STATE_UNKNOWN
                    )
            elif isinstance(state, list):
                state_list = state
                if desc.value_id is None:
                    state = state_list[0]
                    for i, attr_state in enumerate(state_list[1:], start=1):
                        self._attributes[f"state{i}"] = attr_state
                else:
                    state = state_list[int(desc.value_id)]
                    for attr_entry in desc.attribute_ids or []:
                        attr_id = attr_entry.split(":")[0]
                        attr_index = attr_entry.split(":")[1]
                        self._attributes[attr_id] = state_list[int(attr_index)]
            return state
        except Exception as e:
            _LOGGER.error(
                "%s - %s: _async_update_validate_property failed: %s (%s.%s)",
                self._charger_id,
                self._identifier,
                str(e),
                e.__class__.__module__,
                type(e).__name__,
            )
            return None

    async def _async_update_validate_platform_state(
        self, state: Any = None
    ) -> Any | None:
        """Async: Validate the given state for platform specific requirements."""
        return state

    async def async_local_poll(self) -> None:
        """Async: Poll the latest data and states from the entity."""
        try:
            _LOGGER.debug(
                "%s - %s: async_local_poll", self._charger_id, self._identifier
            )
            if self._source == SOURCE_ATTRIBUTE:
                state = getattr(self._charger, self._identifier, self._default_state)
            elif self._source == SOURCE_NAMESPACELIST:
                state = await async_GetChargerProp(
                    self._charger, self._identifier, self._default_state
                )
                try:
                    ns_idx = int(self._namespace_id)
                except (TypeError, ValueError):
                    _LOGGER.error(
                        "%s - %s: async_local_poll invalid namespacelist index: %s",
                        self._charger_id,
                        self._identifier,
                        self._namespace_id,
                    )
                    return
                if not isinstance(state, (list, tuple)) or ns_idx >= len(state):
                    _LOGGER.error(
                        "%s - %s: async_local_poll namespacelist index out of range: %s",
                        self._charger_id,
                        self._identifier,
                        self._namespace_id,
                    )
                    return

                state = state[ns_idx]
                _LOGGER.debug(
                    "%s - %s: async_local_poll namespace pre validate state of %s: %s",
                    self._charger_id,
                    self._identifier,
                    self._attr_unique_id,
                    state,
                )
                state = await self._async_update_validate_property(state)
                _LOGGER.debug(
                    "%s - %s: async_local_poll namespace post validate state of %s: %s",
                    self._charger_id,
                    self._identifier,
                    self._attr_unique_id,
                    state,
                )
            elif self._source == SOURCE_PROPERTY:
                state = await async_GetChargerProp(
                    self._charger, self._identifier, self._default_state
                )
                state = await self._async_update_validate_property(state)

            state = await self._async_update_validate_platform_state(state)
            if state is not None:
                setattr(self, self._state_attr, state)
                self.async_write_ha_state()
        except Exception as e:
            _LOGGER.error(
                "%s - %s: async_local_poll failed: %s (%s.%s)",
                self._charger_id,
                self._identifier,
                str(e),
                e.__class__.__module__,
                type(e).__name__,
            )

    async def async_local_push(self, state: Any = None, initwait: bool = False) -> None:
        """Async: Get the latest status from the entity after an update was pushed."""
        try:
            if not self.enabled:
                return
            _LOGGER.debug(
                "%s - %s: async_local_push", self._charger_id, self._identifier
            )
            if self._source == SOURCE_ATTRIBUTE:
                pass
            elif self._source == SOURCE_NAMESPACELIST:
                try:
                    ns_idx = int(self._namespace_id)
                except (TypeError, ValueError):
                    _LOGGER.error(
                        "%s - %s: async_local_push invalid namespacelist index: %s",
                        self._charger_id,
                        self._identifier,
                        self._namespace_id,
                    )
                    state = None
                else:
                    if isinstance(state, (list, tuple)) and ns_idx < len(state):
                        state = state[ns_idx]
                    else:
                        state = None
                state = await self._async_update_validate_property(state)
            elif self._source == SOURCE_PROPERTY:
                state = await self._async_update_validate_property(state)

            state = await self._async_update_validate_platform_state(state)
            if state is not None:
                setattr(self, self._state_attr, state)
                self.async_write_ha_state()
            else:
                await self.async_local_poll()
        except Exception as e:
            if type(e).__name__ == "NoEntitySpecifiedError" and not initwait:
                _LOGGER.debug(
                    "%s - %s: async_local_push: wait and retry once for setup init delay",
                    self._charger_id,
                    self._identifier,
                )
                await asyncio.sleep(5)
                await self.async_local_push(state, True)
            else:
                _LOGGER.error(
                    "%s - %s: async_local_push failed: %s (%s.%s)",
                    self._charger_id,
                    self._identifier,
                    str(e),
                    e.__class__.__module__,
                    type(e).__name__,
                )
