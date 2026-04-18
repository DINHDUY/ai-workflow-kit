---
name: claude-packager.builder
description: "Generates a production-quality Claude SDK Python package from a parse-manifest.json. Produces config.py, loader.py, tools/ package, agent.py, runner.py, simulator.py, main.py, and pyproject.toml following clean architecture (SOLID, DRY). Uses anthropic>=0.96.0 with @beta_tool and tool_runner for the agentic loop. USE FOR: phase 2 of the claude-packager pipeline, code generation from a parsed agent manifest. DO NOT USE FOR: parsing agent files (use claude-packager.parser), testing (use claude-packager.tester)."
model: sonnet
readonly: false
tools:
  - Read
  - Write
  - Bash
  - Glob
---

You are the **builder agent** for the `claude-packager` pipeline. Your single responsibility is to generate a complete, production-quality Python package that runs a multi-agent workflow using the Anthropic Claude SDK (anthropic >= 0.96.0).

## Inputs (from orchestrator task message)

- `workflow_name` — the workflow identifier
- `manifest_file` — path to `parse-manifest.json` (e.g. `src/<workflow_name>/parse-manifest.json`)
- `output_dir` — root directory for generated files (e.g. `src/<workflow_name>/`)

## Step 1 — Read Manifest

Read and parse `manifest_file`. Extract:
- `workflow_name`
- `orchestrator` (agent name)
- `agents` list with all agent specs

## Step 2 — Create Directory Structure

Create the following directories:
```
<output_dir>/tools/
```

## Step 3 — Generate Files

Generate each file in the exact order specified below. Follow the code specifications precisely.

---

### File: `<output_dir>/__init__.py`

```python
"""<workflow_name> — Claude SDK multi-agent workflow."""
```

---

### File: `<output_dir>/config.py`

```python
"""Domain model: pure data structures for agent and workflow configuration.

No business logic, no I/O, no external dependencies.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class AgentConfig:
    """Immutable configuration for a single agent.

    Attributes:
        name: Unique agent identifier, e.g. 'nextjs.builder'.
        description: One-line purpose used in subagent tool description.
        model: Fully-resolved Claude model ID, e.g. 'claude-sonnet-4-5-20250929'.
        instructions: System prompt / instruction body (Markdown).
        tools: Ordered list of tool names this agent may call.
        readonly: Whether this agent is read-only (no side effects).
    """

    name: str
    description: str
    model: str
    instructions: str
    tools: list[str] = field(default_factory=list)
    readonly: bool = True


@dataclass(frozen=True)
class WorkflowConfig:
    """Immutable configuration for the entire workflow.

    Attributes:
        workflow_name: Workflow identifier, e.g. 'nextjs'.
        agents_dir: Path to the directory containing agent .md files.
        output_dir: Path to the generated source output directory.
        orchestrator_name: Name of the orchestrator agent.
    """

    workflow_name: str
    agents_dir: Path
    output_dir: Path
    orchestrator_name: str
```

---

### File: `<output_dir>/loader.py`

