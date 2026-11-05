// City map with real streets (OpenStreetMap via OpenFreeMap, prepared by scripts/fetch-city.mjs) and animated blast rings.
// The static base map (streets, water, buildings, runways) is painted once per shot into an offscreen canvas at 2x and
// scaled per frame: on the azimuthal equidistant projection a zoom about the view centre is a pure uniform scale, and the
// small centre drift inside a shot is treated as a translation. That turns a 5-second frame into a few milliseconds.
import React, {useEffect, useLayoutEffect, useMemo, useRef, useState} from 'react';
import {AbsoluteFill, continueRender, delayRender, staticFile, useVideoConfig} from 'remotion';
import {geoCircle, geoPath} from 'd3-geo';
import type {CityShot, LonLat, RegionView} from '../scene';
import {C, COND, MONO, clamp01, ease, easeOut} from '../theme';
import {destination, makeProjection, viewAt} from './RegionMap';
import {getBase} from './baseCache';

type CityData = {
  roads: Record<'motorway' | 'primary' | 'secondary' | 'minor' | 'rail', LonLat[][]>;
  water: LonLat[][]; waterway: LonLat[][]; aeroway: {type: number; pts: LonLat[]}[]; parks: LonLat[][]; buildings: LonLat[][];
  places: {name: string; at: LonLat; cls: string; rank: number}[];
};
const cache: Record<string, Promise<CityData>> = {};
const loadCity = (slug: string) => {
  if (!cache[slug]) cache[slug] = fetch(staticFile(`city/${slug}.json`)).then((r) => { if (!r.ok) throw new Error(`city ${slug} missing`); return r.json(); });
  return cache[slug];
};
const EARTH_KM = 6371.0088;
const D2R = Math.PI / 180;
const SUPER = 2; // offscreen resolution multiplier

const multi = (lines: LonLat[][]) => ({type: 'MultiLineString', coordinates: lines} as const);
const polys = (rings: LonLat[][]) => ({type: 'MultiPolygon', coordinates: rings.map((r) => [r])} as const);

function paintBase(data: CityData, baseView: RegionView, W: number, H: number, key: string): HTMLCanvasElement {
  return getBase('city|' + key, () => paintCity(data, baseView, W, H));
}

function paintCity(data: CityData, baseView: RegionView, W: number, H: number): HTMLCanvasElement {
  const bw = W * SUPER, bh = H * SUPER;
  const canvas = document.createElement('canvas');
  canvas.width = bw; canvas.height = bh;
  // CPU-backed canvas: under the software GL backend used for CI renders, accelerated canvases silently drop
  // very large paths
  const ctx = canvas.getContext('2d', {willReadFrequently: true})!;
  const proj = makeProjection(baseView, bw, bh);
  const path = geoPath(proj, ctx);
  const pxPerKm = bw / baseView.widthKm;
  const detail = baseView.widthKm < 60;
  // City polygons are drawn flat (project each vertex, fill planar). d3's spherical polygons depend on ring winding,
  // and OSM tile rings come in both directions, so one reversed ring would flood the whole canvas.
  const flat = (rings: LonLat[][]) => {
    ctx.beginPath();
    for (const ring of rings) {
      for (let i = 0; i < ring.length; i++) {
        const p = proj(ring[i]) as [number, number] | null;
        if (!p) continue;
        if (i === 0) ctx.moveTo(p[0], p[1]); else ctx.lineTo(p[0], p[1]);
      }
      ctx.closePath();
    }
  };
  ctx.fillStyle = '#0D1117'; ctx.fillRect(0, 0, bw, bh);
  flat(data.parks); ctx.fillStyle = '#10171A'; ctx.fill('nonzero');
  flat(data.water); ctx.fillStyle = '#0B1726'; ctx.fill('nonzero');
  ctx.beginPath(); path(multi(data.waterway) as any); ctx.strokeStyle = '#0F2238'; ctx.lineWidth = Math.max(1, pxPerKm * 0.03); ctx.stroke();
  if (detail && data.buildings.length) {
    ctx.fillStyle = 'rgba(190,205,215,0.10)';
    for (let i = 0; i < data.buildings.length; i += 1500) {  // batches keep each path small
      flat(data.buildings.slice(i, i + 1500)); ctx.fill('nonzero');
    }
  }
  const road = (lines: LonLat[][], color: string, lw: number, dash?: number[]) => {
    if (!lines.length) return;
    ctx.strokeStyle = color; ctx.lineWidth = lw; ctx.lineJoin = 'round'; ctx.lineCap = 'round'; ctx.setLineDash(dash ?? []);
    for (let i = 0; i < lines.length; i += 2000) { ctx.beginPath(); path(multi(lines.slice(i, i + 2000)) as any); ctx.stroke(); }
    ctx.setLineDash([]);
  };
  if (detail) road(data.roads.minor, 'rgba(160,180,190,0.16)', Math.max(0.6, pxPerKm * 0.012));
  road(data.roads.secondary, 'rgba(170,190,200,0.32)', Math.max(0.9, pxPerKm * 0.02));
  road(data.roads.primary, 'rgba(190,210,220,0.5)', Math.max(1.3, pxPerKm * 0.03));
  road(data.roads.motorway, 'rgba(225,235,240,0.75)', Math.max(2, pxPerKm * 0.045));
  road(data.roads.rail, 'rgba(200,200,210,0.35)', 1.2 * SUPER, [6, 6]);
  for (const a of data.aeroway) {
    ctx.beginPath();
    if (a.type === 3) { flat([a.pts]); ctx.fillStyle = 'rgba(200,210,220,0.10)'; ctx.fill('nonzero'); }
    else { path({type: 'LineString', coordinates: a.pts} as any); ctx.strokeStyle = 'rgba(220,230,235,0.8)'; ctx.lineWidth = Math.max(2, pxPerKm * 0.06); ctx.stroke(); }
  }
  return canvas;
}

