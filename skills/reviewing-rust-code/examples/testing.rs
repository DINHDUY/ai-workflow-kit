// Testing — Code Examples
// Rule: unit + integration tests, doc tests for public APIs

// ── Bad: No tests for public function ─────────────────────────────────

pub fn calculate_discount(price: f64, code: &str) -> f64 {
    if code == "SAVE10" {
        price * 0.9
    } else if code == "SAVE20" {
        price * 0.8
    } else {
        price
    }
}

// No tests — ❌ Bad for a public function

// ── Good: Comprehensive unit tests ────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_save10_discount() {
        // ✅ Good: test the happy path
        let result = calculate_discount(100.0, "SAVE10");
        assert!((result - 90.0).abs() < f64::EPSILON);
    }

    #[test]
    fn test_save20_discount() {
        // ✅ Good: test another discount code
        let result = calculate_discount(200.0, "SAVE20");
        assert!((result - 160.0).abs() < f64::EPSILON);
    }

    #[test]
    fn test_no_discount() {
        // ✅ Good: test edge case — unknown code
        let result = calculate_discount(100.0, "INVALID");
        assert!((result - 100.0).abs() < f64::EPSILON);
    }

    #[test]
    fn test_zero_price() {
        // ✅ Good: test boundary condition
        let result = calculate_discount(0.0, "SAVE10");
        assert!((result - 0.0).abs() < f64::EPSILON);
    }

    #[test]
    #[should_panic]
    fn test_empty_code_panics() {
        // ✅ Good: document expected panic behavior
        calculate_discount(100.0, "");
    }
}

// ── Good: Doc test with examples ─────────────────────────────────────

/// Calculate the discounted price based on a promotion code.
///
/// # Examples
///
/// ```
/// use my_crate::calculate_discount;
///
/// let result = calculate_discount(100.0, "SAVE10");
/// assert!((result - 90.0).abs() < f64::EPSILON);
/// ```
///
/// # Panics
///
/// Panics if the discount code is empty.
pub fn calculate_discount_with_docs(price: f64, code: &str) -> f64 {
    if code.is_empty() {
        panic!("discount code cannot be empty");
    }
    match code {
        "SAVE10" => price * 0.9,
        "SAVE20" => price * 0.8,
        _ => price,
    }
}

// ── Bad: Integration test in wrong place ─────────────────────────────

// ❌ Bad: putting integration tests in src/lib.rs
// #[cfg(test)]
// mod integration_tests {
//     #[test]
//     fn test_full_flow() { ... }
// }

// ── Good: Integration test in tests/ directory ────────────────────────
// File: tests/integration_test.rs
//
// #[test]
// fn test_order_flow() {
//     // ✅ Good: black-box test — only uses public API
//     let client = Client::new();
//     let order = client.create_order(Order::new());
//     assert_eq!(order.status, OrderStatus::Created);
// }

// ── Good: Property-based testing with proptest ────────────────────────

// #[cfg(test)]
// mod prop_tests {
//     use proptest::prelude::*;
//
//     proptest! {
//         // ✅ Good: property test — generates many random inputs
//         #[test]
//         fn discount_is_always_less_than_original(
//             price in 0.0..10000.0,
//             code in r"SAVE\d+"
//         ) {
//             let result = calculate_discount(price, &code);
//             prop_assert!(result <= price);
//         }
//     }
// }

// ── Bad: Only testing happy path ─────────────────────────────────────

#[cfg(test)]
mod bad_test_suite {
    use super::*;

    #[test]
    fn test_valid_config() {
        // ❌ Bad: only happy path, no error cases
        let config = parse_config("valid_json");
        assert!(config.is_ok());
    }
}

// ── Good: Testing error paths ─────────────────────────────────────────

#[cfg(test)]
mod good_test_suite {
    use super::*;

    #[test]
    fn test_valid_config() {
        let config = parse_config("valid_json");
        assert!(config.is_ok());
    }

    #[test]
    fn test_invalid_json() {
        // ✅ Good: test error path
        let result = parse_config("invalid json{");
        assert!(result.is_err());
    }

    #[test]
    fn test_missing_field() {
        // ✅ Good: test partial/missing data
        let config = parse_config(r#"{"name": "test"}"#);
        assert!(result.is_err()); // Missing required "host" field
    }
}
