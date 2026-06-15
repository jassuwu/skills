# SOUND — writing Strudel that sounds composed

The bar: the music has a **shape**. Something leads, something supports, there is space, and it doesn't clip. A loop of equal-weight events is the "beep" this skill exists to avoid. Everything below is in service of shape.

You write patterns in `music.mjs` as a `stack(...)` of layers, then `npm run audio` renders and you **listen** (it takes ~1s). Compose with your ears, not just your eyes.

## 1. The three ways notes relate in time — get this right first

This is the distinction that trips everyone up. Inside a mini-notation string:

| Notation | Name | Meaning | Use for |
|---|---|---|---|
| `"a b c"` | sequence | three events sharing **one cycle**, in order | a drum row, a fast riff, subdivision *within* a bar |
| `"<a b c>"` | slowcat | **one** element **per cycle**, cycling bar to bar | a chord progression, a melody that unfolds over bars |
| `"a,b,c"` | stack | all **at once** | a chord, simultaneous layers |

```js
note("c3 e3 g3")     // do-re-mi inside one bar — fast
note("<c3 e3 g3>")   // c3 in bar 1, e3 in bar 2, g3 in bar 3 — slow, melodic
note("c3,e3,g3")     // a C-major triad, struck together
```

Mixing them is how music happens: `note("<[c3,e3,g3] [f3,a3,c4]>")` is a two-bar chord progression (each bar one triad). Reach for `<>` whenever you want something to evolve across bars — it is the single most useful operator for making a loop feel *written* instead of repeated.

## 2. Mini-notation rhythm vocabulary

Built on the three above:

- `[a b]` — a **subdivision group**: `a b` packed into the time of one step. `"a [b c]"` = a, then b-c twice as fast.
- `a*2` faster (2×), `a/2` slower (half), `a!3` replicate (a a a), `a@3` elongate (a holds 3 steps), `~` rest.
- `a(3,8)` — **euclidean**: spread 3 hits as evenly as possible across 8 steps (`x..x..x.`). The fastest route to a groove that isn't a straight 4-on-the-floor. Try `(3,8)`, `(5,8)`, `(5,16)`, `(7,16)`.
- `a?` — random drop (50%). `<a b>?` plus `.degradeBy(0.2)` thins a busy line so it breathes.

Groove comes from **space and syncopation**, not density. A hat on `hh*8` is a metronome; `hh(5,8)` or `hh*8.gain("[.3 .6]*4")` has feel. Leave rests. Put the snare a hair late with `.late(0.02)` for a lazy, human pocket.

## 3. Harmony & mood

**Work in a scale** so wrong notes are impossible. `n("0 2 4 6").scale("C:minor")` plays scale degrees (0 = root, negatives and >7 wrap octaves):

```js
n("0 2 4 <2 4>").scale("C:minor")          // a melody that can't hit a sour note
note("c2").add(note("<0 3 5 7>")).scale...  // transpose a bassline through degrees
```

Mood shorthand (pick a tonic + scale + tempo together):

| Feeling | Scale | BPM (cps) | Notes |
|---|---|---|---|
| calm / dreamy | `C:major`, `C:lydian` | 70–90 (.29–.38) | long releases, reverb, sparse |
| melancholy / cinematic | `C:minor`, `A:aeolian` | 70–100 (.29–.42) | minor triads, slow `<>`, sub bass |
| tense / driving | `E:phrygian`, `C:minor` | 120–140 (.5–.58) | steady pulse, short notes, filter movement |
| hopeful / bright | `D:mixolydian`, `G:major` | 100–120 (.42–.5) | major chords, plucky arps |
| eerie / unresolved | `C:locrian`, whole-tone | any | avoid the root, let it hang |

**Register is arrangement.** Bass below ~C3, pads in the middle (C3–C4), leads/arps above C4. Don't pile layers in the same octave — they turn to mud. A wide gap between a low bass and a high arp, with a pad filling the middle, reads as "produced."

