# Course HTML — Theme Reference

Full CSS variable sets and Google Fonts imports for all three themes. Copy the chosen theme block
into the `<style>` section of the course HTML file.

---

## How to choose a theme

| Domain type | Audience | Use theme |
|---|---|---|
| Developer tools, agent systems, trading, data pipelines, CLI, APIs | Engineers, quant researchers, power users | **A — Dark Cyberpunk** |
| Business process, HR, onboarding, soft skills, product training | Managers, non-technical staff, business users | **B — Light Editorial** |
| Design, creative workflows, mixed audiences | Designers, product teams, mixed roles | **C — Warm Neutral** |

**Rule:** Pick one theme per file and apply it consistently. Never mix variable sets.

---

## Theme A — Dark Cyberpunk / Terminal

### Accent colour variants (pick one per course, based on domain sub-type)

| Sub-type | Accent | Use for |
|---|---|---|
| Data / systems | `#3df5e0` cyan | data pipelines, RAG, backend systems |
| AI / agents | `#c8b8ff` violet | Claude, LLM, multi-agent, orchestration |
| Finance / trading | `#4fffb0` green | trading, quant research, fintech |
| General dev | `#60a5fa` blue | general developer tooling, APIs |

### Full CSS block

```css
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Bricolage+Grotesque:opsz,wght@12..96,300;12..96,400;12..96,500;12..96,600&display=swap');

:root {
  /* === SURFACES === */
  --bg:           #08090d;
  --bg-surface:   #0d0f17;
  --bg-card:      #12141f;
  --bg-hover:     #171928;

  /* === BORDERS === */
  --border:       rgba(255,255,255,0.06);
  --border-mid:   rgba(255,255,255,0.11);
  --border-hi:    rgba(255,255,255,0.20);

  /* === TEXT === */
  --text:         #e6e8f2;
  --text-mid:     #888ba6;
  --text-dim:     #41445a;

  /* === ACCENT — CHOOSE ONE BLOCK BELOW === */

  /* Cyan (data/systems) */
  --accent:       #3df5e0;
  --accent-dim:   rgba(61,245,224,0.08);
  --accent-glow:  rgba(61,245,224,0.20);

  /* Violet (AI/agents) — uncomment to use
  --accent:       #c8b8ff;
  --accent-dim:   rgba(200,184,255,0.09);
  --accent-glow:  rgba(200,184,255,0.22);
  */

  /* Green (finance/trading) — uncomment to use
  --accent:       #4fffb0;
  --accent-dim:   rgba(79,255,176,0.08);
  --accent-glow:  rgba(79,255,176,0.20);
  */

  /* Blue (general dev) — uncomment to use
  --accent:       #60a5fa;
  --accent-dim:   rgba(96,165,250,0.09);
  --accent-glow:  rgba(96,165,250,0.20);
  */

  /* === SECONDARY ACCENT (gradient end for progress bar) === */
  --accent-2:     #a78bfa;   /* violet secondary — works with all primary accents */

  /* === SEMANTIC COLOURS (used in callouts, quiz feedback) === */
  --c-green:      #4ade80;   --c-green-dim: rgba(74,222,128,0.09);
  --c-amber:      #fbbf24;   --c-amber-dim: rgba(251,191,36,0.09);
  --c-rose:       #fb7185;   --c-rose-dim:  rgba(251,113,133,0.09);
  --c-blue:       #60a5fa;   --c-blue-dim:  rgba(96,165,250,0.09);
  --c-violet:     #a78bfa;   --c-violet-dim:rgba(167,139,250,0.09);

  /* === SHAPE === */
  --radius:       10px;
  --radius-sm:    6px;

  /* === TYPOGRAPHY === */
  --font:         'Bricolage Grotesque', sans-serif;
  --mono:         'Space Mono', monospace;
}

*, *::before, *::after { box-sizing:border-box; margin:0; padding:0; }

body {
  background: var(--bg);
  color: var(--text);
  font-family: var(--font);
  min-height: 100vh;
  padding: 2rem 1rem 5rem;
  line-height: 1.6;
}

/* Scanline overlay — required for Theme A */
body::before {
  content: '';
  position: fixed; inset: 0;
  background: repeating-linear-gradient(
    0deg, transparent, transparent 2px,
    rgba(0,0,0,0.04) 2px, rgba(0,0,0,0.04) 4px
  );
  pointer-events: none;
  z-index: 9000;
}

/* Scrollbar styling */
::-webkit-scrollbar{width:4px;height:4px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:var(--border-mid);border-radius:2px}

.wrap { max-width:820px; margin:0 auto; }
```

---

## Theme B — Light Editorial

