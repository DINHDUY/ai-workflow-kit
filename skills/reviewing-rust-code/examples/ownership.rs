// Ownership & Borrowing — Code Examples
// Rule: embrace move semantics, use references, let the compiler elide lifetimes

// ── Bad: Unnecessary clone in hot path ──────────────────────────────────

fn process_items_bad(items: &[String]) -> Vec<String> {
    // ❌ Bad: Cloning every item when a reference would suffice
    let mut result = Vec::new();
    for item in items {
        let owned = item.clone(); // Unnecessary heap allocation
        result.push(owned.to_uppercase());
    }
    result
}

// ── Good: Work with references ─────────────────────────────────────────

fn process_items_good(items: &[String]) -> Vec<String> {
    // ✅ Good: Use &str to avoid allocation
    items
        .iter()
        .map(|s| s.to_uppercase())
        .collect()
}

// ── Bad: Multiple mutable borrows ───────────────────────────────────────

fn modify_twice_bad(data: &mut Vec<i32>) {
    let a = &mut data[0];
    let b = &mut data[1]; // ❌ Bad: two mutable borrows, even if non-overlapping
    *a += 1;
    *b += 2;
}

// ── Good: Sequential mutable access ────────────────────────────────────

fn modify_twice_good(data: &mut Vec<i32>) {
    // ✅ Good: Sequential mutable borrows are allowed
    data[0] += 1;
    data[1] += 2;
}

// ── Bad: Storing references without lifetime annotations ───────────────

struct BadConfig {
    // ❌ Bad: missing lifetime annotation
    // name: &str,  // won't compile
    // value: &str, // won't compile
    name: String,  // works but unnecessary copy
    value: String,
}

// ── Good: Proper lifetime elision ──────────────────────────────────────

struct GoodConfig<'a> {
    // ✅ Good: lifetime elision — the compiler knows there's one input, one output
    name: &'a str,
    value: &'a str,
}

impl<'a> GoodConfig<'a> {
    fn new(name: &'a str, value: &'a str) -> Self {
        Self { name, value }
    }
}

// ── Bad: clone() on String instead of using &str ───────────────────────

fn greet_bad(name: String) -> String {
    // ❌ Bad: takes ownership of String, forces caller to clone or move
    format!("Hello, {}!", name)
}

// ── Good: borrow with &str ────────────────────────────────────────────

fn greet_good(name: &str) -> String {
    // ✅ Good: accepts any string-like type via &str
    format!("Hello, {}!", name)
}

// ── Bad: clone() on Vec in a loop ─────────────────────────────────────

fn duplicate_vectors_bad(vectors: &[Vec<i32>]) -> Vec<Vec<i32>> {
    // ❌ Bad: unnecessary deep clone
    let mut result = Vec::new();
    for v in vectors {
        result.push(v.clone());
    }
    result
}

// ── Good: use references or move semantics ─────────────────────────────

fn duplicate_vectors_good(vectors: Vec<Vec<i32>>) -> Vec<Vec<i32>> {
    // ✅ Good: if caller doesn't need the original, take ownership (move)
    vectors // Move semantics — zero cost
}

// ── Smart pointer selection guide ─────────────────────────────────────

// Use Box<T> when:
//   - Size is unknown at compile time
//   - You want heap allocation with single ownership
// Use Rc<T> when:
//   - Single-threaded shared ownership
// Use Arc<T> when:
//   - Multithreaded shared ownership (requires T: Send + Sync)
// Use RefCell<T> / Mutex<T> when:
//   - Interior mutability needed (borrow rules at runtime)
