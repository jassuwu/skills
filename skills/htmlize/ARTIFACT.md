# HTML Artifact Format

Each artifact is one self-contained `.html` file — inline CSS, no external requests, works offline, shareable as a single file. It should read like a top-tier interactive blog post (think samwho.dev), **not** a Markdown dump in a `<body>`. The bar: someone too fed up to read an ugly plan will *want* to read this one.

Two jobs:
1. **Look typeset** — serif display over humanist-sans body, one calm column, real dark mode. (Design system, below.) Non-negotiable on every post.
2. **Make ideas move — only when it helps.** Interaction is what *can* earn HTML over Markdown, but most replies are mostly prose. Reach for a diagram or a live widget when it conveys something words can't; otherwise leave it out. A decorative visual is worse than none. (Explorable playbook, below.)

The server injects the live-reload script and a "← reading list" back-link, so **don't** add navigation chrome yourself.

---

## Required `<head>` metadata

The reading-list index is built from these — always set all three.

```html
<meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>A Specific, Real Title</title>                 <!-- index label + post H1 source -->
<meta name=description content="One-line summary of what this delivers.">  <!-- index sub-line -->
<meta name=htmlize-type content="plan">              <!-- index type chip + color -->
```

Valid `htmlize-type` values (each gets a distinct chip color): `plan`, `review`, `spec`, `explainer`, `comparison`, `research`, `runbook`, `design`, `note`. Reading time is computed automatically from word count.

---

## The scaffold

Copy this whole thing and fill it in. The token block, type, and components match the index exactly — don't swap the fonts or accent.

