# AI Daily Brief — Agent Plan

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   ai-daily.orchestrator                      │
│           Collects config, dispatches pipeline               │
└──────────────────────┬──────────────────────────────────────┘
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
┌─────────────┐ ┌───────────┐ ┌──────────┐
│ai-daily.    │ │ai-daily.  │ │ai-daily. │
│scraper      │ │filter-and-│ │formatter │
│             │ │dedup      │ │          │
└──────┬──────┘ └─────┬─────┘ └────┬─────┘
       │              │            │
       ▼              ▼            ▼
  articles.json    ranked.json    brief.md
```

**Sequential pipeline**: scraper → filter-and-dedup → summarizer → formatter.
The summarizer is integrated into the filter-and-dedup agent for simplicity since the context is small enough.

---

## Agent Inventory

### 1. ai-daily.orchestrator

- **Model**: claude-sonnet-4-20250514
- **Role**: Entry point. Reads or creates configuration, invokes sub-agents in sequence, validates output.
- **Responsibilities**:
  - Accept optional date parameter (defaults to today)
  - Read `config.yaml` or use built-in source defaults
  - Invoke `ai-daily.scraper` → `ai-daily.filter-and-dedup` → `ai-daily.summarizer` → `ai-daily.formatter`
  - Validate the final output exists and has the expected structure
  - Display the brief to stdout
- **Tools**: Read, Write, Bash, Glob, Grep, WebFetch, WebSearch

### 2. ai-daily.scraper

- **Model**: claude-sonnet-4-20250514
- **Role**: Fetches articles from all configured sources.
- **Inputs**: Source configuration (list of sources with URLs and types)
- **Outputs**: Raw articles JSON — array of objects with `{source, title, url, date, description, content}`
- **Responsibilities**:
  - For RSS sources: fetch feed via HTTP, parse XML with feedparser logic, extract entries
  - For API sources: make API call, parse JSON response
  - For HTML sources: fetch page, parse HTML, extract article cards
  - Handle timeouts, retries (2 attempts), and rate limiting (1s between requests)
  - Collect up to N articles per source (configurable, default 20)
  - Handle encoding issues, malformed XML, empty feeds gracefully
  - Write raw articles to `workflows/ai-daily/output/raw-articles.json`
- **Tools**: Read, Bash, WebFetch, Write, Grep

### 3. ai-daily.filter-and-dedup

- **Model**: claude-sonnet-4-20250514
- **Role**: Filters articles for AI relevance, deduplicates, and ranks.
- **Inputs**: Raw articles JSON from scraper
- **Outputs**: Filtered articles JSON — `{top_stories: [...], notable_mentions: [...]}`
- **Responsibilities**:
  - Filter articles using AI keyword matching (primary + secondary keywords)
  - Exclude articles matching exclusion keywords (jobs, hiring, etc.)
  - Deduplicate across sources using title similarity and URL matching
  - Rank by source authority and recency
  - Separate into Top Stories (3-7) and Notable Mentions (3-10)
  - Write results to `workflows/ai-daily/output/filtered-articles.json`
- **Tools**: Read, Write, Bash, Grep

### 4. ai-daily.summarizer

- **Model**: claude-opus-4-20250514 (needs higher reasoning for quality summaries)
- **Role**: Generates concise summaries for each article.
- **Inputs**: Filtered articles JSON with top stories and notable mentions
- **Outputs**: Summarized articles JSON — adds `summary` field to each article
- **Responsibilities**:
  - Generate 2-3 sentence summaries for Top Stories (what happened + why it matters)
  - Generate 1-2 sentence summaries for Notable Mentions
  - Maintain professional, informative, neutral tone
  - Never fabricate facts — only summarize what's in the article metadata
  - Write results to `workflows/ai-daily/output/summarized-articles.json`
- **Tools**: Read, Write, Bash, Grep

### 5. ai-daily.formatter

- **Model**: claude-sonnet-4-20250514
- **Role**: Assembles the final markdown brief.
- **Inputs**: Summarized articles JSON
- **Outputs**: Markdown brief file — `outputs/ai-daily-brief-YYYY-MM-DD.md`
- **Responsibilities**:
  - Apply the standard brief template (header, Top Stories, Notable Mentions, footer)
  - Format article links as markdown `[Title](url)`
  - Include source attribution for each article
  - Add generation timestamp and source list
  - Validate output format
- **Tools**: Read, Write, Bash, Grep

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

---

## Default Source Configuration

Built-in sources (used when config.yaml is absent):

| Source | RSS URL | Type | Articles Limit |
|--------|---------|------|----------------|
| TechCrunch | https://techcrunch.com/feed/ | rss | 20 |
| The Verge | https://www.theverge.com/rss/tech-index.xml | rss | 20 |
| Ars Technica | https://feeds.arstechnica.com/arstechnica/index-rss | rss | 20 |
| MIT Technology Review | https://www.technologyreview.com/feed/ | rss | 15 |
| VentureBeat | https://venturebeat.com/feed/ | rss | 20 |
| The Guardian (AI) | https://www.theguardian.com/technology/ai-artificialintelligence/rss | rss | 20 |
| Hacker News | https://hacker-news.firebaseio.com/v0/topstories.json | api | 30 |

---

## AI Keyword Definitions

**Primary** (article must match one): `artificial intelligence`, `AI`, `LLM`, `large language model`, `machine learning`, `deep learning`, `generative AI`, `GPT`, `Claude`, `Gemini`, `Llama`, `diffusion`, `transformer`, `neural network`, `AGI`, `foundation model`, `OpenAI`, `Anthropic`, `Google DeepMind`, `Meta AI`, `xAI`

**Secondary** (boosts ranking): `autonomous agent`, `AI agent`, `multi-agent`, `RAG`, `retrieval augmented`, `fine-tuning`, `model context protocol`, `MCP`, `AI safety`, `AI alignment`, `AI regulation`, `AI policy`

**Exclude** (remove from results): `jobs`, `job`, `hiring`, `recruiting`, `salary`, `compensation`, `merchandise`, `ad`, `sponsored`, `webinar`, `conference`, `event`

---

## Source Authority Ranking

Used for deduplication — when the same story appears on multiple sources, keep the one from the highest-ranked source:

1. MIT Technology Review
2. Ars Technica
3. The Verge
4. TechCrunch
5. VentureBeat
6. Wired
7. The Guardian
8. Reuters
9. Hacker News
