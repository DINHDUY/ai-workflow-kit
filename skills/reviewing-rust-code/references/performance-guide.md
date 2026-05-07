# Rust Performance Review Guide

Guidelines for reviewing performance-critical Rust code.

## Zero-Cost Abstractions

### Prefer Iterators Over Loops

```rust
// ❌ Bad: Manual indexing
let mut results = Vec::new();
for i in 0..items.len() {
    if items[i] > threshold {
        results.push(items[i] * 2);
    }
}

// ✅ Good: Iterator chain — zero overhead after optimization
let results: Vec<_> = items
    .iter()
    .filter(|&&x| x > threshold)
    .map(|&x| x * 2)
    .collect();
```

### Avoid Unnecessary Allocations

```rust
// ❌ Bad: Allocates new String each iteration
let mut output = String::new();
for s in items {
    output.push_str(&format!("{}: {}\n", key, s));
}

// ✅ Good: Reuse buffer with write!
let mut output = String::with_capacity(total_size);
for s in items {
    write!(output, "{}: {}\n", key, s).unwrap();
}

// ✅ Better: Use &str to avoid allocation entirely
fn process(item: &str) { ... }
```

## Memory Layout

### Struct Field Ordering

```rust
// ❌ Bad: Padding waste (16 bytes on 64-bit)
struct BadLayout {
    a: u8,    // 1 byte + 7 bytes padding
    b: u64,   // 8 bytes
    c: u32,   // 4 bytes + 4 bytes padding
} // Total: 24 bytes (wastes 11 bytes to padding)

// ✅ Good: Sorted by size — minimal padding
struct GoodLayout {
    b: u64,   // 8 bytes
    c: u32,   // 4 bytes
    a: u8,    // 1 byte + 3 bytes padding
} // Total: 16 bytes
```

### Stack vs Heap

| Use Stack When | Use Heap When |
|---------------|---------------|
| Size is known and small | Size is large or unknown |
| Short-lived data | Data outlives current scope |
| Single ownership | Shared ownership needed |

## String Handling

| Operation | Fast | Slow |
|-----------|------|------|
| Read-only access | `&str` | `String` |
| Single allocation | `String::with_capacity()` | Repeated `push_str` |
| Formatting | `write!` into pre-allocated | Repeated `format!` concat |
| Binary data | `bytes::Bytes` | `Vec<u8>` |

## Collection Performance

```rust
// ❌ Bad: Collecting before filtering
let result: Vec<_> = items.iter()
    .filter(|x| x.valid())
    .collect()
    .iter()
    .map(|x| x.compute())
    .collect(); // Two allocations

// ✅ Good: Single iterator chain
let result: Vec<_> = items.iter()
    .filter(|x| x.valid())
    .map(|x| x.compute())
    .collect(); // One allocation
```

## Profiling Tools

| Tool | Use For | Command |
|------|---------|---------|
| `cargo flamegraph` | CPU hotspots | `cargo flamegraph --bin myapp` |
| `tokio-console` | Async task inspection | `tokio-console` |
| `criterion` | Benchmarking | `cargo bench` |
| `perf` | System-level profiling | `perf record` |
| `tracing` | Structured observability | `tracing-subscriber` |

## Review Checklist

- [ ] No unnecessary allocations in hot paths
- [ ] Iterators used instead of manual indexing where appropriate
- [ ] Struct fields ordered by size for cache locality
- [ ] `&str`/`&[T]` used instead of owned types for read-only access
- [ ] `String::with_capacity()` used when final size is known
- [ ] No blocking I/O in async code
- [ ] Async code offloads CPU work via `spawn_blocking()`
- [ ] Profiling done before optimization (measure first)
