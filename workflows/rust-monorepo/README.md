# Rust Monorepo Workflow

Multi-agent system for developing, testing, and releasing Rust monorepos managed as Cargo workspaces. Automates the full lifecycle from initial scaffolding through CI/CD setup and crates.io publishing.

## What It Does

Coordinates six specialized agents across the key phases of Rust monorepo development:

1. **Scaffold** — creates virtual workspace manifests, crate directories, and stub source files; or adds new crates to an existing workspace
2. **Manage Dependencies** — centralizes shared deps in `[workspace.dependencies]`, audits for CVEs and drift
3. **Build & Test** — runs workspace builds, parallel tests with nextest, and detects affected crates
4. **Enforce Code Quality** — runs `cargo fmt`, `cargo clippy`, and optionally `cargo-deny`
5. **Set Up CI/CD** — generates GitHub Actions or GitLab CI pipelines with caching and matrix builds
6. **Release & Publish** — manages versioning, CHANGELOG, publish ordering, and crates.io publication

## Agents

| Agent | Model | Purpose |
|---|---|---|
| `rust-mono.orchestrator` | sonnet | Coordinates the full pipeline end-to-end |
| `rust-mono.scaffolder` | fast | Creates workspace layout, Cargo.toml files, and stubs |
| `rust-mono.dep-manager` | fast | Manages workspace and per-crate dependencies |
| `rust-mono.build-tester` | fast | Builds workspace and runs test suites |
| `rust-mono.code-quality` | fast | Enforces formatting and Clippy lints |
| `rust-mono.ci-setup` | fast | Creates GitHub Actions / GitLab CI pipelines |
| `rust-mono.releaser` | sonnet | Handles versioning, CHANGELOG, and crates.io publishing |

## Pipeline

```
User: "Set up a Rust monorepo for [project]"
        |
        v
rust-mono.scaffolder
  - Creates virtual workspace Cargo.toml
  - Creates crates/ directory layout
  - Writes per-crate Cargo.toml and src stubs
  - Runs cargo check --workspace
        |
        v
rust-mono.dep-manager
  - Audits existing deps across crates
  - Centralizes shared deps in [workspace.dependencies]
  - Adds new deps with workspace = true
  - Runs cargo audit
        |
        v
rust-mono.build-tester
  - cargo build --workspace
  - cargo nextest run --workspace
  - Reports affected crates on change
        |
        v
rust-mono.code-quality
  - cargo fmt --all
  - cargo clippy --workspace --all-targets -- -D warnings
  - Configures rustfmt.toml and workspace lint levels
        |
        v
rust-mono.ci-setup
  - Creates .github/workflows/ci.yml
  - Jobs: fmt, clippy, test (matrix), build, optional release
  - Configures Swatinem/rust-cache
        |
        v
rust-mono.releaser
  - Checks pre-release readiness
  - Bumps versions (independent or locked)
  - Generates CHANGELOG
  - Publishes in dependency order
  - Optionally creates xtask automation
```

## Workspace Layout Reference

```
my-project/
├── Cargo.toml          ← virtual workspace (no [package] section)
├── Cargo.lock
├── Cargo.toml  [workspace.dependencies]
├── rustfmt.toml
├── deny.toml           ← cargo-deny config (optional)
├── crates/
│   ├── my-lib/
│   │   ├── Cargo.toml  ← [lints] workspace = true
│   │   └── src/lib.rs
│   └── my-bin/
│       ├── Cargo.toml
│       └── src/main.rs
├── xtask/              ← release automation (optional)
│   ├── Cargo.toml      ← publish = false
│   └── src/main.rs
├── target/             ← shared build cache
└── .github/
    └── workflows/
        └── ci.yml
```

## Usage

### Mode A — Full Pipeline (new workspace)

```
@rust-mono.orchestrator Set up a new Rust monorepo called payments-engine
with a payments-core lib crate and payments-cli bin crate.
Target CI: GitHub Actions. Publish target: crates.io.
```

### Mode B — Add a crate to an existing workspace

```
@rust-mono.orchestrator Add a new lib crate called payments-notifier
to my existing workspace at ./payments-engine
```

Or invoke the scaffolder directly:
```
@rust-mono.scaffolder Add a bin crate called payments-cli
to the workspace at ./payments-engine
```

The scaffolder automatically detects whether a workspace already exists:
- **Wildcard `members = ["crates/*"]`** — just creates the crate directory; Cargo picks it up automatically.
- **Explicit `members` list** — creates the crate directory and appends the entry to `members`.

### Individual Phases

**Scaffold a new workspace:**
```
@rust-mono.scaffolder Create a Rust workspace called analytics
with two lib crates: analytics-core and analytics-io
```

**Add a dependency:**
```
@rust-mono.dep-manager Add tokio 1 (full features) to the my-server crate
in workspace at ./my-project
```

**Run build and tests:**
```
@rust-mono.build-tester Build and test the workspace at ./my-project
using cargo-nextest
```

**Lint and format:**
```
@rust-mono.code-quality Run fmt and clippy on workspace at ./my-project
Fix any formatting issues and report clippy warnings
```

**Set up CI:**
```
@rust-mono.ci-setup Create a GitHub Actions workflow for workspace at ./my-project
Matrix: stable + beta. Include a release job triggered by version tags.
```

**Release a crate:**
```
@rust-mono.releaser Release my-lib 0.2.0 from workspace at ./my-project
Bump version, update CHANGELOG, dry-run publish to crates.io
```

## Key Commands Reference

```bash
# Build
cargo build --workspace
cargo build --workspace --release

# Test
cargo nextest run --workspace --all-targets   # preferred
cargo test --workspace                         # fallback

# Lint
cargo fmt --all
cargo fmt --all -- --check                     # CI mode
cargo clippy --workspace --all-targets --all-features -- -D warnings

# Dependencies
cargo add [dep] --package [crate]              # requires cargo-edit
cargo audit                                    # security check
cargo outdated --workspace                     # version check
cargo deny check                               # license + advisory check

# Workspace ops
cargo build --package [crate]                  # single crate
cargo test --package [crate]                   # single crate
cargo metadata --format-version 1             # dependency graph

# Release
cargo workspaces version minor                 # bump all crates
cargo publish --package [crate] --dry-run      # verify before publish
cargo publish --package [crate]
cargo xtask release                            # if xtask is set up
```

## Research

See [research.md](research.md) for the full domain research document covering Cargo workspace best practices, CI/CD strategies, and common pitfalls.
