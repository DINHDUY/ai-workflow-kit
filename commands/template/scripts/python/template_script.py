#!/usr/bin/env python3
"""
template_script.py — Template helper script for AI agent commands.

Replace this module docstring and all TODO comments with your actual logic.

Usage:
    python template_script.py <input> [options]

Examples:
    python template_script.py path/to/input.txt
    python template_script.py path/to/input.txt -o docs/result.txt --verbose
    python template_script.py path/to/input.txt --dry-run
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


# ─── Argument parsing ─────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="template_script.py",
        description="TODO: Replace with a one-line description of what this script does.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s path/to/input.txt
  %(prog)s path/to/input.txt -o docs/result.txt
  %(prog)s path/to/input.txt --dry-run --verbose
        """,
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Path to the input file to process.",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="Output file path. Defaults to ./output/<input-stem><input-suffix>.",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        default=False,
        help="Enable verbose/debug output to stderr.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Preview actions without writing any files.",
    )
    parser.add_argument(
        "-f", "--force",
        action="store_true",
        default=False,
        help="Overwrite the output file if it already exists.",
    )
    return parser


# ─── Core logic ───────────────────────────────────────────────────────────────

def process(input_path: Path, verbose: bool) -> str:
    """
    TODO: Replace this function with your actual processing logic.

    Reads the input file and returns the processed content as a string.

    Args:
        input_path: Resolved path to the input file.
        verbose: If True, print debug lines to stderr.

    Returns:
        Processed content as a string.
    """
    if verbose:
        print(f"[DEBUG] Reading input: {input_path}", file=sys.stderr)

    content = input_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    if verbose:
        print(f"[DEBUG] Lines read: {len(lines)}", file=sys.stderr)

    # TODO: Replace this placeholder transformation with real logic.
    processed_lines = [f"Processed: {line}" for line in lines]

    if verbose:
        print(f"[DEBUG] Lines processed: {len(processed_lines)}", file=sys.stderr)

    return "\n".join(processed_lines) + "\n"


def resolve_output(input_path: Path, output_arg: Path | None) -> Path:
    """Return the resolved output path, creating parent directories as needed."""
    if output_arg is not None:
        return output_arg
    return Path("output") / input_path.name


# ─── Entry point ──────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    input_path: Path = args.input.resolve()
    output_path: Path = resolve_output(args.input, args.output)
    verbose: bool = args.verbose
    dry_run: bool = args.dry_run
    force: bool = args.force

    # ── Validate input ────────────────────────────────────────────────────────
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        return 1
    if not input_path.is_file():
        print(f"Error: Input path is not a file: {input_path}", file=sys.stderr)
        return 1

    # ── Dry run preview ───────────────────────────────────────────────────────
    if dry_run:
        line_count = len(input_path.read_text(encoding="utf-8").splitlines())
        print("[DRY RUN] No files will be written.\n")
        print(f"  Input:  {input_path}  ({line_count} lines, UTF-8)")
        print(f"  Output: {output_path}")
        print(f"  Mode:   {'verbose' if verbose else 'normal'}\n")
        print("Actions that would be taken:")
        print(f"  1. Read {input_path}")
        print(f"  2. Apply transformation ({line_count} lines)")
        print(f"  3. Write {output_path}")
        return 0

    # ── Overwrite guard ───────────────────────────────────────────────────────
    if output_path.exists() and not force:
        print(
            f"Error: Output file already exists: {output_path}\n"
            "Use --force to overwrite.",
            file=sys.stderr,
        )
        return 1
    if output_path.exists() and force and verbose:
        print(f"[WARN] Overwriting existing file: {output_path}", file=sys.stderr)

    # ── Process ───────────────────────────────────────────────────────────────
    try:
        result = process(input_path, verbose)
    except Exception as exc:  # noqa: BLE001
        print(f"Error: Failed to process input: {exc}", file=sys.stderr)
        return 2

    # ── Write output ──────────────────────────────────────────────────────────
    if verbose:
        print(f"[DEBUG] Writing output: {output_path}", file=sys.stderr)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(result, encoding="utf-8")

    line_count = len(result.splitlines())
    print(f"✓ Completed successfully.")
    print(f"Output written to: {output_path} ({line_count} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
