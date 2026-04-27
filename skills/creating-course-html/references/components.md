# Course HTML — Component Library

Full HTML/CSS/JS for every reusable component. Copy-paste into the `<style>` block and HTML body as needed. All components are designed for both dark and light themes via CSS variables.

---

## Scanline Overlay

Add to `body::before`. Creates the subtle CRT scanline texture used in dark/cyberpunk theme.

```css
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
```

---

## Top Bar

```html
<div class="top-bar">
  <div class="course-id">COURSE TITLE — 15-min practical course</div>
  <div class="timer-wrap">
    <div class="timer-dot"></div>
    <div class="timer-val" id="timer">00:00</div>
  </div>
</div>
```

```css
.top-bar { display:flex; align-items:center; justify-content:space-between; margin-bottom:1.75rem; }
.course-id { font-family:var(--mono); font-size:10px; letter-spacing:.12em; text-transform:uppercase; color:var(--text-dim); }
.timer-wrap { display:flex; align-items:center; gap:8px; }
.timer-dot { width:6px; height:6px; border-radius:50%; background:var(--accent); box-shadow:0 0 8px var(--accent-glow); animation:pulse 1.4s ease-in-out infinite; }
.timer-val { font-family:var(--mono); font-size:13px; color:var(--accent); letter-spacing:.06em; }
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.25}}
```

---

## Progress Bar

```html
<div class="progress-track">
  <div class="progress-fill" id="pfill" style="width:5%"></div>
</div>
```

```css
.progress-track { height:2px; background:var(--border); border-radius:2px; margin-bottom:1.75rem; overflow:hidden; }
.progress-fill { height:100%; background:linear-gradient(90deg,var(--accent),var(--accent-2,var(--accent))); border-radius:2px; transition:width .5s cubic-bezier(.4,0,.2,1); box-shadow:0 0 10px var(--accent-glow); }
```

JS: `document.getElementById('pfill').style.width = Math.round(((cur+1)/TOTAL)*100)+'%';`

---

## Module Tabs

```html
<div class="module-tabs">
  <button class="module-tab active" onclick="goTo(0)">01 / Label</button>
  <button class="module-tab" onclick="goTo(1)">02 / Label</button>
</div>
```

```css
.module-tabs { display:flex; gap:6px; margin-bottom:2.5rem; overflow-x:auto; padding-bottom:4px; scrollbar-width:none; }
.module-tabs::-webkit-scrollbar{display:none}
.module-tab { font-family:var(--mono); font-size:10px; letter-spacing:.05em; padding:5px 12px; border-radius:999px; border:1px solid var(--border); cursor:pointer; white-space:nowrap; color:var(--text-dim); background:transparent; transition:all .2s; }
.module-tab:hover { border-color:var(--border-mid); color:var(--text-mid); }
.module-tab.active { background:var(--accent-dim); border-color:var(--accent); color:var(--accent); box-shadow:0 0 14px var(--accent-glow); }
.module-tab.done { border-color:var(--border-mid); color:var(--text-mid); }
```

---

## Slide Shell + Fade Animation

```html
<div class="slide active" id="slide-0"> ... </div>
<div class="slide" id="slide-1"> ... </div>
```

```css
.slide { display:none; animation:fadeUp .3s ease; }
.slide.active { display:block; }
@keyframes fadeUp{from{opacity:0;transform:translateY(7px)}to{opacity:1;transform:none}}
```

---

## Slide Header

```html
<div class="eyebrow"><span class="eyebrow-line"></span>Module 1 — Label · 3 min</div>
<div class="slide-title">Title of this module</div>
<div class="slide-sub">One or two sentences describing what the learner will understand by the end of this slide.</div>
```

