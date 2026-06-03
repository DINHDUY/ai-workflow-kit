# AI Daily Brief — Research Specification

## Overview

A multi-agent workflow that daily scans top AI news websites, aggregates articles, and produces a well-formatted executive summary with source references and links to original articles.

## Workflow Purpose

AI professionals, researchers, and decision-makers need a daily digest of AI developments across major tech publications. Manually checking 6-10 sources every morning is inefficient. This workflow automates that process: fetching the latest articles from each source, filtering for AI-relevant content, summarizing key stories, and assembling everything into a clean markdown brief.

---

## Phase 1: AI News Sources & Programmatic Access

### Primary AI News Websites and Their RSS/API Endpoints

| # | Source | RSS Feed URL | API Available? | AI Coverage |
|---|--------|-------------|----------------|-------------|
| 1 | TechCrunch | `https://techcrunch.com/feed/` | Yes (Jetpack REST API) | General — filter by "artificial-intelligence" category or keyword |
| 2 | The Verge | `https://www.theverge.com/rss/tech-index.xml` | No (paywalled API) | General — filter by AI keywords in title/description |
| 3 | Ars Technica | `https://feeds.arstechnica.com/arstechnica/index-rss` | No | General — filter by AI keywords; also `https://feeds.arstechnica.com/arstechnica/technology-lounge-rss` for tech deep dives |
| 4 | MIT Technology Review | `https://www.technologyreview.com/feed/` | Partial (newsletter API) | Has "Artificial intelligence" category — structured AI content |
| 5 | VentureBeat | `https://venturebeat.com/feed/` | No | Strong AI coverage — filter by "ai" or "AI" keywords |
| 6 | Wired | `https://www.wired.com/feed/rss` | No | General tech — filter for AI/ML articles |
| 7 | The Guardian (AI) | `https://www.theguardian.com/technology/ai-artificialintelligence/rss` | Yes (open news API) | Dedicated AI section |
| 8 | Reuters AI | `https://www.reutersagency.com/feed/?best-topics=tech&post_type=best` | Yes (Reuters API) | Tech/AI focused |

### Secondary / Supplemental Sources

| # | Source | Access Method | Notes |
|---|--------|--------------|-------|
| 9 | Hacker News | `https://hacker-news.firebaseio.com/v0/` (JSON API) | Search `topstories` + filter by AI keywords; great for community-vetted AI news |
| 10 | Google News (AI) | `https://news.google.com/rss?headlines=1&topic=QAAQ6AI` | RSS-based, broad coverage |
| 11 | Product Hunt (AI) | `https://www.producthunt.com/topics/artificial-intelligence` | Web scraping or API |
| 12 | AI-specific newsletters | ArXiv daily summaries, TL;DR AI, etc. | Email-based, harder to automate |

### Feed Fetching Strategy

**Approach**: Primary method uses RSS/Atom feeds (XML). Each feed returns article entries with:
- `<title>` — article title
- `<link>` — URL to original article
- `<pubDate>` / `<updated>` — publication date
- `<description>` / `<content:encoded>` — summary or full content
- `<category>` — category tags (where available)

**HTTP Requirements**:
- `Accept: application/rss+xml, application/xml, text/xml`
- `User-Agent: AIDailyBrief/1.0 (ai-daily-brief workflow)`
- Timeout: 10 seconds per request
- Retry: 2 attempts with exponential backoff (1s, 2s)

### Fallback: Web Scraping

If a site does not provide an RSS feed (or the feed is unreliable), the scraper agent falls back to targeted HTML scraping:

1. Fetch the AI section page (e.g., `https://venturebeat.com/category/ai/`)
2. Parse the HTML for article cards/links
3. Extract title, link, date, and excerpt
4. Handle dynamic content (lazy-loaded images, etc.)

**Libraries**: `BeautifulSoup4` (Python) or `cheerio` (Node.js) for HTML parsing.

### Fallback: API-Based

For sites with official APIs:
- **TechCrunch Jetpack API**: `https://public-api.wordpress.com/rest/v1.1/sites/techcrunch.com/posts?category=artificial-intelligence&number=20`
- **The Guardian API**: `https://content.guardianapis.com/search?section-id=technology&tag-id=technology/ai-artificialintelligence&api-key=...` (requires free API key)

---

## Phase 2: Article Filtering & Deduplication

### Keyword Filtering

Articles are classified as AI-relevant if their title or summary contains any of these terms (case-insensitive):

**Primary AI keywords**: `artificial intelligence`, `AI`, `LLM`, `large language model`, `machine learning`, `deep learning`, `generative AI`, `GPT`, `Claude`, `Gemini`, `Llama`, `diffusion`, `transformer`, `neural network`, `AGI`, `foundation model`

**Secondary AI keywords**: `autonomous agent`, `AI agent`, `multi-agent`, `RAG`, `retrieval augmented`, `fine-tuning`, `model context protocol`, `MCP`, `AI safety`, `AI alignment`, `AI regulation`, `AI policy`

**Exclusion keywords** (to reduce noise): `jobs`, `job`, `hiring`, `recruiting`, `salary`, `compensation`, `merchandise`, `ad`, `sponsored`