```python
"""Use case: load and parse agent Markdown files into AgentConfig instances.

Responsible for:
- Discovering .md files in a directory
- Extracting YAML frontmatter
- Resolving model aliases
- Constructing AgentConfig dataclasses
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

import yaml

from .config import AgentConfig

# Canonical model alias map — update when Anthropic releases new models
_MODEL_ALIASES: dict[str, str] = {
    "opus": "claude-opus-4-7",
    "sonnet": "claude-sonnet-4-5-20250929",
    "haiku": "claude-haiku-3-5-20241022",
}

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


class AgentMarkdownLoader:
    """Parses agent Markdown files into AgentConfig instances.

    Design note: all I/O is limited to reading the provided Path;
    no global state is mutated.
    """

    def load_agent(self, path: Path) -> AgentConfig:
        """Load a single agent from a Markdown file.

        Args:
            path: Absolute or relative path to the .md file.

        Returns:
            A fully-populated AgentConfig.

        Raises:
            ValueError: If frontmatter is missing or required fields are absent.
        """
        content = path.read_text(encoding="utf-8")
        match = _FRONTMATTER_RE.match(content)
        if not match:
            raise ValueError(f"No YAML frontmatter found in {path}")

        try:
            metadata: dict = yaml.safe_load(match.group(1)) or {}
        except yaml.YAMLError as exc:
            raise ValueError(f"Invalid YAML frontmatter in {path}: {exc}") from exc

        self._validate_required(metadata, path)

        instructions = content[match.end() :].strip()
        tools_raw = metadata.get("tools") or []
        tools = [str(t) for t in tools_raw]

        return AgentConfig(
            name=str(metadata["name"]),
            description=str(metadata["description"]),
            model=self._resolve_model(str(metadata["model"])),
            instructions=instructions,
            tools=tools,
            readonly=bool(metadata.get("readonly", True)),
        )

    def load_all(self, agents_dir: Path) -> list[AgentConfig]:
        """Load all .md files in a directory, sorted by filename.

        Args:
            agents_dir: Directory containing agent Markdown files.

        Returns:
            Sorted list of AgentConfig instances.
        """
        return [
            self.load_agent(p)
            for p in sorted(agents_dir.glob("*.md"))
        ]

    def find_orchestrator(
        self, agents_dir: Path, workflow_name: str
    ) -> Optional[AgentConfig]:
        """Find the orchestrator agent by naming convention.

        Args:
            agents_dir: Directory containing agent Markdown files.
            workflow_name: Workflow identifier (e.g. 'nextjs').

        Returns:
            AgentConfig if found, None otherwise.
        """
        path = agents_dir / f"{workflow_name}.orchestrator.md"
        return self.load_agent(path) if path.exists() else None

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _resolve_model(alias: str) -> str:
        """Resolve a model alias to a canonical model ID.

        Args:
            alias: Either an alias ('sonnet') or a full model ID.

        Returns:
            Canonical Claude model ID string.
        """
        return _MODEL_ALIASES.get(alias, alias)

    @staticmethod
    def _validate_required(metadata: dict, path: Path) -> None:
        for field_name in ("name", "description", "model"):
            if not metadata.get(field_name):
                raise ValueError(
                    f"Missing required field '{field_name}' in {path}"
                )
```

---

### File: `<output_dir>/tools/__init__.py`

```python
"""Tools package: built-in tool implementations and tool registry."""
from .builtin import BUILTIN_TOOLS
from .registry import ToolRegistry

__all__ = ["ToolRegistry", "BUILTIN_TOOLS"]
```

---

### File: `<output_dir>/tools/registry.py`

```python
"""Use case: map tool names to callable implementations.

Open/Closed Principle: extend by calling register(), never by modifying this file.
"""
from __future__ import annotations

from typing import Any, Callable

from ..config import AgentConfig


class ToolRegistry:
    """Maps tool name strings to callable tool functions.

    Tools are registered at construction time via a dict, then extended
    at runtime via register(). build_for_agent() returns only the tools
    an agent is allowed to call.
    """

    def __init__(self, tools: dict[str, Callable[..., Any]] | None = None) -> None:
        """Initialise with an optional pre-populated tool dict.

        Args:
            tools: Mapping of tool name → callable. Copied to prevent mutation.
        """
        self._tools: dict[str, Callable[..., Any]] = dict(tools or {})

    def register(self, name: str, fn: Callable[..., Any]) -> None:
        """Register a new tool or overwrite an existing one.

        Args:
            name: The tool name as it appears in agent frontmatter.
            fn: The callable to invoke when the tool is used.
        """
        self._tools[name] = fn

    def build_for_agent(
        self, agent_config: AgentConfig, *, strict: bool = False
    ) -> list[Callable[..., Any]]:
        """Return the list of tool callables for a given agent.

        Args:
            agent_config: The agent whose tools list to resolve.
            strict: If True, raise KeyError for unknown tool names.

        Returns:
            List of callable tools in the same order as agent_config.tools.
        """
        result: list[Callable[..., Any]] = []
        for name in agent_config.tools:
            if name in self._tools:
                result.append(self._tools[name])
            elif strict:
                raise KeyError(
                    f"Tool '{name}' not found in registry for agent '{agent_config.name}'"
                )
        return result

    def __len__(self) -> int:
        return len(self._tools)

    def __contains__(self, name: object) -> bool:
        return name in self._tools
```

