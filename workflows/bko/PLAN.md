# Breakout Trading — Subagent Plan

Source workflow: `docs/trading/2.md`

---

## Overview

The breakout trading workflow has 7 sequential steps across 4 phases. This plan defines a dedicated `bko.*` subagent suite to automate the full pipeline from pre-market prep through post-trade journaling. Two existing `mtr.*` agents (`mtr.entry-calculator` and `mtr.trade-journal`) are reused unchanged, as their logic is strategy-agnostic.

---

## Workflow-to-Agent Mapping

| Workflow Step | Agent(s) |
|---|---|
| Step 1 — Pre-market scan + level identification | `bko.pre-market-analyst` + `bko.level-mapper` (parallel) |
| Step 2 — Monitor for setup patterns (9:30–11 AM) | `bko.setup-monitor` |
| Step 3 — Confirm breakout vs. fakeout | `bko.breakout-confirmer` |
| Step 4 — Entry + position sizing | `mtr.entry-calculator` (reused) |
| Step 5 — Stop-loss placement + trailing plan | `bko.risk-manager` |
| Step 6 — Monitor position, exit signals | `bko.exit-monitor` (background) |
| Step 7 — Post-trade journal | `mtr.trade-journal` (reused) |
| All phases — Pipeline coordination | `bko.orchestrator` |

---

## Agent Specifications

### `bko.orchestrator`
- **Model:** sonnet
- **Readonly:** No
- **Role:** Coordinates the full 4-phase breakout trading day. Spawns subagents in the correct sequence, passes context explicitly between them (subagents share no state), and presents structured output at each phase transition.
- **Phases:**
  1. **Pre-Market (Parallel):** Spawns `bko.pre-market-analyst` and `bko.level-mapper` simultaneously; merges into a watchlist-with-levels.
  2. **Setup Watch (Sequential, 9:30–11 AM):** Calls `bko.setup-monitor` per ticker, then gates `bko.breakout-confirmer` -> `mtr.entry-calculator` only on confirmed setups.
  3. **Active Trade (Parallel):** Launches `bko.risk-manager` + `bko.exit-monitor` (background) once entry is placed.
  4. **Post-Trade:** Calls `mtr.trade-journal` with complete trade details.

---

### `bko.pre-market-analyst`
- **Model:** sonnet
- **Readonly:** Yes
- **Tools:** Read, WebFetch, WebSearch
- **Role:** Surveys the pre-market landscape for stocks that are strong breakout candidates. Focuses on breakout-specific signals: gap ups/downs, high relative volume (2x+), clear prior resistance/support on the chart, and verifiable catalysts (news, earnings, sector momentum). Low-to-medium float stocks are prioritized.
- **Output:** Ranked candidate list with catalyst tier, pre-market % change, float, and RVOL.

---

### `bko.level-mapper`
- **Model:** fast
- **Readonly:** Yes
- **Role:** For each candidate ticker, identifies and structures the key price levels that define a breakout trade. Invoked twice: (1) pre-market to mark daily levels, and (2) at ~9:45-10:00 AM to add the Opening Range High/Low after the first 15-30 minutes of trading.
- **Levels mapped:**
  - Horizontal resistance/support from recent swing highs/lows
  - Prior day close, pre-market high/low
  - VWAP (estimated or provided)
  - Round numbers, pivot points
  - Opening Range High/Low (ORH/ORL) — added in second invocation
- **Output:** Structured level map per ticker consumed by `bko.setup-monitor` and `bko.breakout-confirmer`.

---

### `bko.setup-monitor`
- **Model:** fast
- **Readonly:** Yes
- **Role:** Runs during market hours, watching each watchlist ticker for consolidation near key levels and flagging when a tradeable breakout pattern is forming. Does not confirm — it surfaces patterns for `bko.breakout-confirmer` to gate.
- **Patterns watched:**
  - **ORB (Opening Range Breakout):** Price approaching or pressing against the ORH/ORL
  - **Bull Flag:** Flagpole up, then tight downward/sideways consolidation on contracting volume
  - **Flat Top:** Price testing the same resistance 2+ times with tightening price action
  - **Rectangle/Triangle breakout:** Range compression preceding an expansion move
