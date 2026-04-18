"""Tests for maf.workflow — workflow builder and orchestrator detection."""
from __future__ import annotations

import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock

import pytest


# ---------------------------------------------------------------------------
# Stubs
# ---------------------------------------------------------------------------

def _stub_deps(monkeypatch):
    """Register stubs for agent_framework, azure.identity, and maf.client."""
    af = ModuleType("agent_framework")
    af.Agent = MagicMock
    af.tool = lambda fn: fn
    monkeypatch.setitem(sys.modules, "agent_framework", af)

    af_orch = ModuleType("agent_framework.orchestrations")

    class _Builder:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
            self.built = False

        def build(self):
            self.built = True
            return self

    af_orch.MagenticBuilder = _Builder
    monkeypatch.setitem(sys.modules, "agent_framework.orchestrations", af_orch)

    af_azure = ModuleType("agent_framework.azure")

    class _Client:
        def __init__(self, *args, **kwargs):
            pass

        def as_agent(self, name, **kwargs):
            m = MagicMock()
            m.name = name
            return m

    af_azure.AzureOpenAIResponsesClient = _Client
    monkeypatch.setitem(sys.modules, "agent_framework.azure", af_azure)

    az = ModuleType("azure")
    az_id = ModuleType("azure.identity")
    az_id.AzureCliCredential = MagicMock(return_value="cli-cred")
    az_id.DefaultAzureCredential = MagicMock(return_value="default-cred")
    monkeypatch.setitem(sys.modules, "azure", az)
    monkeypatch.setitem(sys.modules, "azure.identity", az_id)

    return _Builder


@pytest.fixture(autouse=True)
def _setup(monkeypatch):
    _stub_deps(monkeypatch)
    for mod in ("maf.client", "maf.agents", "maf.tools", "maf.workflow"):
        monkeypatch.delitem(sys.modules, mod, raising=False)
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://test.openai.azure.com/")
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "test-key")
    yield


# ---------------------------------------------------------------------------
# find_orchestrator
# ---------------------------------------------------------------------------

class TestFindOrchestrator:
    def _agents(self, names):
        return {n: {"name": n} for n in names}

    def test_exact_workflow_specific(self):
        from maf.workflow import find_orchestrator
        agents = self._agents(["nextjs.orchestrator", "nextjs.worker"])
        assert find_orchestrator(agents, workflow_name="nextjs") == "nextjs.orchestrator"

    def test_any_dot_orchestrator(self):
        from maf.workflow import find_orchestrator
        agents = self._agents(["sample.orchestrator", "sample.worker"])
        assert find_orchestrator(agents) == "sample.orchestrator"

    def test_fuzzy_orchestrator_in_name(self):
        from maf.workflow import find_orchestrator
        agents = self._agents(["main-orchestrator", "worker-agent"])
        result = find_orchestrator(agents)
        assert result == "main-orchestrator"

    def test_returns_none_when_no_orchestrator(self):
        from maf.workflow import find_orchestrator
        agents = self._agents(["worker-a", "worker-b"])
        assert find_orchestrator(agents) is None

    def test_exact_match_takes_precedence(self):
        """Exact workflow-name match wins over *.orchestrator."""
        from maf.workflow import find_orchestrator
        agents = self._agents(["other.orchestrator", "myflow.orchestrator"])
        result = find_orchestrator(agents, workflow_name="myflow")
        assert result == "myflow.orchestrator"

    def test_empty_agents(self):
        from maf.workflow import find_orchestrator
        assert find_orchestrator({}) is None


# ---------------------------------------------------------------------------
# _build_manager_from_data  /  _build_default_manager
# ---------------------------------------------------------------------------