```css
.eyebrow { font-family:var(--mono); font-size:10px; letter-spacing:.1em; text-transform:uppercase; color:var(--accent); margin-bottom:10px; display:flex; align-items:center; gap:8px; }
.eyebrow-line { width:24px; height:1px; background:var(--accent); box-shadow:0 0 6px var(--accent-glow); }
.slide-title { font-size:27px; font-weight:600; color:var(--text); line-height:1.25; margin-bottom:10px; letter-spacing:-.01em; }
.slide-sub { font-size:14px; color:var(--text-mid); line-height:1.7; max-width:640px; margin-bottom:2rem; }
```

---

## CardGrid

3–4 concept cards in a responsive grid.

```html
<div class="card-grid">
  <div class="card">
    <div class="card-tag">Tag label</div>
    <div class="card-title">Card Title</div>
    <div class="card-body">Explanation text here. Keep to 2–3 sentences.</div>
  </div>
</div>
```

```css
.card-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(175px,1fr)); gap:12px; margin-bottom:2rem; }
.card { background:var(--bg-card); border:1px solid var(--border); border-radius:var(--radius); padding:1.1rem 1.2rem; transition:border-color .2s; }
.card:hover { border-color:var(--border-mid); }
.card-tag { font-family:var(--mono); font-size:9px; letter-spacing:.08em; text-transform:uppercase; color:var(--accent); margin-bottom:8px; }
.card-title { font-size:13px; font-weight:600; color:var(--text); margin-bottom:5px; }
.card-body { font-size:12px; color:var(--text-mid); line-height:1.55; }
```

---

## CompareTable (Two-Column)

```html
<div class="compare-row">
  <div class="compare-col">
    <div class="compare-label">Option A / Before</div>
    <div class="compare-item">Point one</div>
    <div class="compare-item">Point two</div>
  </div>
  <div class="compare-col highlight">
    <div class="compare-label accent">Option B / After</div>
    <div class="compare-item">Point one</div>
    <div class="compare-item">Point two</div>
  </div>
</div>
```

```css
.compare-row { display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-bottom:2rem; }
@media(max-width:540px){.compare-row{grid-template-columns:1fr}}
.compare-col { background:var(--bg-card); border:1px solid var(--border); border-radius:var(--radius); padding:1.1rem 1.25rem; }
.compare-col.highlight { border-color:var(--accent); box-shadow:0 0 24px var(--accent-glow); }
.compare-label { font-family:var(--mono); font-size:10px; letter-spacing:.08em; text-transform:uppercase; color:var(--text-dim); margin-bottom:12px; }
.compare-label.accent { color:var(--accent); }
.compare-item { font-size:13px; color:var(--text-mid); padding:5px 0; border-bottom:1px solid var(--border); display:flex; align-items:flex-start; gap:8px; }
.compare-item:last-child{border-bottom:none}
.compare-item::before{content:'›';color:var(--text-dim);flex-shrink:0}
```

---

## SpecTable

Agent/step tables with model pills or status badges.

```html
<table class="spec-table">
  <thead><tr><th>Agent</th><th>Model</th><th>Role</th></tr></thead>
  <tbody>
    <tr>
      <td>agent.name</td>
      <td><span class="model-pill pill-sonnet">sonnet</span></td>
      <td>What this agent does in one sentence.</td>
    </tr>
  </tbody>
</table>
```

```css
.spec-table { width:100%; border-collapse:collapse; font-size:12px; margin-bottom:2rem; }
.spec-table thead tr { border-bottom:1px solid var(--border-mid); }
.spec-table th { font-family:var(--mono); font-size:9px; letter-spacing:.08em; text-transform:uppercase; color:var(--text-dim); padding:0 12px 10px 0; text-align:left; font-weight:400; }
.spec-table td { padding:9px 12px 9px 0; border-bottom:1px solid var(--border); color:var(--text-mid); vertical-align:top; }
.spec-table tr:last-child td{border-bottom:none}
.spec-table td:first-child { font-family:var(--mono); font-size:11px; color:var(--accent); white-space:nowrap; }
.model-pill { display:inline-block; font-family:var(--mono); font-size:9px; padding:2px 7px; border-radius:999px; }
/* Add colour variants as needed: */
.pill-sonnet { background:rgba(96,165,250,.09); color:#60a5fa; border:1px solid rgba(96,165,250,.2); }
.pill-fast   { background:rgba(74,222,128,.09); color:#4ade80; border:1px solid rgba(74,222,128,.2); }
.pill-o3     { background:rgba(251,191,36,.09); color:#fbbf24; border:1px solid rgba(251,191,36,.2); }
```

