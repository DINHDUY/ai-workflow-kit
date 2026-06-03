---
name: comm-winston-star
description: Patrick Winston's MIT presentation framework for crafting structured, memorable, high-impact talks using the Empowerment Promise and Winston's Star 5-element structure.
---

# Winston Star — Agent Plan

## Overview

This workflow implements **Patrick Winston's MIT presentation framework** for crafting structured, memorable, high-impact talks. The framework has two core components: the **Empowerment Promise** (how to start a talk) and **Winston's Star** (the 5-element structure for making ideas unforgettable).

**Practitioners**: Speakers, presenters, communicators, educators, and anyone who needs to deliver impactful talks or presentations.

**Goal**: Guide a speaker from raw topic and audience context through a complete Winston Star presentation structure, producing an Empowerment Promise, a Symbol, Slogan, Surprise, Salient Idea, Story, delivery guidance, and a closing Contributions slide plan.

---

## Agent Architecture

| Agent | Role | Model | Parallel? |
|-------|------|-------|-----------|
| `comm-winston-star.orchestrator` | Entry point — collects inputs, writes `winston-star-context.json`, invokes sub-agents, validates output | claude-sonnet | N/A (orchestrator) |
| `comm-winston-star.context-collector` | Gathers topic, audience, occasion, time, outcome, constraints, and existing materials | claude-sonnet | First (sequential) |
| `comm-winston-star.promise-crafter` | Crafts the Empowerment Promise — a specific, outcome-driven, one-sentence opening | claude-sonnet | After context |
| `comm-winston-star.symbol-builder` | Designs the Symbol — a visual or physical object that represents the core idea | claude-sonnet | After promise (can parallelize with slogan) |
| `comm-winston-star.slogan-crafter` | Writes the Slogan — a short, repeatable phrase the audience can repeat without explanation | claude-sonnet | After promise (can parallelize with symbol) |
| `comm-winston-star.surprise-designer` | Creates the Surprise — a counterintuitive insight that breaks an assumption | claude-sonnet | After promise |
| `comm-winston-star.salient-idea-focuser` | Distills the Salient Idea — the one thing the audience remembers above all else | claude-sonnet | After surprise |
| `comm-winston-star.story-weaver` | Constructs the Story — specific enough to be vivid, universal enough to resonate | claude-sonnet | Last element (after salient idea) |
| `comm-winston-star.delivery-guide` | Produces delivery guidance — boards, props, slide design, whitespace, font guidance | claude-sonnet | After star elements |
| `comm-winston-star.closer` | Crafts the Contributions Slide — summarizing what the audience gained, no "Thank you" or "Questions?" | claude-sonnet | Final element |

---

## Orchestrator Flow

```
Orchestrator
  └── Step 1: Collect user inputs (topic, audience, occasion, time, outcome, constraints)
  └── Step 2: Write winston-star-context.json with initial inputs and agent status tracking
  └── Step 3: Invoke comm-winston-star.context-collector
      └── Waits for "complete" before proceeding
  └── Step 4: Invoke comm-winston-star.promise-crafter
      └── Waits for "complete" before proceeding
  └── Step 5: Invoke comm-winston-star.symbol-builder AND comm-winston-star.slogan-crafter (parallel)
      └── Waits for both to complete
  └── Step 6: Invoke comm-winston-star.surprise-designer
      └── Waits for "complete" before proceeding
  └── Step 7: Invoke comm-winston-star.salient-idea-focuser
      └── Waits for "complete" before proceeding
  └── Step 8: Invoke comm-winston-star.story-weaver
      └── Waits for "complete" before proceeding
  └── Step 9: Invoke comm-winston-star.delivery-guide
      └── Waits for "complete" before proceeding
  └── Step 10: Invoke comm-winston-star.closer
      └── Waits for "complete" before proceeding
  └── Step 11: Final validation — verify all elements present in context.json
  └── Step 12: Report success with full Winston Star output
```

---

## Context File Schema (`winston-star-context.json`)

```json
{
  "topic": "<user-provided>",
  "audience": "<user-provided>",
  "occasion": "<user-provided>",
  "timeAvailable": "<user-provided>",
  "desiredOutcome": "<user-provided>",
  "constraints": "<user-provided>",
  "existingMaterials": "<user-provided>",
  "empowermentPromise": "<crafted by promise-crafter>",
  "symbol": {
    "description": "<crafted by symbol-builder>",
    "visualGuidance": "<crafted by symbol-builder>"
  },
  "slogan": "<crafted by slogan-crafter>",
  "surprise": {
    "assumptionBroke": "<crafted by surprise-designer>",
    "counterintuitiveInsight": "<crafted by surprise-designer>",
    "audienceReaction": "<crafted by surprise-designer>"
  },
  "salientIdea": "<crafted by salient-idea-focuser>",
  "story": {
    "setup": "<crafted by story-weaver>",
    "conflict": "<crafted by story-weaver>",
    "resolution": "<crafted by story-weaver>",
    "universalTheme": "<crafted by story-weaver>"
  },
  "deliveryGuidance": {
    "slides": "<crafted by delivery-guide>",
    "props": "<crafted by delivery-guide>",
    "boards": "<crafted by delivery-guide>",
    "pacing": "<crafted by delivery-guide>"
  },
  "contributionsSlide": "<crafted by closer>",
  "generatedAt": "<ISO 8601 timestamp>",
  "agents": {
    "context-collector": { "status": "pending" },
    "promise-crafter": { "status": "pending" },
    "symbol-builder": { "status": "pending" },
    "slogan-crafter": { "status": "pending" },
    "surprise-designer": { "status": "pending" },
    "salient-idea-focuser": { "status": "pending" },
    "story-weaver": { "status": "pending" },
    "delivery-guide": { "status": "pending" },
    "closer": { "status": "pending" }
  }
}
```

---

## Agent Invocation Protocol

Each sub-agent follows this protocol:
1. Read `winston-star-context.json` from the directory specified by the orchestrator.
2. Update its own status to `"running"`.
3. Perform its specialized task using the context data.
4. Write its output back into `winston-star-context.json` under its designated field.
5. Update its own status to `"complete"`.

If an agent encounters an error, it sets its status to `"failed"` with an `error` field and aborts. The orchestrator halts the pipeline on any failure.

---

## Model Selection

All agents use `claude-sonnet` (Claude 3.5 Sonnet or current equivalent) for balanced reasoning speed and quality. Winston's framework requires creative synthesis and audience empathy — sonnet's strength in nuanced communication tasks makes it the right choice over faster/harsher models.
