// Regional vector map: Natural Earth 50m countries on an azimuthal equidistant projection centred on the view,
// with highlighted countries, labelled cities, range rings, great-circle lines, a wind-driven plume and a scale bar.
import React, {useLayoutEffect, useMemo, useRef} from 'react';
import {AbsoluteFill, useVideoConfig} from 'remotion';
import {geoAzimuthalEquidistant, geoCircle, geoGraticule, geoGraticule10, geoInterpolate, geoPath, geoCentroid} from 'd3-geo';
import {feature, mesh} from 'topojson-client';
import world50 from 'world-atlas/countries-50m.json';
import usStates from 'us-atlas/states-10m.json';
import type {Ship, LonLat, RegionShot, RegionView} from '../scene';
import {C, MONO, clamp01, ease, easeOut, lerp} from '../theme';
import {getBase} from './baseCache';
import {SafeLabel, useReserve} from './SafeLabel';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const topo = world50 as any;
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const COUNTRIES: any[] = (feature(topo, topo.objects.countries) as any).features;
const BORDERS = mesh(topo, topo.objects.countries, (a: any, b: any) => a !== b);
const COAST = mesh(topo, topo.objects.countries, (a: any, b: any) => a === b);
const GRAT = geoGraticule10();
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const usTopo = usStates as any;
const STATE_BORDERS = mesh(usTopo, usTopo.objects.states, (a: any, b: any) => a !== b);
const EARTH_KM = 6371.0088;
const D2R = Math.PI / 180;

// Static layers (graticule, land, highlights, state lines, coast, borders) are painted once per shot into an offscreen
// canvas at 2x the widest view and scaled per frame, like the city map. SVG for these layers cost about 2 s a frame.
const SUPER = 2;
function paintRegionBase(shot: RegionShot, base: RegionView, W: number, H: number, key: string): HTMLCanvasElement {
  return getBase('region|' + key, () => paintRegion(shot, base, W, H));
}
// Bright theme (2026-11-12) for map thumbnails: real coastlines and borders on a blue sea and sand land, so a "map"
// thumbnail is accurate (an AI-drawn map put Iran's mountain in the Hindu Kush) and bright enough for the feed.
export const MAP_THEMES = {
  dark: {sea: C.bg, grat: 'rgba(140,180,200,0.13)', land: C.land, states: 'rgba(150,185,200,0.28)', coast: 'rgba(170,215,225,0.5)', border: C.border, hiAlpha: '33'},
  bright: {sea: '#2C6CA8', grat: 'rgba(255,255,255,0.10)', land: '#E6DBBF', states: 'rgba(90,80,60,0.35)', coast: 'rgba(16,36,56,0.65)', border: 'rgba(80,66,50,0.7)', hiAlpha: '66'},
};
function paintRegion(shot: RegionShot, base: RegionView, W: number, H: number): HTMLCanvasElement {
  const T = MAP_THEMES[shot.theme ?? 'dark'];
  const bw = W * SUPER, bh = H * SUPER;
  const cv = document.createElement('canvas');
  cv.width = bw; cv.height = bh;
  const ctx = cv.getContext('2d', {willReadFrequently: true})!;
  const proj = makeProjection(base, bw, bh);
  const path = geoPath(proj, ctx);
  ctx.fillStyle = T.sea; ctx.fillRect(0, 0, bw, bh);
  const hiMap = new Map((shot.highlight ?? []).map((h) => [h.iso, h]));
  for (const c of COUNTRIES) {
    // every country is drawn: a centroid test drops large countries (the US, Russia) when zoomed into one corner
    const h = hiMap.get(String(c.id));
    ctx.beginPath(); path(c); ctx.fillStyle = T.land; ctx.fill();
    if (h) { ctx.fillStyle = h.fill ?? h.color + T.hiAlpha; ctx.fill(); }   // tint over land, not over the sea colour
  }
  // HUD grid over land and sea, finer when zoomed in (2026-11-13): inland views have no coast or border in frame, so an
  // empty map showed nothing moving and failed the freeze check (006 c1-sites, central Iran at 500 km). It moves with
  // the camera. (Until then the grid was painted under the land and only showed at sea.)
  const step = base.widthKm < 1100 ? 1 : base.widthKm < 2600 ? 2 : base.widthKm < 6000 ? 5 : 10;
  ctx.beginPath(); path(step === 10 ? GRAT : geoGraticule().step([step, step])()); ctx.strokeStyle = T.grat;
  ctx.lineWidth = SUPER; ctx.stroke();
  const c0 = base.center;
  if (base.widthKm < 8000 && c0[0] < -60 && c0[0] > -170 && c0[1] > 22 && c0[1] < 72) {
    ctx.beginPath(); path(STATE_BORDERS); ctx.strokeStyle = T.states; ctx.lineWidth = 0.9 * SUPER; ctx.stroke();
  }
  ctx.beginPath(); path(COAST); ctx.strokeStyle = T.coast; ctx.lineWidth = 1.3 * SUPER; ctx.stroke();
  ctx.beginPath(); path(BORDERS); ctx.strokeStyle = T.border; ctx.lineWidth = 1 * SUPER; ctx.stroke();
  for (const h of shot.highlight ?? []) {
    const c = COUNTRIES.find((x) => String(x.id) === h.iso);
    if (!c) continue;
    ctx.save(); ctx.shadowColor = h.color; ctx.shadowBlur = 5 * SUPER;
    ctx.beginPath(); path(c); ctx.strokeStyle = h.color; ctx.lineWidth = 2.2 * SUPER; ctx.stroke(); ctx.restore();
  }
  return cv;
}