---

## PipelineDiagram (Clickable)

Horizontal flow nodes that expand a detail panel on click.

```html
<div class="pipeline-wrap">
  <div class="pipeline">
    <div class="pipe-node" id="pn0" onclick="selectPipe(0)">
      <div class="pipe-phase">Phase 1</div>
      <div class="pipe-name">Node Name</div>
      <div class="pipe-sub">subtitle</div>
    </div>
    <div class="pipe-arrow">→</div>
    <!-- repeat for each node -->
  </div>
  <div class="pipe-panel" id="pipe-panel">
    <div class="pipe-panel-title" id="pp-title"></div>
    <div id="pp-body"></div>
  </div>
</div>
```

```css
.pipeline-wrap { margin-bottom:2rem; overflow-x:auto; }
.pipeline { display:flex; align-items:stretch; gap:0; min-width:500px; }
.pipe-node { flex:1; background:var(--bg-card); border:1px solid var(--border); border-radius:var(--radius-sm); padding:10px 8px; text-align:center; cursor:pointer; transition:all .2s; }
.pipe-node:hover,.pipe-node.lit { border-color:var(--accent); box-shadow:0 0 16px var(--accent-glow); background:var(--accent-dim); }
.pipe-phase { font-family:var(--mono); font-size:9px; letter-spacing:.06em; color:var(--text-dim); margin-bottom:4px; }
.pipe-name  { font-size:12px; font-weight:600; color:var(--text); }
.pipe-sub   { font-size:10px; color:var(--text-mid); margin-top:3px; line-height:1.3; }
.pipe-arrow { display:flex; align-items:center; padding:0 4px; color:var(--text-dim); font-size:14px; flex-shrink:0; }
.pipe-panel { background:var(--bg-surface); border:1px solid var(--border-mid); border-radius:var(--radius); padding:1rem 1.2rem; margin-top:12px; display:none; }
.pipe-panel.vis { display:block; animation:fadeUp .2s ease; }
.pipe-panel-title { font-family:var(--mono); font-size:10px; letter-spacing:.08em; text-transform:uppercase; color:var(--accent); margin-bottom:10px; }
.pipe-row { display:flex; justify-content:space-between; gap:12px; margin-bottom:7px; font-size:12px; }
.pipe-row:last-child{margin-bottom:0}
.pr-label { color:var(--text-dim); white-space:nowrap; }
.pr-val   { color:var(--text); text-align:right; font-family:var(--mono); font-size:11px; }
```

```js
// Data array — one object per node
const pipeData = [
  { title: 'Node Title', rows: [['Label','Value'],['Label','Value']] },
  // ...
];
let openPipe = -1;
function selectPipe(idx){
  const nodes = document.querySelectorAll('.pipe-node');
  const panel = document.getElementById('pipe-panel');
  if(openPipe===idx){ nodes[idx].classList.remove('lit'); panel.classList.remove('vis'); openPipe=-1; return; }
  nodes.forEach(n=>n.classList.remove('lit'));
  nodes[idx].classList.add('lit');
  openPipe=idx;
  const d = pipeData[idx];
  document.getElementById('pp-title').textContent = d.title;
  document.getElementById('pp-body').innerHTML = d.rows.map(r=>
    `<div class="pipe-row"><span class="pr-label">${r[0]}</span><span class="pr-val">${r[1]}</span></div>`
  ).join('');
  panel.classList.add('vis');
}
```

