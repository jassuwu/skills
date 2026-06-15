# HTML Artifact Format

One self-contained `.html` file per reply. The bar is simple: **the reader understands this faster than they would the same thing as terminal text.** If a post doesn't beat plain text, it failed. Aim for samwho.dev (calm, plain, a visual exactly where it helps) — not a styled magazine.

## Required `<head>` metadata

The reading list is built from these — always set all three.

```html
<meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>A plain, specific title</title>
<meta name=description content="One sentence on what this delivers.">
<meta name=htmlize-type content="plan">   <!-- plan|review|spec|explainer|comparison|research|runbook|design|note -->
```

Optional, to thread posts into a conversation trail — the server renders prev/next + the connection from these:

```html
<meta name=htmlize-conversation content="Auth rework">   <!-- the thread this belongs to -->
<meta name=htmlize-link content="a stored token raised a revocation question, so next: rotation">
```

`htmlize-link` is the **inbound** phrase — *why the work moved here* from the previous post. Omit it on the first post and whenever there's no honest hop; a forced "next we…" is filler, same bar as a decorative visual.

## Principles

1. **Understanding first.** Every element earns its place by making the idea clearer. If deleting it loses no understanding, delete it.
2. **Open with the problem in plain words** — sentence one states the situation. No slogans, hooks, or throat-clearing.
3. **Plain copy.** Short sentences, 1–3 sentence paragraphs, calm. Cut anything that only *sounds* smart.
4. **Headings are a table of contents** — descriptive ("When round-robin isn't enough"), never clever/cryptic ("The shape of it").
5. **Name the concept before you show it.** Prose/code defines the mechanism; a visual confirms it — it never teases.
6. **A visual must teach one mechanism words can't make obvious** (motion, flow, spatial position, a tradeoff curve). Most posts have zero or one. Never decorative, never stacked. If you can't name the variable it encodes, cut it.
7. **Contrast & accessibility are non-negotiable.** Verified contrast in both themes; reduced-motion ships the still state; keyboard-reachable controls; never color alone.
8. **One self-contained file** — everything inlined except a short allow-list of pinned + SRI'd CDN libs (below).

## The scaffold

Clean system-sans, neutral surfaces, real contrast — shadcn's restraint, samwho's readability. Copy and fill in.

