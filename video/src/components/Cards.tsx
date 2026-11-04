// HUD chrome and card shots: tag, clock, caption, stamp, big number, chapter, isotype grid, bars, timeline,
// radar, text, airburst/groundburst split, end slate.
import React from 'react';
import {AbsoluteFill, useVideoConfig} from 'remotion';
import type {BarsShot, ChapterShot, EndSlateShot, IsotypeShot, NumberShot, RadarShot, SplitShot, StampShot, Tag, TextShot, TimelineShot} from '../scene';
import {C, COND, FONT, MONO, TAG_COLOR, clamp01, ease, easeOut} from '../theme';

const pop = (t: number, at = 0, dur = 0.45) => ease(clamp01((t - at) / dur));

export const Grid: React.FC = () => {
  const {width: W, height: H} = useVideoConfig();
  const step = 96;
  return (
    <svg width={W} height={H} style={{position: 'absolute', inset: 0}}>
      {Array.from({length: Math.ceil(W / step) + 1}, (_, i) => <line key={`v${i}`} x1={i * step} y1={0} x2={i * step} y2={H} stroke={C.grid} />)}
      {Array.from({length: Math.ceil(H / step) + 1}, (_, i) => <line key={`h${i}`} x1={0} y1={i * step} x2={W} y2={i * step} stroke={C.grid} />)}
    </svg>
  );
};

export const Ground: React.FC<{children?: React.ReactNode; blue?: boolean}> = ({children, blue}) => (
  <AbsoluteFill style={{background: blue ? 'radial-gradient(ellipse at 50% 60%, #0E2A4A 0%, #0B1A2E 45%, #0B0E12 100%)' : `radial-gradient(ellipse at 50% 50%, ${C.bg2} 0%, ${C.bg} 70%)`}}>
    <Grid />
    {children}
  </AbsoluteFill>
);

export const Chrome: React.FC<{tag?: Tag; clock?: string; clockLabel?: string; caption?: string; source?: string; t: number}> = ({tag, clock, clockLabel, caption, source, t}) => {
  const {width: W, height: H} = useVideoConfig();
  const vertical = H > W;
  const s = vertical ? 1.35 : 1;
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      {tag ? (
        <div style={{position: 'absolute', left: 40 * s, top: 36 * s, display: 'flex', alignItems: 'center', gap: 10, padding: `${6 * s}px ${12 * s}px`,
          border: `1px solid ${TAG_COLOR[tag]}88`, background: 'rgba(8,10,14,0.65)', borderRadius: 3}}>
          <div style={{width: 8 * s, height: 8 * s, borderRadius: 8, background: TAG_COLOR[tag], boxShadow: `0 0 10px ${TAG_COLOR[tag]}`}} />
          <div style={{fontFamily: MONO, fontSize: 16 * s, letterSpacing: 3, color: TAG_COLOR[tag], fontWeight: 600}}>{tag}</div>
        </div>
      ) : null}
      {clock ? (
        <div style={{position: 'absolute', right: 40 * s, top: 30 * s, textAlign: 'right'}}>
          {clockLabel ? <div style={{fontFamily: MONO, fontSize: 13 * s, letterSpacing: 3, color: C.dim}}>{clockLabel}</div> : null}
          <div style={{fontFamily: MONO, fontSize: 34 * s, fontWeight: 600, color: clock.startsWith('T') ? C.red : C.text, letterSpacing: 2, textShadow: '0 0 12px rgba(0,0,0,0.8)'}}>{clock}</div>
        </div>
      ) : null}
      {caption ? (
        <div style={{position: 'absolute', left: 0, right: 0, bottom: vertical ? 260 : 64, display: 'flex', justifyContent: 'center', opacity: pop(t, 0.1, 0.35)}}>
          <div style={{fontFamily: FONT, fontWeight: 600, fontSize: (vertical ? 44 : 34), color: C.text, padding: '10px 22px', background: 'rgba(8,10,14,0.72)',
            borderLeft: `3px solid ${C.red}`, maxWidth: W * 0.8, textAlign: 'center', lineHeight: 1.25}}>{caption}</div>
        </div>
      ) : null}
      {source ? (
        <div style={{position: 'absolute', left: 40 * s, bottom: vertical ? 200 : 28, fontFamily: MONO, fontSize: 13 * s, letterSpacing: 1, color: C.faint}}>{source}</div>
      ) : null}
    </AbsoluteFill>
  );
};