class TestManagerBuilders:
    def _data(self, name="test.orchestrator"):
        return {
            "name": name,
            "description": "Orchestrates things.",
            "instructions": "Orchestrate all the things carefully. " * 3,
            "tools": [],
            "model": "default",
        }

    def test_build_manager_from_data_returns_agent(self):
        from maf.workflow import _build_manager_from_data
        agent = _build_manager_from_data(self._data(), global_instructions=None)
        assert agent is not None

    def test_build_default_manager_no_global(self):
        from maf.workflow import _build_default_manager
        agent = _build_default_manager(global_instructions=None)
        assert agent is not None

    def test_build_default_manager_with_global(self):
        from maf.workflow import _build_default_manager
        agent = _build_default_manager(global_instructions="some global rules")
        assert agent is not None


# ---------------------------------------------------------------------------
# build_workflow
# ---------------------------------------------------------------------------

class TestBuildWorkflow:
    def test_returns_built_workflow(self, tmp_agents_dir):
        from maf.workflow import build_workflow
        workflow = build_workflow(str(tmp_agents_dir))
        # Should be a _Builder instance that has been built
        assert workflow.built is True

    def test_workflow_has_participants(self, tmp_agents_dir):
        from maf.workflow import build_workflow
        workflow = build_workflow(str(tmp_agents_dir))
        # sample.orchestrator acts as manager → 2 participants remain
        assert len(workflow.kwargs["participants"]) == 2

    def test_workflow_name_inferred_from_dir(self, tmp_path):
        agents_dir = tmp_path / "myflow" / "agents"
        agents_dir.mkdir(parents=True)
        (agents_dir / "a.md").write_text(
            "---\nname: myflow.orchestrator\ndescription: d\ntools: []\n---\n" + "X" * 60,
            encoding="utf-8",
        )
        from maf.workflow import build_workflow
        workflow = build_workflow(str(agents_dir))
        assert workflow.built

    def test_explicit_workflow_name(self, tmp_agents_dir):
        from maf.workflow import build_workflow
        workflow = build_workflow(str(tmp_agents_dir), workflow_name="custom")
        assert workflow.built

    def test_no_orchestrator_uses_default_manager(self, tmp_path):
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()
        # Only workers, no orchestrator
        for i in range(2):
            (agents_dir / f"worker{i}.md").write_text(
                f"---\nname: worker{i}\ndescription: d\ntools: []\n---\n" + "X" * 60,
                encoding="utf-8",
            )
        from maf.workflow import build_workflow
        workflow = build_workflow(str(agents_dir))
        assert workflow.built

    def test_custom_max_round_count(self, tmp_agents_dir):
        from maf.workflow import build_workflow
        workflow = build_workflow(str(tmp_agents_dir), max_round_count=10)
        assert workflow.kwargs["max_round_count"] == 10

    def test_custom_max_stall_count(self, tmp_agents_dir):
        from maf.workflow import build_workflow
        workflow = build_workflow(str(tmp_agents_dir), max_stall_count=2)
        assert workflow.kwargs["max_stall_count"] == 2

    def test_intermediate_outputs_false(self, tmp_agents_dir):
        from maf.workflow import build_workflow
        workflow = build_workflow(str(tmp_agents_dir), intermediate_outputs=False)
        assert workflow.kwargs["intermediate_outputs"] is False

    def test_enable_plan_review_true(self, tmp_agents_dir):
        from maf.workflow import build_workflow
        workflow = build_workflow(str(tmp_agents_dir), enable_plan_review=True)
        assert workflow.kwargs["enable_plan_review"] is True

    def test_raises_on_missing_dir(self, tmp_path):
        from maf.workflow import build_workflow
        with pytest.raises(FileNotFoundError):
            build_workflow(str(tmp_path / "no_such"))

    def test_raises_when_no_autodetect(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from maf.workflow import build_workflow
        with pytest.raises(FileNotFoundError):
            build_workflow(agents_dir=None)

    def test_autodetect_cursor_agents(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        agents_dir = tmp_path / ".cursor" / "agents"
        agents_dir.mkdir(parents=True)
        (agents_dir / "a.md").write_text(
            "---\nname: auto.agent\ndescription: d\ntools: []\n---\n" + "X" * 60,
            encoding="utf-8",
        )
        from maf.workflow import build_workflow
        workflow = build_workflow()
        assert workflow.built
