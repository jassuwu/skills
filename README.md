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
<em>teach it once.</em>
</div>

<p align="center">
<a href="https://skills.sh/jassuwu/skills"><img src="https://skills.sh/b/jassuwu/skills" alt="skills.sh"></a>
</p>

## install

```sh
bunx --bun skills add jassuwu/skills
```

or just the one you want:

```sh
bunx --bun skills add jassuwu/skills -s htmlize
```

installs via [skills.sh](https://skills.sh) — works with Claude Code, Cursor, Codex, and friends.

## the skills

| skill | what it teaches the agent |
|---|---|
| [`htmlize`](./skills/htmlize) | render substantial replies — plans, reviews, specs, explainers — as polished, self-contained HTML in a live browser tab that updates in place, instead of walls of terminal Markdown. needs `python3` and a browser. `/htmlize on` to start, `/htmlize off` to stop, bare `/htmlize` to toggle |
| [`reelize`](./skills/reelize) | make a short video where the music is composed in code and locked to the motion — Strudel (live-coding music) rendered to audio headlessly in Node, Remotion (React) for frame-perfect visuals, muxed into one MP4. encodes the taste to make reels that feel composed, not "a div with a beep." needs `node` 18+; the first video render fetches a headless chromium |

## anatomy

each skill is a directory under [`skills/`](./skills). the `SKILL.md` is the lesson; anything else is the tooling and reference it drives. [`.claude-plugin/plugin.json`](./.claude-plugin/plugin.json) lists what ships.

```
skills/
└── htmlize/
    ├── SKILL.md          # when it's on, the behaviour, the on/off toggle
    ├── ARTIFACT.md       # how each HTML artifact should look + read
    ├── README.md         # the skill, in depth
    └── scripts/
        └── serve.py      # live-reload server (python3, stdlib, binds 127.0.0.1)
```

## license

[MIT](LICENSE)
