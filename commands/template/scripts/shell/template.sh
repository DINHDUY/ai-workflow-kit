#!/usr/bin/env bash
# template.sh — Template helper script for AI agent commands.
#
# TODO: Replace this header comment and all TODO lines with your actual logic.
#
# Usage:
#   ./template.sh --input <path> [options]
#
# Examples:
#   ./template.sh --input path/to/input.txt
#   ./template.sh --input path/to/input.txt --output docs/result.txt --verbose
#   ./template.sh --input path/to/input.txt --dry-run

set -euo pipefail

# ─── Defaults ─────────────────────────────────────────────────────────────────
INPUT=""
OUTPUT=""
VERBOSE=false
DRY_RUN=false
FORCE=false

# ─── Usage ────────────────────────────────────────────────────────────────────
usage() {
  cat <<EOF
Usage: $(basename "$0") --input <path> [options]

Options:
  --input   <path>   Input file to process (required)
  --output  <path>   Output path (default: ./output/<basename>)
  --verbose          Enable debug output to stderr
  --dry-run          Preview actions without writing files
  --force            Overwrite output if it already exists
  --help             Show this message and exit

Examples:
  $(basename "$0") --input path/to/input.txt
  $(basename "$0") --input path/to/input.txt --output docs/result.txt
  $(basename "$0") --input path/to/input.txt --dry-run --verbose
EOF
}

# ─── Argument parsing ─────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --input)   INPUT="$2";  shift 2 ;;
    --output)  OUTPUT="$2"; shift 2 ;;
    --verbose) VERBOSE=true; shift ;;
    --dry-run) DRY_RUN=true; shift ;;
    --force)   FORCE=true;   shift ;;
    --help|-h) usage; exit 0 ;;
    *)
      echo "Error: Unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

# ─── Helpers ──────────────────────────────────────────────────────────────────
log_debug() {
  [[ "$VERBOSE" == true ]] && echo "[DEBUG] $*" >&2 || true
}

log_warn() {
  echo "[WARN] $*" >&2
}

die() {
  echo "Error: $*" >&2
  exit 1
}

# ─── Validate input ───────────────────────────────────────────────────────────
[[ -z "$INPUT" ]] && { usage >&2; die "Missing required option: --input"; }
[[ -f "$INPUT" ]] || die "Input file not found: $INPUT"

# ─── Resolve output path ──────────────────────────────────────────────────────
if [[ -z "$OUTPUT" ]]; then
  BASENAME="$(basename "$INPUT")"
  OUTPUT="output/${BASENAME}"
fi

# ─── Dry run preview ──────────────────────────────────────────────────────────
if [[ "$DRY_RUN" == true ]]; then
  LINE_COUNT="$(wc -l < "$INPUT" | tr -d ' ')"
  echo "[DRY RUN] No files will be written."
  echo ""
  echo "  Input:  $INPUT  ($LINE_COUNT lines)"
  echo "  Output: $OUTPUT"
  echo "  Mode:   $([ "$VERBOSE" == true ] && echo 'verbose' || echo 'normal')"
  echo ""
  echo "Actions that would be taken:"
  echo "  1. Read $INPUT"
  echo "  2. Apply transformation ($LINE_COUNT lines)"
  echo "  3. Write $OUTPUT"
  exit 0
fi

# ─── Overwrite guard ──────────────────────────────────────────────────────────
if [[ -f "$OUTPUT" && "$FORCE" != true ]]; then
  die "Output file already exists: $OUTPUT\nUse --force to overwrite."
fi
if [[ -f "$OUTPUT" && "$FORCE" == true ]]; then
  log_warn "Overwriting existing file: $OUTPUT"
fi

# ─── Process ──────────────────────────────────────────────────────────────────
log_debug "Reading input: $INPUT"
LINE_COUNT="$(wc -l < "$INPUT" | tr -d ' ')"
log_debug "Lines read: $LINE_COUNT"

# TODO: Replace this placeholder transformation with your actual logic.
# This example prepends "Processed: " to each line.
RESULT="$(sed 's/^/Processed: /' "$INPUT")"

log_debug "Lines processed: $(echo "$RESULT" | wc -l | tr -d ' ')"

# ─── Write output ─────────────────────────────────────────────────────────────
log_debug "Writing output: $OUTPUT"
mkdir -p "$(dirname "$OUTPUT")"
echo "$RESULT" > "$OUTPUT"

OUT_LINE_COUNT="$(wc -l < "$OUTPUT" | tr -d ' ')"
echo "✓ Completed successfully."
echo "Output written to: $OUTPUT ($OUT_LINE_COUNT lines)"
