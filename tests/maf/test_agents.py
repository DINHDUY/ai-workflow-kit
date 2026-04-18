"""Tests for maf.agents — Agent construction and instruction helpers."""
from __future__ import annotations

import logging
import sys
from types import ModuleType
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Stubs — must be registered BEFORE importing maf.agents
# ---------------------------------------------------------------------------

def _stub_agent_framework(monkeypatch):
    """Register lightweight stubs for agent_framework and azure.identity."""
    # agent_framework
    af = ModuleType("agent_framework")

    class _Agent:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    af.Agent = _Agent
    af.tool = lambda fn: fn
    monkeypatch.setitem(sys.modules, "agent_framework", af)

    # agent_framework.azure
    af_azure = ModuleType("agent_framework.azure")

    class _Client:
        def __init__(self, *args, **kwargs):
            pass

        def as_agent(self, name, **kwargs):
            return _Agent(name=name, **kwargs)

    af_azure.AzureOpenAIResponsesClient = _Client
    monkeypatch.setitem(sys.modules, "agent_framework.azure", af_azure)

    # agent_framework.orchestrations
    af_orch = ModuleType("agent_framework.orchestrations")
    af_orch.MagenticBuilder = MagicMock()
    monkeypatch.setitem(sys.modules, "agent_framework.orchestrations", af_orch)

    # azure.identity
    az = ModuleType("azure")
    az_id = ModuleType("azure.identity")
    az_id.AzureCliCredential = MagicMock(return_value="cli-cred")
    az_id.DefaultAzureCredential = MagicMock(return_value="default-cred")
    monkeypatch.setitem(sys.modules, "azure", az)
    monkeypatch.setitem(sys.modules, "azure.identity", az_id)

    return _Agent, _Client


@pytest.fixture(autouse=True)
def _setup(monkeypatch):
    _stub_agent_framework(monkeypatch)
    # Ensure maf.client is fresh so it picks up the stubs
    for mod in ("maf.client", "maf.agents", "maf.tools"):
        monkeypatch.delitem(sys.modules, mod, raising=False)
    # Set required env vars
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://test.openai.azure.com/")
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "test-key")
    yield


# ---------------------------------------------------------------------------
# get_deployment
# ---------------------------------------------------------------------------

class TestGetDeployment:
    def test_none_returns_default(self, monkeypatch):
        monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "my-gpt4")
        from maf.agents import get_deployment
        assert get_deployment(None) == "my-gpt4"

    def test_sonnet_returns_deployment(self, monkeypatch):
        monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-premium")
        from maf.agents import get_deployment
        assert get_deployment("sonnet") == "gpt-4o-premium"

    def test_opus_returns_deployment(self, monkeypatch):
        monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-premium")
        from maf.agents import get_deployment
        assert get_deployment("opus") == "gpt-4o-premium"

    def test_haiku_returns_fast_deployment(self, monkeypatch):
        monkeypatch.setenv("AZURE_OPENAI_FAST_DEPLOYMENT", "gpt-4o-mini-test")
        from maf.agents import get_deployment
        assert get_deployment("haiku") == "gpt-4o-mini-test"

    def test_fast_returns_fast_deployment(self, monkeypatch):
        monkeypatch.setenv("AZURE_OPENAI_FAST_DEPLOYMENT", "my-mini")
        from maf.agents import get_deployment
        assert get_deployment("fast") == "my-mini"

    def test_default_returns_deployment(self, monkeypatch):
        monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
        from maf.agents import get_deployment
        assert get_deployment("default") == "gpt-4o"

    def test_unknown_model_falls_back_to_default(self, monkeypatch):
        monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
        from maf.agents import get_deployment
        assert get_deployment("unknown-model") == "gpt-4o"

    def test_env_var_defaults(self, monkeypatch):
        monkeypatch.delenv("AZURE_OPENAI_DEPLOYMENT", raising=False)
        monkeypatch.delenv("AZURE_OPENAI_FAST_DEPLOYMENT", raising=False)
        from maf.agents import get_deployment
        assert get_deployment(None) == "gpt-4o"
        assert get_deployment("haiku") == "gpt-4o-mini"


# ---------------------------------------------------------------------------
# build_instructions
# ---------------------------------------------------------------------------

