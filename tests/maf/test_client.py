"""Tests for maf.client — AzureOpenAIResponsesClient factory."""
from __future__ import annotations

import sys
from types import ModuleType
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Module-level helpers: build fake azure.identity + agent_framework.azure
# ---------------------------------------------------------------------------

def _patch_azure_deps(monkeypatch):
    """Inject lightweight fakes so client.py can be imported without real Azure SDK."""
    # azure.identity mocks
    mock_az_identity = ModuleType("azure")
    mock_az_identity_sub = ModuleType("azure.identity")
    mock_az_identity_sub.AzureCliCredential = MagicMock(return_value="cli-cred")
    mock_az_identity_sub.DefaultAzureCredential = MagicMock(return_value="default-cred")
    monkeypatch.setitem(sys.modules, "azure", mock_az_identity)
    monkeypatch.setitem(sys.modules, "azure.identity", mock_az_identity_sub)

    # dotenv mock
    mock_dotenv = ModuleType("dotenv")
    mock_dotenv.load_dotenv = lambda: None
    monkeypatch.setitem(sys.modules, "dotenv", mock_dotenv)

    # agent_framework.azure mock
    mock_af_azure = ModuleType("agent_framework.azure")

    class _FakeClient:
        def __init__(self, **kwargs):
            self.init_kwargs = kwargs

    mock_af_azure.AzureOpenAIResponsesClient = _FakeClient
    monkeypatch.setitem(sys.modules, "agent_framework.azure", mock_af_azure)

    # also patch parent agent_framework if not yet present
    if "agent_framework" not in sys.modules:
        monkeypatch.setitem(sys.modules, "agent_framework", ModuleType("agent_framework"))

    return _FakeClient


class TestGetClient:
    """Tests for maf.client.get_client()."""

    def test_raises_when_no_endpoint(self, monkeypatch):
        """EnvironmentError raised if AZURE_OPENAI_ENDPOINT is absent."""
        _patch_azure_deps(monkeypatch)
        monkeypatch.delenv("AZURE_OPENAI_ENDPOINT", raising=False)
        monkeypatch.delenv("AZURE_OPENAI_API_KEY", raising=False)
        monkeypatch.delenv("USE_MANAGED_IDENTITY", raising=False)

        # Force fresh import by removing cached module
        monkeypatch.delitem(sys.modules, "maf.client", raising=False)
        from maf.client import get_client

        with pytest.raises(EnvironmentError, match="AZURE_OPENAI_ENDPOINT"):
            get_client()

    def test_api_key_auth(self, monkeypatch):
        """When AZURE_OPENAI_API_KEY is set, the client is built with api_key."""
        FakeClient = _patch_azure_deps(monkeypatch)
        monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://test.openai.azure.com/")
        monkeypatch.setenv("AZURE_OPENAI_API_KEY", "test-key-123")
        monkeypatch.delenv("USE_MANAGED_IDENTITY", raising=False)

        monkeypatch.delitem(sys.modules, "maf.client", raising=False)
        from maf.client import get_client

        client = get_client()
        assert isinstance(client, FakeClient)
        assert client.init_kwargs["api_key"] == "test-key-123"
        assert client.init_kwargs["endpoint"] == "https://test.openai.azure.com/"

    def test_azure_cli_credential(self, monkeypatch):
        """When no API key and use_managed_identity=False, uses AzureCliCredential."""
        _patch_azure_deps(monkeypatch)
        monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://test.openai.azure.com/")
        monkeypatch.delenv("AZURE_OPENAI_API_KEY", raising=False)
        monkeypatch.setenv("USE_MANAGED_IDENTITY", "false")

        monkeypatch.delitem(sys.modules, "maf.client", raising=False)
        from maf.client import get_client

        client = get_client(use_managed_identity=False)
        # credential should be the return value of AzureCliCredential()
        assert client.init_kwargs["credential"] == "cli-cred"

    def test_default_azure_credential(self, monkeypatch):
        """When use_managed_identity=True, uses DefaultAzureCredential."""
        _patch_azure_deps(monkeypatch)
        monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://test.openai.azure.com/")
        monkeypatch.delenv("AZURE_OPENAI_API_KEY", raising=False)

        monkeypatch.delitem(sys.modules, "maf.client", raising=False)
        from maf.client import get_client

        client = get_client(use_managed_identity=True)
        assert client.init_kwargs["credential"] == "default-cred"

    def test_managed_identity_from_env(self, monkeypatch):
        """USE_MANAGED_IDENTITY env var is respected when argument is None."""
        _patch_azure_deps(monkeypatch)
        monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://test.openai.azure.com/")
        monkeypatch.delenv("AZURE_OPENAI_API_KEY", raising=False)
        monkeypatch.setenv("USE_MANAGED_IDENTITY", "true")

        monkeypatch.delitem(sys.modules, "maf.client", raising=False)
        from maf.client import get_client

        client = get_client()  # None → reads env
        assert client.init_kwargs["credential"] == "default-cred"

    def test_deployment_defaults(self, monkeypatch):
        """Default deployment is gpt-4o when env vars are absent."""
        FakeClient = _patch_azure_deps(monkeypatch)
        monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://test.openai.azure.com/")
        monkeypatch.setenv("AZURE_OPENAI_API_KEY", "key")
        monkeypatch.delenv("AZURE_OPENAI_DEPLOYMENT", raising=False)
        monkeypatch.delenv("AZURE_OPENAI_API_VERSION", raising=False)

        monkeypatch.delitem(sys.modules, "maf.client", raising=False)
        from maf.client import get_client

        client = get_client()
        assert client.init_kwargs["deployment"] == "gpt-4o"
        assert client.init_kwargs["api_version"] == "2025-01-01-preview"