```css
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Bricolage+Grotesque:opsz,wght@12..96,300;12..96,400;12..96,500;12..96,600&display=swap');

:root {
  --bg:           #f8f9fc;
  --bg-surface:   #f0f2f8;
  --bg-card:      #ffffff;
  --bg-hover:     #f0f4ff;

  --border:       rgba(0,0,0,0.08);
  --border-mid:   rgba(0,0,0,0.14);
  --border-hi:    rgba(0,0,0,0.22);

  --text:         #111827;
  --text-mid:     #6b7280;
  --text-dim:     #9ca3af;

  /* Primary accent — blue */
  --accent:       #2563eb;
  --accent-dim:   rgba(37,99,235,0.08);
  --accent-glow:  rgba(37,99,235,0.15);
  --accent-2:     #7c3aed;

  --c-green:      #059669;  --c-green-dim: rgba(5,150,105,0.09);
  --c-amber:      #d97706;  --c-amber-dim: rgba(217,119,6,0.09);
  --c-rose:       #dc2626;  --c-rose-dim:  rgba(220,38,38,0.09);
  --c-blue:       #2563eb;  --c-blue-dim:  rgba(37,99,235,0.09);
  --c-violet:     #7c3aed;  --c-violet-dim:rgba(124,58,237,0.09);

  --radius:       10px;
  --radius-sm:    6px;
  --font:         'Bricolage Grotesque', sans-serif;
  --mono:         'Space Mono', monospace;
}

*, *::before, *::after { box-sizing:border-box; margin:0; padding:0; }

body {
  background: var(--bg);
  color: var(--text);
  font-family: var(--font);
  min-height: 100vh;
  padding: 2rem 1rem 5rem;
  line-height: 1.6;
}

/* No scanline for light theme */

.wrap { max-width:820px; margin:0 auto; }
```

---

## Theme C — Warm Neutral

```css
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,500;12..96,600&display=swap');

:root {
  --bg:           #f5f0e8;
  --bg-surface:   #ede8dc;
  --bg-card:      #fffdf9;
  --bg-hover:     #f0ebe0;

  --border:       rgba(60,40,10,0.10);
  --border-mid:   rgba(60,40,10,0.16);
  --border-hi:    rgba(60,40,10,0.26);

  --text:         #2c2416;
  --text-mid:     #7a6a50;
  --text-dim:     #b0a090;

  /* Primary accent — amber */
  --accent:       #d97706;
  --accent-dim:   rgba(217,119,6,0.09);
  --accent-glow:  rgba(217,119,6,0.18);
  --accent-2:     #b45309;

  --c-green:      #15803d;  --c-green-dim: rgba(21,128,61,0.09);
  --c-amber:      #d97706;  --c-amber-dim: rgba(217,119,6,0.09);
  --c-rose:       #be123c;  --c-rose-dim:  rgba(190,18,60,0.09);
  --c-blue:       #1d4ed8;  --c-blue-dim:  rgba(29,78,216,0.09);
  --c-violet:     #6d28d9;  --c-violet-dim:rgba(109,40,217,0.09);

  --radius:       10px;
  --radius-sm:    6px;
  --font:         'Bricolage Grotesque', sans-serif;
  --mono:         'Space Mono', monospace;
}

*, *::before, *::after { box-sizing:border-box; margin:0; padding:0; }

body {
  background: var(--bg);
  color: var(--text);
  font-family: var(--font);
  min-height: 100vh;
  padding: 2rem 1rem 5rem;
  line-height: 1.6;
}

.wrap { max-width:820px; margin:0 auto; }
```

---

## Callout colour overrides per theme

Component callout classes use semantic colour vars. These are theme-independent since each
theme defines `--c-green`, `--c-amber`, etc. The callout CSS just needs to reference those:

```css
/* Works across all themes: */
.callout.tip  { background:var(--accent-dim);  border-color:rgba(from var(--accent) r g b/.15); color:var(--accent); }
.callout.warn { background:var(--c-amber-dim); color:var(--c-amber); border:1px solid rgba(from var(--c-amber) r g b/.15); }
.callout.info { background:var(--c-violet-dim);color:var(--c-violet);border:1px solid rgba(from var(--c-violet) r g b/.15); }
.callout.good { background:var(--c-green-dim); color:var(--c-green); border:1px solid rgba(from var(--c-green) r g b/.15); }
```

For maximum browser compatibility, use explicit rgba values instead of `rgba(from ...)` syntax:

```css
/* Theme A (dark) explicit: */
.callout.tip  { background:rgba(61,245,224,.08);  border:1px solid rgba(61,245,224,.15);  color:var(--accent); }
.callout.warn { background:rgba(251,191,36,.09);  border:1px solid rgba(251,191,36,.15);  color:var(--c-amber); }
.callout.info { background:rgba(167,139,250,.09); border:1px solid rgba(167,139,250,.15); color:var(--c-violet); }
.callout.good { background:rgba(74,222,128,.09);  border:1px solid rgba(74,222,128,.15);  color:var(--c-green); }
```