---

## Timeline (Expandable Steps)

Vertical steps that expand on click. Ideal for process walkthroughs.

```html
<div class="timeline">
  <div class="tl-step" onclick="toggleStep(0)">
    <div class="tl-left">
      <div class="tl-num" id="tln-0">1</div>
      <div class="tl-line"></div>
    </div>
    <div class="tl-body">
      <div><span class="tl-mode mode-ask">MODE LABEL</span></div>
      <div class="tl-title">Step Title</div>
      <div class="tl-desc">Brief description always visible.</div>
      <div class="tl-detail">
        <!-- Expanded content: template box, code blocks, callouts -->
      </div>
    </div>
  </div>
</div>
```

```css
.timeline { margin-bottom:2rem; }
.tl-step { display:flex; gap:16px; padding:14px 0; border-bottom:1px solid var(--border); cursor:pointer; align-items:flex-start; }
.tl-step:last-child{border-bottom:none}
.tl-left { display:flex; flex-direction:column; align-items:center; gap:4px; flex-shrink:0; }
.tl-num { width:32px; height:32px; border-radius:50%; background:var(--bg-card); border:1px solid var(--border-mid); display:flex; align-items:center; justify-content:center; font-family:var(--mono); font-size:11px; font-weight:700; color:var(--text-dim); transition:all .2s; }
.tl-step.active-step .tl-num,.tl-step:hover .tl-num { background:var(--accent-dim); border-color:var(--accent); color:var(--accent); box-shadow:0 0 12px var(--accent-glow); }
.tl-line { width:1px; flex:1; background:var(--border); min-height:12px; }
.tl-step:last-child .tl-line{display:none}
.tl-body { flex:1; padding-top:4px; }
.tl-mode { display:inline-flex; align-items:center; font-family:var(--mono); font-size:9px; letter-spacing:.06em; text-transform:uppercase; padding:2px 8px; border-radius:999px; margin-bottom:6px; font-weight:700; }
/* Mode badge colour variants */
.mode-ask   { background:rgba(167,139,250,.09); color:#a78bfa; border:1px solid rgba(167,139,250,.2); }
.mode-plan  { background:rgba(251,191,36,.09);  color:#fbbf24; border:1px solid rgba(251,191,36,.2); }
.mode-agent { background:rgba(61,245,224,.09);  color:#3df5e0; border:1px solid rgba(61,245,224,.2); }
.mode-test  { background:rgba(251,113,133,.09); color:#fb7185; border:1px solid rgba(251,113,133,.2); }
.tl-title { font-size:14px; font-weight:600; color:var(--text); margin-bottom:4px; }
.tl-desc  { font-size:12px; color:var(--text-mid); line-height:1.55; }
.tl-detail { margin-top:10px; display:none; }
.tl-step.active-step .tl-detail { display:block; animation:fadeUp .2s ease; }
```

```js
let openStep = -1;
function toggleStep(idx){
  const steps = document.querySelectorAll('.tl-step');
  if(openStep===idx){ steps[idx].classList.remove('active-step'); openStep=-1; return; }
  if(openStep>=0) steps[openStep].classList.remove('active-step');
  steps[idx].classList.add('active-step');
  openStep=idx;
}
```

---

## CodeBlock (with copy button)

```html
<div class="code-wrap">
  <div class="code-label">Label describing this code</div>
  <div class="code-block" style="position:relative">
    <button class="copy-btn" onclick="copyCode(this)">COPY</button>
    <span class="kw">keyword</span> <span class="str">"string value"</span>
    <span class="cmt"># comment</span>
    <span class="ph">placeholder</span>
  </div>
</div>
```

