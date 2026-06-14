# htmlize

A single Claude Code skill. Type `/htmlize` and substantial replies — plans, reviews, specs,
explainers — render as polished, self-contained HTML in a live browser tab instead of walls of
terminal Markdown. The view updates in place as new replies land — no refresh tick, no new tabs.

Needs **`python3`** (stdlib only) and a browser. The server binds to `127.0.0.1`.

## Structure

```
skills/htmlize/
├── SKILL.md          # the skill: when on, behaviour, the on/off toggle
├── ARTIFACT.md       # how each HTML artifact should look + read
└── scripts/
    └── serve.py      # the live-reload server (stdlib, binds 127.0.0.1)
```

## Install

Via [skills.sh](https://skills.sh):

```bash
bunx --bun skills add jassuwu/skills -s htmlize
```

## Use

- `/htmlize on` — start the server and open the live view tab
- `/htmlize off` — stop the server, back to normal terminal replies
- `/htmlize` — toggle

Artifacts land in `.claude-html/NNNN-slug.html` (static, self-contained files the server lists by
their `<title>`). The server live-reloads the open tab over SSE whenever one is added or edited, so
a new reply appears with no click and no flicker. Worth `.gitignore`-ing `.claude-html/`.
