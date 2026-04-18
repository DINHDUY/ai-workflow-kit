# MAF Packager — Implementation Specification

> **Purpose**: Reference document for implementing `maf-packager`, a Python package that discovers
> agent markdown files, parses YAML frontmatter, instantiates Microsoft Agent Framework (MAF)
> `Agent` objects, assembles multi-agent workflows, and runs them with a user task.
>
> **Scope**: Full API reference, working code examples, testing patterns, and recommended package
> structure — sufficient to implement without additional research.

---

## 1. Package Overview

### What maf-packager does

Given a workflow directory like `workflows/my-workflow/`, `maf-packager`:

1. Discovers all `agents/*.md` files in the workflow directory
2. Parses YAML frontmatter from each file to extract agent config (name, description, role, tools)
3. Instantiates MAF `Agent` objects from the parsed config
4. Identifies the orchestrator agent (the file matching `<workflow-name>.orchestrator.md`)
5. Assembles a `MagenticBuilder` (or `GroupChatBuilder`) workflow with participants + manager
6. Returns a runnable workflow or runs it immediately with a user task

### Microsoft Agent Framework (MAF)

- **PyPI package**: `agent-framework` (v1.0.1, released April 9, 2026)
- **GitHub**: https://github.com/microsoft/agent-framework
- **Python requirement**: 3.10+

---

## 2. Installation

```bash
# Full install (all integrations)
pip install agent-framework

# Selective installs
pip install agent-framework-core                # Core + OpenAI + workflows
pip install agent-framework-foundry             # Azure AI Foundry integration
pip install agent-framework-orchestrations      # Multi-agent orchestration builders
pip install agent-framework-openai              # OpenAI / Azure OpenAI clients
```

---

## 3. Core API Reference

### 3.1 `Agent`

```python
from agent_framework import Agent

agent = Agent(
    name="ResearcherAgent",               # str — required for orchestration
    description="Gathers information",    # str — used by orchestrator to select agent
    instructions="You are a researcher.", # str — system prompt
    client=client,                        # ChatClient instance
    tools=[get_weather, search_web],      # list of callables or tool dicts
)
```

**Key properties**:

| Property | Type | Description |
|---|---|---|
| `name` | `str \| None` | Agent name (required for MagenticBuilder/GroupChatBuilder) |
| `description` | `str \| None` | Used by orchestrator to route tasks |
| `instructions` | `str \| None` | System prompt sent to the LLM |
| `client` | `ChatClient` | The underlying LLM client |
| `tools` | `list` | Callables, `FunctionTool` instances, or tool dicts |
| `default_options` | `dict` | Merged with per-run options |
| `context_providers` | `list` | History, tool, and instruction providers |

**Running an agent**:

```python
import asyncio

# Non-streaming
result = asyncio.run(agent.run("What is the capital of France?"))
print(result.text)                # "Paris"
print(result.messages[0].role)    # "assistant"
print(result.messages[0].author_name)  # agent name

# Streaming
async def run():
    async for update in agent.run("Tell me a story", stream=True):
        print(update.text, end="", flush=True)

asyncio.run(run())
```

**Running with a session** (multi-turn):

```python
session = agent.create_session()
response1 = asyncio.run(agent.run("My name is Alex.", session=session))
response2 = asyncio.run(agent.run("What was my name?", session=session))
```

---

### 3.2 Chat Clients

#### `FoundryChatClient` (recommended for Azure)

```python
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential, DefaultAzureCredential
import os

client = FoundryChatClient(
    project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],  # e.g. "https://.../..."
    model=os.environ["FOUNDRY_MODEL"],                         # e.g. "gpt-4o"
    credential=AzureCliCredential(),                           # or DefaultAzureCredential()
)
```

Required env vars:
- `FOUNDRY_PROJECT_ENDPOINT` — Azure AI Foundry project endpoint URL
- `FOUNDRY_MODEL` — model deployment name

**Getting hosted tools** (code interpreter, file search, etc.):

```python
code_interpreter_tool = client.get_code_interpreter_tool()
agent = Agent(name="Coder", client=client, tools=code_interpreter_tool)
```

#### `OpenAIChatClient`

```python
from agent_framework.openai import OpenAIChatClient

# Via environment variables (auto-detected)
# Set: OPENAI_API_KEY, OPENAI_CHAT_MODEL (or OPENAI_CHAT_COMPLETION_MODEL)
client = OpenAIChatClient()

# Explicit parameters
client = OpenAIChatClient(
    api_key="sk-...",
    model="gpt-4o",
)
```

#### `OpenAIChatCompletionClient` (Azure OpenAI — chat completions)

```python
from agent_framework.openai import OpenAIChatCompletionClient

client = OpenAIChatCompletionClient(
    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    model=os.environ["AZURE_OPENAI_MODEL"],
    api_version="2024-02-01",
)
```

Env vars:
- `AZURE_OPENAI_API_KEY` — API key (or use managed identity)
- `AZURE_OPENAI_ENDPOINT` — endpoint URL
- `AZURE_OPENAI_MODEL` — deployment name

---

### 3.3 Tool Definition

Tools are plain Python callables. Use `Annotated` for parameter documentation:

