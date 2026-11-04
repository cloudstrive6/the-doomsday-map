// Software-rendered globe: NASA Blue Marble (day) and Black Marble (night) sampled per pixel with a real
// day-night terminator, atmosphere rim, country borders from Natural Earth, lofted great-circle arcs,
// markers and flashes. No WebGL, so it renders the same on a GitHub runner as on a workstation.
import React, {useEffect, useLayoutEffect, useMemo, useRef, useState} from 'react';
import {AbsoluteFill, continueRender, delayRender, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {geoGraticule10, geoInterpolate, geoOrthographic, geoPath} from 'd3-geo';
import {feature, mesh} from 'topojson-client';
import world110 from 'world-atlas/countries-110m.json';
import world50 from 'world-atlas/countries-50m.json';
import type {CameraKey, GlobeShot, LonLat} from '../scene';
import {C, MONO, ease, clamp01, lerp} from '../theme';

type Tex = {w: number; h: number; d: Uint8ClampedArray};
const texCache: Record<string, Promise<Tex>> = {};
const loadTex = (name: string): Promise<Tex> => {
  if (!texCache[name]) {
    texCache[name] = new Promise((resolve, reject) => {
      const img = new Image();
      img.crossOrigin = 'anonymous';
      img.onload = () => {
        const c = document.createElement('canvas');
        c.width = img.width;
        c.height = img.height;
        const ctx = c.getContext('2d', {willReadFrequently: true})!;
        ctx.drawImage(img, 0, 0);
        const id = ctx.getImageData(0, 0, c.width, c.height);
        resolve({w: c.width, h: c.height, d: id.data});
      };
      img.onerror = () => reject(new Error(`texture failed: ${name}`));
      img.src = staticFile(name);
    });
  }
  return texCache[name];
};

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const topo110 = world110 as any;
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const topo50 = world50 as any;
const BORDERS110 = mesh(topo110, topo110.objects.countries, (a: any, b: any) => a !== b);
const BORDERS50 = mesh(topo50, topo50.objects.countries, (a: any, b: any) => a !== b);
const COAST110 = mesh(topo110, topo110.objects.countries, (a: any, b: any) => a === b);
const COAST50 = mesh(topo50, topo50.objects.countries, (a: any, b: any) => a === b);
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const COUNTRIES50: any[] = (feature(topo50, topo50.objects.countries) as any).features;
const GRATICULE = geoGraticule10();

const D2R = Math.PI / 180;

export function cameraAt(keys: CameraKey[], t: number): CameraKey {
  if (keys.length === 1 || t <= keys[0].t) return keys[0];
  for (let i = 0; i < keys.length - 1; i++) {
    const a = keys[i], b = keys[i + 1];
    if (t <= b.t) {
      const u = ease(clamp01((t - a.t) / Math.max(1e-6, b.t - a.t)));
      let dl = b.lon - a.lon;
      if (dl > 180) dl -= 360;
      if (dl < -180) dl += 360;
      return {t, lat: lerp(a.lat, b.lat, u), lon: a.lon + dl * u, scale: Math.exp(lerp(Math.log(a.scale), Math.log(b.scale), u))};
    }
  }
  return keys[keys.length - 1];
}

/** geographic -> view-space unit vector for a camera centred on (lat0, lon0). z > 0 faces the viewer. */
function toView(lon: number, lat: number, lat0: number, lon0: number): [number, number, number] {
  const φ = lat * D2R, λ = (lon - lon0) * D2R, φ0 = lat0 * D2R;
  const cφ = Math.cos(φ), sφ = Math.sin(φ), cφ0 = Math.cos(φ0), sφ0 = Math.sin(φ0);
  return [cφ * Math.sin(λ), cφ0 * sφ - sφ0 * cφ * Math.cos(λ), sφ0 * sφ + cφ0 * cφ * Math.cos(λ)];
}

function smooth(a: number, b: number, x: number) {
  const t = clamp01((x - a) / (b - a));
  return t * t * (3 - 2 * t);
}

function drawRaster(ctx: CanvasRenderingContext2D, day: Tex, night: Tex, cam: CameraKey, sun: {lat: number; lon: number},
  W: number, H: number, dim: number) {
  const r = cam.scale, cx = W / 2, cy = H / 2;
  const φ0 = cam.lat * D2R, λ0 = cam.lon * D2R;
  const sφ0 = Math.sin(φ0), cφ0 = Math.cos(φ0);
  const sl = sun.lat * D2R, sn = sun.lon * D2R;
  const Sx = Math.cos(sl) * Math.cos(sn), Sy = Math.cos(sl) * Math.sin(sn), Sz = Math.sin(sl);
  const x0 = Math.max(0, Math.floor(cx - r)), x1 = Math.min(W - 1, Math.ceil(cx + r));
  const y0 = Math.max(0, Math.floor(cy - r)), y1 = Math.min(H - 1, Math.ceil(cy + r));
  if (x1 <= x0 || y1 <= y0) return;
  const bw = x1 - x0 + 1, bh = y1 - y0 + 1;
  const img = ctx.createImageData(bw, bh);
  const out = img.data;
  const dw = day.w, dh = day.h, dd = day.d, nw = night.w, nh = night.h, nd = night.d;
  const TWO_PI = Math.PI * 2;
  const keep = 1 - dim;
  for (let py = y0; py <= y1; py++) {
    const y = (cy - py) / r;
    const yy = y * y;
    const row = (py - y0) * bw;
    for (let px = x0; px <= x1; px++) {
      const x = (px - cx) / r;
      const q = 1 - x * x - yy;
      if (q < 0) continue;
      const z = Math.sqrt(q);
      const sφ = y * cφ0 + z * sφ0;
      const lat = Math.asin(sφ > 1 ? 1 : sφ < -1 ? -1 : sφ);
      const lon = λ0 + Math.atan2(x, z * cφ0 - y * sφ0);
      const cl = Math.cos(lat);
      const nx = cl * Math.cos(lon), ny = cl * Math.sin(lon), nz = sφ;
      const dot = nx * Sx + ny * Sy + nz * Sz;
      // texture coords
      let u = lon / TWO_PI + 0.5;
      u -= Math.floor(u);
      const v = 0.5 - lat / Math.PI;
      // bilinear day
      const fx = u * dw - 0.5, fy = v * dh - 0.5;
      let ix = Math.floor(fx), iy = Math.floor(fy);
      const tx = fx - ix, ty = fy - iy;
      if (iy < 0) iy = 0;
      const iy1 = iy + 1 >= dh ? dh - 1 : iy + 1;
      const ix0 = ((ix % dw) + dw) % dw, ix1 = (ix0 + 1) % dw;
      const a = (iy * dw + ix0) * 4, b = (iy * dw + ix1) * 4, c2 = (iy1 * dw + ix0) * 4, d2 = (iy1 * dw + ix1) * 4;
      const w00 = (1 - tx) * (1 - ty), w10 = tx * (1 - ty), w01 = (1 - tx) * ty, w11 = tx * ty;
      const dr = dd[a] * w00 + dd[b] * w10 + dd[c2] * w01 + dd[d2] * w11;
      const dg = dd[a + 1] * w00 + dd[b + 1] * w10 + dd[c2 + 1] * w01 + dd[d2 + 1] * w11;
      const db = dd[a + 2] * w00 + dd[b + 2] * w10 + dd[c2 + 2] * w01 + dd[d2 + 2] * w11;
      // nearest night
      const nxp = Math.floor(u * nw) % nw, nyp = Math.min(nh - 1, Math.floor(v * nh));
      const ni = (nyp * nw + nxp) * 4;
      const nr = nd[ni], ng = nd[ni + 1], nb = nd[ni + 2];
      const w = smooth(-0.14, 0.12, dot);
      const light = 0.22 + 0.78 * (dot > 0 ? dot : 0);
      const dayMul = light * w;
      const nightMul = (1 - w) * 1.05 + 0.25 * (1 - w) * w;
      const e = x * x + yy;
      const rim = Math.pow(e, 7) * (0.35 + 0.65 * w);
      let R = (dr * dayMul + nr * nightMul + 16 * (1 - w)) * keep + 60 * rim;
      let G = (dg * dayMul + ng * nightMul * 0.95 + 22 * (1 - w)) * keep + 110 * rim;
      let B = (db * dayMul + nb * nightMul * 0.85 + 34 * (1 - w)) * keep + 200 * rim;
      const o = (row + (px - x0)) * 4;
      out[o] = R > 255 ? 255 : R;
      out[o + 1] = G > 255 ? 255 : G;
      out[o + 2] = B > 255 ? 255 : B;
      out[o + 3] = 255;
    }
  }
  ctx.putImageData(img, x0, y0);
  // atmosphere halo
  const g = ctx.createRadialGradient(cx, cy, r * 0.98, cx, cy, r * 1.07);
  g.addColorStop(0, 'rgba(90,150,255,0.55)');
  g.addColorStop(0.35, 'rgba(70,120,230,0.18)');
  g.addColorStop(1, 'rgba(40,80,180,0)');
  ctx.save();
  ctx.globalCompositeOperation = 'lighter';
  ctx.beginPath();
  ctx.arc(cx, cy, r * 1.08, 0, Math.PI * 2);
  ctx.arc(cx, cy, r * 0.985, 0, Math.PI * 2, true);
  ctx.fillStyle = g;
  ctx.fill();
  ctx.restore();
}

export const Globe: React.FC<{shot: GlobeShot; t: number}> = ({shot, t}) => {
  const {width: W, height: H} = useVideoConfig();
  const ref = useRef<HTMLCanvasElement>(null);
  const [tex, setTex] = useState<{day: Tex; night: Tex} | null>(null);
  const cam = cameraAt(shot.camera, t);
  const hi = cam.scale > 1100;
  const [handle] = useState(() => delayRender('globe textures'));
  useEffect(() => {
    let alive = true;
    Promise.all([loadTex(hi ? 'textures/day_4k.jpg' : 'textures/day_2k.jpg'), loadTex(hi ? 'textures/night_4k.jpg' : 'textures/night_2k.jpg')])
      .then(([day, night]) => { if (alive) { setTex({day, night}); continueRender(handle); } })
      .catch((e) => { console.error(e); continueRender(handle); });
    return () => { alive = false; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [hi]);

  const sun = shot.sun ?? {lat: -15, lon: cam.lon - 70};
  const proj = useMemo(() => geoOrthographic().rotate([-cam.lon, -cam.lat]).scale(cam.scale).translate([W / 2, H / 2]).clipAngle(90),
    [cam.lon, cam.lat, cam.scale, W, H]);

  useLayoutEffect(() => {
    const canvas = ref.current;
    if (!canvas || !tex) return;
    const ctx = canvas.getContext('2d')!;
    ctx.fillStyle = C.bg;
    ctx.fillRect(0, 0, W, H);
    drawRaster(ctx, tex.day, tex.night, cam, sun, W, H, shot.dim ?? 0);
    const path = geoPath(proj, ctx);
    const r = cam.scale;
    if (shot.graticule !== false) {
      ctx.beginPath(); path(GRATICULE); ctx.strokeStyle = 'rgba(140,180,200,0.10)'; ctx.lineWidth = 1; ctx.stroke();
    }
    if (shot.highlight?.length) {
      for (const h of shot.highlight) {
        const f = COUNTRIES50.find((c) => String(c.id) === h.iso);
        if (!f) continue;
        ctx.beginPath(); path(f);
        ctx.fillStyle = h.color + '55'; ctx.fill();
        ctx.strokeStyle = h.color; ctx.lineWidth = r > 900 ? 2 : 1.4; ctx.stroke();
      }
    }
    if (shot.borders !== false) {
      ctx.beginPath(); path(r > 900 ? COAST50 : COAST110); ctx.strokeStyle = 'rgba(160,210,220,0.35)'; ctx.lineWidth = r > 900 ? 1.2 : 0.8; ctx.stroke();
      ctx.beginPath(); path(r > 900 ? BORDERS50 : BORDERS110); ctx.strokeStyle = 'rgba(120,190,200,0.45)'; ctx.lineWidth = r > 900 ? 1.1 : 0.7; ctx.stroke();
    }
    // arcs
    const cx = W / 2, cy = H / 2;
    for (const a of shot.arcs ?? []) {
      if (t < a.t0) continue;
      const p = clamp01((t - a.t0) / Math.max(0.01, a.t1 - a.t0));
      const since = t - a.t1;
      const alpha = p < 1 ? 1 : Math.max(0.35, 1 - since * 0.4);
      const interp = geoInterpolate(a.from, a.to);
      const loft = a.loft ?? 0.14;
      const N = 96;
      const col = a.color ?? C.red;
      ctx.lineWidth = a.width ?? Math.max(1.2, r / 420);
      ctx.lineCap = 'round';
      let prev: [number, number] | null = null;
      ctx.beginPath();
      for (let i = 0; i <= N; i++) {
        const s = (i / N) * p;
        const g = interp(s);
        const [vx, vy, vz] = toView(g[0], g[1], cam.lat, cam.lon);
        const h = loft * Math.sin(Math.PI * s);
        const sx = cx + r * (1 + h) * vx, sy = cy - r * (1 + h) * vy;
        const visible = vz > -h * 0.9;
        if (visible && prev) ctx.lineTo(sx, sy); else ctx.moveTo(sx, sy);
        prev = visible ? [sx, sy] : null;
      }
      ctx.strokeStyle = col; ctx.globalAlpha = alpha * 0.9; ctx.shadowColor = col; ctx.shadowBlur = 8; ctx.stroke();
      ctx.shadowBlur = 0;
      if (p < 1 && prev) {  // bright head
        ctx.beginPath(); ctx.arc(prev[0], prev[1], Math.max(2.5, r / 300), 0, Math.PI * 2); ctx.fillStyle = '#fff'; ctx.globalAlpha = 1; ctx.fill();
      }
      ctx.globalAlpha = 1;
    }
    // markers
    for (const m of shot.markers ?? []) {
      if (m.t !== undefined && t < m.t) continue;
      const [vx, vy, vz] = toView(m.at[0], m.at[1], cam.lat, cam.lon);
      if (vz < 0.02) continue;
      const sx = cx + r * vx, sy = cy - r * vy;
      const pop = m.t === undefined ? 1 : ease(clamp01((t - m.t) / 0.4));
      const size = (m.size ?? Math.max(3, r / 200)) * (1.6 - 0.6 * pop);
      const col = m.color ?? C.teal;
      ctx.globalAlpha = pop;
      if (m.kind === 'ring' || m.kind === 'target') {
        ctx.beginPath(); ctx.arc(sx, sy, size * 2.2, 0, Math.PI * 2); ctx.strokeStyle = col; ctx.lineWidth = 1.2; ctx.stroke();
      }
      if (m.kind === 'target') {
        ctx.beginPath(); ctx.moveTo(sx - size * 3.2, sy); ctx.lineTo(sx + size * 3.2, sy); ctx.moveTo(sx, sy - size * 3.2); ctx.lineTo(sx, sy + size * 3.2);
        ctx.strokeStyle = col; ctx.lineWidth = 1; ctx.stroke();
      }
      if (m.kind === 'base' || m.kind === 'sub') {
        ctx.beginPath(); ctx.rect(sx - size, sy - size, size * 2, size * 2); ctx.fillStyle = col; ctx.fill();
      } else {
        ctx.beginPath(); ctx.arc(sx, sy, size, 0, Math.PI * 2); ctx.fillStyle = col; ctx.shadowColor = col; ctx.shadowBlur = 10; ctx.fill(); ctx.shadowBlur = 0;
      }
      ctx.globalAlpha = 1;
    }
    // flashes
    for (const f of shot.flashes ?? []) {
      if (t < f.t) continue;
      const [vx, vy, vz] = toView(f.at[0], f.at[1], cam.lat, cam.lon);
      if (vz < 0) continue;
      const sx = cx + r * vx, sy = cy - r * vy;
      const age = t - f.t;
      const hold = f.hold ?? 2.2;
      const maxR = f.radius ?? Math.max(14, r / 40);
      const col = f.color ?? '#FFB36B';
      if (age < hold) {
        const k = age / hold;
        const rr = maxR * (0.3 + 0.7 * ease(Math.min(1, age / 0.5)));
        const g = ctx.createRadialGradient(sx, sy, 0, sx, sy, rr);
        g.addColorStop(0, `rgba(255,255,255,${(1 - k) * 0.95})`);
        g.addColorStop(0.35, `rgba(255,190,110,${(1 - k) * 0.8})`);
        g.addColorStop(1, 'rgba(255,120,40,0)');
        ctx.beginPath(); ctx.arc(sx, sy, rr, 0, Math.PI * 2); ctx.fillStyle = g; ctx.fill();
        ctx.beginPath(); ctx.arc(sx, sy, rr * (0.6 + 0.9 * k), 0, Math.PI * 2); ctx.strokeStyle = `rgba(255,120,60,${(1 - k) * 0.8})`; ctx.lineWidth = 1.5; ctx.stroke();
      }
      ctx.beginPath(); ctx.arc(sx, sy, Math.max(2.2, r / 260), 0, Math.PI * 2); ctx.fillStyle = col; ctx.shadowColor = col; ctx.shadowBlur = 12; ctx.fill(); ctx.shadowBlur = 0;
    }
    // vignette
    const vg = ctx.createRadialGradient(cx, cy, Math.min(W, H) * 0.45, cx, cy, Math.max(W, H) * 0.75);
    vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,0,0,0.55)');
    ctx.fillStyle = vg; ctx.fillRect(0, 0, W, H);
  }, [tex, t, cam.lat, cam.lon, cam.scale, W, H, proj, shot, sun]);

  // HTML labels for markers (crisp text)
  const labels = useMemo(() => {
    const out: {x: number; y: number; text: string; color: string; a: number}[] = [];
    const cx = W / 2, cy = H / 2, r = cam.scale;
    for (const m of shot.markers ?? []) {
      if (!m.label || (m.t !== undefined && t < m.t)) continue;
      const [vx, vy, vz] = toView(m.at[0], m.at[1], cam.lat, cam.lon);
      if (vz < 0.06) continue;
      out.push({x: cx + r * vx, y: cy - r * vy, text: m.label, color: m.color ?? C.teal, a: m.t === undefined ? 1 : ease(clamp01((t - m.t) / 0.4))});
    }
    return out;
  }, [shot.markers, t, cam.lat, cam.lon, cam.scale, W, H]);

  return (
    <AbsoluteFill style={{background: C.bg}}>
      <canvas ref={ref} width={W} height={H} style={{width: '100%', height: '100%'}} />
      {labels.map((l, i) => (
        <div key={i} style={{position: 'absolute', left: l.x + 12, top: l.y - 11, fontFamily: MONO, fontSize: 18, letterSpacing: 1.5,
          color: l.color, opacity: l.a, textShadow: '0 0 6px rgba(0,0,0,0.9), 0 0 2px rgba(0,0,0,1)', whiteSpace: 'nowrap', textTransform: 'uppercase'}}>
          {l.text}
        </div>
      ))}
    </AbsoluteFill>
  );
};

export const _internal = {toView, cameraAt};
export type {LonLat};
