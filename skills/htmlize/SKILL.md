---
name: htmlize
description: Render substantial replies (plans, specs, code reviews, explainers, comparisons) as polished, self-contained HTML in a live browser tab instead of walls of terminal Markdown. Use when the user runs /htmlize, says "htmlize", wants a live HTML view of the conversation, or asks for visual or shareable output.
argument-hint: "on | off (omit to toggle)"
---

# htmlize

When on, write each substantial reply as a self-contained HTML file in `.claude-html/` and surface it in a browser tab. The terminal reply shrinks to a one-line pointer. Needs only a POSIX shell and a browser — no Python or Node. Never explain this plumbing to the user.

`/htmlize on` turns it on for the session; `/htmlize off` turns it off; bare `/htmlize` toggles — read `.claude-html/.htmlize` and switch to the opposite state.

## Turn on

1. Make `.claude-html/`. Copy the bundled [scripts/mkindex.sh](scripts/mkindex.sh) to `.claude-html/.mkindex.sh`.
2. Run `sh .claude-html/.mkindex.sh` (builds an empty index), then write `on` to `.claude-html/.htmlize`.
3. Open `.claude-html/index.html` in the browser — try `open`, else `xdg-open`, else `start`; if none works, print the path. Tell the user in one line where the view is.

## Turn off

Write `off` to `.claude-html/.htmlize`. Reply in the terminal normally again.

## While on

A substantial reply — plan, spec, code review, PR writeup, architecture overview, research summary, explainer, comparison, runbook — does not go in the terminal. Write it to `.claude-html/NNNN-slug.html` (zero-padded; next number from `ls .claude-html/*.html`), run `sh .claude-html/.mkindex.sh`, then reply in at most two lines: what it is and the path. New topic → new file. Iterating on the same thing → edit that file.

A trivial reply — a quick fact, a clarifying question, a status line, a confirmation — goes in the terminal as usual. Don't wrap one sentence in a web page.

Write each artifact per [ARTIFACT.md](ARTIFACT.md).

## Notes

Only `index.html` refreshes — it's a list. Artifacts are static, so they read smoothly and keep interactive state. The mode is remembered for the session; after `/compact`, run `/htmlize on` again. On a remote or headless box there's no browser to open — give the user the path. For a zero-click variant that updates in place (needs Python or Node), run the bundled [scripts/serve.py](scripts/serve.py) instead of the steps above.
