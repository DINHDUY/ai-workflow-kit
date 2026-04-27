# How to Use the IPO Workflow

This guide demonstrates using the IPO workflow for automated research and report generation on upcoming IPOs using authenticated access to Renaissance Capital IPO Pro and public SEC/news sources.

## Overview

The IPO workflow runs a five-stage pipeline—scrape the scheduled IPO calendar, filter by offering size, enrich with public research, draft per-deal dossiers, and compile a master summary—all coordinated by a single orchestrator agent.

## Prerequisites

- **Node.js 18+**
- **Playwright MCP** registered in your AI client ([microsoft/playwright-mcp](https://github.com/microsoft/playwright-mcp))
- Valid **IPO Pro** credentials (personal or firm license; comply with Renaissance Capital terms)
- Environment variables set (see below)

### Environment Variables

| Variable | Description |
|----------|-------------|
| `IPO_PRO_EMAIL` | IPO Pro login email |
| `IPO_PRO_PASSWORD` | IPO Pro password |
| `IPO_THRESHOLD_MILLIONS` | Minimum offering size in millions USD (default: `100`) |
| `IPO_PRO_STORAGE_STATE_PATH` | *(Optional)* Path to persist Playwright browser session |
| `INCLUDE_UNKNOWN_SIZE` | *(Optional)* Include deals with unparseable offering size |

Never commit credentials. Use a `.env` file (gitignored), OS keychain, or CI secret store.

### Register the Playwright MCP Server

**Cursor:** Settings → MCP → Add server — command `npx`, args `@playwright/mcp@latest`

```bash
npx @playwright/mcp@latest
```

## Installation

Install the workflow into your Cursor workspace:

**Cursor:**
```bash
uvx --from git+https://github.com/DINHDUY/ai-workflow-kit-py ^
    add-workflows ipo --output .cursor/agents
```

This installs the workflow agents into your `.cursor/agents/` directory.

## Usage

Invoke the orchestrator agent with a natural-language prompt:

```
Use ipo.orchestrator to run the full IPO Playwright pipeline.
```

The orchestrator coordinates all five stages in sequence and writes output to `./ipo_reports/`.

## Example Invocations

**Default run ($100M threshold):**
```
Use ipo.orchestrator to run the full IPO Playwright pipeline.
```

**Custom offering-size threshold:**
```
Use ipo.orchestrator to run the IPO pipeline with a $250M threshold.
```

**Include deals with unknown offering size:**
```
Use ipo.orchestrator with INCLUDE_UNKNOWN_SIZE=true and a $150M threshold.
```

## Output

| Output | Location |
|--------|----------|
| Per-deal dossiers | `./ipo_reports/{Company}.md` |
| Master roll-up | `./ipo_reports/MASTER_SUMMARY.md` |

Typical runtime: **3–10+ minutes** depending on table size, network latency, and any MFA prompts.

## Specialized Agents

| Agent | Purpose |
|-------|---------|
| `ipo.orchestrator` | Entry point — coordinates all stages, manages retries and status reporting |
| `ipo.navigator` | Authenticates to IPO Pro and extracts the Scheduled table as JSON via Playwright MCP |
| `ipo.filter` | Applies `IPO_THRESHOLD_MILLIONS` to include/exclude deals |
| `ipo.research` | Enriches each deal with S-1 filings, news, and comparable company data |
| `ipo.report-writer` | Drafts a per-deal Markdown dossier |
| `ipo.compiler` | Writes final files and `MASTER_SUMMARY.md`; runs QA checklist |

You can invoke individual agents directly for a single stage, though `ipo.orchestrator` is recommended for end-to-end automation.

## Troubleshooting

| Symptom | Resolution |
|---------|------------|
| MCP tools missing | Confirm Playwright MCP is enabled and connected in Cursor/VS Code |
| MFA / SSO wall | Complete the challenge manually; persist session via `IPO_PRO_STORAGE_STATE_PATH` |
| Empty or moved table | Re-run `ipo.navigator`; the agent uses defensive selectors to handle UI changes |
| SEC fetch 403 | Retry later or reduce request frequency; use alternate SEC EDGAR URLs |
