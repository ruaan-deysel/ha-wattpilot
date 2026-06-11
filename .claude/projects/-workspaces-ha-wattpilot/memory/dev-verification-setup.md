---
name: dev-verification-setup
description: How to run and verify the HA dev instance in this devcontainer
metadata:
  type: project
---

`./scripts/develop` starts a real Home Assistant instance on http://localhost:8123 (login `dev`/`dev`). It uses `config/` which already has a configured wattpilot entry pointing at a **live charger reachable from the container** (serial `91003723`, host `192.168.20.25`) — so setup logs show real property updates, not just a mock. Verify changes via the HA log (redirect to a file) and check the entry reaches loaded state.

Known unrelated startup errors in this container (ignore them): `usb`/`bluetooth` (missing `aioesphomeapi`) and `go2rtc` (missing docker binary) — all from `default_config`, not the integration.

Playwright is available for UI checks: `playwright-cli install-browser --with-deps`.
