## C# Code Review Skill

On-demand skill for reviewing C# code against SOLID principles, Clean Architecture, DDD patterns, async conventions, security, and .NET 10 standards. Activates automatically on `.cs` files or when a review is requested.

## What It Does

Reviews C# code across these areas:

1. **Architecture** — Clean Architecture layer rules, dependency direction
2. **Design** — SOLID principles, DDD patterns (entities, aggregates, repositories)
3. **Style** — Microsoft conventions, C# 14 / .NET 10 features, naming
4. **Async** — `async`/`await`, `CancellationToken`, no `.Result`/`.Wait()`
5. **Security** — Input validation, logging hygiene, OWASP basics
6. **Testing** — xUnit + FluentAssertions + Moq, ≥90% business logic coverage

## Get It

**For Cursor:**
```bash
uvx --from git+https://github.com/DINHDUY/ai-workflow-kit-py ^
    add-skill reviewing-cs-code --output .cursor/skills
```

**For Claude:**
```bash
uvx --from git+https://github.com/DINHDUY/ai-workflow-kit-py ^
    add-skill reviewing-cs-code --output .claude/skills
```

## Use It

Skills load on demand — either automatically when you open a `.cs` file and ask a question, or explicitly.

**Use the slash shortcut (explicit):**

Type `/` in the chat input, start typing the skill name, select it, then type your request.

```
/reviewing-cs-code Review OrderService.cs for SOLID violations
```

**Use natural language (agent picks it up automatically):**

```
Review this C# pull request for Clean Architecture violations
```

```
Check if this Order entity follows DDD best practices
```

Both work. The slash form is reliable when you want the skill every time. Natural language works when context makes the intent clear.

**Feedback comes back as:**

```
🔴 Critical   — must fix before merge  (architectural violations, security)
🟡 Suggestion — should improve         (naming, code clarity)
🟢 Nice to have — optional             (performance, style)
```

> **Good to know:** Reference files and code examples inside the skill load only when needed, so your context window stays lean regardless of how many standards are defined.

## More

- [skills/reviewing-cs-code/README.md](../skills/reviewing-cs-code/README.md)
- [skills/reviewing-cs-code/SKILL.md](../skills/reviewing-cs-code/SKILL.md)