export const Stamp: React.FC<{shot: StampShot; t: number}> = ({shot, t}) => {
  const {width: W} = useVideoConfig();
  const p = pop(t, 0, 0.4);
  const col = shot.color ?? C.red;
  const scale = 1.35 - 0.35 * p;
  return (
    <Ground>
      <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center'}}>
        <div style={{transform: `rotate(-5deg) scale(${scale})`, opacity: p, border: `7px solid ${col}`, borderRadius: 10, padding: '14px 44px',
          fontFamily: COND, fontWeight: 800, fontSize: Math.min(120, (W * 0.8) / Math.max(6, shot.text.length) * 1.6), color: col, letterSpacing: 3, textTransform: 'uppercase',
          boxShadow: `0 0 40px ${col}33, inset 0 0 30px ${col}22`, whiteSpace: 'nowrap'}}>
          {shot.text}
        </div>
        {shot.line ? (
          <div style={{marginTop: 42, fontFamily: MONO, fontSize: 22, letterSpacing: 4, color: C.dim, textTransform: 'uppercase', opacity: pop(t, 0.35, 0.4), maxWidth: W * 0.8, textAlign: 'center', lineHeight: 1.6}}>{shot.line}</div>
        ) : null}
      </AbsoluteFill>
    </Ground>
  );
};

function fmt(n: number, decimals: number) {
  return n.toLocaleString('en-US', {minimumFractionDigits: decimals, maximumFractionDigits: decimals});
}

export const BigNumber: React.FC<{shot: NumberShot; t: number}> = ({shot, t}) => {
  const {width: W, height: H} = useVideoConfig();
  const col = shot.color ?? C.red;
  const p = pop(t, 0, 0.5);
  let value = shot.value;
  if (shot.countTo !== undefined) {
    const k = easeOut(clamp01(t / 1.6));
    value = `${shot.prefix ?? ''}${fmt(shot.countTo * k, shot.decimals ?? 0)}${shot.suffix ?? ''}`;
  }
  const vertical = H > W;
  const size = Math.min(vertical ? 200 : 230, (W * 0.9) / Math.max(4, value.length) * 1.55);
  return (
    <Ground>
      <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', textAlign: 'center'}}>
        {shot.label && shot.label.startsWith('^') ? <div style={{fontFamily: MONO, fontSize: 20, letterSpacing: 5, color: C.dim, marginBottom: 18, opacity: p}}>{shot.label.slice(1)}</div> : null}
        <div style={{fontFamily: COND, fontWeight: 800, fontSize: size, color: col, lineHeight: 1, letterSpacing: 2, opacity: p, transform: `translateY(${(1 - p) * 30}px)`, textShadow: `0 0 50px ${col}44`}}>
          {value}
        </div>
        {shot.label && !shot.label.startsWith('^') ? <div style={{marginTop: 26, fontFamily: FONT, fontWeight: 600, fontSize: 42, letterSpacing: 4, color: C.text, textTransform: 'uppercase', opacity: pop(t, 0.3, 0.4)}}>{shot.label}</div> : null}
        {shot.sub ? <div style={{marginTop: 16, fontFamily: MONO, fontSize: 20, letterSpacing: 2, color: C.dim, opacity: pop(t, 0.5, 0.4), maxWidth: W * 0.75, lineHeight: 1.6}}>{shot.sub}</div> : null}
      </AbsoluteFill>
    </Ground>
  );
};

export const Chapter: React.FC<{shot: ChapterShot; t: number}> = ({shot, t}) => {
  const p = pop(t, 0, 0.5);
  return (
    <Ground>
      <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', textAlign: 'center'}}>
        {shot.kicker ? <div style={{fontFamily: MONO, fontSize: 20, letterSpacing: 6, color: C.teal, marginBottom: 22, opacity: p}}>{shot.kicker}</div> : null}
        <div style={{fontFamily: COND, fontWeight: 700, fontSize: 118, color: C.text, letterSpacing: 2, textTransform: 'uppercase', opacity: p, transform: `translateY(${(1 - p) * 24}px)`}}>{shot.title}</div>
        <div style={{marginTop: 26, width: 80 * pop(t, 0.25, 0.5), height: 4, background: C.red}} />
      </AbsoluteFill>
    </Ground>
  );
};

