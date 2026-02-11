# Wattpilot-HA Copilot Instructions

Custom Home Assistant integration for Fronius Wattpilot EV chargers using wattpilot-api (WebSocket gateway to chargers on local LAN or Fronius Cloud).

## Quick Start

```bash
scripts/setup      # Install uv, sync deps, install pre-commit hooks
scripts/develop    # Start HA at http://localhost:8123 with debug logging
scripts/lint       # Format and lint (ruff format + check --fix) - REQUIRED before commits
```

Dependency management uses `uv` with `pyproject.toml` + `uv.lock`. Config in `config/`. Debug logging already enabled in `config/configuration.yaml`.

## Architecture Overview

**Data Flow**: `WebSocket (wattpilot-api) → charger.all_properties → WattpilotCoordinator → CoordinatorEntity → HA state`

| Component         | Purpose                                                                                    |
| ----------------- | ------------------------------------------------------------------------------------------ |
| `__init__.py`     | Entry point: connects charger, creates coordinator, registers services, forwards platforms |
| `coordinator.py`  | `WattpilotCoordinator` wraps charger updates, provides centralized availability state      |
| `entities.py`     | Base `ChargerPlatformEntity(CoordinatorEntity)` with firmware/variant/connection filters   |
| `descriptions.py` | Dataclass entity descriptions (replaces YAML per-platform configs)                         |
| `{platform}.py`   | Platform implementation that loads descriptions and creates entities                       |
| `utils.py`        | Property helpers (`GetChargerProp`, `async_GetChargerProp`, `async_SetChargerProp`)        |
| `services.py`     | Integration services (set_next_trip, disconnect_charger, etc.)                             |

## wattpilot-api Package

The integration uses the external `wattpilot-api>=1.0.0` package (from PyPI). Key types and patterns:

```python
from wattpilot_api import Wattpilot, LoadMode, CarStatus

# Main client class with WebSocket connection
charger = Wattpilot(host, password)  # local connection
await charger.connect()
await charger.disconnect()

# Properties access
charger.all_properties  # Dict of all current property values
charger.connected  # Boolean connection state
charger.properties_initialized  # Boolean - all properties loaded
charger.name, charger.serial, charger.firmware  # Device identifiers

# Callbacks (async-friendly)
async def on_property_change(charger_id: str, value: Any) -> None:
    ...

unsub = charger.on_property_change(on_property_change)  # returns unsubscribe callable
unsub()  # disconnect the callback

# Enums and constants
LoadMode.DEFAULT  # 3
LoadMode.ECO      # 4
LoadMode.NEXTTRIP # 5
```

## Entity Descriptions (descriptions.py)

Entities are defined as dataclass descriptions in `descriptions.py`, not separate YAML files. Pattern:

```python
from homeassistant.components.sensor import SensorEntityDescription
from .descriptions import (
    WattpilotSensorEntityDescription,
    SENSOR_DESCRIPTIONS,
    filter_descriptions
)

# In platform setup
descriptions = filter_descriptions(SENSOR_DESCRIPTIONS, charger, entry, charger_id)
for desc in descriptions:
    entity = ChargerSensor(hass, entry, desc, charger)
    entities.append(entity)

# Description definition (in descriptions.py)
WattpilotSensorEntityDescription(
    key="session_energy",
    charger_key="wh",  # go-eCharger API key
    name="Session Energy",
    source=SOURCE_PROPERTY,  # "property" | "attribute" | "namespacelist"
    device_class=SensorDeviceClass.ENERGY,
    state_class=SensorStateClass.TOTAL_INCREASING,
    native_unit_of_measurement="Wh",
    firmware=">=38.5",  # Optional version constraint
    variant="11",        # Optional variant filter
    connection="local",  # Optional connection filter
)
```

**Adding entities**:

