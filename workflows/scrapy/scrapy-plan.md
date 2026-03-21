# Scrapy Multi-Agent System Plan

Source workflow: `f:\Users\DTRAN\SDD\ai-agent-skills\workflows\scrapy\scrapy-spec.md`

---

## Overview

This multi-agent system automates the creation of production-grade Scrapy 2.14.2 projects following SOLID principles, DRY patterns, and Clean Architecture. The system consists of 8 specialized agents orchestrated through a sequential pipeline with some parallel execution opportunities in the middle phases.

---

## Pattern Selection

**Primary pattern:** Sequential Pipeline
**Reason:** The workflow has clear dependencies where each phase builds on artifacts from previous phases. Environment setup must precede project creation, which must precede code generation, etc.

**Secondary pattern:** Parallel Fan-Out (Phases 2-4)
**Reason:** Once the project skeleton exists, domain layer (items), application layer (spiders), and infrastructure layer (pipelines/settings) can be built simultaneously since they have minimal interdependencies at creation time.

---

## Workflow-to-Agent Mapping

| Workflow Step | Agent | Pattern Role |
|---|---|---|
| Phase 0 - Environment Setup | `scrapy.environment-setup` | Sequential stage 1 |
| Phase 1 - Project Skeleton | `scrapy.project-generator` | Sequential stage 2 |
| Phase 2 - Domain Layer (Items) | `scrapy.domain-builder` | Fan-out worker 1 |
| Phase 3 - Application Layer (Spiders) | `scrapy.spider-builder` | Fan-out worker 2 |
| Phase 4 - Infrastructure Layer | `scrapy.infrastructure-builder` | Fan-out worker 3 |
| Phase 5 - Runner Script | `scrapy.runner-builder` | Sequential stage 3 |
| Phase 6-7 - Testing & Production | `scrapy.quality-setup` | Sequential stage 4 |
| Full Coordination | `scrapy.orchestrator` | Pipeline coordinator |

---

## Pipeline

```
[User Request]
      ↓
[scrapy.orchestrator]
      ↓
[scrapy.environment-setup] → venv, deps, .env created
      ↓
[scrapy.project-generator] → Project skeleton + Clean Architecture folders
      ↓
      ├──→ [scrapy.domain-builder] ───────┐
      ├──→ [scrapy.spider-builder] ───────┼──→ Code layers complete
      └──→ [scrapy.infrastructure-builder]┘
      ↓
[scrapy.runner-builder] → run.py entry point
      ↓
[scrapy.quality-setup] → pytest, ruff, black, Docker configs
      ↓
[SUCCESS: Runnable Scrapy project]
```

---

## Agent Specifications

### `scrapy.orchestrator`
- **Model:** sonnet
- **Readonly:** false
- **Tools:** File read/write, subagent invocation
- **Pattern Role:** Pipeline coordinator
- **Role:** Coordinates the full Scrapy project creation pipeline. Invokes agents in correct sequence, passes context between stages, manages the parallel fan-out for code generation phases, and ensures all artifacts are correctly linked.
- **Input:** User requirements (project name, target URL, item fields, custom settings)
- **Output:** Confirmation of completed project with file paths to all generated artifacts and instructions for running the spider.

### `scrapy.environment-setup`
- **Model:** sonnet
- **Readonly:** false
- **Tools:** Shell execution, file write
- **Pattern Role:** Sequential stage 1 (foundation)
- **Role:** Creates Python 3.11+ virtual environment, installs Scrapy 2.14.2 and dependencies (scrapy-poet, black, ruff, pytest, python-dotenv), generates .env template with PROXY_URL/DB_PATH/USER_AGENT_POOL placeholders, creates requirements.txt and .gitignore.
- **Input:** Project root directory path, Python version requirement (≥3.11), optional additional dependencies
- **Output:** Path to activated venv, requirements.txt path, .env template path, confirmation that `pip install scrapy==2.14.2` succeeded

### `scrapy.project-generator`
- **Model:** sonnet
- **Readonly:** false
- **Tools:** Shell execution (scrapy startproject), file read/write, directory manipulation
- **Pattern Role:** Sequential stage 2 (skeleton creation)
- **Role:** Runs `scrapy startproject <name>`, then reorganizes the default structure into Clean Architecture layers: creates domain/, application/spiders/, infrastructure/ folders, moves items.py → domain/, pipelines.py → infrastructure/, updates all imports in settings.py and __init__.py files.
- **Input:** Project name, parent directory path, venv activation path
- **Output:** Restructured project root path, list of created directories (domain/, application/, infrastructure/), scrapy.cfg path

### `scrapy.domain-builder`
- **Model:** fast
- **Readonly:** false
- **Tools:** File write
- **Pattern Role:** Fan-out worker 1 (parallel code generation)
- **Role:** Generates domain/items.py with scrapy.Item classes and ItemLoader classes. Implements field definitions with processors (TakeFirst, MapCompose, Join) based on user-specified data schema. Includes type hints and docstrings following Clean Code principles.
- **Input:** Project domain/ path, list of item fields with types (title:string, price:float, rating:int, etc.), data transformation rules
- **Output:** domain/items.py file path, list of generated Item and Loader class names

