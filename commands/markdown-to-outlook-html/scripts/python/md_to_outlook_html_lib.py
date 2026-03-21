"""Convert Markdown to Outlook-safe HTML (stdlib only).

Outlook uses Microsoft Word's rendering engine which supports only a
limited subset of HTML and CSS.  This module produces HTML that renders
reliably in Outlook 2013-2021, Outlook 365 desktop, and Outlook.com
while still looking clean in other email clients.

Outlook-safe rules applied
--------------------------
* Full HTML5 document with explicit ``<!DOCTYPE html>``
* All CSS is **inline** — no ``<style>`` blocks or external sheets
* Web-safe font stack: ``Arial, Helvetica, sans-serif``
* Table-based wrapper layout for consistent width
* Explicit ``margin`` / ``padding`` on every element
* Hex colour values only (no named colours, no ``rgb()``)
* MSO conditional comments for Outlook-specific fixes
* ``<pre>`` code blocks with ``white-space: pre-wrap``
* Images with ``border=0``, ``display:block``
* Local images embedded as base64 data URIs (no external file links)

Typical usage::

    from md_to_outlook_html_lib import convert_file, ConvertOptions

    html = convert_file("report.md", "report.html")
"""

from __future__ import annotations

import base64
import html as _html
import logging
import re
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Literal

# MIME types for common image formats (used when embedding as base64)
_IMAGE_MIME_TYPES: dict[str, str] = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".svg": "image/svg+xml",
}

__all__ = ["ConvertOptions", "DEFAULT_OPTIONS", "convert", "convert_file", "format_summary"]
__version__ = "1.0.0"

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_HEX_COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")

_COLOR_FIELDS = (
    "text_color",
    "bg_color",
    "link_color",
    "code_bg",
    "code_border",
    "heading_color",
    "border_color",
    "blockquote_color",
    "blockquote_border",
    "blockquote_bg",
)


@dataclass(frozen=True)
class ConvertOptions:  # pylint: disable=too-many-instance-attributes
    """Options controlling the Markdown -> HTML conversion.

    All colour values must be 6-digit hex strings (e.g. ``#333333``).

    Raises:
        ValueError: If any colour value is not a valid hex string, or if
            ``max_width`` / ``font_size`` are out of range.
    """

    title: str = ""
    max_width: int = 800
    font_family: str = "Arial, Helvetica, sans-serif"
    font_size: int = 14
    text_color: str = "#333333"
    bg_color: str = "#ffffff"
    link_color: str = "#0563C1"
    code_bg: str = "#f5f5f5"
    code_border: str = "#e0e0e0"
    heading_color: str = "#1a1a1a"
    border_color: str = "#dddddd"
    blockquote_color: str = "#666666"
    blockquote_border: str = "#dddddd"
    blockquote_bg: str = "#f9f9f9"

    def __post_init__(self) -> None:
        for name in _COLOR_FIELDS:
            value = getattr(self, name)
            if not _HEX_COLOR_RE.match(value):
                raise ValueError(
                    f"{name!r} must be a 6-digit hex colour "
                    f"(e.g. '#333333'), got {value!r}",
                )
        if self.max_width <= 0:
            raise ValueError(f"max_width must be positive, got {self.max_width}")
        if not 8 <= self.font_size <= 72:
            raise ValueError(
                f"font_size must be between 8 and 72, got {self.font_size}",
            )


DEFAULT_OPTIONS = ConvertOptions()


# ---------------------------------------------------------------------------
# Inline styles (Outlook-safe)
# ---------------------------------------------------------------------------