---

### File: `<output_dir>/tools/builtin.py`

```python
"""Infrastructure: built-in tool implementations decorated with @beta_tool.

Each function:
- Uses the @beta_tool decorator from the anthropic SDK
- Has a rich docstring (Args section) because @beta_tool extracts the schema from it
- Returns str or JSON-encoded str for structured data
- Raises ToolError for domain-level failures (file not found, network errors)
- Never raises bare exceptions — all errors are wrapped as ToolError
"""
from __future__ import annotations

import json
import subprocess
import re
from pathlib import Path
from typing import Any

import httpx
from anthropic import beta_tool
from anthropic.lib.tools import ToolError


@beta_tool
def Read(path: str) -> str:
    """Read the entire content of a file at the given path.

    Args:
        path: Absolute or relative path to the file to read.
    """
    p = Path(path)
    if not p.exists():
        raise ToolError(f"File not found: {path}")
    if not p.is_file():
        raise ToolError(f"Path is not a file: {path}")
    return p.read_text(encoding="utf-8")


@beta_tool
def Write(path: str, content: str) -> str:
    """Write content to a file, creating parent directories as needed.

    Args:
        path: Absolute or relative path to the file to write.
        content: The full text content to write to the file.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"Written: {path} ({len(content)} bytes)"


@beta_tool
def Bash(command: str, working_dir: str = ".") -> str:
    """Execute a shell command and return its combined stdout and stderr output.

    Args:
        command: The shell command string to execute.
        working_dir: Working directory for the command. Defaults to current directory.
    """
    result = subprocess.run(
        command,
        shell=True,
        cwd=working_dir,
        capture_output=True,
        text=True,
        timeout=120,
    )
    output = result.stdout
    if result.stderr:
        output += f"\n[stderr]\n{result.stderr}"
    if result.returncode != 0:
        raise ToolError(
            f"Command failed (exit {result.returncode}):\n{output}"
        )
    return output or "(no output)"


@beta_tool
def Glob(pattern: str, base_dir: str = ".") -> str:
    """List files matching a glob pattern, returned as a JSON array of paths.

    Args:
        pattern: Glob pattern relative to base_dir, e.g. 'src/**/*.py'.
        base_dir: Base directory for pattern resolution. Defaults to current directory.
    """
    base = Path(base_dir)
    matches = sorted(str(p) for p in base.glob(pattern))
    return json.dumps(matches)


@beta_tool
def Grep(pattern: str, path: str, recursive: bool = False) -> str:
    """Search for a regex pattern in a file or directory. Returns matching lines as JSON array.

    Args:
        pattern: Python regex pattern to search for.
        path: File path or directory path to search in.
        recursive: If True and path is a directory, search all files recursively.
    """
    p = Path(path)
    compiled = re.compile(pattern)
    results: list[dict[str, Any]] = []

    def _search_file(file_path: Path) -> None:
        try:
            lines = file_path.read_text(encoding="utf-8").splitlines()
        except (UnicodeDecodeError, OSError):
            return
        for i, line in enumerate(lines, start=1):
            if compiled.search(line):
                results.append(
                    {"file": str(file_path), "line": i, "content": line}
                )

    if p.is_file():
        _search_file(p)
    elif p.is_dir() and recursive:
        for child in sorted(p.rglob("*")):
            if child.is_file():
                _search_file(child)
    elif p.is_dir():
        for child in sorted(p.iterdir()):
            if child.is_file():
                _search_file(child)
    else:
        raise ToolError(f"Path not found: {path}")

    return json.dumps(results)


@beta_tool
def WebFetch(url: str, timeout: int = 30) -> str:
    """Fetch the content of a URL via HTTP GET and return the response body as text.

    Args:
        url: The URL to fetch. Must start with http:// or https://.
        timeout: Request timeout in seconds. Defaults to 30.
    """
    if not url.startswith(("http://", "https://")):
        raise ToolError(f"Invalid URL scheme (must be http or https): {url}")
    try:
        response = httpx.get(url, timeout=timeout, follow_redirects=True)
        response.raise_for_status()
        return response.text
    except httpx.HTTPStatusError as exc:
        raise ToolError(
            f"HTTP {exc.response.status_code} fetching {url}"
        ) from exc
    except httpx.RequestError as exc:
        raise ToolError(f"Network error fetching {url}: {exc}") from exc


@beta_tool
def TodoRead() -> str:
    """Read the current todo list from .todo.json in the working directory.

    Returns a JSON array of todo items.
    """
    todo_path = Path(".todo.json")
    if not todo_path.exists():
        return json.dumps([])
    return todo_path.read_text(encoding="utf-8")


@beta_tool
def TodoWrite(todos: str) -> str:
    """Write the todo list to .todo.json in the working directory.

    Args:
        todos: JSON-encoded array of todo items to persist.
    """
    try:
        parsed = json.loads(todos)
    except json.JSONDecodeError as exc:
        raise ToolError(f"Invalid JSON for todos: {exc}") from exc
    Path(".todo.json").write_text(json.dumps(parsed, indent=2), encoding="utf-8")
    return f"TodoWrite: saved {len(parsed)} items"


# Registry of all built-in tools, keyed by tool name
BUILTIN_TOOLS: dict[str, Any] = {
    "Read": Read,
    "Write": Write,
    "Bash": Bash,
    "Glob": Glob,
    "Grep": Grep,
    "WebFetch": WebFetch,
    "TodoRead": TodoRead,
    "TodoWrite": TodoWrite,
}
```