```html
<!doctype html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>…</title><meta name=description content="…"><meta name=htmlize-type content="plan">
<style>
:root{
 --bg:#fff;--surface:#f7f7f8;--surface-2:#f0f0f2;--fg:#0a0a0b;--fg-strong:#000;
 --muted:#52525b;--border:#e4e4e7;--border-2:#d4d4d8;          /* --muted ~8:1 on --bg */
 --accent:#4338ca;--accent-text:#3730a3;--accent-weak:#eef0fb;--accent-border:#c7c9f2;
 --warn:#b42318;--warn-weak:#fdecea;--ok:#067647;
 --code-bg:#0b0d12;--code-fg:#e4e6eb;--code-bar:#080a0e;--code-line:#21242c;
 /* data palette — VISUALS ONLY, never chrome. Darkened for stroke contrast on light. */
 --d-blue:#0a5a8c;--d-green:#0a7a59;--d-orange:#a6690a;--d-red:#b8420c;--d-sky:#2a78ad;--d-pink:#974d7e;--d-slate:#475060;
 --sans:-apple-system,BlinkMacSystemFont,"Segoe UI",system-ui,Roboto,"Helvetica Neue",Arial,sans-serif;
 --mono:ui-monospace,"SF Mono","Cascadia Code",Menlo,Consolas,monospace;
 --measure:68ch;--shell:60rem;--pad:1.25rem;--radius:.5rem;
 --shadow:0 1px 2px rgba(9,9,11,.05),0 4px 16px rgba(9,9,11,.06);--ring:0 0 0 2px var(--bg),0 0 0 4px var(--accent);
}
@media(prefers-color-scheme:dark){:root{
 --bg:#09090b;--surface:#131316;--surface-2:#1b1b1f;--fg:#f4f4f5;--fg-strong:#fff;
 --muted:#a1a1aa;--border:#27272a;--border-2:#3f3f46;          /* --muted ~7:1 on --bg */
 --accent:#a5b4fc;--accent-text:#bcc6fd;--accent-weak:#1a1c2e;--accent-border:#383b63;
 --warn:#fca5a5;--warn-weak:#2a1414;--ok:#6ee7b7;
 --code-bg:#08090c;--code-fg:#e8e9ee;--code-bar:#050608;--code-line:#1c1f27;
 --d-blue:#5aa6d8;--d-green:#3fbf95;--d-orange:#e8a73b;--d-red:#ec7a4e;--d-sky:#7cc3ec;--d-pink:#cf94b4;--d-slate:#9aa3b5;
 --shadow:0 1px 2px rgba(0,0,0,.5),0 6px 24px rgba(0,0,0,.55);
}}
*{box-sizing:border-box}html{font-size:16px;-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--fg);font:1.0625rem/1.7 var(--sans);overflow-x:clip;
 -webkit-font-smoothing:antialiased;padding:4rem var(--pad) 6rem}
.post{max-width:var(--measure);margin-inline:auto}
.bleed{width:min(var(--shell),calc(100vw - 2*var(--pad)));margin-left:50%;transform:translateX(-50%)}
h1{font:650 clamp(2rem,5vw,2.75rem)/1.1 var(--sans);letter-spacing:-.02em;color:var(--fg-strong);margin:0 0 .5rem}
.lead{font-size:1.2rem;color:var(--muted);margin:0 0 1rem}
.dateline{font:.8125rem/1.4 var(--mono);color:var(--muted);border-top:1px solid var(--border);padding-top:.8rem;margin:0 0 2.5rem}
h2{font:600 clamp(1.4rem,3.5vw,1.75rem)/1.2 var(--sans);letter-spacing:-.01em;color:var(--fg-strong);margin:3.5rem 0 1rem}
h3{font:600 1.2rem/1.25 var(--sans);color:var(--fg-strong);margin:2rem 0 .6rem}
p{margin:0}p+p,ul,ol,figure,.callout,.tw{margin-top:1.4rem}
strong{color:var(--fg-strong);font-weight:650}a{color:var(--accent-text);text-decoration:underline;text-underline-offset:2px}
ul,ol{padding-left:1.3rem}li{margin:.4rem 0}
:focus-visible{outline:none;box-shadow:var(--ring);border-radius:var(--radius)}
code{font:600 .9em var(--mono);color:var(--fg-strong)}
figure{margin:2rem 0}figure svg,figure canvas{display:block;width:100%;height:auto}
figcaption{font-size:.9375rem;color:var(--muted);text-align:center;margin-top:.7rem}
figure.code{margin:1.5rem 0;border-radius:var(--radius);box-shadow:var(--shadow);overflow:hidden}
.code-bar{display:flex;gap:.6rem;background:var(--code-bar);color:var(--muted);font:.8125rem/1 var(--mono);padding:.7rem .9rem}
figure.code pre{margin:0;background:var(--code-bg);color:var(--code-fg);padding:1rem;overflow:auto;font:.875rem/1.6 var(--mono)}
pre code{font:inherit;color:inherit}.c{color:#8a93a1}.k{color:#c39ac9}.s{color:#9ccb8f}.n{color:#e0a87e}
.callout{padding:1rem 1.25rem;border-radius:var(--radius);border:1px solid var(--border);border-left:3px solid var(--accent);background:var(--surface)}
.callout.warn{border-left-color:var(--warn);background:var(--warn-weak)}
.callout .label{font:.75rem/1 var(--sans);text-transform:uppercase;letter-spacing:.08em;color:var(--accent-text);margin-bottom:.4rem}
.callout.warn .label{color:var(--warn)}
.tw{border:1px solid var(--border);border-radius:var(--radius);overflow:hidden}
table{border-collapse:collapse;width:100%;font-size:.9375rem}
thead th{background:var(--surface-2);text-align:left;font:.75rem/1.4 var(--mono);text-transform:uppercase;color:var(--muted);padding:.7rem .9rem}
td{padding:.6rem .9rem;border-top:1px solid var(--border)}
.controls{display:flex;flex-wrap:wrap;gap:.7rem;align-items:center;margin-top:1rem;font-size:.9rem;color:var(--muted)}
.btn{font:600 .82rem var(--sans);background:var(--surface);color:var(--fg);border:1px solid var(--border-2);border-radius:var(--radius);padding:.45rem .8rem;cursor:pointer}
.btn:hover{border-color:var(--accent)}input[type=range]{accent-color:var(--accent)}.readout{font:600 .875rem var(--mono);color:var(--fg-strong)}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation-duration:.001ms!important;transition-duration:.001ms!important}}
</style></head><body>
<article class=post>
 <h1>The title</h1>
 <p class=lead>One sentence on what this delivers.</p>
 <p class=dateline>plan · context</p>
 <p>Open with the problem, plainly.</p>
 <h2>A descriptive section heading</h2>
 <p>…</p>
</article>
</body></html>
```

