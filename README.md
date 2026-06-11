<h1 align="center">skills</h1>

<p align="center">

<img src="https://img.shields.io/badge/Markdown-000000.svg?style=for-the-badge&logo=markdown&logoColor=white">
<img src="https://img.shields.io/badge/TypeScript-000000.svg?style=for-the-badge&logo=typescript&logoColor=white">
<img src="https://img.shields.io/badge/Bun-000000.svg?style=for-the-badge&logo=bun&logoColor=white">
<img src="https://img.shields.io/badge/Discord-000000.svg?style=for-the-badge&logo=discord&logoColor=white">

</p>

<p align="center">
agent skills you install like packages.
</p>

<div align="center">
_teach it once._
</div>

## install

```sh
bunx --bun skills add jassuwu/skills
```

or just the one you want:

```sh
bunx --bun skills add jassuwu/skills -s swiggy
```

installs via [skills.sh](https://skills.sh) — works with Claude Code, Cursor, Codex, and friends.

## the skills

| skill | what it teaches the agent |
|---|---|
| [`swiggy`](./swiggy) | order food, groceries, and book restaurants via Swiggy MCP — Food, Instamart, and Dineout. hard safety rules baked in: explicit confirmation before every order, COD only, no silent retries |
| [`bms-watcher`](./bms-watcher) | watch BookMyShow for ticket availability — a zero-dependency Bun CLI that polls your theatres for a movie, format, and seat tier, and pings a Discord webhook the moment seats open |

## anatomy

each skill is a directory. the SKILL.md is the lesson; anything else is the tooling it drives.

```
skills/
├── swiggy/
│   └── SKILL.md          # workflows, safety rules, presentation
└── bms-watcher/
    ├── SKILL.md          # commands, config, alert flow
    ├── bms-watcher.ts    # the watcher CLI (bun, zero npm deps)
    └── watches.json      # what to watch, where, in which format
```

## license

[MIT](LICENSE)