Tempo lives in `sync.mjs` (`CPS`). `BPM = CPS * 60 * 4`. Changing it re-times the whole piece and the video with it.

## 4. Sound design

A voice = a **sound** (`s`) + usually a **pitch** (`note`/`n`) + a **shape** (envelope) + **color** (filter/effects).

**Sources (`s`)** — verified to render headless:
- Native oscillators: `sine` (sub, soft), `triangle` (mellow, flute-ish), `square` (hollow, reedy), `sawtooth` (bright, the workhorse for bass & leads).
- Worklet oscillators (need `USE_WORKLETS = true`, the default): `supersaw` (huge detuned pad/lead), wavetables.
- Samples (need a `SAMPLES` bank loaded): `bd sd hh` etc. — see §7.

**Envelope** — `attack` `decay` `sustain` `release` (the four are seconds/level). This is the difference between a pluck and a pad:
```js
.attack(0.001).decay(0.12).sustain(0).release(0.05)   // pluck / stab
.attack(0.4).decay(0.2).sustain(0.7).release(1.2)     // slow pad swell
```

**Filter** — `cutoff` (lowpass, the main tone control; lower = darker/warmer), `resonance` (emphasis at the cutoff), `hcutoff` (highpass, thins the low end). A static `sawtooth` is harsh; `.cutoff(700)` makes it a warm bass. **Move** the filter for life: `.cutoff(sine.range(400,2000).slow(4))` sweeps it over 4 cycles.

**Effects** — `room` (reverb mix 0–1) + `size`; `delay` (echo mix) + `delaytime` + `delayfeedback`; `pan` (0 left–1 right); `gain`. Verified working offline. Use reverb to push a pad *back* and a dry signal to pull a lead *forward* — depth is an axis like register.

## 5. Mixing & loudness — so it doesn't clip

There is **no master limiter**. Stacked voices sum, and an `OfflineAudioContext` hard-clips past ±1.0 into ugly distortion. Two rules:

1. **Gain-stage per voice.** Loud things low, quiet things lower. Sane starting points:

   | layer | gain | | layer | gain |
   |---|---|---|---|---|
   | kick / pulse | 0.6–1.0 | | pad / chords | 0.12–0.2 |
   | snare | 0.5–0.8 | | lead / arp | 0.1–0.15 |
   | bass | 0.35–0.5 | | hats | 0.2–0.3 |

2. **Let the renderer normalize.** `render-audio.mjs` measures the true peak and scales to ‑1 dBFS, so the final WAV is loud but never clips — *you* set the **balance** (relative gains), it sets the **level**. If it reports a raw peak way over 1.0 (e.g. >3), your balance is off: turn down whatever dominates, don't rely on the normalizer to fix a muddy mix.

Carve frequency space too: highpass pads off the bass (`.hcutoff(200)`), keep only one thing busy in any register at a time.

## 6. Arrangement — give it an arc over the bars

A reel is 8–16 bars. Don't play everything for all of them. `<>` over the whole length, or stack layers that enter/leave:

```js
// a layer that only plays the back half (mask by cycle):
arp.mask("<0 0 1 1>")             // silent bars 1–2, plays bars 3–4 (repeating)
// build energy: hats get busier each bar
s("hh").euclid("<3 5 7 8>", 8)
// a drop: everything drops out for a bar, then hits — leave a rest in the pulse on bar 4
```

The shape to aim for: **intro** (1–2 bars, sparse — a hook) → **build** (add layers, open the filter, busier hats) → **drop/payoff** (the fullest, loudest moment — land it on a downbeat so the video can cut to it) → **resolve** (thin back out). MOTION.md syncs the visuals to exactly these moments.

## 7. Drums

Use whichever sounds best for the piece. **Sampled drums hit harder** — the template defaults to them — but the punch comes with a license question; synth drums carry none.