class TestBuildInstructions:
    def _agent_data(self, description="An agent.", instructions="Do something useful."):
        return {"name": "test.agent", "description": description, "instructions": instructions}

    def test_includes_description(self):
        from maf.agents import build_instructions
        data = self._agent_data()
        result = build_instructions(data, global_instructions=None)
        assert "An agent." in result

    def test_no_description_prefix(self):
        from maf.agents import build_instructions
        data = self._agent_data()
        result = build_instructions(data, global_instructions=None, prefix_description=False)
        assert "# Role" not in result

    def test_includes_global_instructions(self):
        from maf.agents import build_instructions
        data = self._agent_data()
        result = build_instructions(data, global_instructions="Global rule 1.")
        assert "Global rule 1." in result
        assert "Global Context" in result

    def test_no_global_instructions_skips_section(self):
        from maf.agents import build_instructions
        data = self._agent_data()
        result = build_instructions(data, global_instructions=None)
        assert "Global Context" not in result

    def test_empty_description_skipped(self):
        from maf.agents import build_instructions
        data = self._agent_data(description="")
        result = build_instructions(data, global_instructions=None)
        assert "# Role" not in result

    def test_instructions_always_present(self):
        from maf.agents import build_instructions
        data = self._agent_data(instructions="Core instructions here.")
        result = build_instructions(data, global_instructions="G")
        assert "Core instructions here." in result


# ---------------------------------------------------------------------------
# _validate_instructions
# ---------------------------------------------------------------------------

class TestValidateInstructions:
    def test_valid_instructions_returns_true(self, caplog):
        from maf.agents import _validate_instructions
        valid = "A" * 100
        with caplog.at_level(logging.WARNING, logger="maf.agents"):
            assert _validate_instructions("test.agent", valid) is True
        assert caplog.records == []

    def test_short_instructions_warns_and_returns_false(self, caplog):
        from maf.agents import _validate_instructions
        short = "Too short"
        with caplog.at_level(logging.WARNING, logger="maf.agents"):
            assert _validate_instructions("test.agent", short) is False
        assert any("very short" in r.message for r in caplog.records)

    def test_long_instructions_warns_and_returns_true(self, caplog):
        from maf.agents import _validate_instructions
        long = "A" * 100_001
        with caplog.at_level(logging.WARNING, logger="maf.agents"):
            result = _validate_instructions("test.agent", long)
        assert result is True
        assert any("very long" in r.message for r in caplog.records)


# ---------------------------------------------------------------------------
# create_ms_agent
# ---------------------------------------------------------------------------

class TestCreateMsAgent:
    def test_returns_agent_object(self):
        from maf.agents import create_ms_agent
        data = {
            "name": "sample.worker",
            "description": "A worker agent.",
            "instructions": "Do your work carefully. " * 5,
            "tools": [],
            "model": "default",
        }
        agent = create_ms_agent(data)
        # Should be the _Agent stub from as_agent()
        assert agent is not None

    def test_agent_has_correct_name(self):
        from maf.agents import create_ms_agent
        data = {
            "name": "my.special.agent",
            "description": "Desc.",
            "instructions": "Instructions. " * 5,
            "tools": [],
            "model": None,
        }
        agent = create_ms_agent(data)
        assert agent.kwargs.get("name") == "my.special.agent"

    def test_global_instructions_injected(self):
        from maf.agents import create_ms_agent
        data = {
            "name": "agent",
            "description": "D",
            "instructions": "Body instructions. " * 5,
            "tools": [],
            "model": None,
        }
        agent = create_ms_agent(data, global_instructions="Global rule.")
        instructions = agent.kwargs.get("instructions", "")
        assert "Global rule." in instructions


# ---------------------------------------------------------------------------
# build_ms_agents
# ---------------------------------------------------------------------------

class TestBuildMsAgents:
    def test_builds_agents_from_dir(self, tmp_agents_dir):
        from maf.agents import build_ms_agents
        agents = build_ms_agents(str(tmp_agents_dir))
        assert len(agents) == 3
        assert "sample.orchestrator" in agents
        assert "sample.worker" in agents
        assert "sample.analyzer" in agents

    def test_raises_when_no_dir_and_no_candidates(self, monkeypatch, tmp_path):
        # Ensure no default candidate dirs exist
        from pathlib import Path
        monkeypatch.chdir(tmp_path)
        from maf.agents import build_ms_agents
        with pytest.raises(FileNotFoundError):
            build_ms_agents(agents_dir=None)

    def test_auto_detects_cursor_dir(self, tmp_path, monkeypatch):
        from pathlib import Path
        monkeypatch.chdir(tmp_path)
        agents_dir = tmp_path / ".cursor" / "agents"
        agents_dir.mkdir(parents=True)
        (agents_dir / "a.md").write_text(
            "---\nname: auto.agent\ndescription: d\ntools: []\n---\n" + "X" * 60,
            encoding="utf-8",
        )
        from maf.agents import build_ms_agents
        agents = build_ms_agents()
        assert "auto.agent" in agents