const mix = (a: RegionView, b: RegionView, u: number): RegionView =>
  ({center: [lerp(a.center[0], b.center[0], u), lerp(a.center[1], b.center[1], u)], widthKm: Math.exp(lerp(Math.log(a.widthKm), Math.log(b.widthKm), u))});

// Camera keys (2026-11-10): `camera: [{t, center, widthKm}, ...]` gives a region or city shot several moves (a pull-out,
// a hold, a pan to the next place) instead of one view-to-zoomTo ease. Each leg eases; before the first key the view
// holds at it, after the last key it keeps a slow push so the shot never freezes.
export type CamKey = RegionView & {t: number};
// 2026-11-12: 006 failed QC with 4 to 7 s freezes: the director padded shots with keys that hold one view (to clear the
// pace check), and a hold between identical keys stood perfectly still. Keyed shots now always carry the same gentle
// push the automatic drift gives unkeyed shots (1.4% a second, at most 20%), on top of the keyed moves; and a first leg
// shorter than 0.25 s (a snap zoom that reads as a jump) is dropped, so the shot opens on the second key.
const PUSH = 0.014;
export function viewAt(a: RegionView, b: RegionView | undefined, t: number, dur: number, keys?: CamKey[]): RegionView {
  if (keys && keys.length >= 2) {
    let k = [...keys].sort((x, y) => x.t - y.t);
    while (k.length > 2 && k[1].t - k[0].t < 0.25) k = [{...k[1], t: k[0].t}, ...k.slice(2)];
    const push = Math.max(0.8, 1 - PUSH * t);
    // and a slow eastward pan (0.5% of the view width a second) that keeps going after the push reaches its cap
    const at = (v: RegionView): RegionView => {
      const km = v.widthKm * 0.005 * t;
      return {center: [v.center[0] + km / (111.2 * Math.max(0.2, Math.cos(v.center[1] * D2R))), v.center[1]], widthKm: v.widthKm * push};
    };
    if (t <= k[0].t) return at(k[0]);
    for (let i = 1; i < k.length; i++) {
      if (t <= k[i].t) return at(mix(k[i - 1], k[i], ease(clamp01((t - k[i - 1].t) / Math.max(0.01, k[i].t - k[i - 1].t)))));
    }
    return at(k[k.length - 1]);
  }
  if (!b) return a;
  return mix(a, b, ease(clamp01(t / Math.max(0.01, dur))));
}

// The painted base covers the view at 1.6 to 3.2x its width, in power-of-two steps, centred on a snapped point near the
// view centre. Deep zooms and long pans repaint at the right scale instead of stretching one wide canvas.
export function baseFor(view: RegionView, width?: number): RegionView {
  const w = width ?? Math.pow(2, Math.ceil(Math.log2(view.widthKm * 1.6)));
  const stepKm = w / 8;
  const latStep = stepKm / 111.2;
  const lat = Math.max(-85, Math.min(85, Math.round(view.center[1] / latStep) * latStep));
  const lonStep = stepKm / (111.2 * Math.max(0.2, Math.cos(lat * Math.PI / 180)));
  return {center: [Math.round(view.center[0] / lonStep) * lonStep, lat], widthKm: w};
}

