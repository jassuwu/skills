---
name: htmlize
description: Render substantial replies (plans, specs, code reviews, explainers, comparisons) as polished, self-contained HTML in a live browser tab instead of walls of terminal Markdown. Use when the user runs /htmlize, says "htmlize", wants a live HTML view of the conversation, or asks for visual or shareable output.
argument-hint: "on | off (omit to toggle)"
---

# htmlize

When on, write each substantial reply as a self-contained HTML file in `.htmlize/` and show it in a live browser tab served by a tiny local server. The terminal reply shrinks to a one-line pointer. Needs `python3`. Never explain this plumbing to the user.

`/htmlize on` turns it on for the session; `/htmlize off` turns it off; bare `/htmlize` toggles — read `.htmlize/.mode` and switch to the opposite state.

## Turn on

1. Make `.htmlize/`. Copy the bundled [scripts/serve.py](scripts/serve.py) to `.htmlize/.serve.py`.
2. If `.htmlize/.serve.pid` names a live process, reuse it. Otherwise start the server in the background:
   `nohup python3 .htmlize/.serve.py --dir .htmlize > .htmlize/.serve.log 2>&1 & echo $! > .htmlize/.serve.pid`
   It binds `127.0.0.1` on a free port from 7878, opens the browser, and live-reloads on every change. If `python3` is missing, tell the user the skill needs Python and stop.
3. Write `on` to `.htmlize/.mode`. Read the URL the server printed in `.htmlize/.serve.log` and tell the user in one line where the view is.

## Turn off

Stop the server (`kill "$(cat .htmlize/.serve.pid 2>/dev/null)" 2>/dev/null`; remove `.htmlize/.serve.pid`), write `off` to `.htmlize/.mode`. Reply in the terminal normally again.

## While on

A substantial reply — plan, spec, code review, PR writeup, architecture overview, research summary, explainer, comparison, runbook — does not go in the terminal. Write it to `.htmlize/NNNN-slug.html` (zero-padded; next number from `ls .htmlize/*.html`). The server detects the new file and reloads the open tab — no extra step. Reply in at most two lines: what it is and the path. New topic → new file. Iterating on the same thing → edit that file.

Each artifact must set three `<head>` tags — `<title>`, `<meta name=description>` (one-line summary), and `<meta name=htmlize-type>` (one of: plan, review, spec, explainer, comparison, research, runbook, design, note) — because the index is a **reading list** built from them. Then build it per [ARTIFACT.md](ARTIFACT.md): a clear, readable, self-contained post that uses a visual only where it genuinely helps the reader understand — not a Markdown dump in a `<body>`.

Posts from one conversation form a trail. Optionally tag a post with `<meta name=htmlize-conversation content="…">` (the thread's title) to group it, and — on a post that continues an earlier one — `<meta name=htmlize-link content="…">`: one plain phrase for *why the work moved here* from the post before it. Omit the link when there's no honest connection; never manufacture filler. The reading list and an injected in-page prev/next render the trail from these.

A trivial reply — a quick fact, a clarifying question, a status line, a confirmation — goes in the terminal as usual. Don't wrap one sentence in a web page.

## Notes

The server ([scripts/serve.py](scripts/serve.py), stdlib only, binds `127.0.0.1`) renders the index as a reading list — the user can drag to reorder, pin, soft-delete (recoverable from Trash), and filter; that state persists to `.htmlize/.state.json`. It injects a live-reload script over SSE plus a "← reading list" back-link into each post, so new and edited artifacts appear in place — no refresh tick, no new tab, and you never add nav chrome yourself. The mode is remembered for the session; after `/compact`, run `/htmlize on` again (a still-running server is reused, no second tab). On a remote or headless box there's no browser to open — give the user the URL.
