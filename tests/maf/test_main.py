"""Tests for maf.main — CLI entry point."""
from __future__ import annotations

import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Stubs: patch agent_framework before any maf imports touch it
# ---------------------------------------------------------------------------

def _stub_af(monkeypatch):
    af = ModuleType("agent_framework")
    af.Agent = MagicMock
    af.tool = lambda fn: fn
    monkeypatch.setitem(sys.modules, "agent_framework", af)

    af_azure = ModuleType("agent_framework.azure")
    af_azure.AzureOpenAIResponsesClient = MagicMock
    monkeypatch.setitem(sys.modules, "agent_framework.azure", af_azure)

    af_orch = ModuleType("agent_framework.orchestrations")
    af_orch.MagenticBuilder = MagicMock
    monkeypatch.setitem(sys.modules, "agent_framework.orchestrations", af_orch)

    az = ModuleType("azure")
    az_id = ModuleType("azure.identity")
    az_id.AzureCliCredential = MagicMock()
    az_id.DefaultAzureCredential = MagicMock()
    monkeypatch.setitem(sys.modules, "azure", az)
    monkeypatch.setitem(sys.modules, "azure.identity", az_id)


@pytest.fixture(autouse=True)
def _setup(monkeypatch):
    _stub_af(monkeypatch)
    for mod in ("maf.client", "maf.agents", "maf.tools", "maf.workflow", "maf.main"):
        monkeypatch.delitem(sys.modules, mod, raising=False)
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://test.openai.azure.com/")
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "test-key")
    yield


# ---------------------------------------------------------------------------
# _parse_args
# ---------------------------------------------------------------------------

class TestParseArgs:
    def test_inline_task(self):
        from maf.main import _parse_args
        args = _parse_args(["hello world"])
        assert args.task_inline == "hello world"

    def test_task_flag(self, tmp_path):
        from maf.main import _parse_args
        f = tmp_path / "task.txt"
        f.write_text("task content", encoding="utf-8")
        args = _parse_args(["--task", str(f)])
        assert args.task_file == str(f)

    def test_interactive_flag(self):
        from maf.main import _parse_args
        args = _parse_args(["--interactive"])
        assert args.interactive is True

    def test_agents_dir(self):
        from maf.main import _parse_args
        args = _parse_args(["--agents-dir", "workflows/myflow/agents", "task"])
        assert args.agents_dir == "workflows/myflow/agents"

    def test_no_stream_flag(self):
        from maf.main import _parse_args
        args = _parse_args(["--no-stream", "task"])
        assert args.no_stream is True

    def test_verbose_flag(self):
        from maf.main import _parse_args
        args = _parse_args(["-v", "task"])
        assert args.verbose is True

    def test_timeout_default(self):
        from maf.main import _parse_args
        args = _parse_args(["task"])
        assert args.timeout == 600

    def test_timeout_override(self):
        from maf.main import _parse_args
        args = _parse_args(["--timeout", "120", "task"])
        assert args.timeout == 120

    def test_platform_flag(self):
        from maf.main import _parse_args
        args = _parse_args(["--platform", "cursor", "task"])
        assert args.platform == "cursor"

    def test_workflow_name_flag(self):
        from maf.main import _parse_args
        args = _parse_args(["--workflow-name", "myflow", "task"])
        assert args.workflow_name == "myflow"

    def test_global_instructions_flag(self, tmp_path):
        from maf.main import _parse_args
        gi = tmp_path / "gi.md"
        gi.write_text("gi", encoding="utf-8")
        args = _parse_args(["--global-instructions", str(gi), "task"])
        assert args.global_instructions_path == str(gi)


# ---------------------------------------------------------------------------
# _load_workflow
# ---------------------------------------------------------------------------

class TestLoadWorkflow:
    def test_delegates_to_build_workflow(self, monkeypatch):
        """_load_workflow imports and calls build_workflow (main.py:39,41)."""
        from unittest.mock import MagicMock, patch
        import maf.main as main_mod

        fake_wf = MagicMock()

        with patch("maf.workflow.build_workflow", return_value=fake_wf) as mock_bw:
            result = main_mod._load_workflow(
                agents_dir="some/dir",
                platform=None,
                global_instructions_path=None,
            )

        mock_bw.assert_called_once()
        assert result is fake_wf


