# htmlize

A single Claude Code skill. Type `/htmlize` and substantial replies — plans, reviews, specs,
explainers — render as polished, self-contained HTML in a live browser tab instead of walls of
terminal Markdown. New replies appear on their own.

Needs only a **POSIX shell and a browser** — no Python, no Node, no install. (Python isn't a
safe default: macOS dropped the bundled runtime in 12.3, Windows ships none, and Claude Code's
native binary means Node isn't guaranteed either.)

## Structure

```
skills/htmlize/
├── SKILL.md          # the skill: when on, behaviour, the toggle (≈40 lines)
├── ARTIFACT.md       # how each HTML artifact should look + read
└── scripts/
    ├── mkindex.sh    # 10-line POSIX-sh index generator (deterministic, bundled)
    └── serve.py      # optional live-reload server for a zero-click variant
```

## Install

```bash
mkdir -p ~/.claude/skills && cp -r skills/htmlize ~/.claude/skills/   # all projects
# or this project only:
mkdir -p .claude/skills && cp -r skills/htmlize .claude/skills/
```

## Use

- `/htmlize on` — start the view, switch to HTML output (opens a tab)
- `/htmlize off` — back to normal terminal replies
- `/htmlize` — toggle

Artifacts land in `.claude-html/NNNN-slug.html` (static — flicker-free, widgets keep state);
`index.html` lists them and refreshes every ~2s. Worth `.gitignore`-ing `.claude-html/`.

## Default vs the optional server

Default (shell only): a new reply shows up atop the auto-refreshing index — one click to read.
`scripts/serve.py` (needs Python or Node): content appears in place, no clicks, no refresh tick.
