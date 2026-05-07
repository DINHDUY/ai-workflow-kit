// Error Handling — Code Examples
// Rule: use Result<T, E> + ?, thiserror for libs, anyhow for apps

// ── Library error types with thiserror ─────────────────────────────────

use thiserror::Error;

#[derive(Error, Debug)]
pub enum LibraryError {
    // ✅ Good: domain-specific error variants with contextual fields
    #[error("invalid user ID: {0}")]
    InvalidUserId(String),

    #[error("database connection failed: {0}")]
    DbConnection(#[from] sqlx::Error),

    #[error("serialization error: {0}")]
    Serialization(#[from] serde_json::Error),

    // ✅ Good: custom error that enforces invariants
    #[error("balance must be non-negative, got: {0}")]
    NegativeBalance(i64),
}

// ── Application error types with anyhow ────────────────────────────────

use anyhow::{Context, Result};

async fn fetch_user_data_bad(user_id: i32) -> Result<String> {
    // ❌ Bad: generic anyhow error, loses context
    let data = fetch_from_api(user_id).await?;
    Ok(data)
}

async fn fetch_user_data_good(user_id: i32) -> Result<String> {
    // ✅ Good: structured context via .context()
    let data = fetch_from_api(user_id)
        .await
        .with_context(|| format!("failed to fetch user data for ID {}", user_id))?;
    Ok(data)
}

// ── Bad: unwrap() in production code ──────────────────────────────────

fn parse_config_bad(path: &str) -> Config {
    let content = std::fs::read_to_string(path).unwrap(); // ❌ Panics on missing file
    let parsed: Config = serde_json::from_str(&content).unwrap(); // ❌ Panics on bad JSON
    parsed
}

fn parse_config_better(path: &str) -> Result<Config> {
    // ✅ Better: return Result instead of panicking
    let content = std::fs::read_to_string(path)?;
    let parsed: Config = serde_json::from_str(&content)?;
    Ok(parsed)
}

fn parse_config_best(path: &str) -> Result<Config> {
    // ✅ Best: unwrap() only at program boundaries where panic is acceptable
    parse_config_better(path)
        .context("failed to load application configuration")
        .expect("application cannot start without configuration")
}

// ── Bad: Silent error swallowing ───────────────────────────────────────

fn process_bad(data: &[u8]) -> Option<String> {
    // ❌ Bad: silently returns None on error
    let text = std::str::from_utf8(data).ok()?;
    Some(text.to_string())
}

// ── Good: Explicit error propagation ───────────────────────────────────

fn process_good(data: &[u8]) -> Result<String, std::str::Utf8Error> {
    // ✅ Good: error propagates to caller
    let text = std::str::from_utf8(data)?;
    Ok(text.to_string())
}

// ── Bad: expect() with unhelpful message ──────────────────────────────

fn get_first_bad(items: &[i32]) -> i32 {
    items.first().copied().expect("error") // ❌ Vague message
}

// ── Good: expect() with specific message (only at boundaries) ──────────

fn get_first_good(items: &[i32]) -> i32 {
    items
        .first()
        .copied()
        .expect("expected at least one item in the results list") // ✅ Specific
}

// ── Good: Custom error from library error using thiserror #[from] ─────

#[derive(Error, Debug)]
pub enum AppError {
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),

    #[error("parse error: {0}")]
    Parse(#[from] LibraryError),
}

// ── Making invalid states unrepresentable ─────────────────────────────

// ❌ Bad: Boolean flag that can be inconsistent with value
struct BadBalance {
    amount: i64,
    is_positive: bool, // Can be set incorrectly
}

// ✅ Good: Separate types enforce the invariant at compile time
#[derive(Debug, Clone, Copy, PartialEq)]
enum Sign {
    Positive(i64),
    Negative(i64),
}

struct GoodBalance {
    amount: Sign, // Cannot be negative without using the Negative variant
}

impl GoodBalance {
    fn new(amount: i64) -> Self {
        let sign = if amount >= 0 {
            Sign::Positive(amount)
        } else {
            Sign::Negative(amount.abs())
        };
        Self { amount: sign }
    }
}