```css
.code-wrap { margin-bottom:14px; }
.code-label { font-family:var(--mono); font-size:9px; letter-spacing:.1em; text-transform:uppercase; color:var(--text-dim); margin-bottom:5px; display:flex; align-items:center; gap:8px; }
.code-label::after { content:''; flex:1; height:1px; background:var(--border); }
.code-block { background:var(--bg-surface); border:1px solid var(--border); border-radius:var(--radius); padding:1rem 1.2rem; font-family:var(--mono); font-size:12px; line-height:1.75; color:var(--text-mid); overflow-x:auto; position:relative; }
/* Syntax colour classes — adapt accent colours to theme */
.code-block .kw  { color:var(--accent); }
.code-block .str { color:#fbbf24; }       /* amber  */
.code-block .cmt { color:var(--text-dim); font-style:italic; }
.code-block .ph  { color:#a78bfa; }       /* violet */
.code-block .ag  { color:#60a5fa; }       /* blue   */
.copy-btn { position:absolute; top:8px; right:10px; font-family:var(--mono); font-size:9px; letter-spacing:.06em; padding:3px 8px; border-radius:4px; background:var(--bg-card); border:1px solid var(--border-mid); color:var(--text-dim); cursor:pointer; transition:all .15s; }
.copy-btn:hover { color:var(--accent); border-color:var(--accent); }
.copy-btn.copied { color:#4ade80; border-color:#4ade80; }
```

```js
function copyCode(btn){
  const txt = btn.parentElement.innerText.replace('COPY','').replace('COPIED','').trim();
  navigator.clipboard.writeText(txt).catch(()=>{});
  btn.textContent='COPIED'; btn.classList.add('copied');
  setTimeout(()=>{ btn.textContent='COPY'; btn.classList.remove('copied'); },1500);
}
```

---

## TemplateBox

Visual prompt template with `[placeholder]` brackets.

```html
<div class="template-box">
  <div class="template-label">Prompt template</div>
  <div class="template-text">
    Do something for <span class="bracket">[who]</span> using <span class="bracket">[what]</span>
  </div>
</div>
```

```css
.template-box { border:1px dashed rgba(61,245,224,.3); border-radius:var(--radius); padding:1rem 1.2rem; margin-bottom:1.5rem; background:rgba(61,245,224,.03); }
.template-label { font-family:var(--mono); font-size:9px; letter-spacing:.1em; text-transform:uppercase; color:var(--accent); margin-bottom:8px; display:flex; align-items:center; gap:8px; }
.template-label::after { content:''; flex:1; height:1px; background:rgba(61,245,224,.2); }
.template-text { font-size:14px; color:var(--text); line-height:1.6; }
.template-text .bracket { color:#a78bfa; }
```

---

## Callout

Tip, warning, info, or success message.

```html
<div class="callout tip">
  <div class="callout-icon">◈</div>
  <div class="callout-body"><strong>Label:</strong> Message text here.</div>
</div>
```

```css
.callout { display:flex; gap:12px; padding:12px 14px; border-radius:var(--radius); margin-bottom:12px; }
.callout-icon { font-size:16px; flex-shrink:0; }
.callout-body { font-size:13px; line-height:1.6; color:inherit; }
.callout.tip  { background:rgba(61,245,224,.08);  border:1px solid rgba(61,245,224,.15);  color:#3df5e0; }
.callout.warn { background:rgba(251,191,36,.09);  border:1px solid rgba(251,191,36,.15);  color:#fbbf24; }
.callout.info { background:rgba(167,139,250,.09); border:1px solid rgba(167,139,250,.15); color:#a78bfa; }
.callout.good { background:rgba(74,222,128,.09);  border:1px solid rgba(74,222,128,.15);  color:#4ade80; }
```

---

## Quiz (Multiple Choice)