def _build_styles(opts: ConvertOptions) -> dict[str, str]:
    """Build a dictionary of inline CSS style strings."""
    ff = opts.font_family
    fs = f"{opts.font_size}px"
    return {
        "body": f"margin:0;padding:0;background-color:{opts.bg_color};",
        "wrapper_table": (
            f"width:100%;background-color:{opts.bg_color};"
            "border-spacing:0;border-collapse:collapse;"
        ),
        "container": (
            f"width:100%;max-width:{opts.max_width}px;"
            f"font-family:{ff};font-size:{fs};"
            f"line-height:1.6;color:{opts.text_color};padding:20px;"
        ),
        "h1": (
            f"font-family:{ff};font-size:28px;font-weight:bold;"
            f"color:{opts.heading_color};margin:0 0 16px 0;line-height:1.3;"
            f"border-bottom:2px solid {opts.border_color};padding-bottom:8px;"
        ),
        "h2": (
            f"font-family:{ff};font-size:24px;font-weight:bold;"
            f"color:{opts.heading_color};margin:24px 0 12px 0;line-height:1.3;"
            f"border-bottom:1px solid {opts.border_color};padding-bottom:6px;"
        ),
        "h3": (
            f"font-family:{ff};font-size:20px;font-weight:bold;"
            f"color:{opts.heading_color};margin:20px 0 10px 0;line-height:1.3;"
        ),
        "h4": (
            f"font-family:{ff};font-size:16px;font-weight:bold;"
            f"color:{opts.heading_color};margin:16px 0 8px 0;line-height:1.3;"
        ),
        "h5": (
            f"font-family:{ff};font-size:{fs};font-weight:bold;"
            f"color:{opts.heading_color};margin:12px 0 6px 0;line-height:1.3;"
        ),
        "h6": (
            f"font-family:{ff};font-size:12px;font-weight:bold;"
            f"color:{opts.heading_color};margin:12px 0 6px 0;line-height:1.3;"
        ),
        "p": (
            f"font-family:{ff};font-size:{fs};"
            f"color:{opts.text_color};margin:0 0 12px 0;line-height:1.6;"
        ),
        "code_inline": (
            "font-family:Consolas,Monaco,'Courier New',monospace;"
            f"font-size:13px;background-color:{opts.code_bg};"
            f"padding:2px 6px;border:1px solid {opts.code_border};"
            "color:#c7254e;"
        ),
        "code_block": (
            "font-family:Consolas,Monaco,'Courier New',monospace;"
            f"font-size:13px;background-color:{opts.code_bg};"
            f"padding:12px 16px;border:1px solid {opts.code_border};"
            f"margin:0 0 12px 0;line-height:1.5;color:{opts.text_color};"
            "white-space:pre-wrap;word-wrap:break-word;display:block;"
        ),
        "blockquote": (
            f"margin:0 0 12px 0;padding:8px 16px;"
            f"border-left:4px solid {opts.blockquote_border};"
            f"background-color:{opts.blockquote_bg};"
            f"color:{opts.blockquote_color};font-style:italic;"
        ),
        "a": f"color:{opts.link_color};text-decoration:underline;",
        "hr": (
            f"border:0;border-top:1px solid {opts.border_color};margin:24px 0;"
        ),
        "ul": "margin:0 0 12px 0;padding-left:24px;",
        "ol": "margin:0 0 12px 0;padding-left:24px;",
        "li": (
            f"font-family:{ff};font-size:{fs};"
            f"color:{opts.text_color};margin:0 0 4px 0;line-height:1.6;"
        ),
        "img": "max-width:100%;height:auto;border:0;outline:none;",
        "table": (
            f"border-collapse:collapse;width:100%;margin:0 0 12px 0;"
            f"font-family:{ff};font-size:{fs};"
        ),
        "th": (
            f"border:1px solid {opts.border_color};padding:8px 12px;"
            f"text-align:left;font-weight:bold;background-color:{opts.code_bg};"
            f"color:{opts.text_color};"
        ),
        "td": (
            f"border:1px solid {opts.border_color};padding:8px 12px;"
            f"text-align:left;color:{opts.text_color};"
        ),
    }


# ---------------------------------------------------------------------------
# Inline element parsing
# ---------------------------------------------------------------------------

# Placeholder tokens avoid nested-match conflicts.  They are replaced in
# a second pass with final styled HTML.
# Placeholder delimiters — \x00 never appears in normal Markdown, so
# these tokens won't collide with bold (__) or italic (_) patterns.
_PH = "\x00"

_IMG_REPL = (
    _PH + r"IMG" + _PH + r"\2" + _PH + r"ALT" + _PH + r"\1"
    + _PH + r"ENDIMG" + _PH
)
_LINK_REPL = (
    _PH + r"LINK" + _PH + r"\2" + _PH + r"TEXT" + _PH + r"\1"
    + _PH + r"ENDLINK" + _PH
)

