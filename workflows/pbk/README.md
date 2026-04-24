# Pullback Trading Agent System

A multi-agent AI system that automates the full pullback/continuation day trading workflow — from pre-market scanning to post-trade journaling. Built for active day traders who use VWAP, EMA, and ATR-based entries on high-RVOL, catalyst-driven stocks. The system handles candidate discovery, trade analysis, entry confirmation, position sizing, in-trade management, and performance logging in one coordinated pipeline.

## What It Does

1. **Scans pre-market** for gapping stocks with confirmed catalysts, high relative volume (RVOL ≥ 2x), and clean chart structure
2. **Identifies pullback setups** — grades flagpole quality, pullback depth (38–62% Fibonacci), and VWAP/EMA alignment
3. **Confirms entries** — validates Tier 1/2 bullish reversal candles with volume expansion at support
4. **Sizes positions** — applies the 1% account risk rule with ATR-adjusted stops and computes 2R–4R profit targets
5. **Manages open trades** — trails stops via Chandelier Exit, moves to breakeven at +1R, scales out at 2R
6. **Journals results** — grades trade quality (A–F), logs R-multiples, and tracks session win rate and average R:R

## Agents

| Agent | Model | Role |
|-------|-------|------|
| `pullback.orchestrator` | claude-sonnet-4-5 | Coordinates all 6 phases; entry point for full pipeline runs |
| `pullback.scanner` | claude-sonnet-4-5 | Pre-market screener; builds daily watchlist from gap/RVOL/catalyst data |
| `pullback.setup-analyzer` | claude-sonnet-4-5 | Grades trend quality, flagpole strength, and pullback depth |
| `pullback.entry-advisor` | claude-sonnet-4-5 | Confirms entry candle patterns and volume at VWAP/EMA support |
| `pullback.risk-manager` | o3-mini | Calculates position size, ATR stop, and R-multiple targets |
| `pullback.trade-manager` | claude-sonnet-4-5 | Manages open trades: breakeven stops, Chandelier Exit trailing, scale-outs |
| `pullback.journal` | o3-mini | Post-trade journaling, quality grading, and session performance metrics |

## Pipeline

```
Pre-Market                 Intraday                        Post-Trade
─────────                  ────────                        ──────────
pullback.scanner
  └── Watchlist (3-8)
        └── pullback.setup-analyzer
              └── Qualifying setups
                    └── pullback.entry-advisor
                          └── Entry signal confirmed
                                └── pullback.risk-manager
                                      └── Position size + stops + targets
                                            └── pullback.trade-manager
                                                  └── Manage open trade
                                                        └── pullback.journal
                                                              └── Trade log + metrics
```

**Phase sequence:**
1. **Scan** — find candidates (gap ≥ 3%, RVOL ≥ 2x, clear catalyst)
2. **Analyze** — grade pullback setup against VWAP/9 EMA/20 EMA
3. **Confirm** — validate entry candle and volume at support
4. **Size** — compute shares using 1% rule + ATR stop
5. **Manage** — trail with Chandelier Exit, scale at 2R
6. **Journal** — log outcome, grade process, track metrics

## Invocation Examples

### Full Pipeline via Orchestrator

Run the complete pre-market to journal workflow for a trading session:

**Claude**

```
Run agent /pullback.orchestrator pipeline for today. Account size: $120,000. Prioritize NVDA and TSLA if they gap up.
```

```
Run agent /pullback.orchestrator It's 9:45 AM scan and identify any qualifying setups with entry signals forming. Account: $120,000.
```

### Individual Subagent Examples

**Scanning only** — build a watchlist without running the full pipeline:
```
@pullback.scanner Scan for pullback candidates for today. Show top 5 by catalyst strength and RVOL.
```

**Setup analysis** — check if a specific stock has a valid pullback:
```
@pullback.setup-analyzer Analyze NVDA for a pullback setup.
Current price: $875. VWAP: $862. 9 EMA: $858. ATR: $14.20.
Pre-market high was $882.
```

**Position sizing** — calculate trade size before entering:
```
@pullback.risk-manager Size a trade for AAPL.
Account: $50,000. Entry: $195.50. Stop: $193.20. ATR: $2.80.
```

**Trade management** — get Chandelier Exit update for an open position:
```
@pullback.trade-manager I'm long TSLA from $248.00, stop at $244.50.
Current price: $256.80. Highest high since entry: $257.40. ATR: $3.60.
Update my Chandelier Exit and advise on stop placement.
```

**Post-trade journal** — log a completed trade:
```
@pullback.journal Log this trade: NVDA long, entry $870, stop $858,
exit $895 (full) at 10:45 AM. ATR was $14. RVOL was 3.2x.
Setup had bullish engulfing off VWAP. Account $50,000.
```

## Output

The orchestrator produces a structured session report covering all six phases, including the pre-market watchlist, setup grades, entry signals, risk plans (shares, stop, targets), and a post-session journal entry per trade. Individual subagents output their phase-specific summaries in formatted blocks. No files are written to disk by default — outputs are returned as structured text in chat for the trader to review and act on.

## Requirements

| Requirement | Details |
|-------------|---------|
| **Data access** | WebSearch and WebFetch tools enabled (Cursor) for live price/news fetching |
| **Price sources** | Yahoo Finance, Finviz screener, Seeking Alpha (accessed via WebFetch) |
| **Account info** | Trader must supply account size at invocation for position sizing |
| **Market hours** | Designed for 9:30–11:00 AM ET peak session; scanner runs pre-market |
| **Agent platform** | Cursor with multi-agent support (`.cursor/agents/` directory) |

> **Risk disclaimer:** Day trading is high-risk. This system is a decision-support tool, not financial advice. Always verify signals manually and use a paper trading account before live execution.
