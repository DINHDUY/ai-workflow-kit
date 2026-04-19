# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `.github/agents/` workflow builder agents: `workflow.builder`, `workflow.documenter`,
  `workflow.orchestrator`, `workflow.planner`, `workflow.researcher`
- `LICENSE` file (MIT)
- `author`, `homepage`, `repository`, and `bugs` fields in `package.json`

## [1.0.0] - 2026-03-01

### Added

- `add-skills` command: scaffold a skill template (`.md` + optional `scripts/`) into your project
- `add-commands` command: scaffold an AI-agent command (`.md` + optional scripts) into your project
- `add-workflows` command: scaffold a multi-agent workflow (agent files + docs) into your project
- Shared CLI options: `--output`, `--force`, `--dry-run`
- Built-in skills: `abc`, `auditing-agent-skill`, `creating-new-skill`, `reviewing-agent-skill`,
  `submitting-pr`, `template`
- Built-in commands: `abc`, `docx-to-markdown`, `markdown-to-outlook-html`
- Built-in workflows: `builder`, `maf`, `nextjs`, `prodify`, `scrapy`, `speckit`
- TypeScript source with ESM output targeting Node.js 22+
- `bin` entries: `ai-workflow-kit`, `add-skills`, `add-commands`, `add-workflows`

[Unreleased]: https://github.com/DINHDUY/ai-workflow-kit/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/DINHDUY/ai-workflow-kit/releases/tag/v1.0.0