# Pre-compiled inline patterns (avoids re-compilation on every call).
_INLINE_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    # Images: ![alt](url)
    (re.compile(r"!\[([^\]]*)\]\(([^)]+)\)"), _IMG_REPL),
    # Links: [text](url)
    (re.compile(r"\[([^\]]+)\]\(([^)]+)\)"), _LINK_REPL),
    # Bold-italic: ***text*** or ___text___
    (re.compile(r"\*{3}(.+?)\*{3}"), r"<strong><em>\1</em></strong>"),
    (re.compile(r"_{3}(.+?)_{3}"), r"<strong><em>\1</em></strong>"),
    # Bold: **text** or __text__
    (re.compile(r"\*{2}(.+?)\*{2}"), r"<strong>\1</strong>"),
    (re.compile(r"_{2}(.+?)_{2}"), r"<strong>\1</strong>"),
    # Italic: *text* or _text_ (word-boundary aware for underscores)
    (re.compile(r"\*(.+?)\*"), r"<em>\1</em>"),
    (re.compile(r"(?<!\w)_(.+?)_(?!\w)"), r"<em>\1</em>"),
    # Inline code: `code` — placeholder to HTML-escape contents later
    (re.compile(r"`([^`]+)`"), _PH + r"CODE" + _PH + r"\1" + _PH + r"ENDCODE" + _PH),
    # Strikethrough: ~~text~~
    (re.compile(r"~~(.+?)~~"), r"<s>\1</s>"),
]

# Pre-compiled placeholder resolution patterns.
_RE_PH_CODE = re.compile(
    _PH + r"CODE" + _PH + r"(.+?)" + _PH + r"ENDCODE" + _PH,
)
_RE_PH_IMG = re.compile(
    _PH + r"IMG" + _PH + r"(.+?)" + _PH + r"ALT" + _PH + r"(.*?)"
    + _PH + r"ENDIMG" + _PH,
)
_RE_PH_LINK = re.compile(
    _PH + r"LINK" + _PH + r"(.+?)" + _PH + r"TEXT" + _PH + r"(.+?)"
    + _PH + r"ENDLINK" + _PH,
)


def _process_inline(text: str, styles: dict[str, str]) -> str:
    """Apply inline Markdown formatting to *text*."""
    # First pass: regex replacements → placeholders
    for pattern, replacement in _INLINE_PATTERNS:
        text = pattern.sub(replacement, text)

    # Second pass: resolve placeholders into styled HTML
    text = _RE_PH_CODE.sub(
        lambda m: (
            f'<code style="{styles["code_inline"]}">'
            f"{_html.escape(m.group(1))}</code>"
        ),
        text,
    )
    text = _RE_PH_IMG.sub(
        lambda m: (
            f'<img src="{_html.escape(m.group(1))}" '
            f'alt="{_html.escape(m.group(2))}" '
            f'style="{styles["img"]}" />'
        ),
        text,
    )
    text = _RE_PH_LINK.sub(
        lambda m: (
            f'<a href="{_html.escape(m.group(1))}" '
            f'style="{styles["a"]}">{_html.escape(m.group(2))}</a>'
        ),
        text,
    )
    return text


# ---------------------------------------------------------------------------
# Block-level parsing (state machine)
# ---------------------------------------------------------------------------

_RE_HEADING = re.compile(r"^(#{1,6})\s+(.+?)(?:\s+#+)?\s*$")
_RE_FENCE = re.compile(r"^(`{3,}|~{3,})(\w*)\s*$")
_RE_HR = re.compile(r"^(?:[-*_]\s*){3,}$")
_RE_UL = re.compile(r"^(\s*)[-*+]\s+(.+)$")
_RE_OL = re.compile(r"^(\s*)\d+[.)]\s+(.+)$")
_RE_BLOCKQUOTE = re.compile(r"^>\s?(.*)")
_RE_TABLE_ROW = re.compile(r"^\|(.+)\|$")
_RE_TABLE_SEP = re.compile(r"^\|[\s:]*-+[\s:]*(?:\|[\s:]*-+[\s:]*)*\|$")