# ---------------------------------------------------------------------------
# _resolve_task
# ---------------------------------------------------------------------------

class TestResolveTask:
    def _args(self, **overrides):
        from maf.main import _parse_args
        base = _parse_args(["placeholder"])
        # Reset
        base.task_file = None
        base.task_inline = None
        for k, v in overrides.items():
            setattr(base, k, v)
        return base

    def test_reads_from_file(self, tmp_path):
        from maf.main import _resolve_task
        f = tmp_path / "task.txt"
        f.write_text("  file task  ", encoding="utf-8")
        result = _resolve_task(self._args(task_file=str(f)))
        assert result == "file task"

    def test_missing_file_exits(self, tmp_path):
        from maf.main import _resolve_task
        with pytest.raises(SystemExit) as exc_info:
            _resolve_task(self._args(task_file=str(tmp_path / "missing.txt")))
        assert exc_info.value.code == 1

    def test_inline_task(self):
        from maf.main import _resolve_task
        result = _resolve_task(self._args(task_inline="my inline task"))
        assert result == "my inline task"

    def test_empty_input_exits(self, monkeypatch):
        from maf.main import _resolve_task
        monkeypatch.setattr("builtins.input", lambda: "")
        with pytest.raises(SystemExit) as exc_info:
            _resolve_task(self._args())
        assert exc_info.value.code == 1

    def test_interactive_prompt(self, monkeypatch):
        from maf.main import _resolve_task
        responses = iter(["my task text", ""])
        monkeypatch.setattr("builtins.input", lambda: next(responses))
        result = _resolve_task(self._args())
        assert result == "my task text"

    def test_eof_with_content(self, monkeypatch):
        from maf.main import _resolve_task
        first = True

        def _input():
            nonlocal first
            if first:
                first = False
                return "task from eof"
            raise EOFError

        monkeypatch.setattr("builtins.input", _input)
        result = _resolve_task(self._args())
        assert result == "task from eof"


# ---------------------------------------------------------------------------
# main() — full CLI integration
# ---------------------------------------------------------------------------

def _make_fake_workflow():
    """Return a workflow stub whose .run() yields a completed event."""
    from maf.simulator import MockEvent, MockEventData

    class _FakeWorkflow:
        async def run(self, task, stream=True):
            yield MockEvent(type="completed", data=MockEventData(output="All done."))

    return _FakeWorkflow()


