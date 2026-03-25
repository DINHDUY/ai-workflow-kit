# Example: Basic Usage

This example shows the simplest invocation of the command — one required input, all other options at their defaults.

## Input

**User invocation:**
```
/command-name path/to/input.txt
```

**Input file (`path/to/input.txt`):**
```
Hello, world!
This is a sample input.
```

## What the Agent Does

1. Detects that `path/to/input.txt` was provided; no further questions needed.
2. Confirms the file exists and is readable.
3. Runs the default operation:
   ```bash
   python scripts/python/template_script.py path/to/input.txt
   ```
4. Verifies the output file was created at the default location (`./output/input.txt`).

## Expected Output

```
Processing: path/to/input.txt
✓ Completed successfully.
Output written to: ./output/input.txt (2 lines)
```

**Output file (`./output/input.txt`):**
```
Processed result line 1
Processed result line 2
```

## Notes

- Output goes to `./output/` by default when no `--output` is specified.
- No overwrite confirmation needed — the output directory was empty.