```python
from typing import Annotated
from agent_framework import tool

# Simple callable — docstring becomes tool description
def get_weather(
    location: Annotated[str, "The city to get weather for"],
) -> str:
    """Get current weather for a location."""
    return f"Sunny, 22°C in {location}"

# With @tool decorator for extra control
@tool(name="search_web", approval_mode="never_require")
def search_web(
    query: Annotated[str, "The search query string"],
    max_results: Annotated[int, "Maximum number of results to return"] = 5,
) -> str:
    """Search the web for information."""
    return f"Search results for: {query}"

# Using pydantic Field for richer descriptions
from pydantic import Field

def analyze_data(
    data: Annotated[list[dict], Field(description="List of data records to analyze")],
    metric: Annotated[str, Field(description="The metric to compute, e.g. 'mean', 'sum'")],
) -> dict:
    """Analyze a dataset and return computed metrics."""
    return {"metric": metric, "result": 42.0}

# Register tools with agent
agent = Agent(
    name="ResearchAgent",
    instructions="You are a research assistant.",
    client=client,
    tools=[get_weather, search_web, analyze_data],
)
```

---

### 3.4 Message and Content Types

```python
from agent_framework import Message, Content, Role

# Simple text message
msg = Message(role="user", contents=["Hello, how are you?"])

# With Content objects
msg = Message(role="user", contents=[Content.from_text("Hello")])

# Key properties
msg.role       # "user" | "assistant" | "system" | "tool"
msg.text       # str — concatenated text of all content items
msg.author_name  # str | None — set for agent responses
msg.contents   # list[Content]
```

**`AgentResponse`** (non-streaming result):

```python
result = await agent.run("Hello")

result.text           # str — full response text
result.messages       # list[Message]
result.response_id    # str | None
result.value          # parsed Pydantic model (if response_format set)
```

**`AgentResponseUpdate`** (streaming token):

```python
async for update in agent.run("Hello", stream=True):
    update.text          # str — token or chunk
    update.author_name   # str | None
    update.response_id   # str | None
```

---

### 3.5 Session Management

```python
from agent_framework import Agent, AgentSession, InMemoryHistoryProvider

agent = Agent(client=client, name="MyAgent")

# Create a new session
session = agent.create_session()

# Multi-turn conversation
r1 = await agent.run("My name is Alex", session=session)
r2 = await agent.run("What is my name?", session=session)  # sees history

# Get a session with existing service-side ID (e.g. Azure Assistants thread)
session = agent.get_session(service_session_id="thread_abc123")

# Serialize/deserialize session (e.g. to store in a database)
state = session.to_dict()
restored = AgentSession.from_dict(state)

# Inspect session message history
memory_state = session.state.get(InMemoryHistoryProvider.DEFAULT_SOURCE_ID, {})
messages = memory_state.get("messages", [])
```

---

## 4. Orchestration Builders

All builders are imported from `agent_framework.orchestrations`:

```python
from agent_framework.orchestrations import (
    SequentialBuilder,
    ConcurrentBuilder,
    HandoffBuilder,
    GroupChatBuilder,
    MagenticBuilder,
)
```

### 4.1 `SequentialBuilder`

Agents run one after another. Output of each becomes input to the next.

```python
workflow = SequentialBuilder(
    participants=[agent_a, agent_b, agent_c],
    intermediate_outputs=True,
).build()

result = await workflow.run("Analyze this document")
```

### 4.2 `ConcurrentBuilder`

All agents run in parallel; results are merged.

```python
workflow = ConcurrentBuilder(
    participants=[agent_a, agent_b],
    intermediate_outputs=True,
).build()
```

### 4.3 `HandoffBuilder`

Agents transfer control to each other. Each agent requiring per-call history:

```python
workflow = HandoffBuilder(
    participants=[triage_agent, specialist_agent],
).build()

# Note: agents used in HandoffBuilder need:
agent = Agent(
    client=client,
    name="TriageAgent",
    require_per_service_call_history_persistence=True,  # required
    tools=[transfer_to_specialist],
)
```

### 4.4 `GroupChatBuilder`

An orchestrator agent manages conversation turns between participants.

```python
from agent_framework.orchestrations import GroupChatBuilder

# Orchestrator agent coordinates who speaks when
orchestrator = Agent(
    name="Orchestrator",
    description="Coordinates multi-agent collaboration by selecting speakers",
    instructions="""
    You coordinate a team conversation to solve the user's task.
    Guidelines:
    - Start with Researcher to gather information
    - Then have Writer synthesize the final answer
    - Only finish after both have contributed meaningfully
    """,
    client=client,
)

researcher = Agent(name="Researcher", description="Collects background information",
                   instructions="Gather concise facts that help a teammate answer the question.",
                   client=client)

writer = Agent(name="Writer", description="Synthesizes polished answers",
               instructions="Compose clear and structured answers using any notes provided.",
               client=client)

workflow = (
    GroupChatBuilder(
        participants=[researcher, writer],
        orchestrator_agent=orchestrator,
        termination_condition=lambda messages: sum(
            1 for msg in messages if msg.role == "assistant"
        ) >= 4,
        intermediate_outputs=True,
    )
    .with_termination_condition(
        lambda messages: sum(1 for msg in messages if msg.role == "assistant") >= 4
    )
    .build()
)
```

### 4.5 `MagenticBuilder` (recommended for complex tasks)

A planning-based orchestrator that uses a dedicated manager agent to assign tasks.