```html
<div class="quiz-q">Question text here?</div>
<div id="q0">
  <div class="quiz-opt" onclick="qz('q0',this,false)"><span class="opt-key">A</span>Wrong option</div>
  <div class="quiz-opt" onclick="qz('q0',this,true)"><span class="opt-key">B</span>Correct option</div>
  <div class="quiz-opt" onclick="qz('q0',this,false)"><span class="opt-key">C</span>Wrong option</div>
  <div class="quiz-fb" id="q0-fb"></div>
</div>
```

```css
.quiz-q { font-size:13px; font-weight:600; color:var(--text); margin-bottom:10px; }
.quiz-opt { background:var(--bg-card); border:1px solid var(--border); border-radius:var(--radius-sm); padding:10px 14px; margin-bottom:8px; cursor:pointer; font-size:13px; color:var(--text); transition:all .15s; display:flex; align-items:center; gap:12px; }
.quiz-opt:hover { border-color:var(--border-mid); background:var(--bg-hover,var(--bg-card)); }
.quiz-opt.correct { border-color:#4ade80; background:rgba(74,222,128,.09); color:#4ade80; }
.quiz-opt.wrong   { border-color:#fb7185; background:rgba(251,113,133,.09); color:#fb7185; }
.opt-key { width:24px; height:24px; border-radius:50%; border:1px solid var(--border-mid); display:flex; align-items:center; justify-content:center; font-family:var(--mono); font-size:10px; font-weight:700; flex-shrink:0; }
.quiz-fb { font-size:12px; padding:9px 14px; border-radius:var(--radius-sm); margin-top:8px; display:none; line-height:1.55; }
.quiz-fb.show   { display:block; }
.quiz-fb.ok  { background:rgba(74,222,128,.09); color:#4ade80; border:1px solid rgba(74,222,128,.2); }
.quiz-fb.bad { background:rgba(251,113,133,.09); color:#fb7185; border:1px solid rgba(251,113,133,.2); }
```

```js
// qMsg object: one key per quiz id, with .t (correct text) and .f (wrong text)
const qMsg = {
  q0: { t:'Correct! Explanation of why.', f:'Not quite. Explanation of correct answer.' },
};
function qz(id, el, ok){
  document.getElementById(id).querySelectorAll('.quiz-opt').forEach(o=>{ o.onclick=null; o.style.cursor='default'; });
  el.classList.add(ok?'correct':'wrong');
  const fb = document.getElementById(id+'-fb');
  fb.classList.add('show', ok?'ok':'bad');
  fb.textContent = ok ? qMsg[id].t : qMsg[id].f;
}
```

---

## Checklist (Tickable)

```html
<div class="checklist">
  <div class="chk-item" onclick="ck(this)">
    <div class="chk-box"></div>
    <div class="chk-label">Task description goes here</div>
  </div>
</div>
```

```css
.checklist { margin-bottom:2rem; }
.chk-item { display:flex; align-items:flex-start; gap:12px; padding:10px 0; border-bottom:1px solid var(--border); cursor:pointer; }
.chk-item:last-child{border-bottom:none}
.chk-box { width:18px; height:18px; border-radius:4px; border:1px solid var(--border-mid); flex-shrink:0; margin-top:2px; display:flex; align-items:center; justify-content:center; transition:all .2s; }
.chk-box.on { background:var(--accent); border-color:var(--accent); box-shadow:0 0 10px var(--accent-glow); }
.chk-box.on::after { content:''; display:block; width:9px; height:5px; border-left:1.5px solid var(--bg); border-bottom:1.5px solid var(--bg); transform:rotate(-45deg) translateY(-1px); }
.chk-label { font-size:13px; color:var(--text); line-height:1.5; }
.chk-label.on { color:var(--text-dim); text-decoration:line-through; }
```

```js
function ck(el){ el.querySelector('.chk-box').classList.toggle('on'); el.querySelector('.chk-label').classList.toggle('on'); }
```

---

## BestPracticeRows

Numbered tips card.