- **Output:** `SETUP FORMING` or `NO SETUP` per ticker, with pattern type, trigger level, and invalidation level.

---

### `bko.breakout-confirmer`
- **Model:** fast
- **Readonly:** Yes
- **Role:** The critical fakeout filter. Given a setup flagged by `bko.setup-monitor`, evaluates whether the actual breakout qualifies as confirmed or should be skipped. This is the most breakout-specific agent in the suite — volume confirmation is the centerpiece.
- **Confirmation criteria:**
  - Strong candle **close** above resistance (not a wick)
  - Volume surge: 1.5-3x average on the breakout bar
  - Momentum indicators: MACD not diverging, RSI not above 80
  - Tape quality: aggressive buying visible on Level 2 / time & sales
  - Price directional bias: above VWAP, market (SPY) aligned
- **Output:** `CONFIRMED` with confidence score, or `SKIP` with specific reason. Feeds directly into `mtr.entry-calculator`.

---

### `bko.risk-manager`
- **Model:** fast
- **Readonly:** Yes
- **Role:** Breakout-specific stop-loss placement and trailing plan. Distinct from `mtr.risk-manager` because the stop anchor is the breakout level itself (not a consolidation low or VWAP), and the trail strategy references VWAP reclaim as the primary signal.
- **Stop logic:**
  - Initial stop: just below the breakout level (ATR buffer: $0.10-$0.50 depending on stock volatility)
  - Hard stop (resting broker order) — never mental
  - Never widen after placement
- **Trail plan:**
  - Move to breakeven at +1R
  - Phase 2: Trail via recent swing lows (1-min/5-min)
  - Phase 3 (2R+): Tighten to below VWAP or candle-by-candle trail
- **Output:** Structured risk plan with exact price levels for each phase.

---

### `bko.exit-monitor`
- **Model:** fast
- **Readonly:** Yes
- **Background:** Yes
- **Role:** Runs as a background watcher on an open breakout position. Evaluates continuation vs. reversal signals and recommends partial or full exits with specific urgency levels.
- **Exit triggers:**
  - **Predefined target:** Measured move = height of prior range added to breakout point; or 2:1-3:1 R:R
  - **Partial exit (50%):** At +1R or first overhead resistance level
  - **Reversal signals:** Shooting star, bearish engulfing, heavy-volume red candle, VWAP breakdown
  - **Volume fade:** Volume drying up at a new high (no follow-through / distribution)
  - **Time-based:** Flag for review if still open approaching 12:00 PM ET with slowing volatility
- **Output:** Structured assessment with `HOLD`, `PARTIAL EXIT`, or `FULL EXIT` recommendation per check.

---

## Reused Agents (No Changes)

| Agent | Used at | Reason reused |
|---|---|---|
| `mtr.entry-calculator` | Step 4 (Entry) | Position sizing math (dollar risk / stop distance) is strategy-agnostic |
| `mtr.trade-journal` | Step 7 (Journal) | Journal format is generic; breakout context passed as inputs |

---

## File Layout

```
.cursor/agents/
  bko.orchestrator.md
  bko.pre-market-analyst.md
  bko.level-mapper.md
  bko.setup-monitor.md
  bko.breakout-confirmer.md
  bko.risk-manager.md
  bko.exit-monitor.md
```

---

## Key Design Decisions

1. **`bko.breakout-confirmer` is the most critical new agent** — volume + candle-close confirmation is the breakout strategy's primary edge; it acts as a hard gate before any money is committed.
2. **`bko.level-mapper` is invoked twice** — daily levels are known pre-market, but the Opening Range only forms after 9:30 AM. A second call at ~9:45 AM adds ORH/ORL to the level map.
3. **`bko.risk-manager` replaces `mtr.risk-manager`** — the stop anchor logic differs; breakout stops are placed relative to the breakout candle, not the consolidation low or VWAP.
4. **`bko.exit-monitor` is a background agent** — it runs non-blocking so the orchestrator can continue with other tickers while monitoring an open position.
5. **Context is always passed explicitly** — no agent shares conversation history; the orchestrator is responsible for threading ticker, levels, catalyst, pattern type, entry price, and account params to each downstream agent.
