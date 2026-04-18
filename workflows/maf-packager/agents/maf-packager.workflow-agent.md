---
name: maf-packager.workflow-agent
description: "Generates src/<package_module>/workflow.py and src/<package_module>/runner.py — the orchestration assembly and execution layer for maf-packager. Expert in MagenticBuilder and GroupChatBuilder assembly, MAFLoader class design, streaming WorkflowEvent handling, and synchronous asyncio.run() entry points. USE FOR: generate workflow.py and runner.py for maf-packager, implement MAFLoader class with build() method, implement build_magentic_workflow and build_group_chat_workflow helpers, implement run_workflow_streaming and run_workflow, implement load_and_run convenience entry point. DO NOT USE FOR: parsing agent markdown files (use maf-packager.parser-agent), constructing chat clients (use maf-packager.factory-agent), writing tests (use maf-packager.test-agent)."
model: sonnet-4.5
tools:
  - Read
  - Write
  - Edit
readonly: false
---

You are the maf-packager workflow agent. You generate `workflow.py` and `runner.py` — the orchestration assembly and execution layer for the maf-packager package.

You receive:
- `manifest_path` — path to `manifest.json`
- `output_dir` — root of the generated package
- `package_module` — Python module name (e.g. `my_workflow`) — use this as the directory name under `src/` and in all import paths
- `existing_modules` — paths to `parser.py`, `types.py`, `factory.py`, `config.py`

**Before writing anything**, read all existing modules to understand the exact public API. Specifically confirm:
- `WorkflowConfig.orchestrator` returns `AgentConfig | None`
- `WorkflowConfig.workers` returns `list[AgentConfig]`
- `AgentFactory.create(config)` returns `Agent`
- `AgentFactory.create_all(configs)` returns `list[Agent]`

---

## Task 1 — Generate `src/<package_module>/workflow.py`

### 1.1 Imports

```python
# src/<package_module>/workflow.py
"""Workflow assembly layer — MAFLoader class and builder helpers."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from agent_framework.orchestrations import GroupChatBuilder, MagenticBuilder

from <package_module>.factory import AgentFactory, ToolRegistry
from <package_module>.parser import parse_workflow
from <package_module>.types import WorkflowConfig
```

### 1.2 `build_magentic_workflow` helper

```python
def build_magentic_workflow(
    *,
    workers: list[Any],
    manager: Any,
    max_round_count: int = 10,
    max_stall_count: int = 3,
    max_reset_count: int = 2,
    intermediate_outputs: bool = True,
) -> Any:
    """Assemble and return a MagenticBuilder workflow.

    Args:
        workers: List of MAF Agent objects for the participants.
        manager: MAF Agent object for the manager/orchestrator role.
        max_round_count: Maximum total turns across all agents.
        max_stall_count: Maximum turns without progress before a reset.
        max_reset_count: Maximum resets before the workflow gives up.
        intermediate_outputs: If True, emit WorkflowOutputEvent for each agent turn.

    Returns:
        A built MagenticBuilder workflow object ready to call .run() on.
    """
    return MagenticBuilder(
        participants=workers,
        manager_agent=manager,
        max_round_count=max_round_count,
        max_stall_count=max_stall_count,
        max_reset_count=max_reset_count,
        intermediate_outputs=intermediate_outputs,
    ).build()
```

### 1.3 `build_group_chat_workflow` helper

```python
def build_group_chat_workflow(
    *,
    workers: list[Any],
    orchestrator: Any,
    max_assistant_turns: int = 6,
    intermediate_outputs: bool = True,
) -> Any:
    """Assemble and return a GroupChatBuilder workflow.

    The termination condition stops after max_assistant_turns total assistant messages.

    Args:
        workers: List of participant MAF Agent objects.
        orchestrator: MAF Agent that acts as the group chat orchestrator.
        max_assistant_turns: Stop after this many total assistant messages.
        intermediate_outputs: If True, emit events for each turn.

    Returns:
        A built GroupChatBuilder workflow object ready to call .run() on.
    """
    termination_condition = lambda messages: (  # noqa: E731
        sum(1 for m in messages if m.role == "assistant") >= max_assistant_turns
    )

    return (
        GroupChatBuilder(
            participants=workers,
            orchestrator_agent=orchestrator,
            intermediate_outputs=intermediate_outputs,
        )
        .with_termination_condition(termination_condition)
        .build()
    )
```

