"""Tests for maf.simulator — MockWorkflow, SCENARIOS, and Simulator."""
from __future__ import annotations

import pytest

from maf.simulator import (
    SCENARIOS,
    MockEvent,
    MockEventData,
    MockWorkflow,
    Simulator,
    _RAW_SCENARIOS,
)


# ---------------------------------------------------------------------------
# SCENARIOS / _RAW_SCENARIOS
# ---------------------------------------------------------------------------

class TestScenarios:
    def test_all_four_scenarios_exist(self):
        assert set(SCENARIOS.keys()) == {"happy_path", "error_recovery", "multi_turn", "stall_then_complete"}

    def test_scenarios_match_raw(self):
        for name, events in SCENARIOS.items():
            assert len(events) == len(_RAW_SCENARIOS[name])

    def test_scenario_items_are_mock_events(self):
        for scenario, events in SCENARIOS.items():
            for event in events:
                assert isinstance(event, MockEvent)
                assert isinstance(event.data, MockEventData)

    def test_happy_path_ends_with_completed(self):
        assert SCENARIOS["happy_path"][-1].type == "completed"

    def test_error_recovery_has_error_event(self):
        types = [e.type for e in SCENARIOS["error_recovery"]]
        assert "error" in types

    def test_stall_scenario_has_stall_event(self):
        types = [e.type for e in SCENARIOS["stall_then_complete"]]
        assert "stall" in types

    def test_multi_turn_has_multiple_agent_selected(self):
        types = [e.type for e in SCENARIOS["multi_turn"]]
        assert types.count("agent_selected") > 1


# ---------------------------------------------------------------------------
# MockWorkflow
# ---------------------------------------------------------------------------

class TestMockWorkflow:
    def test_valid_scenario_creates_instance(self):
        wf = MockWorkflow("happy_path")
        assert wf is not None

    def test_unknown_scenario_raises_key_error(self):
        with pytest.raises(KeyError, match="Unknown scenario"):
            MockWorkflow("does_not_exist")

    @pytest.mark.asyncio
    async def test_yields_all_events(self):
        wf = MockWorkflow("happy_path", delay=0)
        events = [e async for e in wf.run("test task")]
        assert len(events) == len(SCENARIOS["happy_path"])

    @pytest.mark.asyncio
    async def test_yields_mock_event_objects(self):
        wf = MockWorkflow("happy_path", delay=0)
        events = [e async for e in wf.run("test task")]
        for event in events:
            assert isinstance(event, MockEvent)

    @pytest.mark.asyncio
    async def test_all_scenarios_run_to_completion(self):
        for name in SCENARIOS:
            wf = MockWorkflow(name, delay=0)
            events = [e async for e in wf.run("task")]
            assert len(events) > 0

    @pytest.mark.asyncio
    async def test_stream_false_still_yields_events(self):
        wf = MockWorkflow("happy_path", delay=0)
        events = [e async for e in wf.run("task", stream=False)]
        assert len(events) == len(SCENARIOS["happy_path"])

    @pytest.mark.asyncio
    async def test_zero_delay_runs_fast(self):
        """Zero delay should not sleep between events."""
        import time
        wf = MockWorkflow("happy_path", delay=0)
        start = time.monotonic()
        _ = [e async for e in wf.run("task")]
        elapsed = time.monotonic() - start
        # Should complete in << 1 second with no delay
        assert elapsed < 1.0


# ---------------------------------------------------------------------------
# Simulator
# ---------------------------------------------------------------------------

class TestSimulator:
    @pytest.mark.asyncio
    async def test_happy_path_returns_string(self):
        sim = Simulator(scenario="happy_path", delay=0, stream=False)
        result = await sim.run_simulation("test task")
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_happy_path_output_content(self):
        sim = Simulator(scenario="happy_path", delay=0, stream=False)
        result = await sim.run_simulation("test task")
        assert "Workflow finished" in result

    @pytest.mark.asyncio
    async def test_all_scenarios_complete(self):
        for name in SCENARIOS:
            sim = Simulator(scenario=name, delay=0, stream=False)
            result = await sim.run_simulation("test task")
            assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_stream_true_prints_output(self, capsys):
        sim = Simulator(scenario="happy_path", delay=0, stream=True)
        await sim.run_simulation("test task")
        captured = capsys.readouterr()
        assert len(captured.out) > 0

    @pytest.mark.asyncio
    async def test_stream_false_no_print(self, capsys):
        sim = Simulator(scenario="happy_path", delay=0, stream=False)
        await sim.run_simulation("test task")
        captured = capsys.readouterr()
        assert captured.out == ""

    @pytest.mark.asyncio
    async def test_verbose_mode_accepted(self):
        sim = Simulator(scenario="happy_path", delay=0, stream=False, verbose=True)
        result = await sim.run_simulation("test task")
        assert isinstance(result, str)

    def test_unknown_scenario_raises(self):
        with pytest.raises(KeyError):
            Simulator(scenario="not_a_scenario")

    @pytest.mark.asyncio
    async def test_nonzero_delay_sleeps(self):
        """MockWorkflow with delay > 0 hits the asyncio.sleep branch (simulator.py:160)."""
        import asyncio
        from unittest.mock import AsyncMock, patch

        wf = MockWorkflow("happy_path", delay=0.001)
        sleep_calls = []

        original_sleep = asyncio.sleep

        async def _track_sleep(t):
            sleep_calls.append(t)
            # don't actually sleep in tests
            return

        with patch("maf.simulator.asyncio.sleep", side_effect=_track_sleep):
            events = [e async for e in wf.run("task")]

        assert len(sleep_calls) == len(SCENARIOS["happy_path"])
        assert all(s == 0.001 for s in sleep_calls)
