# reelize

Generate short videos where the **music and the motion are one composition**, both written in code. [Strudel](https://strudel.cc) composes the music and renders it to a WAV headlessly in Node; [Remotion](https://remotion.dev) builds the visuals in React and reads the same tempo, so beats and cuts line up. Out comes one MP4.

This is greenfield — nothing else wires Strudel into Remotion. The hard part (rendering a Strudel pattern to audio with no browser and no screen recording) is solved here and verified end-to-end.

## What it teaches the agent

Not just plumbing — **taste**. The skill carries three reference files the model reads before it writes:

| File | Read before | Carries |
|---|---|---|
| [`SKILL.md`](SKILL.md) | always | the philosophy, the mental model, the workflow, the non-negotiables |
| [`SOUND.md`](SOUND.md) | writing music | rhythm, harmony, sound design, mixing, a cookbook — how Strudel sounds *composed* |
| [`MOTION.md`](MOTION.md) | writing visuals | beat→frame sync, easing, short-form composition, the arc of a piece |
| [`REFERENCE.md`](REFERENCE.md) | when it breaks | the verified rig, every footgun, version pins, troubleshooting, licensing |

## The pipeline

```
music.mjs ──► render-audio.mjs ──► public/audio.wav ──► Remotion (src/Video.tsx) ──► out.mp4
(Strudel)     (superdough on a                          (Html5Audio + frame-locked
               Node OfflineAudioContext)                 motion + visualizeAudio)
                           ▲                                      ▲
                           └──────────── sync.mjs ────────────────┘
                              (tempo + length: one source of truth)
```

Strudel counts time in **cycles** (a cycle = a bar), Remotion in **frames**; `sync.mjs` is the only place tempo and length live, so the two halves can't drift. `seconds = cycles / cps = frames / fps`.

## How a piece gets made

```sh
cp -r template reel && cd reel && npm install   # complete, pinned, verified starter
# edit sync.mjs   → tempo & length
# edit music.mjs  → the music (read SOUND.md)
npm run audio                                    # → public/audio.wav, normalized, ~1s
# edit src/Video.tsx → the motion (read MOTION.md)
npm run studio                                   # live preview (audio + scrub)
npm run video                                    # → out.mp4 with audio muxed in
```

`npm run build` does audio + video in one step.

## The stack (and why these versions)

- **`@strudel/core` / `mini` / `tonal` @ 1.2.5** — the pattern language. 1.2.6 fails to import in Node (a broken `@kabelsalat/web` import); 1.2.5 is the last clean release.
- **`superdough` @ 1.3.0** — Strudel's standalone sound engine. Driven directly (no `@strudel/webaudio`), so there's exactly one `@strudel/core` copy and mini-notation works.
- **`node-web-audio-api` @ 2.0.0** — IRCAM's native Web Audio for Node; provides the `OfflineAudioContext` that renders faster than realtime.
- **`remotion` + `@remotion/cli` + `@remotion/media-utils` @ 4.0.477** — the video side. `Html5Audio` consumes the WAV; `visualizeAudio` drives audio-reactive visuals.

Full rationale and the footgun list are in [REFERENCE.md](REFERENCE.md).

## Licensing (short version — details in REFERENCE.md)

- **Remotion is not MIT.** Free for individuals / non-profits / orgs ≤ 3 employees; 4+ employees need a paid Company License, including CI renders.
- **Strudel/superdough are AGPL-3.0.** Your rendered MP4 is *not* covered; distributing a project that bundles `@strudel/*` is.
- **Sample banks vary** — the template defaults to dirt-samples drums (best sound; mostly unlicensed, fine for personal use). For distribution, switch to CC0 (`VCSL`) or pure synthesis.

## Requirements

Node 18+ (tested on 22), `npm`. The first video render downloads a headless Chromium (Remotion handles it). macOS/Linux/Windows.
