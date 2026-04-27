---
name: creating-course-html
description: >
  Create a fully self-contained, interactive HTML course file from any source material or topic.
  Use this skill whenever the user asks to: create a course, build a training module, package
  knowledge as an interactive lesson, convert documentation into a learning experience, generate
  a slide-based tutorial, produce a 15-minute or 30-minute course, or build any kind of
  structured educational HTML. Triggers on keywords: "course", "training", "learn", "lesson",
  "module", "tutorial HTML", "interactive slides", "teach non-developers", "onboarding material",
  "workshop", "cheatsheet course". Always use this skill — even for short or informal requests —
  whenever the output is a self-contained HTML learning experience.
---

# Course HTML Skill

Produces a fully self-contained, interactive HTML course file from any source material (spec,
markdown, document, topic description). No external dependencies except Google Fonts. Opens
directly in any browser.

## Step 0 — Read the inputs before writing anything

Before generating a single line of HTML, extract these from the conversation:

| Input | Where to look | Fallback |
|---|---|---|
| Source material | Attached doc / pasted text | Ask: "What's the course about?" |
| Target audience | Stated in prompt | Assume non-technical professional |
| Duration | Stated ("15-min", "30-min") | Default: 15 min = 5 slides × 3 min |
| Tone | Inferred from domain | Technical domain → terminal/dark; soft domain → light |

**Duration → slide count formula:**
- 15 minutes = 5 slides (3 min each)
- 30 minutes = 5 slides (5–6 min each, richer content per slide)
- Other durations: round to nearest 5-slide structure

---

## Step 1 — Structure the course

Decompose the source material into exactly **5 slides**. Each slide = one module.

**Universal 5-slide arc:**

| Slide | Module type | Purpose |
|---|---|---|
| 1 | **What / Why** | Context, the problem solved, key concepts defined |
| 2 | **How it works** | Core mechanism, process, or architecture |
| 3 | **Components / Anatomy** | Parts, agents, steps, building blocks |
| 4 | **In practice** | Real invocations, examples, patterns |
| 5 | **Mastery / Refine** | Best practices, testing, checklists, next steps |

Adapt the arc to the domain. For a trading system: scan → analyze → confirm → size → manage.
For a meta-workflow: research → plan → build → document → test. The arc is flexible — what
matters is that each slide has a single, clear teaching objective.

**Quiz rule:** Every slide must end with at least one quiz question that tests the slide's
core concept. Use multiple-choice with 3 options (one correct, two plausible wrong answers).

---

## Step 2 — Choose the design theme

Match the design theme to the domain and audience:

### Theme A — Dark Cyberpunk / Terminal (default for technical topics)
Use for: developer tools, agent systems, trading, data pipelines, CLI tools, anything
targeting engineers or quant researchers.

```css
--bg: #08090d;  --bg-surface: #0d0f17;  --bg-card: #12141f;
--text: #e6e8f2;  --text-mid: #888ba6;  --text-dim: #41445a;
/* Primary accent: pick ONE neon */
--accent: #3df5e0;   /* cyan  — for data/systems topics */
--accent: #c8b8ff;   /* violet — for AI/agent topics    */
--accent: #4fffb0;   /* green — for trading/finance     */
--font: 'Bricolage Grotesque'; --mono: 'Space Mono';
```
Always add the scanline overlay (see references/components.md → Scanline).

### Theme B — Light Editorial (for non-technical / business audiences)
Use for: HR, onboarding, business process, soft skills, product training.

```css
--bg: #fafafa;  --bg-card: #ffffff;  --text: #111827;
--accent: #2563eb; /* blue */
--font: 'Bricolage Grotesque'; --mono: 'JetBrains Mono';
```

### Theme C — Warm Neutral (for design, creative, mixed audiences)
```css
--bg: #f5f0e8;  --bg-card: #fffdf9;  --text: #2c2416;
--accent: #d97706; /* amber */
--font: 'Bricolage Grotesque';
```

**Rule:** Once a theme is chosen, apply it consistently. Never mix themes within a file.

---

## Step 3 — Select components per slide

Each slide is built from a combination of these components. Read `references/components.md`
for full HTML/CSS/JS for each component before writing the slide.