Components: **callout** `<div class="callout"><div class="label">Note</div><p>…</p></div>` (add `warn`); **code** `<figure class="code"><div class="code-bar">file.ts</div><pre><code>…</code></pre></figure>`; **table** wrap in `<div class="tw"><table>…</table></div>`. The server injects the back-link + live-reload — don't add nav chrome.

## Visualize, or write prose?

**Visualize** when the lesson is motion, flow, spatial position, a tradeoff curve, or "small change → big change." **Write prose** (or a table/callout) for definitions, rules, lookups, and branches you don't take. Test each candidate: *does it help understanding, or advertise cleverness?* Name the variable it encodes, or cut it.

The techniques worth keeping:

- **Animated entity-flow narrative** — the flagship (worked example below). One persistent SVG the reader steps/scrubs; a token travels edges; balances/state update in the same frames; one plain sentence per step. Money flow, request flow, state machines.
- **Tweakable parameter** — one `<input>` bound to a live variable the loop reads, with a live readout + Reset; the reader runs the experiment.
- **Annotated diagram** — hand-placed SVG nodes/edges with hover/`<details>` for detail-on-demand.
- **Before/after toggle** — same layout, one variable changes; the eye does the diffing.
- **Faux code editor / diff** — gutter + hand-tagged syntax + a highlighted line, for reviews.
- **Small multiples / bars** — a distribution or comparison from real numbers (hand-built `<div>`/canvas bars).

### Styling SVG (read this — the #1 break)

`var()` does **not** resolve in SVG *presentation attributes* (`fill="var(--x)"`, `stroke=`, `font-family=`) — they fall back to black/default. Style SVG only through CSS: a `<style>` block **inside** the `<svg>` (page custom properties cascade in), or `style="fill:var(--x)"` on elements. Give every diagram `<svg>` an explicit `style="width:100%;height:auto"` — a bare `viewBox` renders tiny and off-center.

### Worked example — animated entity-flow (vanilla, no library)

```html
<figure class="bleed">
 <svg id=flow viewBox="0 0 720 140" style="width:100%;height:auto" role=img aria-label="a $50 balance moves and the spendable total updates">
  <style>
   #flow text{font:600 13px var(--sans);fill:var(--fg)}#flow .lbl{font:600 12px var(--mono);fill:var(--muted)}
   #flow .node{fill:var(--surface);stroke:var(--border-2);stroke-width:1.5}#flow .edge{fill:none;stroke:var(--border-2);stroke-width:2}
   #flow .tok{fill:var(--d-green)}
  </style>
  <path class=edge id=e0 d="M150,55 H290"/><path class=edge id=e1 d="M430,55 H570"/>
  <g><rect class=node x=30 y=33 width=120 height=44 rx=8/><text x=90 y=60 text-anchor=middle>User</text></g>
  <g><rect class=node x=290 y=33 width=140 height=44 rx=8/><text x=360 y=60 text-anchor=middle>Provider</text></g>
  <g><rect class=node x=570 y=33 width=120 height=44 rx=8/><text x=630 y=60 text-anchor=middle>Ledger</text></g>
  <circle class=tok id=tok cx=150 cy=55 r=7/>
  <text class=lbl id=bal x=90 y=110 text-anchor=middle>spendable $50.00</text>
 </svg>
 <div class=controls><button class=btn id=step>Step ▸</button><button class=btn id=reset>Reset</button><span class=readout id=say></span></div>
</figure>
<script>
(function(){
 var reduce=matchMedia('(prefers-reduced-motion:reduce)').matches, tok=document.getElementById('tok'), bal=document.getElementById('bal');
 var steps=[
  {say:'A $50 balance sits with the user.', bal:'spendable $50.00'},
  {edge:'e0', say:'The provider authorizes a $10 charge.', bal:'spendable $40.00'},
  {edge:'e1', say:'Settlement records it on the ledger.', bal:'spendable $40.00'}];
 var i=0;
 function render(){ document.getElementById('say').textContent='Step '+i+' — '+steps[i].say; bal.textContent=steps[i].bal; }
 function go(n){ var s=steps[n]; if(!s.edge||reduce){ if(s.edge){var p=document.getElementById(s.edge),e=p.getPointAtLength(p.getTotalLength());tok.setAttribute('cx',e.x);tok.setAttribute('cy',e.y);} i=n; render(); return; }
  var pa=document.getElementById(s.edge), L=pa.getTotalLength(), t0=0;
  function fr(now){ if(!t0)t0=now; var k=Math.min((now-t0)/650,1), pt=pa.getPointAtLength(L*k); tok.setAttribute('cx',pt.x); tok.setAttribute('cy',pt.y); if(k<1)requestAnimationFrame(fr); else {i=n; render();} }
  requestAnimationFrame(fr); }
 document.getElementById('step').onclick=function(){ if(i<steps.length-1) go(i+1); };
 document.getElementById('reset').onclick=function(){ i=0; tok.setAttribute('cx',150); tok.setAttribute('cy',55); render(); };
 render();
})();
</script>
```

