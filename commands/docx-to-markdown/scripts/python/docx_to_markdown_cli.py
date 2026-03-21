#!/usr/bin/env python3
"""
DOCX to Markdown Converter - Command Line Interface

A production-ready script to convert Microsoft Word (.docx) documents to
Markdown format with support for essential formatting, images, and links.

Usage:
    python docx_to_markdown.py input.docx [-o output.md] [--image-dir images]
    python docx_to_markdown.py input.docx --no-images
    python docx_to_markdown.py input.docx -v  # verbose output

Features:
    - Converts headings, paragraphs, bold, italic, lists, and links
    - Extracts embedded images to a separate directory
    - GitHub Flavored Markdown output
    - Comprehensive error handling and logging
    - Production-ready with SOLID principles

Author: AI Alpha Forge
Version: 1.0.0
"""

import argparse
import logging
import sys
from pathlib import Path

def _safe_symbols() -> tuple[str, str]:
    """Return (check, cross) symbols safe for stdout/stderr (e.g. Windows cp1252)."""
    utf_encodings = ("utf-8", "utf-16", "utf-32", "cp65001")
    for stream in (sys.stdout, sys.stderr):
        enc = (getattr(stream, "encoding", None) or "").lower()
        if enc not in utf_encodings:
            return ("[OK] ", "")
    return ("\u2713 ", "\u2717 ")


_CHECK, _CROSS = _safe_symbols()

from docx_to_markdown import (
    ConversionConfig,
    ConversionError,
    InvalidDocxError,
    convert_docx_to_markdown,
    setup_logging,
    __version__
)

logger = logging.getLogger(__name__)


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments.
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description='Convert Microsoft Word (.docx) documents to Markdown format.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic conversion
  python docx_to_markdown.py document.docx
  
  # Specify output file
  python docx_to_markdown.py document.docx -o output.md
  
  # Custom image directory
  python docx_to_markdown.py document.docx --image-dir assets/images
  
  # Disable image extraction
  python docx_to_markdown.py document.docx --no-images
  
  # Verbose output for debugging
  python docx_to_markdown.py document.docx -v

Supported Features:
  - Headings (H1-H6)
  - Text formatting (bold, italic, combined)
  - Paragraphs with proper spacing
  - Ordered and unordered lists
  - Hyperlinks
  - Embedded images (extracted separately)

Output Format:
  GitHub Flavored Markdown (GFM)
        """
    )
    
    # Required arguments
    parser.add_argument(
        'input',
        type=Path,
        help='Path to the input .docx file'
    )
    
    # Optional arguments
    parser.add_argument(
        '-o', '--output',
        type=Path,
        help='Path for the output .md file (default: <input>.md)'
    )
    
    parser.add_argument(
        '--image-dir',
        type=str,
        default=None,
        help='Directory for extracted images (default: <document_name>/ next to output)'
    )
    
    parser.add_argument(
        '--no-images',
        action='store_true',
        help='Disable image extraction'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output for debugging'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )
    
    return parser.parse_args()


def validate_input_file(input_path: Path) -> None:
    """Validate that the input file exists and has the correct extension.
    
    Args:
        input_path: Path to the input file
        
    Raises:
        SystemExit: If validation fails
    """
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        print(f"Error: Input file does not exist: {input_path}", file=sys.stderr)
        sys.exit(1)
    
    if not input_path.is_file():
        logger.error(f"Input path is not a file: {input_path}")
        print(f"Error: Input path is not a file: {input_path}", file=sys.stderr)
        sys.exit(1)
    
    if input_path.suffix.lower() != '.docx':
        logger.warning(f"Input file does not have .docx extension: {input_path}")
        print(f"Warning: Input file does not have .docx extension: {input_path}", file=sys.stderr)


def main() -> int:
    """Main entry point for the CLI application.
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    # Parse arguments
    args = parse_arguments()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(log_level)
    
    logger.info(f"DOCX to Markdown Converter v{__version__}")
    logger.info(f"Input file: {args.input}")
    
    # Validate input
    validate_input_file(args.input)
    
    # Determine output path
    output_path = args.output if args.output else args.input.with_suffix('.md')
    logger.info(f"Output file: {output_path}")

    # Default image dir: same path as output, folder named after document
    image_dir = args.image_dir
    if image_dir is None:
        image_dir = str(output_path.parent / output_path.stem)

    # Create configuration
    config = ConversionConfig(
        extract_images=not args.no_images,
        image_dir=image_dir,
        output_encoding='utf-8',
        markdown_flavor='gfm'
    )
    
    try:
        # Validate configuration
        config.validate()
        
        if config.extract_images:
            logger.info(f"Image extraction enabled. Images will be saved to: {config.image_dir}/")
        else:
            logger.info("Image extraction disabled")
        
        # Perform conversion
        logger.info("Starting conversion...")
        convert_docx_to_markdown(
            input_path=args.input,
            output_path=output_path,
            config=config
        )
        
        # Success!
        print(f"\n{_CHECK}Conversion successful!")
        print(f"  Output: {output_path}")
        if config.extract_images:
            image_dir = Path(config.image_dir)
            if image_dir.exists():
                image_count = len(list(image_dir.glob('*')))
                if image_count > 0:
                    print(f"  Images: {image_count} image(s) extracted to {config.image_dir}/")
        
        return 0
    
    except InvalidDocxError as e:
        logger.error(f"Invalid DOCX file: {e}")
        print(f"\n{_CROSS}Error: {e.message}", file=sys.stderr)
        print("\nPlease ensure the input file is a valid Microsoft Word (.docx) document.", file=sys.stderr)
        return 1
    
    except ConversionError as e:
        logger.error(f"Conversion error: {e}")
        print(f"\n{_CROSS}Conversion failed: {str(e)}", file=sys.stderr)
        return 1
    
    except PermissionError as e:
        logger.error(f"Permission error: {e}")
        print(f"\n{_CROSS}Permission denied: {str(e)}", file=sys.stderr)
        print("\nPlease check that you have write permissions for the output location.", file=sys.stderr)
        return 1
    
    except KeyboardInterrupt:
        logger.info("Conversion interrupted by user")
        print("\n\nConversion interrupted by user.", file=sys.stderr)
        return 1
    
    except Exception as e:
        logger.exception("Unexpected error")
        print(f"\n{_CROSS}Unexpected error: {str(e)}", file=sys.stderr)
        if args.verbose:
            import traceback
            print("\nFull traceback:", file=sys.stderr)
            traceback.print_exc()
        else:
            print("Run with -v for detailed error information.", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
