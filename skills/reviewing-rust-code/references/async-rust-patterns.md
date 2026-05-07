# Async Rust Patterns Reference

Detailed async Rust patterns for code review.

## Runtime Selection

| Runtime | Use When | Setup |
|---------|----------|-------|
| `tokio` | Most applications, default choice | `#[tokio::main]` |
| `current_thread` | Simple single-threaded apps, easier debugging | `#[tokio::main(flavor = "current_thread")]` |
| `async-std` | Standard-library-like API preference | Rarely needed |
| `glommio` | Ultra-low latency I/O, IO_uring | Specialized cases |

## Task Management

### Structured Concurrency (Preferred)

```rust
// Use join! for known, bounded set of tasks
let (a, b) = tokio::join!(task_a(), task_b());

// Use JoinSet for dynamic collections
let mut set = JoinSet::new();
for item in items {
    set.spawn(process_item(item));
}
while let Some(result) = set.join_next().await {
    handle_result(result);
}
```

### spawn (Use Sparingly)

```rust
// Only for fire-and-forget or truly concurrent work
tokio::spawn(async move {
    // Must be Send + 'static
});
```

## Channel Patterns

| Pattern | When |
|---------|------|
| Bounded `mpsc` | Default — backpressure under load |
| Unbounded `mpsc` | Producer count known and bounded |
| `watch` | Single value, last-writer-wins (config updates) |
| `broadcast` | Fan-out to multiple consumers (events) |

## Cancellation Safety Patterns

1. **Idempotent operations** — safe to retry on cancellation
2. **Transaction-based** — either complete or roll back
3. **Checkpoint-based** — save state before expensive `.await`

## Performance Tips

- Keep futures small — avoid capturing large structs by value
- Use `&str`/`&[T]` instead of owned types in futures when possible
- Prefer `tokio::sync::Mutex` only when holding across `.await`
- Use `std::sync::Mutex` for quick critical sections
- Profile with `tokio-console` + `cargo flamegraph`

## Common Pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| Blocking I/O in async | Thread starvation, latency spikes | `spawn_blocking()` |
| Large futures | Stack overflow | `Box::pin()` |
| Unbounded channels | OOM under load | Bounded channels |
| Holding locks across `.await` | Task blocking | Scope locks tightly |
| Missing `.await` | Silent no-op | Enable `clippy::future_not_send` lint |

## Testing Async Code

```rust
#[tokio::test]
async fn test_async_flow() {
    let result = do_async_work().await;
    assert_eq!(result, expected);
}
```

- Use `#[tokio::test]` for unit tests
- Spin up full runtime in integration tests
- Test with realistic concurrency levels