# Type alias for list kind tracking.
_ListKind = Literal["ul", "ol", ""]


@dataclass
class _BlockParser:  # pylint: disable=too-many-instance-attributes
    """State machine that parses Markdown lines into HTML blocks.

    Call :meth:`feed` for each line, then :meth:`finish` to flush any
    remaining buffered content and retrieve the final HTML.
    """

    styles: dict[str, str]
    blocks: list[str] = field(default_factory=list)

    # ---- internal state ----
    _in_fence: bool = False
    _fence_marker: str = ""
    _fence_lines: list[str] = field(default_factory=list)
    _in_list: _ListKind = ""
    _list_items: list[str] = field(default_factory=list)
    _in_blockquote: bool = False
    _bq_lines: list[str] = field(default_factory=list)
    _in_table: bool = False
    _table_headers: list[str] = field(default_factory=list)
    _table_rows: list[list[str]] = field(default_factory=list)
    _para_lines: list[str] = field(default_factory=list)

    # -- flush helpers --

    def _flush_paragraph(self) -> None:
        if self._para_lines:
            content = _process_inline(
                " ".join(self._para_lines), self.styles,
            )
            self.blocks.append(
                f'<p style="{self.styles["p"]}">{content}</p>',
            )
            self._para_lines = []

    def _flush_list(self) -> None:
        if not self._list_items:
            return
        tag = self._in_list
        items_html = "\n".join(
            f'<li style="{self.styles["li"]}">'
            f"{_process_inline(item, self.styles)}</li>"
            for item in self._list_items
        )
        self.blocks.append(
            f'<{tag} style="{self.styles[tag]}">\n{items_html}\n</{tag}>',
        )
        self._list_items = []
        self._in_list = ""

    def _flush_blockquote(self) -> None:
        if not self._bq_lines:
            return
        content = _process_inline(" ".join(self._bq_lines), self.styles)
        self.blocks.append(
            f'<blockquote style="{self.styles["blockquote"]}">'
            f'<p style="margin:0;">{content}</p></blockquote>',
        )
        self._bq_lines = []
        self._in_blockquote = False

    def _flush_table(self) -> None:
        if not self._table_headers:
            return
        header_cells = "".join(
            f'<th style="{self.styles["th"]}">'
            f"{_process_inline(c.strip(), self.styles)}</th>"
            for c in self._table_headers
        )
        row_fragments: list[str] = []
        for row in self._table_rows:
            cells = "".join(
                f'<td style="{self.styles["td"]}">'
                f"{_process_inline(c.strip(), self.styles)}</td>"
                for c in row
            )
            row_fragments.append(f"<tr>{cells}</tr>")
        rows_html = "\n".join(row_fragments)
        self.blocks.append(
            f'<table style="{self.styles["table"]}">\n'
            f"<thead><tr>{header_cells}</tr></thead>\n"
            f"<tbody>\n{rows_html}\n</tbody>\n</table>",
        )
        self._table_headers = []
        self._table_rows = []
        self._in_table = False

    def _flush_all(self) -> None:
        """Flush every buffered block."""
        self._flush_paragraph()
        self._flush_list()
        self._flush_blockquote()
        self._flush_table()

    # -- block-type handlers (each returns True when the line is consumed) --

    def _handle_fence(self, line: str) -> bool:
        """Handle fenced code blocks."""
        fence_match = _RE_FENCE.match(line)
        if self._in_fence:
            if fence_match and fence_match.group(1)[0] == self._fence_marker[0]:
                code = _html.escape("\n".join(self._fence_lines))
                self.blocks.append(
                    f'<pre style="{self.styles["code_block"]}">'
                    f"<code>{code}</code></pre>",
                )
                self._in_fence = False
                self._fence_marker = ""
                self._fence_lines = []
            else:
                self._fence_lines.append(line)
            return True

        if fence_match:
            self._flush_all()
            self._in_fence = True
            self._fence_marker = fence_match.group(1)
            self._fence_lines = []
            return True

        return False

    def _handle_hr(self, line: str) -> bool:
        """Handle horizontal rules."""
        if _RE_HR.match(line.strip()):
            self._flush_all()
            self.blocks.append(f'<hr style="{self.styles["hr"]}" />')
            return True
        return False

    def _handle_heading(self, line: str) -> bool:
        """Handle ATX headings."""
        heading_match = _RE_HEADING.match(line)
        if heading_match:
            self._flush_all()
            level = len(heading_match.group(1))
            content = _process_inline(heading_match.group(2), self.styles)
            tag = f"h{level}"
            style = self.styles.get(tag, self.styles["p"])
            self.blocks.append(f'<{tag} style="{style}">{content}</{tag}>')
            return True
        return False

    def _handle_table(self, line: str) -> bool:
        """Handle table rows."""
        table_match = _RE_TABLE_ROW.match(line.strip())
        if table_match:
            cells = table_match.group(1).split("|")
            if self._in_table:
                if _RE_TABLE_SEP.match(line.strip()):
                    return True  # separator row — skip
                self._table_rows.append(cells)
            else:
                self._flush_all()
                self._in_table = True
                self._table_headers = cells
            return True

        if self._in_table:
            self._flush_table()
        return False

    def _handle_blockquote(self, line: str) -> bool:
        """Handle blockquote lines."""
        bq_match = _RE_BLOCKQUOTE.match(line)
        if bq_match:
            if not self._in_blockquote:
                self._flush_all()
                self._in_blockquote = True
            self._bq_lines.append(bq_match.group(1))
            return True

        if self._in_blockquote:
            self._flush_blockquote()
        return False

    def _handle_list(self, line: str) -> bool:
        """Handle ordered and unordered list items."""
        ul_match = _RE_UL.match(line)
        if ul_match:
            if self._in_list != "ul":
                self._flush_all()
                self._in_list = "ul"
            self._list_items.append(ul_match.group(2))
            return True

        ol_match = _RE_OL.match(line)
        if ol_match:
            if self._in_list != "ol":
                self._flush_all()
                self._in_list = "ol"
            self._list_items.append(ol_match.group(2))
            return True

        if self._in_list:
            self._flush_list()
        return False

    # -- main line processor --

    def feed(self, line: str) -> None:  # pylint: disable=too-many-return-statements
        """Process a single line of Markdown."""
        if self._handle_fence(line):
            return
        if self._handle_hr(line):
            return
        if self._handle_heading(line):
            return
        if self._handle_table(line):
            return
        if self._handle_blockquote(line):
            return
        if self._handle_list(line):
            return

        # Blank line → flush paragraph
        if not line.strip():
            self._flush_paragraph()
            return

        # Normal text → accumulate paragraph
        self._para_lines.append(line.strip())

    def finish(self) -> str:
        """Flush remaining content and return the combined HTML body."""
        self._flush_all()
        return "\n".join(self.blocks)


