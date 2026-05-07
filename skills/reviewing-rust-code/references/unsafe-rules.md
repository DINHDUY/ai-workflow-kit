# Unsafe Rust Review Guidelines

Rules for reviewing `unsafe` code in Rust.

## Core Principle

> Minimize `unsafe` — always encapsulate behind safe APIs.

## When `unsafe` is Acceptable

1. **Raw pointer dereferencing** — when safe abstractions don't exist
2. **FFI boundaries** — interfacing with C/C++ libraries
3. **Memory management** — custom allocators, arena patterns
4. **Lock-free data structures** — atomics, concurrent data structures
5. **Zero-copy parsing** — memory-mapped files, binary protocols

## Review Checklist for `unsafe` Blocks

- [ ] `unsafe` block is minimal — only what's necessary is inside
- [ ] Safety invariants are documented in a `// SAFETY:` comment
- [ ] The block is encapsulated behind a `safe` wrapper function
- [ ] All uses of `unsafe` can be verified for correctness
- [ ] No `unsafe` inside loops without careful review

## Required `// SAFETY:` Comment Pattern

```rust
unsafe {
    // SAFETY: ptr is guaranteed to be valid and aligned because:
    // 1. It was created from a &reference in [function], which guarantees validity
    // 2. T is a primitive type with align_of::<T>() == 1
    *ptr = value;
}
```

## Common Unsafe Anti-Patterns

| Anti-Pattern | Why It's Bad | Fix |
|-------------|-------------|-----|
| Large `unsafe` blocks | Hard to verify, one bug breaks everything | Minimize scope |
| Missing SAFETY comments | Future reviewers can't verify correctness | Always document |
| Exposing `unsafe` internals | Users can trigger UB unknowingly | Wrap in safe API |
| `unsafe` in loops | Bugs compound, harder to reason about | Extract to function |
| Using `transmute` for type coercion | Undefined behavior on type mismatch | Use `cast` or `from_bits` |

## Prefer Safe Alternatives

```rust
// ❌ Bad: unsafe pointer cast
let value = unsafe { *(ptr as *const T) };

// ✅ Good: safe equivalent
let value = ptr.read(); // or ptr.as_ref().unwrap()
```

## FFI Guidelines

- Use `#[repr(C)]` on structs passed to FFI
- Validate all data from FFI before using it
- Document lifetime requirements clearly
- Use `unsafe trait` marker for FFI-safe traits

## Review Severity

- 🔴 **Critical**: `unsafe` without SAFETY comment, unsafe exposed without wrapper
- 🟡 **Suggestion**: `unsafe` block could be smaller, missing documentation
- 🟢 **Nice to have**: Alternative safe implementation exists
