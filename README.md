# @dtranllc/ai-workflow-kit

Scaffold AI agent workflows into your project with a single command.

## What is this?

**ai-workflow-kit** is a collection of production-ready multi-agent workflow systems that you can instantly add to your project. Each workflow is a coordinated team of specialized AI agents that work together to automate complex development tasks—from researching and planning to implementation and optimization.

The **`builder` workflow** is the centerpiece: it automates the creation of *new* multi-agent workflows. Point it at any professional domain, and it will research best practices, design the agent decomposition, generate all agent definition files, and produce comprehensive documentation—ready to use in Cursor, Claude Code, or GitHub Copilot.

## Who is this for?

- **AI-native developers** building with Cursor, Claude Code, or GitHub Copilot agents
- **Teams** standardizing on multi-agent workflows for complex tasks
- **DevOps & Platform Engineers** automating domain-specific pipelines
- **Tech Leads** creating reusable agent patterns for their organization

Whether you're building web apps with the `nextjs` workflow, optimizing performance with `perf`, or creating your own custom workflows with `builder`, this kit gives you battle-tested agent systems instead of starting from scratch.

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

## Usage

Copy a multi-agent workflow into your project. Agent definition files are placed flat in the output directory; all other files go to `docs/workflows/<name>/`.

```bash
npx @dtranllc/ai-workflow-kit add-workflows <workflowName> --output .cursor/agents
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `-o, --output <path>` | `.cursor/agents` | Output directory for agent files |
| `-f, --force` | `false` | Overwrite existing files |
| `--dry-run` | `false` | Preview without writing |

## Available Workflows

**Start here:** The **`builder`** workflow automates the creation of new multi-agent workflows for any professional domain.

| Name | Description | Docs |
|------|-------------|------|
| **`builder`** | **Multi-agent workflow builder with pattern references** ⭐ | [README](workflows/builder/README.md) |
| `claude-packager` | Generate a complete, production-ready Python package wrapping agents into an Anthropic Claude SDK multi-agent application | [README](workflows/claude-packager/README.md) |
| `maf-packager` | Generate a complete, production-ready Python package wrapping agents into a Microsoft Agent Framework (MAF) multi-agent application | [README](workflows/maf-packager/README.md) |
| `nextjs` | Automate the conversion of UI designs into production-ready Next.js 15+ enterprise React applications | [README](workflows/nextjs/README.md) |
| `perf` | Performance-first code generation with TDD and benchmarking | [README](workflows/perf/README.md) |
| `prodify` | Transform React prototypes into enterprise production-grade applications | [README](workflows/prodify/README.md) |
| `scrapy` | Automate creation of production-grade Scrapy web scraping projects | [README](workflows/scrapy/README.md) |
| `speckit` | Automate spec-driven development from initial concept to full implementation | [README](workflows/speckit/README.md) |

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