# ---------------------------------------------------------------------------
# HTML document template (Outlook-safe)
# ---------------------------------------------------------------------------

_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en" xmlns="http://www.w3.org/1999/xhtml" \
xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<meta http-equiv="X-UA-Compatible" content="IE=edge" />
<!--[if mso]>
<noscript>
<xml>
  <o:OfficeDocumentSettings>
    <o:PixelsPerInch>96</o:PixelsPerInch>
  </o:OfficeDocumentSettings>
</xml>
</noscript>
<![endif]-->
<title>{title}</title>
</head>
<body style="{body_style}">
<!--[if mso]>
<table role="presentation" cellspacing="0" cellpadding="0" border="0" \
width="100%"><tr><td>
<![endif]-->
<table role="presentation" cellspacing="0" cellpadding="0" border="0" \
width="100%" style="{wrapper_style}">
<tr>
<td align="center" style="padding:0;">
<table role="presentation" cellspacing="0" cellpadding="0" border="0" \
style="{container_style}">
<tr>
<td>
{content}
</td>
</tr>
</table>
</td>
</tr>
</table>
<!--[if mso]>
</td></tr></table>
<![endif]-->
</body>
</html>"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _embed_local_images(html: str, base_path: Path) -> str:
    """Replace local image src attributes with base64 data URIs.

    Paths starting with http://, https://, or data: are left unchanged.
    Relative paths are resolved against *base_path* (typically the
    directory of the source Markdown file).
    """
    pattern = re.compile(r'src=(["\'])([^"\']+)\1')

    def replacer(match: re.Match[str]) -> str:
        quote, src = match.group(1), match.group(2)
        if src.startswith(("http://", "https://", "data:")):
            return match.group(0)
        resolved = (base_path / src).resolve()
        if not resolved.is_file():
            logger.warning("Image file not found: %s", resolved)
            return match.group(0)
        try:
            data = resolved.read_bytes()
            b64 = base64.b64encode(data).decode("ascii")
            mime = _IMAGE_MIME_TYPES.get(
                resolved.suffix.lower(), "application/octet-stream",
            )
            return f'src={quote}data:{mime};base64,{b64}{quote}'
        except OSError as exc:
            logger.warning("Could not read image %s: %s", resolved, exc)
            return match.group(0)

    return pattern.sub(replacer, html)


