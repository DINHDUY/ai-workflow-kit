---
name: reviewing-rust-code
description: Review Rust code for quality, idiomatic usage, and safety following The Book, Programming Rust, Rust for Rustaceans, and Zero to Production. Use when reviewing Rust code, pull requests, or when the user asks for Rust code review, idiomatic patterns, ownership/borrowing checks, error handling, async Rust, or Cargo project guidance.
file_scopes:
  - "**/*.rs"
  - "**/Cargo.toml"
  - "**/Cargo.lock"
metadata:
  category: code-review
  stack: Rust
---

# Rust Code Review

Apply these standards when reviewing Rust code. Core rules are inline; load reference files for detail when needed.

---

## Review Checklist

```
- [ ] Naming follows Rust conventions (snake_case, UpperCamelCase, SCREAMING_SNAKE_CASE)
- [ ] rustfmt and clippy pass cleanly
- [ ] Ownership and borrowing are idiomatic (no unnecessary clones or unwraps)
- [ ] Error handling uses Result<T, E> + ? operator with thiserror/anyhow
- [ ] Traits and generics leverage zero-cost abstractions
- [ ] Unsafe code is minimized and encapsulated behind safe APIs
- [ ] Async code is cancellation-safe and does not block the executor
- [ ] Tests exist: unit, integration, and doc tests where appropriate
- [ ] Public APIs have /// documentation with examples
- [ ] No performance anti-patterns (excessive allocation, blocking I/O in async)
- [ ] Cargo.toml is clean (no unnecessary dependencies, features used)
- [ ] DRY: no duplicated logic, shared utilities used
```

---

## 1. Code Style & Naming

Core rules:
- `snake_case` for functions, variables, modules; `UpperCamelCase` for types, structs, traits, enums; `SCREAMING_SNAKE_CASE` for constants
- Run `rustfmt` and `clippy` consistently — they are non-negotiable
- Prefer `let` over `let mut`; immutability by default
- Keep functions small and focused; use expressive names

Flag:
- Mixed naming conventions in the same file
- Missing `#[derive]` on types that should implement `Debug`, `Clone`, `Default`, `PartialEq`
- Overly long functions (>50 lines) or functions with >3 nested `if`/`match` levels

---

## 2. Ownership & Borrowing

- Embrace ownership and move semantics — every value has a single owner
- Use references (`&` / `&mut`) instead of cloning when possible
- Let the compiler elide lifetimes where feasible; annotate only when required
- Use `Box`, `Rc`, `Arc` only when needed (heap allocation, shared ownership, thread-safe sharing)

Red flags:
- `clone()` on strings or collections in hot paths without profiling
- `&mut` references held across `.await` points
- Multiple mutable borrows that could be structured as immutable + immutable
- Smart pointer usage that could be replaced with a local variable or reference

> Good and bad patterns: `examples/ownership.rs`

---

## 3. Error Handling

- Use `Result<T, E>` and the `?` operator for propagation throughout
- Avoid `unwrap()` and `expect()` in library and production code
- Use `thiserror` for library errors (derivable, focused types)
- Use `anyhow` for application-level errors (context-rich, opaque to callers)
- Design domain-specific error types that enforce invariants via the type system
- Make invalid states unrepresentable with the type system

Red flags:
- `.unwrap()` or `.expect()` on public-facing or fallible operations
- Catching errors with `Err(_) => Ok(default_value)` and silently ignoring
- Error types that expose internal implementation details

> Good and bad patterns: `examples/error-handling.rs`

---

## 4. Traits, Generics & Type System

- Leverage traits for polymorphism and code reuse
- Combine traits with generics for flexible, zero-cost abstractions
- Implement common traits (`Debug`, `Display`, `Clone`, `Default`, `PartialEq`)
- Use the type system to encode invariants at compile time
- Follow trait coherence rules; prefer newtype pattern for extension

Red flags:
- Using `dyn Trait` where a generic `<T: Trait>` would be more flexible
- Implementing traits on types you don't own without a wrapper type
- Generic functions that don't actually use the generic parameter

---

## 5. Concurrency

- Rely on Rust's ownership rules to eliminate data races
- Use `std::thread`, channels (`mpsc`), `Arc<Mutex<T>>`/`RwLock` safely
- Understand `Pin`, `Waker`, and the async runtime model for advanced code
- Minimize and encapsulate `unsafe` — always behind a safe API

Red flags:
- Shared mutable state without synchronization (`Arc` + `Mutex`/`RwLock`)
- `unsafe` blocks without documentation explaining safety invariants
- Using `Send`/`Sync` marker traits without verifying actual safety

> Unsafe review guidelines: `references/unsafe-rules.md`

---

## 6. Testing & Documentation

- Write unit tests (`#[test]`) and integration tests (in `tests/` directory)
- Use property-based testing (`proptest`) for complex logic
- Write comprehensive documentation with `///` and testable examples
- Test public APIs thoroughly; prefer black-box integration tests for applications
- Aim for high test coverage on core logic

Red flags:
- No tests for public functions or business-critical logic
- Tests that only verify happy paths (no error/edge cases)
- Documentation examples that don't compile (`/// # ` not used for hidden setup)

> Testing patterns: `examples/testing.rs`

---

## 7. Project Structure & Tooling

- Use Cargo workspaces for projects with multiple crates
- Organize code with clear module hierarchy and feature flags
- Adopt hexagonal/clean architecture for backend services
- Set up CI with formatting, linting, tests, security audits, and coverage

