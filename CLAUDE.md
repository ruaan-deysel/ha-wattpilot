# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a Home Assistant custom integration for Fronius Wattpilot EV chargers. It uses a reverse-engineered WebSocket API to communicate with the charger via local LAN or Fronius Cloud. The integration follows Home Assistant's Silver quality scale standards with DataUpdateCoordinator, comprehensive tests, and CI/CD.

## Key Development Commands

### Testing

```bash
./scripts/test                  # Run all tests
./scripts/test tests/test_sensor.py  # Run specific test file
python -m pytest tests/ -v --tb=short  # Direct pytest invocation
python -m pytest tests/ -k test_name   # Run specific test by name
python -m pytest tests/ --cov --cov-report=term-missing  # With coverage
```

### Linting

```bash
./scripts/lint                  # Format and lint with ruff
ruff format .                   # Format only
ruff check . --fix              # Lint only with auto-fix
pre-commit run --all-files      # Run all pre-commit hooks
```

### Development Environment

```bash
./scripts/setup                 # Install dependencies from requirements.txt
pip install -e ".[dev]"         # Install with dev dependencies
./scripts/develop               # Start Home Assistant dev instance with this integration
```

The dev instance uses `config/` directory for Home Assistant configuration and sets `PYTHONPATH` to include `custom_components/` to load the integration.

## Architecture

### Core Components

**Entry Point (`__init__.py`)**

- `async_setup_entry`: Main setup flow - connects charger, creates coordinator, registers services, forwards to platforms
- `async_unload_entry`: Cleanup - unloads platforms, disconnects charger, removes event handlers
- Services are registered globally once across all config entries (tracked by `_SERVICES_REGISTERED`)
- Property update handler bridges WebSocket events to entity updates via `PropertyUpdateHandler`

**Data Flow**

```
Wattpilot WebSocket (push) → PropertyUpdateHandler → Coordinator → CoordinatorEntity (sensors/switches/etc)
```

**DataUpdateCoordinator (`coordinator.py`)**

- `WattpilotCoordinator`: Wraps WebSocket push-based updates (no polling by default)
- `available` property: Checks `charger.connected` and `charger.allPropsInitialized`
- `async_handle_property_update`: Called when WebSocket receives property updates
- `_async_update_data`: Validates connection state and returns `charger.allProps`

**Runtime Data (`types.py`)**

- `WattpilotRuntimeData`: Stored in `entry.runtime_data` (modern Home Assistant pattern)
  - `charger`: Wattpilot client instance (from vendored module)
  - `coordinator`: WattpilotCoordinator instance
  - `push_entities`: Dict of entities receiving property updates
  - `params`: Connection configuration
  - `options_update_listener`: Callback for config changes
  - `property_updates_callback`: Callback for WebSocket events

**Base Entity (`entities.py`)**

- `ChargerPlatformEntity`: Base class for all platform entities (sensors, switches, etc.)
- Inherits from `CoordinatorEntity` for coordinated updates
- Supports filtering by firmware version, device variant, and connection type
- Properties can be sourced from `property` (charger properties), `attribute` (charger attributes), or `namespacelist`
- Uses `GetChargerProp` and `async_GetChargerProp` utilities to access charger data

**Platform Implementation Pattern**
Each platform (sensor, switch, button, number, select, update) follows this pattern:

1. YAML file (e.g., `sensor.yaml`) defines entity configurations
2. Python file (e.g., `sensor.py`) implements the platform:
   - `async_setup_entry`: Loads YAML config, creates entities from config
   - Platform-specific entity class inherits from `ChargerPlatformEntity`
   - Implements required properties/methods for the platform type

### Entity Configuration System

Entities are defined in YAML files (`sensor.yaml`, `switch.yaml`, etc.) with this structure:

```yaml
entities:
  - id: property_identifier # Wattpilot property ID
    name: "Display Name" # Entity name
    source: property|attribute # Data source type
    firmware: ">=1.0.0" # Optional: minimum firmware version
    variant: "Home|Flex" # Optional: supported device variants
    connection: "local|cloud" # Optional: supported connection types
    device_class: ... # Platform-specific attributes
    enabled: true|false # Default enabled state
```

The system supports conditional entity creation based on firmware version, device variant, and connection type.

### Vendored Wattpilot Module

The `custom_components/wattpilot/wattpilot/` directory contains a vendored copy of the `wattpilot` Python module (originally from joscha82/wattpilot). This module handles:

- WebSocket connection management (local and cloud)
- Property parsing and updates
- Charger model and variant detection
- Event handling system

Do not modify files in `custom_components/wattpilot/wattpilot/` - they are excluded from linting, formatting, and testing.

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
- pytest configuration in `pyproject.toml` under `[tool.pytest.ini_options]`
- All code must pass ruff format and ruff check

**Testing**

- Test fixtures in `tests/conftest.py` provide mocked Home Assistant and charger instances
- Use `pytest-homeassistant-custom-component` for Home Assistant test utilities
- Tests are in `tests/` and mirror the structure of `custom_components/wattpilot/`
- Async tests use `pytest-asyncio` with `asyncio_mode = "auto"`

## Important Files

- `manifest.json`: Integration metadata, dependencies, version
- `strings.json`: User-facing text and translations
- `icons.json`: Custom icons for entities
- `quality_scale.yaml`: Home Assistant quality scale compliance checklist
- `services.yaml`: Service definitions for Home Assistant
- Platform YAML files: Entity definitions for each platform
- `.pre-commit-config.yaml`: Pre-commit hooks configuration

## Services

The integration provides custom services defined in `services.py`:

- `wattpilot.set_next_trip`: Configure next trip departure time
- `wattpilot.set_goe_cloud`: Set go-eCharger cloud settings
- `wattpilot.disconnect_charger`: Manually disconnect
- `wattpilot.reconnect_charger`: Manually reconnect
- `wattpilot.set_debug_properties`: Enable debug property logging

Services are registered once globally (not per config entry) and use `async_registerService` helper.

## Common Patterns

**Adding a New Entity**

1. Add entity configuration to the appropriate YAML file (e.g., `sensor.yaml`)
2. If adding a new platform, create corresponding Python file following existing patterns
3. For existing platforms, the entity will be auto-created from YAML config
4. Add tests in `tests/test_<platform>.py`

**Accessing Charger Data**

```python
from .utils import GetChargerProp, async_GetChargerProp

# Sync access (in __init__ or properties)
value = GetChargerProp(self._charger, "property_id", default_value)

# Async access (in async methods)
value = await async_GetChargerProp(self._charger, "property_id", default_value)
```

**Coordinator Usage**

```python
# In entity class
@property
def native_value(self):
    """Return sensor value from coordinator data."""
    if self.coordinator.data is None:
        return self._default_state
    return self.coordinator.data.get(self._identifier, self._default_state)

@property
def available(self) -> bool:
    """Return entity availability based on coordinator."""
    return self.coordinator.available and not self._init_failed
```
