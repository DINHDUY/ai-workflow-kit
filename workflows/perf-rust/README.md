# Performance-First Rust Coder

A multi-agent system that generates high-performance, correctness-guaranteed Rust crates from a natural language feature request. It is designed for Rust developers who need optimized implementations with full test coverage and want the rigor of a TDD workflow without the manual overhead. The system researches optimal Rust-specific algorithms and data structures, writes a formal spec, decomposes work into atomic tasks, implements code following Rust idioms, and iteratively refines performance through two nested feedback loops -- producing optimized Rust source code, a complete test suite (unit, integration, property-based, and Criterion benchmarks), and a full provenance trail of every decision made.

## What It Does

1. Researches the fastest Rust-specific algorithms, data structures, and ecosystem crates for your feature
2. Generates a Rust constitution (coding rule-set) and formal specification with performance targets
3. Authors a complete test suite: `#[cfg(test)]` unit tests, `tests/` integration tests, `proptest`/`quickcheck` property tests, and `benches/` Criterion benchmarks
4. Decomposes the implementation into atomic, dependency-ordered tasks (each under 30 lines)
5. Implements all tasks and iteratively fixes failures through an inner correctness loop (Loop A, up to 5 retries)
6. Re-runs the entire pipeline through an outer performance loop (Loop B, up to 3 iterations) until targets are met or improvement plateaus

## Agents

| Agent | Role |
|-------|------|
| `perf-rust.orchestrator` | Coordinates the full pipeline and controls the outer performance optimization loop (Loop B) |
| `perf-rust.researcher` | Researches Rust-specific algorithms, ecosystem crates, and performance patterns from authoritative sources |
| `perf-rust.constitution-writer` | Distills research into a compact Rust rule-set injected into all downstream agents |
| `perf-rust.spec-writer` | Converts the feature request into a formal spec and authors all Rust test files (unit, integration, property, benchmarks) |
| `perf-rust.planner` | Produces a TDD implementation plan with step-by-step Cargo build order |
| `perf-rust.task-decomposer` | Breaks the plan into atomic tasks and outputs a dependency graph (DAG) |
| `perf-rust.implementer` | Writes Rust source code task-by-task, following constitution rules; fixes failures on retry |
| `perf-rust.test-runner` | Executes `cargo test`, `cargo bench`, `cargo clippy`, and `cargo fmt --check`; produces a structured JSON report (read-only) |
| `perf-rust.loop-controller` | Manages the inner implement/test cycle (Loop A), enforcing retry limits |

## How to Use

### Full Pipeline

Invoke `perf-rust.orchestrator` with your feature request and performance targets:

```
@perf-rust.orchestrator Implement a high-performance CSV parser crate in Rust. Performance target: 500MB/s throughput, zero-copy parsing using &[u8] slices, streaming API with Iterator impl.
```

```
@perf-rust.orchestrator Build a concurrent hash map crate with lock-free reads using DashMap or a custom sharded design. Performance target: 10M reads/sec with 8 threads, 1M writes/sec.
```

```
@perf-rust.orchestrator Create a SIMD-accelerated string search crate implementing Boyer-Moore-Horspool with AVX2 SIMD. Performance target: within 10% of ripgrep's grep performance.
```

### Targeting an Existing rust-monorepo Crate

If you already have a workspace scaffolded with `rust-mono.scaffolder`, pass `--crate-path` to write directly into that crate instead of creating a standalone output:

```
@perf-rust.orchestrator Implement a high-performance CSV parser. Performance target: 500MB/s throughput, zero-copy &[u8] parsing. --crate-path ./payments-engine/crates/csv-parser
```

```
@perf-rust.orchestrator Build a concurrent hash map with lock-free reads. Performance target: 10M reads/sec with 8 threads. --crate-path /home/user/my-project/crates/concurrent-map
```

The orchestrator will:
1. Detect the workspace root automatically by scanning for `[workspace]` in parent `Cargo.toml` files
2. Write source to `[crate-path]/src/`, integration tests to `[crate-path]/tests/`, benchmarks to `[crate-path]/benches/`
3. Append `criterion` and `proptest` dev-dependencies to the crate's existing `Cargo.toml` (using `{ workspace = true }` if already declared in `[workspace.dependencies]`)
4. Save all provenance artifacts (spec, constitution, research report, etc.) to `[crate-path]/.perf-rust/`

### Individual Agents

**Research only** -- Use `perf-rust.researcher` when you just need Rust optimization strategies:
```
@perf-rust.researcher Research the fastest approaches for CSV parsing in Rust 1.87. Compare: zero-copy &[u8] parsing, memmap2 for memory-mapped I/O, nom parser combinators, manual byte scanning. Focus on throughput (MB/s) and zero-allocation patterns.
```

**Spec and tests only** -- Use `perf-rust.spec-writer` when you already have research and a constitution:
```
@perf-rust.spec-writer Create a specification and Rust test suite for a CSV parser crate. Use constitution at workflows/perf-rust/outputs/csv-parser/constitution.md and research report at workflows/perf-rust/outputs/csv-parser/performance-research-report.md. Performance targets: 500MB/s throughput.
```

