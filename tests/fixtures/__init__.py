"""Test fixtures package for Wattpilot integration tests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

FIXTURES_DIR = Path(__file__).parent


def load_fixture(filename: str) -> dict[str, Any]:
    """
    Load a fixture file from the fixtures directory.

    Args:
        filename: Name of the fixture file (e.g., 'charger_properties.json')

    Returns:
        Parsed JSON data from the fixture file

    """
    fixture_path = FIXTURES_DIR / filename
    with fixture_path.open() as f:
        return json.load(f)


def get_charger_properties() -> dict[str, Any]:
    """
    Get mock charger properties from fixture.

    Returns:
        Dictionary with charger properties

    """
    data = load_fixture("charger_properties.json")
    return {k: v["value"] for k, v in data["properties"].items()}


def get_expected_entity_states() -> dict[str, Any]:
    """
    Get expected entity states from fixture.

    Returns:
        Dictionary with expected entity states by platform

    """
    return load_fixture("expected_entity_states.json")
