**Rust monorepos (multiple crates in one repo) are best managed using Cargo workspaces.** This is the standard, idiomatic approach for related crates developed together. It provides a shared `Cargo.lock`, unified `target/` directory (for efficient incremental builds), and centralized dependency management.

### 1. Basic Setup: Virtual Workspace Root

Use a **virtual manifest** at the repository root (no `[package]` section). This keeps the root clean.

**Root `Cargo.toml`**:
```toml
[workspace]
resolver = "3"  # Use the latest resolver
members = [
    "crates/*",   # Or explicit list: "my-lib", "my-bin", etc.
]
# Optional but recommended
[workspace.dependencies]
# Define common deps here once
serde = { version = "1.0", features = ["derive"] }
tokio = { version = "1", features = ["full"] }
# ...
```

**Individual crate `Cargo.toml`** (e.g., `crates/my-lib/Cargo.toml`):
```toml
[package]
name = "my-lib"
version = "0.1.0"
edition = "2021"

[dependencies]
serde = { workspace = true }
tokio = { workspace = true }
my-other-crate = { path = "../my-other-crate" }  # Internal path dep
```

**Recommended directory layout** (flat under `crates/` for medium-to-large projects):
```
my-project/
├── Cargo.toml          # Virtual workspace
├── Cargo.lock
├── crates/
│   ├── my-lib/
│   │   ├── Cargo.toml
│   │   └── src/
│   │       └── lib.rs
│   ├── my-bin/
│   │   ├── Cargo.toml
│   │   └── src/
│   │       └── main.rs
│   └── another-crate/
├── target/             # Shared
└── README.md
```

- **Why flat?** Easier navigation (`ls crates/` gives a full overview), matches Cargo's flat crate namespace, simpler refactoring, and less hierarchy maintenance. Use this for up to ~100 crates / ~1M LOC. Nested structures add complexity without much benefit in this range.
- For very large repos, consider sub-grouping (e.g., `crates/core/*`, `crates/apps/*`) or tools like Bazel/Buck2, but stick with Cargo workspaces for most cases.

### 2. Key Best Practices

- **Dependency Management**:
  - Centralize shared/external dependencies in `[workspace.dependencies]`.
  - In member crates, use `foo = { workspace = true }` for consistency and easy updates.
  - Internal crates: Use `path = "../sibling-crate"` dependencies. Add `version` alongside `path` if you plan to publish (Cargo strips the path on publish).
  - Avoid version conflicts; the shared lockfile helps enforce this.

- **Crate Granularity**:
  - Split logically by functionality/domain (e.g., `core`, `utils`, `api`, `cli`). Prefer small crates that do one thing well—they compile in parallel and improve reusability/modularity.
  - Keep boundaries clear; minimize tight coupling.
  - Don't split prematurely—start with fewer crates and extract as the project grows.

- **Commands** (run from root):
  - `cargo build` / `cargo test` / `cargo check` — affects the workspace.
  - Target specific crates: `cargo test -p my-crate`, `cargo run -p my-bin`.
  - Format/lint all: `cargo fmt --all`, `cargo clippy --all-targets --all-features`.

- **Versioning & Publishing**:
  - Internal crates: Use `version = "0.0.0"`.
  - Publishable crates: Be deliberate with semver. Consider separating them (e.g., into a `libs/` folder) if some are public.
  - Each crate publishes independently with `cargo publish -p crate-name`.

- **Development Workflow**:
  - Use `cargo xtask` (a dedicated Rust binary crate for automation like codegen, releases, etc.) to avoid Makefile sprawl.
  - Enable features like `resolver = "3"` for better dependency handling.
  - For CI/performance: Use `sccache`, incremental compilation, and selective testing/builds (tools like `cargo-rail` exist for graph-aware orchestration).

- **Testing & Quality**:
  - Run workspace-wide tests or per-crate.
  - Consistent `cargo fmt` + `clippy` across the workspace.

### 3. Advanced / Scaling Tips

- **Features**: Define workspace-level features for coordinated activation across crates.
- **Performance**: For huge workspaces, watch compile times (Cargo can struggle beyond certain scales). Consider build caching and selective rebuilds.
- **Examples**: Look at real projects like `rust-analyzer`, Tokio, or Bevy for patterns.

### Common Pitfalls to Avoid

- Putting the main crate in the root (pollutes with `src/`, requires extra flags).
- Inconsistent dependency versions.
- Overly deep nesting.
- Ignoring path dependencies for internal crates.

This setup scales well for most teams and projects while staying within Cargo's native capabilities. For specifics, the official Cargo book chapter on workspaces is the best starting point.

