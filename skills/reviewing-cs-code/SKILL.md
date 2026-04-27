---
name: reviewing-cs-code
description: Review C# code for quality, architecture, and maintainability following SOLID principles, Clean Architecture, and Domain-Driven Design. Use when reviewing C# code, pull requests, or when the user asks for C# code review, .NET standards, or architectural guidance.
file_scopes:
  - "**/*.cs"
metadata:
  category: code-review
  stack: C# .NET 10
---

# C# Code Review

Apply these standards when reviewing C# code. Core rules are inline; load reference files for detail when needed.

---

## Review Checklist

```
- [ ] Coding style follows Microsoft conventions
- [ ] Naming conventions are correct
- [ ] SOLID principles are applied (no NotImplementedException, no fat interfaces)
- [ ] Clean Architecture layers are respected (no cross-layer leaks)
- [ ] Async/await patterns are correct (no .Result, no missing CancellationToken)
- [ ] Error handling uses custom exception types and structured logging
- [ ] Logging is appropriate and secure (no PII, no secrets)
- [ ] Dependency injection is properly used (constructor injection only)
- [ ] DDD patterns are correctly implemented (rich entities, not anemic)
- [ ] Security: inputs validated, no sensitive data in logs/responses
- [ ] Tests exist: unit + integration, ≥90% coverage for business logic
- [ ] DRY: no duplicated logic, shared utilities used
- [ ] Public APIs have XML doc comments
- [ ] No performance anti-patterns (blocking calls, unbounded queries)
```

---

## 1. Coding Style

Core rules:
- `var` only when type is obvious from the right side; explicit types for primitives
- PascalCase: classes, methods, properties, interfaces; camelCase: parameters, locals; `_camelCase`: private fields
- File-scoped namespaces; `readonly` for unchanged fields; no regions; no magic strings
- String interpolation over concatenation; `using` for disposables

Modern C# 14 / .NET 10 — flag under-use:
- Nullable reference types MUST be enabled (`<Nullable>enable</Nullable>`)
- Primary constructors for simple DTOs/records
- Pattern matching over chains of `if`/`as` casts
- `Span<T>` / `Memory<T>` for hot-path memory operations
- `System.Text.Json` (not Newtonsoft) for serialization

---

## 2. Naming Conventions

| Element | Pattern | Example |
|---------|---------|---------|
| Interface | `I` prefix | `IOrderRepository` |
| Async method | `Async` suffix | `GetOrderAsync` |
| Event | Past tense | `OrderPlaced` |
| Domain entity | Noun | `Order`, `Customer` |
| Repository | `Repository` suffix | `OrderRepository` |
| DTO | `Dto` suffix | `OrderDto` |
| Command / Query / Handler | Type suffix | `CreateOrderCommand`, `GetOrderQuery`, `CreateOrderHandler` |

---

## 3. SOLID Principles

- **SRP**: Each class has one reason to change — flag classes with mixed concerns
- **OCP**: Extend via new implementations, not by modifying existing classes
- **LSP**: Implementations MUST NOT throw `NotImplementedException` — honor the full contract
- **ISP**: Prefer small, focused interfaces (`IReadable`, `IWritable`) over fat ones
- **DIP**: All dependencies injected via constructor; depend on abstractions, not concretions

> Detail + examples: `references/solid-principles.md` · `examples/solid.cs`

---

## 4. Clean Architecture

```
API/UI → Application → Domain (no deps)
                    ↑ implemented by Infrastructure
```

- **Domain**: NO EF Core attributes, NO persistence, NO external dependencies
- **Application**: depends ONLY on Domain; contains commands, queries, handlers, DTOs
- **Infrastructure**: EF Core, external services, repository implementations
- **API**: thin controllers only — NO business logic, NO direct repository calls

> Layer rules, red flags, examples: `references/clean-architecture.md` · `examples/clean-arch.cs`

---

## 5. Async/Await

- All I/O MUST be async
- NEVER use `.Result`, `.Wait()`, `.GetAwaiter().GetResult()`
- Async methods MUST end with `Async` and ALWAYS accept `CancellationToken`
- Use `ConfigureAwait(false)` in library/infrastructure code (not in ASP.NET Core)

> Patterns and deadlock-prone examples: `examples/async-patterns.cs`

---

## 6. Error Handling

