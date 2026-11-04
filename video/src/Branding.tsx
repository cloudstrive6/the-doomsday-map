// Channel branding stills: avatar (800x800), banner (2560x1440, safe area 1546x423 centred), watermark (150x150).
import React from 'react';
import {AbsoluteFill, useVideoConfig} from 'remotion';
import {Globe} from './components/Globe';
import {C, COND, MONO} from './theme';
import type {GlobeShot} from './scene';

const globeShot = (scale: number, lat: number, lon: number): GlobeShot => ({
  id: 'brand', type: 'globe', start: 0, end: 10, camera: [{t: 0, lat, lon, scale}], sun: {lat: -18, lon: lon + 95}, graticule: true,
  arcs: [
    {from: [35.78, 54.03], to: [-101.36, 48.42], t0: -10, t1: -1, color: C.red},
    {from: [60.1, 51.1], to: [-95.91, 41.12], t0: -10, t1: -1, color: C.red},
    {from: [45.6, 51.7], to: [-104.87, 41.15], t0: -10, t1: -1, color: C.red},
    {from: [35.0, 72.0], to: [-77.04, 38.9], t0: -10, t1: -1, color: C.orange},
    {from: [150.0, 55.0], to: [-122.72, 47.72], t0: -10, t1: -1, color: C.orange},
  ],
  flashes: [{at: [-101.36, 48.42], t: -10, hold: 0}, {at: [-95.91, 41.12], t: -10, hold: 0}, {at: [-104.87, 41.15], t: -10, hold: 0}, {at: [-77.04, 38.9], t: -10, hold: 0}, {at: [-122.72, 47.72], t: -10, hold: 0}],
});

export const Avatar: React.FC = () => {
  const {width: W} = useVideoConfig();
  return (
    <AbsoluteFill style={{background: C.bg}}>
      <Globe shot={globeShot(W * 0.46, 48, -60)} t={5} />
      <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center'}}>
        <div style={{width: W * 0.62, height: W * 0.62, borderRadius: '50%', border: `${W * 0.012}px solid ${C.red}`, boxShadow: `0 0 ${W * 0.05}px ${C.red}66, inset 0 0 ${W * 0.05}px ${C.red}33`}} />
        <div style={{position: 'absolute', width: W * 0.72, height: 2, background: C.red, opacity: 0.6}} />
        <div style={{position: 'absolute', height: W * 0.72, width: 2, background: C.red, opacity: 0.6}} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

export const Watermark: React.FC = () => {
  const {width: W} = useVideoConfig();
  return (
    <AbsoluteFill style={{background: 'transparent', justifyContent: 'center', alignItems: 'center'}}>
      <div style={{width: W * 0.8, height: W * 0.8, borderRadius: '50%', border: `${W * 0.06}px solid ${C.red}`, boxSizing: 'border-box'}} />
      <div style={{position: 'absolute', width: W * 0.95, height: W * 0.06, background: C.red}} />
      <div style={{position: 'absolute', height: W * 0.95, width: W * 0.06, background: C.red}} />
      <div style={{position: 'absolute', width: W * 0.22, height: W * 0.22, borderRadius: '50%', background: C.red}} />
    </AbsoluteFill>
  );
};

export const Banner: React.FC = () => {
  const {width: W, height: H} = useVideoConfig();
  return (
    <AbsoluteFill style={{background: C.bg}}>
      <div style={{position: 'absolute', left: W * 0.5 - H * 0.02, top: -H * 0.12, width: H * 1.3, height: H * 1.3}}>
        <div style={{position: 'absolute', inset: 0}}>
          <GlobeInBox scale={H * 0.56} />
        </div>
      </div>
      <AbsoluteFill style={{background: 'linear-gradient(90deg, rgba(11,14,18,0.96) 0%, rgba(11,14,18,0.85) 38%, rgba(11,14,18,0.0) 62%)'}} />
      <div style={{position: 'absolute', left: W * 0.5 - 773 + 60, top: H * 0.5 - 211 + 70}}>
        <div style={{fontFamily: MONO, fontSize: 24, letterSpacing: 8, color: C.red}}>REAL DATA · REAL HISTORY · SIMULATED ENDINGS</div>
        <div style={{fontFamily: COND, fontWeight: 800, fontSize: 150, color: C.text, lineHeight: 0.95, marginTop: 22, letterSpacing: 2}}>THE DOOMSDAY<br />MAP</div>
        <div style={{fontFamily: MONO, fontSize: 24, letterSpacing: 3, color: C.dim, marginTop: 26}}>What a nuclear war would look like, minute by minute, on real maps. New scenario every day.</div>
      </div>
    </AbsoluteFill>
  );
};

const GlobeInBox: React.FC<{scale: number}> = ({scale}) => {
  // Globe draws using the composition size; for the banner we render it full-frame and let the gradient cover the left.
  return <Globe shot={globeShot(scale, 42, -75)} t={5} />;
};