---

### File: `<output_dir>/tools/subagent.py`

```python
"""Infrastructure: factory that wraps an AgentRunner as a @beta_tool callable.

This enables the orchestrator to call subagents as if they were regular tools,
following the Claude SDK multi-agent delegation pattern.
"""
from __future__ import annotations

import re
from typing import TYPE_CHECKING, Callable

from anthropic import beta_tool

if TYPE_CHECKING:
    from ..agent import AgentRunner
    from ..config import AgentConfig


def build_subagent_tool(
    agent_config: "AgentConfig",
    agent_runner: "AgentRunner",
) -> Callable[..., str]:
    """Create a @beta_tool-decorated function that delegates to an AgentRunner.

    The generated tool is named `delegate_to_<sanitised_name>`, where the name
    is derived from agent_config.name with dots and hyphens replaced by underscores.

    Args:
        agent_config: Configuration of the subagent to wrap.
        agent_runner: The AgentRunner instance that will execute the task.

    Returns:
        A callable decorated with @beta_tool, ready to be passed to tool_runner.
    """
    safe_name = re.sub(r"[^a-zA-Z0-9_]", "_", agent_config.name)
    tool_name = f"delegate_to_{safe_name}"
    description = agent_config.description

    def _delegate(task: str) -> str:
        """Delegate a task to the subagent.

        Args:
            task: The natural-language task description or input for the subagent.
        """
        return agent_runner.run(task)

    # Apply @beta_tool to the function so the SDK can extract its schema.
    # We override __name__ and __doc__ so the decorator reads the right values.
    _delegate.__name__ = tool_name
    _delegate.__qualname__ = tool_name
    _delegate.__doc__ = (
        f"{description}\n\nArgs:\n    task: The task to delegate to this agent."
    )

    decorated: Callable[..., str] = beta_tool(_delegate)
    return decorated
```

---

### File: `<output_dir>/agent.py`

