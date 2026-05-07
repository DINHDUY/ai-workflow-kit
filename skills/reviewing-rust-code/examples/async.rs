// Async Rust — Code Examples
// Rule: async is cooperative, never block the executor, cancellation-safe

use tokio::time::{sleep, timeout, Duration};

// ── Bad: Blocking I/O in async context ─────────────────────────────────

async fn read_file_bad(path: &str) -> String {
    // ❌ Bad: blocks the entire async runtime thread
    let content = std::fs::read_to_string(path).unwrap();
    content
}

// ── Good: Async I/O with Tokio ────────────────────────────────────────

async fn read_file_good(path: &str) -> Result<String, std::io::Error> {
    // ✅ Good: non-blocking I/O
    tokio::fs::read_to_string(path).await
}

// ── Bad: Blocking CPU work in async ───────────────────────────────────

async fn compute_bad(n: u64) -> u64 {
    // ❌ Bad: heavy computation blocks the executor
    let mut result = 0u64;
    for i in 0..n {
        result = result.wrapping_add(i);
    }
    result
}

// ── Good: Offload blocking work to spawn_blocking ─────────────────────

async fn compute_good(n: u64) -> u64 {
    // ✅ Good: offload CPU-bound work
    tokio::task::spawn_blocking(move || {
        let mut result = 0u64;
        for i in 0..n {
            result = result.wrapping_add(i);
        }
        result
    })
    .await
    .expect("spawn_blocking panicked")
}

// ── Bad: Holding lock across .await ───────────────────────────────────

async fn update_and_query_bad(
    data: Arc<Mutex<Vec<String>>>,
    query: &str,
) -> Option<String> {
    let mut guard = data.lock().await;
    guard.push(query.to_string());
    // ❌ Bad: MutexGuard held across .await — blocks other tasks
    let result = find_in_db(query).await;
    drop(guard); // Manual drop doesn't help — guard is still in scope
    result
}

// ── Good: Scope lock tightly ─────────────────────────────────────────

async fn update_and_query_good(
    data: Arc<Mutex<Vec<String>>>,
    query: &str,
) -> Option<String> {
    {
        let mut guard = data.lock().await;
        guard.push(query.to_string());
    } // ✅ Guard dropped here, before .await
    find_in_db(query).await
}

// ── Bad: Forgetting .await ────────────────────────────────────────────

async fn fire_and_forget_bad(client: &HttpClient) {
    // ❌ Bad: this creates a future but never awaits it — does nothing!
    client.send_request(Request::new());
}

// ── Good: Properly await ─────────────────────────────────────────────

async fn fire_and_forget_good(client: &HttpClient) {
    client.send_request(Request::new()).await; // ✅ Awaited
}

// ── Bad: Unbounded channel — memory leak under load ───────────────────

async fn unbounded_channel_bad() {
    let (tx, mut rx) = tokio::sync::mpsc::unbounded_channel(); // ❌ Unbounded
    for i in 0..10000 {
        tx.send(i).unwrap(); // Will never block, memory grows unbounded
    }
}

// ── Good: Bounded channel with backpressure ───────────────────────────

async fn bounded_channel_good() {
    let (tx, mut rx) = tokio::sync::mpsc::channel(64); // ✅ Bounded — backpressure
    for i in 0..10000 {
        if tx.send(i).await.is_err() {
            break; // ✅ Producer blocks when channel is full
        }
    }
}

// ── Bad: Cancellation-unsafe operation ────────────────────────────────

async fn transfer_bad(from: Account, to: Account, amount: i64) -> Result<(), Error> {
    // ❌ Bad: if dropped mid-operation, money disappears
    from.withdraw(amount); // Side effect before .await
    sleep(Duration::from_millis(100)).await; // If cancelled here, money is gone
    to.deposit(amount); // Never executes on cancellation
    Ok(())
}

// ── Good: Cancellation-safe design ────────────────────────────────────

async fn transfer_good(
    from: Account,
    to: Account,
    amount: i64,
) -> Result<(), Error> {
    // ✅ Good: atomic operation — either both happen or neither
    let (tx, mut rx) = tokio::sync::mpsc::channel(1);

    let withdraw_task = tokio::spawn(async move {
        from.withdraw(amount).await
    });

    let deposit_task = tokio::spawn(async move {
        to.deposit(amount).await
    });

    let withdraw_result = withdraw_task.await?;
    let deposit_result = deposit_task.await?;

    // ✅ Both succeed or both fail — no partial state
    Ok(())
}

// ── Good: Using select! for racing futures ───────────────────────────

async fn query_with_timeout(
    db: &Database,
    query: &str,
) -> Result<String, Error> {
    tokio::select! {
        result = db.query(query) => {
            result // ✅ Query completed
        }
        _ = sleep(Duration::from_secs(5)) => {
            Err(Error::Timeout) // ✅ Timeout handled
        }
    }
}

// ── Good: Using join! for concurrent independent work ─────────────────

async fn fetch_all_bad(ids: &[i32]) -> Vec<String> {
    // ❌ Bad: sequential awaits
    let mut results = Vec::new();
    for id in ids {
        let data = fetch_data(*id).await;
        results.push(data);
    }
    results
}

async fn fetch_all_good(ids: &[i32]) -> Vec<String> {
    // ✅ Good: concurrent fetching
    let futures: Vec<_> = ids.iter().map(|id| fetch_data(*id)).collect();
    futures::future::join_all(futures).await
}

// ── Good: Returning impl Future for flexibility ───────────────────────

// ❌ Bad: async fn forces a concrete return type
// async fn get_user(id: i32) -> Result<User, Error> { ... }

// ✅ Good: impl Future allows caller to choose async or sync wrapper
fn get_user(id: i32) -> impl Future<Output = Result<User, Error>> + Send {
    async move {
        let user = fetch_user_from_db(id).await?;
        Ok(user)
    }
}

// ── Good: Boxing large futures ───────────────────────────────────────

fn large_future() -> Pin<Box<dyn Future<Output = i32> + Send>> {
    // ✅ Good: boxed future when state machine is too large for stack
    Box::pin(async {
        // Large captured state — would blow stack without Box::pin
        let data = vec![0u8; 1024 * 1024]; // 1MB captured
        process_large_buffer(&data).await
    })
}

// ── Good: Current-thread vs multi-thread runtime selection ────────────

// Use current_thread for simple single-threaded apps (simpler debugging)
// #[tokio::main(flavor = "current_thread")]
// async fn main() { ... }

// Use multi_thread for production I/O workloads
// #[tokio::main(flavor = "multi_thread", worker_threads = 4)]
// async fn main() { ... }
