---
name: bms-watcher
description: Watch BookMyShow for ticket availability — a zero-dependency Bun CLI that polls theatres for a movie, format, and seat tier, and pings a Discord webhook the moment seats open
triggers:
  - "bookmyshow"
  - "bms"
  - "movie tickets"
  - "ticket availability"
  - "watch for tickets"
  - "ticket alert"
  - "imax tickets"
  - "seats open"
  - "track tickets"
  - "movie booking alert"
---

# BMS Watcher

A BookMyShow ticket availability watcher. Zero npm dependencies — uses
Bun's native `fetch()` and regex parsing. Configure what to watch in
`watches.json`, then check once or poll continuously with Discord alerts.

## Commands

```
bun run bms-watcher.ts --discover-venues --region <CODE> [--filter <text>]
bun run bms-watcher.ts --check [--watch-id <id>]
bun run bms-watcher.ts --watch
bun run bms-watcher.ts --test-discord
```

| Command | What it does |
|---------|-------------|
| `--discover-venues` | List all theatre venues for a region (`--region CHEN`, `BANG`, `HYD`, `MUM`; optional `--filter <text>` by name/area) |
| `--check` | Check all watches once, output JSON to stdout (logs go to stderr); `--watch-id <id>` for a single watch |
| `--watch` | Standalone polling mode — checks every 45 seconds and sends Discord alerts. Requires `BMS_DISCORD_WEBHOOK` |
| `--test-discord` | Send a test notification to the webhook. Requires `BMS_DISCORD_WEBHOOK` |

## Configuration (`watches.json`)

Lives in the same directory as the script. Each watch:

```json
{
  "watches": [
    {
      "id": "dhurandhar2",
      "movie": "Dhurandhar 2",
      "regionCode": "CHEN",
      "city": "chennai",
      "formats": ["2D", "IMAX 2D"],
      "language": "Hindi",
      "seatFilter": "optimal",
      "theatres": [
        { "venueCode": "PVTJ", "name": "PVR: Theyagaraja, Thiruvanmiyur, Chennai" }
      ]
    }
  ]
}
```

- **movie** — matched against BookMyShow event titles.
- **regionCode / city** — from `--discover-venues`.
- **formats / language** — e.g. `["2D", "IMAX 2D"]`, `"Hindi"`. Both must match.
- **seatFilter** — `"optimal"` highlights the optimal seat tier (the
  second-highest price band — best viewing); non-optimal-only matches are
  still reported but flagged. `"all"` treats any available seats as a hit.
- **theatres** — venue codes to scan, from `--discover-venues`.

## Check output

`--check` scans today plus the next 14 days for every watched theatre and
prints JSON with a status per watch:

| Status | Meaning |
|--------|---------|
| `found` | Matching shows with available seats |
| `listed_no_seats` | Right format and language listed, but no seats yet |
| `listed_wrong_format` | Movie listed, but not in a watched format/language |
| `not_listed` | Movie not on sale at the watched theatres |

## Discord alerts

Set the webhook first:

```sh
export BMS_DISCORD_WEBHOOK="https://discord.com/api/webhooks/..."
```

In `--watch` mode, each new matching show fires one embed (deduplicated per
show) with theatre, format, date, time, seat tiers with prices, and the
booking URL. Green embed (`0x2ecc71`) when optimal seats are available —
"Tickets Available!" — orange (`0xe67e22`) when only non-optimal tiers are open.

## Workflow

1. `--discover-venues --region <CODE>` to find venue codes (use `--filter`
   to narrow by area or chain).
2. Edit `watches.json` with the movie, formats, language, and theatres.
3. `--test-discord` to verify the webhook.
4. `--check` for a one-shot answer, or `--watch` to poll until seats open.

## Notes

- Polling interval is 45 seconds; each check sleeps 1.5s between venue
  requests to stay polite.
- `--check` writes machine-readable JSON to stdout and human logs to
  stderr — safe to pipe.
- Long-running `--watch` sessions are best kept under a process manager
  (tmux, launchd, systemd) on a machine that stays awake.