export const Isotype: React.FC<{shot: IsotypeShot; t: number}> = ({shot, t}) => {
  const {width: W, height: H} = useVideoConfig();
  const col = shot.color ?? C.red;
  const cols = shot.cols ?? 40;
  const rows = Math.ceil(shot.total / cols);
  const cell = Math.min(18, (W * 0.44) / cols, (H * 0.55) / rows);
  const k = easeOut(clamp01((t - 0.3) / 2.0));
  const filledNow = Math.round(shot.filled * k);
  const vertical = H > W;
  return (
    <Ground blue>
      <div style={{position: 'absolute', left: vertical ? 60 : 110, top: vertical ? 160 : 150, width: vertical ? W - 120 : W * 0.4}}>
        <div style={{fontFamily: COND, fontWeight: 800, fontSize: vertical ? 96 : 92, color: col, lineHeight: 1, opacity: pop(t)}}>{shot.headline}</div>
        <div style={{fontFamily: FONT, fontWeight: 600, fontSize: 30, letterSpacing: 3, color: C.text, textTransform: 'uppercase', marginTop: 16, opacity: pop(t, 0.2)}}>{shot.label}</div>
        {shot.sub ? <div style={{fontFamily: MONO, fontSize: 18, color: C.dim, marginTop: 14, lineHeight: 1.6, opacity: pop(t, 0.4)}}>{shot.sub}</div> : null}
      </div>
      <div style={{position: 'absolute', left: vertical ? 60 : W * 0.52, top: vertical ? H * 0.42 : 150, display: 'grid', gridTemplateColumns: `repeat(${cols}, ${cell}px)`, gap: Math.max(2, cell * 0.22)}}>
        {Array.from({length: shot.total}, (_, i) => (
          <div key={i} style={{width: cell * 0.78, height: cell * 0.78, borderRadius: 2, background: i < filledNow ? col : 'rgba(236,239,242,0.14)', boxShadow: i < filledNow ? `0 0 6px ${col}66` : 'none'}} />
        ))}
      </div>
      <div style={{position: 'absolute', left: vertical ? 60 : W * 0.52, top: vertical ? H * 0.42 + rows * (cell * 1.22) + 24 : 150 + rows * (cell * 1.22) + 24, fontFamily: MONO, fontSize: 15, letterSpacing: 2, color: C.dim, textTransform: 'uppercase'}}>
        each mark = {shot.per}
      </div>
    </Ground>
  );
};

export const Bars: React.FC<{shot: BarsShot; t: number}> = ({shot, t}) => {
  const {width: W, height: H} = useVideoConfig();
  const max = Math.max(...shot.bars.map((b) => b.value));
  const vertical = H > W;
  const left = vertical ? 60 : 160, width = vertical ? W - 120 : W - 320;
  return (
    <Ground blue>
      <div style={{position: 'absolute', left, top: vertical ? 160 : 130}}>
        <div style={{fontFamily: COND, fontWeight: 700, fontSize: 64, color: C.text, textTransform: 'uppercase', letterSpacing: 1, opacity: pop(t)}}>{shot.title}</div>
        {shot.sub ? <div style={{fontFamily: MONO, fontSize: 16, letterSpacing: 3, color: C.dim, marginTop: 6, textTransform: 'uppercase', opacity: pop(t, 0.15)}}>{shot.sub}</div> : null}
      </div>
      <div style={{position: 'absolute', left, top: vertical ? 320 : 290, width}}>
        {shot.bars.map((b, i) => {
          const k = easeOut(clamp01((t - 0.3 - i * 0.25) / 1.2));
          const col = b.color ?? (i === 0 ? C.red : C.teal);
          return (
            <div key={i} style={{marginBottom: 46, opacity: pop(t, 0.2 + i * 0.25)}}>
              <div style={{fontFamily: MONO, fontSize: 17, letterSpacing: 3, color: C.text, textTransform: 'uppercase', marginBottom: 10}}>{b.label}</div>
              <div style={{display: 'flex', alignItems: 'center', gap: 18}}>
                <div style={{height: 26, width: Math.max(4, (b.value / max) * (width - 220) * k), background: col, boxShadow: `0 0 14px ${col}55`}} />
                <div style={{fontFamily: COND, fontWeight: 700, fontSize: 34, color: col}}>{b.display ?? fmt(b.value * k, 0)}</div>
              </div>
            </div>
          );
        })}
      </div>
    </Ground>
  );
};

