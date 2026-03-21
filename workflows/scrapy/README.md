# Scrapy Project Builder

A multi-agent system that automates the creation of production-grade Scrapy 2.14.2 projects following SOLID principles, DRY patterns, and Clean Architecture. The system generates complete web scraping projects with domain/application/infrastructure layer separation, async spider implementations, SQLite/JSONL exporters, pytest test suites, and optional Docker deployment configs. Designed for Python developers who need to quickly scaffold maintainable, scalable scraping projects without manual boilerplate setup.

## What It Does

1. **Sets up isolated Python environment** - Creates Python 3.11+ virtual environment with Scrapy 2.14.2, scrapy-poet, black, ruff, pytest, and generates .env template for configuration
2. **Generates Clean Architecture skeleton** - Runs `scrapy startproject` then restructures into domain/, application/spiders/, infrastructure/ layers with proper imports
3. **Creates spider code with best practices** - Generates async spiders with base classes, CSS/XPath selectors, ItemLoader usage, and pagination logic following Single Responsibility principle
4. **Builds data pipeline infrastructure** - Creates single-purpose validation/SQLite/export pipelines with async support and configures all Scrapy 2.14 settings (AUTOTHROTTLE, FEEDS, ROBOTSTXT_OBEY)
5. **Adds quality assurance tooling** - Includes pytest fixtures, ruff/black configuration, linting validation, and optional Dockerfile for Scrapyd deployment
6. **Generates executable runner** - Creates run.py with AsyncCrawlerProcess entry point that can be executed via `python -m <project>.run`

## Agents

| Agent | Role |
|-------|------|
| `scrapy.orchestrator` | Coordinates full pipeline, invokes agents in sequence, manages parallel code generation phase |
| `scrapy.environment-setup` | Creates venv, installs Scrapy 2.14.2 and dependencies, generates .env template |
| `scrapy.project-generator` | Runs scrapy startproject, restructures to Clean Architecture (domain/application/infrastructure) |
| `scrapy.domain-builder` | Generates domain/items.py with Item classes and ItemLoader with field processors |
| `scrapy.spider-builder` | Creates base_spider.py and concrete async spiders with selectors and pagination |
| `scrapy.infrastructure-builder` | Builds pipelines.py (validation, SQLite, export) and configures settings.py |
| `scrapy.runner-builder` | Creates run.py entry point with AsyncCrawlerProcess |
| `scrapy.quality-setup` | Adds pytest tests, ruff/black config, README, optional Docker deployment |

## How to Use

### Full Pipeline

Invoke `scrapy.orchestrator` with project requirements (name, URL, fields, storage):

```
Create a Scrapy project named "bookstore" that scrapes books from https://books.toscrape.com/. 
Extract title, price, rating, and authors. Store results in SQLite and JSONL. 
Include pytest tests and Docker deployment config.
```

### Individual Agents

**Environment Setup** - Use `scrapy.environment-setup` when you only need venv and dependencies:
```
@scrapy.environment-setup Set up a Python 3.11 virtual environment with Scrapy 2.14.2 
and all required dependencies in ./my-scraper/
```

**Code Generation** - Use `scrapy.orchestrator` to generate code layers for existing project skeleton:
```
@scrapy.orchestrator Generate domain, spider, and infrastructure code for scraping 
product listings. Items should have: name, price, sku, image_url. Target site: example.com/products
```

**Quality Tooling** - Use `scrapy.quality-setup` to add testing and linting to existing project:
```
@scrapy.quality-setup Add pytest configuration, ruff/black linting, and Docker deployment 
to existing Scrapy project at ./bookstore/
```

## Setup

The system automatically installs all dependencies during the environment-setup phase:

```bash
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

No manual setup required - the agents handle environment creation and dependency installation.

## Output

The system generates a complete Scrapy project in your specified directory with Clean Architecture layout: domain/ (Item classes), application/spiders/ (base and concrete spiders), infrastructure/ (pipelines, settings), tests/ (pytest fixtures), run.py (async entry point), pyproject.toml (linter config), and optional Dockerfile. Projects are immediately runnable via `python -m <project>.run` inside the generated virtual environment.

## Examples

**E-commerce product scraper**:
```
Create Scrapy project "shopify_scraper" for https://example-shop.com. Extract product_name, 
price, stock_status, images. Use JSON export only. Skip Docker config.
```

**News article aggregator**:
```
Build "news_crawler" scraping https://news-site.com/articles. Fields: headline, author, 
publish_date, content, tags. Store in SQLite with validation pipeline. Include pytest tests.
```

**Real estate listings scraper**:
```
Generate "realestate_bot" for https://listings.example.com. Extract address, price, bedrooms, 
bathrooms, square_feet, listing_url. JSONL export + SQLite storage. Add Docker deployment.
```
