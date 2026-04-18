"""Tests for maf.parser — agent file parsing and registry building."""
from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from maf.parser import (
    CURSOR_READONLY_DEFAULT_TOOLS,
    build_registry,
    detect_platform,
    find_project_root,
    load_agents,
    load_global_instructions,
)


# ---------------------------------------------------------------------------
# detect_platform
# ---------------------------------------------------------------------------

class TestDetectPlatform:
    def test_claude(self):
        assert detect_platform("/home/user/.claude/agents") == "claude"

    def test_cursor(self):
        assert detect_platform("/project/.cursor/agents") == "cursor"

    def test_copilot_copilot(self):
        assert detect_platform("/project/.copilot/agents") == "copilot"

    def test_copilot_github(self):
        assert detect_platform("/project/.github/copilot/agents") == "copilot"

    def test_generic(self):
        assert detect_platform("/project/workflows/nextjs/agents") == "generic"

    def test_generic_custom(self):
        assert detect_platform("my-custom-dir") == "generic"


# ---------------------------------------------------------------------------
# find_project_root
# ---------------------------------------------------------------------------

class TestFindProjectRoot:
    def test_finds_git_root(self, tmp_path: Path):
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        agents_dir = tmp_path / "workflows" / "agents"
        agents_dir.mkdir(parents=True)
        root = find_project_root(str(agents_dir))
        assert root == tmp_path

    def test_fallback_two_levels_up(self, tmp_path: Path):
        # No .git — falls back two levels
        agents_dir = tmp_path / "a" / "b" / "agents"
        agents_dir.mkdir(parents=True)
        root = find_project_root(str(agents_dir))
        # Should be two levels above agents_dir
        assert root == tmp_path / "a"


# ---------------------------------------------------------------------------
# load_global_instructions
# ---------------------------------------------------------------------------

class TestLoadGlobalInstructions:
    def test_explicit_path_plain_text(self, tmp_path: Path):
        f = tmp_path / "GLOBAL.md"
        f.write_text("global instructions text", encoding="utf-8")
        result = load_global_instructions("generic", explicit_path=str(f))
        assert result == "global instructions text"

    def test_explicit_path_with_frontmatter(self, tmp_path: Path):
        f = tmp_path / "GLOBAL.md"
        f.write_text("---\ntitle: test\n---\nglobal from frontmatter", encoding="utf-8")
        result = load_global_instructions("generic", explicit_path=str(f))
        assert result == "global from frontmatter"

    def test_explicit_path_missing(self, tmp_path: Path):
        result = load_global_instructions("generic", explicit_path=str(tmp_path / "missing.md"))
        assert result is None

    def test_claude_md(self, tmp_path: Path):
        (tmp_path / "CLAUDE.md").write_text("claude instructions", encoding="utf-8")
        result = load_global_instructions("claude", project_root=tmp_path)
        assert result == "claude instructions"

    def test_cursorrules(self, tmp_path: Path):
        (tmp_path / ".cursorrules").write_text("cursor rules", encoding="utf-8")
        result = load_global_instructions("cursor", project_root=tmp_path)
        assert result == "cursor rules"

    def test_copilot_instructions(self, tmp_path: Path):
        gh = tmp_path / ".github"
        gh.mkdir()
        (gh / "copilot-instructions.md").write_text("copilot instructions", encoding="utf-8")
        result = load_global_instructions("copilot", project_root=tmp_path)
        assert result == "copilot instructions"

    def test_generic_agents_md(self, tmp_path: Path):
        (tmp_path / "AGENTS.md").write_text("generic agents instructions", encoding="utf-8")
        result = load_global_instructions("generic", project_root=tmp_path)
        assert result == "generic agents instructions"

    def test_generic_fallback_agent_md(self, tmp_path: Path):
        # No AGENTS.md — falls back to AGENT.md
        (tmp_path / "AGENT.md").write_text("single agent instructions", encoding="utf-8")
        result = load_global_instructions("generic", project_root=tmp_path)
        assert result == "single agent instructions"

    def test_no_file_returns_none(self, tmp_path: Path):
        result = load_global_instructions("claude", project_root=tmp_path)
        assert result is None

    def test_none_project_root_returns_none(self):
        result = load_global_instructions("generic", project_root=None)
        assert result is None

    def test_explicit_path_frontmatter_exception_falls_back_to_read_text(
        self, tmp_path: Path, monkeypatch
    ):
        """When frontmatter.load raises on an explicit path, fall back to read_text."""
        import frontmatter as fm_mod
        from maf import parser as parser_mod

        f = tmp_path / "GLOBAL.md"
        f.write_text("plain fallback text", encoding="utf-8")

        original_load = fm_mod.load

        def _raise_on_path(path):
            if str(path) == str(f):
                raise ValueError("bad frontmatter")
            return original_load(path)

        monkeypatch.setattr(parser_mod.frontmatter, "load", _raise_on_path)
        result = load_global_instructions("generic", explicit_path=str(f))
        assert result == "plain fallback text"

    def test_candidate_frontmatter_exception_uses_read_text(
        self, tmp_path: Path, monkeypatch
    ):
        """When frontmatter.load raises for a candidate file, fall back to read_text."""
        import frontmatter as fm_mod
        from maf import parser as parser_mod

        (tmp_path / "AGENTS.md").write_text("raw fallback notes", encoding="utf-8")

        original_load = fm_mod.load

        def _raise(path):
            p = str(path)
            if p.endswith("AGENTS.md"):
                raise ValueError("bad frontmatter")
            return original_load(path)

        monkeypatch.setattr(parser_mod.frontmatter, "load", _raise)
        result = load_global_instructions("generic", project_root=tmp_path)
        assert result == "raw fallback notes"

    def test_candidate_empty_frontmatter_uses_read_text(self, tmp_path: Path):
        """When frontmatter body is empty, fall back to read_text (line 112)."""
        # A file with frontmatter only and no body — post.content.strip() is empty
        (tmp_path / "AGENTS.md").write_text(
            "---\ntitle: no body\n---\n", encoding="utf-8"
        )
        result = load_global_instructions("generic", project_root=tmp_path)
        # read_text fallback returns the raw file content including frontmatter markers
        assert result is not None
        assert "title" in result