export const Timeline: React.FC<{shot: TimelineShot; t: number}> = ({shot, t}) => {
  const {width: W, height: H} = useVideoConfig();
  const left = 150, width = W - 300, y = H * 0.55;
  const x = (m: number) => left + (m / shot.total) * width;
  const cursor = shot.cursorTo !== undefined ? easeOut(clamp01((t - 0.4) / Math.max(0.5, (shot.end - shot.start) - 1.2))) * shot.cursorTo : null;
  return (
    <Ground>
      <div style={{position: 'absolute', left, top: H * 0.24}}>
        <div style={{fontFamily: COND, fontWeight: 700, fontSize: 60, color: C.text, textTransform: 'uppercase', opacity: pop(t)}}>{shot.title}</div>
        {shot.sub ? <div style={{fontFamily: MONO, fontSize: 16, letterSpacing: 3, color: C.dim, textTransform: 'uppercase', marginTop: 6}}>{shot.sub}</div> : null}
      </div>
      {shot.segments.map((s, i) => {
        const k = easeOut(clamp01((t - 0.3 - i * 0.2) / 0.8));
        const col = s.color ?? C.teal;
        return (
          <React.Fragment key={i}>
            <div style={{position: 'absolute', left: x(s.from), top: y, width: (x(s.to) - x(s.from) - 4) * k, height: 22, background: col, opacity: 0.9}} />
            <div style={{position: 'absolute', left: x(s.from), top: y - 40, fontFamily: MONO, fontSize: 15, letterSpacing: 2, color: col, textTransform: 'uppercase', opacity: k}}>{s.label}</div>
          </React.Fragment>
        );
      })}
      {Array.from({length: Math.floor(shot.total / 5) + 1}, (_, i) => (
        <div key={`tick${i}`} style={{position: 'absolute', left: x(i * 5) - 40, top: y + 34, width: 80, textAlign: 'center', fontFamily: MONO, fontSize: 13, color: C.faint, whiteSpace: 'nowrap'}}>{i * 5} {shot.unit ?? 'MIN'}</div>
      ))}
      {shot.highlight ? (
        <>
          <div style={{position: 'absolute', left: x(shot.highlight.from) - 6, top: y - 14, width: x(shot.highlight.to) - x(shot.highlight.from) + 12, height: 50, border: `3px solid ${C.red}`, opacity: pop(t, 1.2)}} />
          <div style={{position: 'absolute', left: x(shot.highlight.from) - 60, top: y + 80, width: x(shot.highlight.to) - x(shot.highlight.from) + 120, textAlign: 'center', fontFamily: COND, fontWeight: 800, fontSize: 56, color: C.red, opacity: pop(t, 1.4)}}>{shot.highlight.label}</div>
        </>
      ) : null}
      {cursor !== null ? <div style={{position: 'absolute', left: x(cursor) - 2, top: y - 24, width: 4, height: 70, background: C.white, boxShadow: '0 0 12px #fff'}} /> : null}
    </Ground>
  );
};