### `scrapy.spider-builder`
- **Model:** fast
- **Readonly:** false
- **Tools:** File write
- **Pattern Role:** Fan-out worker 2 (parallel code generation)
- **Role:** Generates application/spiders/base_spider.py (DRY base class with common settings) and concrete spider files (e.g., books.py) with async parse methods, CSS/XPath selectors, ItemLoader usage, and pagination logic. Follows Single Responsibility and Open/Closed principles.
- **Input:** Project application/spiders/ path, target URL, allowed domains, CSS selectors for item fields and next page, Item class name from domain-builder
- **Output:** application/spiders/base_spider.py path, application/spiders/<name>.py path, spider name for settings registration

### `scrapy.infrastructure-builder`
- **Model:** fast
- **Readonly:** false
- **Tools:** File write
- **Pattern Role:** Fan-out worker 3 (parallel code generation)
- **Role:** Generates infrastructure/pipelines.py with single-responsibility pipelines (ValidationPipeline, SQLitePipeline, etc.), updates settings.py with ITEM_PIPELINES registration, FEEDS configuration, ROBOTSTXT_OBEY, AUTOTHROTTLE settings, and all Scrapy 2.14 best practices. Includes async pipeline support.
- **Input:** Project infrastructure/ path, settings.py path, list of pipeline types (validation, sqlite, json export), DB connection settings from .env
- **Output:** infrastructure/pipelines.py path, updated settings.py path, list of registered pipeline classes with priority order

### `scrapy.runner-builder`
- **Model:** fast
- **Readonly:** false
- **Tools:** File write
- **Pattern Role:** Sequential stage 3 (integration)
- **Role:** Creates myproject/run.py with AsyncCrawlerProcess entry point, imports correct settings, registers all spiders by name, includes async main() with asyncio.run(). Ensures script is executable via `python -m <project>.run`.
- **Input:** Project root path, project module name, list of spider names from spider-builder, settings path
- **Output:** run.py file path, command to execute (`python -m <project>.run`), confirmation that imports resolve correctly

### `scrapy.quality-setup`
- **Model:** sonnet
- **Readonly:** false
- **Tools:** File write, shell execution
- **Pattern Role:** Sequential stage 4 (quality assurance)
- **Role:** Creates tests/ directory with pytest fixtures and spider contract tests, generates pyproject.toml for black/ruff configuration, adds README.md with usage instructions, optionally creates Dockerfile and docker-compose.yml for Scrapyd deployment. Runs initial `ruff check` and `black --check` to validate code quality.
- **Input:** Project root path, testing framework choice (pytest), linting rules (ruff defaults), whether to include Docker configs
- **Output:** tests/ directory path, pyproject.toml path, README.md path, optional Dockerfile path, linter/formatter validation results

---

## Reused Agents

None. All agents are specific to Scrapy project scaffolding workflow.

---

## File Layout

```
.cursor/agents/
  scrapy.orchestrator.md
  scrapy.environment-setup.md
  scrapy.project-generator.md
  scrapy.domain-builder.md
  scrapy.spider-builder.md
  scrapy.infrastructure-builder.md
  scrapy.runner-builder.md
  scrapy.quality-setup.md
```

---

## Key Design Decisions

1. **Sequential pipeline with parallel fan-out** - Phases 0-1 are strictly sequential (setup dependencies), but phases 2-4 can run in parallel since domain/application/infrastructure layers have minimal compile-time dependencies. This speeds up code generation while maintaining correctness.

2. **Model selection: fast for code generation, sonnet for orchestration/setup** - Code generation agents (domain, spider, infrastructure, runner) use `fast` model since they follow predictable templates. Orchestrator, environment-setup, project-generator, and quality-setup use `sonnet` for complex coordination, shell operations, and multi-step reasoning.

3. **Explicit context threading between phases** - Each agent receives complete input specifications (file paths, generated artifact names, configuration values) from the orchestrator. The orchestrator maintains state about what was created in each phase and threads it forward. No agent relies on reading previous agents' output files during generation.

4. **Clean Architecture enforcement via project-generator** - The restructuring from Scrapy's default flat layout to domain/application/infrastructure happens in a single dedicated agent (project-generator) rather than incrementally. This ensures all subsequent code generators target the correct locations from the start.

5. **DRY via base classes** - spider-builder always generates base_spider.py first, then concrete spiders inherit from it. This enforces the Open/Closed principle and makes the orchestrator's job simpler (always 2 files per spider phase).

6. **Async-first by default** - All generated spiders use `async def parse()` and runner uses AsyncCrawlerProcess to match Scrapy 2.14 best practices. No legacy CrawlerProcess pattern.

---

## Dependencies

```bash
# Installed by scrapy.environment-setup agent
python>=3.11
scrapy==2.14.2
scrapy-poet
black
ruff
pytest
pytest-asyncio
python-dotenv
itemadapter
```

---

## Invocation Examples

**Full pipeline:**
```
Create a Scrapy project named "bookstore" that scrapes books from https://books.toscrape.com/. 
Extract title, price, rating, and authors. Store results in SQLite and JSONL. 
Include pytest tests and Docker deployment config.
```

**Environment setup only:**
```
@scrapy.environment-setup Set up a Python 3.11 virtual environment with Scrapy 2.14.2 
and all required dependencies in ./my-scraper/
```

**Code generation phase (assuming skeleton exists):**
```
@scrapy.orchestrator Generate domain, spider, and infrastructure code for scraping 
product listings. Items should have: name, price, sku, image_url. Target site: example.com/products
```

**Quality setup only:**
```
@scrapy.quality-setup Add pytest configuration, ruff/black linting, and Docker deployment 
to existing Scrapy project at ./bookstore/
```
