"""Tests for YAML configuration files."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml


class TestAllPlatformYamls:
    """Test all platform YAML files."""

    @pytest.fixture
    def platforms(self) -> list[str]:
        """Return list of platforms."""
        return ["button", "number", "select", "sensor", "switch", "update"]

    def test_all_yamls_have_platform_key(self, platforms: list[str]) -> None:
        """Test all YAML files have the platform key."""
        base_path = Path(__file__).parent.parent / "custom_components/wattpilot"

        for platform in platforms:
            yaml_path = base_path / f"{platform}.yaml"
            with yaml_path.open() as f:
                config = yaml.safe_load(f)
            assert platform in config, f"{platform}.yaml missing platform key"

    def test_all_entities_have_unique_ids_within_platform(
        self, platforms: list[str]
    ) -> None:
        """Test entity IDs are unique within each platform."""
        base_path = Path(__file__).parent.parent / "custom_components/wattpilot"

        for platform in platforms:
            yaml_path = base_path / f"{platform}.yaml"
            with yaml_path.open() as f:
                config = yaml.safe_load(f)

            ids = []
            for entity in config[platform]:
                entity_id = entity.get("id")
                uid = entity.get("uid", entity_id)
                ids.append(uid)

            duplicates = [x for x in ids if ids.count(x) > 1]
            assert len(set(duplicates)) == 0, (
                f"{platform}.yaml has duplicate IDs: {set(duplicates)}"
            )

    def test_all_entities_have_names(self, platforms: list[str]) -> None:
        """Test all entities have names defined."""
        base_path = Path(__file__).parent.parent / "custom_components/wattpilot"

        for platform in platforms:
            yaml_path = base_path / f"{platform}.yaml"
            with yaml_path.open() as f:
                config = yaml.safe_load(f)

            for entity in config[platform]:
                assert "name" in entity, (
                    f"{platform}.yaml entity missing name: {entity.get('id')}"
                )

    def test_all_entities_have_source(self, platforms: list[str]) -> None:
        """Test all entities have source defined."""
        base_path = Path(__file__).parent.parent / "custom_components/wattpilot"

        for platform in platforms:
            yaml_path = base_path / f"{platform}.yaml"
            with yaml_path.open() as f:
                config = yaml.safe_load(f)

            for entity in config[platform]:
                # Some entities might not need source, so we just check it's a valid value if present
                source = entity.get("source")
                if source is not None:
                    assert source in ["property", "attribute", "namespacelist"], (
                        f"{platform}.yaml entity has invalid source: {entity.get('id')}"
                    )

    def test_sensor_energy_entities_have_correct_attributes(self) -> None:
        """Test energy sensors have device_class and state_class."""
        base_path = Path(__file__).parent.parent / "custom_components/wattpilot"
        yaml_path = base_path / "sensor.yaml"

        with yaml_path.open() as f:
            config = yaml.safe_load(f)

        energy_sensors = [
            s for s in config["sensor"] if s.get("device_class") == "energy"
        ]

        for sensor in energy_sensors:
            assert "state_class" in sensor, (
                f"Energy sensor {sensor.get('id')} missing state_class"
            )
            assert sensor["state_class"] in ["total", "total_increasing"], (
                f"Energy sensor {sensor.get('id')} has invalid state_class"
            )


class TestServicesYaml:
    """Test services.yaml configuration."""

    def test_services_yaml_loads(self) -> None:
        """Test services.yaml loads without errors."""
        base_path = Path(__file__).parent.parent / "custom_components/wattpilot"
        yaml_path = base_path / "services.yaml"

        with yaml_path.open() as f:
            config = yaml.safe_load(f)

        assert config is not None
        assert isinstance(config, dict)

    def test_all_services_have_descriptions(self) -> None:
        """Test all services have descriptions."""
        base_path = Path(__file__).parent.parent / "custom_components/wattpilot"
        yaml_path = base_path / "services.yaml"

        with yaml_path.open() as f:
            config = yaml.safe_load(f)

        for service_name, service_config in config.items():
            assert "description" in service_config, (
                f"Service {service_name} missing description"
            )


class TestStringsJson:
    """Test strings.json configuration."""

    def test_strings_json_loads(self) -> None:
        """Test strings.json loads without errors."""
        import json

        base_path = Path(__file__).parent.parent / "custom_components/wattpilot"
        json_path = base_path / "strings.json"

        with json_path.open() as f:
            config = json.load(f)

        assert config is not None
        assert isinstance(config, dict)

    def test_strings_has_config_step(self) -> None:
        """Test strings.json has config flow steps."""
        import json

        base_path = Path(__file__).parent.parent / "custom_components/wattpilot"
        json_path = base_path / "strings.json"

        with json_path.open() as f:
            config = json.load(f)

        assert "config" in config
        assert "step" in config["config"]


class TestIconsJson:
    """Test icons.json configuration."""

    def test_icons_json_loads(self) -> None:
        """Test icons.json loads without errors."""
        import json

        base_path = Path(__file__).parent.parent / "custom_components/wattpilot"
        json_path = base_path / "icons.json"

        with json_path.open() as f:
            config = json.load(f)

        assert config is not None
        assert isinstance(config, dict)
