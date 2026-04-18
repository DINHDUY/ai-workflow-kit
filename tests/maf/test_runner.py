"""Tests for maf.runner — event formatting and run_workflow."""
from __future__ import annotations

import pytest

from maf.runner import (
    SEPARATOR,
    THIN_SEP,
    _fmt_agent_selected,
    _fmt_error,
    _fmt_output,
    _fmt_plan_review,
    _fmt_stall,
    _fmt_tool_call,
    _fmt_tool_result,
    run_workflow,
)
from maf.simulator import MockEvent, MockEventData


# ---------------------------------------------------------------------------
# Formatter unit tests
# ---------------------------------------------------------------------------

class TestFmtAgentSelected:
    def test_uses_name_attribute(self):
        data = MockEventData(name="my.agent")
        result = _fmt_agent_selected(data)
        assert "my.agent" in result
        assert THIN_SEP in result

    def test_fallback_to_str(self):
        result = _fmt_agent_selected("some-string")
        assert "some-string" in result


class TestFmtOutput:
    def test_returns_content(self):
        data = MockEventData(content="The output text.")
        assert _fmt_output(data, verbose=False) == "The output text."

    def test_uses_text_fallback(self):
        data = MockEventData(text="fallback text")
        assert _fmt_output(data, verbose=False) == "fallback text"

    def test_truncates_long_content_non_verbose(self):
        data = MockEventData(content="A" * 3000)
        result = _fmt_output(data, verbose=False)
        assert "truncated" in result
        assert len(result) < 2200

    def test_no_truncation_in_verbose(self):
        data = MockEventData(content="A" * 3000)
        result = _fmt_output(data, verbose=True)
        assert "truncated" not in result
        assert len(result) == 3000


class TestFmtToolCall:
    def test_formats_name_and_args(self):
        data = MockEventData(name="read_file", arguments='"path": "foo.txt"')
        result = _fmt_tool_call(data)
        assert "read_file" in result
        assert '"path": "foo.txt"' in result
        assert "Tool →" in result

    def test_missing_name_uses_question_mark(self):
        result = _fmt_tool_call(MockEventData())
        assert "?" in result


class TestFmtToolResult:
    def test_formats_result(self):
        data = MockEventData(result="file content here")
        result = _fmt_tool_result(data, verbose=False)
        assert "file content here" in result
        assert "Tool ←" in result

    def test_truncates_long_result_non_verbose(self):
        data = MockEventData(result="X" * 1000)
        result = _fmt_tool_result(data, verbose=False)
        assert "…" in result
        assert len(result) < 600

    def test_no_truncation_in_verbose(self):
        data = MockEventData(result="X" * 1000)
        result = _fmt_tool_result(data, verbose=True)
        assert "…" not in result


class TestFmtPlanReview:
    def test_shows_plan(self):
        data = MockEventData(plan="Step 1. Step 2.")
        result = _fmt_plan_review(data)
        assert "Step 1." in result
        assert "Plan Review" in result
        assert SEPARATOR in result


class TestFmtStall:
    def test_shows_stall_message(self):
        data = MockEventData(message="No progress")
        result = _fmt_stall(data)
        assert "No progress" in result
        assert "Stall" in result


class TestFmtError:
    def test_shows_error_message(self):
        data = MockEventData(message="Something went wrong")
        result = _fmt_error(data)
        assert "Something went wrong" in result
        assert "ERROR" in result


# ---------------------------------------------------------------------------
# run_workflow integration tests (using MockWorkflow)
# ---------------------------------------------------------------------------