```python
from agent_framework import Agent, AgentResponseUpdate, Message, WorkflowEvent
from agent_framework.foundry import FoundryChatClient
from agent_framework.orchestrations import (
    GroupChatRequestSentEvent,
    MagenticBuilder,
    MagenticProgressLedger,
)
from azure.identity import AzureCliCredential
import asyncio, json, os

async def run_magentic_workflow(task: str):
    client = FoundryChatClient(
        project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        model=os.environ["FOUNDRY_MODEL"],
        credential=AzureCliCredential(),
    )

    researcher = Agent(
        name="ResearcherAgent",
        description="Specialist in research and information gathering",
        instructions="You are a Researcher. Find information without quantitative analysis.",
        client=client,
    )

    coder = Agent(
        name="CoderAgent",
        description="Writes and executes code to analyze data",
        instructions="You solve questions using code. Provide detailed analysis.",
        client=client,
        tools=[client.get_code_interpreter_tool()],
    )

    manager = Agent(
        name="MagenticManager",
        description="Orchestrator that coordinates the research and coding workflow",
        instructions="You coordinate a team to complete complex tasks efficiently.",
        client=client,
    )

    workflow = MagenticBuilder(
        participants=[researcher, coder],
        manager_agent=manager,
        intermediate_outputs=True,   # emit WorkflowOutputEvent for each agent turn
        max_round_count=10,          # max total turns
        max_stall_count=3,           # max turns without progress before reset
        max_reset_count=2,           # max resets before giving up
    ).build()

    last_response_id = None
    output_event = None

    async for event in workflow.run(task, stream=True):
        if event.type == "output" and isinstance(event.data, AgentResponseUpdate):
            # Streaming token from a participant agent
            rid = event.data.response_id
            if rid != last_response_id:
                if last_response_id is not None:
                    print()
                print(f"[{event.executor_id}]:", end=" ", flush=True)
                last_response_id = rid
            print(event.data.text, end="", flush=True)

        elif event.type == "magentic_orchestrator":
            # Manager agent event — plan review or progress ledger
            print(f"\n[Orchestrator] {event.data.event_type.name}")
            if isinstance(event.data.content, Message):
                print(f"Plan:\n{event.data.content.text}")
            elif isinstance(event.data.content, MagenticProgressLedger):
                print(json.dumps(event.data.content.to_dict(), indent=2))

        elif event.type == "group_chat" and isinstance(event.data, GroupChatRequestSentEvent):
            # Manager routing a request to a participant
            print(f"\n[Round {event.data.round_index}] → {event.data.participant_name}")

        elif event.type == "output":
            # Final output: list[Message] from all participants
            output_event = event

    if output_event:
        from typing import cast
        messages = cast(list[Message], output_event.data)
        for msg in messages:
            print(f"\n{msg.author_name or msg.role}: {msg.text}")

asyncio.run(run_magentic_workflow("Compare Python and Rust for systems programming."))
```

---

## 5. Workflow Event Reference

| `event.type` | `event.data` type | Description |
|---|---|---|
| `"output"` (streaming) | `AgentResponseUpdate` | Streaming token from a participant |
| `"output"` (final) | `list[Message]` | Complete conversation transcript |
| `"magentic_orchestrator"` | `MagenticOrchestratorEvent` | Manager plan/progress update |
| `"group_chat"` | `GroupChatRequestSentEvent` | Manager routing to a participant |
| `"executor_invoked"` | any | An executor (agent) was invoked |
| `"executor_completed"` | any | An executor (agent) completed its turn |

**`GroupChatRequestSentEvent` fields**:
- `.round_index` — int, current round number
- `.participant_name` — str, name of the selected participant

**`MagenticProgressLedger` fields**:
- `.to_dict()` — dict representation for logging

---

## 6. Wrapping a Workflow as an Agent

Any workflow can be wrapped as an `Agent` for composability (e.g. using a workflow as a tool inside another workflow):

```python
from agent_framework import Agent, AgentSession, InMemoryHistoryProvider
from agent_framework.foundry import FoundryChatClient
from agent_framework.orchestrations import SequentialBuilder, MagenticBuilder
from azure.identity import AzureCliCredential
import asyncio

async def demo():
    client = FoundryChatClient(
        project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        model=os.environ["FOUNDRY_MODEL"],
        credential=AzureCliCredential(),
    )

    assistant = Agent(client=client, name="assistant",
                      instructions="You are a helpful assistant.")
    summarizer = Agent(client=client, name="summarizer",
                       instructions="Summarize the key point in one sentence.")

    workflow = SequentialBuilder(participants=[assistant, summarizer]).build()

    # Wrap workflow as an agent
    agent = workflow.as_agent()

    # Multi-turn conversation using sessions
    session = agent.create_session()

    r1 = await agent.run("My name is Alex and I'm learning ML.", session=session)
    for msg in r1.messages:
        print(f"[{msg.author_name or msg.role}]: {msg.text}")

    r2 = await agent.run("What was my name again?", session=session)
    for msg in r2.messages:
        print(f"[{msg.author_name or msg.role}]: {msg.text}")

    # Serialize session (e.g. store to database)
    serialized = session.to_dict()
    restored = AgentSession.from_dict(serialized)
    r3 = await agent.run("Can you suggest a first project for me?", session=restored)

asyncio.run(demo())
```

---

## 7. Testing and Mocking Patterns

The MAF core test suite exposes two reusable mock clients. These can be copied directly into `maf-packager`'s test helpers.

### 7.1 `MockChatClient` (simple, no function invocation)

Use for unit tests where you don't need tool call routing:

