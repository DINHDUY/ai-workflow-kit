# Commitizen Commit Types

Format: `<type>[optional scope]: <description>`

- Description must be lowercase, imperative mood, no trailing period.
- Scope is optional and goes in parentheses: `feat(auth): add OAuth2 login`

## Examples

```
feat: add dark mode toggle
fix(api): handle null response from payment service
docs: update README with local setup instructions
refactor(db): extract query builder into separate module
chore: bump eslint to v9
```

## Type Reference

| Type | When to use |
|---|---|
| `feat` | New feature visible to users |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting, whitespace — no logic change |
| `refactor` | Code restructure with no feature or fix |
| `perf` | Performance improvement |
| `test` | Adding or correcting tests |
| `build` | Build system or dependency changes |
| `ci` | CI/CD configuration changes |
| `chore` | Maintenance tasks, tooling, non-src changes |
| `revert` | Revert a previous commit |

## Inferring Type from a Set of Commits

When multiple commits are being squashed, pick the **highest-priority type** present:

`feat` > `fix` > `refactor` > `perf` > `test` > `docs` > `style` > `build` > `ci` > `chore` > `revert`

If the commits span multiple unrelated types, default to `feat` (if any feature work exists) or `fix`.
`revert` should only be used when the entire squash represents an undo of a previous commit.
