"""Tests for maf.tools — tool implementations and registry."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Helpers — inject a minimal agent_framework stub before importing maf.tools
# ---------------------------------------------------------------------------

def _ensure_af_stub(monkeypatch):
    """Register a minimal agent_framework stub with a passthrough @tool decorator."""
    if "agent_framework" not in sys.modules:
        af = ModuleType("agent_framework")

        def _tool(fn):
            fn._is_tool = True
            return fn

        af.tool = _tool
        monkeypatch.setitem(sys.modules, "agent_framework", af)


# ---------------------------------------------------------------------------
# Import tools module (after patching)
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _stub_af(monkeypatch):
    _ensure_af_stub(monkeypatch)
    monkeypatch.delitem(sys.modules, "maf.tools", raising=False)
    yield


# ---------------------------------------------------------------------------
# read_file
# ---------------------------------------------------------------------------

class TestReadFile:
    def test_reads_existing_file(self, tmp_path: Path):
        f = tmp_path / "hello.txt"
        f.write_text("hello world", encoding="utf-8")
        from maf.tools import read_file
        assert read_file(str(f)) == "hello world"

    def test_raises_on_missing(self, tmp_path: Path):
        from maf.tools import read_file
        with pytest.raises(FileNotFoundError):
            read_file(str(tmp_path / "nope.txt"))


# ---------------------------------------------------------------------------
# write_file
# ---------------------------------------------------------------------------

class TestWriteFile:
    def test_writes_and_returns_confirmation(self, tmp_path: Path):
        from maf.tools import write_file
        out = tmp_path / "out.txt"
        result = write_file(str(out), "new content")
        assert out.read_text(encoding="utf-8") == "new content"
        assert "bytes" in result

    def test_creates_parent_dirs(self, tmp_path: Path):
        from maf.tools import write_file
        out = tmp_path / "deep" / "nested" / "file.txt"
        write_file(str(out), "data")
        assert out.exists()


# ---------------------------------------------------------------------------
# edit_file
# ---------------------------------------------------------------------------

class TestEditFile:
    def test_replaces_first_occurrence(self, tmp_path: Path):
        from maf.tools import edit_file
        f = tmp_path / "edit_me.txt"
        f.write_text("foo bar foo", encoding="utf-8")
        result = edit_file(str(f), "foo", "baz")
        assert f.read_text(encoding="utf-8") == "baz bar foo"
        assert "1 occurrence" in result

    def test_raises_when_old_string_absent(self, tmp_path: Path):
        from maf.tools import edit_file
        f = tmp_path / "no_match.txt"
        f.write_text("hello", encoding="utf-8")
        with pytest.raises(ValueError, match="not found"):
            edit_file(str(f), "missing", "replacement")


# ---------------------------------------------------------------------------
# grep
# ---------------------------------------------------------------------------

class TestGrep:
    def test_finds_matching_lines(self, tmp_path: Path):
        from maf.tools import grep
        f = tmp_path / "sample.py"
        f.write_text("def foo():\n    pass\ndef bar():\n    foo()\n", encoding="utf-8")
        result = grep("def ", str(tmp_path))
        assert "def foo" in result
        assert "def bar" in result

    def test_no_matches_returns_empty(self, tmp_path: Path):
        from maf.tools import grep
        (tmp_path / "empty.txt").write_text("nothing here", encoding="utf-8")
        result = grep("ZZZNOMATCH", str(tmp_path))
        assert result == ""

    def test_non_recursive(self, tmp_path: Path):
        from maf.tools import grep
        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "nested.txt").write_text("find me", encoding="utf-8")
        (tmp_path / "top.txt").write_text("also find me", encoding="utf-8")
        result_recursive = grep("find me", str(tmp_path), recursive=True)
        result_non_recursive = grep("find me", str(tmp_path), recursive=False)
        assert "nested.txt" in result_recursive
        assert "nested.txt" not in result_non_recursive
        assert "top.txt" in result_recursive

    def test_oserror_reading_file_is_skipped(self, tmp_path: Path, monkeypatch):
        """Files that raise OSError when read are silently skipped (tools.py:97-98)."""
        from maf.tools import grep
        from pathlib import Path as _Path
        import maf.tools as tools_mod

        f = tmp_path / "problem.txt"
        f.write_text("find me here", encoding="utf-8")

        original_read_text = _Path.read_text

        def _raise_on_problem(self, *args, **kwargs):
            if self.name == "problem.txt":
                raise OSError("permission denied")
            return original_read_text(self, *args, **kwargs)

        monkeypatch.setattr(_Path, "read_text", _raise_on_problem)
        result = grep("find me", str(tmp_path))
        # The file raised OSError — should be silently skipped, returning empty
        assert "find me here" not in result


# ---------------------------------------------------------------------------
# glob_files
# ---------------------------------------------------------------------------

class TestGlobFiles:
    def test_finds_matching_files(self, tmp_path: Path):
        from maf.tools import glob_files
        (tmp_path / "a.py").write_text("", encoding="utf-8")
        (tmp_path / "b.py").write_text("", encoding="utf-8")
        (tmp_path / "c.txt").write_text("", encoding="utf-8")
        result = glob_files("*.py", str(tmp_path))
        assert "a.py" in result
        assert "b.py" in result
        assert "c.txt" not in result

    def test_no_matches(self, tmp_path: Path):
        from maf.tools import glob_files
        result = glob_files("*.xyz", str(tmp_path))
        assert result == "(no matches)"


# ---------------------------------------------------------------------------
# list_dir
# ---------------------------------------------------------------------------

class TestListDir:
    def test_lists_contents(self, tmp_path: Path):
        from maf.tools import list_dir
        (tmp_path / "file.txt").write_text("x", encoding="utf-8")
        (tmp_path / "subdir").mkdir()
        result = list_dir(str(tmp_path))
        assert "file.txt" in result
        assert "subdir/" in result

    def test_empty_dir(self, tmp_path: Path):
        from maf.tools import list_dir
        empty = tmp_path / "empty"
        empty.mkdir()
        assert list_dir(str(empty)) == "(empty)"

    def test_raises_on_non_dir(self, tmp_path: Path):
        from maf.tools import list_dir
        f = tmp_path / "file.txt"
        f.write_text("hi", encoding="utf-8")
        with pytest.raises(NotADirectoryError):
            list_dir(str(f))


# ---------------------------------------------------------------------------
# bash
# ---------------------------------------------------------------------------

class TestBash:
    def test_captures_stdout(self):
        from maf.tools import bash
        result = bash("echo hello_world")
        assert "hello_world" in result

    def test_captures_stderr(self):
        from maf.tools import bash
        result = bash("echo error_msg >&2")
        assert "error_msg" in result

    def test_timeout_raises(self):
        from maf.tools import bash
        with pytest.raises(subprocess.TimeoutExpired):
            bash("sleep 10", timeout=1)

    def test_truncates_large_output(self):
        from maf.tools import bash
        # Generate > 8KB output
        result = bash("python3 -c \"print('x' * 10000)\"", timeout=10)
        assert "truncated" in result

    def test_no_output(self):
        from maf.tools import bash
        result = bash("true")
        assert result == "(no output)"


# ---------------------------------------------------------------------------
# web_fetch
# ---------------------------------------------------------------------------

class TestWebFetch:
    def test_rejects_non_http_schemes(self):
        from maf.tools import web_fetch
        with pytest.raises(ValueError, match="http"):
            web_fetch("ftp://example.com/file")

    def test_rejects_file_scheme(self):
        from maf.tools import web_fetch
        with pytest.raises(ValueError):
            web_fetch("file:///etc/passwd")

    def test_fetches_url(self, monkeypatch):
        from maf.tools import web_fetch
        fake_response = MagicMock()
        fake_response.read.return_value = b"<html>test content</html>"
        fake_response.__enter__ = lambda s: s
        fake_response.__exit__ = MagicMock(return_value=False)

        monkeypatch.setattr("maf.tools.urlopen", lambda url, timeout: fake_response)
        result = web_fetch("https://example.com/")
        assert "test content" in result


# ---------------------------------------------------------------------------
# TOOL_REGISTRY and resolve_tools
# ---------------------------------------------------------------------------

class TestToolRegistry:
    def test_registry_has_all_expected_keys(self):
        from maf.tools import TOOL_REGISTRY
        expected = {"Read", "Write", "Edit", "MultiEdit", "Grep", "Glob", "LS", "Bash", "WebFetch"}
        assert expected.issubset(set(TOOL_REGISTRY.keys()))

    def test_multi_edit_aliased_to_edit(self):
        from maf.tools import TOOL_REGISTRY, edit_file
        assert TOOL_REGISTRY["MultiEdit"] is edit_file

    def test_read_aliased_to_read_file(self):
        from maf.tools import TOOL_REGISTRY, read_file
        assert TOOL_REGISTRY["Read"] is read_file


class TestResolveTools:
    def test_resolves_known_names(self):
        from maf.tools import resolve_tools
        tools = resolve_tools(["Read", "Write", "Bash"])
        assert len(tools) == 3

    def test_skips_unknown_names(self, capsys):
        from maf.tools import resolve_tools
        tools = resolve_tools(["Read", "FancyTool"])
        assert len(tools) == 1
        captured = capsys.readouterr()
        assert "FancyTool" in captured.out

    def test_empty_list(self):
        from maf.tools import resolve_tools
        assert resolve_tools([]) == []

    def test_skips_empty_strings(self):
        from maf.tools import resolve_tools
        result = resolve_tools(["", "Read", ""])
        assert len(result) == 1