export const CityMap: React.FC<{shot: CityShot; t: number}> = ({shot, t}) => {
  const {width: W, height: H} = useVideoConfig();
  const ref = useRef<HTMLCanvasElement>(null);
  const [data, setData] = useState<CityData | null>(null);
  const [handle] = useState(() => delayRender(`city ${shot.city}`));
  useEffect(() => {
    loadCity(shot.city).then((d) => { setData(d); continueRender(handle); }).catch((e) => { console.error(e); continueRender(handle); });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [shot.city]);
  const dur = shot.end - shot.start;
  const view = viewAt(shot.view, shot.zoomTo, t, dur);
  const proj = useMemo(() => makeProjection(view, W, H), [view.center[0], view.center[1], view.widthKm, W, H]);
  const pxPerKm = W / view.widthKm;
  // base view: the widest the shot gets, centred on the shot's start centre, with a margin for drift
  const baseView: RegionView = useMemo(() => ({
    center: shot.view.center,
    widthKm: Math.max(shot.view.widthKm, shot.zoomTo?.widthKm ?? 0) * 1.12,
  }), [shot.view, shot.zoomTo]);
  const baseKey = `${shot.city}|${shot.id}|${W}x${H}|${baseView.widthKm.toFixed(2)}`;

  useLayoutEffect(() => {
    const canvas = ref.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d')!;
    ctx.fillStyle = '#0D1117';
    ctx.fillRect(0, 0, W, H);
    if (!data) return;
    const base = paintBase(data, baseView, W, H, baseKey);
    const pb = makeProjection(baseView, W * SUPER, H * SUPER);
    const q = pb(view.center) as [number, number];
    const k = baseView.widthKm / (SUPER * view.widthKm);
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = 'high';
    ctx.drawImage(base, W / 2 - q[0] * k, H / 2 - q[1] * k, W * SUPER * k, H * SUPER * k);
    // fireball glow after the flash
    if (shot.flashT !== undefined && t >= shot.flashT) {
      const p = proj(shot.gz) as [number, number];
      const fire = shot.rings[0];
      const rr = (fire?.km ?? 0.5) * pxPerKm * (0.5 + 0.5 * easeOut(clamp01((t - shot.flashT) / 1.2)));
      const g = ctx.createRadialGradient(p[0], p[1], 0, p[0], p[1], rr * 2.2);
      g.addColorStop(0, 'rgba(255,255,255,0.95)'); g.addColorStop(0.3, 'rgba(255,190,110,0.85)'); g.addColorStop(0.6, 'rgba(255,110,40,0.35)'); g.addColorStop(1, 'rgba(255,80,20,0)');
      ctx.beginPath(); ctx.arc(p[0], p[1], rr * 2.2, 0, Math.PI * 2); ctx.fillStyle = g; ctx.fill();
    }
    const vg = ctx.createRadialGradient(W / 2, H / 2, Math.min(W, H) * 0.5, W / 2, H / 2, Math.max(W, H) * 0.8);
    vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,0,0,0.5)');
    ctx.fillStyle = vg; ctx.fillRect(0, 0, W, H);
  }, [data, proj, t, W, H, shot, view.widthKm, view.center, pxPerKm, baseView, baseKey]);

  const circle = geoCircle();
  const svgPath = useMemo(() => geoPath(proj), [proj]);
  const flash = shot.flashT !== undefined ? clamp01((t - shot.flashT) / 0.9) : 1;
  const gzPx = proj(shot.gz) as [number, number] | null;
  return (
    <AbsoluteFill style={{background: '#0D1117'}}>
      <canvas ref={ref} width={W} height={H} style={{width: '100%', height: '100%'}} />
      <svg width={W} height={H} style={{position: 'absolute', inset: 0}}>
        {shot.rings.map((r, i) => {
          const k = easeOut(clamp01((t - r.t) / 0.9));
          if (k <= 0) return null;
          const c = circle.center(shot.gz).radius((r.km * k) / EARTH_KM / D2R)();
          const col = r.color ?? [C.white, C.red, C.orange, C.amber, C.teal][i % 5];
          return <path key={i} d={svgPath(c) ?? ''} fill={col + '12'} stroke={col} strokeWidth={2} />;
        })}
        {gzPx ? <g><line x1={gzPx[0] - 14} y1={gzPx[1]} x2={gzPx[0] + 14} y2={gzPx[1]} stroke={C.white} strokeWidth={1} /><line x1={gzPx[0]} y1={gzPx[1] - 14} x2={gzPx[0]} y2={gzPx[1] + 14} stroke={C.white} strokeWidth={1} /></g> : null}
      </svg>
      {shot.rings.map((r, i) => {
        if (t < r.t + 0.6) return null;
        // labels fan out along a diagonal from ground zero so small rings do not overlap
        const edge = proj(destination(shot.gz, 40 + i * 26, r.km)) as [number, number] | null;
        if (!edge) return null;
        const col = r.color ?? [C.white, C.red, C.orange, C.amber, C.teal][i % 5];
        const small = r.km * pxPerKm < 60;
        // keep the label inside the frame: in vertical Shorts the outer rings reach the right edge
        const estW = (`${r.label} · ${r.km} KM`.length) * 11.6;
        const left = Math.max(24, Math.min(edge[0] + 10, W - estW - 24));
        return (
          <div key={i} style={{position: 'absolute', left, top: edge[1] - 12 - (small ? (3 - i) * 22 : 0), fontFamily: MONO, fontSize: 16, letterSpacing: 1.5,
            color: col, textShadow: '0 0 6px rgba(0,0,0,0.95)', whiteSpace: 'nowrap', textTransform: 'uppercase', opacity: ease(clamp01((t - r.t - 0.6) / 0.4))}}>
            {r.label} · {r.km} KM
          </div>
        );
      })}
      {(data?.places ?? []).filter((p) => !(shot.labels ?? []).some((l) => l.text.toLowerCase().includes(p.name.toLowerCase())))
        .filter((p) => p.cls === 'city' || p.cls === 'town' || view.widthKm < 25).slice(0, view.widthKm < 25 ? 40 : 12).map((p, i) => {
        const q = proj(p.at) as [number, number] | null;
        if (!q || q[0] < 0 || q[0] > W || q[1] < 0 || q[1] > H) return null;
        return <div key={i} style={{position: 'absolute', left: q[0] - 60, width: 120, top: q[1] - 9, textAlign: 'center', fontFamily: MONO, fontSize: p.cls === 'city' ? 17 : 13, letterSpacing: 1.5, color: 'rgba(236,239,242,0.6)', textShadow: '0 0 6px rgba(0,0,0,0.95)', textTransform: 'uppercase', whiteSpace: 'nowrap'}}>{p.name}</div>;
      })}
      {(shot.labels ?? []).map((l, i) => {
        const q = proj(l.at) as [number, number] | null;
        if (!q || (l.t !== undefined && t < l.t)) return null;
        return <div key={`l${i}`} style={{position: 'absolute', left: q[0] + 10, top: q[1] - 10, fontFamily: MONO, fontSize: 16, letterSpacing: 1.5, color: l.color ?? C.text, textShadow: '0 0 6px rgba(0,0,0,0.95)', textTransform: 'uppercase', whiteSpace: 'nowrap'}}>{l.text}</div>;
      })}
      {shot.legend?.length ? (
        <div style={{position: 'absolute', left: 48, bottom: 120, background: 'rgba(8,10,14,0.7)', padding: '12px 16px', border: '1px solid rgba(236,239,242,0.1)'}}>
          {shot.legend.map((l, i) => (
            <div key={i} style={{display: 'flex', alignItems: 'center', gap: 10, fontFamily: MONO, fontSize: 14, color: C.dim, letterSpacing: 1, marginBottom: 6}}>
              <div style={{width: 10, height: 10, background: l.color ?? C.red}} />{l.text}
            </div>
          ))}
        </div>
      ) : null}
      <div style={{position: 'absolute', right: 48, bottom: 44, display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 6}}>
        {(() => { const km = [1, 2, 5, 10, 20, 50].find((k) => k * pxPerKm > 140) ?? 50; return (<><div style={{fontFamily: MONO, fontSize: 13, letterSpacing: 2, color: C.dim}}>{km} KM</div><div style={{width: km * pxPerKm, height: 2, background: C.dim}} /></>); })()}
      </div>
      {shot.flashT !== undefined && t >= shot.flashT && flash < 1 ? <AbsoluteFill style={{background: '#fff', opacity: (1 - flash) * 0.95}} /> : null}
      {!data ? <div style={{position: 'absolute', left: 60, top: 60, fontFamily: COND, fontSize: 30, color: C.red}}>city data missing: {shot.city}</div> : null}
    </AbsoluteFill>
  );
};