### Informational components
- `CardGrid` — 2–4 concept cards in a responsive grid
- `CompareTable` — side-by-side "before vs after" or "A vs B"
- `SpecTable` — agent/step tables with model pills or badges
- `PipelineDiagram` — clickable horizontal flow nodes with expand panels
- `Timeline` — expandable vertical steps (ideal for process walkthroughs)
- `CodeBlock` — syntax-highlighted, copy-button-enabled prompt/code example
- `QuoteBlock` — pull-quote or key mental model callout
- `Callout` — tip / warning / info / success message box

### Interactive components
- `Quiz` — multiple-choice with instant correct/wrong feedback
- `Checklist` — tickable hands-on exercise list
- `Calculator` — input-driven number outputs (e.g. position sizer, time estimator)
- `ToggleDetail` — click to reveal deeper explanation

### Structural components (every slide)
- `SlideHeader` — eyebrow label + title + subtitle
- `SectionDivider` — 1px border between major sections

**Component selection guide per slide type:**

| Slide | Recommended components |
|---|---|
| What/Why | CardGrid (3 cards) + QuoteBlock + Quiz |
| How it works | PipelineDiagram or Timeline + CodeBlock + Callout |
| Components/Anatomy | SpecTable + CardGrid + Quiz |
| In practice | CodeBlock × 3–5 + Callout (tip) + Quiz |
| Mastery | BestPracticeRows + Checklist + CTA box |

---

## Step 4 — Build the HTML file

### File structure (always single-file)

```
<!DOCTYPE html>
<html lang="en">
<head>
  <!-- Google Fonts (Bricolage Grotesque + Space Mono) -->
  <!-- <style> with :root vars + all component CSS -->
</head>
<body>
  <div class="wrap">
    <!-- Top bar: course label + live timer -->
    <!-- Progress bar -->
    <!-- Module tabs (one per slide) -->

    <!-- Slide 0 ... Slide N (display:none except .active) -->

    <!-- Nav row: ← Previous | counter | Next → -->
  </div>
  <script>
    <!-- Navigation logic -->
    <!-- Timer -->
    <!-- Per-slide interactivity (quiz, checklist, pipeline, etc.) -->
  </script>
</body>
</html>
```

### Mandatory shell features (every course file)

1. **Live elapsed timer** — `setInterval` counting MM:SS, shown in top-right with a pulsing dot
2. **Progress bar** — fills from 5% → 100% as slides advance; gradient from accent to secondary
3. **Module tabs** — one tab per slide; `.active` highlighted; `.done` style after visiting
4. **Slide fade-in animation** — `@keyframes fadeUp` on `.slide.active`
5. **Prev/Next navigation** — disabled states, "Complete" on last slide
6. **Slide counter** — "Slide N of 5" between nav buttons

### JavaScript architecture

```js
let cur = 0; const TOTAL = 5;
let timerSec = 0;
const done = new Set();

function goTo(idx){ done.add(cur); cur=idx; render(); }
function nav(d){ done.add(cur); cur=Math.max(0,Math.min(TOTAL-1,cur+d)); render(); }

function render(){
  // toggle .active on slides
  // toggle .active/.done on tabs
  // update progress bar width
  // update slide counter
  // disable/enable nav buttons
}
```

All per-slide interactions (quiz, checklist, pipeline expand, copy buttons) are implemented
as standalone functions called from `onclick` attributes. No frameworks, no bundlers.

---

## Step 5 — Quality checklist before saving

Run through these before writing the output file:

- [ ] Exactly 5 slides, each with a clear single teaching objective
- [ ] Every slide has at least one quiz with correct/wrong feedback text
- [ ] All interactive components work without JavaScript errors
- [ ] Copy buttons on all code blocks
- [ ] Timer, progress bar, and tab navigation all functional
- [ ] Design theme applied consistently (no mixed CSS variable sets)
- [ ] File is fully self-contained (no missing external resources)
- [ ] Content faithfully represents the source material
- [ ] CTA or next-steps present on the final slide
- [ ] Risk/disclaimer added if domain is financial or medical

---

## Output

Save to `/mnt/user-data/outputs/[topic-slug]-course.html` and call `present_files`.

Naming convention:
- `pullback-trading-course.html`
- `workflow-builder-course.html`
- `claude-agent-workflows-course.html`

After presenting, summarize:
1. The 5 module titles
2. Which interactive components were used on each slide
3. Any domain-specific design choices made (accent color, theme variant)

---

## Reference files

Read these when building the actual HTML:

- `references/components.md` — Complete HTML/CSS/JS for every component
- `references/themes.md` — Full CSS variable sets for all three themes + Google Fonts imports
