# parser.py
"""
Parses agent *.md files from any platform into a structured agent registry.

Supports:
  - .claude/agents   (Claude Code)
  - .cursor/agents   (Cursor)
  - .copilot/agents  (GitHub Copilot)
  - any custom path  (generic)

Each registry entry contains: name, description, tools, model, instructions,
source_file, readonly, platform.
"""
from pathlib import Path
from typing import Dict, Optional

import frontmatter

KNOWN_TOOLS = {
    "Read", "Write", "Edit", "MultiEdit",
    "Grep", "Glob", "LS",
    "Bash", "Computer",
    "WebSearch", "WebFetch",
    "Task", "TodoRead", "TodoWrite",
    "NotebookRead", "NotebookEdit",
}

# Default tools for Cursor agents that are readonly:true but declare no tools
CURSOR_READONLY_DEFAULT_TOOLS = ["Read", "Glob", "Grep", "LS"]


# ---------------------------------------------------------------------------
# Platform detection
# ---------------------------------------------------------------------------

def detect_platform(agents_dir: str) -> str:
    """
    Infer the source platform from the agents directory path.
    Returns one of: 'claude', 'cursor', 'copilot', 'generic'.
    """
    path = str(agents_dir).lower().replace("\\", "/")
    if ".claude/agents" in path:
        return "claude"
    if ".cursor/agents" in path:
        return "cursor"
    if ".copilot/agents" in path or ".github/copilot" in path:
        return "copilot"
    return "generic"


def find_project_root(agents_dir: str) -> Path:
    """
    Walk up from agents_dir to find the project root (directory containing .git).
    Falls back to two levels up if .git is not found.
    """
    p = Path(agents_dir).resolve()
    for ancestor in [p, *p.parents]:
        if (ancestor / ".git").exists():
            return ancestor
    return p.parent.parent


# ---------------------------------------------------------------------------
# Global instructions loading
# ---------------------------------------------------------------------------

def load_global_instructions(
    platform: str,
    project_root: Optional[Path] = None,
    explicit_path: Optional[str] = None,
) -> Optional[str]:
    """
    Load the platform-specific global instruction file.

    Resolution order:
      1. explicit_path (if provided)
      2. Platform default relative to project_root:
           claude  → CLAUDE.md
           cursor  → .cursorrules
           copilot → .github/copilot-instructions.md
           generic → AGENTS.md, then AGENT.md

    Returns None if no file is found.
    """
    if explicit_path:
        p = Path(explicit_path)
        if p.exists():
            try:
                post = frontmatter.load(p)
                return post.content.strip() or None
            except Exception:
                return p.read_text(encoding="utf-8").strip() or None
        return None

    if project_root is None:
        return None

    candidates: dict = {
        "claude":  [project_root / "CLAUDE.md"],
        "cursor":  [project_root / ".cursorrules"],
        "copilot": [project_root / ".github" / "copilot-instructions.md"],
        "generic": [project_root / "AGENTS.md", project_root / "AGENT.md"],
    }
    for candidate in candidates.get(platform, []):
        if candidate.exists():
            try:
                post = frontmatter.load(candidate)
                text = post.content.strip()
            except Exception:
                text = ""
            if not text:
                text = candidate.read_text(encoding="utf-8").strip()
            return text or None

    return None


# ---------------------------------------------------------------------------
# Agent loading
# ---------------------------------------------------------------------------

def load_agents(
    agents_dir: str,
    platform: Optional[str] = None,
) -> Dict[str, dict]:
    """
    Parse all *.md files in agents_dir into an agent registry dict.

    Works with .claude/agents, .cursor/agents, .copilot/agents, or any custom path.

    Returns:
        {
            "agent-name": {
                "name": str,
                "description": str,
                "tools": list[str],
                "model": str | None,
                "instructions": str,
                "source_file": str,
                "readonly": bool,
            },
            ...
        }
    """
    if platform is None:
        platform = detect_platform(agents_dir)

    agents_path = Path(agents_dir)
    if not agents_path.exists():
        raise FileNotFoundError(f"Agents directory not found: {agents_dir}")

    agents: Dict[str, dict] = {}

    for md_file in sorted(agents_path.glob("*.md")):
        try:
            post = frontmatter.load(md_file)
        except Exception as exc:
            print(f"[WARN] Skipping {md_file.name} — malformed frontmatter: {exc}")
            continue

        name = post.metadata.get("name")
        if not name:
            print(f"[WARN] Skipping {md_file.name} — no 'name' in frontmatter")
            continue

        if name in agents:
            print(
                f"[WARN] Duplicate agent name '{name}' — "
                f"{md_file.name} overwrites {agents[name]['source_file']}"
            )

        readonly = bool(post.metadata.get("readonly", False))
        tools: list = post.metadata.get("tools", [])
        if not isinstance(tools, list):
            tools = list(tools) if tools else []

        # Cursor readonly agents with no explicit tools default to read-only tool set
        if platform == "cursor" and readonly and not tools:
            tools = list(CURSOR_READONLY_DEFAULT_TOOLS)
            print(f"[INFO] {name}: readonly=true with no tools — defaulting to {tools}")

        unknown = set(tools) - KNOWN_TOOLS
        if unknown:
            print(f"[WARN] {name}: unknown tools {unknown} — will be mapped as stubs")

        agents[name] = {
            "name": name,
            "description": post.metadata.get("description", ""),
            "tools": tools,
            "model": post.metadata.get("model"),
            "instructions": post.content.strip(),
            "source_file": str(md_file),
            "readonly": readonly,
        }

    return agents


# ---------------------------------------------------------------------------
# Registry builder (primary public API)
# ---------------------------------------------------------------------------

def build_registry(
    agents_dir: str,
    platform: Optional[str] = None,
    global_instructions_path: Optional[str] = None,
) -> dict:
    """
    Build the full registry used by downstream MAF agents (agents.py, workflow.py).

    Args:
        agents_dir:               Path to the agents directory (any platform or custom path).
        platform:                 Override platform detection:
                                  'claude', 'cursor', 'copilot', 'generic'.
        global_instructions_path: Explicit path to global instructions file;
                                  auto-detected if None.

    Returns:
        {
            "agents": { name: agent_data, ... },
            "global_instructions": str | None,
            "platform": str,
        }

    Raises:
        FileNotFoundError: agents_dir does not exist.
        ValueError:        No valid agents found in agents_dir.
    """
    if platform is None:
        platform = detect_platform(agents_dir)

    agents = load_agents(agents_dir, platform)
    project_root = find_project_root(agents_dir)
    global_instructions = load_global_instructions(platform, project_root, global_instructions_path)

    print(f"[INFO] Platform:    {platform}")
    print(f"[INFO] Agents dir:  {agents_dir}")
    print(f"[INFO] Loaded {len(agents)} agent(s)")
    if global_instructions:
        print(f"[INFO] Global instructions: {len(global_instructions)} chars")
    else:
        print(f"[INFO] No global instructions found for platform '{platform}'")

    if not agents:
        raise ValueError(
            f"No valid agents found in {agents_dir}. "
            "Ensure each file has YAML frontmatter with a 'name' field."
        )

    return {
        "agents": agents,
        "global_instructions": global_instructions,
        "platform": platform,
    }