class TestMain:
    @pytest.mark.asyncio
    async def test_returns_zero_on_success(self, tmp_agents_dir, monkeypatch):
        import maf.main as main_mod
        monkeypatch.setattr(main_mod, "_load_workflow", lambda *a, **kw: _make_fake_workflow())
        code = await main_mod.main(["--agents-dir", str(tmp_agents_dir), "do something"])
        assert code == 0

    @pytest.mark.asyncio
    async def test_returns_one_on_file_not_found(self, monkeypatch):
        import maf.main as main_mod
        monkeypatch.setattr(
            main_mod,
            "_load_workflow",
            lambda *a, **kw: (_ for _ in ()).throw(FileNotFoundError("no agents")),
        )
        code = await main_mod.main(["some task"])
        assert code == 1

    @pytest.mark.asyncio
    async def test_no_stream_flag(self, tmp_agents_dir, monkeypatch):
        import maf.main as main_mod
        monkeypatch.setattr(main_mod, "_load_workflow", lambda *a, **kw: _make_fake_workflow())
        code = await main_mod.main(
            ["--agents-dir", str(tmp_agents_dir), "--no-stream", "task"]
        )
        assert code == 0

    @pytest.mark.asyncio
    async def test_verbose_flag_accepted(self, tmp_agents_dir, monkeypatch):
        import maf.main as main_mod
        monkeypatch.setattr(main_mod, "_load_workflow", lambda *a, **kw: _make_fake_workflow())
        code = await main_mod.main(
            ["--agents-dir", str(tmp_agents_dir), "-v", "task"]
        )
        assert code == 0

    @pytest.mark.asyncio
    async def test_task_from_file(self, tmp_path, tmp_agents_dir, monkeypatch):
        import maf.main as main_mod
        task_file = tmp_path / "task.txt"
        task_file.write_text("do the work", encoding="utf-8")
        monkeypatch.setattr(main_mod, "_load_workflow", lambda *a, **kw: _make_fake_workflow())
        code = await main_mod.main(
            ["--agents-dir", str(tmp_agents_dir), "--task", str(task_file)]
        )
        assert code == 0

    @pytest.mark.asyncio
    async def test_workflow_name_inferred_from_dir(self, tmp_path, monkeypatch):
        import maf.main as main_mod
        captured: list[str] = []
        original_repl = main_mod._interactive_repl

        async def _fake_repl(wf, workflow_name, stream, verbose):
            captured.append(workflow_name)

        monkeypatch.setattr(main_mod, "_load_workflow", lambda *a, **kw: _make_fake_workflow())
        monkeypatch.setattr(main_mod, "_interactive_repl", _fake_repl)

        agents_dir = tmp_path / "myproject" / "agents"
        agents_dir.mkdir(parents=True)
        await main_mod.main(
            ["--agents-dir", str(agents_dir), "--interactive"]
        )
        assert captured == ["myproject"]

    @pytest.mark.asyncio
    async def test_workflow_name_fallback_when_no_dir(self, monkeypatch):
        import maf.main as main_mod
        captured: list[str] = []

        async def _fake_repl(wf, workflow_name, stream, verbose):
            captured.append(workflow_name)

        monkeypatch.setattr(main_mod, "_load_workflow", lambda *a, **kw: _make_fake_workflow())
        monkeypatch.setattr(main_mod, "_interactive_repl", _fake_repl)

        await main_mod.main(["--interactive"])
        assert captured == ["MAF Workflow"]

    @pytest.mark.asyncio
    async def test_timeout_triggers_returns_one(self, monkeypatch):
        import asyncio
        import maf.main as main_mod

        class _HangingWorkflow:
            async def run(self, task, stream=True):
                await asyncio.sleep(999)
                yield  # never reached

        monkeypatch.setattr(main_mod, "_load_workflow", lambda *a, **kw: _HangingWorkflow())
        code = await main_mod.main(["--timeout", "1", "some task"])
        assert code == 1

    @pytest.mark.asyncio
    async def test_interactive_exits_on_quit(self, monkeypatch):
        import maf.main as main_mod
        monkeypatch.setattr(main_mod, "_load_workflow", lambda *a, **kw: _make_fake_workflow())
        monkeypatch.setattr("builtins.input", lambda *a: "quit")
        code = await main_mod.main(["--interactive"])
        assert code == 0

    @pytest.mark.asyncio
    async def test_interactive_exits_on_eof(self, monkeypatch):
        import maf.main as main_mod
        monkeypatch.setattr(main_mod, "_load_workflow", lambda *a, **kw: _make_fake_workflow())
        monkeypatch.setattr("builtins.input", lambda *a: (_ for _ in ()).throw(EOFError()))
        code = await main_mod.main(["--interactive"])
        assert code == 0

    @pytest.mark.asyncio
    async def test_interactive_empty_input_is_skipped(self, monkeypatch):
        """Empty task input triggers continue (main.py:193), not run_workflow."""
        import maf.main as main_mod
        responses = iter(["", "quit"])
        monkeypatch.setattr(main_mod, "_load_workflow", lambda *a, **kw: _make_fake_workflow())
        monkeypatch.setattr("builtins.input", lambda *a: next(responses))
        code = await main_mod.main(["--interactive"])
        assert code == 0

    @pytest.mark.asyncio
    async def test_interactive_valid_task_runs_workflow(self, monkeypatch):
        """Valid task input calls run_workflow (main.py:197)."""
        import maf.main as main_mod
        run_calls: list[str] = []
        responses = iter(["do something useful", "exit"])
        monkeypatch.setattr(main_mod, "_load_workflow", lambda *a, **kw: _make_fake_workflow())
        monkeypatch.setattr("builtins.input", lambda *a: next(responses))

        import maf.runner as runner_mod
        original_run = runner_mod.run_workflow

        async def _capture_run(workflow, task, stream, verbose):
            run_calls.append(task)
            return await original_run(workflow, task, stream=stream, verbose=verbose)

        monkeypatch.setattr(runner_mod, "run_workflow", _capture_run)
        code = await main_mod.main(["--interactive"])
        assert code == 0
        assert run_calls == ["do something useful"]
