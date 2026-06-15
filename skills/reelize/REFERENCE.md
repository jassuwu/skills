# REFERENCE — the rig, the footguns, the licenses

Everything here was verified by rendering real audio and video in Node v22 on the pinned versions. Where a claim was checked by running code, it's marked **(verified)**. Read this before you change the setup or when something silently produces nothing.

## Versions — pinned for a reason

| Package | Pin | Why this exact version |
|---|---|---|
| `@strudel/core` | **1.2.5** | **1.2.6 fails to import in Node (verified):** its bundle does `import { SalatRepl } from '@kabelsalat/web'`, and Node resolves that package's CJS `main`, where the named export isn't visible → `SyntaxError`. 1.2.5 is the last clean version. The error reproduces on a *pristine* single-copy install — it is not a dedupe problem. |
| `@strudel/mini` | **1.2.5** | Exact-pins `@strudel/core@1.2.5`; keep it in lockstep so there is one core copy. |
| `@strudel/tonal` | **1.2.5** | Same — provides `scale`/`chord`/`voicing`. |
| `superdough` | **1.3.0** | The sound engine. Has **no** `@strudel/core` dependency (verified) — that decoupling is what makes the headless path clean. |
| `node-web-audio-api` | **2.0.0** | IRCAM's native Web Audio for Node. Implements `OfflineAudioContext` + `startRendering()` + the full standard node set + `decodeAudioData` (verified). |
| `remotion`, `@remotion/cli`, `@remotion/media-utils` | **4.0.477** | Keep these three on the same version. |

**Do not install `@strudel/webaudio`.** It's the browser glue you don't need, and it drags in a second `@strudel/core` copy — which is exactly what breaks mini-notation (see F2). The template drives `superdough` directly. The `overrides: { "@strudel/core": "1.2.5" }` in `package.json` is belt-and-suspenders to guarantee a single copy; `npm ls @strudel/core` should always show exactly one.

> Strudel development moved from `github.com/tidalcycles/strudel` (now an archived stub) to **`codeberg.org/uzu/strudel`**. Prose docs at **strudel.cc/learn** are canonical. GitHub `packages/` paths 404.

## The headless audio shim (`audio-globals.mjs`)

superdough is browser code. Three things make it run in Node, and **order matters**:

1. **Install Web Audio classes as globals.** superdough patches reverb/delay/vowel onto `BaseAudioContext.prototype` at module-load time, guarded by `typeof AudioContext !== 'undefined'`. We `Object.assign(globalThis, node-web-audio-api)` so those globals exist.
2. **Do it in a module imported *before* superdough.** ES `import` statements are **hoisted** — they run before any top-level code in the same file. So the global install lives in its own file (`audio-globals.mjs`) that is the *first* import of `render-audio.mjs`. Inline `Object.assign(...)` after the imports runs too late and the effect patches silently no-op (verified: `.room()` threw "createReverb is not a function" until the install moved earlier).
3. **Stub `window` and `document` with no-ops.** superdough does `window.addEventListener('message', …)` at load and `window.filterNode = …` in its reverb generator; core attaches a `document` mouse-listener and a highlight `CustomEvent`. A bare `{}` is worse than nothing — it lacks `addEventListener` and crashes (verified). No-op stubs with `addEventListener`/`dispatchEvent`/`createElement` keep every path quiet.

Then the render: `setAudioContext(new OfflineAudioContext(2, frames, SR))`, `registerSynthSounds()`, optionally `loadWorklets()` and `samples(...)`, schedule one `superdough()` per onset hap, `await ctx.startRendering()`. We **never** call `initAudio()`/`initAudioOnFirstClick()` — those are browser-only (they wait on a DOM click).

## How the offline render maps time

- A pattern is queried into **haps** (events): `pattern.queryArc(0, CYCLES)` → array of `{ whole, part, value, … }`. `whole.begin/end` are `Fraction`s of **cycles**; `value` is the control object (`{note, s, gain, …}`).
- Keep only **onsets**: `.filter(h => h.hasOnset())` — a held/clipped note re-appears as fragments without a fresh attack; triggering those double-hits it.
- Convert to seconds with **cps** (cycles per second): `onset = begin / cps`, `duration = (end - begin) / cps`. Then `superdough(value, onset, duration, cps, begin)`.
- Size the context in **sample frames**, not seconds: `Math.ceil(seconds * sampleRate)`. We add `TAIL` seconds so reverb/delay/long releases past the last note aren't cut off.
- **(verified)** renders ~30–50× faster than realtime; an 18s piece renders in ~1–2s.

This mirrors Strudel's own `renderPatternAudio()` (in `@strudel/webaudio`) — but that function's tail does a browser-only `Blob`/anchor download, so we replicate its math and write the WAV with `fs.writeFileSync` instead.

## Footguns (all confirmed by running code)