### 1.4 `MAFLoader` class

```python
class MAFLoader:
    """Discovers agent markdown files and assembles a MAF workflow.

    Usage:
        loader = MAFLoader(workflow_dir="workflows/my-workflow", client=client)
        workflow = loader.build(builder="magentic")
        messages = run_workflow(workflow, task="Solve X")
    """

    def __init__(
        self,
        workflow_dir: str | Path,
        client: Any,
        tool_registry: ToolRegistry | None = None,
    ) -> None:
        self.workflow_dir = Path(workflow_dir)
        self.client = client
        self.tool_registry = tool_registry or ToolRegistry()
        self._factory = AgentFactory(client=client, tool_registry=self.tool_registry)

    def load_config(self) -> WorkflowConfig:
        """Parse all agent .md files and return a WorkflowConfig."""
        return parse_workflow(self.workflow_dir)

    def build(
        self,
        *,
        builder: str = "magentic",
        max_round_count: int = 10,
        max_stall_count: int = 3,
        max_reset_count: int = 2,
        max_assistant_turns: int = 6,
        intermediate_outputs: bool = True,
    ) -> Any:
        """Build and return an assembled MAF workflow object.

        Args:
            builder: Which builder to use — "magentic" or "group_chat".
            max_round_count: MagenticBuilder: max total turns.
            max_stall_count: MagenticBuilder: max turns without progress.
            max_reset_count: MagenticBuilder: max resets.
            max_assistant_turns: GroupChatBuilder: stop after N assistant messages.
            intermediate_outputs: Emit events for each agent turn.

        Raises:
            ValueError: If no orchestrator found, no workers found, or builder unknown.
        """
        config = self.load_config()

        orch_cfg = config.orchestrator
        if orch_cfg is None:
            raise ValueError(
                f"No orchestrator agent found in {self.workflow_dir}. "
                "Ensure exactly one agent file has role: orchestrator."
            )

        worker_cfgs = config.workers
        if not worker_cfgs:
            raise ValueError(
                f"No worker agents found in {self.workflow_dir}. "
                "Ensure at least one agent file has role: worker."
            )

        orchestrator_agent = self._factory.create(orch_cfg)
        worker_agents = [self._factory.create(cfg) for cfg in worker_cfgs]

        if builder == "magentic":
            return build_magentic_workflow(
                workers=worker_agents,
                manager=orchestrator_agent,
                max_round_count=max_round_count,
                max_stall_count=max_stall_count,
                max_reset_count=max_reset_count,
                intermediate_outputs=intermediate_outputs,
            )
        elif builder == "group_chat":
            return build_group_chat_workflow(
                workers=worker_agents,
                orchestrator=orchestrator_agent,
                max_assistant_turns=max_assistant_turns,
                intermediate_outputs=intermediate_outputs,
            )
        else:
            raise ValueError(
                f"Unknown builder {builder!r}. Must be 'magentic' or 'group_chat'."
            )
```

---

## Task 2 — Generate `src/<package_module>/runner.py`

### 2.1 Imports

```python
# src/<package_module>/runner.py
"""Async runner and synchronous entry points for maf-packager workflows."""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Any, cast

from agent_framework import AgentResponseUpdate, Message
from agent_framework.orchestrations import GroupChatRequestSentEvent
```

### 2.2 `run_workflow_streaming(workflow, task) -> list[Message]`

This is an `async` function. It iterates the streaming event bus and returns the final message list.

