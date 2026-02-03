"""DataUpdateCoordinator for the Fronius Wattpilot integration."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import TYPE_CHECKING, Any, Final

from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry

_LOGGER: Final = logging.getLogger(__name__)

# Default intervals - None for push-based updates
DEFAULT_UPDATE_INTERVAL: Final = None  # Push-based, no polling needed
ERROR_UPDATE_INTERVAL: Final = timedelta(minutes=5)


class WattpilotCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """
    Coordinator for Wattpilot charger data.

    This coordinator wraps the WebSocket push-based updates from the Wattpilot
    charger. It provides:
    - Centralized availability handling
    - Coordinated entity updates
    - Error state management
    - Logging when device becomes unavailable
    """

    def __init__(
        self,
        hass: HomeAssistant,
        charger: Any,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the coordinator."""
        self.charger = charger
        self._failed_update_count = 0
        self._max_failed_updates = 3

        # Get charger identifiers for logging
        self.charger_name = getattr(charger, "name", "Unknown")
        self.charger_serial = getattr(charger, "serial", "Unknown")

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{self.charger_serial}",
            config_entry=config_entry,
            update_interval=DEFAULT_UPDATE_INTERVAL,  # Push-based, no polling
        )

        _LOGGER.debug(
            "WattpilotCoordinator initialized for %s (%s)",
            self.charger_name,
            self.charger_serial,
        )

    @property
    def available(self) -> bool:
        """Return if the charger is available."""
        return bool(
            getattr(self.charger, "connected", False)
            and getattr(self.charger, "allPropsInitialized", False)
        )

    @callback
    def async_set_updated_data(self, data: dict[str, Any]) -> None:
        """
        Manually update data and notify listeners.

        Called from property update handler when WebSocket pushes new data.
        """
        self._failed_update_count = 0
        super().async_set_updated_data(data)

    @callback
    def async_handle_property_update(self, identifier: str, value: Any) -> None:
        """
        Handle a property update from the charger.

        This is called when the WebSocket receives a property update.
        """
        if self.data is None:
            self.data = {}

        # Update the specific property in our data
        self.data[identifier] = value

        # Reset error count on successful update
        self._failed_update_count = 0

        # Notify all listeners of the update
        self.async_update_listeners()

    async def _async_update_data(self) -> dict[str, Any]:
        """
        Fetch data from the charger.

        For push-based updates, this primarily validates connection state.
        This method is called during initial refresh or manual refresh requests.
        """
        if not self.available:
            self._failed_update_count += 1
            if self._failed_update_count >= self._max_failed_updates:
                _LOGGER.warning(
                    "Charger %s (%s) is unavailable after %d attempts",
                    self.charger_name,
                    self.charger_serial,
                    self._failed_update_count,
                )
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="charger_unavailable",
                translation_placeholders={
                    "name": self.charger_name,
                    "serial": self.charger_serial,
                },
            )

        # Return current properties from charger
        try:
            all_props = getattr(self.charger, "allProps", {})
            if all_props is None:
                all_props = {}
            return dict(all_props)
        except Exception as err:
            self._failed_update_count += 1
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="update_failed",
                translation_placeholders={"error": str(err)},
            ) from err

    async def async_config_entry_first_refresh(self) -> None:
        """Perform first refresh and raise ConfigEntryNotReady on failure."""
        try:
            await super().async_config_entry_first_refresh()
        except UpdateFailed as err:
            raise ConfigEntryNotReady(
                translation_domain=DOMAIN,
                translation_key="entry_cannot_connect",
                translation_placeholders={
                    "name": self.charger_name,
                    "serial": self.charger_serial,
                    "error": str(err),
                },
            ) from err

    @callback
    def async_log_unavailable(self) -> None:
        """Log when the charger becomes unavailable."""
        _LOGGER.warning(
            "Charger %s (%s) is now unavailable",
            self.charger_name,
            self.charger_serial,
        )

    @callback
    def async_log_available(self) -> None:
        """Log when the charger becomes available again."""
        _LOGGER.info(
            "Charger %s (%s) is now available",
            self.charger_name,
            self.charger_serial,
        )
