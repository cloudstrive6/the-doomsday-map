// Channel branding stills.
// Avatar 800x800: shown as a circle at 98 px down to 24 px, so the mark must survive at thumbnail size:
//   dark night-side globe, one heavy red reticle (ring plus four ticks), nothing thin.
// Banner 2560x1440: YouTube shows only the centre 1546x423 on every device, so the name and tagline sit inside that
//   box; the globe and arcs fill the wider TV and desktop bands as decoration only.
// Watermark 150x150: the reticle alone on transparency.
import React from 'react';
import {AbsoluteFill, useVideoConfig} from 'remotion';
import {Globe} from './components/Globe';
import {C, COND, MONO} from './theme';
import type {GlobeShot} from './scene';

const ARCS: GlobeShot['arcs'] = [
  {from: [35.78, 54.03], to: [-101.36, 48.42], t0: -10, t1: -1, color: C.red},
  {from: [60.1, 51.1], to: [-95.91, 41.12], t0: -10, t1: -1, color: C.red},
  {from: [45.6, 51.7], to: [-104.87, 41.15], t0: -10, t1: -1, color: C.red},
  {from: [35.0, 72.0], to: [-77.04, 38.9], t0: -10, t1: -1, color: C.orange},
  {from: [150.0, 55.0], to: [-122.72, 47.72], t0: -10, t1: -1, color: C.orange},
];

const globeShot = (scale: number, lat: number, lon: number, opts: Partial<GlobeShot> = {}): GlobeShot => ({
  id: 'brand', type: 'globe', start: 0, end: 10, camera: [{t: 0, lat, lon, scale}], sun: {lat: -18, lon: lon + 100}, graticule: false,
  arcs: ARCS, ...opts,
});

const Reticle: React.FC<{size: number; stroke: number; color?: string; dot?: boolean; glow?: boolean}> = ({size, stroke, color = C.red, dot = true, glow = true}) => {
  const r = size / 2 - stroke;
  const c = size / 2;
  const tick = size * 0.2;
  const gap = r * 0.42;
  return (
    <svg width={size} height={size} style={{position: 'absolute', left: '50%', top: '50%', transform: 'translate(-50%, -50%)', overflow: 'visible',
      filter: glow ? `drop-shadow(0 0 ${stroke * 1.2}px ${color}aa)` : undefined}}>
      <circle cx={c} cy={c} r={r * 0.72} fill="none" stroke={color} strokeWidth={stroke} />
      <line x1={c} y1={c - r - tick * 0.15} x2={c} y2={c - gap} stroke={color} strokeWidth={stroke} strokeLinecap="butt" />
      <line x1={c} y1={c + gap} x2={c} y2={c + r + tick * 0.15} stroke={color} strokeWidth={stroke} strokeLinecap="butt" />
      <line x1={c - r - tick * 0.15} y1={c} x2={c - gap} y2={c} stroke={color} strokeWidth={stroke} strokeLinecap="butt" />
      <line x1={c + gap} y1={c} x2={c + r + tick * 0.15} y2={c} stroke={color} strokeWidth={stroke} strokeLinecap="butt" />
      {dot ? <circle cx={c} cy={c} r={stroke * 0.95} fill={color} /> : null}
    </svg>
  );
};

export const Avatar: React.FC = () => {
  const {width: W} = useVideoConfig();
  return (
    <AbsoluteFill style={{background: '#06080B'}}>
      {/* night side of the globe only: lights and outlines read as "Earth" without competing with the mark */}
      <Globe shot={globeShot(W * 0.5, 40, -95, {sun: {lat: 0, lon: 85}, dim: 0.15, arcs: [], borders: false})} t={5} />
      <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 50%, rgba(6,8,11,0) 30%, rgba(6,8,11,0.55) 70%)'}} />
      <Reticle size={W * 0.8} stroke={W * 0.055} />
    </AbsoluteFill>
  );
};

export const Watermark: React.FC = () => {
  const {width: W} = useVideoConfig();
  return (
    <AbsoluteFill style={{background: 'transparent'}}>
      <Reticle size={W * 0.86} stroke={W * 0.085} glow={false} />
    </AbsoluteFill>
  );
};

export const Banner: React.FC = () => {
  const {width: W, height: H} = useVideoConfig();
  // the all-devices safe box
  const sw = 1546, sh = 423;
  const sx = (W - sw) / 2, sy = (H - sh) / 2;
  const globeR = 520;
  return (
    <AbsoluteFill style={{background: C.bg}}>
      {/* globe sits right of centre so its limb and arcs cross the safe box behind the reticle */}
      <div style={{position: 'absolute', inset: 0, transform: `translateX(${W * 0.4}px)`}}>
        <Globe shot={globeShot(globeR, 44, -82, {graticule: true})} t={5} />
      </div>
      <AbsoluteFill style={{background: `linear-gradient(90deg, ${C.bg} 0%, ${C.bg} 30%, rgba(11,14,18,0.95) 62%, rgba(11,14,18,0.3) 72%, rgba(11,14,18,0) 80%)`}} />
      <div style={{position: 'absolute', left: sx, top: sy, width: sw, height: sh, display: 'flex', alignItems: 'center'}}>
        <div style={{position: 'relative', width: 200, height: 200, marginLeft: 30, flexShrink: 0}}>
          <Reticle size={200} stroke={15} />
        </div>
        <div style={{marginLeft: 44}}>
          <div style={{fontFamily: MONO, fontSize: 24, letterSpacing: 7, color: C.red, fontWeight: 600}}>REAL DATA · REAL HISTORY · SIMULATED ENDINGS</div>
          <div style={{fontFamily: COND, fontWeight: 800, fontSize: 148, color: C.text, lineHeight: 0.95, marginTop: 12, letterSpacing: 3, whiteSpace: 'nowrap'}}>THE DOOMSDAY MAP</div>
          <div style={{fontFamily: COND, fontWeight: 600, fontSize: 38, letterSpacing: 2, color: 'rgba(236,239,242,0.9)', marginTop: 14}}>Nuclear war, minute by minute, on real maps · new scenario every day</div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

export const BannerGuide: React.FC = () => {
  // preview with YouTube's crop guides, for QC only
  const {width: W, height: H} = useVideoConfig();
  return (
    <AbsoluteFill>
      <Banner />
      <div style={{position: 'absolute', left: (W - 1546) / 2, top: (H - 423) / 2, width: 1546, height: 423, border: '4px dashed #3ED6C8'}} />
      <div style={{position: 'absolute', left: 0, top: (H - 423) / 2, width: W, height: 423, border: '3px dashed rgba(255,255,255,0.5)'}} />
    </AbsoluteFill>
  );
};
