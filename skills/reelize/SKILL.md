---
name: reelize
description: Generate a short video with music composed in code and locked to the motion — Strudel (the TidalCycles live-coding language) rendered to audio headlessly in Node, Remotion (React) for frame-perfect visuals, muxed into one MP4. Use when the user wants a music video, audio-reactive reel, beat-synced animation, visualizer, title/logo sting, or a generative/programmatic soundtrack for an animation — or names Strudel or Remotion, or says "make a video with music", "score this", "put a beat behind this".
---

# reelize

Make a short audiovisual piece where the **music and the motion are one composition**, both generated from code. Strudel writes the music; it renders to a WAV headlessly in Node (no browser, no screen recording). Remotion builds the visuals in React and reads the **same tempo**, so cuts land on beats and the drop hits on a cut. The result should feel *composed* — intentional rhythm, mood, and motion — not "a React `<div>` with a beep behind it."

The leap this skill is for: a model following it should produce reels that feel authored. That comes from taste, not plumbing. Three reference files carry it — **read the one you're working in before you write**:

- **[SOUND.md](SOUND.md)** — how to write Strudel that actually sounds good: rhythm, harmony, sound design, mixing so it doesn't clip. Read before writing `music.mjs`.
- **[MOTION.md](MOTION.md)** — beat-to-frame sync, easing, and the arc of a 10–30s piece. Read before writing the composition.
- **[REFERENCE.md](REFERENCE.md)** — the verified setup, every footgun, version pins, troubleshooting, and licensing. Read when something breaks or before you change the rig.

**Composing with other skills.** reelize owns what's unique here: the Strudel → headless-WAV half, the music-to-motion sync, and the verified pipeline specifics. For *general or advanced Remotion* craft beyond that — transitions, fonts, captions, text-animation primitives, richer audio-visualization (waveforms, smooth SVG paths) — **defer to the `remotion-best-practices` skill if it's installed**; it's broader and deeper on plain Remotion. But where they overlap, keep reelize's tested choices: **`Html5Audio` from `'remotion'`** (verified headless on the pinned version; the other skill reaches for the experimental `@remotion/media` `<Audio>`), and **`durationInFrames` derived from `sync.mjs`** rather than recomputed via `calculateMetadata` — reelize's whole point is that one source of truth. This is a soft handoff, not a dependency: reelize is fully self-contained and works with the other skill absent.

## The mental model

```
music.mjs ──► render-audio.mjs ──► public/audio.wav ──┐
(Strudel pattern)   (superdough +                      │   Remotion reads sync.mjs ──► out.mp4
                     OfflineAudioContext, in Node)      ▼   (Html5Audio + frame-locked motion)
                              sync.mjs  ◄──────────────────  (one source of truth: tempo + length)
```

Strudel measures time in **cycles** (a cycle = one bar); Remotion in **frames**. `sync.mjs` is the only place tempo and length live, imported by both sides, so audio and video can never drift. `seconds = cycles / cps = frames / fps`.

## Workflow

1. **Scaffold.** Copy [`template/`](template/) into a working directory (default: a `reel/` folder in the user's project). `cd` in and `npm install`. The template is a complete, verified Remotion + Strudel project; pins matter — don't bump them blindly (see REFERENCE.md → "Versions").
2. **Pick the format & tempo.** Aspect ratio depends on where the video is going — **ask the user (or infer from their platform)**: 9:16 `1080×1920` for Reels/Shorts/TikTok (the default if unstated), 1:1 `1080×1080`, or 16:9 `1920×1080`. Set `width`/`height` in `src/Root.tsx`. Set BPM and number of bars in `sync.mjs` — everything downstream derives from it.
3. **Compose** in `music.mjs`. Read **SOUND.md** first. Build a layered `stack(...)` — pulse/drums, bass, harmony, a lead — gain-staged so it doesn't clip. Iterate fast with `npm run audio` (renders in ~1s) and listen.
4. **Render audio:** `npm run audio` → writes `public/audio.wav`, normalized to ‑1 dBFS, and prints the frame count.
5. **Build motion** in `src/Video.tsx`. Read **MOTION.md** first. Lock structural cuts/reveals to beat frames from `sync.mjs`; carry the accent on each hit with `spring()`; optionally make elements react to the audio with `visualizeAudio`. Preview live with `npm run studio`.
6. **Render video:** `npm run video` → `out.mp4` with the audio muxed in. Or `npm run build` to do audio + video in one step.

Iterate steps 3–6. Re-render audio whenever the music changes; the video picks up the new WAV and the new length automatically.

## Non-negotiables (or it silently fails)

These are load-bearing — the full explanation and the rest are in REFERENCE.md, but never drop these:

- **Pinned versions.** `@strudel/core`/`mini`/`tonal` at **`1.2.5`** (1.2.6 fails to import in Node), `superdough@1.3.0`, `node-web-audio-api@2.0.0`. The template's `package.json` already pins them; keep it.
- **`audio-globals.mjs` is imported first**, before any `@strudel/*` or `superdough` — it installs the Web Audio globals those packages patch at load time.
- **`core.setStringParser(mini)`** is called once before building patterns, or mini-notation strings like `"c3 e3 g3"` silently collapse into one dead note.
- **Gain-stage and let the renderer normalize.** Keep per-voice gains low when layering (kick ~0.6–1, bass ~0.4, pads ~0.15, leads ~0.12); `render-audio.mjs` peak-normalizes to ‑1 dBFS so the master never clips. See SOUND.md → "Mixing".

## The taste bar

Before calling a reel done, check it against the bar both reference files set:

- The **music** has a shape — it isn't one loop of equal-weight events. Something leads, something supports, there's space. It doesn't clip.
- The **biggest visual change lands on the biggest musical moment**, on a beat — not on a random frame, not on every beat.
- Motion is **eased**, not linear; there's one focal idea, a limited palette, legible type kept out of the bottom 20%.
- It would survive with the sound off *and* with the picture off — each half is composed on its own.

## Licensing — surface this, don't bury it

Three different licenses touch this pipeline. Tell the user what applies to **their** situation (full detail + sources in REFERENCE.md → "Licensing"):

- **Remotion is not MIT.** Free for individuals, non-profits, and companies **≤ 3 employees**; orgs with **4+ employees need a paid Company License** (remotion.pro) — *including automated/CI render pipelines*. If the user might be over the line, say so up front.
- **Strudel/superdough are AGPL-3.0.** The rendered MP4 does **not** inherit AGPL (it's output, not a covered work). But distributing a project that bundles `@strudel/*` is "conveying" and triggers AGPL on that code. Local rendering for yourself does not.
- **Sample banks have their own licenses.** Reach for whatever sounds best — the template's default uses dirt-samples drums because they sound great, and that's fine for personal/most use. But most dirt-samples banks have *no clear license*, so for **distributed/commercial** work say so and switch to CC0 (`VCSL`) or pure synthesis (`SAMPLES = []` + the synth-drum recipes). Sound first; flag the license cost so the user chooses knowingly.

Don't install or register this skill yourself, and don't claim a reel is "done" until you've actually rendered the MP4 and it has both streams.