```html
<div class="bp-card">
  <div class="bp-row">
    <div class="bp-icon" style="color:var(--accent)">①</div>
    <div>
      <div class="bp-title">Tip title</div>
      <div class="bp-desc">Explanation of the best practice in 1–2 sentences.</div>
    </div>
  </div>
</div>
```

```css
.bp-card { background:var(--bg-card); border:1px solid var(--border); border-radius:var(--radius); padding:0; margin-bottom:1.5rem; overflow:hidden; }
.bp-row { display:flex; gap:14px; align-items:flex-start; padding:12px 1.2rem; border-bottom:1px solid var(--border); }
.bp-row:last-child{border-bottom:none}
.bp-icon { font-size:14px; flex-shrink:0; margin-top:2px; }
.bp-title { font-size:13px; font-weight:600; color:var(--text); margin-bottom:3px; }
.bp-desc  { font-size:12px; color:var(--text-mid); line-height:1.55; }
```

---

## CriteriaGrid

Metric boxes with colour coding (green/amber/red).

```html
<div class="criteria-grid">
  <div class="criteria-box green">
    <div class="criteria-label">Metric name</div>
    <div class="criteria-val">≥ 3%</div>
    <div class="criteria-sub">Sub-label</div>
  </div>
</div>
```

```css
.criteria-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:10px; margin-bottom:2rem; }
@media(max-width:560px){.criteria-grid{grid-template-columns:1fr 1fr}}
.criteria-box { background:var(--bg-card); border:1px solid var(--border); border-radius:var(--radius-sm); padding:10px 12px; }
.criteria-label { font-family:var(--mono); font-size:9px; letter-spacing:.07em; text-transform:uppercase; color:var(--text-dim); margin-bottom:5px; }
.criteria-val { font-size:14px; font-weight:600; color:var(--text); }
.criteria-sub { font-size:11px; color:var(--text-mid); margin-top:2px; }
.criteria-box.green { border-color:rgba(74,222,128,.2); background:rgba(74,222,128,.09); }
.criteria-box.green .criteria-val { color:#4ade80; }
.criteria-box.amber { border-color:rgba(251,191,36,.2); background:rgba(251,191,36,.09); }
.criteria-box.amber .criteria-val { color:#fbbf24; }
.criteria-box.red { border-color:rgba(251,113,133,.2); background:rgba(251,113,133,.09); }
.criteria-box.red .criteria-val { color:#fb7185; }
```

---

## Calculator (Interactive Input → Output)

```html
<div class="calc-box">
  <div class="calc-label">Calculator label</div>
  <div class="calc-row">
    <label>Input label</label>
    <input type="number" id="val-a" value="100" oninput="calcResult()" />
  </div>
  <div class="calc-divider"></div>
  <div class="calc-results">
    <div class="calc-result">
      <div class="calc-result-label">Output label</div>
      <div class="calc-result-val" id="res-a">—</div>
    </div>
  </div>
</div>
```

```css
.calc-box { background:var(--bg-card); border:1px solid var(--border); border-radius:var(--radius); padding:1.25rem; margin-bottom:2rem; }
.calc-label { font-family:var(--mono); font-size:10px; letter-spacing:.08em; text-transform:uppercase; color:var(--accent); margin-bottom:14px; }
.calc-row { display:flex; align-items:center; gap:12px; margin-bottom:12px; }
.calc-row label { font-size:12px; color:var(--text-mid); min-width:120px; }
.calc-row input { flex:1; background:var(--bg-surface); border:1px solid var(--border-mid); border-radius:var(--radius-sm); padding:6px 10px; color:var(--text); font-family:var(--mono); font-size:12px; outline:none; transition:border-color .15s; }
.calc-row input:focus { border-color:var(--accent); box-shadow:0 0 10px var(--accent-glow); }
.calc-divider { height:1px; background:var(--border); margin:14px 0; }
.calc-results { display:grid; grid-template-columns:repeat(3,1fr); gap:10px; }
@media(max-width:480px){.calc-results{grid-template-columns:1fr 1fr}}
.calc-result { text-align:center; padding:10px; background:var(--bg-surface); border-radius:var(--radius-sm); border:1px solid var(--border); }
.calc-result-label { font-family:var(--mono); font-size:9px; letter-spacing:.07em; text-transform:uppercase; color:var(--text-dim); margin-bottom:5px; }
.calc-result-val { font-family:var(--mono); font-size:16px; font-weight:700; color:var(--accent); }
```

