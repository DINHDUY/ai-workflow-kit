# reviewing-cs-code

C# code review skill covering SOLID principles, Clean Architecture, DDD, async patterns, security, testing, and .NET 10 conventions.

## Usage

Activates automatically when reviewing `.cs` files or pull requests. Invoke explicitly with:

```
/reviewing-cs-code
```

Or say: *"Review this C# code"* / *"Check this PR against our .NET standards"*

## Structure

```
reviewing-cs-code/
├── SKILL.md              # Core rules and review checklist (loaded on activation)
├── references/           # Deep-dive guides (loaded on demand)
│   ├── solid-principles.md
│   ├── clean-architecture.md
│   ├── ddd-patterns.md
│   ├── error-handling.md
│   ├── security-checklist.md
│   ├── testing-standards.md
│   ├── dry-principle.md
│   └── documentation.md
└── examples/             # Annotated C# code examples (loaded on demand)
    ├── solid.cs
    ├── async-patterns.cs
    ├── error-handling.cs
    └── ddd-entity.cs
```

## What It Reviews

| Area | Standards Applied |
|------|------------------|
| Architecture | Clean Architecture layers, dependency direction |
| Design | SOLID principles, DDD patterns, DRY |
| C# style | Microsoft conventions, C# 14 / .NET 10 features |
| Async | `async`/`await`, `CancellationToken`, no `.Result` |
| Security | Input validation, logging hygiene, OWASP basics |
| Testing | xUnit + FluentAssertions + Moq, ≥90% business logic coverage |
| Documentation | XML doc comments on all public APIs |

## Feedback Format

- 🔴 **Critical** — must fix before merge
- 🟡 **Suggestion** — should improve
- 🟢 **Nice to have** — optional enhancement