export const Radar: React.FC<{shot: RadarShot; t: number}> = ({shot, t}) => {
  const {width: W, height: H} = useVideoConfig();
  const cx = W * 0.3, cy = H * 0.5, R = Math.min(W, H) * 0.3;
  const angle = (t * 80) % 360;
  const tracks = shot.tracks ?? 0;
  return (
    <Ground>
      <svg width={W} height={H} style={{position: 'absolute', inset: 0}}>
        <defs>
          <radialGradient id="sweep" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stopColor={C.teal} stopOpacity="0.5" /><stop offset="1" stopColor={C.teal} stopOpacity="0" /></radialGradient>
        </defs>
        {[0.25, 0.5, 0.75, 1].map((f) => <circle key={f} cx={cx} cy={cy} r={R * f} fill="none" stroke={C.teal} strokeOpacity={0.35} strokeWidth={1} />)}
        <line x1={cx - R} y1={cy} x2={cx + R} y2={cy} stroke={C.teal} strokeOpacity={0.25} />
        <line x1={cx} y1={cy - R} x2={cx} y2={cy + R} stroke={C.teal} strokeOpacity={0.25} />
        <path d={`M ${cx} ${cy} L ${cx + R * Math.cos((angle - 40) * Math.PI / 180)} ${cy + R * Math.sin((angle - 40) * Math.PI / 180)} A ${R} ${R} 0 0 1 ${cx + R * Math.cos(angle * Math.PI / 180)} ${cy + R * Math.sin(angle * Math.PI / 180)} Z`} fill={C.teal} fillOpacity={0.22} />
        <line x1={cx} y1={cy} x2={cx + R * Math.cos(angle * Math.PI / 180)} y2={cy + R * Math.sin(angle * Math.PI / 180)} stroke={C.teal} strokeWidth={2} />
        {Array.from({length: tracks}, (_, i) => {
          const a = -70 + (i * 37) % 60 + (i % 3) * 4, d = R * (0.35 + ((i * 29) % 60) / 100);
          const show = t > 0.5 + i * 0.12;
          const drift = clamp01((t - 0.5 - i * 0.12) / 12) * R * 0.3;
          const ax = cx + (d - drift) * Math.cos(a * Math.PI / 180), ay = cy + (d - drift) * Math.sin(a * Math.PI / 180);
          return show ? (
            <g key={i}>
              <path d={`M ${cx + (d + 40) * Math.cos(a * Math.PI / 180)} ${cy + (d + 40) * Math.sin(a * Math.PI / 180)} L ${ax} ${ay}`} stroke={C.red} strokeOpacity={0.5} strokeWidth={1} />
              <circle cx={ax} cy={ay} r={4} fill={C.red} />
            </g>
          ) : null;
        })}
      </svg>
      <div style={{position: 'absolute', left: W * 0.62, top: H * 0.22, width: W * 0.33}}>
        <div style={{fontFamily: MONO, fontSize: 16, letterSpacing: 4, color: C.teal, textTransform: 'uppercase', opacity: pop(t)}}>{shot.title}</div>
        {shot.lines.map((l, i) => (
          <div key={i} style={{marginTop: 30, opacity: pop(t, 0.3 + i * 0.3)}}>
            <div style={{fontFamily: MONO, fontSize: 13, letterSpacing: 3, color: C.dim, textTransform: 'uppercase'}}>{l.k}</div>
            <div style={{fontFamily: MONO, fontSize: 30, fontWeight: 600, color: C.text, marginTop: 4}}>{l.v}</div>
          </div>
        ))}
        {shot.big ? <div style={{marginTop: 44, fontFamily: COND, fontWeight: 800, fontSize: 64, color: shot.bigColor ?? C.red, lineHeight: 1, opacity: pop(t, 1.2)}}>{shot.big}</div> : null}
      </div>
      {shot.footer ? <div style={{position: 'absolute', left: cx - R, top: cy + R + 40, width: R * 2, textAlign: 'center', fontFamily: FONT, fontWeight: 600, fontSize: 24, color: C.text, padding: '8px 0', background: 'rgba(8,10,14,0.7)', opacity: pop(t, 1.6)}}>{shot.footer}</div> : null}
    </Ground>
  );
};

export const TextCard: React.FC<{shot: TextShot; t: number}> = ({shot, t}) => {
  const {width: W} = useVideoConfig();
  return (
    <Ground>
      <AbsoluteFill style={{justifyContent: 'center', alignItems: shot.align === 'left' ? 'flex-start' : 'center', padding: '0 160px'}}>
        {shot.lines.map((l, i) => (
          <div key={i} style={{fontFamily: i === 0 ? COND : FONT, fontWeight: i === 0 ? 800 : 500, fontSize: i === 0 ? (shot.size ?? 84) : 34, color: i === 0 ? (shot.color ?? C.text) : C.dim,
            textAlign: shot.align === 'left' ? 'left' : 'center', maxWidth: W * 0.8, lineHeight: 1.3, marginBottom: 18, opacity: pop(t, i * 0.3), textTransform: i === 0 ? 'uppercase' : 'none'}}>{l}</div>
        ))}
      </AbsoluteFill>
    </Ground>
  );
};