**Sampled drums (the template default):** set `SAMPLES = ['github:tidalcycles/dirt-samples']` in `music.mjs`, then `s("bd ~ ~ bd")`, `s("hh*8")`, `s("~ sd")`. Groove the hats with a gain pattern (`s("hh*8").gain("[.3 .55]*4")`) so they swing instead of buzz. **Most dirt-samples banks have no declared license** — fine for personal/most use, but for distribution switch to CC0 `VCSL` or the synth kit below (REFERENCE.md → "Licensing").

**Synth drums (license-free, no network):**
```js
const kick  = note("c1*4").s("sine").decay(0.16).sustain(0).gain(0.9);    // body thump
const snare = s("white").decay(0.2).sustain(0).hcutoff(1500).gain(0.5).struct("~ x ~ x"); // noise crack
const hat   = s("white").decay(0.03).sustain(0).hcutoff(7000).gain(0.3).fast(8);
```

## 8. Four starting recipes

Each is a complete `getPattern` body. Paste, render, then make it yours.

```js
// LO-FI — hazy, ~80 BPM (set CPS≈0.333 in sync.mjs)
const { note, n, stack } = c;
return stack(
  note("c1*4").s("sine").decay(0.18).sustain(0).gain(0.7),
  note("<c2 eb2 f2 g2>").s("sawtooth").cutoff(420).sustain(0.5).gain(0.4),
  n("<0 3 5 4>").scale("C:minor").s("triangle").attack(0.01).release(0.3).gain(0.14).room(0.4),
  n("[0 2 4 7]*2").scale("C:minor").s("sine").gain(0.1).delay(0.3).cutoff(2200),
);
```
```js
// AMBIENT — no beat, slow swells, ~70 BPM (CPS≈0.29)
const { note, stack } = c;
return stack(
  note("<c2 g1>").s("sawtooth").cutoff(300).attack(1).release(2).gain(0.35),
  note("<[c3,g3,d4] [bb2,f3,c4]>").s("supersaw").attack(1.5).release(2.5).cutoff(1200).gain(0.13).room(0.7).size(0.9),
  note("<g4 c5 d5 ~>").s("triangle").attack(0.2).release(1.5).gain(0.1).delay(0.5).delaytime(0.375).room(0.6),
);
```
```js
// DRIVING — tense, 130 BPM (CPS≈0.542). Note the filter SWEEP: a sine LFO over 8 cycles.
const { note, n, stack } = c;
return stack(
  note("c1*4").s("sine").decay(0.14).sustain(0).gain(0.9),
  note("c2*8").s("sawtooth").cutoff(c.sine.range(600, 1800).slow(8)).sustain(0.3).gain(0.4),
  n("0 ~ 3 ~ 5 ~ <7 10> ~").scale("C:minor").s("square").decay(0.1).sustain(0).gain(0.18),
);
```
```js
// CINEMATIC — the template's default mood, 120 BPM (CPS=0.5)
const { note, stack } = c;
return stack(
  note("c1*4").s("sine").decay(0.16).sustain(0).gain(0.6),
  note("<c2 c2 ab1 g1>").s("sawtooth").cutoff(520).sustain(0.4).gain(0.42),
  note("<[c3,eb3,g3] [c3,eb3,g3] [ab2,c3,eb3] [g2,b2,d3]>").s("supersaw").attack(0.06).release(0.7).cutoff(1700).gain(0.13).room(0.55),
  note("eb4 g4 bb4 c5 bb4 g4 eb4 g4").s("triangle").gain(0.12).cutoff(2600).delay(0.3).delaytime(0.1875),
);
```

## Anti-patterns

- **Everything in one octave** → mud. Spread across registers.
- **Every layer at gain 1** → clipping / a wall of noise. Gain-stage (§5).
- **A loop with no `<>` anywhere** → nothing evolves; it's a ringtone. Make at least one layer change across bars.
- **`hh*16` straight** → a sewing machine. Use euclid or gain accents.
- **Reverb on everything** → washy soup. Reverb the pad, keep the bass and kick dry.
- **A synth voice with no duration** → it throws and goes silent (the renderer warns). Always give synths an envelope/length.
- **No rests** → exhausting. Space is a layer.