```python
from collections.abc import AsyncIterable, Awaitable, Sequence
from typing import Any

from agent_framework import (
    ChatResponse,
    ChatResponseUpdate,
    Content,
    Message,
    ResponseStream,
)


class MockChatClient:
    """Minimal mock chat client for unit tests."""

    def __init__(self, **kwargs: Any) -> None:
        self.call_count: int = 0
        self.responses: list[ChatResponse] = []
        self.streaming_responses: list[list[ChatResponseUpdate]] = []

    def get_response(
        self,
        messages: str | Message | list[str] | list[Message],
        *,
        stream: bool = False,
        options: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Awaitable[ChatResponse] | ResponseStream[ChatResponseUpdate, ChatResponse]:
        options = options or {}
        if stream:
            return self._get_streaming_response(messages=messages, options=options, **kwargs)

        async def _get() -> ChatResponse:
            self.call_count += 1
            if self.responses:
                return self.responses.pop(0)
            return ChatResponse(messages=Message(role="assistant", contents=["test response"]))

        return _get()

    def _get_streaming_response(
        self,
        *,
        messages: Any,
        options: dict[str, Any],
        **kwargs: Any,
    ) -> ResponseStream[ChatResponseUpdate, ChatResponse]:
        async def _stream() -> AsyncIterable[ChatResponseUpdate]:
            self.call_count += 1
            if self.streaming_responses:
                for update in self.streaming_responses.pop(0):
                    yield update
            else:
                yield ChatResponseUpdate(
                    contents=[Content.from_text("test streaming response ")],
                    role="assistant",
                )
                yield ChatResponseUpdate(
                    contents=[Content.from_text("another update")],
                    role="assistant",
                )

        def _finalize(updates: Sequence[ChatResponseUpdate]) -> ChatResponse:
            return ChatResponse.from_updates(updates, output_format_type=options.get("response_format"))

        return ResponseStream(_stream(), finalizer=_finalize)
```

### 7.2 `MockBaseChatClient` (full-featured, supports tool calls)

Use when testing agents with tool-calling and function invocation pipelines:

```python
from collections.abc import AsyncIterable, MutableSequence, Sequence
from typing import Any, Generic
from unittest.mock import patch

from agent_framework import (
    BaseChatClient,
    ChatMiddlewareLayer,
    ChatResponse,
    ChatResponseUpdate,
    Content,
    FunctionInvocationLayer,
    Message,
    ResponseStream,
)
from agent_framework._clients import OptionsCoT
from agent_framework.observability import ChatTelemetryLayer


class MockBaseChatClient(
    FunctionInvocationLayer[OptionsCoT],
    ChatMiddlewareLayer[OptionsCoT],
    ChatTelemetryLayer[OptionsCoT],
    BaseChatClient[OptionsCoT],
    Generic[OptionsCoT],
):
    """Full-featured mock that routes tool calls like a real client."""

    def __init__(self, **kwargs: Any):
        super().__init__(middleware=[], **kwargs)
        self.run_responses: list[ChatResponse] = []
        self.streaming_responses: list[list[ChatResponseUpdate]] = []
        self.call_count: int = 0

    def _inner_get_response(
        self,
        *,
        messages: MutableSequence[Message],
        stream: bool,
        options: dict[str, Any],
        **kwargs: Any,
    ) -> Any:
        if stream:
            return self._get_streaming_response(messages=messages, options=options, **kwargs)

        async def _get() -> ChatResponse:
            return await self._get_non_streaming_response(
                messages=messages, options=options, **kwargs
            )

        return _get()

    async def _get_non_streaming_response(
        self,
        *,
        messages: MutableSequence[Message],
        options: dict[str, Any],
        **kwargs: Any,
    ) -> ChatResponse:
        self.call_count += 1
        if not self.run_responses:
            return ChatResponse(
                messages=Message(role="assistant", contents=[f"test response - {messages[-1].text}"])
            )
        return self.run_responses.pop(0)

    def _get_streaming_response(
        self,
        *,
        messages: MutableSequence[Message],
        options: dict[str, Any],
        **kwargs: Any,
    ) -> ResponseStream[ChatResponseUpdate, ChatResponse]:
        async def _stream() -> AsyncIterable[ChatResponseUpdate]:
            self.call_count += 1
            if not self.streaming_responses:
                yield ChatResponseUpdate(
                    contents=[Content.from_text(f"update - {messages[0].text}")],
                    role="assistant",
                    finish_reason="stop",
                )
                return
            for update in self.streaming_responses.pop(0):
                yield update

        def _finalize(updates: Sequence[ChatResponseUpdate]) -> ChatResponse:
            return ChatResponse.from_updates(updates, output_format_type=options.get("response_format"))

        return ResponseStream(_stream(), finalizer=_finalize)


def make_mock_client(max_iterations: int = 2) -> MockBaseChatClient:
    """Factory helper — patches DEFAULT_MAX_ITERATIONS for deterministic tests."""
    with patch("agent_framework._tools.DEFAULT_MAX_ITERATIONS", max_iterations):
        return MockBaseChatClient()
```

### 7.3 `MockAgent` (implements `SupportsAgentRun`)

Use when testing code that consumes agents (e.g., orchestration builders, maf-packager):

