// Regional vector map: Natural Earth 50m countries on an azimuthal equidistant projection centred on the view,
// with highlighted countries, labelled cities, range rings, great-circle lines, a wind-driven plume and a scale bar.
import React, {useMemo} from 'react';
import {AbsoluteFill, useVideoConfig} from 'remotion';
import {geoAzimuthalEquidistant, geoCircle, geoGraticule10, geoInterpolate, geoPath, geoCentroid} from 'd3-geo';
import {feature, mesh} from 'topojson-client';
import world50 from 'world-atlas/countries-50m.json';
import type {LonLat, RegionShot, RegionView} from '../scene';
import {C, MONO, clamp01, ease, easeOut, lerp} from '../theme';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const topo = world50 as any;
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const COUNTRIES: any[] = (feature(topo, topo.objects.countries) as any).features;
const BORDERS = mesh(topo, topo.objects.countries, (a: any, b: any) => a !== b);
const COAST = mesh(topo, topo.objects.countries, (a: any, b: any) => a === b);
const GRAT = geoGraticule10();
const EARTH_KM = 6371.0088;
const D2R = Math.PI / 180;

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
  return {type: 'Polygon', coordinates: [pts]} as const;
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
  const bbox = (() => {
    // only draw countries whose centroid is within ~1.6 view widths (performance)
    return (c: any) => {
      const p = pt(geoCentroid(c));
      return p && p[0] > -W && p[0] < 2 * W && p[1] > -H && p[1] < 2 * H;
    };
  })();
  const hiMap = new Map((shot.highlight ?? []).map((h) => [h.iso, h]));
  return (
    <AbsoluteFill style={{background: C.bg}}>
      <svg width={W} height={H} style={{position: 'absolute', inset: 0}}>
        <defs>
          <radialGradient id="plumeG"><stop offset="0" stopColor={C.amber} stopOpacity="0.55" /><stop offset="1" stopColor={C.amber} stopOpacity="0.05" /></radialGradient>
          <filter id="soft"><feGaussianBlur stdDeviation="6" /></filter>
          <filter id="glow"><feGaussianBlur stdDeviation="2.5" result="b" /><feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge></filter>
        </defs>
        <path d={path(GRAT) ?? ''} fill="none" stroke="rgba(140,180,200,0.07)" />
        {COUNTRIES.filter(bbox).map((c) => {
          const h = hiMap.get(String(c.id));
          return <path key={c.id} d={path(c) ?? ''} fill={h ? (h.fill ?? h.color + '33') : C.land} stroke="none" />;
        })}
        <path d={path(COAST) ?? ''} fill="none" stroke="rgba(170,215,225,0.5)" strokeWidth={1.3} />
        <path d={path(BORDERS) ?? ''} fill="none" stroke={C.border} strokeWidth={1} />
        {(shot.highlight ?? []).map((h) => {
          const c = COUNTRIES.find((x) => String(x.id) === h.iso);
          return c ? <path key={h.iso} d={path(c) ?? ''} fill="none" stroke={h.color} strokeWidth={2.2} filter="url(#glow)" /> : null;
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
        const edge = pt(destination(r.at, 90, r.km));
        return edge ? <Label key={`r${i}`} x={edge[0]} y={edge[1]} text={r.label} color={r.color ?? C.red} size={15} /> : null;
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
      {shot.scaleBar !== false ? (
        <div style={{position: 'absolute', right: 48, bottom: 44, display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 6}}>
          <div style={{fontFamily: MONO, fontSize: 13, letterSpacing: 2, color: C.dim}}>{scaleKm} KM</div>
          <div style={{width: scaleKm * pxPerKm, height: 2, background: C.dim, boxShadow: '0 0 4px rgba(0,0,0,0.9)'}} />
        </div>
      ) : null}
    </AbsoluteFill>
  );
};
