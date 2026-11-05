// Regional vector map: Natural Earth 50m countries on an azimuthal equidistant projection centred on the view,
// with highlighted countries, labelled cities, range rings, great-circle lines, a wind-driven plume and a scale bar.
import React, {useLayoutEffect, useMemo, useRef} from 'react';
import {AbsoluteFill, useVideoConfig} from 'remotion';
import {geoAzimuthalEquidistant, geoCircle, geoGraticule10, geoInterpolate, geoPath, geoCentroid} from 'd3-geo';
import {feature, mesh} from 'topojson-client';
import world50 from 'world-atlas/countries-50m.json';
import usStates from 'us-atlas/states-10m.json';
import type {Ship, LonLat, RegionShot, RegionView} from '../scene';
import {C, MONO, clamp01, ease, easeOut, lerp} from '../theme';
import {getBase} from './baseCache';

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
function paintRegion(shot: RegionShot, base: RegionView, W: number, H: number): HTMLCanvasElement {
  const bw = W * SUPER, bh = H * SUPER;
  const cv = document.createElement('canvas');
  cv.width = bw; cv.height = bh;
  const ctx = cv.getContext('2d', {willReadFrequently: true})!;
  const proj = makeProjection(base, bw, bh);
  const path = geoPath(proj, ctx);
  ctx.fillStyle = C.bg; ctx.fillRect(0, 0, bw, bh);
  ctx.beginPath(); path(GRAT); ctx.strokeStyle = 'rgba(140,180,200,0.07)'; ctx.lineWidth = SUPER; ctx.stroke();
  const hiMap = new Map((shot.highlight ?? []).map((h) => [h.iso, h]));
  for (const c of COUNTRIES) {
    // every country is drawn: a centroid test drops large countries (the US, Russia) when zoomed into one corner
    const h = hiMap.get(String(c.id));
    ctx.beginPath(); path(c); ctx.fillStyle = h ? (h.fill ?? h.color + '33') : C.land; ctx.fill();
  }
  const c0 = base.center;
  if (base.widthKm < 8000 && c0[0] < -60 && c0[0] > -170 && c0[1] > 22 && c0[1] < 72) {
    ctx.beginPath(); path(STATE_BORDERS); ctx.strokeStyle = 'rgba(150,185,200,0.28)'; ctx.lineWidth = 0.9 * SUPER; ctx.stroke();
  }
  ctx.beginPath(); path(COAST); ctx.strokeStyle = 'rgba(170,215,225,0.5)'; ctx.lineWidth = 1.3 * SUPER; ctx.stroke();
  ctx.beginPath(); path(BORDERS); ctx.strokeStyle = C.border; ctx.lineWidth = 1 * SUPER; ctx.stroke();
  for (const h of shot.highlight ?? []) {
    const c = COUNTRIES.find((x) => String(x.id) === h.iso);
    if (!c) continue;
    ctx.save(); ctx.shadowColor = h.color; ctx.shadowBlur = 5 * SUPER;
    ctx.beginPath(); path(c); ctx.strokeStyle = h.color; ctx.lineWidth = 2.2 * SUPER; ctx.stroke(); ctx.restore();
  }
  return cv;
}

