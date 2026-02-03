"""Tests for configuration schema."""

from __future__ import annotations

from unittest.mock import MagicMock

import voluptuous as vol


class TestConnectionSchema:
    """Test connection schema validation."""

    def test_connection_schema_exists(self) -> None:
        """Test that CONNECTION_SCHEMA is defined."""
        from custom_components.wattpilot.configuration_schema import CONNECTION_SCHEMA

        assert CONNECTION_SCHEMA is not None
        assert isinstance(CONNECTION_SCHEMA, vol.Schema)

    def test_local_schema_exists(self) -> None:
        """Test that LOCAL_SCHEMA is defined."""
        from custom_components.wattpilot.configuration_schema import LOCAL_SCHEMA

        assert LOCAL_SCHEMA is not None
        assert isinstance(LOCAL_SCHEMA, vol.Schema)

    def test_cloud_schema_exists(self) -> None:
        """Test that CLOUD_SCHEMA is defined."""
        from custom_components.wattpilot.configuration_schema import CLOUD_SCHEMA

        assert CLOUD_SCHEMA is not None
        assert isinstance(CLOUD_SCHEMA, vol.Schema)


class TestOptionsSchema:
    """Test options schema functions."""

    async def test_get_options_local_schema(self) -> None:
        """Test async_get_OPTIONS_LOCAL_SCHEMA returns valid schema."""
        from custom_components.wattpilot.configuration_schema import (
            async_get_OPTIONS_LOCAL_SCHEMA,
        )

        schema = await async_get_OPTIONS_LOCAL_SCHEMA(MagicMock())
        assert schema is not None
        assert isinstance(schema, vol.Schema)

    async def test_get_options_cloud_schema(self) -> None:
        """Test async_get_OPTIONS_CLOUD_SCHEMA returns valid schema."""
        from custom_components.wattpilot.configuration_schema import (
            async_get_OPTIONS_CLOUD_SCHEMA,
        )

        schema = await async_get_OPTIONS_CLOUD_SCHEMA(MagicMock())
        assert schema is not None
        assert isinstance(schema, vol.Schema)
