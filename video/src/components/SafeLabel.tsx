// Map labels that stay readable and inside the frame (2026-11-10 quality pass: 005 shipped labels cut off at the
// frame edge and one printed over the SIMULATION tag; map type was 13 to 18 px, below the 24 px floor for a phone).
// Every map label goes through this: a 24 px floor (1.5x in vertical Shorts), a dark plate, and a position clamped
// into a safe box that keeps clear of the corner tag and clock (top), the caption or subtitles (bottom) and the edges.
// A label whose map point has left the frame is hidden rather than pinned to the edge pointing at nothing.
import React, {createContext, useContext} from 'react';
import {useCurrentFrame, useVideoConfig} from 'remotion';
import {C, MONO} from '../theme';

export interface Box { l: number; r: number; t: number; b: number }

export function safeBox(W: number, H: number, caption = false): Box {
  if (H > W) return {l: 56, r: W - 56, t: 548, b: H - 770};          // Short: under the title band, tag row and end pill, above subtitles
  return {l: 72, r: W - 72, t: 112, b: H - (caption ? 176 : 92)};     // long video: below tag and clock, above caption, scale bar
}

export const FLOOR = 24;
const CHAR = 0.6;     // IBM Plex Mono advance width in em
const SPACING = 1.5;  // letter spacing in px

export function labelSize(W: number, H: number, size: number, floor = FLOOR): number {
  return Math.round(Math.max(size, floor) * (H > W ? 1.5 : 1));
}

export function measure(text: string, fs: number, plate: boolean): {w: number; h: number} {
  const padX = plate ? 9 : 0, padY = plate ? 3 : 0;
  // + border and a few px of slack so a font that runs slightly wide never clips the last letter
  return {w: Math.ceil(text.length * (fs * CHAR + SPACING) + padX * 2 + (plate ? 2 : 0) + 6), h: Math.ceil(fs * 1.25 + padY * 2)};
}

// Labels placed so far in this frame, so two labels pulled to the same spot stack instead of printing over each other.
// Labels render in order within a frame; the list resets when the frame changes. A label re-rendering in the same
// frame (same id, same box) keeps the spot it already has, so a second render pass cannot move labels around.
export const LabelScope = createContext('');
let placedFrame = '';
let placed: {id: string; l: number; t: number; r: number; b: number; w: number; h: number; top0: number}[] = [];
function place(frame: string, id: string, left: number, top: number, w: number, h: number, box: Box): number {
  if (frame !== placedFrame) { placedFrame = frame; placed = []; }
  const again = placed.find((p) => p.id === id);
  if (again && again.l === left && again.w === w && again.h === h && again.top0 === top) return again.t;
  placed = placed.filter((p) => p.id !== id);
  const hits = (t: number) => placed.some((p) => left < p.r && left + w > p.l && t < p.b + 4 && t + h > p.t - 4);
  let best = top;
  for (let k = 0; k <= 8; k++) {
    const cands = k === 0 ? [top] : [top + k * (h + 6), top - k * (h + 6)];
    const ok = cands.find((t) => t >= box.t && t + h <= box.b && !hits(t));
    if (ok !== undefined) { best = ok; break; }
  }
  placed.push({id, l: left, t: best, r: left + w, b: best + h, w, h, top0: top});
  return best;
}

export const SafeLabel: React.FC<{
  x: number; y: number; text: string; color?: string; a?: number; size?: number; floor?: number;
  align?: 'left' | 'center' | 'right'; dx?: number; dy?: number; plate?: boolean; caption?: boolean; weight?: number;
}> = ({x, y, text, color, a = 1, size = 18, floor, align = 'left', dx = 12, dy = -10, plate = true, caption = false, weight = 500}) => {
  const {width: W, height: H} = useVideoConfig();
  const frame = `${useContext(LabelScope)}|${useCurrentFrame()}`;
  // hide a label only when its point is well outside the frame; near the edge it is pulled inside (005 placed text
  // labels a little above the frame, and hiding them lost the line)
  const mx = W * 0.25, my = H * 0.25;
  if (!(x >= -mx && x <= W + mx && y >= -my && y <= H + my)) return null;
  const box = safeBox(W, H, caption);
  let fs = labelSize(W, H, size, floor);
  let {w, h} = measure(text, fs, plate);
  if (w > box.r - box.l) {  // a very long label shrinks to fit the safe width rather than running off it
    fs = Math.max(16, Math.floor(fs * (box.r - box.l) / w));
    ({w, h} = measure(text, fs, plate));
  }
  const k = fs / size;
  let left = align === 'left' ? x + dx * k : align === 'right' ? x - dx * k - w : x - w / 2;
  let top = y + dy * k - h / 2;
  const clampX = (v: number) => Math.max(box.l, Math.min(v, box.r - w));
  let cl = clampX(left);
  // pulled sideways onto its own point (a label near the right edge covering its marker): put it on the other side
  if (align !== 'center' && cl !== left && x >= cl - 4 && x <= cl + w + 4) {
    const other = align === 'left' ? x - dx * k - w : x + dx * k;
    if (clampX(other) === other) cl = other;
  }
  left = cl;
  top = Math.max(box.t, Math.min(top, box.b - h));
  // labels that have not appeared yet still hold their place, so a label fading in never pushes a visible one
  top = place(frame, `${text}|${Math.round(x / 8)}`, left, top, w, h, box);
  if (a <= 0) return null;
  return (
    <div style={{position: 'absolute', left, top, width: w, boxSizing: 'border-box', fontFamily: MONO, fontSize: fs, fontWeight: weight,
      letterSpacing: SPACING, lineHeight: 1.25, color: color ?? C.text, opacity: a, whiteSpace: 'nowrap', overflow: 'hidden',
      textTransform: 'uppercase', textAlign: 'center', padding: plate ? '3px 9px' : 0,
      background: plate ? 'rgba(8,10,14,0.78)' : undefined, borderLeft: plate ? `2px solid ${color ?? C.text}` : undefined,
      textShadow: '0 0 6px rgba(0,0,0,0.95), 0 0 2px rgba(0,0,0,1)'}}>{text}</div>
  );
};
