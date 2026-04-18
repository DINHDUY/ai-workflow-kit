"""Tests for maf.config — Settings loading and cache management."""
from __future__ import annotations

import pytest

from maf.config import Settings, clear_settings_cache, get_settings


class TestSettings:
    """Unit tests for the Settings pydantic model."""

    def test_defaults(self, monkeypatch):
        """All optional fields have sensible defaults when env vars are absent."""
        # Remove any ambient vars that might leak from the test environment
        for var in (
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_DEPLOYMENT",
            "AZURE_OPENAI_FAST_DEPLOYMENT",
            "AZURE_OPENAI_API_VERSION",
            "AZURE_OPENAI_API_KEY",
            "USE_MANAGED_IDENTITY",
            "MAX_ROUND_COUNT",
            "MAX_STALL_COUNT",
            "INTERMEDIATE_OUTPUTS",
            "ENABLE_PLAN_REVIEW",
        ):
            monkeypatch.delenv(var, raising=False)

        s = Settings()
        assert s.azure_openai_endpoint == ""
        assert s.azure_openai_deployment == "gpt-4o"
        assert s.azure_openai_fast_deployment == "gpt-4o-mini"
        assert s.azure_openai_api_version == "2025-01-01-preview"
        assert s.azure_openai_api_key is None
        assert s.use_managed_identity is False
        assert s.max_round_count == 30
        assert s.max_stall_count == 5
        assert s.intermediate_outputs is True
        assert s.enable_plan_review is False

    def test_env_override(self, monkeypatch):
        """Environment variables override defaults."""
        monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://my.openai.azure.com/")
        monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "my-deployment")
        monkeypatch.setenv("AZURE_OPENAI_FAST_DEPLOYMENT", "my-fast-deployment")
        monkeypatch.setenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
        monkeypatch.setenv("AZURE_OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("USE_MANAGED_IDENTITY", "true")
        monkeypatch.setenv("MAX_ROUND_COUNT", "10")
        monkeypatch.setenv("MAX_STALL_COUNT", "3")
        monkeypatch.setenv("INTERMEDIATE_OUTPUTS", "false")
        monkeypatch.setenv("ENABLE_PLAN_REVIEW", "true")

        s = Settings()
        assert s.azure_openai_endpoint == "https://my.openai.azure.com/"
        assert s.azure_openai_deployment == "my-deployment"
        assert s.azure_openai_fast_deployment == "my-fast-deployment"
        assert s.azure_openai_api_version == "2024-12-01-preview"
        assert s.azure_openai_api_key == "sk-test-key"
        assert s.use_managed_identity is True
        assert s.max_round_count == 10
        assert s.max_stall_count == 3
        assert s.intermediate_outputs is False
        assert s.enable_plan_review is True

    def test_extra_env_ignored(self, monkeypatch):
        """Unknown environment variables do not raise an error (extra='ignore')."""
        monkeypatch.setenv("TOTALLY_UNKNOWN_VAR", "should-be-ignored")
        s = Settings()  # should not raise
        assert not hasattr(s, "totally_unknown_var")


class TestGetSettings:
    """Unit tests for the get_settings() cached singleton."""

    def setup_method(self):
        clear_settings_cache()

    def teardown_method(self):
        clear_settings_cache()

    def test_returns_settings_instance(self):
        s = get_settings()
        assert isinstance(s, Settings)

    def test_is_cached(self):
        s1 = get_settings()
        s2 = get_settings()
        assert s1 is s2

    def test_clear_cache_reloads(self, monkeypatch):
        """clear_settings_cache() forces re-creation on next call."""
        s1 = get_settings()
        clear_settings_cache()
        monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "fresh-deployment")
        s2 = get_settings()
        assert s1 is not s2
        assert s2.azure_openai_deployment == "fresh-deployment"