```python
from collections.abc import AsyncIterable, Awaitable
from typing import Any
from uuid import uuid4

from agent_framework import (
    AgentResponse,
    AgentResponseUpdate,
    AgentSession,
    Content,
    Message,
    SupportsAgentRun,
)


class MockAgent(SupportsAgentRun):
    """Mock agent for testing orchestration logic."""

    def __init__(
        self,
        name: str = "MockAgent",
        description: str = "Mock description",
        response_text: str = "Mock response",
    ) -> None:
        self._name = name
        self._description = description
        self._response_text = response_text
        self.run_call_count = 0

    @property
    def id(self) -> str:
        return str(uuid4())

    @property
    def name(self) -> str | None:
        return self._name

    @property
    def description(self) -> str | None:
        return self._description

    def run(
        self,
        messages: str | Message | list[str] | list[Message] | None = None,
        *,
        session: AgentSession | None = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> Awaitable[AgentResponse] | AsyncIterable[AgentResponseUpdate]:
        if stream:
            return self._run_stream(messages=messages, session=session, **kwargs)
        return self._run(messages=messages, session=session, **kwargs)

    async def _run(self, **kwargs: Any) -> AgentResponse:
        self.run_call_count += 1
        return AgentResponse(
            messages=[Message(role="assistant", contents=[Content.from_text(self._response_text)])]
        )

    async def _run_stream(self, **kwargs: Any) -> AsyncIterable[AgentResponseUpdate]:
        self.run_call_count += 1
        yield AgentResponseUpdate(contents=[Content.from_text(self._response_text)])

    def create_session(self) -> AgentSession:
        return AgentSession()
```

### 7.4 pytest fixture wiring

```python
# tests/conftest.py
import pytest
from tests.helpers.mocks import MockChatClient, MockBaseChatClient, MockAgent


@pytest.fixture
def mock_client() -> MockChatClient:
    return MockChatClient()


@pytest.fixture
def mock_base_client() -> MockBaseChatClient:
    return MockBaseChatClient()


@pytest.fixture
def mock_agent() -> MockAgent:
    return MockAgent()
```

### 7.5 Example unit test for maf-packager

```python
# tests/test_loader.py
import pytest
from agent_framework import Agent, AgentResponse

from maf_loader import MAFLoader
from tests.helpers.mocks import MockChatClient


@pytest.mark.asyncio
async def test_loader_discovers_agents(tmp_path):
    """Loader discovers agent files and instantiates Agent objects."""
    # Create mock workflow directory
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()

    (agents_dir / "my-workflow.orchestrator.md").write_text("""---
name: OrchestratorAgent
description: Coordinates the team
role: orchestrator
instructions: You coordinate a research team.
---
# Orchestrator Agent
""")

    (agents_dir / "my-workflow.worker.md").write_text("""---
name: ResearcherAgent
description: Gathers information
role: worker
instructions: You are a researcher.
---
# Researcher Agent
""")

    client = MockChatClient()
    loader = MAFLoader(workflow_dir=tmp_path, client=client)
    agents = loader.load_agents()

    assert len(agents) == 2
    names = {a.name for a in agents}
    assert "OrchestratorAgent" in names
    assert "ResearcherAgent" in names


@pytest.mark.asyncio
async def test_loader_identifies_orchestrator(tmp_path):
    """Loader identifies the orchestrator from the frontmatter role field."""
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()

    (agents_dir / "my-workflow.orchestrator.md").write_text("""---
name: Manager
role: orchestrator
instructions: You manage the team.
---
""")
    (agents_dir / "my-workflow.worker.md").write_text("""---
name: Worker
role: worker
instructions: You do the work.
---
""")

    loader = MAFLoader(workflow_dir=tmp_path, client=MockChatClient())
    orchestrator, workers = loader.get_orchestrator_and_workers()

    assert orchestrator.name == "Manager"
    assert len(workers) == 1
    assert workers[0].name == "Worker"
```

---

## 8. maf-packager Implementation Guide

### 8.1 Agent Markdown File Format

Each agent file at `workflows/<workflow-name>/agents/<workflow-name>.<role>.md`:

```markdown
---
name: ResearcherAgent
description: Specialist in research and information gathering
role: worker                    # "orchestrator" | "worker" | "manager"
instructions: |
  You are a Researcher. Find information without quantitative analysis.
  Always cite your sources.
tools:                          # optional list of tool names to register
  - search_web
  - get_weather
model: gpt-4o                   # optional model override
---

# Researcher Agent

Extended description or notes (not parsed by maf-packager).
```

**Frontmatter fields**:

| Field | Required | Description |
|---|---|---|
| `name` | Yes | Agent name passed to `Agent(name=...)` |
| `description` | Yes | Passed to `Agent(description=...)` |
| `role` | Yes | `"orchestrator"`, `"worker"`, or `"manager"` |
| `instructions` | Yes | System prompt for the agent |
| `tools` | No | List of tool names to look up from a tool registry |
| `model` | No | Override the default model for this agent |

### 8.2 Recommended Package Structure

```
maf_loader/
├── __init__.py            # Public API: MAFLoader, load_workflow, run_workflow
├── loader.py              # MAFLoader class — discover, parse, instantiate
├── parser.py              # YAML frontmatter parser for agent .md files
├── registry.py            # Tool registry (name → callable mapping)
├── builder.py             # Workflow builder — wraps MagenticBuilder/GroupChatBuilder
├── runner.py              # Async runner — event loop, streaming output handler
└── types.py               # AgentConfig dataclass, WorkflowConfig

tests/
├── conftest.py
├── helpers/
│   └── mocks.py           # MockChatClient, MockBaseChatClient, MockAgent
├── test_parser.py
├── test_loader.py
├── test_builder.py
└── test_runner.py
```

### 8.3 `types.py` — Data Classes

