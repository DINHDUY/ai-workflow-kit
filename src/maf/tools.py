# tools.py
"""
Maps tool name strings (from agent frontmatter 'tools:' list) to MAF-compatible
Python callables for use with agent_framework.

The Next.js pipeline agents in .cursor/agents/ do not declare explicit tools —
they rely on Cursor's built-in file system access and the workflow orchestrator
for coordination. resolve_tools() therefore returns an empty list for this
pipeline but is kept here as an extension point.

To add a real tool:
  1. Define a Python function decorated with @tool (from agent_framework).
  2. Add it to TOOL_REGISTRY keyed by its frontmatter name.

Example:
    from agent_framework import tool

    @tool
    def web_search(query: str) -> str:
        ...

    TOOL_REGISTRY = {"WebSearch": web_search, ...}
"""
from typing import Callable

# ---------------------------------------------------------------------------
# Tool registry — maps frontmatter tool names → MAF callables
# Extend this dict when agents start declaring tools.
# ---------------------------------------------------------------------------

TOOL_REGISTRY: dict[str, Callable] = {
    # "Read":      read_file_tool,
    # "Write":     write_file_tool,
    # "Bash":      bash_tool,
    # "WebSearch": web_search_tool,
    # "WebFetch":  web_fetch_tool,
}


def resolve_tools(tool_names: list[str]) -> list[Callable]:
    """
    Resolve a list of tool name strings to their MAF callable implementations.

    Unrecognised names are skipped with a warning so the rest of the agent
    build does not fail.

    Args:
        tool_names: List of tool name strings from agent frontmatter.

    Returns:
        List of MAF-compatible callable tool objects (may be empty).
    """
    resolved: list[Callable] = []
    for name in tool_names:
        if name in TOOL_REGISTRY:
            resolved.append(TOOL_REGISTRY[name])
        else:
            if name:  # skip empty strings silently
                print(f"[WARN] tools.py: no implementation for tool '{name}' — skipping")
    return resolved
