# HTML Artifact Format

Each artifact is one self-contained `.html` file: inline CSS, no external requests, a real `<title>` (the index uses it as the label). It must read well and be trivial to share — the user can send the file and it just opens, offline. Static, so any interactive widgets keep their state.

## Scaffold

```html
<!doctype html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1"><title>…</title><style>
:root{--fg:#1b1b1a;--bg:#fbfbfa;--mut:#6b6b68;--ln:#e7e7e3;--ac:#4f46e5;--cb:#0f1117}
@media(prefers-color-scheme:dark){:root{--fg:#e9eaec;--bg:#0e0f12;--mut:#9aa0a8;--ln:#262a31;--ac:#a5b4fc;--cb:#0a0c11}}
body{background:var(--bg);color:var(--fg);font:16px/1.65 -apple-system,system-ui,sans-serif;max-width:840px;margin:0 auto;padding:44px 20px}
h2{margin-top:2em;padding-top:.4em;border-top:1px solid var(--ln)}a{color:var(--ac)}
code{background:color-mix(in srgb,var(--ac) 14%,transparent);padding:.1em .4em;border-radius:6px;font:.9em ui-monospace,monospace}
pre{background:var(--cb);color:#e7e9ee;padding:16px;border-radius:12px;overflow:auto;font:.86rem/1.55 ui-monospace,monospace}pre code{background:none;padding:0}
table{border-collapse:collapse;width:100%}th,td{border:1px solid var(--ln);padding:8px 11px;text-align:left}
.card{border:1px solid var(--ln);border-radius:12px;padding:18px}.grid{display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(240px,1fr))}
details{border:1px solid var(--ln);border-radius:10px;padding:0 14px}summary{cursor:pointer;padding:12px 0;font-weight:600}
</style></head><body>
<!-- content -->
</body></html>
```

## Convey with the medium

The format earns its place by carrying what Markdown can't. Use it.

- **Diagrams in SVG, never ASCII** — flows, state machines, architecture, sequences. For graph-shaped dependency or call diagrams, Mermaid from a CDN is acceptable (it then needs network); mix hand-built SVG for editorial visuals so it doesn't read as generic.
- **Tables** for tabular data. **`<details>`** to fold long code or secondary detail. Tabs when comparing variants.
- **Code review** — render the diff with inline margin annotations; colour-code findings by severity.
- **Exploration** — lay 3–6 options in `.grid`, each labelled with the tradeoff it makes.
- **Tuning (animation, colour, params)** — build a throwaway editor: live preview plus sliders or knobs, and always a "copy as prompt / JSON" button that turns the user's tweaks back into something they can paste back. These live widgets are why artifacts are static rather than auto-refreshing.

## Style

Lean editorial, not corporate dashboard. Generous whitespace. One accent colour, plus red for warnings. If a section needs a paragraph to be understood, restructure it — prefer a diagram, a table, or bullets. No throat-clearing, no "it's worth noting". Keep each artifact focused; several small files beat one giant document.
