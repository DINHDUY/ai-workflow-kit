# DOCX to Markdown

## Overview

Convert a Microsoft Word (.docx) document to Markdown (.md) format. Uses a Python script located in `commands/docx-to-markdown/` that supports headings, text formatting (bold, italic), lists, hyperlinks, and embedded image extraction. Outputs GitHub Flavored Markdown (GFM).

## Scripts

The implementation lives in `commands/docx-to-markdown/`:

- **`docx_to_markdown_cli.py`** — CLI entry point. Run this script directly.
- **`docx_to_markdown/`** — Core package (config, DOCX extraction, element conversion, image handling, Markdown writing). Imported by the CLI.

## Steps

1. **Gather information**
   - Extract any details the user already provided (e.g., `/docx-to-markdown report.docx` or `/docx-to-markdown report.docx to output.md`)
   - Ask only for what is missing:
     - **Input file** — path to the `.docx` file to convert
   - Optional parameters (use defaults if not specified):
     - **Output file** — path for the `.md` file (default: same name/location as input with `.md` extension)
     - **Image directory** — where to save extracted images (default: `<document_name>/` next to output)
     - **Extract images** — whether to extract embedded images (default: yes)

2. **Ensure dependencies are installed**
   - The script requires the `python-docx` package (>= 0.8.11)
   - Check if it is installed:
     ```bash
     python -c "import docx; print(docx.__version__)"
     ```
   - If not installed, install it:
     ```bash
     pip install python-docx>=0.8.11
     ```

3. **Run the conversion**
   ```bash
   python commands/docx-to-markdown/docx_to_markdown.py <input.docx> -o <output.md>
   ```
   With image extraction to a custom directory:
   ```bash
   python commands/docx-to-markdown/docx_to_markdown.py <input.docx> -o <output.md> --image-dir assets/images
   ```
   Without image extraction:
   ```bash
   python commands/docx-to-markdown/docx_to_markdown.py <input.docx> -o <output.md> --no-images
   ```

4. **Verify result**
   - Confirm the success message: `✓ Conversion successful!`
   - On failure, re-run with `-v` for verbose diagnostics and suggest corrective action
   - If the output file was created, read the first ~30 lines to confirm it looks correct

## Command Line Options

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `input` | Yes | — | Path to the input `.docx` file |
| `-o`, `--output` | No | `<input>.md` | Path for the output `.md` file |
| `--image-dir` | No | `<document_name>/` | Directory for extracted images (relative paths in Markdown) |
| `--no-images` | No | `false` | Disable image extraction |
| `-v`, `--verbose` | No | `false` | Enable verbose/debug output |

## Examples

### Basic conversion

```
/docx-to-markdown report.docx
```

### Specify output path

```
/docx-to-markdown report.docx to docs/report.md
```

### Disable image extraction

```
/docx-to-markdown report.docx with no images
```

## Notes

- Requires Python 3.11+ and the `python-docx` package
- Supported: headings (H1-H6), bold, italic, ordered/unordered lists, hyperlinks, embedded images
- Not supported: text colors, underline, page breaks, comments, track changes, text boxes, headers/footers
- Output is always UTF-8 encoded GitHub Flavored Markdown
- Image paths in Markdown are relative to the output file
- Exit code `0` on success, `1` on any error
