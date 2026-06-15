# MOTION — making the picture feel like part of the music

The bar: the **biggest visual change lands on the biggest musical moment**, on a beat. Motion is *eased*, there's one focal idea, and the type is legible. If the visuals would look the same behind any other track, they aren't composed — they're decoration.

You build the composition in `src/Video.tsx`. Preview live with `npm run studio` (scrub the timeline, hear the audio, see the motion). Everything timing-related comes from `sync.mjs` so it stays locked to the music.

## 1. Beat → frame is exact — use it

Remotion is frame-deterministic: frame `f` is exactly `f / fps` seconds. Strudel's tempo is known. So every beat maps to an exact frame, and `sync.mjs` already computes it:

```js
import { FRAMES_PER_BEAT, FRAMES_PER_BAR, beatFrame, barFrame } from '../sync.mjs';
// 30 fps + 120 BPM → 15 frames/beat, 60 frames/bar.
beatFrame(4)   // the frame where beat 4 starts
barFrame(2)    // the frame where bar 2 (the third bar) starts
```

**Round only at placement** (the helpers do). Never accumulate `fps*60/bpm` in a loop — float error drifts the picture off the beat over a long piece. Derive each cut as `Math.round(index * framesPerBeat)`.

## 2. Where to cut — not on every beat

Cutting on every beat is frantic and flattens the arc. Instead:

- **Minor accents on beats** (a pulse, a flicker) — small.
- **Major cuts on downbeats** (`frame % FRAMES_PER_BAR === 0`) — a new section, a new color, a new shot.
- **The biggest change on the drop** — the one moment you've been building to. Reserve your largest move (full-screen flash, hard cut, scale jump) for it. Sync this to the loudest bar in `music.mjs` (SOUND.md → "Arrangement").
- **Vary shot length by energy:** sparse intro = long holds (whole bars); peak = quick changes (every beat or half-beat). Accelerating cut frequency *is* tension.

```js
const bar = Math.floor(frame / FRAMES_PER_BAR);
const isDrop = bar === 4;                      // the bar your music drops on
```

## 3. Easing — the line between musical and mechanical

Linear tweens read robotic. Two tools, used together:

- **`spring()`** for the *accent on a hit* — natural overshoot and settle, few magic numbers:
  ```js
  const since = frame - beatFrame(Math.floor(frame / FRAMES_PER_BEAT));
  const settle = spring({ frame: since, fps, config: { damping: 12, stiffness: 180, mass: 0.7 } });
  const punch = 1 - settle;                    // 1 at the beat, decays to 0 — a pop
  ```
- **`interpolate(...)` + `Easing`** for *grid-locked reveals* — exact start/end frames, eased curve:
  ```js
  const intro = interpolate(frame, [0, FRAMES_PER_BAR], [0, 1],
    { extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic) });   // ease-out entrance
  ```
  `Easing.out(Easing.cubic)` decelerates into place; `Easing.inOut(Easing.cubic)` for symmetric moves; reserve `Easing.linear` for genuinely continuous mechanical motion (a steady rotation).

**Anticipation + follow-through** sell a hit: a small wind-up a few frames *before* the downbeat, the impact *on* it, an eased overshoot *after*. That tiny pre-roll is what makes a beat feel struck rather than switched.

## 4. React to the audio (optional, tasteful)

`visualizeAudio` gives per-frame frequency energy so elements can breathe with the sound. It needs `@remotion/media-utils` (in the template) and **must be guarded** — `useAudioData` is `null` until the file loads:

```js
const audio = useAudioData(staticFile('audio.wav'));
let bass = 0;
if (audio) {
  const bins = visualizeAudio({ audioData: audio, frame, fps, numberOfSamples: 16, smoothing: false });
  bass = Math.min(1, (bins[0] + bins[1]) * 1.6);   // low bins = bass; high index = treble
}
```

`numberOfSamples` **must be a power of two** (16/32/64/128). `smoothing: false` gives sharp per-frame transients (good for a kick punch); `true` blurs them. Map energy to **one** property — scale, glow, opacity — not ten. Reactivity is seasoning on top of the beat-locked structure, not a substitute for it: a purely amplitude-driven blob with no choreography still reads as a screensaver.

For *richer* readouts — oscilloscope waveforms, smooth SVG paths, windowed data for long tracks — defer to the **`remotion-best-practices`** skill's audio-visualization rules if it's installed (`visualizeAudioWaveform`, `createSmoothSvgPath`, `useWindowedAudioData`). The point above still governs: lock structure to the beat first, react second.

## 5. Compose for short-form

- **Format.** Default **9:16, 1080×1920** (Reels/Shorts/TikTok). Keep the focal idea centered so the same composition survives a 1:1 (1080×1080) or 16:9 (1920×1080) crop — change `width`/`height` in `src/Root.tsx`. Reserve the **bottom ~20%** for platform UI; keep nothing essential there.
- **One focal point.** A single thing the eye goes to, dead center or on a third. Everything else supports it. Resist adding a second hero.
- **Three tiers of weight** — focal (brightest/largest/moving), support (the backdrop that breathes), detail (small accents). If everything is loud, nothing is.
- **Limited palette.** Two or three hues plus near-black/near-white. A single accent hue that shifts subtly per section (the template drifts hue by bar) reads as intentional.
- **Type as motion, kept legible.** Bold sans, big, animated in on a beat. Contrast ≥ 4.5:1 — over a busy background add a scrim (a 60–80% black panel) or a stroke. Keep text in the centre band (top ~20% to ~80%), never the bottom strip.
- **Restraint.** Reduce until removing one more thing would break it. Most great reels are one strong idea executed cleanly, not five competing ones.

## 6. The arc of a 10–30s piece (map it to frames)

Match the music's shape (SOUND.md → "Arrangement"):

| Section | When | Visual |
|---|---|---|
| **Hook** | bar 1 (frames `0 … FRAMES_PER_BAR`) | the focal idea enters, eased; establish the world in the first second |
| **Build** | bars 2–3 | add motion/elements, tighten, accelerate accents, push energy up |
| **Drop / payoff** | the drop bar | the biggest change — land it on the downbeat; this is the frame people remember |
| **Resolve** | last bar | ease everything out; let the reverb tail and the picture settle together |

Hold the hook for the first ~second — a viewer decides instantly. Don't open on black or a slow fade-up unless the music does too.

## 7. Render

`npm run studio` to preview (live audio + scrub). `npm run video` to render `out.mp4` (audio muxed in by Remotion — no screen capture). The composition length is `DURATION_IN_FRAMES` from `sync.mjs`, so it always matches the WAV. Re-render audio first if the music changed.

## Anti-patterns

- **Motion that ignores the beat** — the cardinal sin. If a cut doesn't land on a beat frame, move it.
- **Cutting on every beat** — frantic, no arc. Save big moves for downbeats and the drop.
- **Linear tweens everywhere** — mechanical. Ease entrances, spring the hits.
- **Everything moving at once / no focal point** — a screensaver. One hero, supported.
- **Hit with no setup** — a change that just appears. Add a few frames of anticipation.
- **Low-contrast text, or text in the bottom 20%** — illegible or covered by platform UI. Scrim it, raise it.
- **Reactivity as the whole plan** — amplitude-driven scale with no choreography. Beat-lock the structure first, react second.
- **Hardcoding `durationInFrames`** — drifts from the audio. It comes from `sync.mjs`; leave it.