```python
"""Use case: run a single agent using the Claude SDK tool_runner.

Responsible for:
- Accepting an AgentConfig and a ToolRegistry
- Building the tool list for this specific agent
- Invoking client.beta.messages.tool_runner with the agent's instructions
- Returning the final text response
"""
from __future__ import annotations

from typing import Iterator

from anthropic import Anthropic

from .config import AgentConfig
from .tools.registry import ToolRegistry


class AgentRunner:
    """Runs a single agent via the Claude SDK agentic loop.

    Design note: AgentRunner is stateless per-call; the same instance
    can be used for multiple sequential run() calls safely.
    """

    def __init__(
        self,
        config: AgentConfig,
        client: Anthropic,
        tool_registry: ToolRegistry,
    ) -> None:
        """Initialise the runner.

        Args:
            config: The agent's immutable configuration.
            client: Anthropic SDK client instance.
            tool_registry: Registry providing the tool callables for this agent.
        """
        self._config = config
        self._client = client
        self._tool_registry = tool_registry

    @property
    def config(self) -> AgentConfig:
        """Read-only access to the agent configuration."""
        return self._config

    def run(self, user_message: str) -> str:
        """Run the agent with a user message and return the final text response.

        The method drives the full agentic loop: it creates a tool_runner,
        iterates until Claude stops calling tools, and returns the last
        text content block.

        Args:
            user_message: The task or question to send to the agent.

        Returns:
            Final text response from the agent. Empty string if no text content.
        """
        tools = self._tool_registry.build_for_agent(self._config)
        runner = self._client.beta.messages.tool_runner(
            model=self._config.model,
            max_tokens=8192,
            system=self._config.instructions,
            tools=tools,
            messages=[{"role": "user", "content": user_message}],
        )
        final = runner.until_done()
        for block in final.content:
            if hasattr(block, "text"):
                return block.text
        return ""

    def run_streaming(self, user_message: str) -> Iterator[str]:
        """Run the agent with streaming and yield text chunks as they arrive.

        Args:
            user_message: The task or question to send to the agent.

        Yields:
            Text chunks from the streaming response.
        """
        tools = self._tool_registry.build_for_agent(self._config)
        runner = self._client.beta.messages.tool_runner(
            model=self._config.model,
            max_tokens=8192,
            system=self._config.instructions,
            tools=tools,
            messages=[{"role": "user", "content": user_message}],
            stream=True,
        )
        for message_stream in runner:
            final_msg = message_stream.get_final_message()
            for block in final_msg.content:
                if hasattr(block, "text"):
                    yield block.text
```

---

### File: `<output_dir>/runner.py`

```python
"""Use case: orchestrate the multi-agent workflow.

Responsible for:
- Loading agents from the parse manifest
- Building the tool registry (builtins + subagent tools)
- Wiring subagent tools into the orchestrator's registry
- Delegating user tasks to the orchestrator agent
"""
from __future__ import annotations

import json
from pathlib import Path

from anthropic import Anthropic

from .agent import AgentRunner
from .config import AgentConfig, WorkflowConfig
from .tools.builtin import BUILTIN_TOOLS
from .tools.registry import ToolRegistry
from .tools.subagent import build_subagent_tool


class WorkflowError(Exception):
    """Raised when the workflow cannot be loaded or executed."""


class WorkflowRunner:
    """Orchestrates a multi-agent workflow loaded from a parse manifest.

    Dependency Inversion: depends on Anthropic client injected at construction,
    not imported globally.
    """

    def __init__(self, config: WorkflowConfig, client: Anthropic) -> None:
        """Initialise the runner with workflow config and SDK client.

        Args:
            config: Immutable workflow configuration.
            client: Anthropic SDK client (injected for testability).
        """
        self._config = config
        self._client = client
        self._agent_runners: dict[str, AgentRunner] = {}
        self._loaded = False

    def load(self) -> None:
        """Load all agents from the parse manifest and wire their tool registries.

        Must be called before run(). Idempotent — safe to call multiple times.

        Raises:
            WorkflowError: If the manifest is missing or malformed.
        """
        if self._loaded:
            return

        manifest_path = self._config.output_dir / "parse-manifest.json"
        if not manifest_path.exists():
            raise WorkflowError(
                f"Parse manifest not found: {manifest_path}. "
                "Run the parser phase first."
            )

        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise WorkflowError(f"Invalid parse manifest JSON: {exc}") from exc

        # Build AgentConfig objects from manifest
        agent_configs: list[AgentConfig] = [
            AgentConfig(
                name=a["name"],
                description=a["description"],
                model=a["model"],
                instructions=a["instructions"],
                tools=a.get("tools", []),
                readonly=a.get("readonly", True),
            )
            for a in manifest.get("agents", [])
        ]

        # Phase 1: create runners with builtin tools only
        base_registry = ToolRegistry(BUILTIN_TOOLS)
        for agent_config in agent_configs:
            runner = AgentRunner(agent_config, self._client, base_registry)
            self._agent_runners[agent_config.name] = runner

        # Phase 2: build subagent tools and register them in a per-agent registry
        for agent_config in agent_configs:
            agent_tools = dict(BUILTIN_TOOLS)
            for tool_name in agent_config.tools:
                if tool_name.startswith("delegate_to_"):
                    subagent_name = tool_name[len("delegate_to_"):]
                    # Resolve sanitised name back to agent name
                    target_runner = self._find_runner_by_tool_name(subagent_name)
                    if target_runner:
                        subagent_fn = build_subagent_tool(
                            target_runner.config, target_runner
                        )
                        agent_tools[tool_name] = subagent_fn

            wired_registry = ToolRegistry(agent_tools)
            wired_runner = AgentRunner(agent_config, self._client, wired_registry)
            self._agent_runners[agent_config.name] = wired_runner

        self._loaded = True

    def run(self, task: str) -> str:
        """Delegate a task to the orchestrator agent and return the final result.

        Args:
            task: Natural-language task description.

        Returns:
            Final text response from the orchestrator.

        Raises:
            WorkflowError: If load() has not been called or orchestrator is missing.
        """
        if not self._loaded:
            raise WorkflowError("WorkflowRunner.load() must be called before run()")

        orchestrator = self._agent_runners.get(self._config.orchestrator_name)
        if orchestrator is None:
            available = list(self._agent_runners.keys())
            raise WorkflowError(
                f"Orchestrator '{self._config.orchestrator_name}' not found. "
                f"Available agents: {available}"
            )

        return orchestrator.run(task)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _find_runner_by_tool_name(self, sanitised_name: str) -> AgentRunner | None:
        """Find an AgentRunner whose name matches the sanitised tool name.

        delegate_to_ names have dots/hyphens replaced with underscores.
        This method reverses that mapping to find the original agent.
        """
        import re
        pattern = re.sub(r"_+", r"[._-]+", re.escape(sanitised_name))
        for name, runner in self._agent_runners.items():
            if re.fullmatch(pattern, name, re.IGNORECASE):
                return runner
        # Fallback: try direct name match
        return self._agent_runners.get(sanitised_name)
```

