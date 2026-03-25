# @dtranllc/ai-workflow-kit

Scaffold AI agent skills, commands, and workflows into your project with a single command.

## Install

```bash
npm install -g @dtranllc/ai-workflow-kit
```

Or run directly without installing:

```bash
npx @dtranllc/ai-workflow-kit <command> [options]
```

Or run straight from a GitHub repository:

```bash
npx github:DINHDUY/ai-workflow-kit <command> [options]
```

Replace `user` with the repository owner.

Requires Node.js 22 or later.

## Commands

All three commands share the same options:

| Option | Default | Description |
|--------|---------|-------------|
| `-o, --output <path>` | *(per command)* | Output directory |
| `-f, --force` | `false` | Overwrite existing files |
| `--dry-run` | `false` | Preview without writing |

### `add-skills`

Copy a skill template into your project. The `scripts/` subdirectory inside the bundle is copied to the project root `scripts/` directory.

```bash
npx @dtranllc/ai-workflow-kit add-skills <skillName> --output ./skills
```

### `add-commands`

Copy an AI-agent command (`.md` file + optional scripts) into your project.

```bash
npx @dtranllc/ai-workflow-kit add-commands <commandName> --output .cursor/commands
```

### `add-workflows`

Copy a multi-agent workflow into your project. Agent definition files are placed flat in the output directory; all other files go to `docs/workflows/<name>/`.

```bash
npx @dtranllc/ai-workflow-kit add-workflows <workflowName> --output .cursor/agents
```

## Available Resources

### Skills

| Name | Description |
|------|-------------|
| `abc` | Minimal example skill |
| `auditing-agent-skill` | Security-audit an agent skill for vulnerabilities |
| `creating-new-skill` | Guide for authoring new skills |
| `reviewing-agent-skill` | Code-review an agent skill against a checklist |
| `submitting-pr` | Submit a pull request following Commitizen conventions |
| `template` | Full skill template with scripts, references, and assets |

### Commands

| Name | Description |
|------|-------------|
| `abc` | Minimal example command |
| `docx-to-markdown` | Convert a Word `.docx` file to GitHub Flavored Markdown |
| `markdown-to-outlook-html` | Convert Markdown to Outlook-safe inline-styled HTML |
| `template` | Full command template with scripts, examples, and references |

### Workflows

| Name | Description |
|------|-------------|
| `builder` | Multi-agent workflow builder with pattern references |
| `maf` | Port Claude/Cursor/Copilot agents to Microsoft Agent Framework |
| `nextjs` | Full-stack Next.js app scaffolding and implementation |
| `prodify` | Production-readiness workflow |
| `scrapy` | Scrapy web-scraping pipeline workflow |
| `speckit` | Specification and planning workflow |

## Development

```bash
git clone https://github.com/DINHDUY/ai-workflow-kit.git && cd ai-workflow-kit
npm install
```

Run `make` or `make help` to list all available targets.

| Make target | Description |
|-------------|-------------|
| `make install` | Install dependencies |
| `make build` | Compile TypeScript to `dist/` |
| `make test` | Run all tests |
| `make typecheck` | Type-check without emitting |
| `make dev ARGS="..."` | Run CLI in development mode |
| `make clean` | Remove build artifacts |

## License

MIT
