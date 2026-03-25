# agents.py
"""
Constructs Microsoft Agent Framework Agent objects from a parsed agent registry.

Supports any agent source:
  - .cursor/agents  (Cursor)
  - .claude/agents  (Claude Code)
  - .copilot/agents (GitHub Copilot)
  - any custom path (generic)

Public API:
  create_ms_agent(agent_data, global_instructions) → Agent
  build_ms_agents(agents_dir, platform, global_instructions_path) → dict[str, Agent]
  ms_agents  — singleton dict auto-detected from common platform locations
"""
import os
from pathlib import Path
from typing import Optional

from agent_framework import Agent
from maf.client import client
from maf.parser import build_registry
from maf.tools import resolve_tools

# ---------------------------------------------------------------------------
# Model mapping — Cursor/Claude model tier names → Azure OpenAI deployments
# ---------------------------------------------------------------------------

MODEL_MAP: dict[str | None, str] = {
    "opus":    os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o"),
    "sonnet":  os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o"),
    "haiku":   os.environ.get("AZURE_OPENAI_FAST_DEPLOYMENT", "gpt-4o-mini"),
    "fast":    os.environ.get("AZURE_OPENAI_FAST_DEPLOYMENT", "gpt-4o-mini"),
    "default": os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o"),
    None:      os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o"),
}


def get_deployment(model: Optional[str]) -> str:
    """Map a model tier name to the corresponding Azure OpenAI deployment name."""
    return MODEL_MAP.get(model, MODEL_MAP[None])


# ---------------------------------------------------------------------------
# Instructions helpers
# ---------------------------------------------------------------------------

def build_instructions(
    agent_data: dict,
    global_instructions: Optional[str],
    prefix_description: bool = True,
) -> str:
    """
    Compose the full instructions string for an MAF agent.

    Strategy:
      1. Optionally prepend the agent's description as a role statement.
      2. Inject global instructions (from .cursorrules, CLAUDE.md, etc.)
         as a 'Global Context' section.
      3. Append the full body of the original agent *.md.
    """
    parts: list[str] = []

    if prefix_description and agent_data.get("description"):
        parts.append(f"# Role\n{agent_data['description']}\n")

    if global_instructions:
        parts.append(f"# Global Context (applies to all agents)\n{global_instructions}\n")

    parts.append(agent_data["instructions"])

    return "\n\n".join(parts).strip()


def _validate_instructions(name: str, instructions: str) -> bool:
    """Warn about suspiciously short or very long instruction strings."""
    if len(instructions) < 50:
        print(
            f"[WARN] {name}: very short instructions ({len(instructions)} chars) "
            "— agent may be ineffective"
        )
        return False
    if len(instructions) > 100_000:
        print(
            f"[WARN] {name}: very long instructions ({len(instructions)} chars) "
            "— may exceed context window"
        )
    return True


# ---------------------------------------------------------------------------
# Agent factory
# ---------------------------------------------------------------------------

def create_ms_agent(
    agent_data: dict,
    global_instructions: Optional[str] = None,
) -> Agent:
    """
    Create a single MAF Agent from one parsed agent registry entry.

    Args:
        agent_data:          Dict produced by parser.build_registry() for one agent.
        global_instructions: Shared instructions injected into every agent
                             (loaded from .cursorrules, CLAUDE.md, etc.).

    Returns:
        A configured agent_framework.Agent instance.
    """
    instructions = build_instructions(agent_data, global_instructions)
    _validate_instructions(agent_data["name"], instructions)

    tools = resolve_tools(agent_data.get("tools", []))
    deployment = get_deployment(agent_data.get("model"))

    agent = client.as_agent(
        name=agent_data["name"],
        instructions=instructions,
        description=agent_data.get("description") or None,
        tools=tools,
        model=deployment,
    )
    return agent


# ---------------------------------------------------------------------------
# Bulk builder
# ---------------------------------------------------------------------------

def build_ms_agents(
    agents_dir: Optional[str] = None,
    platform: Optional[str] = None,
    global_instructions_path: Optional[str] = None,
) -> dict[str, Agent]:
    """
    Parse agent files and return a dict of {name: Agent}.

    Args:
        agents_dir:               Path to agents directory (any platform or custom path).
                                  If None, auto-detects from common locations in priority order:
                                  .cursor/agents → .claude/agents → .copilot/agents → .github/agents
        platform:                 Override platform detection: 'claude', 'cursor', 'copilot', 'generic'.
        global_instructions_path: Explicit path to global instructions file; auto-detected if None.
    """
    if agents_dir is None:
        for candidate in [".cursor/agents", ".claude/agents", ".copilot/agents", ".github/agents"]:
            if Path(candidate).exists():
                agents_dir = candidate
                print(f"[INFO] Auto-detected agents dir: {agents_dir}")
                break
        else:
            raise FileNotFoundError(
                "No agents directory found. Pass agents_dir= explicitly or create one of: "
                ".cursor/agents, .claude/agents, .copilot/agents"
            )

    registry = build_registry(agents_dir, platform, global_instructions_path)
    global_instructions = registry["global_instructions"]
    agents_data = registry["agents"]

    ms_agents_dict: dict[str, Agent] = {}
    for name, data in agents_data.items():
        agent = create_ms_agent(data, global_instructions)
        ms_agents_dict[name] = agent
        resolved = resolve_tools(data.get("tools", []))
        tool_names = [fn.__name__ for fn in resolved] if resolved else []
        print(f"[INFO] Built agent: {name}  model={get_deployment(data.get('model'))}  tools={tool_names}")

    print(f"\n[INFO] Total agents built: {len(ms_agents_dict)}")
    return ms_agents_dict


# ---------------------------------------------------------------------------
# Singleton — auto-detects agents dir from common platform locations.
# Use build_ms_agents(agents_dir="...") when you need an explicit path.
# ---------------------------------------------------------------------------

ms_agents: dict[str, Agent] = build_ms_agents()
