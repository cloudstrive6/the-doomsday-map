// Survival Clock kit: time and cue helpers, the running clock, word-pill captions, stamps and the board widgets.
// Everything is driven by the video time `t` (seconds), never by timers, so every frame renders the same way twice.
import React, {createContext, useContext} from 'react';
import {Img, staticFile} from 'remotion';
import {loadFont as loadBarlow} from '@remotion/google-fonts/Barlow';
import {loadFont as loadCond} from '@remotion/google-fonts/BarlowCondensed';
import {loadFont as loadMono} from '@remotion/google-fonts/IBMPlexMono';
import {Icon} from './icons';
import type {ClockSpec, Cue, StateStep, Tone, Widget, Word, StampSpec, CompareSide} from './spec';

const heavy = loadBarlow('normal', {weights: ['700', '800', '900'], subsets: ['latin']});
const cond = loadCond('normal', {weights: ['700', '800', '900'], subsets: ['latin']});
const mono = loadMono('normal', {weights: ['500', '600', '700'], subsets: ['latin']});
export const SANS = heavy.fontFamily;
export const COND = cond.fontFamily;
export const MONO = mono.fontFamily;

export const S = {
  bg: '#090B0E', panel: 'rgba(14, 18, 23, 0.92)', line: 'rgba(150, 200, 220, 0.32)', lineHi: 'rgba(150, 200, 220, 0.6)',
  text: '#F3F5F7', dim: 'rgba(243, 245, 247, 0.58)', faint: 'rgba(243, 245, 247, 0.28)',
  red: '#FF3B3B', yellow: '#FFD21F', cyan: '#2EC7F0', blue: '#2D8CFF', green: '#3FE39A', amber: '#FFB347',
  paper: '#EEE6D3', ink: '#1A1A1A', inkDim: 'rgba(26, 26, 26, 0.6)',
};
export const toneColor = (t?: Tone | 'white' | 'yellow'): string =>
  t === 'red' ? S.red : t === 'ok' ? S.green : t === 'warn' ? S.yellow : t === 'info' ? S.cyan : t === 'dim' ? S.dim
    : t === 'yellow' ? S.yellow : S.text;

export const clamp01 = (x: number) => Math.max(0, Math.min(1, x));
export const easeOut = (x: number) => 1 - Math.pow(1 - clamp01(x), 3);
export const easeInOut = (x: number) => { const k = clamp01(x); return k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2; };
const backOut = (x: number) => { const k = clamp01(x), c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(k - 1, 3) + c1 * Math.pow(k - 1, 2); };
export const hash = (n: number) => { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };

/** Entrance for any element: fade, a small rise and a scale with a little overshoot. */
export function pop(t: number, at: number, d = 0.32) {
  const x = (t - at) / d;
  if (x <= 0) return {o: 0, s: 0.84, y: 22, k: 0};
  return {o: clamp01(x * 2.5), s: 0.84 + 0.16 * backOut(x), y: (1 - easeOut(x)) * 22, k: clamp01(x)};
}
export const popStyle = (p: ReturnType<typeof pop>): React.CSSProperties =>
  ({opacity: p.o, transform: `translateY(${p.y}px) scale(${p.s})`});

// ---- time context and word cues ---------------------------------------------------------------------------------
export interface Ctx { t: number; words: Word[]; sceneStart: number; sceneEnd: number; W: number; H: number }
export const SurvivalCtx = createContext<Ctx>({t: 0, words: [], sceneStart: 0, sceneEnd: 1, W: 1080, H: 1920});
export const useS = () => useContext(SurvivalCtx);

