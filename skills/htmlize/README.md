# htmlize

A single skill. Type `/htmlize` and substantial replies — plans, reviews, specs,
explainers — stop being walls of terminal Markdown and become a **personal blog that writes
itself as you work**: a calm reading list of posts, each a typeset, self-contained page that
reaches for the right diagram, animation, or live explorable to make the idea click.

Needs **`python3`** (stdlib only) and a browser. The server binds to `127.0.0.1`.

## Structure

```
skills/htmlize/
├── SKILL.md          # when it's on, the behaviour, the on/off toggle
├── ARTIFACT.md       # the design system + explorable playbook every post is built from
└── scripts/
    └── serve.py      # the reading-list server (stdlib, binds 127.0.0.1)
```

## Install

Via [skills.sh](https://skills.sh):

```bash
bunx --bun skills add jassuwu/skills -s htmlize
```

## Use

- `/htmlize on` — start the server and open the reading list
- `/htmlize off` — stop the server, back to normal terminal replies
- `/htmlize` — toggle

Substantial replies land as posts in `.htmlize/NNNN-slug.html`. The **reading list** (the
index) is yours to manage: drag to reorder, pin to the top, soft-delete to a recoverable Trash,
and filter — all of which persist to `.htmlize/.state.json`. The server live-reloads the
open tab over SSE as posts are added or edited (no flicker, no new tabs) and injects a "← reading
list" link into each post. Worth `.gitignore`-ing `.htmlize/`.

Each post is a self-contained file — email it and it just opens, offline. The look (clean
system-sans, neutral surfaces, real contrast, dark mode) and the visual craft (animated SVG flows,
tweakable widgets, before/after — vanilla, plus a small pinned-and-SRI'd CDN allow-list for
animation and the shadcn aesthetic) live in [ARTIFACT.md](ARTIFACT.md).
```