export function makeProjection(view: RegionView, W: number, H: number) {
  const scale = W / (view.widthKm / EARTH_KM);  // px per radian of arc from the centre
  return geoAzimuthalEquidistant().rotate([-view.center[0], -view.center[1]]).scale(scale).translate([W / 2, H / 2]).clipAngle(150);
}

export function destination(from: LonLat, bearingDeg: number, km: number): LonLat {
  const δ = km / EARTH_KM, θ = bearingDeg * D2R;
  const φ1 = from[1] * D2R, λ1 = from[0] * D2R;
  const φ2 = Math.asin(Math.sin(φ1) * Math.cos(δ) + Math.cos(φ1) * Math.sin(δ) * Math.cos(θ));
  const λ2 = λ1 + Math.atan2(Math.sin(θ) * Math.sin(δ) * Math.cos(φ1), Math.cos(δ) - Math.sin(φ1) * Math.sin(φ2));
  return [((λ2 / D2R + 540) % 360) - 180, φ2 / D2R];
}

export function plumePolygon(at: LonLat, bearing: number, lengthKm: number, widthKm: number, k: number) {
  // teardrop: narrow at the source, widening downwind; k = growth 0..1
  const L = lengthKm * k, Wd = widthKm * (0.3 + 0.7 * k);
  const pts: LonLat[] = [];
  const N = 24;
  for (let i = 0; i <= N; i++) {
    const s = i / N;
    const d = L * s;
    const half = Wd * 0.5 * Math.pow(Math.sin(Math.PI * Math.min(1, s * 0.8 + 0.1)), 0.7);
    pts.push(destination(destination(at, bearing, d), bearing + 90, half));
  }
  for (let i = N; i >= 0; i--) {
    const s = i / N;
    const d = L * s;
    const half = Wd * 0.5 * Math.pow(Math.sin(Math.PI * Math.min(1, s * 0.8 + 0.1)), 0.7);
    pts.push(destination(destination(at, bearing, d), bearing - 90, half));
  }
  pts.push(pts[0]);
  pts.reverse(); // d3-geo: exterior rings wind clockwise
  return {type: 'Polygon', coordinates: [pts]} as const;
}

const SHIP_COLOR: Record<string, string> = {pla: C.red, coastguard: C.orange, us: C.teal, ally: '#7FB2FF', cargo: 'rgba(236,239,242,0.75)', tanker: C.amber};

// Position and heading of a ship at time t along its path (piecewise linear in screen space, even speed).
function shipAt(sh: Ship, t: number, pt: (ll: LonLat) => [number, number] | null): {p: [number, number]; ang: number; trail: [number, number][]} | null {
  const pts = sh.path.map(pt).filter(Boolean) as [number, number][];
  if (!pts.length) return null;
  if (pts.length === 1) return {p: pts[0], ang: 0, trail: []};
  const segs = pts.slice(1).map((q, i) => Math.hypot(q[0] - pts[i][0], q[1] - pts[i][1]));
  const total = segs.reduce((a, b) => a + b, 0) || 1;
  const t0 = sh.t0 ?? 0, t1 = sh.t1 ?? t0 + 1;
  const k = clamp01((t - t0) / Math.max(0.01, t1 - t0));
  const at = (d: number): [number, number, number] => {
    let acc = 0;
    for (let i = 0; i < segs.length; i++) {
      if (acc + segs[i] >= d || i === segs.length - 1) {
        const f = segs[i] ? clamp01((d - acc) / segs[i]) : 0;
        const a = pts[i], b = pts[i + 1];
        return [a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f, Math.atan2(b[1] - a[1], b[0] - a[0])];
      }
      acc += segs[i];
    }
    return [pts[0][0], pts[0][1], 0];
  };
  const d = k * total;
  const [x, y, ang] = at(d);
  const trail: [number, number][] = [];
  if (k > 0 && k < 1) for (let j = 1; j <= 6; j++) { const q = at(Math.max(0, d - j * 9)); trail.push([q[0], q[1]]); }
  return {p: [x, y], ang, trail};
}


