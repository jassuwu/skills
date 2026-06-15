import {
  AbsoluteFill, Html5Audio, staticFile, useCurrentFrame, useVideoConfig,
  spring, interpolate, Easing,
} from 'remotion';
import { useAudioData, visualizeAudio } from '@remotion/media-utils';
import { FRAMES_PER_BEAT, FRAMES_PER_BAR } from '../sync.mjs';

// One focal idea, centered, calm palette. Motion is LOCKED to the beat grid (sync.mjs), with the
// expressive accent — the pop on each beat — carried by spring(). Read MOTION.md before editing.
export const Video: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const audio = useAudioData(staticFile('audio.wav'));

  // Bass energy (low FFT bins), 0..1. Guard: useAudioData is null until the file loads.
  let bass = 0;
  if (audio) {
    const bins = visualizeAudio({ audioData: audio, frame, fps, numberOfSamples: 16, smoothing: false });
    bass = Math.min(1, (bins[0] + bins[1]) * 1.6); // low two bins, lightly scaled
  }

  // Pop on every beat: spring restarts at each beat, settling 0→1, so (1-spring) is a decaying punch.
  const beatIndex = Math.floor(frame / FRAMES_PER_BEAT);
  const sinceBeat = frame - beatIndex * FRAMES_PER_BEAT;
  const settle = spring({ frame: sinceBeat, fps, config: { damping: 12, stiffness: 180, mass: 0.7 } });
  const punch = 1 - settle;

  // Eased intro over the first bar; bar index drives a slow hue drift so each section feels distinct.
  const intro = interpolate(frame, [0, FRAMES_PER_BAR], [0, 1], { extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic) });
  const bar = Math.floor(frame / FRAMES_PER_BAR);
  const hue = 250 + bar * 8;

  const scale = (0.9 + 0.1 * intro) * (1 + 0.16 * punch + 0.10 * bass);
  const glow = 40 + 120 * punch + 80 * bass;

  return (
    <AbsoluteFill style={{ backgroundColor: '#07070c', justifyContent: 'center', alignItems: 'center' }}>
      <Html5Audio src={staticFile('audio.wav')} />

      {/* breathing backdrop — barely there, never competes with the focal form */}
      <AbsoluteFill style={{
        background: `radial-gradient(circle at 50% 42%, hsla(${hue},70%,30%,${0.25 + 0.25 * bass}), transparent 60%)`,
      }} />

      {/* the focal form: a ring that pulses on the beat and swells with the bass */}
      <div style={{
        width: 460, height: 460, borderRadius: '50%', opacity: intro,
        border: '2px solid hsla(' + hue + ',80%,80%,0.9)',
        background: `radial-gradient(circle at 42% 36%, hsl(${hue},75%,68%), hsl(${hue + 20},70%,42%))`,
        transform: `scale(${scale})`,
        boxShadow: `0 0 ${glow}px hsla(${hue},85%,65%,0.55)`,
      }} />

      {/* one line of type, animated in, kept in the legible center band (never the bottom 20%) */}
      <div style={{
        position: 'absolute', top: '24%', color: '#eef0ff', opacity: intro,
        fontFamily: 'system-ui, -apple-system, Segoe UI, Roboto, sans-serif',
        fontWeight: 700, fontSize: 64, letterSpacing: '-0.02em',
        transform: `translateY(${(1 - intro) * 24}px)`,
      }}>
        made of code
      </div>
    </AbsoluteFill>
  );
};
