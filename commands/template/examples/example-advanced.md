# Example: Advanced Usage

This example shows a fully-specified invocation with custom output path, verbose logging, and a dry run preview followed by the real execution.

## Input

**User invocation:**
```
/command-name path/to/input.txt --output docs/result.txt --verbose
```

**Input file (`path/to/input.txt`):**
```
Line 1: First item
Line 2: Second item with special characters: <>&"
Line 3: Unicode content: café, naïve, résumé
```

## Step 1: Dry Run Preview

Before executing, the agent runs a dry run to show what would happen:

```bash
python scripts/python/template_script.py path/to/input.txt \
  --output docs/result.txt \
  --verbose \
  --dry-run
```

**Expected dry run output:**
```
[DRY RUN] No files will be written.

  Input:  path/to/input.txt  (3 lines, UTF-8)
  Output: docs/result.txt
  Mode:   verbose

Actions that would be taken:
  1. Read path/to/input.txt
  2. Apply transformation (3 lines)
  3. Write docs/result.txt
  4. Log summary to stderr
```

## Step 2: Real Execution

After confirming the plan, the agent runs the actual command:

```bash
python scripts/python/template_script.py path/to/input.txt \
  --output docs/result.txt \
  --verbose
```

**Expected output:**
```
[DEBUG] Reading input: path/to/input.txt
[DEBUG] Detected encoding: UTF-8
[DEBUG] Lines read: 3
[DEBUG] Processing line 1: "Line 1: First item"
[DEBUG] Processing line 2: "Line 2: Second item with special characters: <>&""
[DEBUG] Processing line 3: "Line 3: Unicode content: café, naïve, résumé"
[DEBUG] Writing output: docs/result.txt
✓ Completed successfully.
Output written to: docs/result.txt (3 lines)
```

## Expected Output File (`docs/result.txt`)

```
Processed: Line 1: First item
Processed: Line 2: Second item with special characters: <>&"
Processed: Line 3: Unicode content: café, naïve, résumé
```

## Edge Cases Illustrated

| Scenario | Behavior |
|----------|----------|
| Output file already exists | Agent uses `--force` to overwrite, warns the user |
| Input file not found | Agent reports error, suggests checking the path |
| Input encoding not UTF-8 | Script auto-detects; verbose mode shows detected encoding |
| Output directory does not exist | Script creates it automatically |
| Special characters in input | Preserved exactly as-is in output |

## Notes

- `--verbose` is safe to use in production — it writes debug info to stderr, not stdout.
- The output directory (`docs/`) is created if it does not exist.
- Use `--force` when the output file already exists and an overwrite is intended.