```html
<!doctype html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>…</title>
<meta name=description content="…">
<meta name=htmlize-type content="plan">
<style>
:root{
 --bg:#faf9f7;--surface:#fff;--surface-2:#f3f1ec;--fg:#1c1b19;--fg-strong:#100f0e;
 --muted:#6b685f;--faint:#6e6a61;--border:#e6e3dc;--border-2:#d8d4ca;
 --accent:#3a4ab8;--accent-text:#2e3a96;--accent-weak:#e9ebf7;--accent-border:#c3c8ec;
 --warn:#b4422a;--warn-weak:#f7e8e3;--ok:#2f7d4f;
 --code-bg:#1c2027;--code-fg:#d7dbe0;--code-bar:#14171c;--code-line:#2a2f37;
 /* data-semantic palette — explorables ONLY, never chrome. Darkened for stroke contrast on paper. */
 --d-orange:#a6690a;--d-sky:#2a78ad;--d-green:#0a7a59;--d-blue:#0a5a8c;--d-red:#b8420c;--d-pink:#974d7e;--d-slate:#475060;
 --display:"Iowan Old Style","Palatino Linotype","URW Palladio L",Palatino,P052,Georgia,serif;
 --body:Seravek,"Gill Sans Nova",Ubuntu,Calibri,"Source Sans Pro",-apple-system,BlinkMacSystemFont,"Segoe UI",system-ui,sans-serif;
 --mono:ui-monospace,"Cascadia Code","SF Mono",Menlo,Consolas,"DejaVu Sans Mono",monospace;
 --measure:68ch;--shell:60rem;--pad:1.25rem;
 --shadow:0 1px 2px rgba(28,27,25,.04),0 6px 20px rgba(28,27,25,.06);
 --ring:0 0 0 3px var(--accent-weak),0 0 0 1px var(--accent);
}
@media(prefers-color-scheme:dark){:root{
 --bg:#0e0f12;--surface:#15171c;--surface-2:#1b1e24;--fg:rgba(237,238,240,.92);--fg-strong:#f4f5f6;
 --muted:rgba(237,238,240,.58);--faint:rgba(237,238,240,.5);--border:rgba(237,238,240,.10);--border-2:rgba(237,238,240,.18);
 --accent:#97a4f0;--accent-text:#aab4f4;--accent-weak:#1e2236;--accent-border:#353c63;
 --warn:#e08266;--warn-weak:#2c1c18;--ok:#6cc28d;
 --code-bg:#0a0c10;--code-fg:rgba(231,233,238,.82);--code-bar:#111419;--code-line:rgba(237,238,240,.08);
 --d-orange:#e8a73b;--d-sky:#7cc3ec;--d-green:#3fbf95;--d-blue:#5aa6d8;--d-red:#ec7a4e;--d-pink:#cf94b4;--d-slate:#9aa3b5;
 --shadow:0 1px 2px rgba(0,0,0,.4),0 8px 28px rgba(0,0,0,.5);
}}
*{box-sizing:border-box}
html{font-size:16px;-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--fg);font:1.0625rem/1.7 var(--body);overflow-x:clip;
 -webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility;padding:4.5rem var(--pad) 6rem}
.post{max-width:var(--measure);margin-inline:auto}
.bleed{width:min(var(--shell),calc(100vw - 2*var(--pad)));margin-left:50%;transform:translateX(-50%)}
/* header block */
.eyebrow{font:.75rem/1.3 var(--body);text-transform:uppercase;letter-spacing:.14em;color:var(--accent-text);margin:0 0 .6rem}
h1{font:400 clamp(2.5rem,6vw,3.5rem)/1.1 var(--display);letter-spacing:-.01em;color:var(--fg-strong);margin:0;text-wrap:balance}
.lead{font:italic 1.25rem/1.5 var(--display);color:var(--muted);margin:.8rem 0 1.1rem}
.dateline{font:.8125rem/1.4 var(--mono);color:var(--muted);border-top:1px solid var(--border);padding-top:.9rem;margin:0 0 var(--s,3rem)}
/* sections & prose */
h2{font:400 clamp(1.75rem,4vw,2.25rem)/1.2 var(--display);letter-spacing:-.01em;color:var(--fg-strong);
 margin:4.5rem 0 1rem;border-top:1px solid var(--border);padding-top:1.6rem}
h3{font:400 1.4rem/1.25 var(--display);color:var(--fg-strong);margin:2.5rem 0 .8rem}
p{margin:0}p+p,ul,ol,figure,.callout,table,.explor{margin-top:1.4rem}
strong{color:var(--fg-strong);font-weight:600}
a{color:var(--accent-text);text-decoration:none}
a:hover{text-decoration:underline;text-decoration-thickness:1px;text-underline-offset:3px}
ul,ol{padding-left:1.3rem}li{margin:.4rem 0}
ul{list-style:none}ul>li::before{content:"→";color:var(--accent);margin-left:-1.3rem;margin-right:.5rem;font-weight:600}
:focus-visible{outline:none;box-shadow:var(--ring);border-radius:4px}
/* inline code: bold mono, no pill */
code{font:600 .9em var(--mono);color:var(--fg-strong)}
.tok{font-weight:500;background:var(--surface-2);border-radius:4px;padding:0 .35em}
/* code slab with filename chrome */
figure.code{margin:1.5rem 0;border-radius:10px;box-shadow:var(--shadow);overflow:hidden}
figure.code.bleed{margin-block:1.5rem}
.code-bar{display:flex;align-items:center;gap:.6rem;background:var(--code-bar);color:var(--faint);
 font:.8125rem/1 var(--mono);padding:.7rem .9rem}
.code-bar .copy{margin-left:auto;background:none;border:1px solid var(--code-line);color:var(--faint);
 font:.75rem var(--mono);padding:.25rem .6rem;border-radius:6px;cursor:pointer;opacity:0;transition:opacity .15s,color .15s}
figure.code:hover .copy{opacity:1}.code-bar .copy:hover{color:var(--code-fg)}
figure.code pre{margin:0;background:var(--code-bg);color:var(--code-fg);padding:1rem;overflow:auto;font:.875rem/1.6 var(--mono)}
pre code{font:inherit;color:inherit}
/* muted syntax tokens (hand-tag, optional) */
.k{color:#c39ac9}.s{color:#9ccb8f}.n{color:#e0a87e}.c{color:#8a93a1}.f{color:#8fa6e3}
/* callouts */
.callout{padding:1rem 1.25rem;border-radius:10px;border-left:3px solid var(--accent);background:var(--accent-weak)}
.callout.warn{border-color:var(--warn);background:var(--warn-weak)}
.callout .label{font:.75rem/1 var(--body);text-transform:uppercase;letter-spacing:.14em;color:var(--accent-text);margin-bottom:.5rem}
.callout.warn .label{color:var(--warn)}.callout :last-child{margin-bottom:0}
blockquote{margin:1.6rem 0;padding-left:1.1rem;border-left:3px solid var(--accent);font:italic 1.2rem/1.5 var(--display);color:var(--fg-strong)}
/* figures */
figure{margin:2rem 0}figure svg,figure canvas{display:block;width:100%;height:auto;margin-inline:auto}
figcaption{font:.9375rem/1.5 var(--body);color:var(--muted);text-align:center;margin-top:.7rem}
figcaption::before{content:"Fig · ";color:var(--faint);font:.8125rem var(--mono)}
/* tables */
.tw{margin-top:1.4rem;border:1px solid var(--border);border-radius:10px;overflow:hidden}
table{border-collapse:collapse;width:100%;font-size:.9375rem}
thead th{background:var(--surface-2);text-align:left;font:.75rem/1.4 var(--mono);text-transform:uppercase;letter-spacing:.06em;color:var(--muted);padding:.7rem .9rem}
td{padding:.6rem .9rem;border-top:1px solid var(--border)}tbody tr:hover{background:var(--accent-weak)}
/* margin sidenotes (collapse inline on narrow) */
.sn{float:right;clear:right;width:14rem;margin:.3rem -16rem .8rem 0;font:.9rem/1.5 var(--body);color:var(--muted)}
@media(max-width:1180px){.sn{float:none;width:auto;margin:.8rem 0;padding-left:1rem;border-left:2px solid var(--border)}}
/* explorable shell + controls */
.explor{margin:3rem 0;padding:1.25rem;border:1px solid var(--border);border-radius:12px;background:var(--surface)}
.controls{display:flex;flex-wrap:wrap;gap:.8rem 1.2rem;align-items:center;margin-top:1rem;font:.875rem var(--body)}
.controls label{display:flex;align-items:center;gap:.5rem;color:var(--muted)}
input[type=range]{accent-color:var(--accent)}
.readout{font:600 .875rem var(--mono);color:var(--fg-strong)}
button.ui{font:600 .82rem var(--mono);background:var(--surface-2);color:var(--fg);border:1px solid var(--border-2);
 border-radius:7px;padding:.45rem .8rem;cursor:pointer}button.ui:hover{border-color:var(--accent);color:var(--accent-text)}
/* details */
details{margin-top:1.4rem;border:1px solid var(--border);border-radius:10px;background:var(--surface-2);padding:0 1rem}
summary{cursor:pointer;font-weight:600;padding:.85rem 0}details[open] summary{margin-bottom:.6rem}
/* reduced motion: kill all animation/transition */
@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation-duration:.001ms!important;transition-duration:.001ms!important}}
</style></head><body>
<article class=post>
  <p class=eyebrow>Type · context</p>
  <h1>The Title</h1>
  <p class=lead>An italic one-line summary that sets up what this delivers.</p>
  <p class=dateline>plan · written for X</p>

  <p>Opening paragraph. Get to the point — no throat-clearing.</p>

  <h2>A section</h2>
  <p>…</p>

  <!-- a figure / explorable goes here; use class="bleed" to break the column -->

</article>
<script>
/* copy buttons */
document.querySelectorAll('figure.code .copy').forEach(b=>b.addEventListener('click',()=>{
  const t=b.closest('figure.code').querySelector('code').innerText;
  const flash=m=>{const o=b.textContent;b.textContent=m;setTimeout(()=>b.textContent=o,1200)};
  if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(t).then(()=>flash('Copied ✓')).catch(()=>flash('Press ⌘C'))}
  else{flash('Press ⌘C')}
}));
</script>
</body></html>
```