Cargo.toml red flags:
- Unpinned dependency versions in production code
- `workspace.dependencies` unused (dead dependency declaration)
- Overly broad feature flags without clear purpose
- Dependencies on crates with known vulnerabilities (`cargo audit` should pass)

---

## 8. Performance & Idiomatic Code

- Write zero-cost abstractions; understand when to allocate vs. use stack
- Leverage iterators and closures for expressive, efficient code
- Use `bytes::Bytes` for zero-copy buffering; `BufReader`/`BufWriter` for I/O
- Control memory layout when performance matters (`#[repr(C)]`, field ordering)

Red flags:
- Collecting iterators into `Vec` before passing to a function that accepts `impl Iterator`
- Repeated `to_string()` instead of `&str` where possible
- String concatenation in loops instead of `format!` or `write!`

> Performance review guide: `references/performance-guide.md`

---

## 9. Async Rust

### Core Principles
- **Async is cooperative**: Tasks only yield at `.await` — no long-running CPU work without yielding
- **Choose the right runtime**: Tokio is the default choice for most applications
- **Prefer async APIs** throughout: use Tokio's `fs`, `net`, `time` instead of `std` blocking versions

### Writing Async Code
- Use `async fn` and `.await` for readability
- Return `impl Future<Output = T>` from non-`async` functions for flexibility
- Make futures `Send + 'static` when spawning on multi-threaded runtimes
- Box large futures (`Box::pin(async { ... })`) when state machines grow too big

### Concurrency Primitives
- `tokio::spawn()` for concurrent work — avoid over-spawning
- `tokio::join!` / `futures::future::join_all` for running futures concurrently
- `tokio::select!` for racing futures with cancellation of losers
- `tokio::sync::mpsc` (bounded) for channels with backpressure
- `tokio::sync::Mutex`/`RwLock` when holding across `.await`; `std::sync::Mutex` for quick critical sections

### Critical Pitfalls
- **Never block the executor**: No blocking `std` I/O, heavy computation, or long locks in async — use `tokio::task::spawn_blocking()`
- **Cancellation safety**: Futures can be dropped at any `.await` — design operations to be cancellation-safe (no partial side effects)
- **Holding resources across `.await`**: Locks, guards, `&mut` references often cause issues — scope them tightly
- **Forgotten `.await`**: Calling an `async fn` without awaiting does nothing

Red flags:
- Blocking I/O (`std::fs::read`, `std::net::TcpStream::connect`) in async functions
- `Mutex` guards or `&mut` references held across `.await`
- `tokio::spawn` with closures capturing non-`Send` types
- Unbounded channels (memory leak under load)

> Async patterns (good/bad): `examples/async.rs` · Advanced patterns reference: `references/async-rust-patterns.md`

---

## 10. API Design & Idiomatic Patterns

- Design ergonomic, hard-to-misuse APIs
- Use builder pattern, newtype wrappers, and sealed traits when appropriate
- Prefer composition over inheritance
- Follow Rust API Guidelines (rust-lang.github.io/api-guidelines)

Red flags:
- APIs that allow creating invalid states
- Methods with too many boolean parameters (use builder or enums)
- Public fields on structs that should be methods with validation

---

## Review Feedback Format

- 🔴 **Critical**: Must fix before merge (safety violations, data races, blocking in async)
- 🟡 **Suggestion**: Should improve (naming, idiomatic patterns, error handling)
- 🟢 **Nice to have**: Optional enhancement (performance, documentation, style)

Examples:
- 🔴 `unwrap()` on a fallible operation in production code
- 🔴 Blocking I/O call (`std::fs::read`) inside an async function
- 🔴 Shared mutable state accessed without `Arc<Mutex<T>>`
- 🟡 Unnecessary `.clone()` on `String` in a hot path
- 🟡 Missing `#[derive(Debug)]` on a public error type
- 🟡 Consider returning `impl Future` instead of an `async fn` for caller flexibility
- 🟢 Add a doc test example for this public function

---

## Common Review Workflow

1. Run `cargo fmt --check` — formatting violations are immediate flags
2. Run `cargo clippy --all-targets --all-features` — catches idiomatic issues
3. Run `cargo test` — ensure tests pass
4. Run `cargo audit` — check for vulnerable dependencies
5. Review code against the checklist above

> If the code doesn't compile or tests don't pass, flag as 🔴 before reviewing other concerns.

---

## Bundled Reference Files

- `examples/ownership.rs` — Ownership, borrowing, smart pointer, lifetime examples
- `examples/error-handling.rs` — thiserror/anyhow, Result patterns, make-invalid-states-unrepresentable
- `examples/async.rs` — Async patterns: executor safety, cancellation safety, channels, select!/join!
- `examples/testing.rs` — Unit, integration, doc test, and property-based testing patterns
- `references/async-rust-patterns.md` — Runtime selection, task management, cancellation safety, profiling
- `references/unsafe-rules.md` — Unsafe review checklist, SAFETY comment patterns, FFI guidelines
- `references/performance-guide.md` — Zero-cost abstractions, memory layout, string handling, profiling tools

---

## General Mindset

- Let the compiler guide development — if it compiles cleanly with few warnings, you're on the right track
- Start simple, iterate, and refactor fearlessly thanks to strong type safety
- Read and study high-quality open-source crates for patterns
- Balance safety, performance, and ergonomics based on project needs
- The Rust community values clarity, safety, and practicality above cleverness