const Burst: React.FC<{kind: 'airburst' | 'groundburst'; t: number; x: number; y: number; w: number}> = ({kind, t, x, y, w}) => {
  const k = easeOut(clamp01((t - 0.6) / 1.4));
  const groundY = y + w * 0.42;
  const fr = w * 0.07 * (0.3 + 0.7 * k);
  return (
    <svg style={{position: 'absolute', left: x, top: y, overflow: 'visible'}} width={w} height={w}>
      <defs>
        <radialGradient id={`fb-${kind}`}><stop offset="0" stopColor="#fff" /><stop offset="0.4" stopColor="#FFB36B" /><stop offset="1" stopColor="#FF7A1A" stopOpacity="0" /></radialGradient>
        <radialGradient id={`dust-${kind}`}><stop offset="0" stopColor="#8a6a4a" stopOpacity="0.8" /><stop offset="1" stopColor="#8a6a4a" stopOpacity="0" /></radialGradient>
      </defs>
      <rect x={0} y={groundY - y} width={w} height={w * 0.08} fill="#1C2229" />
      {kind === 'airburst' ? (
        <circle cx={w / 2} cy={w * 0.25} r={fr * 1.3} fill={`url(#fb-${kind})`} />
      ) : (
        <>
          <circle cx={w / 2} cy={groundY - y - fr * 0.4} r={fr * 1.2} fill={`url(#fb-${kind})`} />
          {Array.from({length: 7}, (_, i) => (
            <circle key={i} cx={w / 2 + (i - 3) * w * 0.03 * k} cy={groundY - y - fr * 0.8 - i * w * 0.05 * k} r={w * (0.05 + i * 0.012) * k} fill={`url(#dust-${kind})`} />
          ))}
        </>
      )}
    </svg>
  );
};

export const Split: React.FC<{shot: SplitShot; t: number}> = ({shot, t}) => {
  const {width: W, height: H} = useVideoConfig();
  const panels = [shot.left, shot.right];
  return (
    <Ground blue>
      {panels.map((p, i) => {
        const x0 = i === 0 ? 0 : W / 2;
        const col = p.color ?? (i === 0 ? C.teal : C.red);
        return (
          <div key={i} style={{position: 'absolute', left: x0, top: 0, width: W / 2, height: H, opacity: pop(t, i * 0.25)}}>
            <div style={{position: 'absolute', left: 0, right: 0, top: H * 0.17, textAlign: 'center', fontFamily: COND, fontWeight: 700, fontSize: 56, color: col, textTransform: 'uppercase', letterSpacing: 2}}>{p.title}</div>
            <div style={{position: 'absolute', left: 0, right: 0, top: H * 0.17 + 66, textAlign: 'center', fontFamily: MONO, fontSize: 15, letterSpacing: 3, color: C.dim, textTransform: 'uppercase'}}>{p.sub}</div>
            <Burst kind={p.kind} t={t - i * 0.25} x={W / 4 - H * 0.22} y={H * 0.33} w={H * 0.44} />
          </div>
        );
      })}
      <div style={{position: 'absolute', left: W / 2 - 1, top: H * 0.14, width: 2, height: H * 0.72, background: 'rgba(236,239,242,0.15)'}} />
    </Ground>
  );
};

export const EndSlate: React.FC<{shot: EndSlateShot; t: number}> = ({shot, t}) => {
  const {width: W, height: H} = useVideoConfig();
  return (
    <Ground>
      <div style={{position: 'absolute', left: 90, top: H * 0.16, width: W * 0.36}}>
        <div style={{fontFamily: MONO, fontSize: 18, letterSpacing: 5, color: C.red, opacity: pop(t)}}>THE DOOMSDAY MAP</div>
        <div style={{fontFamily: COND, fontWeight: 800, fontSize: 92, color: C.text, lineHeight: 1, marginTop: 20, textTransform: 'uppercase', opacity: pop(t, 0.2)}}>{shot.title}</div>
        {shot.line ? <div style={{fontFamily: FONT, fontSize: 28, color: C.dim, marginTop: 24, lineHeight: 1.5, opacity: pop(t, 0.5)}}>{shot.line}</div> : null}
      </div>
      <div style={{position: 'absolute', left: W * 0.5, top: H * 0.16, width: W * 0.4, height: H * 0.45, border: `1px dashed rgba(236,239,242,0.12)`}} />
      <div style={{position: 'absolute', left: W * 0.5, top: H * 0.68, width: W * 0.4, textAlign: 'center', fontFamily: MONO, fontSize: 14, letterSpacing: 3, color: C.faint}}>NEXT SCENARIO</div>
    </Ground>
  );
};