- Use custom exception types for domain errors (e.g., `OrderNotFoundException : DomainException`)
- NEVER swallow exceptions silently — always log before rethrowing
- NO stack traces returned to API callers
- Log with appropriate severity: Warning for domain/validation, Error for unexpected exceptions

> Patterns, anti-patterns, API mapping: `references/error-handling.md` · `examples/error-handling.cs`

---

## 7. Logging

Never log: passwords, PII, API keys, credit card numbers.
Use structured logging with message templates.

| Level | Use For |
|-------|---------|
| Trace | Detailed diagnostics |
| Debug | Development-only |
| Information | Normal flow, key events |
| Warning | Recoverable issues, validation failures |
| Error | Failures requiring attention |
| Critical | System-wide failures |

Red flags: empty catch blocks, static logger instances.

---

## 8. Dependency Injection

- Constructor injection only — NO service locator
- Register abstractions, not concrete types
- Null-check injected dependencies in constructor
- Flag classes with >3–4 constructor dependencies (class doing too much)

| Lifetime | Use For |
|----------|---------|
| `AddScoped` | Business services, repositories (per-request) |
| `AddTransient` | Stateless, lightweight services |
| `AddSingleton` | Thread-safe, immutable services only |

Red flags: singleton with scoped dependency (captive dep), `new OrderService()` inline.

---

## 9. Security

Quick flags:
- Unvalidated inputs at service/API boundaries
- Sensitive data (tokens, PII) in logs or error responses
- Missing HTTPS, rate limiting, or CORS configuration
- Non-cryptographic session IDs; SQL string interpolation (injection risk)

> Full checklist with code examples: `references/security-checklist.md`

---

## 10. Testing

- Minimum **90% coverage** for domain + application layers
- Stack: **xUnit + FluentAssertions + Moq**; Arrange-Act-Assert pattern
- Required: Unit, Integration, Contract tests

> Standards, tooling, full examples: `references/testing-standards.md`

---

## 11. DRY Principle

- After the second occurrence of similar logic, refactor to a shared component
- Use FluentValidation validators (not per-handler null checks)
- Base repository patterns for common CRUD; extension methods for cross-cutting logic

> Patterns with examples: `references/dry-principle.md`

---

## 12. Documentation

All public APIs MUST have XML doc comments: `<summary>`, `<param>`, `<returns>`, `<exception>`.

> Templates and anti-patterns: `references/documentation.md`

---

## 13. Performance

| Operation | Target |
|-----------|--------|
| Simple queries / lookups | <200ms p95 |
| Complex operations | <500ms p95 |
| Operations >2s | MUST use streaming (`IAsyncEnumerable` / SSE) |

Red flags: unbounded `ToList()`, no connection pooling, large synchronous payloads.

---

## 14. Domain-Driven Design

- **Entities**: strongly-typed identity; behavior-rich (not anemic); encapsulate business rules
- **Value Objects**: immutable `record` types; equality by value
- **Aggregates**: enforce invariants; modifications through aggregate root only
- **Domain Events**: immutable `record` types; handlers in Application layer
- **Repositories**: return domain objects (not EF entities); intention-revealing method names

> Full patterns with code: `references/ddd-patterns.md` · `examples/ddd-entity.cs`

---

## Review Feedback Format

- 🔴 **Critical**: Must fix before merge (architectural violations, security issues)
- 🟡 **Suggestion**: Should improve (naming, code clarity)
- 🟢 **Nice to have**: Optional enhancement (performance, style)

Examples:
- 🔴 Domain entity has EF Core `[Column]` attribute — remove it
- 🔴 Input parameter not validated at service boundary
- 🟡 Async method missing `CancellationToken` parameter
- 🟡 `NotImplementedException` in interface implementation (LSP violation)
- 🟢 Consider `record` for immutable DTO

---

## Common Architectural Violations

1. Domain depending on Infrastructure — EF Core attributes on domain entities
2. Application layer bypassed — controllers calling repositories or containing business logic
3. Anemic domain model — entities with only getters/setters
4. Incorrect DI lifetimes — singleton with scoped dependency (captive dependency)
5. Missing async/await — `.Result`, `.Wait()`, synchronous I/O
6. Security gaps — unvalidated inputs, sensitive data in logs
7. Inadequate tests — missing unit tests, <90% coverage for business logic
