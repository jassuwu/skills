---
name: htmlize
description: Render substantial replies (plans, specs, code reviews, explainers, comparisons) as polished, self-contained HTML in a live browser tab instead of walls of terminal Markdown. Use when the user runs /htmlize, says "htmlize", wants a live HTML view of the conversation, or asks for visual or shareable output.
argument-hint: "on | off (omit to toggle)"
---

# htmlize

When on, write each substantial reply as a self-contained HTML file in `.claude-html/` and show it in a live browser tab served by a tiny local server. The terminal reply shrinks to a one-line pointer. Needs `python3`. Never explain this plumbing to the user.

`/htmlize on` turns it on for the session; `/htmlize off` turns it off; bare `/htmlize` toggles — read `.claude-html/.htmlize` and switch to the opposite state.

## Turn on

1. Make `.claude-html/`. Copy the bundled [scripts/serve.py](scripts/serve.py) to `.claude-html/.serve.py`.
2. If `.claude-html/.serve.pid` names a live process, reuse it. Otherwise start the server in the background:
   `nohup python3 .claude-html/.serve.py --dir .claude-html > .claude-html/.serve.log 2>&1 & echo $! > .claude-html/.serve.pid`
   It binds `127.0.0.1` on a free port from 7878, opens the browser, and live-reloads on every change. If `python3` is missing, tell the user the skill needs Python and stop.
3. Write `on` to `.claude-html/.htmlize`. Read the URL the server printed in `.claude-html/.serve.log` and tell the user in one line where the view is.

## Turn off

Stop the server (`kill "$(cat .claude-html/.serve.pid 2>/dev/null)" 2>/dev/null`; remove `.claude-html/.serve.pid`), write `off` to `.claude-html/.htmlize`. Reply in the terminal normally again.

## While on

A substantial reply — plan, spec, code review, PR writeup, architecture overview, research summary, explainer, comparison, runbook — does not go in the terminal. Write it to `.claude-html/NNNN-slug.html` (zero-padded; next number from `ls .claude-html/*.html`). The server detects the new file and reloads the open tab — no extra step. Reply in at most two lines: what it is and the path. New topic → new file. Iterating on the same thing → edit that file.

A trivial reply — a quick fact, a clarifying question, a status line, a confirmation — goes in the terminal as usual. Don't wrap one sentence in a web page.

Write each artifact per [ARTIFACT.md](ARTIFACT.md).

## Notes

The server ([scripts/serve.py](scripts/serve.py), stdlib only, binds `127.0.0.1`) lists artifacts by their `<title>` and injects a live-reload script over SSE, so new and edited artifacts appear in place — no refresh tick, no new tab. The mode is remembered for the session; after `/compact`, run `/htmlize on` again (a still-running server is reused, no second tab). On a remote or headless box there's no browser to open — give the user the URL.
