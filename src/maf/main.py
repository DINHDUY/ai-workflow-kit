"""
main.py — Entry point for the Next.js Stitch-to-production MAF workflow.

Imports the pre-built workflow from workflow.py and drives it with streaming
event handling, printing per-agent outputs as they arrive and surfacing the
final result clearly.

Usage:
    python main.py "Convert my Stitch export at ./stitch to a Next.js app"
    python main.py --task task.txt
    python main.py --interactive          # REPL mode
    python main.py -i                     # REPL mode (short flag)
    python main.py --agents-dir .cursor/agents "task"
    python main.py --no-stream "task"     # collect full output, then print
"""
import argparse
import asyncio
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Workflow import — done lazily inside build() so CLI flags (--agents-dir etc.)
# are applied BEFORE workflow.py module-level code runs.
# ---------------------------------------------------------------------------

_workflow = None
_workflow_agent = None


def _load_workflow(agents_dir: str | None, platform: str | None, global_instructions_path: str | None):
    """Import workflow module and return (workflow, workflow_agent)."""
    # Patch sys.argv so workflow.py's build_workflow() can pick up overrides
    # via environment if needed — but we call build_workflow() directly instead.
    from maf.workflow import build_workflow  # noqa: PLC0415 (import not at top)

    w = build_workflow(
        agents_dir=agents_dir,
        platform=platform,
        global_instructions_path=global_instructions_path,
    )
    wa = w.as_agent(
        name="NextJsStitchPipeline",
        description=(
            "End-to-end pipeline that converts Google Stitch UI sketches into "
            "production-ready Next.js 15+ applications."
        ),
    )
    return w, wa


# ---------------------------------------------------------------------------
# Event handling
# ---------------------------------------------------------------------------

SEPARATOR = "=" * 64
THIN_SEP = "-" * 64


async def run_workflow(workflow, task: str, stream: bool = True, verbose: bool = False) -> str:
    """
    Drive the workflow for *task*, streaming events to stdout.
    Returns the final consolidated output text.
    """
    print(f"\n{SEPARATOR}")
    print(f"  TASK")
    print(THIN_SEP)
    print(task)
    print(f"{SEPARATOR}\n")

    final_output: str = ""
    current_agent: str | None = None

    async for event in workflow.run(task, stream=stream):
        etype = event.type

        # ── Agent transition ────────────────────────────────────────────────
        if etype == "agent_selected":
            agent_name = getattr(event.data, "name", "unknown")
            if agent_name != current_agent:
                current_agent = agent_name
                # Newline before new agent block so tokens don't run together
                print(f"\n\n[{agent_name}]", flush=True)

        # ── Streaming text ──────────────────────────────────────────────────
        elif etype == "output":
            text = getattr(event.data, "text", "") or ""
            if text:
                print(text, end="", flush=True)
                final_output += text

        # ── Tool call ───────────────────────────────────────────────────────
        elif etype == "tool_call":
            if verbose:
                tool_name = getattr(event.data, "name", "?")
                tool_args = getattr(event.data, "arguments", "")
                print(f"\n  [tool → {tool_name}]  {str(tool_args)[:120]}", flush=True)
            else:
                tool_name = getattr(event.data, "name", "?")
                print(f"\n  [tool → {tool_name}]", end="", flush=True)

        # ── Tool result ─────────────────────────────────────────────────────
        elif etype == "tool_result":
            if verbose:
                result_preview = str(getattr(event.data, "content", ""))[:200]
                print(f"\n  [result] {result_preview}", flush=True)

        # ── Human-in-the-loop plan review ───────────────────────────────────
        elif etype == "plan_review":
            print(f"\n\n{SEPARATOR}")
            print("  PLAN REVIEW REQUIRED")
            print(SEPARATOR)
            print(event.data.plan)
            print(THIN_SEP)
            approval = input("Approve this plan? [y/N]: ").strip().lower()
            if approval == "y":
                await event.data.approve()
            else:
                reason = input("Rejection reason (optional): ").strip()
                await event.data.reject(reason or "Rejected by user")

        # ── Stall detection ─────────────────────────────────────────────────
        elif etype == "stall":
            print(
                f"\n[WARNING] Workflow stalled — no progress detected. "
                "The workflow will terminate early.",
                flush=True,
            )

        # ── Completion ──────────────────────────────────────────────────────
        elif etype == "completed":
            text = getattr(event.data, "text", None) or getattr(event.data, "content", None)
            if text and text not in final_output:
                final_output = text
                print(f"\n\n{SEPARATOR}")
                print("  FINAL OUTPUT")
                print(SEPARATOR)
                print(final_output)

        # ── Error ───────────────────────────────────────────────────────────
        elif etype == "error":
            print(f"\n[ERROR] {event.data}", file=sys.stderr, flush=True)

    print(f"\n\n{SEPARATOR}\n")
    return final_output.strip()


