# Winston Star Pipeline

Craft structured, memorable, high-impact presentations using Patrick Winston's MIT framework. Starting from a raw topic and audience context, the pipeline produces an Empowerment Promise, a complete Winston's Star (Symbol, Slogan, Surprise, Salient Idea, Story), delivery guidance with slide plan and pacing, and a Contributions Slide closer.

Designed for speakers, presenters, educators, and anyone who needs to deliver clear, memorable talks or presentations. Based on the legendary MIT lecture *How to Speak* delivered annually for 40+ years by Patrick Winston.

---

## What It Does

1. **Intakes context** -- gathers topic, audience profile, occasion, time, outcome, and constraints; then deepens the analysis with audience assumptions, knowledge gaps, and objections
2. **Crafts the Empowerment Promise** -- one specific, outcome-driven sentence that opens the talk: "By the end of this talk, you will be able to ___." Winston banned jokes, "thank you for having me," and apologies as weak openings.
3. **Builds Winston's Star** -- the 5-element structure for making ideas unforgettable:
   - **Symbol**: A concrete visual or physical object that represents the core idea
   - **Slogan**: A short, repeatable phrase the audience can say tomorrow without context
   - **Surprise**: A counterintuitive insight that breaks an audience assumption
   - **Salient Idea**: The single idea the audience remembers above all else (not two, not three -- one)
   - **Story**: A vivid, specific narrative that demonstrates the salient idea
4. **Produces delivery guidance** -- slide plan, prop strategy, board usage, minute-by-minute pacing, and pitfalls to avoid. Winston's rules: never read slides, use large fonts, embrace whitespace.
5. **Closes with a Contributions Slide** -- summarizes what the audience gained. Winston disliked "Thank you" and "Questions?" as final slides.

---

## Agents

| Agent | Role | Phase |
|-------|------|-------|
| `comm-winston-star.orchestrator` | Coordinates the full pipeline, validates inputs, manages handoffs | All |
| `comm-winston-star.context-collector` | Profiles audience, analyzes occasion, maps time constraints | 1 |
| `comm-winston-star.promise-crafter` | Crafts the Empowerment Promise -- one-sentence opening | 2 |
| `comm-winston-star.symbol-builder` | Designs the Symbol -- a concrete prop or visual anchor | 3a (parallel) |
| `comm-winston-star.slogan-crafter` | Writes the Slogan -- a short, repeatable phrase | 3b (parallel) |
| `comm-winston-star.surprise-designer` | Creates the Surprise -- a counterintuitive insight | 4 |
| `comm-winston-star.salient-idea-focuser` | Distills the Salient Idea -- the one thing to remember | 5 |
| `comm-winston-star.story-weaver` | Constructs the Story -- a vivid, resonant narrative | 6 |
| `comm-winston-star.delivery-guide` | Produces slide plan, prop strategy, and pacing | 7 |
| `comm-winston-star.closer` | Crafts the Contributions Slide closer | 8 |

---

## How to Use

### Full Pipeline

Invoke `comm-winston-star.orchestrator` with your talk topic and audience:

```
@comm-winston-star.orchestrator I need to give a 30-minute talk about distributed systems to engineering managers who are not deeply technical.
Topic: Designing resilient distributed systems
Audience: Engineering managers, 15-20 people, moderate technical background, not individual contributors
Occasion: Internal engineering all-hands meeting
Time available: 30 minutes (including 5 min Q&A)
Desired outcome: Managers should be able to assess whether their team's system design is resilient and ask the right questions during architecture reviews
Constraints: No deep technical diagrams; keep it accessible to non-coders
```

### Individual Agents

**Context Collection Only** -- use `comm-winston-star.context-collector` when you just need an audience and occasion analysis:
```
@comm-winston-star.context-collector
Topic: Climate policy for local governments
Audience: City council members, 12 people, mixed technical background
Occasion: Town hall presentation
Time: 20 minutes
```

