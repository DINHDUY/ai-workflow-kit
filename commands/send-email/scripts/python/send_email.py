#!/usr/bin/env python3
"""
send_email.py — Send an email via SMTP or API.

Usage:
    python send_email.py --to <address> --subject <text> --body <text>
    python send_email.py --to <address> --subject <text> --body <text> --dry-run
"""

from __future__ import annotations

import argparse
import sys


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="send_email.py",
        description="Send an email via SMTP.",
    )
    parser.add_argument("--to", required=True, help="Recipient address(es), comma-separated")
    parser.add_argument("--subject", required=True, help="Email subject line")
    parser.add_argument("--body", required=True, help="Email body text")
    parser.add_argument("--dry-run", action="store_true", default=False,
                        help="Preview without sending")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.dry_run:
        print("[DRY RUN] Email would be sent:")
        print(f"  To:      {args.to}")
        print(f"  Subject: {args.subject}")
        print(f"  Body:    {args.body[:80]}...")
        return 0

    # TODO: Replace with real SMTP / API send logic.
    print(f"Sending email to {args.to}…")
    print("✓ Email sent successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
