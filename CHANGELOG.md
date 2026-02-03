# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2026-02-03

### Added

- **DataUpdateCoordinator**: Implemented coordinator pattern wrapping WebSocket push-based updates for centralized availability handling and coordinated entity updates
- **CoordinatorEntity Base**: All platform entities now inherit from `CoordinatorEntity` for proper availability management
- **Comprehensive Test Suite**: Added 50 tests including coordinator tests, diagnostics tests, config flow tests, and sensor tests
- **Test Infrastructure**: Created test fixtures with mock charger properties and expected entity states for reliable testing
- **Diagnostics Platform**: Added diagnostics support with sensitive data redaction (passwords, WiFi credentials, serial numbers)
- **Exception Translations**: Added user-friendly exception messages in English and German for charger unavailable, connection failed, and invalid property errors
- **Service Icons**: Added icons for all services (set_next_trip, set_goe_cloud, set_debug_properties, disconnect_charger, reconnect_charger)
- **Type Annotations**: Added `py.typed` marker file for PEP 561 compliance indicating inline type annotations
- **Pre-commit Hooks**: Configured pre-commit with ruff, codespell, yamllint, and prettier for code quality
- **CI/CD Workflow**: Added continuous integration with pytest, coverage reporting, and Codecov integration
- **Energy Dashboard Compatibility**: Fixed `SensorDeviceClass` enum conversion for proper Energy Dashboard integration

### Changed

- **Quality Scale Upgrade**: Integration upgraded from Bronze to Silver tier following Home Assistant quality scale guidelines
- **Entity Base Class**: `ChargerPlatformEntity` now extends `CoordinatorEntity` with coordinator availability checks
- **Runtime Data Structure**: Added `coordinator` field to `WattpilotRuntimeData` for centralized data management
- **Property Update Handler**: Updated to notify coordinator of property changes for coordinated entity updates
- **Sensor Configuration**: Enhanced Energy Dashboard sensor descriptions and updated state classes (`total_increasing` for energy sensors)
- **Test Configuration**: Enhanced pytest configuration with async support and coverage settings
- **Documentation**: Updated README with improved badges and codecov integration

### Fixed

- **Sensor Device Classes**: Fixed device_class string to enum conversion preventing Energy Dashboard recognition
- **Availability Handling**: Entities now properly check coordinator availability before reporting their own status
- **Error Logging**: Improved logging when charger becomes unavailable with translation support

## [0.4.2] - 2025-12-09

### Added

- Thin schema validation for `wattpilot.yaml` on shell startup to fail fast when definitions are malformed.
- MQTT client disconnect handler with retry/backoff in `wattpilotshell`.

### Changed

- `wattpilotshell` now parses boolean env vars (e.g. `WATTPILOT_SPLIT_PROPERTIES`) correctly, replaces `exit()` with typed exceptions, and improves logging setup without overriding existing handlers.
- Resource loading uses `importlib.resources` with a pkgutil fallback; package data now ships `wattpilot/resources/wattpilot.yaml` for pip installs.
- Additional guards around MQTT property set commands and child property resolution to avoid crashes on missing data.

## [0.4.1] - 2025-12-09

### Added

- `quality_scale.yaml` scaffold declaring Bronze rules (runtime_data, unique IDs, entity names, action setup) to align with HA 2025 quality scale guidance.

### Changed

- Services are now registered once globally (guarded in `async_setup`/`async_setup_entry`) to avoid duplicate registrations when multiple chargers exist.
- Changelog and manifest version bumped to 0.4.1.
- Code formatting improvements and style consistency fixes across the codebase

### Fixed

- Entity polling now awaits `async_local_poll` directly (no misuse of `async_create_task`).
- Property update handling refactored to use `entry.runtime_data` exclusively (no `hass.data` dependency), improving push updates and reload resilience.
- Timeout/connection lookups now read from `runtime_data.params`; `carConnected` sensor displays the corrected friendly name.
- **Git-LFS dependency**: Removed Git-LFS configuration and hooks from repository. The repository no longer requires Git-LFS as it's not necessary for Python Home Assistant integration distribution.

## [0.3.9] - 2025-12-01

### Added

- GitHub Actions workflow for automated releases when version is bumped
- GitHub Actions workflow for PR validation (lint, version check, HACS validation)

## [0.3.8] - 2025-12-01

### Fixed

- **Switch entities infinite recursion**: Fixed `RecursionError` caused by `is_on` property calling `self.state` which in turn calls `is_on` in Home Assistant's `SwitchEntity` base class. Switch entities now use `_internal_state` to store state instead of conflicting with `SwitchEntity.state` property.

- **Switch entities failing to initialize**: Fixed "property 'state' of 'ChargerSwitch' object has no setter" error that prevented multiple switch entities (ebe, fap, fre, ful, loe, lse, nmo, pdte, su, tse, upo, wda) from loading.

- **Number entity temperature conversion error**: Fixed `TypeError: can't multiply sequence by non-int of type 'float'` for `ohmpilot_threshold` and similar number entities. Added `native_value` property override to handle list/tuple values from the charger API by extracting the first element and converting to float.

- **PropertyUpdateHandler KeyError**: Fixed `KeyError: 'wattpilot'` spam in logs when property updates arrive before the integration data structure is fully initialized. Now checks if `DOMAIN` exists in `hass.data` before accessing.

### Changed

- `ChargerSwitch` class now overrides `_state_attr` to use `_internal_state` instead of `state`
- `ChargerSwitch.is_on` property now returns `None` for unknown states instead of comparing against `STATE_ON`
- `ChargerNumber` now overrides `native_value` property to handle list/tuple values at the property level
- `PropertyUpdateHandler` now safely checks for domain existence before accessing `hass.data[DOMAIN]`

### Documentation

- Restructured README.md to match standard integration format with clear sections for Features, Installation, Configuration, Entities, Services, Troubleshooting, and Contributing
- Updated info.md (HACS description) to match new README structure
- Added HACS installation badge and repository links
- Fixed typos throughout codebase:
  - `reverese enginered` → `reverse-engineered`
  - `prerequsites` → `prerequisites`
  - `wihtin` → `within`
  - `objec` → `object`
  - `Asnyc` → `Async`
  - `enitity` → `entity`
  - `unitl` → `until`
  - `untest` → `untested`
  - `mutliple wiht` → `multiple with`
  - `photovoltaik` → `photovoltaic`
  - `directy` → `directly`
  - `greate` → `great`
  - `timesamp` → `timestamp`
  - `specific` → `specify`
  - `ressources` → `resources` (folder rename in embedded wattpilot library)

## [0.3.7] - Previous Release

- Initial tracked version