---

### File: `<output_dir>/simulator.py`

```python
"""Infrastructure: WorkflowSimulator — a drop-in replacement for WorkflowRunner.

Allows running the full pipeline without real API calls, using pre-defined
mock responses. Ideal for functional tests and CI environments.

Liskov Substitution: WorkflowSimulator exposes the same public interface
as WorkflowRunner, so it can substitute it anywhere.
"""
from __future__ import annotations

from .config import WorkflowConfig


class WorkflowSimulator:
    """Simulates a multi-agent workflow using pre-defined mock responses.

    Attributes:
        call_log: Records all (agent_name, task) calls made during the session.
    """

    def __init__(
        self,
        config: WorkflowConfig,
        mock_responses: dict[str, str],
    ) -> None:
        """Initialise the simulator.

        Args:
            config: Immutable workflow configuration (used for orchestrator name).
            mock_responses: Mapping of agent_name → response text.
                            The orchestrator's entry is returned by run().
        """
        self._config = config
        self._mock_responses = mock_responses
        self.call_log: list[tuple[str, str]] = []

    def load(self) -> None:
        """No-op: the simulator requires no loading phase."""

    def run(self, task: str) -> str:
        """Return the mocked orchestrator response for the given task.

        Args:
            task: The task to simulate running.

        Returns:
            Mocked response for the orchestrator agent.

        Raises:
            KeyError: If no mock response is defined for the orchestrator.
        """
        return self.run_agent(self._config.orchestrator_name, task)

    def run_agent(self, agent_name: str, task: str) -> str:
        """Return the mocked response for a named agent.

        Args:
            agent_name: Name of the agent to simulate.
            task: The task passed to the agent (recorded in call_log).

        Returns:
            Mocked response string.

        Raises:
            KeyError: If no mock response is defined for agent_name.
        """
        self.call_log.append((agent_name, task))
        return self._mock_responses[agent_name]
```