### Component quick-reference

- **Callout:** `<div class="callout"><div class="label">Note</div><p>…</p></div>` — add `warn` for the red variant. Use a bare `<blockquote>` for a punchy thesis line (no box).
- **Code with chrome:** `<figure class="code"><div class="code-bar">server.py<button class="copy">copy</button></div><pre><code>…</code></pre></figure>`. Hand-tag syntax with `<span class="k/s/n/c/f">` only if it helps; an untagged block still looks right. Add `bleed` for wide code.
- **Figure:** `<figure class="bleed"><svg style="width:100%;height:auto">…</svg><figcaption>What it shows.</figcaption></figure>`. Style the SVG via an inner `<style>` or `style=` — never `fill=`/`stroke=` attributes (`var()` won't resolve there). See "Styling SVG" below.
- **Sidenote:** `<span class="sn">A margin aside.</span>` right after the word it annotates.
- **Table:** wrap in `<div class="tw"><table>…</table></div>`.

---

## Make it move — the explorable playbook

The medium justifying itself — *when it earns it*. **Most posts need zero or one visual.** Reach for one only when it conveys something prose can't: timing, flow, a tradeoff curve, a structure. Never add a visual to decorate or to look rich — if you can't name what it teaches, cut it. A plan or a review usually wants exactly one thing (a dependency flow; the diff), not a gallery; only a genuine tutorial earns several, and even then each must pull its weight.

> **Styling SVG (critical).** `var()` does NOT resolve inside SVG *presentation attributes* — `fill="var(--x)"`, `stroke="…"`, `font-family="…"` silently fall back to black / default serif (this is the #1 way htmlize diagrams break). Style SVG only through CSS: a `<style>` block *inside* the `<svg>` (the page's custom properties cascade in), or `style="fill:var(--x)"` on elements. And give every diagram `<svg>` an explicit `style="width:100%;height:auto"` — a bare `viewBox` with no width renders tiny and off-center.

**Philosophy**
- **Show the thing moving.** If the lesson is timing, throughput, backpressure, emergence, or "small change → big change," static can't carry it — animate the *mechanism*, not decoration. If you can't name the variable a motion represents, cut it.
- **One strong visual beats five paragraphs — but prose beats a weak visual.** Interactives for processes/systems; animation for change-over-time; tables for relationships; **plain text for definitions and caveats.**
- **Let the reader drive.** The highest-leverage interaction is one `<input>` bound to a live variable the loop already reads. Always pair a sim with a live readout (cause + effect together) and a Reset.
- **Reduced-motion + dark are non-negotiable.** Author still-by-default, add motion in the no-preference branch; drive every viz color from the `--d-*` tokens.

**Structural backbone** (every widget)
1. **Single source of truth** — all state in one object; one idempotent `render()` reads it and rewrites the view.
2. **One master rAF loop:** `loop(now){if(playing)update(min(now-last,50));last=now;draw();raf=requestAnimationFrame(loop)}`. Never one rAF per entity; clamp `dt`.
3. **Model ≠ render** — a plain object/array is truth; `draw()` is a pure function of it. Makes pause/step/scrub/reset trivial.
4. **Snapshot pattern** — store full state per step in `states[]`; forward/back = `render(states[i±1])`, zero per-frame cost.
5. **Sliders mutate a live var** the loop reads — never restart the sim on a tick.
6. **Color encodes meaning** — hue for wait/staleness (`hsl(120 - age/max*120,70%,55%)`), lightness ramp for intensity, `--d-green`/`--d-red` for changed/unchanged.
7. **Canvas vs DOM** — canvas + `devicePixelRatio` for hundreds of dots / thousands of cells; CSS-grid `<div>`s for ≤ a few hundred where you want hover/click.
8. **Perf** — gate animated canvases on `IntersectionObserver` (pause off-screen); DPR-scale once.

**Technique catalog** (use-when → recipe)

- **A1 Self-drawing SVG flow** *(architecture, pipelines, handshakes)* — `<path>` no fill; `dasharray=dashoffset=getTotalLength()`, animate offset→0; chain with `animation-delay`; start on IntersectionObserver.
- **A2 Annotated diagram** *(dense diagram / jargon)* — `<span class=term data-note>`; one reused tooltip div positioned via `getBoundingClientRect`; `tabindex=0`, Esc to dismiss.
- **A3 Grid-of-cells state map** *(memory, buckets, collisions, heatmaps)* — CSS-grid divs (small) or canvas `fillRect` (large); color = state/intensity.
- **B1 CSS keyframes + staggered reveal** — animate only `transform`/`opacity`; stagger via `--i`.
- **B3 Animated counter** *(headline metric)* — rAF + easeOutCubic; set final value immediately under reduced-motion.
- **C1 Tweakable parameter (what-if slider)** *(any tunable system/formula)* — the core move; see P1.
- **C2 Draggable inline number (Tangle)** *(budgets/estimates in prose)* — `ew-resize` span; mousedown→delta→clamp→`update()` rewrites every output.
- **C4 Bit-flip / avalanche diff** *(small→big change)* — two cell rows; click flips; diff output bits → green/grey; show "% changed."
- **D1–D5 Mock UI** — window chrome (traffic-light dots), fake terminal (`$ ` prefix, blinking cursor), faux code editor (gutter via CSS counters, hand-tagged syntax, `.hl` focus line), browser chrome (URL pill + 🔒), request/response + chat bubbles. Frame real content as a real surface; see P3.
- **E1 Play/pause/step/reset transport** *(algorithm walkthroughs)* — boolean `playing`; Step calls `stepOnce(dt)` once then `draw()`; always a Reset.
- **E2 Timeline scrubber** *(deterministic traces)* — precompute `states[]`; `range` input → `render(states[i])`; buttery, no sim cost.
- **E3 Sticky-graphic scrollytelling** *(phased process)* — `position:sticky` graphic + 100vh `.step` blocks; IntersectionObserver (`rootMargin:-50% 0`) mutates the ONE persistent visual.
- **F1 Entity-flow simulation** *(distributed systems, queues, networking)* — canvas; spawn on accumulator, lerp requests to servers, queue+process, color-encode wait, drop on overflow; see structural backbone.
- **F3 Probability bars over many trials** *(sampling, fairness, Monte Carlo)* — `counts[]`; "run N" loops; bars = divs with `height` transition; plot theoretical beside empirical.
- **F4 Live readout chart** *(latency/SLO/dropped over time)* — rolling array, draw on a small canvas in the SAME rAF frame as the sim; dashed threshold line.
- **G1 Side-by-side panels, one shared input** *(algorithm comparisons)* — `makeSim(canvas,algo)` ×N; one event source + shared seeded RNG feeds all; differences are unambiguously the algorithm's.
- **G2 Before/after toggle / clip-path wipe** *(ablation, naive-vs-optimized)* — see P4.

**Which technique for which reply-type**

| Reply type | Reach for |
|---|---|
| Implementation plan | E3 sticky-scrolly (phases) · A1 flow (dependencies) |
| Code review | D3 faux editor + diff/line-highlight · A2 annotated · G2 before/after |
| Architecture / system design | A1 flow · F1 entity-sim + F4 live chart · C1 capacity slider |
| Algorithm explainer | E2 scrubber · E1 step transport · A3 cell map |
| Comparison | G1 shared-input panels · G2 toggle · C1 playground |
| Debugging walkthrough | D2 terminal · E1 step · A2 annotated |
| Research summary | B3 stat counters · A2 annotated terms · C1 what-if |
| Runbook | D2 terminal · D5 request/response · A1 ordered flow |

### Mini patterns (copy-and-adapt)

**P1 — Tweakable-parameter live sim** (slider mutates the var the loop reads)
```html
<div class=explor>
 <canvas id=c height=120 style="width:100%"></canvas>
 <div class=controls><label>Arrival rate <input id=rate type=range min=1 max=60 value=10></label><span class=readout id=v>10/s</span>
  <button class="ui" id=play>Pause</button><button class="ui" id=reset>Reset</button></div>
</div>
<script>
const cv=c,ctx=cv.getContext('2d'),dpr=devicePixelRatio||1;
const reduce=matchMedia('(prefers-reduced-motion:reduce)').matches;
const sim={spawnMs:100,acc:0,dots:[],playing:!reduce,onscreen:true};
function draw(){ctx.clearRect(0,0,cv.clientWidth,120);ctx.fillStyle=getComputedStyle(document.body).getPropertyValue('--d-sky').trim();
 for(const d of sim.dots){ctx.beginPath();ctx.arc(d.x,60,4,0,7);ctx.fill()}}
function fit(){cv.width=cv.clientWidth*dpr;cv.height=120*dpr;ctx.setTransform(dpr,0,0,dpr,0,0);draw()}   // redraw on resize, so the static frame survives
function reset(){sim.dots=reduce?[{x:90},{x:250},{x:410}]:[];sim.acc=0;draw()}
let last=0,running=false;
function frame(now){const dt=Math.min(now-(last||now),50);last=now;
 sim.acc+=dt;while(sim.acc>sim.spawnMs){sim.dots.push({x:0});sim.acc-=sim.spawnMs}
 for(const d of sim.dots)d.x+=.12*dt;sim.dots=sim.dots.filter(d=>d.x<cv.clientWidth);draw();
 if(sim.playing&&sim.onscreen)requestAnimationFrame(frame);else running=false}
function kick(){if(sim.playing&&sim.onscreen&&!running){running=true;last=0;requestAnimationFrame(frame)}}
rate.oninput=e=>{v.textContent=e.target.value+'/s';sim.spawnMs=1000/+e.target.value};
play.onclick=()=>{sim.playing=!sim.playing;play.textContent=sim.playing?'Pause':'Play';kick()};
reset.onclick=reset;
addEventListener('resize',fit);
new IntersectionObserver(es=>{sim.onscreen=es[0].isIntersecting;kick()},{threshold:0}).observe(cv);   // pause off-screen
fit();reset();if(reduce)play.textContent='Play';kick();
</script>
```

**P3 — Mock terminal frame**
```html
<figure class=explor style="padding:0;border:none">
 <div style="border-radius:10px;overflow:hidden;box-shadow:var(--shadow);font:13px/1.6 var(--mono)">
  <div style="display:flex;gap:8px;align-items:center;padding:10px 14px;background:#2c2f36">
   <span style="width:12px;height:12px;border-radius:50%;background:#ff5f56"></span>
   <span style="width:12px;height:12px;border-radius:50%;background:#ffbd2e"></span>
   <span style="width:12px;height:12px;border-radius:50%;background:#27c93f"></span>
   <span style="flex:1;text-align:center;color:#999;margin-left:-54px">zsh — build</span></div>
  <pre style="margin:0;padding:16px;background:#15171c;color:#ddd;white-space:pre-wrap"><span style="color:#27c93f">$ </span>npm run build
<span style="color:#9aa">vite building for production…</span>
<span style="color:#27c93f">✓ built in 1.24s</span></pre></div>
</figure>
```

**P4 — Before/after clip-path slider**
```html
<figure class=explor style="padding:0;border:none">
 <div style="position:relative;height:120px;border-radius:10px;overflow:hidden;font:600 16px var(--body)">
  <div style="position:absolute;inset:0;display:grid;place-items:center;background:var(--d-green);color:#04130d">AFTER · optimized</div>
  <div id=bef style="position:absolute;inset:0;display:grid;place-items:center;background:var(--d-red);color:#1b0a04;clip-path:inset(0 50% 0 0)">BEFORE · naive</div>
  <input id=h type=range min=0 max=100 value=50 aria-label=reveal style="position:absolute;bottom:8px;left:8px;right:8px;width:calc(100% - 16px);accent-color:var(--accent)">
 </div>
</figure>
<script>h.oninput=e=>bef.style.clipPath=`inset(0 ${100-e.target.value}% 0 0)`;</script>
```

---

## Signature moves

The details that make it instantly read as high-taste:
1. **Serif display (weight 400) over humanist-sans body, from system stacks** — the single biggest tell apart from generic AI output.
2. **One ink accent + one warning red, disciplined** — links, focus rings, the `→`/`←` motif, bullets. The `--d-*` palette is quarantined to viz.
3. **Code as a physical slab** — dark in both themes, soft shadow, no hard border, filename chrome, hover-reveal copy.
4. **Margin sidenotes** that float into the gutter on wide screens.
5. **A live explorable when the topic genuinely earns it** — as the centerpiece, never as filler.

## Anti-patterns

- **No Inter/Geist/Roboto + indigo-gradient hero.** That combo *is* the AI-generic look. Serif/humanist-sans system pairing only.
- **No bold-sans headlines, no centered long body text, no full-width prose sprawl.** Left-aligned ~68ch; only figures/explorables `bleed`.
- **No ASCII/box-drawing diagrams** — SVG (A1/A3); it's not more code and it actually reflows.
- **No `var()` in SVG presentation attributes** (`fill=`/`stroke=`/`font-family=`) — it renders black/default. Style SVG via `<style>`/`style=`, and give diagram SVGs `style="width:100%;height:auto"`.
- **No visual-for-the-sake-of-it.** One purposeful visual beats three decorative ones; a review needs the diff, not a gallery. No fake mock-UI panels that illustrate nothing. When in doubt, prose.
- **No charting libraries or CDNs** — hand-roll canvas/SVG; the file must work offline.
- **No decorative/unpausable motion** — if you can't name the variable it encodes, cut it; every loop >5s needs Step/Pause/Reset; default sims to manual Step under reduced-motion.
- **No content trapped at `opacity:0`** — apply hidden state only via JS; reveal immediately under reduced-motion / no-JS.
- **No color-only encoding** — pair hue with shape/label/position; meet contrast in both themes.
- **No multiple accents, neon syntax, grey rounded-pill inline code, emoji in headings, or throat-clearing copy.**