```python
# maf_loader/types.py
from dataclasses import dataclass, field


@dataclass
class AgentConfig:
    name: str
    description: str
    role: str                       # "orchestrator" | "worker" | "manager"
    instructions: str
    tools: list[str] = field(default_factory=list)
    model: str | None = None
    source_file: str | None = None  # path to the .md file


@dataclass
class WorkflowConfig:
    workflow_name: str
    agents: list[AgentConfig]

    @property
    def orchestrator(self) -> AgentConfig | None:
        return next((a for a in self.agents if a.role == "orchestrator"), None)

    @property
    def workers(self) -> list[AgentConfig]:
        return [a for a in self.agents if a.role == "worker"]

    @property
    def manager(self) -> AgentConfig | None:
        return next((a for a in self.agents if a.role == "manager"), None)
```

### 8.4 `parser.py` — Frontmatter Parser

```python
# maf_loader/parser.py
from pathlib import Path
import re
import yaml

from maf_loader.types import AgentConfig


_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)


def parse_agent_file(path: Path) -> AgentConfig:
    """Parse a markdown agent file and return an AgentConfig."""
    content = path.read_text(encoding="utf-8")
    match = _FRONTMATTER_RE.match(content)
    if not match:
        raise ValueError(f"No YAML frontmatter found in {path}")

    data = yaml.safe_load(match.group(1))
    if not isinstance(data, dict):
        raise ValueError(f"Frontmatter must be a YAML mapping in {path}")

    required = ["name", "description", "role", "instructions"]
    for field in required:
        if field not in data:
            raise ValueError(f"Missing required frontmatter field '{field}' in {path}")

    return AgentConfig(
        name=data["name"],
        description=data["description"],
        role=data["role"],
        instructions=data["instructions"],
        tools=data.get("tools", []),
        model=data.get("model"),
        source_file=str(path),
    )
```

### 8.5 `loader.py` — MAFLoader

```python
# maf_loader/loader.py
from pathlib import Path
from typing import Any

from agent_framework import Agent

from maf_loader.parser import parse_agent_file
from maf_loader.registry import ToolRegistry
from maf_loader.types import AgentConfig, WorkflowConfig


class MAFLoader:
    """Discovers agent markdown files and instantiates MAF Agent objects."""

    def __init__(
        self,
        workflow_dir: str | Path,
        client: Any,                        # any ChatClient instance
        tool_registry: ToolRegistry | None = None,
    ) -> None:
        self.workflow_dir = Path(workflow_dir)
        self.client = client
        self.tool_registry = tool_registry or ToolRegistry()
        self._agents_dir = self.workflow_dir / "agents"
        self._workflow_name = self.workflow_dir.name

    def load_config(self) -> WorkflowConfig:
        """Parse all agent .md files and return a WorkflowConfig."""
        if not self._agents_dir.exists():
            raise FileNotFoundError(f"Agents directory not found: {self._agents_dir}")

        agent_configs = []
        for md_file in sorted(self._agents_dir.glob("*.md")):
            try:
                cfg = parse_agent_file(md_file)
                agent_configs.append(cfg)
            except ValueError as e:
                raise ValueError(f"Failed to parse {md_file}: {e}") from e

        if not agent_configs:
            raise ValueError(f"No agent files found in {self._agents_dir}")

        return WorkflowConfig(
            workflow_name=self._workflow_name,
            agents=agent_configs,
        )

    def instantiate_agent(self, cfg: AgentConfig) -> Agent:
        """Create an Agent from an AgentConfig."""
        tools = [self.tool_registry.get(name) for name in cfg.tools]
        tools = [t for t in tools if t is not None]  # filter missing tools

        return Agent(
            name=cfg.name,
            description=cfg.description,
            instructions=cfg.instructions,
            client=self.client,
            tools=tools if tools else [],
        )

    def load_agents(self) -> list[Agent]:
        """Discover and instantiate all agents."""
        config = self.load_config()
        return [self.instantiate_agent(cfg) for cfg in config.agents]

    def get_orchestrator_and_workers(self) -> tuple[Agent, list[Agent]]:
        """Return (orchestrator_agent, worker_agents)."""
        config = self.load_config()

        orchestrator_cfg = config.orchestrator
        if orchestrator_cfg is None:
            raise ValueError(
                f"No orchestrator agent found in {self._agents_dir}. "
                "Add 'role: orchestrator' to one agent's frontmatter."
            )

        worker_cfgs = config.workers
        if not worker_cfgs:
            raise ValueError(f"No worker agents found in {self._agents_dir}.")

        orchestrator = self.instantiate_agent(orchestrator_cfg)
        workers = [self.instantiate_agent(cfg) for cfg in worker_cfgs]
        return orchestrator, workers
```

### 8.6 `registry.py` — Tool Registry

```python
# maf_loader/registry.py
from typing import Any, Callable


class ToolRegistry:
    """Maps tool names to callable Python functions."""

    def __init__(self, tools: dict[str, Callable] | None = None) -> None:
        self._registry: dict[str, Callable] = tools or {}

    def register(self, name: str, fn: Callable) -> None:
        self._registry[name] = fn

    def get(self, name: str) -> Callable | None:
        return self._registry.get(name)

    def register_all(self, tools: dict[str, Callable]) -> None:
        self._registry.update(tools)
```

### 8.7 `builder.py` — Workflow Assembly