export const normWord = (w: string) => w.toLowerCase().replace(/[^a-z0-9½]/g, '');
export function resolveCue(at: Cue | undefined, words: Word[], from: number, fallback: number): number {
  if (at === undefined || at === null) return fallback;
  if (typeof at === 'number') return at;
  const m = /^@([^#+]+?)(?:#(\d+))?([+-][\d.]+)?$/.exec(at.trim());
  if (!m) return fallback;
  const target = normWord(m[1]);
  let n = Number(m[2] ?? 1);
  for (const w of words) {
    if (w.start >= from - 0.05 && normWord(w.word) === target && --n === 0) return w.start + Number(m[3] ?? 0);
  }
  return fallback;
}
/** Resolve a cue inside the current scene; default: the scene start plus `def` seconds. */
export function useCue() {
  const c = useS();
  return (at: Cue | undefined, def = 0) => resolveCue(at, c.words, c.sceneStart, c.sceneStart + def);
}
const stepAt = (steps: StateStep[], t: number, cue: (a: Cue | undefined, d?: number) => number) => {
  let cur = -1;
  steps.forEach((s, i) => { if (t >= cue(s.at, i * 0.6)) cur = i; });
  return cur;
};

// ---- background --------------------------------------------------------------------------------------------------
export const Backdrop: React.FC = () => (
  <>
    <div style={{position: 'absolute', inset: 0, background: S.bg}} />
    <div style={{position: 'absolute', inset: 0, backgroundImage:
      'linear-gradient(rgba(150,200,220,0.045) 2px, transparent 2px), linear-gradient(90deg, rgba(150,200,220,0.045) 2px, transparent 2px)',
      backgroundSize: '72px 72px'}} />
  </>
);
export const Vignette: React.FC = () => (
  <div style={{position: 'absolute', inset: 0, background: 'radial-gradient(ellipse at 50% 42%, transparent 45%, rgba(0,0,0,0.72) 100%)',
    pointerEvents: 'none'}} />
);

// ---- the running clock -------------------------------------------------------------------------------------------
export const fmtClock = (sec: number) => {
  const s = Math.max(0, Math.floor(sec));
  const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), r = s % 60;
  return [h, m, r].map((x) => String(x).padStart(2, '0')).join(':');
};

/** Big = the opening read-out; pill = the small badge that rides at the top of every later scene. */
export const Clock: React.FC<{spec: ClockSpec; t: number; big: number; W: number}> = ({spec, t, big, W}) => {
  const value = fmtClock(spec.from - t * (spec.rate ?? 1));
  const glow = '0 0 18px rgba(255,59,59,0.85), 0 0 46px rgba(255,59,59,0.45)';
  return (
    <>
      {big > 0.01 ? (
        <div style={{position: 'absolute', left: 0, width: W, top: 150 - (1 - big) * 70, textAlign: 'center', opacity: big,
          transform: `scale(${0.55 + 0.45 * big})`, transformOrigin: '50% 0%'}}>
          <div style={{fontFamily: MONO, fontWeight: 600, fontSize: 30, letterSpacing: 10, color: S.text}}>
            {spec.label ?? 'SURVIVAL CLOCK'}</div>
          <div style={{fontFamily: MONO, fontWeight: 700, fontSize: 168, lineHeight: 1.05, color: S.red, textShadow: glow, letterSpacing: 4}}>
            {value}</div>
        </div>
      ) : null}
      {big < 0.99 ? (
        <div style={{position: 'absolute', left: 0, width: W, top: 118, display: 'flex', justifyContent: 'center', opacity: 1 - big}}>
          <div style={{display: 'flex', alignItems: 'center', gap: 16, padding: '10px 28px', borderRadius: 40, border: `3px solid ${S.red}`,
            background: 'rgba(30,8,8,0.82)', boxShadow: '0 0 22px rgba(255,59,59,0.35)'}}>
            <div style={{width: 16, height: 16, borderRadius: 8, background: S.red, opacity: 0.55 + 0.45 * Math.round((t * 2) % 1)}} />
            <div style={{fontFamily: MONO, fontWeight: 600, fontSize: 24, letterSpacing: 6, color: S.dim}}>{spec.pillLabel ?? 'SURVIVAL CLOCK'}</div>
            <div style={{fontFamily: MONO, fontWeight: 700, fontSize: 40, color: S.red, textShadow: glow}}>{value}</div>
          </div>
        </div>
      ) : null}
    </>
  );
};

// ---- word-pill captions ------------------------------------------------------------------------------------------
interface Page { words: Word[]; start: number; end: number }
export function paginate(words: Word[]): Page[] {
  const pages: Page[] = [];
  let cur: Word[] = [];
  const flush = () => { if (cur.length) pages.push({words: cur, start: cur[0].start, end: cur[cur.length - 1].end}); cur = []; };
  words.forEach((w, i) => {
    const prev = words[i - 1];
    const chars = cur.reduce((n, x) => n + x.word.length + 1, 0);
    if (cur.length && (cur.length >= 3 || chars + w.word.length > 18 || (prev && w.start - prev.end > 0.35))) flush();
    cur.push(w);
    if (/[.,!?;:]$/.test(w.word)) flush();
  });
  flush();
  return pages;
}

export const Captions: React.FC<{words: Word[]; t: number; W: number; H: number; red: string[]; plain: string[]}> = ({words, t, W, H, red, plain}) => {
  const pages = paginate(words);
  const i = pages.findIndex((p, k) => t >= p.start - 0.06 && t < (pages[k + 1]?.start ?? p.end + 0.45) - 0.06 && t < p.end + 0.45);
  if (i < 0) return null;
  const page = pages[i];
  const p = pop(t, page.start - 0.06, 0.2);
  const redSet = new Set(red.map(normWord)), plainSet = new Set(plain.map(normWord));
  return (
    <div style={{position: 'absolute', left: W * 0.07, width: W * 0.86, top: H * 0.695, display: 'flex', flexWrap: 'wrap',
      justifyContent: 'center', alignItems: 'center', gap: '6px 16px', ...popStyle(p)}}>
      {page.words.map((w, k) => {
        const next = page.words[k + 1];
        const active = t >= w.start - 0.04 && t < (next ? next.start - 0.04 : w.end + 0.45);
        const n = normWord(w.word);
        const isRed = redSet.has(n);
        const pill = active && !plainSet.has(n);
        return (
          <span key={k} style={{fontFamily: SANS, fontWeight: 900, fontSize: 74, lineHeight: 1.18, letterSpacing: -0.5,
            color: pill ? (isRed ? S.text : S.ink) : S.text, background: pill ? (isRed ? S.red : S.yellow) : 'transparent',
            borderRadius: 18, padding: '0 14px', WebkitTextStroke: pill ? undefined : '3px #000', paintOrder: 'stroke fill',
            textShadow: pill ? undefined : '0 4px 14px rgba(0,0,0,0.9)', transform: pill ? 'scale(1.06)' : undefined}}>
            {w.word}
          </span>
        );
      })}
    </div>
  );
};

// ---- stamp -------------------------------------------------------------------------------------------------------
export const Stamp: React.FC<{spec: StampSpec; at: number; t: number; W: number; H: number}> = ({spec, at, t, W, H}) => {
  if (t < at) return null;
  const x = clamp01((t - at) / 0.22);
  const col = toneColor(spec.tone ?? 'red');
  const shake = t - at < 0.3 ? Math.sin((t - at) * 90) * 6 * (1 - (t - at) / 0.3) : 0;
  return (
    <div style={{position: 'absolute', left: 0, width: W, top: (spec.y ?? 0.4) * H, display: 'flex', justifyContent: 'center',
      transform: `translate(${shake}px, -50%) rotate(${spec.rotate ?? -8}deg) scale(${1.6 - 0.6 * easeOut(x)})`, opacity: clamp01(x * 3)}}>
      <div style={{border: `9px solid ${col}`, borderRadius: 14, background: 'rgba(12,4,4,0.9)', padding: '14px 40px 22px',
        boxShadow: `0 0 40px ${col}66`, textAlign: 'center', maxWidth: W * 0.86}}>
        {spec.kicker ? <div style={{fontFamily: MONO, fontWeight: 600, fontSize: 30, letterSpacing: 8, color: S.text}}>{spec.kicker}</div> : null}
        <div style={{fontFamily: COND, fontWeight: 900, fontSize: 132, lineHeight: 0.95, color: col, textTransform: 'uppercase'}}>{spec.text}</div>
      </div>
    </div>
  );
};

// ---- small parts -------------------------------------------------------------------------------------------------
export const Pill: React.FC<{text: string; tone?: Tone; size?: number}> = ({text, tone = 'red', size = 30}) => (
  <div style={{display: 'inline-flex', alignItems: 'center', gap: 14, padding: '12px 26px', borderRadius: 50,
    background: tone === 'red' ? 'rgba(255,59,59,0.92)' : `${toneColor(tone)}26`, border: `3px solid ${toneColor(tone)}`}}>
    <div style={{width: 14, height: 14, borderRadius: 7, background: tone === 'red' ? S.text : toneColor(tone)}} />
    <div style={{fontFamily: MONO, fontWeight: 700, fontSize: size, letterSpacing: 3, color: S.text, textTransform: 'uppercase'}}>{text}</div>
  </div>
);

export const MonoLabel: React.FC<{children: React.ReactNode; color?: string; size?: number}> = ({children, color = S.dim, size = 26}) => (
  <div style={{fontFamily: MONO, fontWeight: 600, fontSize: size, letterSpacing: 5, color, textTransform: 'uppercase'}}>{children}</div>
);

const Card: React.FC<{children: React.ReactNode; style?: React.CSSProperties}> = ({children, style}) => (
  <div style={{border: `3px solid ${S.line}`, borderRadius: 18, background: S.panel, padding: '22px 28px', ...style}}>{children}</div>
);

const fmtNum = (v: number, d = 0) => v.toLocaleString('en-US', {minimumFractionDigits: d, maximumFractionDigits: d});

// ---- widgets -----------------------------------------------------------------------------------------------------
const Gauge: React.FC<{from: number; to: number; k: number; labels: [string, string, string]}> = ({from, to, k, labels}) => {
  const v = from + (to - from) * easeInOut(k);
  const W = 820, R = 330, cx = W / 2, cy = 380;
  const ang = (f: number) => Math.PI + f * Math.PI;
  const pt = (f: number, r: number) => [cx + Math.cos(ang(f)) * r, cy + Math.sin(ang(f)) * r];
  const arc = (a: number, b: number, r: number) => { const [x0, y0] = pt(a, r), [x1, y1] = pt(b, r); return `M${x0} ${y0} A${r} ${r} 0 0 1 ${x1} ${y1}`; };
  const [nx, ny] = pt(v, R - 40);
  return (
    <svg width={W} height={450} viewBox={`0 0 ${W} 450`}>
      <path d={arc(0, 0.27, R)} stroke={S.red} strokeWidth={34} fill="none" />
      <path d={arc(0.29, 0.49, R)} stroke="rgba(243,245,247,0.22)" strokeWidth={34} fill="none" />
      <path d={arc(0.51, 1, R)} stroke={S.cyan} strokeWidth={34} fill="none" />
      {[0.25, 0.5, 0.75].map((f) => { const [a, b] = pt(f, R - 30), [c, d] = pt(f, R + 30); return <line key={f} x1={a} y1={b} x2={c} y2={d} stroke={S.bg} strokeWidth={8} />; })}
      <text x={pt(0, R)[0] + 4} y={cy + 56} fill={S.text} fontFamily={COND} fontWeight={900} fontSize={54} textAnchor="middle">{labels[0]}</text>
      <text x={cx} y={cy - R - 32} fill={S.text} fontFamily={COND} fontWeight={900} fontSize={54} textAnchor="middle">{labels[1]}</text>
      <text x={pt(1, R)[0] - 4} y={cy + 56} fill={S.text} fontFamily={COND} fontWeight={900} fontSize={54} textAnchor="middle">{labels[2]}</text>
      <line x1={cx} y1={cy} x2={nx} y2={ny} stroke={S.text} strokeWidth={12} strokeLinecap="round" />
      <circle cx={cx} cy={cy} r={22} fill={S.text} />
    </svg>
  );
};

const Wave: React.FC<{t: number; spike: number; label?: string; spikeLabel?: string}> = ({t, spike, label, spikeLabel}) => {
  const W = 930, H = 330;
  const pts: string[] = [];
  for (let x = 0; x <= W; x += 6) {
    let y = H / 2 + Math.sin(x / 38 - t * 6) * 34;
    if (t >= spike) {
      const sx = W * 0.62, d = (x - sx) / 22, decay = Math.exp(-Math.max(0, t - spike) * 0.4);
      y -= Math.exp(-d * d) * 115 * decay * (Math.sin(x / 6) > 0 ? 1 : -0.8);
    }
    pts.push(`${x},${y.toFixed(1)}`);
  }
  const on = t >= spike;
  return (
    <div style={{position: 'relative', width: W, height: H, border: `3px solid ${S.line}`, borderRadius: 14,
      backgroundImage: 'linear-gradient(rgba(150,200,220,0.12) 1px, transparent 1px), linear-gradient(90deg, rgba(150,200,220,0.12) 1px, transparent 1px)',
      backgroundSize: '45px 45px', overflow: 'hidden'}}>
      <svg width={W} height={H} style={{position: 'absolute', inset: 0}}>
        <polyline points={pts.join(' ')} fill="none" stroke={on ? S.cyan : S.cyan} strokeWidth={6}
          style={{filter: `drop-shadow(0 0 8px ${S.cyan})`}} />
      </svg>
      {label ? <div style={{position: 'absolute', left: 18, top: 12}}><MonoLabel>{label}</MonoLabel></div> : null}
      {on && spikeLabel ? <div style={{position: 'absolute', left: W * 0.66, top: 18, fontFamily: COND, fontWeight: 900, fontSize: 64,
        color: S.red}}>{spikeLabel}</div> : null}
    </div>
  );
};

const CompareCard: React.FC<{side: CompareSide}> = ({side}) => {
  const col = toneColor(side.tone);
  return (
    <Card style={{flex: 1, borderColor: `${col}AA`, background: `${col}14`, display: 'flex', flexDirection: 'column', gap: 10}}>
      <MonoLabel color={col}>{side.title}</MonoLabel>
      <div style={{display: 'flex', alignItems: 'center', gap: 18}}>
        {side.icon ? <Icon name={side.icon} size={150} color={col} /> : null}
        <div style={{fontFamily: COND, fontWeight: 900, fontSize: 130, lineHeight: 0.9, color: col}}>
          {side.value}<span style={{fontSize: 56}}> {side.unit ?? ''}</span></div>
      </div>
      <div style={{fontFamily: COND, fontWeight: 900, fontSize: 76, color: col, textTransform: 'uppercase'}}>{side.label}</div>
    </Card>
  );
};

export const WidgetView: React.FC<{w: Widget; idx: number}> = ({w, idx}) => {
  const {t} = useS();
  const cue = useCue();
  const at = cue(w.at, 0.35 + idx * 0.45);
  const p = pop(t, at);
  let body: React.ReactNode = null;
  switch (w.type) {
    case 'state': {
      const cur = stepAt(w.states, t, cue);
      const s = w.states[Math.max(0, cur)];
      const col = toneColor(s.tone ?? 'ok');
      const flip = cur >= 0 ? pop(t, cue(s.at), 0.2) : {o: 1, s: 1, y: 0, k: 1};
      body = (
        <Card style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 20}}>
          <MonoLabel>{w.label}</MonoLabel>
          <div style={{border: `4px solid ${col}`, background: `${col}22`, borderRadius: 12, padding: '8px 26px', fontFamily: COND,
            fontWeight: 900, fontSize: 80, color: col, textTransform: 'uppercase', transform: `scale(${flip.s})`,
            boxShadow: `0 0 26px ${col}55`}}>{s.text}</div>
        </Card>
      );
      break;
    }
    case 'gauge': {
      const k = clamp01((t - at) / (w.dur ?? 1.6));
      const cur = w.caption ? stepAt(w.caption, t, cue) : -1;
      const c = cur >= 0 && w.caption ? w.caption[cur] : null;
      body = (
        <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
          <Gauge from={w.from} to={w.to} k={k} labels={w.labels ?? ['E', '½', 'F']} />
          {c ? <div style={{fontFamily: COND, fontWeight: 900, fontSize: 84, color: toneColor(c.tone ?? 'red'), textTransform: 'uppercase',
            marginTop: 6}}>{c.text}</div> : null}
        </div>
      );
      break;
    }
    case 'counter': {
      const k = easeOut((t - at) / (w.dur ?? 1.2));
      const v = w.from + (w.to - w.from) * k;
      const size = w.size ?? 210;
      body = (
        <div>
          {w.label ? <MonoLabel color={S.cyan}>{w.label}</MonoLabel> : null}
          <div style={{fontFamily: COND, fontWeight: 900, fontSize: size, lineHeight: 0.92, color: toneColor(w.tone ?? 'white')}}>
            {fmtNum(v, w.decimals ?? 0)}<span style={{fontSize: size * 0.42}}>{w.unit && !w.unit.startsWith('%') ? ' ' : ''}{w.unit ?? ''}</span></div>
          {w.sub ? <MonoLabel size={28} color={S.text}>{w.sub}</MonoLabel> : null}
        </div>
      );
      break;
    }
    case 'bar': {
      const k = easeInOut((t - at) / (w.dur ?? 1.4));
      const v = w.from + (w.to - w.from) * k;
      const col = toneColor(w.tone ?? 'info');
      body = (
        <div>
          <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: 10}}>
            <MonoLabel>{w.label ?? ''}</MonoLabel>
            {w.right ? <MonoLabel color={S.red}>{w.right}</MonoLabel> : <MonoLabel color={S.text}>{`${Math.round(v * 100)}%`}</MonoLabel>}
          </div>
          <div style={{height: 54, border: `3px solid ${S.line}`, borderRadius: 8, padding: 5}}>
            <div style={{height: '100%', width: `${clamp01(v) * 100}%`, borderRadius: 4, background: w.hazard
              ? `repeating-linear-gradient(-45deg, ${S.yellow} 0 22px, #111 22px 44px)` : col, boxShadow: `0 0 18px ${col}66`}} />
          </div>
          {w.ticks ? <div style={{display: 'flex', justifyContent: 'space-between', marginTop: 10}}>
            {w.ticks.map((x, i) => <MonoLabel key={i} size={24} color={i === w.ticks!.length - 1 ? S.text : S.dim}>{x}</MonoLabel>)}</div> : null}
        </div>
      );
      break;
    }
    case 'tiles': {
      const col = toneColor(w.tone ?? 'info');
      body = (
        <div style={{display: 'flex', gap: 22}}>
          {w.items.map((it, i) => {
            const a = cue(it.at, 0.5 + i * 0.7);
            const f = easeInOut((t - a) / 1.3);
            return (
              <Card key={i} style={{flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 14,
                borderColor: f > 0.02 ? col : S.line, padding: '26px 10px'}}>
                <Icon name={it.icon} size={150} color={f > 0.02 ? col : S.text} fill={f} fillColor={col} />
                <MonoLabel color={S.text}>{it.label}</MonoLabel>
              </Card>
            );
          })}
        </div>
      );
      break;
    }
    case 'row': {
      const col = toneColor(w.tone ?? 'info');
      const k = clamp01((t - at) / (w.dur ?? 1.6));
      const filled = k * w.fill;
      body = (
        <div>
          {w.label ? <MonoLabel>{w.label}</MonoLabel> : null}
          <div style={{display: 'flex', gap: 10, marginTop: 8}}>
            {Array.from({length: w.count}).map((_, i) => (
              <Icon key={i} name={w.icon} size={86} color={i < filled ? col : S.dim} fill={clamp01(filled - i)} fillColor={col} stroke={7} />
            ))}
          </div>
        </div>
      );
      break;
    }
    case 'pill':
      body = <Pill text={w.text} tone={w.tone} />;
      break;
    case 'text':
      body = <div style={{fontFamily: w.mono ? MONO : COND, fontWeight: w.mono ? 600 : 900, fontSize: w.size ?? 76, lineHeight: 1,
        color: toneColor(w.tone ?? 'white'), textTransform: 'uppercase', letterSpacing: w.mono ? 4 : 0}}>{w.text}</div>;
      break;
    case 'compare':
      body = <div style={{display: 'flex', gap: 20}}><CompareCard side={w.left} /><CompareCard side={w.right} /></div>;
      break;
    case 'wave':
      body = <Wave t={t} spike={cue(w.spikeAt, 1e6)} label={w.label} spikeLabel={w.spikeLabel} />;
      break;
    case 'photo':
      body = (
        <div>
          <Img src={staticFile(w.src)} style={{width: '100%', height: w.height ?? 420, objectFit: 'cover', borderRadius: 12,
            border: `3px solid ${S.line}`, filter: 'saturate(0.85) contrast(1.05)'}} />
          <MonoLabel size={20}>{w.credit}</MonoLabel>
        </div>
      );
      break;
    case 'icon':
      body = <div style={{display: 'flex', alignItems: 'center', gap: 24}}>
        <Icon name={w.icon} size={w.size ?? 240} color={toneColor(w.tone ?? 'white')} glow />
        {w.label ? <div style={{fontFamily: COND, fontWeight: 900, fontSize: 86, color: toneColor(w.tone ?? 'white')}}>{w.label}</div> : null}
      </div>;
      break;
  }
  return <div style={{...popStyle(p), transformOrigin: '50% 50%'}}>{body}</div>;
};
