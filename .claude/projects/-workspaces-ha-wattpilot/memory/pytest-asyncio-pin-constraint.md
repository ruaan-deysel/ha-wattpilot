---
name: pytest-asyncio-pin-constraint
description: pytest-asyncio version is constrained by pytest-homeassistant-custom-component
metadata:
  type: project
---

`pytest-homeassistant-custom-component` pins `pytest-asyncio==1.3.0` (as of pthcc 0.13.334). Do NOT raise the `pytest-asyncio` floor in `pyproject.toml` above what pthcc allows — it makes `uv.lock` unsatisfiable. A merged Dependabot PR did exactly this (bumped to `>=1.4.0`) and silently broke the lock; fixed by reverting to `>=1.3.0`. Dependabot now ignores `pytest-asyncio` in `.github/dependabot.yml` to prevent recurrence. See [[dev-verification-setup]].