# ---------------------------------------------------------------------------
# load_agents
# ---------------------------------------------------------------------------

class TestLoadAgents:
    def test_loads_three_valid_agents(self, tmp_agents_dir: Path):
        agents = load_agents(str(tmp_agents_dir))
        assert len(agents) == 3
        assert "sample.orchestrator" in agents
        assert "sample.worker" in agents
        assert "sample.analyzer" in agents

    def test_agent_fields(self, tmp_agents_dir: Path):
        agents = load_agents(str(tmp_agents_dir))
        orch = agents["sample.orchestrator"]
        assert orch["name"] == "sample.orchestrator"
        assert "Coordinates" in orch["description"]
        assert isinstance(orch["tools"], list)
        assert orch["model"] == "sonnet"
        assert "orchestrator" in orch["instructions"].lower()
        assert orch["source_file"].endswith(".md")
        assert orch["readonly"] is False

    def test_worker_tools(self, tmp_agents_dir: Path):
        agents = load_agents(str(tmp_agents_dir))
        assert agents["sample.worker"]["tools"] == ["Read", "Write", "Bash"]

    def test_analyzer_readonly(self, tmp_agents_dir: Path):
        agents = load_agents(str(tmp_agents_dir))
        assert agents["sample.analyzer"]["readonly"] is True

    def test_skips_no_name_agent(self, tmp_agents_dir_with_noname: Path, capsys):
        agents = load_agents(str(tmp_agents_dir_with_noname))
        # noname.md has no 'name' field — should be skipped
        assert len(agents) == 3
        captured = capsys.readouterr()
        assert "no 'name'" in captured.out

    def test_raises_on_missing_dir(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            load_agents(str(tmp_path / "nonexistent"))

    def test_cursor_readonly_default_tools(self, tmp_path: Path):
        """Cursor readonly agents with no tools get CURSOR_READONLY_DEFAULT_TOOLS."""
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()
        (agents_dir / "readonly.md").write_text(
            "---\nname: my.agent\ndescription: test\nreadonly: true\ntools: []\n---\nDo stuff.",
            encoding="utf-8",
        )
        agents = load_agents(str(agents_dir), platform="cursor")
        assert agents["my.agent"]["tools"] == list(CURSOR_READONLY_DEFAULT_TOOLS)

    def test_malformed_frontmatter_skipped(self, tmp_path: Path, capsys):
        """Files with malformed frontmatter are skipped with a warning."""
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()
        # Write a valid agent first so we don't hit "No valid agents found"
        (agents_dir / "valid.md").write_text(
            "---\nname: good.agent\ndescription: ok\ntools: []\n---\nBody.",
            encoding="utf-8",
        )
        # Write a file that causes frontmatter.load to raise
        bad_file = agents_dir / "bad.md"
        bad_file.write_text("---\n: invalid: yaml: [\n---\nBody.", encoding="utf-8")
        import frontmatter as fm_mod
        from maf import parser as parser_mod

        original_load = fm_mod.load

        call_count = {"n": 0}

        def _raise_on_bad(path):
            if str(path).endswith("bad.md"):
                raise ValueError("malformed yaml")
            return original_load(path)

        import unittest.mock as _mock

        with _mock.patch.object(parser_mod.frontmatter, "load", side_effect=_raise_on_bad):
            agents = load_agents(str(agents_dir))

        assert "good.agent" in agents
        assert len(agents) == 1
        captured = capsys.readouterr()
        assert "malformed frontmatter" in captured.out.lower()

    def test_non_list_tools_converted(self, tmp_path: Path):
        """When tools is not a list (e.g. a string), it is converted to a list."""
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()
        # 'tools' as a plain string (rare but possible)
        (agents_dir / "agent.md").write_text(
            "---\nname: my.agent\ndescription: d\ntools: Read\n---\nBody.",
            encoding="utf-8",
        )
        agents = load_agents(str(agents_dir))
        assert isinstance(agents["my.agent"]["tools"], list)

    def test_duplicate_name_warning(self, tmp_path: Path, capsys):
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()
        for suffix in ("a", "b"):
            (agents_dir / f"dup_{suffix}.md").write_text(
                f"---\nname: dup.agent\ndescription: d\ntools: []\n---\nBody {suffix}.",
                encoding="utf-8",
            )
        agents = load_agents(str(agents_dir))
        assert "dup.agent" in agents
        captured = capsys.readouterr()
        assert "Duplicate" in captured.out

    def test_unknown_tools_warning(self, tmp_path: Path, capsys):
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()
        (agents_dir / "agent.md").write_text(
            "---\nname: my.agent\ndescription: d\ntools: [UnknownTool]\n---\nBody.",
            encoding="utf-8",
        )
        load_agents(str(agents_dir))
        captured = capsys.readouterr()
        assert "unknown tools" in captured.out.lower()


# ---------------------------------------------------------------------------
# build_registry
# ---------------------------------------------------------------------------

class TestBuildRegistry:
    def test_returns_expected_keys(self, tmp_agents_dir: Path):
        reg = build_registry(str(tmp_agents_dir))
        assert "agents" in reg
        assert "global_instructions" in reg
        assert "platform" in reg

    def test_platform_inferred(self, tmp_agents_dir: Path):
        reg = build_registry(str(tmp_agents_dir))
        assert reg["platform"] == "generic"

    def test_platform_overridden(self, tmp_agents_dir: Path):
        reg = build_registry(str(tmp_agents_dir), platform="cursor")
        assert reg["platform"] == "cursor"

    def test_raises_on_empty_dir(self, tmp_path: Path):
        empty = tmp_path / "empty_agents"
        empty.mkdir()
        with pytest.raises(ValueError, match="No valid agents found"):
            build_registry(str(empty))

    def test_global_instructions_loaded(self, tmp_agents_dir: Path):
        # find_project_root walks up to the nearest .git dir; create one here
        git_dir = tmp_agents_dir.parent / ".git"
        git_dir.mkdir()
        (tmp_agents_dir.parent / "AGENTS.md").write_text("project-wide notes", encoding="utf-8")
        reg = build_registry(str(tmp_agents_dir))
        assert reg["global_instructions"] == "project-wide notes"

    def test_explicit_global_instructions(self, tmp_agents_dir: Path, tmp_path: Path):
        gi = tmp_path / "custom_global.md"
        gi.write_text("explicit global notes", encoding="utf-8")
        reg = build_registry(str(tmp_agents_dir), global_instructions_path=str(gi))
        assert reg["global_instructions"] == "explicit global notes"

    def test_agents_count(self, tmp_agents_dir: Path):
        reg = build_registry(str(tmp_agents_dir))
        assert len(reg["agents"]) == 3