export function viewAt(a: RegionView, b: RegionView | undefined, t: number, dur: number): RegionView {
  if (!b) return a;
  const u = ease(clamp01(t / Math.max(0.01, dur)));
  return {center: [lerp(a.center[0], b.center[0], u), lerp(a.center[1], b.center[1], u)], widthKm: Math.exp(lerp(Math.log(a.widthKm), Math.log(b.widthKm), u))};
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

const Label: React.FC<{x: number; y: number; text: string; color?: string; a?: number; size?: number; dx?: number; dy?: number}> = ({x, y, text, color, a = 1, size = 18, dx = 12, dy = -10}) => (
  <div style={{position: 'absolute', left: x + dx, top: y + dy, fontFamily: MONO, fontSize: size, letterSpacing: 1.5, color: color ?? C.text, opacity: a, whiteSpace: 'nowrap',
    textShadow: '0 0 6px rgba(0,0,0,0.95), 0 0 2px rgba(0,0,0,1)', textTransform: 'uppercase'}}>{text}</div>
);

export const RegionMap: React.FC<{shot: RegionShot; t: number}> = ({shot, t}) => {
  const {width: W, height: H} = useVideoConfig();
  const dur = shot.end - shot.start;
  const view = viewAt(shot.view, shot.zoomTo, t, dur);
  const proj = useMemo(() => makeProjection(view, W, H), [view.center[0], view.center[1], view.widthKm, W, H]);
  const path = useMemo(() => geoPath(proj), [proj]);
  const pxPerKm = W / view.widthKm;
  const scaleKm = [10, 20, 50, 100, 200, 500, 1000, 2000].find((k) => k * pxPerKm > 140) ?? 2000;
  const circle = geoCircle();
  const pt = (ll: LonLat) => proj(ll) as [number, number] | null;
  const baseView: RegionView = useMemo(() => ({center: shot.view.center, widthKm: Math.max(shot.view.widthKm, shot.zoomTo?.widthKm ?? 0) * 1.12}), [shot.view, shot.zoomTo]);
  const baseKey = `${shot.id}|${W}x${H}|${baseView.widthKm.toFixed(1)}`;
  const ref = useRef<HTMLCanvasElement>(null);
  useLayoutEffect(() => {
    const cv = ref.current;
    if (!cv) return;
    const ctx = cv.getContext('2d')!;
    const base = paintRegionBase(shot, baseView, W, H, baseKey);
    const pb = makeProjection(baseView, W * SUPER, H * SUPER);
    const q = pb(view.center) as [number, number];
    const k = baseView.widthKm / (SUPER * view.widthKm);
    ctx.fillStyle = C.bg; ctx.fillRect(0, 0, W, H);
    ctx.imageSmoothingEnabled = true; ctx.imageSmoothingQuality = 'high';
    ctx.drawImage(base, W / 2 - q[0] * k, H / 2 - q[1] * k, W * SUPER * k, H * SUPER * k);
  }, [shot, baseView, baseKey, view.center[0], view.center[1], view.widthKm, W, H]);
  return (
    <AbsoluteFill style={{background: C.bg}}>
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
          return <path key={i} d={path({type: 'LineString', coordinates: coords}) ?? ''} fill="none" stroke={l.color ?? C.teal} strokeWidth={2} strokeDasharray={l.dashed ? '10 8' : undefined} filter="url(#glow)" />;
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
        if (!p || !m.label || (m.t !== undefined && t < m.t)) return null;
        return <Label key={`l${i}`} x={p[0]} y={p[1]} text={m.label} color={m.color} a={m.t === undefined ? 1 : ease(clamp01((t - m.t) / 0.4))} />;
      })}
      {(shot.rings ?? []).map((r, i) => {
        if (!r.label || (r.t !== undefined && t < r.t + 0.5)) return null;
        const edge = pt(destination(r.at, 40 + i * 26, r.km));
        const small = r.km * pxPerKm < 60;
        return edge ? <Label key={`r${i}`} x={edge[0]} y={edge[1]} text={r.label} color={r.color ?? C.red} size={15} dy={small ? -10 - (3 - i) * 20 : -10} /> : null;
      })}
      {(shot.zones ?? []).map((z, i) => {
        if (!z.label || (z.t !== undefined && t < z.t + 0.3)) return null;
        const ps = z.points.map(pt).filter(Boolean) as [number, number][];
        if (!ps.length) return null;
        const cx = ps.reduce((a, q) => a + q[0], 0) / ps.length, cy = ps.reduce((a, q) => a + q[1], 0) / ps.length;
        return <Label key={`zl${i}`} x={cx} y={cy} text={z.label} color={z.color ?? C.red} size={14} dx={-z.label.length * 4.1} dy={-8} />;
      })}
      {(shot.ships ?? []).map((sh, i) => {
        if (!sh.label || (sh.t !== undefined && t < sh.t) || (sh.sunkAt !== undefined && t > sh.sunkAt + 0.6)) return null;
        const st = shipAt(sh, t, pt);
        return st ? <Label key={`sl${i}`} x={st.p[0]} y={st.p[1]} text={sh.label} color={sh.color ?? SHIP_COLOR[sh.kind ?? 'cargo']} size={14} dy={6} /> : null;
      })}
      {(shot.labels ?? []).map((l, i) => {
        const p = pt(l.at);
        if (!p || (l.t !== undefined && t < l.t)) return null;
        return <Label key={`t${i}`} x={p[0]} y={p[1]} text={l.text} color={l.color ?? C.dim} size={16} dx={-l.text.length * 4.6} dy={8} />;
      })}
      {(shot.countryLabels ?? []).map((cl, i) => {
        const c = COUNTRIES.find((x) => String(x.id) === cl.iso);
        if (!c) return null;
        const p = pt(geoCentroid(c));
        return p ? <Label key={`c${i}`} x={p[0]} y={p[1]} text={cl.text} color={cl.color ?? 'rgba(236,239,242,0.45)'} size={17} dx={-cl.text.length * 5.5} dy={-9} /> : null;
      })}
      {shot.plume?.label && t > shot.plume.t0 + 0.6 ? (() => {
        const p = pt(destination(shot.plume!.at, shot.plume!.bearing, shot.plume!.lengthKm * 0.55));
        return p ? <Label x={p[0]} y={p[1]} text={shot.plume!.label!} color={C.amber} size={16} dx={-shot.plume!.label!.length * 4.6} dy={-10} /> : null;
      })() : null}
      {shot.burst && t >= shot.burst.t ? (() => {
        const b = shot.burst!;
        const dt = t - b.t;
        const p = pt(b.at);
        const white = Math.max(0, 1 - dt / 0.9);
        const rPx = Math.max(14, b.km * pxPerKm);
        const glow = Math.max(0, 1 - dt / 7);
        return (
          <>
            {p ? (
              <div style={{position: 'absolute', left: p[0] - rPx * 3, top: p[1] - rPx * 3, width: rPx * 6, height: rPx * 6, borderRadius: '50%', pointerEvents: 'none',
                background: `radial-gradient(circle, rgba(255,255,240,${0.95 * glow}) 0%, rgba(255,210,120,${0.85 * glow}) 18%, rgba(255,122,26,${0.5 * glow}) 34%, rgba(255,59,59,${0.18 * glow}) 55%, rgba(0,0,0,0) 70%)`}} />
            ) : null}
            {white > 0 ? <AbsoluteFill style={{background: '#FFFDF4', opacity: white * white}} /> : null}
          </>
        );
      })() : null}
      {shot.scaleBar !== false ? (
        <div style={{position: 'absolute', right: 48, bottom: 44, display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 6}}>
          <div style={{fontFamily: MONO, fontSize: 13, letterSpacing: 2, color: C.dim}}>{scaleKm} KM</div>
          <div style={{width: scaleKm * pxPerKm, height: 2, background: C.dim, boxShadow: '0 0 4px rgba(0,0,0,0.9)'}} />
        </div>
      ) : null}
    </AbsoluteFill>
  );
};