```python
# maf_loader/builder.py
from agent_framework import Agent
from agent_framework.orchestrations import GroupChatBuilder, MagenticBuilder


def build_magentic_workflow(
    workers: list[Agent],
    manager: Agent,
    *,
    max_round_count: int = 10,
    max_stall_count: int = 3,
    max_reset_count: int = 2,
    intermediate_outputs: bool = True,
):
    """Assemble a MagenticBuilder workflow."""
    return MagenticBuilder(
        participants=workers,
        manager_agent=manager,
        intermediate_outputs=intermediate_outputs,
        max_round_count=max_round_count,
        max_stall_count=max_stall_count,
        max_reset_count=max_reset_count,
    ).build()


def build_group_chat_workflow(
    workers: list[Agent],
    orchestrator: Agent,
    *,
    max_assistant_turns: int = 6,
    intermediate_outputs: bool = True,
):
    """Assemble a GroupChatBuilder workflow."""
    termination = lambda messages: sum(
        1 for m in messages if m.role == "assistant"
    ) >= max_assistant_turns

    return (
        GroupChatBuilder(
            participants=workers,
            orchestrator_agent=orchestrator,
            termination_condition=termination,
            intermediate_outputs=intermediate_outputs,
        )
        .with_termination_condition(termination)
        .build()
    )
```

### 8.8 `runner.py` — Streaming Runner

```python
# maf_loader/runner.py
import asyncio
from typing import Any, cast

from agent_framework import AgentResponseUpdate, Message, WorkflowEvent
from agent_framework.orchestrations import GroupChatRequestSentEvent


async def run_workflow_streaming(workflow: Any, task: str) -> list[Message]:
    """
    Run a workflow with streaming output.
    Returns the final list[Message] transcript.
    """
    last_response_id = None
    output_event = None

    async for event in workflow.run(task, stream=True):
        if event.type == "output" and isinstance(event.data, AgentResponseUpdate):
            rid = event.data.response_id
            if rid != last_response_id:
                if last_response_id is not None:
                    print()
                agent_label = getattr(event, "executor_id", event.data.author_name) or "agent"
                print(f"[{agent_label}]:", end=" ", flush=True)
                last_response_id = rid
            print(event.data.text, end="", flush=True)

        elif event.type == "group_chat" and isinstance(event.data, GroupChatRequestSentEvent):
            print(f"\n[Round {event.data.round_index}] → {event.data.participant_name}")

        elif event.type == "output":
            output_event = event

    print()  # final newline
    if output_event:
        return cast(list[Message], output_event.data)
    return []


def run_workflow(workflow: Any, task: str) -> list[Message]:
    """Synchronous wrapper for run_workflow_streaming."""
    return asyncio.run(run_workflow_streaming(workflow, task))
```

### 8.9 `__init__.py` — Public API

```python
# maf_loader/__init__.py
from maf_loader.loader import MAFLoader
from maf_loader.registry import ToolRegistry
from maf_loader.builder import build_magentic_workflow, build_group_chat_workflow
from maf_loader.runner import run_workflow, run_workflow_streaming
from maf_loader.types import AgentConfig, WorkflowConfig


def load_and_run(
    workflow_dir: str,
    task: str,
    client,
    *,
    tool_registry: ToolRegistry | None = None,
    builder: str = "magentic",
) -> list:
    """
    High-level convenience function.

    1. Discovers agent files in workflow_dir/agents/
    2. Parses frontmatter and instantiates Agent objects
    3. Builds a MagenticBuilder (or GroupChatBuilder) workflow
    4. Runs the workflow with the given task
    5. Returns the final list[Message] transcript

    Args:
        workflow_dir: Path to workflow directory (must contain agents/ subdirectory)
        task: The user task to solve
        client: A ChatClient instance (FoundryChatClient, OpenAIChatClient, etc.)
        tool_registry: Optional ToolRegistry mapping tool names to callables
        builder: "magentic" (default) or "group_chat"
    """
    loader = MAFLoader(workflow_dir=workflow_dir, client=client, tool_registry=tool_registry)
    orchestrator, workers = loader.get_orchestrator_and_workers()

    if builder == "magentic":
        workflow = build_magentic_workflow(workers=workers, manager=orchestrator)
    elif builder == "group_chat":
        workflow = build_group_chat_workflow(workers=workers, orchestrator=orchestrator)
    else:
        raise ValueError(f"Unknown builder: {builder!r}. Use 'magentic' or 'group_chat'.")

    return run_workflow(workflow, task)


__all__ = [
    "MAFLoader",
    "ToolRegistry",
    "build_magentic_workflow",
    "build_group_chat_workflow",
    "run_workflow",
    "run_workflow_streaming",
    "load_and_run",
    "AgentConfig",
    "WorkflowConfig",
]
```

---

## 9. End-to-End Usage Example

