# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2025-12-08

### Fixed

- **Git-LFS dependency**: Removed Git-LFS configuration and hooks from repository. The repository no longer requires Git-LFS as it's not necessary for Python Home Assistant integration distribution.

### Changed

- Code formatting improvements and style consistency fixes across the codebase

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
