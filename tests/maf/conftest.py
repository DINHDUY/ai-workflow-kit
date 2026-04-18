"""
Shared pytest fixtures for the MAF test suite.

Provides:
  - ``fixtures_dir``          — Path to tests/maf/fixtures/
  - ``tmp_agents_dir``        — Temporary directory populated with sample .md files
  - ``mock_agent_framework``  — Patches agent_framework module with minimal mocks
  - ``mock_agent``            — A mock Agent object
  - ``mock_client``           — A mock AzureOpenAIResponsesClient
  - ``mock_magentic_builder`` — A mock MagenticBuilder
"""
from __future__ import annotations

import shutil
from pathlib import Path
from types import ModuleType
from typing import AsyncIterator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


FIXTURES_DIR = Path(__file__).parent / "fixtures"


# ---------------------------------------------------------------------------
# Directory fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def fixtures_dir() -> Path:
    """Return the path to tests/maf/fixtures/."""
    return FIXTURES_DIR


@pytest.fixture()
def tmp_agents_dir(tmp_path: Path) -> Path:
    """Return a temporary directory populated with the 3 valid sample agents.

    The ``noname.md`` fixture (which has no 'name' field) is intentionally
    excluded so tests that need *only* valid agents get a clean set.
    """
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()
    for name in ("sample.orchestrator.md", "sample.worker.md", "sample.analyzer.md"):
        shutil.copy(FIXTURES_DIR / name, agents_dir / name)
    return agents_dir


@pytest.fixture()
def tmp_agents_dir_with_noname(tmp_path: Path) -> Path:
    """Return a temporary directory including the noname.md file."""
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()
    for name in ("sample.orchestrator.md", "sample.worker.md", "sample.analyzer.md", "noname.md"):
        shutil.copy(FIXTURES_DIR / name, agents_dir / name)
    return agents_dir


# ---------------------------------------------------------------------------
# agent_framework mocks
# ---------------------------------------------------------------------------

class _MockAgent:
    """Minimal stand-in for ``agent_framework.Agent``."""

    def __init__(self, name: str = "mock-agent", **kwargs):
        self.name = name
        self.kwargs = kwargs


class _MockClient:
    """Minimal stand-in for ``AzureOpenAIResponsesClient``."""

    def as_agent(self, name: str, **kwargs) -> _MockAgent:
        return _MockAgent(name=name, **kwargs)


class _MockMagenticBuilder:
    """Minimal stand-in for ``agent_framework.orchestrations.MagenticBuilder``."""

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self._built = False

    def build(self):
        self._built = True
        return self

    async def run(self, task: str, stream: bool = True) -> AsyncIterator:  # noqa: ARG002
        """Yield nothing — tests override this per-scenario."""
        return
        yield  # make it an async generator


def _make_tool_decorator(fn):
    """Passthrough @tool decorator that records the function unchanged."""
    fn._is_tool = True
    return fn


def _build_mock_agent_framework() -> ModuleType:
    """Construct a minimal fake ``agent_framework`` module tree."""
    af = ModuleType("agent_framework")
    af.Agent = _MockAgent
    af.tool = _make_tool_decorator

    # agent_framework.azure submodule
    af_azure = ModuleType("agent_framework.azure")
    af_azure.AzureOpenAIResponsesClient = _MockClient

    # agent_framework.orchestrations submodule
    af_orch = ModuleType("agent_framework.orchestrations")
    af_orch.MagenticBuilder = _MockMagenticBuilder

    return af, af_azure, af_orch


@pytest.fixture()
def mock_agent_framework(monkeypatch):
    """Patch sys.modules so MAF source imports fake agent_framework classes."""
    import sys

    af, af_azure, af_orch = _build_mock_agent_framework()
    monkeypatch.setitem(sys.modules, "agent_framework", af)
    monkeypatch.setitem(sys.modules, "agent_framework.azure", af_azure)
    monkeypatch.setitem(sys.modules, "agent_framework.orchestrations", af_orch)
    yield af


@pytest.fixture()
def mock_client() -> _MockClient:
    return _MockClient()


@pytest.fixture()
def mock_agent() -> _MockAgent:
    return _MockAgent(name="test-agent")