def _detect_title(markdown: str, fallback: str) -> str:
    """Extract title from the first ATX heading, or return *fallback*."""
    for line in markdown.splitlines():
        match = _RE_HEADING.match(line)
        if match:
            return match.group(2)
    return fallback


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def convert(markdown: str, options: ConvertOptions | None = None) -> str:
    """Convert a Markdown string to an Outlook-safe HTML document.

    Args:
        markdown: The Markdown source text.
        options: Conversion options (uses defaults when *None*).

    Returns:
        A complete HTML document string.
    """
    opts = options or DEFAULT_OPTIONS
    styles = _build_styles(opts)

    parser = _BlockParser(styles=styles)
    for line in markdown.splitlines():
        parser.feed(line)
    body_html = parser.finish()

    return _TEMPLATE.format(
        title=_html.escape(opts.title) if opts.title else "Document",
        body_style=styles["body"],
        wrapper_style=styles["wrapper_table"],
        container_style=styles["container"],
        content=body_html,
    )


def convert_file(
    src: str | Path,
    dst: str | Path | None = None,
    *,
    options: ConvertOptions | None = None,
) -> str:
    """Read a Markdown file and write (or return) Outlook-safe HTML.

    Args:
        src: Path to the ``.md`` file.
        dst: Path to write the HTML output.  When *None* the HTML is
             returned but not written to disk.
        options: Conversion options.

    Returns:
        The generated HTML string.

    Raises:
        FileNotFoundError: If *src* does not exist.
        PermissionError: If *src* cannot be read or *dst* cannot be written.
    """
    src = Path(src)
    logger.info("Reading Markdown source: %s", src)
    markdown = src.read_text(encoding="utf-8")

    # Auto-detect title from first heading or filename
    opts = options or DEFAULT_OPTIONS
    if not opts.title:
        title = _detect_title(markdown, fallback=src.stem)
        opts = replace(opts, title=title)

    html_output = convert(markdown, opts)
    html_output = _embed_local_images(html_output, src.parent)

    if dst is not None:
        dst = Path(dst)
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(html_output, encoding="utf-8")
        logger.info("Wrote HTML output: %s (%d bytes)", dst, len(html_output))

    return html_output


def format_summary(src: str | Path, dst: str | Path | None = None) -> str:
    """Return a dry-run summary without performing any conversion.

    Shows what *would* happen: source file, destination, and size
    estimates.
    """
    src = Path(src)
    if not src.exists():
        return f"[dry-run] Source file not found: {src}"

    md_text = src.read_text(encoding="utf-8")
    line_count = len(md_text.splitlines())
    char_count = len(md_text)
    dst_display = Path(dst) if dst else src.with_suffix(".html")
    title = _detect_title(md_text, fallback=src.stem)

    lines = [
        "[dry-run] Markdown -> Outlook-safe HTML conversion",
        f"  Source : {src} ({line_count} lines, {char_count:,} chars)",
        f"  Output : {dst_display}",
        f"  Title  : {title}",
        "  Mode   : No files will be written",
    ]
    return "\n".join(lines)
