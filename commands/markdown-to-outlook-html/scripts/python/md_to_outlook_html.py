#!/usr/bin/env python3
"""CLI for converting Markdown files to Outlook-safe HTML.

This is a thin wrapper around :mod:`md_to_outlook_html_lib`.  All
conversion logic lives in the library so it can be reused
programmatically.

Usage:
    python md_to_outlook_html.py README.md
    python md_to_outlook_html.py report.md -o report.html
    python md_to_outlook_html.py notes.md --dry-run
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from md_to_outlook_html_lib import ConvertOptions, convert_file, format_summary


def _build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser."""
    parser = argparse.ArgumentParser(
        description="Convert Markdown to Outlook-safe HTML.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python md_to_outlook_html.py README.md\n"
            "  python md_to_outlook_html.py report.md -o email-body.html\n"
            "  python md_to_outlook_html.py doc.md --title 'Weekly Report'\n"
            "  python md_to_outlook_html.py notes.md --dry-run\n"
        ),
    )
    parser.add_argument(
        "input",
        help="path to the Markdown (.md) file to convert",
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="output HTML file path (default: INPUT with .html extension)",
    )
    parser.add_argument(
        "--title",
        default=None,
        help="HTML document title (default: first heading or filename)",
    )
    parser.add_argument(
        "--max-width",
        type=int,
        default=800,
        help="maximum content width in pixels (default: 800)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="show what would happen without writing any files",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point.  Returns 0 on success, 1 on error."""
    args = _build_parser().parse_args(argv)

    src = Path(args.input)
    if not src.exists():
        print(f"Error: file not found: {src}", file=sys.stderr)
        return 1

    dst = Path(args.output) if args.output else src.with_suffix(".html")

    # --- Dry run ---
    if args.dry_run:
        print(format_summary(src, dst))
        return 0

    # --- Convert ---
    options = ConvertOptions(
        title=args.title or "",
        max_width=args.max_width,
    )
    try:
        html_output = convert_file(src, dst, options=options)
        line_count = len(html_output.splitlines())
        print(f"Converted {src} -> {dst} ({line_count} lines)")
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
