# docx-to-markdown

Convert a Microsoft Word (`.docx`) file to GitHub Flavored Markdown (`.md`), with optional image extraction.

## When to use

- You have a `.docx` document and need it as Markdown (e.g., for a wiki, docs site, or Git repo).
- You want to preserve headings, bold/italic, lists, links, and embedded images.

## Requirements

Python 3.11+ and `python-docx`:

```bash
pip install python-docx
```

## Usage

```bash
python scripts/python/docx_to_markdown_cli.py <input.docx> [options]
```

| Option | Default | Description |
|---|---|---|
| `-o`, `--output` | `<input>.md` | Output `.md` file path |
| `--image-dir` | `<document_name>/` | Directory for extracted images |
| `--no-images` | — | Skip image extraction |
| `-v`, `--verbose` | — | Debug output |

## Examples

```bash
# Basic — output next to the input file
python scripts/python/docx_to_markdown_cli.py report.docx

# Custom output path
python scripts/python/docx_to_markdown_cli.py report.docx -o docs/report.md

# Custom image folder
python scripts/python/docx_to_markdown_cli.py report.docx -o docs/report.md --image-dir docs/assets

# Skip images
python scripts/python/docx_to_markdown_cli.py report.docx --no-images

# Verbose (useful when troubleshooting)
python scripts/python/docx_to_markdown_cli.py report.docx -v
```

## What's supported

| Supported | Not supported |
|---|---|
| Headings (H1–H6) | Text colors / underline |
| Bold, italic | Comments / track changes |
| Ordered & unordered lists | Text boxes |
| Hyperlinks | Headers / footers |
| Embedded images | Page breaks |

## Cursor command

Use the `/docx-to-markdown` slash command in Cursor chat to trigger this conversion without running the script manually.

```
/docx-to-markdown report.docx
/docx-to-markdown report.docx to docs/report.md
/docx-to-markdown report.docx with no images
```

## How-to Get This Command

For **Cursor**:

```bash
uvx --from git+https://itadoprd01.panagora.com/Research/training/_git/ai-agent-skills add-commands docx-to-markdown --output .cursor/commands
```

