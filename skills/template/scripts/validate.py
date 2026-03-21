#!/usr/bin/env python3
"""Validation script for the skill.

This script demonstrates best practices for skill validation scripts.
Scripts should be self-contained, include helpful error messages,
and handle edge cases gracefully.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def validate(target: Path) -> bool:
    """Validate the target path or resource.
    
    Args:
        target: Path to validate
        
    Returns:
        True if validation passes, False otherwise
    """
    if not target.exists():
        print(f"Error: Target '{target}' does not exist.", file=sys.stderr)
        return False
    
    # Add your validation logic here
    print(f"Validating: {target}")
    
    # Example validation checks
    # - Check file format
    # - Verify required fields
    # - Validate configurations
    
    print("Validation passed.")
    return True


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate resources for the skill.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s ./path/to/resource
  %(prog)s --verbose ./config.json
        """,
    )
    parser.add_argument(
        "target",
        type=Path,
        help="Path to the resource to validate",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output",
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        print(f"Target: {args.target}")
    
    success = validate(args.target)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