1. Find charger API key in [go-eCharger API v2](https://github.com/goecharger/go-eCharger-API-v2/blob/main/apikeys-en.md)
2. Create `WattpilotXXXEntityDescription` in `descriptions.py` with appropriate `source` and platform-specific fields
3. Add to `XXX_DESCRIPTIONS` list - entity auto-created by platform setup

## Data Update Coordinator Pattern

The integration uses `DataUpdateCoordinator` for centralized data management and availability handling:

```python
# In __init__.py during setup_entry
coordinator = WattpilotCoordinator(hass, charger, entry)
await coordinator.async_config_entry_first_refresh()

entry.runtime_data = WattpilotRuntimeData(
    charger=charger,
    coordinator=coordinator,  # Coordinator instance
    push_entities={},
    params=dict(entry.data),
)

# Register callback for WebSocket property updates
async def _on_property_change(identifier: str, value: Any) -> None:
    await async_property_update_handler(hass, entry, identifier, value)

unsub = charger.on_property_change(_on_property_change)
entry.runtime_data.property_updates_callback = unsub  # Save for cleanup
```

**Coordinator state management**:

- `coordinator.data`: Current `charger.all_properties` dict
- `coordinator.available`: True if charger connected AND properties initialized
- `async_handle_property_update(key, value)`: Called from property update handler to update data and notify listeners
- Entities inherit from `CoordinatorEntity` and check `coordinator.available` for state

## Key Patterns

```python
# Property access (from utils.py)
from .utils import async_GetChargerProp, async_SetChargerProp, GetChargerProp

value = await async_GetChargerProp(charger, 'amp', default=6)  # async read
await async_SetChargerProp(charger, 'amp', 16)                 # async write
value = GetChargerProp(charger, 'amp', default=6)              # sync read (from coordinator.data)

# Modern HA runtime data storage pattern (entry.runtime_data)
charger = entry.runtime_data.charger
coordinator = entry.runtime_data.coordinator
push_entities = entry.runtime_data.push_entities

# Entity base pattern (inherits from CoordinatorEntity)
class ChargerSensor(ChargerPlatformEntity, SensorEntity):
    @property
    def native_value(self) -> StateType:
        """Return sensor value from coordinator data."""
        if self.coordinator.data is None:
            return self._default_state
        return self.coordinator.data.get(self._identifier, self._default_state)

    @property
    def available(self) -> bool:
        """Check availability based on coordinator."""
        return self.coordinator.available and not self._init_failed

# Logging convention (includes entry_id for debugging)
_LOGGER.debug("%s - %s: message", entry.entry_id, method_name)
```

## Services Pattern

Services are registered once globally (even with multiple config entries). Defined in `services.yaml` (schema) + `services.py` (implementation):

```python
# Registration in __init__.py (only once, even if multiple entries)
if not hass.data.get(DOMAIN, {}).get("services_registered"):
    await async_registerService(hass, "set_next_trip", async_service_SetNextTrip)
    hass.data.setdefault(DOMAIN, {})["services_registered"] = True

# Service implementation pattern (services.py)
async def async_service_SetNextTrip(hass: HomeAssistant, call: ServiceCall) -> None:
    device_id = call.data.get(CONF_DEVICE_ID)
    if device_id is None:
        _LOGGER.error("%s - async_service_SetNextTrip: device_id required", DOMAIN)
        return

    charger = await async_GetChargerFromDeviceID(hass, device_id)
    await async_SetChargerProp(charger, 'ftt', timestamp)
```

## Common API Keys

Reference: [go-eCharger API v2 Documentation](https://github.com/goecharger/go-eCharger-API-v2/blob/main/apikeys-en.md)

Common charger properties used in sensors and controls:

- `car`: carState (1=Idle, 2=Charging, 3=WaitCar, 4=Complete)
- `amp`: requestedCurrent (Ampere) - typically 6-16A or 6-32A
- `frc`: forceState (0=Neutral, 1=Off, 2=On)
- `lmo`: logic mode (3=Default, 4=Eco, 5=NextTrip)
- `nrg`: energy array (voltages, currents, power, power factor)
- `eto`: total energy (Wh) - for Energy Dashboard
- `wh`: session energy (Wh) - per-charge tracking

## Platform-Specific Entity Setup

Each platform (`sensor.py`, `switch.py`, `button.py`, etc.) follows this pattern:

```python
async def async_setup_entry(hass, entry, async_add_entities):
    charger = entry.runtime_data.charger
    charger_id = entry.data.get(CONF_FRIENDLY_NAME, ...default...)

    # Filter descriptions by firmware, variant, connection type
    descriptions = filter_descriptions(
        SENSOR_DESCRIPTIONS,
        charger,      # Used to get firmware version and variant
        entry,        # Config entry
        charger_id    # Charger identifier for logging
    )

    # Create entity from each description
    entities = [
        ChargerSensor(hass, entry, desc, charger)
        for desc in descriptions
        if not getattr(entity, "_init_failed", False)
    ]

    if entities:
        async_add_entities(entities)
```

**filter_descriptions** helper:

- Filters descriptions by firmware version constraint (`firmware=">=40.0"`)
- Filters by device variant (`variant="11"` or `variant="22"` for kW)
- Filters by connection type (`connection="local"` or `connection="cloud"`)
- Returns only applicable descriptions for this charger

## Configuration & Standards

**Home Assistant Integration Rules**

- Always use `entry.runtime_data` for storing runtime state (not `hass.data[DOMAIN]`)
- Use `DataUpdateCoordinator` for coordinated entity updates
- Use `ConfigEntry` typed as `WattpilotConfigEntry` with runtime data
- Entities must inherit from `CoordinatorEntity` and implement `available` property
- Use translation keys for user-facing strings (defined in `strings.json`)

**Code Quality**

- Pre-commit hooks enforce ruff formatting, codespell, YAML linting, and JSON validation
- Tests require 90%+ coverage (configured in `pyproject.toml`)
- pytest configuration: `asyncio_mode = "auto"` with `pytest-asyncio`
- All code must pass ruff format and ruff check

**Testing**

- Test fixtures in `tests/conftest.py` provide mocked Home Assistant and charger instances
- Use `pytest-homeassistant-custom-component` for HA test utilities
- Tests are in `tests/` and mirror the structure of `custom_components/wattpilot/`
- Async tests use `@pytest.mark.asyncio` decorator on test methods in classes