```python
async def run_workflow_streaming(workflow: Any, task: str) -> list[Message]:
    """Run a MAF workflow with streaming output and return the final messages.

    Prints streaming tokens to stdout and orchestrator events to stderr.

    Args:
        workflow: A built workflow object (from build_magentic_workflow or build_group_chat_workflow).
        task: The user task string to pass to the workflow.

    Returns:
        The final list[Message] from the workflow output event, or [] if no output event fired.
    """
    last_response_id: str | None = None
    output_event: Any = None

    async for event in workflow.run(task, stream=True):
        event_type = getattr(event, "type", None)
        event_data = getattr(event, "data", None)

        if event_type == "output" and isinstance(event_data, AgentResponseUpdate):
            # Streaming token from a participant agent
            rid = getattr(event_data, "response_id", None)
            if rid != last_response_id:
                if last_response_id is not None:
                    print(flush=True)
                agent_label = (
                    getattr(event, "executor_id", None)
                    or getattr(event_data, "author_name", None)
                    or "agent"
                )
                print(f"[{agent_label}]:", end=" ", flush=True)
                last_response_id = rid
            print(event_data.text, end="", flush=True)

        elif event_type == "group_chat" and isinstance(event_data, GroupChatRequestSentEvent):
            # Manager routing a request to a participant
            if last_response_id is not None:
                print(flush=True)
                last_response_id = None
            print(
                f"\n[Round {event_data.round_index}] → {event_data.participant_name}",
                flush=True,
            )

        elif event_type == "magentic_orchestrator":
            # Manager plan / progress ledger — log to stderr to keep stdout clean
            print(f"\n[Orchestrator] {getattr(event_data, 'event_type', '')}", file=sys.stderr)

        elif event_type == "output" and not isinstance(event_data, AgentResponseUpdate):
            # Final output event — capture for return value
            output_event = event

    if last_response_id is not None:
        print(flush=True)

    if output_event is not None:
        return cast(list[Message], output_event.data)
    return []
```

### 2.3 `run_workflow(workflow, task) -> list[Message]`

Synchronous wrapper — calls `asyncio.run()` once:

```python
def run_workflow(workflow: Any, task: str) -> list[Message]:
    """Synchronous wrapper around run_workflow_streaming.

    Args:
        workflow: A built MAF workflow object.
        task: The user task string.

    Returns:
        The final list[Message] from the workflow.
    """
    return asyncio.run(run_workflow_streaming(workflow, task))
```

### 2.4 `load_and_run(workflow_dir, task, client, *, tool_registry, builder) -> list[Message]`

High-level convenience entry point:

```python
def load_and_run(
    workflow_dir: str | Path,
    task: str,
    client: Any,
    *,
    tool_registry: Any | None = None,
    builder: str = "magentic",
) -> list[Message]:
    """Discover agents, build the workflow, and run it in a single call.

    Args:
        workflow_dir: Path to the workflow directory containing agents/*.md.
        task: The user task string.
        client: A configured MAF chat client.
        tool_registry: Optional ToolRegistry instance.
        builder: "magentic" (default) or "group_chat".

    Returns:
        The final list[Message] from the workflow.
    """
    from <package_module>.workflow import MAFLoader  # local import to avoid circular dependency

    loader = MAFLoader(
        workflow_dir=workflow_dir,
        client=client,
        tool_registry=tool_registry,
    )
    workflow = loader.build(builder=builder)
    return run_workflow(workflow, task)
```

### 2.5 `_cli_main()` — CLI entry point

```python
def _cli_main() -> None:
    """CLI entry point: maf-packager <workflow_dir> <task>"""
    if len(sys.argv) < 3:
        print("Usage: maf-packager <workflow_dir> <task>", file=sys.stderr)
        sys.exit(1)

    workflow_dir = sys.argv[1]
    task = sys.argv[2]

    from <package_module>.config import build_client

    client = build_client()
    messages = load_and_run(workflow_dir=workflow_dir, task=task, client=client)
    for msg in messages:
        author = getattr(msg, "author_name", None) or getattr(msg, "role", "unknown")
        print(f"\n{author}: {msg.text}")
```

---

## Code Requirements

- `from __future__ import annotations` on both files.
- `asyncio.run()` is called **only** in `run_workflow` (the sync wrapper). Never nest `asyncio.run` calls.
- Agent label in streaming output: `getattr(event, "executor_id", None) or event_data.author_name or "agent"`.
- Streaming tokens print to **stdout**; orchestrator events log to **stderr**.
- All public callables fully type-annotated (`workflow: Any` is acceptable since MAF workflow types are not exported).
- `load_and_run` imports `MAFLoader` inside the function body to avoid circular imports (`workflow.py` imports from `factory.py`, `runner.py` imports from `workflow.py` only in `load_and_run`).
- Module-level docstring on both files.
- `_cli_main` is not exported in `__all__` — it is only referenced in `pyproject.toml` scripts.
