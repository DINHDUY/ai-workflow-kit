# Create PR

## Objective
Create a well-structured pull request
for the current branch changes.

## Steps
1. Run `git diff main..HEAD` to review
   all changes in this branch
2. Analyze the intent behind the changes
3. Check for anything missing (tests,
   docs, migration files)
4. Create a conventional commit message
   if needed
5. Generate a PR description

## PR Description Template
## Summary
[2-3 sentence explanation of the change]

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Refactor
- [ ] Docs / chore

## What Changed
- [bullet 1]
- [bullet 2]

## Testing
[How this was verified]

## Screenshots
[If UI changes apply]

## Conventional Commit Format
feat(scope): title
fix(scope): title
refactor(scope): title
chore(scope): title