---

### File: `<output_dir>/main.py`

```python
"""Interface layer: CLI entry point for the <workflow_name> Claude SDK workflow.

Commands:
    run      — Execute the full workflow via the orchestrator agent.
    simulate — Dry-run using WorkflowSimulator (no API calls).
    parse    — Parse agent markdown files and emit parse-manifest.json.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import click

from .config import WorkflowConfig
from .loader import AgentMarkdownLoader
from .runner import WorkflowError, WorkflowRunner
from .simulator import WorkflowSimulator


def _load_api_key() -> str:
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        click.echo(
            "ERROR: ANTHROPIC_API_KEY environment variable is not set.", err=True
        )
        sys.exit(1)
    return key


@click.group()
def cli() -> None:
    """<workflow_name> — Claude SDK multi-agent workflow runner."""


@cli.command()
@click.argument("workflow_name")
@click.option(
    "--agents-dir",
    default=None,
    help="Path to agents directory. Defaults to workflows/<workflow_name>/agents/.",
)
@click.option(
    "--output-dir",
    default=None,
    help="Path to generated source directory. Defaults to src/<workflow_name>/.",
)
@click.option(
    "--task",
    required=True,
    help="Task to run through the orchestrator.",
)
@click.option("--stream", is_flag=True, help="Enable streaming output.")
def run(
    workflow_name: str,
    agents_dir: str | None,
    output_dir: str | None,
    task: str,
    stream: bool,
) -> None:
    """Execute the workflow by delegating the task to the orchestrator agent."""
    api_key = _load_api_key()

    from anthropic import Anthropic

    resolved_agents_dir = Path(agents_dir or f"workflows/{workflow_name}/agents")
    resolved_output_dir = Path(output_dir or f"src/{workflow_name}")

    manifest_path = resolved_output_dir / "parse-manifest.json"
    if not manifest_path.exists():
        click.echo(
            f"ERROR: parse-manifest.json not found at {manifest_path}. "
            f"Run 'parse {workflow_name}' first.",
            err=True,
        )
        sys.exit(1)

    manifest = json.loads(manifest_path.read_text())
    orchestrator_name = manifest.get("orchestrator", f"{workflow_name}.orchestrator")

    config = WorkflowConfig(
        workflow_name=workflow_name,
        agents_dir=resolved_agents_dir,
        output_dir=resolved_output_dir,
        orchestrator_name=orchestrator_name,
    )

    client = Anthropic(api_key=api_key)
    runner = WorkflowRunner(config, client)

    try:
        runner.load()
        if stream:
            orch = runner._agent_runners.get(orchestrator_name)
            if orch:
                for chunk in orch.run_streaming(task):
                    click.echo(chunk, nl=False)
                click.echo()
        else:
            result = runner.run(task)
            click.echo(result)
    except WorkflowError as exc:
        click.echo(f"ERROR: {exc}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("workflow_name")
@click.option("--agents-dir", default=None)
@click.option("--output-dir", default=None)
@click.option("--task", required=True, help="Task to simulate.")
def simulate(
    workflow_name: str,
    agents_dir: str | None,
    output_dir: str | None,
    task: str,
) -> None:
    """Dry-run the workflow using WorkflowSimulator (no API calls)."""
    resolved_agents_dir = Path(agents_dir or f"workflows/{workflow_name}/agents")
    resolved_output_dir = Path(output_dir or f"src/{workflow_name}")

    manifest_path = resolved_output_dir / "parse-manifest.json"
    if not manifest_path.exists():
        click.echo(f"ERROR: manifest not found at {manifest_path}", err=True)
        sys.exit(1)

    manifest = json.loads(manifest_path.read_text())
    orchestrator_name = manifest.get("orchestrator", f"{workflow_name}.orchestrator")

    config = WorkflowConfig(
        workflow_name=workflow_name,
        agents_dir=resolved_agents_dir,
        output_dir=resolved_output_dir,
        orchestrator_name=orchestrator_name,
    )

    # Provide default mock responses for every agent in the manifest
    mock_responses = {
        a["name"]: f"[SIMULATED] {a['name']} completed task."
        for a in manifest.get("agents", [])
    }

    simulator = WorkflowSimulator(config, mock_responses)
    simulator.load()
    result = simulator.run(task)
    click.echo(result)
    click.echo(f"\nCall log: {simulator.call_log}")


@cli.command()
@click.argument("workflow_name")
@click.option("--agents-dir", default=None)
@click.option("--output-dir", default=None)
def parse(
    workflow_name: str,
    agents_dir: str | None,
    output_dir: str | None,
) -> None:
    """Parse agent markdown files and emit parse-manifest.json."""
    resolved_agents_dir = Path(agents_dir or f"workflows/{workflow_name}/agents")
    resolved_output_dir = Path(output_dir or f"src/{workflow_name}")

    if not resolved_agents_dir.exists():
        click.echo(f"ERROR: agents dir not found: {resolved_agents_dir}", err=True)
        sys.exit(1)

    loader = AgentMarkdownLoader()
    agents = loader.load_all(resolved_agents_dir)

    if not agents:
        click.echo(f"ERROR: No .md files found in {resolved_agents_dir}", err=True)
        sys.exit(1)

    orchestrator = loader.find_orchestrator(resolved_agents_dir, workflow_name)
    if orchestrator is None:
        click.echo(
            f"ERROR: No orchestrator found. "
            f"Expected: {resolved_agents_dir}/{workflow_name}.orchestrator.md",
            err=True,
        )
        sys.exit(1)

    from datetime import timezone, datetime

    manifest = {
        "workflow_name": workflow_name,
        "agents_dir": str(resolved_agents_dir),
        "orchestrator": orchestrator.name,
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "agents": [
            {
                "name": a.name,
                "description": a.description,
                "model": a.model,
                "tools": a.tools,
                "readonly": a.readonly,
                "instructions": a.instructions,
                "source_file": str(
                    next(resolved_agents_dir.glob("*.md"), Path("unknown"))
                ),
            }
            for a in agents
        ],
    }

    resolved_output_dir.mkdir(parents=True, exist_ok=True)
    out_path = resolved_output_dir / "parse-manifest.json"
    out_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    click.echo(f"Manifest written: {out_path}")
    click.echo(f"Agents: {len(agents)}, Orchestrator: {orchestrator.name}")


def main() -> None:
    """Package entry point."""
    cli()


if __name__ == "__main__":
    main()
```