### Deduplication Strategy

Cross-source deduplication is critical since the same story appears on multiple sites:

1. **URL deduplication**: If two articles share the same canonical URL, keep only the one from the most authoritative source.
2. **Title similarity**: Use Levenshtein distance or embedding-based similarity (>85% match = duplicate).
3. **Heuristic**: If articles from different sources have very similar titles within the same hour, keep the one from the most authoritative source.

**Source authority ranking**: MIT Technology Review > Ars Technica > The Verge > TechCrunch > VentureBeat > Wired > Guardian > Reuters > Hacker News

---

## Phase 3: Summarization Approach

### Executive Summary Structure

The output follows this markdown template:

```markdown
# AI Daily Brief — [Date]

## Top Stories

1. **[Article Title](link)** — *Source: Website Name*
   Brief 2-3 sentence summary of the key points and why it matters.

2. ...

## Notable Mentions

1. **[Article Title](link)** — *Source: Website Name*
   1-2 sentence summary of secondary but still relevant developments.

...

---
*Generated by AI Daily Brief. Sources: [list of sources scanned]*
```

### Summary Generation Guidelines

- **Top Stories**: 3-7 articles that represent the most impactful AI developments of the day
- **Notable Mentions**: 3-10 articles that are interesting but less impactful
- **Summary length**: 2-3 sentences for Top Stories, 1-2 sentences for Notable Mentions
- **Each summary must**: (a) state what happened, (b) explain why it matters
- **Tone**: Professional, informative, neutral

---

## Phase 3: Tool & Technology Requirements

### Runtime Environment

- **Language**: Python 3.10+ (best for RSS parsing, web scraping, and LLM summarization)
- **Key libraries**:
  - `feedparser` — RSS/Atom feed parsing
  - `requests` — HTTP fetching
  - `beautifulsoup4` — HTML scraping fallback
  - `aiohttp` — concurrent feed fetching (speed)
  - `python-dateutil` — date parsing
  - `pydantic` — data validation

### LLM Integration

Summarization requires an LLM. Options:
- **Anthropic Claude** (preferred): `anthropic` Python SDK
- **OpenAI GPT**: `openai` Python SDK
- **Local models**: Ollama + llama/gemma for offline operation

The workflow should accept an `LLM_PROVIDER` environment variable to switch between providers.

### Configuration

A `config.yaml` file manages:
```yaml
sources:
  - name: TechCrunch
    rss_url: https://techcrunch.com/feed/
    type: rss
    articles_limit: 20
  - name: The Verge
    rss_url: https://www.theverge.com/rss/tech-index.xml
    type: rss
    articles_limit: 20
  # ... more sources

filtering:
  ai_keywords:
    primary: [artificial intelligence, AI, LLM, large language model, ...]
    secondary: [autonomous agent, AI agent, multi-agent, ...]
    exclude: [jobs, job, hiring, ...]
  dedup_threshold: 0.85

output:
  top_stories_max: 7
  notable_mentions_max: 10
  summary_length_top: 3  # sentences
  summary_length_notable: 2  # sentences

llm:
  provider: anthropic  # anthropic | openai | ollama
  model: claude-sonnet-4-20250514
  temperature: 0.3
```

---

## Phase 4: Execution Model

### Daily Execution

The workflow runs once per day, ideally in the morning (e.g., 7:00 AM UTC). Options:
1. **Cron job**: `0 7 * * * python -m ai_daily_brief`
2. **GitHub Actions**: Scheduled workflow (`schedule: cron: '0 7 * * *'`)
3. **Claude Code schedule skill**: `schedule: daily at 7am UTC run AI Daily Brief`
4. **Loop skill**: Continuous monitoring mode

### Output Delivery

The generated brief is saved as:
- File: `outputs/ai-daily-brief-YYYY-MM-DD.md`
- Console: printed to stdout
- Optional: emailed, posted to Slack, or stored in a knowledge base

---

## Phase 5: Error Handling & Reliability

- **Feed failures**: If a source fails to respond, log the error and continue with remaining sources
- **Rate limiting**: Respect robots.txt; add 1-second delay between requests
- **Content length limits**: Truncate extremely long feed entries; use first 500 characters of description for filtering
- **Missing LLM**: If no LLM provider is configured, fall back to extractive summarization (headline + first sentence of description)

---

## Agent Decomposition Rationale

The workflow decomposes into 4 specialized agents:

1. **Scraper Agent**: Fetches articles from all configured sources via RSS feeds, APIs, or HTML scraping. Handles errors, retries, and rate limiting.
2. **Filter & Dedup Agent**: Filters AI-relevant articles, deduplicates across sources, ranks by source authority and keyword relevance.
3. **Summarizer Agent**: Generates concise 2-3 sentence summaries for top stories and 1-2 sentence summaries for notable mentions using an LLM.
4. **Formatter Agent**: Assembles the final markdown brief with proper formatting, source citations, and links.

This decomposition follows the Single Responsibility Principle — each agent has one clear job and a well-defined input/output contract.