---

## CTA Box (Final Slide)

```html
<div class="cta-box">
  <div class="cta-title">What to do next</div>
  <div class="cta-body">Instructional text telling the learner the immediate next action to take.</div>
</div>
```

```css
.cta-box { background:var(--accent-dim); border:1px solid rgba(61,245,224,.2); border-radius:var(--radius); padding:1.25rem; margin-top:2rem; }
.cta-title { font-size:14px; font-weight:600; color:var(--accent); margin-bottom:6px; }
.cta-body  { font-size:13px; color:var(--text-mid); line-height:1.65; }
```

---

## Navigation Row

```html
<div class="nav-row">
  <button class="btn" id="btn-prev" onclick="nav(-1)" disabled>← Previous</button>
  <span class="slide-ctr" id="slide-ctr">Slide 1 of 5</span>
  <button class="btn btn-accent" id="btn-next" onclick="nav(1)">Next →</button>
</div>
```

```css
.nav-row { display:flex; align-items:center; justify-content:space-between; margin-top:2.5rem; padding-top:1.5rem; border-top:1px solid var(--border); }
.slide-ctr { font-family:var(--mono); font-size:11px; color:var(--text-dim); }
.btn { font-family:var(--font); font-size:13px; padding:8px 18px; border-radius:var(--radius-sm); border:1px solid var(--border-mid); cursor:pointer; color:var(--text); background:transparent; transition:all .2s; }
.btn:hover { background:var(--bg-hover,var(--bg-card)); border-color:var(--border-hi,var(--border-mid)); }
.btn:active{transform:scale(.98)}
.btn:disabled{opacity:.3;cursor:default;transform:none}
.btn-accent { background:var(--accent-dim); border-color:var(--accent); color:var(--accent); }
.btn-accent:hover { box-shadow:0 0 20px var(--accent-glow); }
```

---

## Section Divider

```html
<div class="div"></div>
```

```css
.div { height:1px; background:var(--border); margin:1.75rem 0; }
```

---

## Full JS Bootstrap (copy into every file)

```js
let cur = 0; const TOTAL = 5;
let timerSec = 0;
const done = new Set();

setInterval(() => {
  timerSec++;
  const m = Math.floor(timerSec/60), s = timerSec%60;
  document.getElementById('timer').textContent = p(m)+':'+p(s);
}, 1000);
function p(n){ return n<10?'0'+n:n; }

function goTo(idx){ done.add(cur); cur=idx; render(); }
function nav(d){ done.add(cur); cur=Math.max(0,Math.min(TOTAL-1,cur+d)); render(); }

function render(){
  document.querySelectorAll('.slide').forEach((s,i)=>s.classList.toggle('active',i===cur));
  document.querySelectorAll('.module-tab').forEach((t,i)=>{
    t.classList.remove('active','done');
    if(i===cur) t.classList.add('active');
    else if(done.has(i)) t.classList.add('done');
  });
  document.getElementById('pfill').style.width = Math.round(((cur+1)/TOTAL)*100)+'%';
  document.getElementById('slide-ctr').textContent = 'Slide '+(cur+1)+' of '+TOTAL;
  document.getElementById('btn-prev').disabled = cur===0;
  const nb = document.getElementById('btn-next');
  nb.disabled = cur===TOTAL-1;
  nb.textContent = cur===TOTAL-1 ? 'Complete' : 'Next →';
}
```