- **F1 — Mini-notation silently dies without a parser.** `note("c3 e3 g3")` without `setStringParser` becomes ONE atom valued `"c3 e3 g3"`; at trigger time `noteToMidi` throws and the voice is **silent + a logged error**. **Fix:** `core.setStringParser(mini)` once, before building patterns. (Importing `@strudel/mini` does not auto-enable it across copies.)
- **F2 — Two `@strudel/core` copies break mini-notation even with `setStringParser`.** The parser is a per-copy module-scoped singleton; set it on copy A, reify in copy B → no-op. **Fix:** one core copy — keep the trio version-locked, don't add `@strudel/webaudio`, keep the `overrides`.
- **F3 — `@strudel/core@1.2.6` won't import in Node.** See the version table. **Fix:** pin 1.2.5.
- **F4 — ESM only.** All `@strudel/*` and `superdough` are `type: module`. Run audio generation as a separate Node ESM step that writes a WAV; never import `@strudel/*` into the bundled Remotion/browser graph.
- **F5 — Globals/stubs must precede superdough** (the shim above). Wrong order → silent render or import crash.
- **F6 — Synths need `registerSynthSounds()`** or `sawtooth/square/triangle/sine` are silent with no error. Call it once after `setAudioContext`.
- **F7 — Synths REQUIRE a duration.** Omit it → `t + undefined = NaN` → the voice throws and (un-awaited) can crash the render. **Fix:** always pass `duration`, and wrap scheduling in `await Promise.allSettled(...)` (the template does). One-shot samples may omit it.
- **F8 — No master limiter → clipping.** Stacked voices sum past ±1.0 and `OfflineAudioContext` hard-clips. **Fix:** gain-stage (SOUND.md §5) and let `render-audio.mjs` peak-normalize. A reported raw peak ≫ 1 means the *balance* is off, not just the level.
- **F9 — `.room()`/`.delay()` and the controller context.** Reverb/delay work headless **(verified)** *as long as* `setAudioContext` runs before the first voice, so superdough's effect controller binds to the offline context. Rendering **one pattern per process** (what the template does — a fresh `node render-audio.mjs`) guarantees this. If you render multiple patterns in one long-lived process, the controller singleton can hold a stale context and throw "connecting nodes from different contexts" — start a new process per render, or reset the controller.
- **F10 — Worklet sounds need `loadWorklets()`.** `supersaw`, wavetables, `crush`/`coarse`/`shape` are AudioWorklet-based; they load in Node via superdough's bundled `data:` URL **(verified)** but only after `await loadWorklets()`. The template sets `USE_WORKLETS = true`. If a future version breaks `data:`-URL worklet loading, set it `false` and stay on native oscillators + filters + delay + reverb (still a full palette).
- **F11 — Remotion stale names.** Use **`Html5Audio`** (not the deprecated `Audio` alias) and **`trimBefore`/`trimAfter`** (not `startFrom`/`endAt`). Both old names still resolve in 4.0.477 but don't mix old + new on one element.
- **F12 — `useAudioData()` is `null` until loaded.** Guard `if (audio) { … }` before `visualizeAudio` or the render crashes. `numberOfSamples` must be a power of two.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| WAV is silent | missing `registerSynthSounds()`, or mini-notation not parsed, or wrong import order | check F1/F5/F6; the renderer warns on errored voices |
| `SyntaxError … SalatRepl` | core at 1.2.6 | pin 1.2.5 (F3) |
| `createReverb is not a function` | globals installed after superdough import | move them to `audio-globals.mjs`, imported first (F5) |
| crackle/distortion | clipping before normalize | turn down the dominant layer (F8) |
| `connecting nodes from different contexts` | controller bound to a stale context | one render per process (F9) |
| video length ≠ audio length | hardcoded `durationInFrames` | derive from `sync.mjs` (the template does) |
| `npm ls @strudel/core` shows 2 | a dep pulled another core | remove `@strudel/webaudio`; keep the `overrides` (F2) |

## Licensing — tell the user what applies to them

| Component | License | What it means |
|---|---|---|
| `@strudel/*`, `superdough` | **AGPL-3.0-or-later** | Copyleft. The **rendered MP4 is NOT a covered work** — it's output, you can sell/close it. But **distributing a project that bundles `@strudel/*` is "conveying"** and that code must be offered under AGPL with source. Running it locally to render your own video is not conveying. §13 network-source only bites if you *modify* Strudel *and* serve it over a network. |
| `node-web-audio-api` | **BSD-3-Clause** | Permissive; keep the notice. Not a copyleft trigger. |
| Remotion | **Remotion License** (not MIT) | Free for individuals, non-profits, and for-profit orgs **≤ 3 employees**. **4+ employees → paid Company License** (remotion.pro), *including automated/CI render pipelines.* Re-verify against the installed version (Remotion 5.0 will adjust terms). |
| Sample banks | **per-bank, mixed** | The template defaults to **dirt-samples** drums (they sound best) — most of its banks have **no declared license** (`tidal-drum-machines`/`EmuSP12` also emulate trademarked hardware), which is fine for personal/most use but a clearance risk for distribution. Clean options: `VCSL` = **CC0**; pure synthesis = none. `piano` = CC-BY (attribution), `mridangam` = CC-BY-SA. |

**Practical guidance:** sound first — sampled drums are the default because they're punchier, and for personal or most use the licensing is a non-issue. When the user is **distributing or selling**, that's when it matters: switch to CC0 (`VCSL`) or pure synthesis (`SAMPLES = []`) for a zero-burden soundtrack, and check the Remotion employee tier. The Strudel AGPL question is about *distributing the project/code*, never the video itself. The Remotion license is the one most likely to actually bind a user — surface it early if they sound like a company.

Sources: AGPL text gnu.org/licenses/agpl-3.0 · Strudel LICENSE codeberg.org/uzu/strudel · node-web-audio-api LICENSE (BSD-3) github.com/ircam-ismm/node-web-audio-api · Remotion license remotion.dev/docs/license · Dirt-Samples per-folder `*_license.txt` github.com/tidalcycles/Dirt-Samples · VCSL github.com/sgossner/VCSL.
