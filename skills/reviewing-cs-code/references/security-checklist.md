# Security Checklist

## Input Validation

All inputs at service/API boundaries MUST be validated before processing.

```csharp
// ✅ Good — Validate at boundary
public async Task<Order> CreateOrderAsync(CreateOrderCommand command, CancellationToken ct)
{
    ArgumentException.ThrowIfNullOrWhiteSpace(command.CustomerId);
    ArgumentOutOfRangeException.ThrowIfNegativeOrZero(command.Amount);
    // Or use a FluentValidation validator injected via MediatR pipeline behavior
}

// ❌ Bad — No validation
public async Task<Order> CreateOrderAsync(CreateOrderCommand command, CancellationToken ct)
{
    var order = Order.Create(command.CustomerId, command.Amount); // CustomerId could be null/empty
}
```

---

## Full Security Checklist

### Input & Data
- [ ] All API/service parameters validated (null, range, format)
- [ ] User-generated content sanitized before storage or processing
- [ ] Parameterized queries used — no raw SQL with string interpolation
- [ ] No hardcoded secrets, connection strings, or API keys in source

### Logging & Error Responses
- [ ] No sensitive data (passwords, tokens, API keys, PII) in logs
- [ ] No sensitive data in error messages returned to callers
- [ ] Stack traces not exposed to API consumers

### Transport & Auth
- [ ] HTTPS required for all remote connections
- [ ] OAuth 2.1 with PKCE for remote / user-facing deployments
- [ ] Origin header validated for HTTP endpoints
- [ ] Rate limiting implemented on HTTP endpoints
- [ ] Local servers bind to `127.0.0.1`, not `0.0.0.0`

### Session & Identity
- [ ] Session IDs are cryptographically secure (not sequential integers)
- [ ] Session invalidated on logout / token expiry
- [ ] Principle of least privilege applied to service accounts

### Web / API
- [ ] CORS properly configured — no wildcard `*` in production
- [ ] CSRF protection on state-changing endpoints
- [ ] HTTP security headers set (HSTS, X-Content-Type-Options, etc.)

### Auditing
- [ ] All security-relevant events logged (auth failures, permission denied)
- [ ] Dependency versions audited for known CVEs

---

## Common C# Security Red Flags

```csharp
// ❌ SQL injection risk — raw string interpolation
var sql = $"SELECT * FROM Orders WHERE CustomerId = '{customerId}'";

// ✅ Use EF Core LINQ (parameterized by default)
var orders = await _context.Orders
    .Where(o => o.CustomerId == customerId)
    .ToListAsync(ct);

// ❌ Logging credentials
_logger.LogInformation("User {Email} logged in with password {Password}", email, password);

// ✅ Log identity, not credentials
_logger.LogInformation("Login attempt for user {UserId}", userId);

// ❌ Exposing internal details
catch (Exception ex) { return ex.StackTrace; }

// ✅ Clean message, full error in logs only
catch (Exception ex)
{
    _logger.LogError(ex, "Unexpected error for order {OrderId}", orderId);
    return "An error occurred processing your request.";
}
```