# ---------------------------------------------------------------------------
# CLI helpers
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="Run the Next.js Stitch-to-production MAF workflow.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            '  python main.py "Convert my Stitch export at ./stitch"\n'
            "  python main.py --task task.txt\n"
            "  python main.py --interactive\n"
            "  python main.py --agents-dir .cursor/agents \"task\"\n"
            "  python main.py --no-stream --verbose \"task\"\n"
        ),
    )
    parser.add_argument(
        "task_inline",
        nargs="?",
        metavar="TASK",
        help="Task string (inline). Omit to be prompted interactively.",
    )
    parser.add_argument(
        "--task", "-t",
        dest="task_file",
        metavar="FILE",
        help="Read the task from a plain-text file instead of the command line.",
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive REPL mode (multi-turn).",
    )
    parser.add_argument(
        "--agents-dir",
        default=None,
        dest="agents_dir",
        metavar="DIR",
        help="Path to agents/*.md directory (auto-detected if omitted).",
    )
    parser.add_argument(
        "--platform",
        default=None,
        metavar="NAME",
        help="Platform override: claude | cursor | copilot | generic.",
    )
    parser.add_argument(
        "--global-instructions",
        default=None,
        dest="global_instructions_path",
        metavar="FILE",
        help="Explicit path to global instructions file (auto-detected if omitted).",
    )
    parser.add_argument(
        "--no-stream",
        action="store_true",
        dest="no_stream",
        help="Collect the full response before printing (disables token streaming).",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print tool call arguments and result previews.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=600,
        metavar="SECONDS",
        help="Abort the workflow if it runs longer than this many seconds (default: 600).",
    )
    return parser.parse_args()


def _resolve_task(args: argparse.Namespace) -> str:
    """Return the task string from args, file, or interactive prompt."""
    if args.task_file:
        p = Path(args.task_file)
        if not p.exists():
            print(f"[ERROR] Task file not found: {p}", file=sys.stderr)
            sys.exit(1)
        return p.read_text(encoding="utf-8").strip()

    if args.task_inline:
        return args.task_inline

    # Fall back to interactive single-prompt
    print("No task provided. Enter your task below (blank line or Ctrl-D to submit):\n")
    lines: list[str] = []
    try:
        while True:
            line = input()
            if not line and lines:
                break
            lines.append(line)
    except EOFError:
        pass
    task = "\n".join(lines).strip()
    if not task:
        print("[ERROR] Empty task. Aborting.", file=sys.stderr)
        sys.exit(1)
    return task


# ---------------------------------------------------------------------------
# REPL
# ---------------------------------------------------------------------------

async def _interactive_repl(workflow, stream: bool, verbose: bool) -> None:
    """Run a simple multi-turn REPL against the workflow."""
    print(
        "\nNext.js Stitch Pipeline — Interactive Mode\n"
        "Type your task and press Enter. Type 'exit' or 'quit' to stop.\n"
    )
    while True:
        try:
            task = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[Exiting]")
            break
        if not task:
            continue
        if task.lower() in {"exit", "quit", "q", "bye"}:
            print("[Exiting]")
            break
        await run_workflow(workflow, task, stream=stream, verbose=verbose)


# ---------------------------------------------------------------------------
# Timeout wrapper
# ---------------------------------------------------------------------------

async def _run_with_timeout(workflow, task: str, timeout: int, stream: bool, verbose: bool) -> str:
    try:
        return await asyncio.wait_for(
            run_workflow(workflow, task, stream=stream, verbose=verbose),
            timeout=float(timeout),
        )
    except asyncio.TimeoutError:
        print(
            f"\n[TIMEOUT] Workflow exceeded {timeout}s — partial output returned.",
            file=sys.stderr,
        )
        return ""


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def main() -> int:
    args = _parse_args()

    # Build workflow with resolved flags so module-level singleton in workflow.py
    # is bypassed in favour of our parameterised call.
    try:
        workflow, _ = _load_workflow(
            agents_dir=args.agents_dir,
            platform=args.platform,
            global_instructions_path=args.global_instructions_path,
        )
    except FileNotFoundError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        sys.exit(1)

    stream = not args.no_stream

    if args.interactive:
        await _interactive_repl(workflow, stream=stream, verbose=args.verbose)
        return 0

    task = _resolve_task(args)
    result = await _run_with_timeout(
        workflow, task,
        timeout=args.timeout,
        stream=stream,
        verbose=args.verbose,
    )
    return 0 if result else 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[Interrupted by user]", file=sys.stderr)
        exit_code = 130
    sys.exit(exit_code)
