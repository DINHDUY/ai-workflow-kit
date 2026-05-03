# Changelog

All notable changes to this project will be documented in this file.

# [1.1.0](https://github.com/DINHDUY/ai-workflow-kit/compare/v1.0.0...v1.1.0) (2026-05-03)


### Features

* add workflow_dispatch to release workflow ([43eca30](https://github.com/DINHDUY/ai-workflow-kit/commit/43eca307a58532dc06b2c294be9291cbe5488780))

# 1.0.0 (2026-05-03)


### Features

* add claude-packager and maf-packager workflows ([e437454](https://github.com/DINHDUY/ai-workflow-kit/commit/e437454e54e665a3806266d635dd4fb6adceba97))
* add creating course html and reviewing cs code ([bd3c9b1](https://github.com/DINHDUY/ai-workflow-kit/commit/bd3c9b136a27066b4c774fbadde4b6e0c0765b38))
* add Cursor IDE command files ([9cf8f3e](https://github.com/DINHDUY/ai-workflow-kit/commit/9cf8f3eae7610c0e939f783ebb00474379f7ceca))
* add day trading workflows ([4e98aa8](https://github.com/DINHDUY/ai-workflow-kit/commit/4e98aa8592e94f19b5d31af70135c494e19be75c))
* add pbk/agents ([01135ea](https://github.com/DINHDUY/ai-workflow-kit/commit/01135ea37ce274ad49762a90f3d921e21bdbcb7d))
* add software-factory workflow ([abcc083](https://github.com/DINHDUY/ai-workflow-kit/commit/abcc083c41df0e4f8b036e3c5d5b2a8f3eb3f1e3))
* add software-factory workflow ([048f226](https://github.com/DINHDUY/ai-workflow-kit/commit/048f22637d4248ec80678f18cefdeae00dfaf745))
* add software-factory workflow ([cf21efd](https://github.com/DINHDUY/ai-workflow-kit/commit/cf21efd23f3ea49822a5464fb0e1dc8594e7b831))
* add software-factory workflow ([c052c16](https://github.com/DINHDUY/ai-workflow-kit/commit/c052c160936ba939948e4676e79abc933c482f20))
* add tauri-codegen workflow ([f9b34ec](https://github.com/DINHDUY/ai-workflow-kit/commit/f9b34ec939ebe16cb6b23587525be1bfbca54450))
* MVP ([19d1ed1](https://github.com/DINHDUY/ai-workflow-kit/commit/19d1ed1fc0f99552a4f668269be530dc4d09dc19))
* MVP ([c07ae4e](https://github.com/DINHDUY/ai-workflow-kit/commit/c07ae4e25e14695f923d7a5bce8d3301abf34ef4))

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