```python
# run.py
import os
from pathlib import Path
from azure.identity import AzureCliCredential
from agent_framework.foundry import FoundryChatClient
from maf_loader import load_and_run, ToolRegistry
from typing import Annotated


# 1. Define tools
def search_arxiv(
    query: Annotated[str, "Search query for academic papers"],
) -> str:
    """Search arXiv for academic papers."""
    return f"Found 5 papers matching '{query}'"


def summarize_paper(
    url: Annotated[str, "URL of the paper to summarize"],
) -> str:
    """Download and summarize a paper."""
    return f"Summary of paper at {url}"


# 2. Build tool registry
registry = ToolRegistry({
    "search_arxiv": search_arxiv,
    "summarize_paper": summarize_paper,
})

# 3. Create chat client
client = FoundryChatClient(
    project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
    model=os.environ["FOUNDRY_MODEL"],
    credential=AzureCliCredential(),
)

# 4. Run workflow
# Directory structure expected:
#   workflows/literature-review/
#   └── agents/
#       ├── literature-review.orchestrator.md
#       ├── literature-review.searcher.md
#       └── literature-review.synthesizer.md
messages = load_and_run(
    workflow_dir="workflows/literature-review",
    task="Survey recent papers on retrieval-augmented generation (RAG) from 2024.",
    client=client,
    tool_registry=registry,
    builder="magentic",
)

for msg in messages:
    print(f"\n{msg.author_name or msg.role}: {msg.text}")
```

---

## 10. All Imports Reference

```python
# Core
from agent_framework import (
    Agent,
    AgentResponse,
    AgentResponseUpdate,
    AgentSession,
    BaseChatClient,
    ChatContext,
    ChatOptions,
    ChatResponse,
    ChatResponseUpdate,
    Content,
    ContextProvider,
    FunctionTool,
    HistoryProvider,
    InMemoryHistoryProvider,
    Message,
    ResponseStream,
    Role,
    SessionContext,
    SupportsAgentRun,
    SupportsChatGetResponse,
    TruncationStrategy,
    WorkflowEvent,
    chat_middleware,
    tool,
)

# Foundry
from agent_framework.foundry import FoundryChatClient

# OpenAI / Azure OpenAI
from agent_framework.openai import OpenAIChatClient, OpenAIChatCompletionClient

# Orchestration builders
from agent_framework.orchestrations import (
    ConcurrentBuilder,
    GroupChatBuilder,
    GroupChatRequestSentEvent,
    HandoffBuilder,
    MagenticBuilder,
    MagenticProgressLedger,
    SequentialBuilder,
)

# Azure identity (for Foundry auth)
from azure.identity import AzureCliCredential, DefaultAzureCredential, ManagedIdentityCredential

# Python typing (for tool parameter docs)
from typing import Annotated
from pydantic import Field
```

---

## 11. Environment Variables Summary

| Variable | Used by | Description |
|---|---|---|
| `FOUNDRY_PROJECT_ENDPOINT` | `FoundryChatClient` | Azure AI Foundry project URL |
| `FOUNDRY_MODEL` | `FoundryChatClient` | Model deployment name |
| `OPENAI_API_KEY` | `OpenAIChatClient` | OpenAI API key |
| `OPENAI_CHAT_MODEL` | `OpenAIChatClient` | Model name (e.g. `gpt-4o`) |
| `OPENAI_CHAT_COMPLETION_MODEL` | `OpenAIChatClient` | Alt env var for model name |
| `AZURE_OPENAI_API_KEY` | `OpenAIChatCompletionClient` | Azure OpenAI key |
| `AZURE_OPENAI_ENDPOINT` | `OpenAIChatCompletionClient` | Azure OpenAI endpoint |
| `AZURE_OPENAI_MODEL` | `OpenAIChatCompletionClient` | Azure OpenAI deployment name |

---

## 12. Companion Tools

| Tool | Purpose | Access |
|---|---|---|
| `agent-framework` | MAF Python SDK | `pip install agent-framework` |
| `azure-identity` | Azure credential providers for Foundry auth | `pip install azure-identity` |
| `python-dotenv` | Load env vars from `.env` file | `pip install python-dotenv` |
| `pydantic` | Field descriptions for tool parameters, response parsing | `pip install pydantic` |
| `pyyaml` | Parse YAML frontmatter in agent .md files | `pip install pyyaml` |
| `pytest-asyncio` | Run async test functions with pytest | `pip install pytest-asyncio` |
| `opentelemetry-sdk` | Observability / tracing (optional, used in MAF core tests) | `pip install opentelemetry-sdk` |

---

## 13. Workflow Stack Diagram

```
workflows/
└── my-workflow/
    └── agents/
        ├── my-workflow.orchestrator.md  ← YAML frontmatter → AgentConfig(role="orchestrator")
        ├── my-workflow.researcher.md    ← YAML frontmatter → AgentConfig(role="worker")
        └── my-workflow.writer.md        ← YAML frontmatter → AgentConfig(role="worker")

                     ┌────────────────────────────────────────┐
                     │             maf_loader                  │
                     │                                         │
  .md files          │  parser.py                             │
  ──────────────►    │  AgentConfig (name, description,       │
  (YAML frontmatter) │             role, instructions, tools) │
                     │         ▼                               │
  ChatClient ──────► │  loader.py                             │
                     │  Agent(name, description, instructions, │
                     │       client, tools=[...])             │
                     │         ▼                               │
  ToolRegistry ────► │  builder.py                            │
                     │  MagenticBuilder(                       │
                     │    participants=[worker1, worker2],     │
                     │    manager_agent=orchestrator,          │
                     │    max_round_count=10, ...              │
                     │  ).build()                              │
                     │         ▼                               │
  task (str) ──────► │  runner.py                             │
                     │  async for event in                     │
                     │    workflow.run(task, stream=True):     │
                     │      event.type == "output" → print    │
                     │      event.type == "group_chat" → log  │
                     │  → list[Message] transcript             │
                     └────────────────────────────────────────┘
```

---

*Sources: https://github.com/microsoft/agent-framework · https://pypi.org/project/agent-framework/ · Python 3.10+, MAF v1.0.1*