If your monorepo has unique constraints (e.g., many binaries, platform-specific crates, or extreme scale), provide more details for tailored advice!

**Rust monorepo CI/CD strategies** focus on speed, reliability, selective execution (only build/test changed crates), strong caching, and consistent quality checks. Cargo workspaces handle most of this natively, but you need smart tooling and workflows for scale.

### 1. Core Principles
- **Run from workspace root** — Use `cargo build --workspace`, `cargo test --workspace`, etc.
- **Selective builds/tests** — Avoid full workspace runs on every PR. Detect changed/affected crates via `git diff` + `cargo metadata` or tools like `affected`, `cargo-deltabuild`.
- **Caching is king** — Rust compilation is expensive; maximize cache hits for dependencies and artifacts.
- **Determinism** — Use `--locked`, consistent toolchains, and pinned dependencies.
- **Parallelism & modern runners** — Leverage `cargo-nextest`, matrix jobs, and fast runners (e.g., GitHub `ubuntu-latest` or larger).

### 2. Essential Tooling
| Tool              | Purpose                          | Why It Matters in Monorepos                  |
|-------------------|----------------------------------|---------------------------------------------|
| **cargo-nextest** | Fast test runner                | Parallel test execution, better reporting, CI-focused features (partitioning, archiving). Often 2-3x faster. |
| **Swatinem/rust-cache** or **sccache** | Build/dependency caching       | Caches `target/` and registry; huge wins on repeated CI runs. |
| **cargo-hack**    | Feature combination testing     | Test all feature powersets efficiently.     |
| **cargo fmt + clippy** | Formatting & linting         | Enforce via `--all` or per-crate.           |
| **xtask**         | Custom automation (releases, etc.) | Dedicated crate for scripts.               |

**Install in CI** (e.g., via `taiki-e/install-action` for nextest).

### 3. GitHub Actions Example (Recommended Starter)
```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: Swatinem/rust-cache@v2   # Excellent Rust caching
      - uses: dtolnay/rust-toolchain@stable
      - run: cargo fmt --all --check
      - run: cargo clippy --workspace --all-targets -- -D warnings

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: Swatinem/rust-cache@v2
      - uses: taiki-e/install-action@cargo-nextest
      - run: cargo nextest run --workspace --all-targets
```

**Advanced enhancements**:
- **Selective testing**: Script to find changed crates (e.g., `git diff --name-only | grep Cargo.toml` or use `cargo metadata` + dependency graph tools) and run `cargo nextest run -p <changed-crate>`.
- **Matrix for platforms/toolchains**: Test stable + beta/nightly, Linux + macOS/Windows (selectively).
- **Partitioning with nextest**: Split large test suites across jobs/machines.
- **sccache for distributed cache**: Use Redis/S3 backend for team-wide sharing.

### 4. Scaling Strategies
- **Affected-only pipelines** — Many teams reduce CI from 45+ minutes to <10 minutes by testing only impacted crates and their dependents.
- **Separate jobs**:
  - Fast lint/format (always).
  - Unit tests (selective).
  - Integration/e2e (on main or scheduled).
  - Release/publish (on tags).
- **Profiles for CI** — Define a lighter `[profile.ci]` in root `Cargo.toml` (lower opt-level, more codegen units) for faster builds.
- **Docker builders** — Pre-bake images with Rust + sccache for consistency and speed.
- **Release automation** — Use `cargo-workspaces` tool or custom xtask for versioning/publishing multiple crates. Tag → publish only changed/public crates.

### 5. Common Pitfalls & Tips
- **Cache invalidation** — Be careful with `target/` in monorepos; tools like `rust-cache` handle it well. Use `--locked` to avoid unexpected downloads.
- **Feature explosion** — Use `cargo hack` in CI for crates with many features.
- **Long builds** — For very large workspaces (>100 crates), consider build systems like Bazel/Buck2, but most projects thrive with optimized Cargo workspaces.
- **Security** — Use `cargo audit`, pin toolchains, and secrets for publishing tokens.
- **Observability** — Nextest provides excellent JUnit/XML output for CI dashboards and flaky test detection.

### Real-World Inspiration
- **Tokio**, **rust-analyzer**, and **Bevy** — Study their GitHub workflows.
- Medium-to-large teams often combine selective execution + nextest + sccache for excellent results.

Start simple with the basic workflow above + caching, then add selective logic and nextest. This setup scales comfortably to dozens of crates.

If you share your repo size, hosting (GitHub/GitLab), or specific pain points (e.g., many features, cross-platform, publishing), I can give more tailored YAML or scripts!