**Inner loop only** -- Use `perf-rust.loop-controller` to run the implement/test cycle on an existing task graph:
```
@perf-rust.loop-controller Execute the implementation/test loop for task graph at workflows/perf-rust/outputs/csv-parser/task-graph.json. Constitution: constitution.md. Spec: spec.md. Tests in tests/ and src/. Write source to src/.
```

## Nested Loop Structure

The system uses two feedback loops to guarantee both correctness and performance:

**Loop A (inner -- correctness):** After all tasks are implemented, the test runner executes `cargo test -- --nocapture` and `cargo clippy -- -D warnings`. If any tests fail or clippy warns, the loop controller sends failure details back to the implementer, which fixes only the failing tasks. This repeats up to 5 times or until all tests pass and clippy is clean.

**Loop B (outer -- performance):** After Loop A succeeds, the orchestrator checks whether performance targets from the spec are met (via `cargo bench` Criterion results). If not (and improvement has not plateaued), the entire pipeline re-runs from research onward -- the researcher focuses on identified bottlenecks, the constitution gets tighter Rust-specific rules, and the spec adjusts thresholds. This repeats up to 3 times.

## Setup

```bash
# Install Rust toolchain
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Install nightly (for some SIMD features, optional)
rustup toolchain install nightly

# Install cargo extensions
cargo install cargo-flamegraph
cargo install cargo-criterion  # enhanced criterion runner (optional)

# Add Criterion and proptest to your Cargo.toml:
# [dev-dependencies]
# criterion = { version = "0.5", features = ["html_reports"] }
# proptest = "1"
# quickcheck = "1"
#
# [[bench]]
# name = "my_benchmark"
# harness = false
```

No additional infrastructure is required. All agents use built-in tools (file read/write, shell execution via `cargo`, web search).

## Rust Crate Structure

The workflow supports two modes:

### Mode A — Standalone

All artifacts are saved to `workflows/perf-rust/outputs/[crate-name]/`. The layout follows standard Cargo conventions:

```
workflows/perf-rust/outputs/[crate-name]/
  Cargo.toml                    # Crate manifest with dependencies
  src/
    lib.rs                      # Main library entry point
    *.rs                        # Additional source modules
  tests/
    integration_test.rs         # Integration tests (separate from src/)
    *.rs                        # Additional integration test files
  benches/
    [crate_name]_bench.rs       # Criterion benchmarks
  .perf-rust/[crate-name]/      # ← provenance_dir (pipeline artifacts)
    constitution.md
    spec.md
    performance-research-report.md
    tdd-plan.md
    task-graph.json
    test-report.json
    loop-a-summary.md
    loop-b-state.json
    implementation-log.md
```

### Mode B — Existing Crate (rust-monorepo)

When a `--crate-path` is provided, the pipeline targets an existing crate inside a Cargo workspace (e.g., one created by `rust-mono.scaffolder`). Source, tests, and benchmarks go directly into the crate's own directories. Pipeline provenance artifacts are isolated inside `.perf-rust/` so they do not pollute the crate:

```
my-project/                     # workspace root (rust-monorepo)
  Cargo.toml                    # virtual workspace manifest (updated if needed)
  crates/
    [crate-name]/               # existing crate (--crate-path points here)
      Cargo.toml                # UPDATED: criterion + proptest dev-deps added
      src/
        lib.rs                  # ← implementation written here
        *.rs
      tests/
        integration_test.rs     # ← integration tests written here
      benches/
        [crate_name]_bench.rs   # ← Criterion benchmarks written here
      .perf-rust/               # ← all provenance artifacts (gitignore-able)
        constitution.md
        spec.md
        performance-research-report.md
        tdd-plan.md
        task-graph.json
        test-report.json
        loop-a-summary.md
        loop-b-state.json
        implementation-log.md
```

## Test Categories

| Category | Location | Tool | Command |
|----------|----------|------|---------|
| Unit tests | `src/lib.rs` (`#[cfg(test)]`) | `cargo test` | `cargo test -- --nocapture` |
| Integration tests | `tests/*.rs` | `cargo test` | `cargo test -- --nocapture` |
| Property-based tests | `tests/prop_tests.rs` | `proptest` / `quickcheck` | `cargo test` |
| Doc tests | `///` comments | `cargo test` | `cargo test --doc` |
| Benchmarks | `benches/*.rs` | Criterion.rs | `cargo bench` |
| Linting | all `.rs` files | clippy | `cargo clippy -- -D warnings` |
| Formatting | all `.rs` files | rustfmt | `cargo fmt --check` |

## Examples

```
@perf-rust.orchestrator Build a concurrent hash map crate with lock-free reads using DashMap or a custom sharded design. Performance target: 10M reads/sec with 8 threads, 1M writes/sec.
```

```
@perf-rust.orchestrator Implement a JSON serializer in Rust that outperforms serde_json by 2x for fixed schemas. Performance target: 1GB/s serialization throughput, zero allocations for primitive types using a custom Write impl.
```

```
@perf-rust.orchestrator Create a SIMD-accelerated base64 encoder/decoder crate using AVX2 intrinsics. Performance target: within 5% of the fastest C implementation, safe wrapper around unsafe SIMD code.
```
