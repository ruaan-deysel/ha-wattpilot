"""Tests for the integration setup."""

from __future__ import annotations

from unittest.mock import MagicMock

import yaml


class TestIntegrationSetup:
    """Test integration setup."""

    def test_domain_is_wattpilot(self) -> None:
        """Test the domain constant."""
        from custom_components.wattpilot.const import DOMAIN

        assert DOMAIN == "wattpilot"

    def test_supported_platforms(self) -> None:
        """Test supported platforms are defined."""
        from custom_components.wattpilot.const import SUPPORTED_PLATFORMS

        expected_platforms = [
            "button",
            "number",
            "select",
            "sensor",
            "switch",
            "update",
        ]
        assert sorted(SUPPORTED_PLATFORMS) == sorted(expected_platforms)

    def test_runtime_data_structure(self) -> None:
        """Test runtime data structure."""
        from custom_components.wattpilot.types import WattpilotRuntimeData

        charger = MagicMock()
        coordinator = MagicMock()
        runtime_data = WattpilotRuntimeData(
            charger=charger,
            coordinator=coordinator,
            push_entities={},
            params={"test": "value"},
            debug_properties=False,
        )

        assert runtime_data.charger == charger
        assert runtime_data.coordinator == coordinator
        assert runtime_data.push_entities == {}
        assert runtime_data.params == {"test": "value"}
        assert runtime_data.debug_properties is False


class TestConstants:
    """Test constant values."""

    def test_default_timeout(self) -> None:
        """Test default timeout value."""
        from custom_components.wattpilot.const import DEFAULT_TIMEOUT

        assert DEFAULT_TIMEOUT == 15

    def test_cloud_api_urls(self) -> None:
        """Test cloud API URL constants."""
        from custom_components.wattpilot.const import (
            CLOUD_API_URL_POSTFIX,
            CLOUD_API_URL_PREFIX,
        )

        assert CLOUD_API_URL_PREFIX == "https://"
        assert ".api.v3.go-e.io/api/" in CLOUD_API_URL_POSTFIX

    def test_event_constants(self) -> None:
        """Test event constants."""
        from custom_components.wattpilot.const import EVENT_PROPS, EVENT_PROPS_ID

        assert EVENT_PROPS_ID == "wattpilot_property_message"
        assert isinstance(EVENT_PROPS, list)


class TestManifest:
    """Test manifest configuration."""

    def test_manifest_loads(self) -> None:
        """Test manifest.json loads correctly."""
        import json
        from pathlib import Path

        manifest_path = (
            Path(__file__).parent.parent / "custom_components/wattpilot/manifest.json"
        )
        with manifest_path.open() as f:
            manifest = json.load(f)

        assert manifest["domain"] == "wattpilot"
        assert manifest["name"] == "Fronius Wattpilot"
        assert manifest["config_flow"] is True

    def test_manifest_has_required_fields(self) -> None:
        """Test manifest has all required fields."""
        import json
        from pathlib import Path

        manifest_path = (
            Path(__file__).parent.parent / "custom_components/wattpilot/manifest.json"
        )
        with manifest_path.open() as f:
            manifest = json.load(f)

        required_fields = [
            "domain",
            "name",
            "version",
            "config_flow",
            "documentation",
            "requirements",
        ]
        for field in required_fields:
            assert field in manifest, f"Missing required field: {field}"

    def test_manifest_iot_class(self) -> None:
        """Test manifest has correct IoT class."""
        import json
        from pathlib import Path

        manifest_path = (
            Path(__file__).parent.parent / "custom_components/wattpilot/manifest.json"
        )
        with manifest_path.open() as f:
            manifest = json.load(f)

        # Should be local_push since it uses WebSocket
        assert manifest["iot_class"] == "local_push"


class TestYamlConfigurations:
    """Test YAML configuration files."""

    def test_all_platform_yamls_exist(self) -> None:
        """Test all platform YAML files exist."""
        from pathlib import Path

        from custom_components.wattpilot.const import SUPPORTED_PLATFORMS

        base_path = Path(__file__).parent.parent / "custom_components/wattpilot"

        for platform in SUPPORTED_PLATFORMS:
            yaml_path = base_path / f"{platform}.yaml"
            assert yaml_path.exists(), f"Missing YAML for platform: {platform}"

    def test_all_platform_yamls_valid(self) -> None:
        """Test all platform YAML files are valid."""
        from pathlib import Path

        from custom_components.wattpilot.const import SUPPORTED_PLATFORMS

        base_path = Path(__file__).parent.parent / "custom_components/wattpilot"

        for platform in SUPPORTED_PLATFORMS:
            yaml_path = base_path / f"{platform}.yaml"
            with yaml_path.open() as f:
                config = yaml.safe_load(f)

            assert platform in config, (
                f"Platform '{platform}' not found in {platform}.yaml"
            )
            assert isinstance(config[platform], list), (
                f"Platform config should be a list in {platform}.yaml"
            )