export const RegionMap: React.FC<{shot: RegionShot; t: number}> = ({shot, t}) => {
  const {width: W, height: H} = useVideoConfig();
  const reserve = useReserve();
  if (shot.legend?.length) {
    const fs = H > W ? 34 : 22;
    const lw = Math.max(...shot.legend.map((l) => l.text.length)) * (fs * 0.6 + 1.5) + 16 + 12 + 34;
    const lh = shot.legend.length * (fs * 1.25 + 8) + 26;
    const bottom = shot.caption ? 150 : 76;
    reserve('legend', 40, H - bottom - lh - 8, 48 + lw + 8, H - bottom + 8);
  }
  const dur = shot.end - shot.start;
  const view = viewAt(shot.view, shot.zoomTo, t, dur, shot.camera);
  const proj = useMemo(() => makeProjection(view, W, H), [view.center[0], view.center[1], view.widthKm, W, H]);
  const path = useMemo(() => geoPath(proj), [proj]);
  const cap = !!shot.caption;
  const pxPerKm = W / view.widthKm;
  const scaleKm = [10, 20, 50, 100, 200, 500, 1000, 2000].find((k) => k * pxPerKm > 140) ?? 2000;
  const circle = geoCircle();
  const pt = (ll: LonLat) => proj(ll) as [number, number] | null;
  const bv = baseFor(view);
  const baseView: RegionView = useMemo(() => bv, [bv.center[0], bv.center[1], bv.widthKm]);
  const baseKey = `${shot.id}|${W}x${H}|${baseView.widthKm}|${baseView.center[0].toFixed(4)},${baseView.center[1].toFixed(4)}`;
  const ref = useRef<HTMLCanvasElement>(null);
  useLayoutEffect(() => {
    const cv = ref.current;
    if (!cv) return;
    const ctx = cv.getContext('2d')!;
    const base = paintRegionBase(shot, baseView, W, H, baseKey);
    const pb = makeProjection(baseView, W * SUPER, H * SUPER);
    const q = pb(view.center) as [number, number];
    const k = baseView.widthKm / (SUPER * view.widthKm);
    ctx.fillStyle = MAP_THEMES[shot.theme ?? 'dark'].sea; ctx.fillRect(0, 0, W, H);
    ctx.imageSmoothingEnabled = true; ctx.imageSmoothingQuality = 'high';
    ctx.drawImage(base, W / 2 - q[0] * k, H / 2 - q[1] * k, W * SUPER * k, H * SUPER * k);
    const r = baseView.widthKm / (1.6 * view.widthKm);   // 1 to 2 inside an octave; the switch to the finer base is at 2
    if (r > 1.6) {
      const fine: RegionView = baseFor({center: view.center, widthKm: view.widthKm * 1.0001}, baseView.widthKm / 2);
      const fb = paintRegionBase(shot, fine, W, H, `${shot.id}|${W}x${H}|${fine.widthKm}|${fine.center[0].toFixed(4)},${fine.center[1].toFixed(4)}`);
      const pf = makeProjection(fine, W * SUPER, H * SUPER);
      const qf = pf(view.center) as [number, number];
      const kf = fine.widthKm / (SUPER * view.widthKm);
      ctx.globalAlpha = clamp01((r - 1.6) / 0.4);
      ctx.drawImage(fb, W / 2 - qf[0] * kf, H / 2 - qf[1] * kf, W * SUPER * kf, H * SUPER * kf);
      ctx.globalAlpha = 1;
    }
  }, [shot, baseView, baseKey, view.center[0], view.center[1], view.widthKm, W, H]);
  return (
    <AbsoluteFill style={{background: MAP_THEMES[shot.theme ?? 'dark'].sea}}>
      <canvas ref={ref} width={W} height={H} style={{position: 'absolute', inset: 0, width: '100%', height: '100%'}} />
      <svg width={W} height={H} style={{position: 'absolute', inset: 0}}>
        <defs>
          <radialGradient id="plumeG"><stop offset="0" stopColor={C.amber} stopOpacity="0.55" /><stop offset="1" stopColor={C.amber} stopOpacity="0.05" /></radialGradient>
          <filter id="soft"><feGaussianBlur stdDeviation="6" /></filter>
          <filter id="glow"><feGaussianBlur stdDeviation="2.5" result="b" /><feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge></filter>
        </defs>
        {(shot.zones ?? []).map((z, i) => {
          if (z.t !== undefined && t < z.t) return null;
          const k = z.t === undefined ? 1 : easeOut(clamp01((t - z.t) / 0.6));
          const ps = z.points.map(pt).filter(Boolean) as [number, number][];
          if (ps.length < 3) return null;
          const d = 'M' + ps.map((q) => `${q[0].toFixed(1)},${q[1].toFixed(1)}`).join('L') + 'Z';
          const col = z.color ?? C.red;
          const pulse = z.pulse ? 0.75 + 0.25 * Math.sin(t * 3) : 1;
          return <path key={`z${i}`} d={d} fill={col} fillOpacity={0.16 * k * pulse} stroke={col} strokeOpacity={0.9 * k} strokeWidth={1.8} strokeDasharray="7 5" />;
        })}
        {(shot.rings ?? []).map((r, i) => {
          const k = r.t === undefined ? 1 : easeOut(clamp01((t - r.t) / 0.9));
          if (k <= 0) return null;
          const c = circle.center(r.at).radius((r.km * k) / EARTH_KM / D2R)();
          return <path key={i} d={path(c) ?? ''} fill={(r.color ?? C.red) + '14'} stroke={r.color ?? C.red} strokeWidth={1.6} strokeDasharray={r.dashed === false ? undefined : '8 6'} />;
        })}
        {(shot.lines ?? []).map((l, i) => {
          const k = l.t0 === undefined ? 1 : easeOut(clamp01((t - l.t0) / Math.max(0.1, (l.t1 ?? l.t0 + 1) - l.t0)));
          if (k <= 0) return null;
          const interp = geoInterpolate(l.from, l.to);
          const coords = Array.from({length: 65}, (_, j) => interp((j / 64) * k));
          return <path key={i} d={path({type: 'LineString', coordinates: coords}) ?? ''} fill="none" stroke={l.color ?? C.teal} strokeWidth={l.width ?? 2} strokeDasharray={l.dashed ? '10 8' : undefined} filter="url(#glow)" />;
        })}
        {shot.plume && t >= shot.plume.t0 ? (() => {
          const k = easeOut(clamp01((t - shot.plume.t0) / Math.max(0.1, shot.plume.t1 - shot.plume.t0)));
          const poly = plumePolygon(shot.plume.at, shot.plume.bearing, shot.plume.lengthKm, shot.plume.widthKm, k);
          return <path d={path(poly as any) ?? ''} fill={shot.plume.color ?? C.amber} fillOpacity={0.32} filter="url(#soft)" />;
        })() : null}
        {(shot.ships ?? []).map((sh, i) => {
          if (sh.t !== undefined && t < sh.t) return null;
          const st = shipAt(sh, t, pt);
          if (!st) return null;
          const col = sh.color ?? SHIP_COLOR[sh.kind ?? 'cargo'];
          const sz = sh.size ?? (sh.kind === 'cargo' || sh.kind === 'tanker' ? 9 : 11);
          const appear = sh.t === undefined ? 1 : clamp01((t - sh.t) / 0.4);
          const sunk = sh.sunkAt !== undefined && t >= sh.sunkAt ? clamp01((t - sh.sunkAt) / 1.2) : 0;
          const [x, y] = st.p;
          const c = Math.cos(st.ang), s2 = Math.sin(st.ang);
          const P = (fx: number, fy: number) => `${(x + fx * c - fy * s2).toFixed(1)},${(y + fx * s2 + fy * c).toFixed(1)}`;
          return (
            <g key={`s${i}`} opacity={appear * (1 - sunk)}>
              {sh.wake !== false && st.trail.length ? <polyline points={[st.p, ...st.trail].map((q) => q.join(',')).join(' ')} fill="none" stroke={col} strokeOpacity={0.35} strokeWidth={1.4} /> : null}
              <polygon points={`${P(sz * 1.3, 0)} ${P(-sz * 0.9, sz * 0.75)} ${P(-sz * 0.45, 0)} ${P(-sz * 0.9, -sz * 0.75)}`} fill={col} filter="url(#glow)" />
              {sunk > 0 ? <circle cx={x} cy={y} r={6 + 26 * sunk} fill="none" stroke={C.amber} strokeOpacity={1 - sunk} strokeWidth={2} /> : null}
            </g>
          );
        })}
        {(shot.cities ?? []).map((m, i) => {
          const p = pt(m.at);
          if (!p || (m.t !== undefined && t < m.t)) return null;
          const col = m.color ?? C.text;
          const size = m.size ?? 4;
          return (
            <g key={i}>
              {m.kind === 'target' || m.kind === 'ring' ? <circle cx={p[0]} cy={p[1]} r={size * 2.6} fill="none" stroke={col} strokeWidth={1.2} /> : null}
              {m.kind === 'base' || m.kind === 'sub' ? <rect x={p[0] - size} y={p[1] - size} width={size * 2} height={size * 2} fill={col} /> : <circle cx={p[0]} cy={p[1]} r={size} fill={col} filter="url(#glow)" />}
            </g>
          );
        })}
      </svg>
      {(shot.cities ?? []).map((m, i) => {
        const p = pt(m.at);
        if (!p || !m.label) return null;
        return <SafeLabel key={`l${i}`} x={p[0]} y={p[1]} text={m.label} color={m.color} caption={cap} a={m.t === undefined ? 1 : t < m.t ? 0 : ease(clamp01((t - m.t) / 0.4))} />;
      })}
      {(shot.rings ?? []).map((r, i) => {
        if (!r.label) return null;
        const ra = r.t !== undefined && t < r.t + 0.5 ? 0 : 1;
        const edge = pt(destination(r.at, 40 + i * 26, r.km));
        const small = r.km * pxPerKm < 60;
        return edge ? <SafeLabel key={`r${i}`} x={edge[0]} y={edge[1]} text={r.label} color={r.color ?? C.red} caption={cap} size={22} a={ra} dy={small ? -10 - (3 - i) * 30 : -10} /> : null;
      })}
      {(shot.zones ?? []).map((z, i) => {
        if (!z.label) return null;
        const za = z.t !== undefined && t < z.t + 0.3 ? 0 : 1;
        const ps = z.points.map(pt).filter(Boolean) as [number, number][];
        if (!ps.length) return null;
        const cx = ps.reduce((a, q) => a + q[0], 0) / ps.length, cy = ps.reduce((a, q) => a + q[1], 0) / ps.length;
        return <SafeLabel key={`zl${i}`} x={cx} y={cy} text={z.label} color={z.color ?? C.red} caption={cap} align="center" dy={0} a={za} />;
      })}
      {(shot.ships ?? []).map((sh, i) => {
        if (!sh.label || (sh.t !== undefined && t < sh.t) || (sh.sunkAt !== undefined && t > sh.sunkAt + 0.6)) return null;
        const st = shipAt(sh, t, pt);
        return st ? <SafeLabel key={`sl${i}`} x={st.p[0]} y={st.p[1]} text={sh.label} color={sh.color ?? SHIP_COLOR[sh.kind ?? 'cargo']} caption={cap} dy={22} /> : null;
      })}
      {(shot.labels ?? []).map((l, i) => {
        const p = pt(l.at);
        if (!p || (l.until !== undefined && t > l.until + 0.3)) return null;
        return <SafeLabel key={`t${i}`} x={p[0]} y={p[1]} text={l.text} color={l.color ?? C.dim} caption={cap} align="center" dy={26} a={(l.t === undefined ? 1 : t < l.t ? 0 : ease(clamp01((t - l.t) / 0.4))) * (l.until === undefined ? 1 : 1 - clamp01((t - l.until) / 0.3))} />;
      })}
      {(shot.countryLabels ?? []).map((cl, i) => {
        const c = COUNTRIES.find((x) => String(x.id) === cl.iso);
        if (!c) return null;
        const p = pt(geoCentroid(c));
        return p ? <SafeLabel key={`c${i}`} x={p[0]} y={p[1]} text={cl.text} color={cl.color ?? 'rgba(236,239,242,0.55)'} caption={cap} size={cl.size ?? 34} align="center" dy={0} plate={false} weight={700} /> : null;
      })}
      {shot.plume?.label && t > shot.plume.t0 + 0.6 ? (() => {
        const p = pt(destination(shot.plume!.at, shot.plume!.bearing, shot.plume!.lengthKm * 0.55));
        return p ? <SafeLabel x={p[0]} y={p[1]} text={shot.plume!.label!} color={C.amber} caption={cap} align="center" dy={-10} /> : null;
      })() : null}
      {shot.burst && t >= shot.burst.t ? (() => {
        const b = shot.burst!;
        const dt = t - b.t;
        const p = pt(b.at);
        // flash v2 (2026-11-10): full white for the first frames, then the fireball grows and cools from white to
        // orange over several seconds while a shock ring runs outward; the shake and afterglow live in Episode.tsx
        const white = dt < 0.06 ? 1 : Math.max(0, 1 - (dt - 0.06) / 0.85) ** 2;
        const grow = 0.55 + 0.6 * easeOut(clamp01(dt / 1.6));
        const rPx = Math.max(14, b.km * pxPerKm) * grow;
        const glow = Math.max(0, 1 - dt / (b.fade ?? 7));
        const cool = clamp01(dt / 4);
        const boil = 1 + 0.04 * Math.sin(dt * 7.3);
        const shockK = clamp01(dt / 1.8);
        const shockR = rPx * (1.2 + 9 * easeOut(shockK));
        const g1 = Math.round(255 - 40 * cool), b1 = Math.round(240 - 140 * cool), g2 = Math.round(210 - 60 * cool), b2 = Math.round(120 - 60 * cool);
        return (
          <>
            {p ? (
              <div style={{position: 'absolute', left: p[0] - rPx * 3 * boil, top: p[1] - rPx * 3 * boil, width: rPx * 6 * boil, height: rPx * 6 * boil, borderRadius: '50%', pointerEvents: 'none',
                background: `radial-gradient(circle, rgba(255,${g1},${b1},${0.97 * glow}) 0%, rgba(255,${g2},${b2},${0.88 * glow}) 18%, rgba(255,122,26,${0.55 * glow}) 34%, rgba(255,59,59,${0.2 * glow}) 55%, rgba(0,0,0,0) 70%)`}} />
            ) : null}
            {p && shockK < 1 ? (
              <div style={{position: 'absolute', left: p[0] - shockR, top: p[1] - shockR, width: shockR * 2, height: shockR * 2, borderRadius: '50%', pointerEvents: 'none',
                border: `${Math.max(2, 6 * (1 - shockK)).toFixed(1)}px solid rgba(255,236,200,${(0.85 * (1 - shockK)).toFixed(3)})`, boxShadow: `0 0 ${(24 * (1 - shockK)).toFixed(1)}px rgba(255,170,90,${(0.6 * (1 - shockK)).toFixed(3)})`}} />
            ) : null}
            {white > 0 ? <AbsoluteFill style={{background: '#FFFDF4', opacity: white}} /> : null}
          </>
        );
      })() : null}
      {shot.legend?.length ? (
        <div style={{position: 'absolute', left: 48, bottom: shot.caption ? 150 : 76, background: 'rgba(8,10,14,0.78)', padding: '12px 16px', border: '1px solid rgba(236,239,242,0.12)'}}>
          {shot.legend.map((l, i) => (
            <div key={i} style={{display: 'flex', alignItems: 'center', gap: 12, fontFamily: MONO, fontSize: H > W ? 34 : 22, color: C.text, letterSpacing: 1.5, textTransform: 'uppercase', marginBottom: i < shot.legend!.length - 1 ? 8 : 0}}>
              <div style={{width: 16, height: 16, background: l.color ?? C.red}} />{l.text}
            </div>
          ))}
        </div>
      ) : null}
      {shot.scaleBar !== false ? (
        <div style={{position: 'absolute', right: 48, bottom: 44, display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 6}}>
          <div style={{fontFamily: MONO, fontSize: 18, letterSpacing: 2, color: C.dim}}>{scaleKm} KM</div>
          <div style={{width: scaleKm * pxPerKm, height: 2, background: C.dim, boxShadow: '0 0 4px rgba(0,0,0,0.9)'}} />
        </div>
      ) : null}
    </AbsoluteFill>
  );
};
