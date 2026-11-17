// Night map for Survival Clock Shorts: dark land, city lights, schematic links between them, a status box that flips
// (GRID: ONLINE to OFFLINE), strike arcs and flashes. Mercator, fitted so `widthKm` spans the frame width.
import React, {useMemo} from 'react';
import {geoInterpolate, geoMercator, geoPath} from 'd3-geo';
import {feature, mesh} from 'topojson-client';
import world50 from 'world-atlas/countries-50m.json';
import cities from '../../public/data/cities.json';
import type {MapSpec} from './spec';
import {MONO, S, clamp01, easeOut, hash, useCue} from './kit';

type City = {n: string; lon: number; lat: number; pop: number};
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const topo = world50 as any;
const land = feature(topo, topo.objects.countries);
const borders = mesh(topo, topo.objects.countries, (a: unknown, b: unknown) => a !== b);

export const NightMap: React.FC<{map: MapSpec; t: number; W: number; H: number; showStatus?: boolean}> = ({map, t, W, H, showStatus = true}) => {
  const cue = useCue();
  const lat = map.center[1] * Math.PI / 180;
  const scale = (W * 6371 * Math.cos(lat)) / map.widthKm;
  const proj = useMemo(() => geoMercator().center(map.center).scale(scale).translate([W / 2, H * 0.47]),
    [map.center[0], map.center[1], scale, W, H]);
  const path = useMemo(() => geoPath(proj), [proj]);
  const landD = useMemo(() => path(land as never) ?? '', [path]);
  const borderD = useMemo(() => path(borders as never) ?? '', [path]);
  const pts = useMemo(() => {
    if (!map.lights) return [] as {x: number; y: number; r: number; i: number}[];
    return (cities as City[])
      .map((c) => ({c, p: proj([c.lon, c.lat])}))
      .filter(({p}) => p && p[0] > -40 && p[0] < W + 40 && p[1] > -40 && p[1] < H + 40)
      .sort((a, b) => b.c.pop - a.c.pop)
      .slice(0, 260)
      .map(({c, p}, i) => ({x: p![0], y: p![1], r: 3 + Math.min(12, Math.sqrt(c.pop) / 420), i}));
  }, [proj, map.lights]);
  const links = useMemo(() => {
    if (!map.links) return [] as [number, number][];
    const out = new Set<string>();
    pts.forEach((a, i) => {
      pts.map((b, j) => ({j, d: (a.x - b.x) ** 2 + (a.y - b.y) ** 2})).filter((x) => x.j !== i).sort((x, y) => x.d - y.d).slice(0, 2)
        .forEach(({j}) => out.add(i < j ? `${i}-${j}` : `${j}-${i}`));
    });
    return [...out].map((k) => k.split('-').map(Number) as [number, number]);
  }, [pts, map.links]);

  const off = map.offAt !== undefined ? cue(map.offAt, 1.2) : 1e9;
  const kOff = clamp01((t - off) / 1.4);
  const kmPx = scale / (6371 * Math.cos(lat));
  return (
    <div style={{position: 'absolute', inset: 0, opacity: map.dim ?? 1}}>
      <svg width={W} height={H} style={{position: 'absolute', inset: 0}}>
        <defs>
          <filter id="nmGlow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="5" /></filter>
        </defs>
        <path d={landD} fill="#0F151C" stroke="rgba(120,175,200,0.28)" strokeWidth={2} />
        <path d={borderD} fill="none" stroke="rgba(120,175,200,0.16)" strokeWidth={1.5} />
        {links.map(([a, b], k) => {
          const dead = kOff > hash(k + 7) * 0.8;
          return <line key={k} x1={pts[a].x} y1={pts[a].y} x2={pts[b].x} y2={pts[b].y} stroke={dead ? S.red : S.cyan}
            strokeOpacity={dead ? 0.55 : 0.5} strokeWidth={2.4} />;
        })}
        {pts.map((p) => {
          const lit = 1 - clamp01((kOff - hash(p.i) * 0.85) / 0.15);
          if (lit <= 0.01) return <circle key={p.i} cx={p.x} cy={p.y} r={p.r * 0.5} fill="rgba(120,120,120,0.35)" />;
          return (
            <g key={p.i} opacity={lit}>
              <circle cx={p.x} cy={p.y} r={p.r * 2.2} fill={S.amber} opacity={0.35} filter="url(#nmGlow)" />
              <circle cx={p.x} cy={p.y} r={p.r * 0.75} fill="#FFE2A8" />
            </g>
          );
        })}
        {(map.arcs ?? []).map((a, k) => {
          const a0 = cue(a.at, 0.5), k1 = easeOut((t - a0) / (a.dur ?? 2));
          if (k1 <= 0) return null;
          const f = geoInterpolate(a.from, a.to);
          const ps = Array.from({length: 41}, (_, i) => proj(f((i / 40) * k1))).filter(Boolean) as [number, number][];
          const d = ps.map((p, i) => `${i ? 'L' : 'M'}${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join(' ');
          const head = ps[ps.length - 1];
          return (
            <g key={`a${k}`}>
              <path d={d} fill="none" stroke={S.red} strokeWidth={7} filter="url(#nmGlow)" opacity={0.8} />
              <path d={d} fill="none" stroke="#FFD0D0" strokeWidth={3} />
              {k1 < 1 ? <circle cx={head[0]} cy={head[1]} r={9} fill="#fff" /> : null}
            </g>
          );
        })}
        {(map.flashes ?? []).map((fl, k) => {
          const a0 = cue(fl.at, 1), dt = t - a0;
          const p = proj(fl.lonlat);
          if (dt < 0 || !p) return null;
          const r = Math.max(16, (fl.km ?? 8) * kmPx) * (0.4 + 0.6 * easeOut(dt / 0.6));
          const fade = Math.exp(-dt / 2.4);
          return (
            <g key={`f${k}`}>
              <circle cx={p[0]} cy={p[1]} r={r * 2.4} fill={S.amber} opacity={0.35 * fade} filter="url(#nmGlow)" />
              <circle cx={p[0]} cy={p[1]} r={r} fill="#FFF6E0" opacity={0.95 * fade} />
              <circle cx={p[0]} cy={p[1]} r={r * (1 + dt * 1.6)} fill="none" stroke="#fff" strokeWidth={4} opacity={0.6 * fade} />
            </g>
          );
        })}
      </svg>
      {showStatus && map.status ? (
        <div style={{position: 'absolute', left: 0, width: W, top: H * 0.255, display: 'flex', justifyContent: 'center'}}>
          <div style={{border: `4px solid ${t >= off ? S.red : S.green}`, padding: '10px 30px', fontFamily: MONO, fontWeight: 700, fontSize: 50,
            letterSpacing: 6, color: t >= off ? S.red : S.green, background: 'rgba(8,10,12,0.8)',
            boxShadow: `0 0 26px ${t >= off ? S.red : S.green}55`}}>{t >= off ? map.status.off : map.status.on}</div>
        </div>
      ) : null}
      {showStatus && map.note ? (
        <div style={{position: 'absolute', left: 0, width: W, top: H * 0.885, textAlign: 'center', fontFamily: MONO, fontWeight: 500,
          fontSize: 20, letterSpacing: 4, color: S.faint}}>{map.note}</div>
      ) : null}
    </div>
  );
};