**Empowerment Promise Only** -- use `comm-winston-star.promise-crafter` when you have context but need a strong opening:
```
@comm-winston-star.promise-crafter
Read the context from: winston-star-context.json
Craft the Empowerment Promise for this talk.
```

**Star Element Only** -- use any star element agent individually:
```
@comm-winston-star.symbol-builder
Read the context from: winston-star-context.json
Design a Symbol for this talk.

@comm-winston-star.slogan-crafter
Read the context from: winston-star-context.json
Craft a Slogan for this talk.

@comm-winston-star.surprise-designer
Read the context from: winston-star-context.json
Design a Surprise for this talk.

@comm-winston-star.salient-idea-focuser
Read the context from: winston-star-context.json
Distill the Salient Idea for this talk.

@comm-winston-star.story-weaver
Read the context from: winston-star-context.json
Construct a Story for this talk.

@comm-winston-star.delivery-guide
Read the context from: winston-star-context.json
Produce delivery guidance for this talk.

@comm-winston-star.closer
Read the context from: winston-star-context.json
Craft the Contributions Slide for this talk.
```

---

## Project Structure

After the pipeline runs, your project will have this structure:

```
{project-name}/
├── winston-star-context.json      # Complete star context (all agents' outputs)
└── analysis/
    ├── enriched-context.md        # Deep audience, occasion, and constraint analysis
    ├── empowerment-promise.md     # 3 candidate promises with selected winner
    ├── symbol.md                  # Primary symbol + alternatives
    ├── slogan.md                  # 3 candidate slogans with selected winner
    ├── surprise.md                # Surprise design with alternatives
    ├── salient-idea.md            # The one idea to remember
    ├── story.md                   # Story structure with alternatives
    ├── delivery-guide.md          # Slide plan, prop strategy, pacing
    └── contributions-slide.md     # Closing slide design with alternatives
```

---

## Winston's Framework Principles

### The Empowerment Promise
Every talk must open with one sentence: "By the end of this talk, you will be able to ___." This promise must be specific, outcome-driven, impossible to ignore, and deliverable in the allotted time. Winston banned: jokes, "thank you for having me," and apologies.

### Winston's Star (5 Elements)
Every unforgettable presentation contains all five:

| Element | Purpose | Winston's Rule |
|---------|---------|----------------|
| **Symbol** | Visual/physical memory anchor | Must be a concrete object, not an abstract concept |
| **Slogan** | Repeatable takeaway phrase | Audience should be able to say it tomorrow without explanation |
| **Surprise** | Emotional hook via broken assumptions | Must target a genuine audience belief, not just present a novel fact |
| **Salient Idea** | The one thing they remember | Not two. Not three. One. |
| **Story** | Makes the idea stick | Specific enough to be vivid, universal enough to resonate |

### Delivery Rules
- **Never read slides** -- the audience has one language processor; they cannot read dense slides and listen simultaneously
- **Use whitespace and large fonts** -- every slide should be readable from the back of the room
- **Use boards, props, and simple slides** -- not dense presentations
- **Every minute must earn the next minute** -- the talk is a continuous engagement contract

### Closing Rule
End with a Contributions Slide summarizing what the audience gained. Winston disliked "Thank you" or "Questions?" as final slides.

---

## References

- [Patrick Winston's MIT How to Speak (OpenCourseWare)](https://ocw.mit.edu/courses/res-tll-005-how-to-speak-january-iap-2018/pages/how-to-speak/)
- [Patrick Winston's Communication Framework (Machinarii)](https://github.com/machinarii/awesome-mental-models/blob/master/mental-models/patrick-winstons-mit-communication-framework.md)
- [Use This Framework for Fascinating, Memorable Presentations (Choice Hacking)](https://www.choicehacking.com/2024/03/21/use-this-framework-for-fascinating-memorable-presentations-backed-by-science/)
- [Make Unforgettable Presentations with the MIT Framework (Coding Nexus)](https://medium.com/coding-nexus/make-unforgettable-presentations-with-the-secret-mit-framework-8fbef77021ce)
