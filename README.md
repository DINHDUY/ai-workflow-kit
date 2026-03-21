# ai-workflow-kit

Scaffold AI agent skills, commands, and workflows into your project with a single command.

## Install

```bash
npm install -g ai-workflow-kit
```

Or run directly without installing:

```bash
npx ai-workflow-kit <command> [options]
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
npx ai-workflow-kit add-skills <skillName> --output ./skills
```

### `add-commands`

Copy an AI-agent command (`.md` file + optional scripts) into your project.

```bash
npx ai-workflow-kit add-commands <commandName> --output .cursor/commands
```

### `add-workflows`

Copy a multi-agent workflow into your project. Agent definition files are placed flat in the output directory; all other files go to `docs/workflows/<name>/`.

```bash
npx ai-workflow-kit add-workflows <workflowName> --output .cursor/agents
```

## Available Resources

### Skills

| Name |
|------|
| `abc` |
| `auditing-agent-skill` |
| `creating-new-skill` |
| `reviewing-agent-skill` |
| `submitting-pr` |
| `template` |

### Commands

| Name |
|------|
| `abc` |
| `docx-to-markdown` |
| `markdown-to-outlook-html` |

### Workflows

| Name |
|------|
| `builder` |
| `nextjs` |
| `prodify` |
| `scrapy` |
| `speckit` |

## Development

```bash
git clone https://github.com/DINHDUY/ai-workflow-kit.git && cd ai-workflow-kit
npm install
```

| Make target | Description |
|-------------|-------------|
| `make install` | Install dependencies |
| `make build` | Compile TypeScript to `dist/` |
| `make test` | Run all tests |
| `make typecheck` | Type-check without emitting |
| `make clean` | Remove build artifacts |

Somechange.

## License

MIT