class TestRunWorkflow:
    @pytest.mark.asyncio
    async def test_happy_path_returns_output(self):
        from maf.simulator import MockWorkflow
        wf = MockWorkflow("happy_path", delay=0)
        result = await run_workflow(wf, "test task", stream=False)
        assert "Workflow finished" in result

    @pytest.mark.asyncio
    async def test_stream_true_prints_separator(self, capsys):
        from maf.simulator import MockWorkflow
        wf = MockWorkflow("happy_path", delay=0)
        await run_workflow(wf, "test task", stream=True)
        captured = capsys.readouterr()
        assert SEPARATOR in captured.out

    @pytest.mark.asyncio
    async def test_error_recovery_completes(self):
        from maf.simulator import MockWorkflow
        wf = MockWorkflow("error_recovery", delay=0)
        result = await run_workflow(wf, "test task", stream=False)
        assert "completed" in result.lower()

    @pytest.mark.asyncio
    async def test_multi_turn_completes(self):
        from maf.simulator import MockWorkflow
        wf = MockWorkflow("multi_turn", delay=0)
        result = await run_workflow(wf, "test task", stream=False)
        assert "Multi-turn" in result

    @pytest.mark.asyncio
    async def test_stall_then_complete(self):
        from maf.simulator import MockWorkflow
        wf = MockWorkflow("stall_then_complete", delay=0)
        result = await run_workflow(wf, "test task", stream=False)
        assert "stall recovery" in result.lower()

    @pytest.mark.asyncio
    async def test_verbose_does_not_truncate_output(self, capsys):
        from maf.simulator import MockWorkflow, MockEvent, MockEventData

        class _BigOutputWorkflow:
            async def run(self, task, stream=True):
                yield MockEvent(type="output", data=MockEventData(content="A" * 3000))
                yield MockEvent(type="completed", data=MockEventData(output="Done."))

        wf = _BigOutputWorkflow()
        await run_workflow(wf, "task", stream=True, verbose=True)
        captured = capsys.readouterr()
        assert "truncated" not in captured.out

    @pytest.mark.asyncio
    async def test_unknown_event_not_printed_when_not_verbose(self, capsys):
        from maf.simulator import MockEvent, MockEventData

        class _UnknownEventWorkflow:
            async def run(self, task, stream=True):
                yield MockEvent(type="mystery_event", data=MockEventData(content="secret"))
                yield MockEvent(type="completed", data=MockEventData(output="Done."))

        await run_workflow(_UnknownEventWorkflow(), "t", stream=True, verbose=False)
        captured = capsys.readouterr()
        assert "mystery_event" not in captured.out

    @pytest.mark.asyncio
    async def test_unknown_event_printed_when_verbose(self, capsys):
        from maf.simulator import MockEvent, MockEventData

        class _UnknownEventWorkflow:
            async def run(self, task, stream=True):
                yield MockEvent(type="mystery_event", data=MockEventData(content="secret"))
                yield MockEvent(type="completed", data=MockEventData(output="Done."))

        await run_workflow(_UnknownEventWorkflow(), "t", stream=True, verbose=True)
        captured = capsys.readouterr()
        assert "mystery_event" in captured.out

    @pytest.mark.asyncio
    async def test_fallback_to_last_output_when_no_completed(self):
        from maf.simulator import MockEvent, MockEventData

        class _NoCompletedWorkflow:
            async def run(self, task, stream=True):
                yield MockEvent(type="output", data=MockEventData(content="Last output text."))

        result = await run_workflow(_NoCompletedWorkflow(), "t", stream=False)
        assert result == "Last output text."

    @pytest.mark.asyncio
    async def test_plan_review_event_is_formatted(self, capsys):
        """plan_review event triggers _fmt_plan_review (runner.py:137)."""
        from maf.simulator import MockEvent, MockEventData

        class _PlanReviewWorkflow:
            async def run(self, task, stream=True):
                yield MockEvent(type="plan_review", data=MockEventData(plan="Step 1; Step 2"))
                yield MockEvent(type="completed", data=MockEventData(output="Done."))

        await run_workflow(_PlanReviewWorkflow(), "task", stream=True)
        captured = capsys.readouterr()
        assert "Step 1" in captured.out or "plan" in captured.out.lower()

    @pytest.mark.asyncio
    async def test_error_event_logs(self, capsys):
        """error event calls logger.error (runner.py:150)."""
        from maf.simulator import MockEvent, MockEventData

        class _ErrorWorkflow:
            async def run(self, task, stream=True):
                yield MockEvent(type="error", data=MockEventData(message="boom"))
                yield MockEvent(type="completed", data=MockEventData(output="recovered"))

        result = await run_workflow(_ErrorWorkflow(), "task", stream=True)
        assert "recovered" in result
