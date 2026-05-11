# AI Daily Brief

A multi-agent workflow that daily scans top AI news websites, aggregates articles, and produces a well-formatted executive summary with source references and links to original articles.

---

## What It Does

Every morning, the AI Daily Brief workflow:

1. **Fetches** articles from 7+ AI news sources via RSS feeds and APIs
2. **Filters** for AI-relevant content using keyword matching
3. **Deduplicates** across sources (the same story often appears on multiple sites)
4. **Ranks** by source authority and relevance
5. **Summarizes** each article with a 2-3 sentence executive summary
6. **Formats** everything into a clean markdown brief

The output is a structured brief like this:

```markdown
# AI Daily Brief — 2025-01-15

## Top Stories

1. **[OpenAI announces GPT-5 with reasoning capabilities](https://...)** — *Source: TechCrunch*
   OpenAI has unveiled GPT-5, its next-generation language model featuring significantly improved reasoning capabilities...

2. **[Google DeepMind introduces AlphaFold 4](https://...)** — *Source: The Verge*
   Google DeepMind has released AlphaFold 4, an upgraded version of its protein structure prediction system...

## Notable Mentions

1. **[Meta open-sources Llama 3.1](https://...)** — *Source: VentureBeat*
   Meta has released Llama 3.1 8B parameters as open-source for edge deployment...
```

---

## News Sources

| Source | Access Method | AI Focus |
|--------|--------------|----------|
| TechCrunch | RSS feed | General tech, strong AI section |
| The Verge | RSS feed | Consumer AI, major announcements |
| Ars Technica | RSS feed | Technical AI coverage |
| MIT Technology Review | RSS feed | Dedicated AI category |
| VentureBeat | RSS feed | AI business and enterprise |
| The Guardian (AI) | RSS feed | Dedicated AI section |
| Hacker News | Firebase API | Community-vetted AI news |

---

## Prerequisites

No external tools required. This workflow runs entirely within Claude Code using built-in capabilities (WebFetch, Read, Write, Bash).

---

## Quick Start

```
Use ai-daily.orchestrator to generate the AI Daily Brief
```

This invokes the full pipeline: scraper → filter-and-dedup → summarizer → formatter.

To generate a brief for a specific date:

```
Use ai-daily.orchestrator to generate the AI Daily Brief for 2025-01-15
```

---

## Agent Pipeline

Agents execute sequentially. The orchestrator collects inputs before dispatching sub-agents.

```
[1] ai-daily.orchestrator      Collects date, sets up output dir, dispatches pipeline
         │
         ▼
[2] ai-daily.scraper           Fetches articles from all 7 sources (RSS + API)
         │
         ▼
[3] ai-daily.filter-and-dedup  Filters AI articles, deduplicates, ranks, categorizes
         │
         ▼
[4] ai-daily.summarizer        Generates 2-3 sentence summaries for each article
         │
         ▼
[5] ai-daily.formatter         Assembles final markdown brief with formatting
```

| Agent | Responsibility |
|-------|---------------|
| `ai-daily.orchestrator` | Entry point; validates inputs, dispatches the pipeline, runs final smoke-check |
| `ai-daily.scraper` | Fetches articles from all configured sources via RSS feeds, APIs, or HTML scraping |
| `ai-daily.filter-and-dedup` | Filters AI-relevant articles, deduplicates across sources, ranks by authority |
| `ai-daily.summarizer` | Generates concise 2-3 sentence summaries for top stories, 1-2 for notable mentions |
| `ai-daily.formatter` | Assembles the final markdown brief with proper formatting, citations, and links |

---

## Data Flow

```
config.yaml          → orchestrator reads sources
                       ↓
raw-articles.json    ← scraper fetches from all sources
                       ↓
filtered-articles.json ← filter-and-dedup applies keywords, deduplicates
                       ↓
summarized-articles.json ← summarizer generates summaries
                       ↓
ai-daily-brief-YYYY-MM-DD.md ← formatter assembles final output
```

All intermediate files are preserved in `workflows/ai-daily/output/` for debugging.

---

## Filtering and Deduplication

### AI Keyword Matching

Articles are classified as AI-relevant if their title or description contains primary keywords such as:
`artificial intelligence`, `AI`, `LLM`, `large language model`, `machine learning`, `deep learning`, `generative AI`, `GPT`, `Claude`, `Gemini`, `Llama`, `OpenAI`, `Anthropic`, `Google DeepMind`, `Meta AI`, `xAI`

### Deduplication

Cross-source deduplication uses:
- **URL matching**: Exact URL duplicates are resolved by source authority
- **Title similarity**: Articles with >70% word overlap and same company + action pattern are treated as duplicates
- **Authority tiebreaker**: MIT Technology Review > Ars Technica > The Verge > TechCrunch > VentureBeat > The Guardian > Hacker News

### Exclusions

Articles about jobs, hiring, recruiting, salary, or sponsored content are excluded to reduce noise.

---

## Configuration (Optional)

Create `workflows/ai-daily/config.yaml` to customize sources:

```yaml
sources:
  - name: TechCrunch
    url: https://techcrunch.com/feed/
    type: rss
    limit: 20
  - name: Custom Source
    url: https://example.com/ai-feed.xml
    type: rss
    limit: 15

output:
  top_stories_max: 7
  notable_mentions_max: 10
```

If no config file exists, the built-in default sources are used.

---

## Output Files

| File | Description |
|------|-------------|
| `output/raw-articles.json` | All articles fetched from all sources |
| `output/filtered-articles.json` | AI-relevant articles after filtering and deduplication |
| `output/summarized-articles.json` | Articles with generated summaries |
| `output/ai-daily-brief-YYYY-MM-DD.md` | Final formatted brief |

---

## Error Handling

- **Feed failures**: If a source fails to respond, the workflow continues with remaining sources
- **No AI articles**: If filtering finds no AI-relevant articles for the date, the brief notes limited coverage
- **Missing summaries**: Articles without generated summaries show "[Summary unavailable]"
- **Partial data**: The workflow always produces the best possible brief even with incomplete data

---

## Files Reference

| File | Description |
|------|-------------|
| [ai-daily-spec.md](ai-daily-spec.md) | Research document with full workflow details |
| [ai-daily-plan.md](ai-daily-plan.md) | Agent decomposition plan |
| `.cursor/agents/ai-daily.orchestrator.md` | Orchestrator agent instructions |
| `.cursor/agents/ai-daily.scraper.md` | Scraper agent instructions |
| `.cursor/agents/ai-daily.filter-and-dedup.md` | Filter and dedup agent instructions |
| `.cursor/agents/ai-daily.summarizer.md` | Summarizer agent instructions |
| `.cursor/agents/ai-daily.formatter.md` | Formatter agent instructions |

---

## Next Steps

```
Use ai-daily.orchestrator to generate the AI Daily Brief
```

To run individual agents:

```
Use ai-daily.scraper to fetch articles from all AI news sources
Use ai-daily.filter-and-dedup to filter and rank AI articles
Use ai-daily.summarizer to generate article summaries
Use ai-daily.formatter to assemble the final brief
```