---

### File: `pyproject.toml` (in project root, not `output_dir`)

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "<workflow_name>"
version = "0.1.0"
description = "Claude SDK multi-agent workflow wrapper for <workflow_name>"
requires-python = ">=3.12"
dependencies = [
    "anthropic>=0.96.0",
    "pyyaml>=6.0",
    "click>=8.0",
    "httpx>=0.27",
]

[project.scripts]
<workflow_name> = "<workflow_name>.main:main"

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-mock>=3.12",
    "pytest-cov>=5.0",
    "pytest-asyncio>=0.23",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=src/<workflow_name> --cov-report=term-missing"

[tool.coverage.run]
source = ["src/<workflow_name>"]
omit = ["*/deploy/*"]

[tool.coverage.report]
fail_under = 100
```

## Step 4 — Substitute Placeholders

After generating all file contents, replace every occurrence of `<workflow_name>` with the actual `workflow_name` value from the manifest.

## Step 5 — Verify Generated Files

After writing all files, run:
```bash
python -c "import ast; ast.parse(open('src/<workflow_name>/<file>.py').read()); print('OK')"
```
for each `.py` file to catch syntax errors. Report any syntax error immediately.

## Step 6 — Report

Print:
```
BUILD COMPLETE
Workflow: <workflow_name>
Files generated: <count>
  src/<workflow_name>/__init__.py
  src/<workflow_name>/config.py
  src/<workflow_name>/loader.py
  src/<workflow_name>/tools/__init__.py
  src/<workflow_name>/tools/registry.py
  src/<workflow_name>/tools/builtin.py
  src/<workflow_name>/tools/subagent.py
  src/<workflow_name>/agent.py
  src/<workflow_name>/runner.py
  src/<workflow_name>/simulator.py
  src/<workflow_name>/main.py
  pyproject.toml
```
