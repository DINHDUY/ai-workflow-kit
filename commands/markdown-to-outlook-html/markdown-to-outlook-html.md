# Markdown to Outlook HTML

## Overview

Convert a Markdown file (`.md`) into Outlook-safe HTML that renders reliably in Outlook 2013–2021, Outlook 365 desktop, and Outlook.com. Uses a self-contained Python script with no external dependencies (standard library only). Includes a `--dry-run` mode.

## Scripts

The implementation lives in `scripts/python/`:

- **`md_to_outlook_html.py`** — CLI entry point. Run this script directly.
- **`md_to_outlook_html_lib.py`** — Core library (Markdown parser, Outlook-safe inline styles, HTML template). Imported by the CLI and reusable from other Python code.

## Steps

1. **Gather information**
   - Extract any details the user already provided (e.g., `/markdown-to-outlook-html report.md`)
   - Ask only for what is missing:
     - **Input file** — path to the `.md` file to convert
   - Optional overrides:
     - **Output file** — defaults to the same name with `.html` extension
     - **Title** — defaults to the first heading in the document or the filename

2. **Run the conversion**
   ```bash
   python scripts/python/md_to_outlook_html.py INPUT.md
   ```
   With options:
   ```bash
   python scripts/python/md_to_outlook_html.py report.md -o email-body.html --title "Weekly Report"
   ```
   Preview without writing files:
   ```bash
   python scripts/python/md_to_outlook_html.py report.md --dry-run
   ```

3. **Verify the result**
   - Confirm the success message: `Converted INPUT.md → OUTPUT.html (N lines)`
   - Optionally open the HTML file in a browser to preview
   - On failure, read the error output and suggest corrective action

## Outlook-Safe HTML Rules

The generated HTML follows these rules for maximum Outlook compatibility:

- Full HTML5 document with explicit `<!DOCTYPE html>`
- All CSS is **inline** — no `<style>` blocks or external stylesheets
- Web-safe font stack: `Arial, Helvetica, sans-serif`
- **Table-based** wrapper layout for consistent rendering
- Explicit `margin` and `padding` on every element
- Hex colour values only (no named colours, no `rgb()`)
- MSO conditional comments for Outlook-specific rendering fixes
- `<pre>` code blocks with `white-space: pre-wrap` for word wrapping
- Images with `border=0`, `display:block`

## Supported Markdown Features

| Feature | Syntax |
|---------|--------|
| Headings | `# H1` through `###### H6` |
| Bold | `**text**` or `__text__` |
| Italic | `*text*` or `_text_` |
| Bold + Italic | `***text***` |
| Inline code | `` `code` `` |
| Code blocks | Fenced with `` ``` `` |
| Links | `[text](url)` |
| Images | `![alt](url)` |
| Unordered lists | `- item` or `* item` |
| Ordered lists | `1. item` |
| Blockquotes | `> quote` |
| Horizontal rules | `---` or `***` |
| Tables | `| col | col |` |
| Strikethrough | `~~text~~` |

## CLI Reference

```
python scripts/python/md_to_outlook_html.py [-h] [-o OUTPUT] [--title TITLE]
                                             [--max-width MAX_WIDTH] [--dry-run]
                                             input

positional arguments:
  input                 path to the Markdown (.md) file to convert

options:
  -o, --output OUTPUT   output HTML file path (default: INPUT.html)
  --title TITLE         HTML document title (default: first heading or filename)
  --max-width MAX_WIDTH maximum content width in pixels (default: 800)
  --dry-run             show what would happen without writing any files
```

## Examples

### Convert a report

```
/markdown-to-outlook-html report.md
```

### Convert with custom title and output

```
/markdown-to-outlook-html notes.md to newsletter.html titled "Weekly Update"
```

### Preview (dry run)

```
/markdown-to-outlook-html meeting-notes.md with --dry-run
```

## Notes

- Uses only the Python standard library — no `pip install` needed
- Outlook uses Microsoft Word's rendering engine, which ignores most CSS; this script works around those limitations
- Output is a complete HTML document suitable for pasting into Outlook or embedding as an email body
- Exit code `0` on success, `1` on any error