That's the pattern: position = where the money is, the label = the state it changes, one sentence per hop, reduced-motion jumps to the end state. For richer choreography (timelines, path-draw, morph) use **anime.js** from the allow-list; for most flows, vanilla rAF like this is plenty.

## CDN allow-list

Default is still **hand-built SVG + vanilla JS** — most posts need no library. Reach for one only when you genuinely can't hand-roll it cleanly.

| Need | Pick | Use when |
|---|---|---|
| Choreographed SVG / entity-flow | **anime.js 4.4.1** (40 kB) | timelines, path-draw, morph, motion-path |
| 1–3 trivial fades/slides | **native WAAPI** (0 kB) | `el.animate([...],{...})`, no tag |
| shadcn components as plain classes | **Basecoat CSS 0.3.11** (13 kB) | want buttons/cards/inputs/badges without a build |
| shadcn look, a few elements | **the token block above** (0 kB) | most posts — it *is* the look |
| Auto-laid dense graph | **Mermaid 11.x** (heavy) | only when you truly can't hand-place nodes |
| Data-bound charts | **D3 7.x** | only for a real dataset (scales/axes/force) |

```html
<script src="https://cdn.jsdelivr.net/npm/animejs@4.4.1/dist/bundles/anime.umd.min.js"
  integrity="sha384-E0YGGlCF/SWRxorVhUbv4MCJ/jFWk1EwDTrTpNvxLFBJ++VCvIo4iHrVOsJ8dEoW" crossorigin="anonymous"></script>
<link rel=stylesheet href="https://cdn.jsdelivr.net/npm/basecoat-css@0.3.11/dist/basecoat.cdn.min.css"
  integrity="sha384-3bN4bCwXgp6P9s9cIM3i9Zl2378Fmumumov4whqgzPqYHuNx0fKoEqqd322RU40c" crossorigin="anonymous">
```

**Supply-chain rules — every external resource:**
1. **Pin the exact version** (`animejs@4.4.1`) — never `@latest`, `@4`, ranges, or branch tags.
2. **Reputable CDN only:** `cdn.jsdelivr.net`, `unpkg.com`, `cdnjs.cloudflare.com`. Never `http://`, never another host.
3. **`integrity="sha384-…" crossorigin="anonymous"` on every `<script>`/`<link>`.** Get the hash from jsdelivr's "Copy SRI", or `curl -s -H "Accept-Encoding: identity" <URL> | openssl dgst -sha384 -binary | openssl base64 -A`. Recompute on every version bump — a stale hash means the tag silently fails, so re-verify before shipping.
4. **Prefer UMD + SRI** over ESM-from-CDN (browsers can't enforce `integrity` on bare `import`s).
5. **Never `eval`/`new Function`/`innerHTML` on fetched text** — SRI can't cover that.

## Anti-patterns

- **No cryptic/editorial headings or slogan hooks.** Headings name the topic; sentence one states the problem.
- **No serif-display "magazine" styling, no dark dramatic hero, no Inter/Geist + indigo-gradient.** Clean system-sans, light default, calm column.
- **No decorative or stacked visuals; no "Loading demo…" placeholders.** One visual per idea, only if it teaches.
- **No `var()` in SVG presentation attributes; no bare-viewBox SVG.** Style via `<style>`/`style=`, set `width:100%`.
- **No low-contrast text, no color-only encoding, no unpausable motion.** Verify both themes; reduced-motion ships the still state.
- **No floating/unpinned CDN URLs, no untrusted hosts, no missing SRI.**
- **A trivial reply stays in the terminal** — don't wrap one sentence in a web page.
