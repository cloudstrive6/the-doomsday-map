// The Survival Clock Short: one 1080x1920 composition that plays a SurvivalSpec (scenes keyed to the narration's
// word timings), with the running clock, word-pill captions and a loop crossfade into the cover frame.
import React from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import type {LineSpec, Scene, SurvivalSpec} from './spec';
import {
  Backdrop, COND, Captions, Clock, MONO, MonoLabel, Pill, S, Stamp, SurvivalCtx, Vignette, WidgetView, clamp01, easeInOut,
  easeOut, hash, pop, popStyle, toneColor, useCue, useS,
} from './kit';
import {Icon} from './icons';
import {NightMap} from './NightMap';

const Lines: React.FC<{lines: LineSpec[]; size: number; align?: 'left' | 'center'; stagger?: number; staticShow?: boolean}> = ({lines, size, align = 'center', stagger = 0.22, staticShow}) => {
  const {t, W} = useS();
  const cue = useCue();
  return (
    <div style={{display: 'flex', flexDirection: 'column', alignItems: align === 'center' ? 'center' : 'flex-start'}}>
      {lines.map((l, i) => {
        const p = staticShow ? {o: 1, s: 1, y: 0, k: 1} : pop(t, cue(l.at, 0.1 + i * stagger));
        const fit = Math.min(size, (W * 0.86) / Math.max(1, l.text.length * 0.5));   // Barlow Condensed Black caps ~0.5 em
        return <div key={i} style={{fontFamily: COND, fontWeight: 900, fontSize: fit, lineHeight: 0.92, textTransform: 'uppercase',
          color: toneColor(l.tone ?? 'white'), textAlign: align, textShadow: '0 6px 24px rgba(0,0,0,0.7)', ...popStyle(p)}}>{l.text}</div>;
      })}
    </div>
  );
};

const Checklist: React.FC<{kicker: string; title: string; sub?: string; items: {text: string; sub?: string; checked?: boolean; at?: number}[];
  tilt?: number; width: number; size?: number}> = ({kicker, title, sub, items, tilt = -2, width, size = 58}) => {
  const {t} = useS();
  return (
    <div style={{width, background: S.paper, borderRadius: 10, transform: `rotate(${tilt}deg)`, boxShadow: '0 30px 80px rgba(0,0,0,0.7)',
      overflow: 'hidden'}}>
      <div style={{background: '#C62424', padding: '10px 24px', fontFamily: MONO, fontWeight: 700, fontSize: 26, letterSpacing: 6, color: '#fff'}}>{kicker}</div>
      <div style={{padding: '18px 30px 26px'}}>
        <div style={{fontFamily: COND, fontWeight: 900, fontSize: size * 1.35, color: S.ink, lineHeight: 1}}>{title}</div>
        {sub ? <div style={{fontFamily: MONO, fontWeight: 600, fontSize: 22, letterSpacing: 3, color: S.inkDim, marginBottom: 10}}>{sub}</div> : null}
        {items.map((it, i) => {
          const on = it.checked ?? (it.at !== undefined ? t >= it.at : true);
          const k = it.at !== undefined ? clamp01((t - it.at) / 0.25) : 1;
          return (
            <div key={i} style={{display: 'flex', alignItems: 'center', gap: 20, padding: '8px 0', borderTop: i ? '2px solid rgba(26,26,26,0.12)' : undefined}}>
              <div style={{width: size * 0.95, height: size * 0.95, border: `5px solid ${S.ink}`, borderRadius: 6, flex: 'none', position: 'relative'}}>
                {on ? <svg viewBox="0 0 100 100" style={{position: 'absolute', inset: -8, width: '130%', height: '130%'}}>
                  <path d="M14 52 L40 78 L92 14" fill="none" stroke="#C62424" strokeWidth={16} strokeLinecap="round" strokeLinejoin="round"
                    strokeDasharray={160} strokeDashoffset={160 * (1 - k)} /></svg> : null}
              </div>
              <div>
                <div style={{fontFamily: COND, fontWeight: 900, fontSize: size, lineHeight: 1, color: S.ink, textTransform: 'uppercase'}}>{it.text}</div>
                {it.sub ? <div style={{fontFamily: MONO, fontWeight: 600, fontSize: 26, letterSpacing: 2, color: S.inkDim}}>{it.sub}</div> : null}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

/** Highlighter sweeps: each mark is a substring, optionally with its own word cue ({text, at}). */
const Marked: React.FC<{text: string; marks: (string | {text: string; at: number})[]; base: number; t: number}> = ({text, marks, base, t}) => {
  const ms = marks.map((m) => typeof m === 'string' ? {text: m, at: base} : m);
  if (!ms.length) return <>{text}</>;
  const parts: {s: string; at: number | null}[] = [];
  let rest = text;
  while (rest.length) {
    let best = -1, mk = ms[0];
    for (const m of ms) { const i = rest.indexOf(m.text); if (i >= 0 && (best < 0 || i < best)) { best = i; mk = m; } }
    if (best < 0) { parts.push({s: rest, at: null}); break; }
    if (best > 0) parts.push({s: rest.slice(0, best), at: null});
    parts.push({s: mk.text, at: mk.at});
    rest = rest.slice(best + mk.text.length);
  }
  return <>{parts.map((p, i) => p.at !== null
    ? <span key={i} style={{backgroundImage: `linear-gradient(${S.yellow}, ${S.yellow})`, backgroundRepeat: 'no-repeat',
      backgroundSize: `${easeOut((t - p.at) / 0.45) * 100}% 78%`, backgroundPosition: '0 70%', padding: '0 2px'}}>{p.s}</span>
    : <span key={i}>{p.s}</span>)}</>;
};

const SceneView: React.FC<{scene: Scene; spec: SurvivalSpec; frozen?: boolean}> = ({scene, spec, frozen}) => {
  const {t, W, H} = useS();
  const cue = useCue();
  const top = 250;
  switch (scene.kind) {
    case 'cover':
      return (
        <div style={{position: 'absolute', left: 0, width: W, top: 470, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 50}}>
          <Lines lines={scene.lines} size={150} staticShow />
          {scene.checklist ? <Checklist kicker="EMERGENCY SURVIVAL CHECKLIST" title="" items={scene.checklist.items.map((x) => ({text: x.text, checked: x.checked}))}
            width={W * 0.8} size={50} tilt={-3} /> : null}
        </div>
      );
    case 'map':
      return (
        <>
          <NightMap map={scene.map} t={t} W={W} H={H} />
          {scene.lines ? <div style={{position: 'absolute', left: 0, width: W, top: H * 0.38}}><Lines lines={scene.lines} size={140} /></div> : null}
        </>
      );
    case 'stat': {
      const p = pop(t, cue(undefined, 0.05), 0.4);
      const n = Number(scene.value);
      const counting = scene.countFrom !== undefined && Number.isFinite(n);
      const cAt = scene.countAt !== undefined ? cue(scene.countAt, 0.9) : scene.start + 0.9;   // the count lands on its spoken number
      const shown = counting ? Math.round(scene.countFrom! + (n - scene.countFrom!) * easeOut((t - (cAt - 0.75)) / 0.75)) : scene.value;
      const col = toneColor(scene.tone ?? 'red');
      const b = scene.bar;
      const bk = b ? easeInOut((t - cue(b.at, 0.6)) / (b.dur ?? 1.6)) : 0;
      return (
        <div style={{position: 'absolute', left: 70, width: W - 140, top: 520}}>
          <div style={{display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', ...popStyle(p)}}>
            <div>
              <div style={{fontFamily: COND, fontWeight: 900, fontSize: 380, lineHeight: 0.8, color: col, textShadow: `0 0 40px ${col}44`}}>{shown}</div>
              <div style={{fontFamily: COND, fontWeight: 900, fontSize: 96, color: col, marginTop: 10}}>{scene.unit}</div>
            </div>
            {scene.aside ? <div style={{textAlign: 'right', maxWidth: 420, paddingBottom: 30}}>
              <MonoLabel color={S.text} size={30}>{scene.aside.title}</MonoLabel>
              {scene.aside.sub ? <MonoLabel size={24}>{scene.aside.sub}</MonoLabel> : null}</div> : null}
          </div>
          {b ? (
            <div style={{marginTop: 70, opacity: clamp01((t - scene.start - 0.3) / 0.3)}}>
              {b.label ? <div style={{marginBottom: 12}}><MonoLabel color={S.red}>{b.label}</MonoLabel></div> : null}
              <div style={{height: 76, border: `3px solid ${S.line}`, borderRadius: 8, padding: 6}}>
                <div style={{height: '100%', width: `${(b.from + (b.to - b.from) * bk) * 100}%`, borderRadius: 4,
                  background: b.hazard ? `repeating-linear-gradient(-45deg, ${S.yellow} 0 26px, #111 26px 52px)` : toneColor(b.tone ?? 'red')}} />
              </div>
              <div style={{display: 'flex', justifyContent: 'space-between', marginTop: 12}}>
                {b.ticks.map((x, i) => <MonoLabel key={i} size={26} color={i === b.ticks.length - 1 ? S.text : S.dim}>{x}</MonoLabel>)}</div>
            </div>
          ) : null}
        </div>
      );
    }
    case 'phone': {
      let cur = 0;
      scene.states.forEach((s, i) => { if (t >= cue(s.at, i * 1.2)) cur = i; });
      const s = scene.states[cur];
      const col = toneColor(s.tone ?? 'white');
      const red = s.tone === 'red';
      const flip = pop(t, cue(s.at, cur * 1.2), 0.22);
      const enter = pop(t, scene.start, 0.4);
      return (
        <div style={{position: 'absolute', left: (W - 600) / 2, top: 290, width: 600, height: 1000, borderRadius: 70, border: '7px solid #3A414B',
          background: red ? 'linear-gradient(#2A0C0E, #12080A)' : '#0E1217', boxShadow: red ? '0 0 80px rgba(255,59,59,0.35)' : '0 30px 80px rgba(0,0,0,0.6)',
          ...popStyle(enter)}}>
          <div style={{display: 'flex', justifyContent: 'space-between', padding: '34px 48px', fontFamily: MONO, fontWeight: 700, fontSize: 30, color: S.text}}>
            <span>{scene.time ?? '21:47'}</span><span style={{color: red ? S.red : S.text}}>{red ? 'SOS' : '●●●'}</span></div>
          <div style={{position: 'absolute', left: 48, right: 48, top: 110, display: 'flex', flexDirection: 'column', gap: 16, opacity: 0.25}}>
            {[0.7, 0.9, 0.5].map((w, i) => <div key={i} style={{height: 22, width: `${w * 100}%`, borderRadius: 11, background: S.text}} />)}</div>
          <div style={{position: 'absolute', left: 0, right: 0, top: 330, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 22,
            transform: `scale(${flip.s})`}}>
            <Icon name={s.icon} size={230} color={col} stroke={8} glow={red} />
            <div style={{fontFamily: COND, fontWeight: 900, fontSize: 104, color: col, lineHeight: 0.95, textAlign: 'center'}}>{s.title}</div>
            {s.sub ? <div style={{maxWidth: 500, textAlign: 'center'}}><MonoLabel size={30} color={red ? S.red : S.dim}>{s.sub}</MonoLabel></div> : null}
          </div>
        </div>
      );
    }
    case 'document': {
      const enter = pop(t, scene.start, 0.45);
      const dim = scene.dimAt !== undefined ? cue(scene.dimAt, 1e6) : 1e6;
      const dt = t - dim;
      const flicker = dt < 0 ? 0 : dt < 1.1 ? (hash(Math.floor(dt * 14)) > 0.45 ? 0.62 : 0.12) : 0.5;
      const sw = scene.stopwatchAt !== undefined ? cue(scene.stopwatchAt, 1e6) : 1e6;
      return (
        <>
          <div style={{position: 'absolute', left: 44, width: W - 88, top: 250, background: S.paper, borderRadius: 8, padding: '40px 44px 44px',
            transform: `rotate(-1.5deg) ${popStyle(enter).transform}`, opacity: enter.o, boxShadow: '0 40px 90px rgba(0,0,0,0.75)'}}>
            <div style={{fontFamily: MONO, fontWeight: 700, fontSize: 28, letterSpacing: 5, color: '#B42020', borderBottom: '3px solid #B42020', paddingBottom: 8}}>{scene.header}</div>
            {scene.kicker ? <div style={{fontFamily: MONO, fontWeight: 600, fontSize: 24, letterSpacing: 3, color: S.inkDim, marginTop: 14}}>{scene.kicker}</div> : null}
            <div style={{fontFamily: MONO, fontWeight: 700, fontSize: 64, color: S.ink, lineHeight: 1.1, margin: '10px 0 30px'}}>{scene.title}</div>
            {scene.lines.map((l, i) => {
              const a = cue(l.at, 0.4 + i * 0.5);
              const p = pop(t, a, 0.3);
              return <div key={i} style={{fontFamily: MONO, fontWeight: l.bold ? 700 : 500, fontSize: 42, lineHeight: 1.42, color: S.ink, margin: '14px 0', ...popStyle(p)}}>
                <Marked text={l.text} t={t} base={a + 0.25} marks={(l.mark ?? []).map((m) => typeof m === 'string' ? m : {text: m.text, at: cue(m.at, 0.5)})} /></div>;
            })}
            {scene.footer ? <div style={{fontFamily: MONO, fontWeight: 700, fontSize: 24, letterSpacing: 5, color: '#B42020', borderTop: '3px solid #B42020',
              paddingTop: 8, marginTop: 18}}>{scene.footer}</div> : null}
            {scene.credit ? <div style={{fontFamily: MONO, fontSize: 24, color: S.inkDim, marginTop: 10}}>{scene.credit}</div> : null}
          </div>
          {t >= sw ? (
            <div style={{position: 'absolute', right: 60, top: 1000, width: 250, height: 250, borderRadius: 125, background: '#F5F1E6',
              border: '10px solid #2A2A2A', boxShadow: '0 20px 50px rgba(0,0,0,0.6)', ...popStyle(pop(t, sw, 0.3))}}>
              <div style={{position: 'absolute', left: 117, top: 20, width: 6, height: 105, background: '#C62424', borderRadius: 3,
                transformOrigin: '50% 100%', transform: `rotate(${(t - sw) * 36}deg)`}} />
              <div style={{position: 'absolute', left: 0, right: 0, top: 150, textAlign: 'center', fontFamily: MONO, fontWeight: 700, fontSize: 30, color: S.ink}}>
                {`00:${String(Math.floor(t - sw)).padStart(2, '0')}.${Math.floor(((t - sw) % 1) * 10)}`}</div>
            </div>
          ) : null}
          {flicker > 0 && !frozen ? <div style={{position: 'absolute', inset: 0, background: '#000', opacity: flicker}} /> : null}
        </>
      );
    }
    case 'rule': {
      const p = pop(t, scene.start, 0.35);
      const flow = clamp01((t - scene.start - 0.4) / 0.6);
      return (
        <div style={{position: 'absolute', left: 70, width: W - 140, top: 270}}>
          <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', ...popStyle(p)}}>
            <div style={{fontFamily: COND, fontWeight: 900, fontSize: 400, lineHeight: 0.8, color: S.red}}>{scene.num}</div>
            {scene.icon ? <div style={{position: 'relative'}}>
              <Icon name={scene.icon} size={260} color={S.text} stroke={7} />
              {scene.icon === 'tap' ? <div style={{position: 'absolute', left: 260 * 0.585, top: 260 * 0.93, width: 260 * 0.1, height: 150 * flow,
                background: S.blue, borderRadius: 4, boxShadow: `0 0 20px ${S.blue}`}} /> : null}
            </div> : null}
          </div>
          <div style={{borderTop: `3px solid ${S.line}`, margin: '34px 0 22px', paddingTop: 18}}><MonoLabel>{scene.kicker}</MonoLabel></div>
          <Lines lines={scene.lines} size={150} align="left" />
        </div>
      );
    }
    case 'board':
      return (
        <div style={{position: 'absolute', left: 40, width: W - 80, top: top - 30, height: 1010, display: 'flex', flexDirection: 'column', gap: 26,
          border: `3px solid ${S.line}`, borderRadius: 22, background: 'rgba(10,13,17,0.72)', padding: '30px 34px', boxSizing: 'border-box'}}>
          <div style={{display: 'flex', alignItems: 'center', gap: 30, ...popStyle(pop(t, scene.start, 0.35))}}>
            {scene.num ? <div style={{fontFamily: COND, fontWeight: 900, fontSize: 230, lineHeight: 0.8, color: S.red}}>{scene.num}</div> : null}
            <div>
              <div style={{fontFamily: COND, fontWeight: 900, fontSize: 104, lineHeight: 0.92, color: S.text, textTransform: 'uppercase'}}>{scene.title}</div>
              {scene.sub ? <MonoLabel size={26}>{scene.sub}</MonoLabel> : null}
            </div>
          </div>
          <div style={{flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'space-evenly', gap: 26}}>
            {scene.widgets.map((w, i) => <WidgetView key={i} w={w} idx={i} />)}
          </div>
        </div>
      );
    case 'grid': {
      return (
        <div style={{position: 'absolute', left: 50, width: W - 100, top: 230}}>
          <div style={{textAlign: 'center', marginBottom: 22}}><MonoLabel color={S.text} size={28}>{scene.title}</MonoLabel></div>
          <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 22, position: 'relative'}}>
            {scene.items.map((it, i) => (
              <div key={i} style={{height: 420, border: `3px solid ${S.line}`, borderRadius: 14, background: S.panel, padding: 26, display: 'flex',
                flexDirection: 'column', justifyContent: 'space-between', ...popStyle(pop(t, scene.start + 0.15 + i * 0.25))}}>
                <div style={{fontFamily: COND, fontWeight: 900, fontSize: 230, lineHeight: 0.85, color: 'transparent', WebkitTextStroke: `3px ${S.dim}`}}>{it.num}</div>
                <div style={{textAlign: i % 2 ? 'right' : 'left'}}><MonoLabel color={S.text} size={32}>{it.label}</MonoLabel></div>
              </div>
            ))}
            {scene.badge ? (
              <div style={{position: 'absolute', left: '50%', top: '50%', width: 220, height: 220, marginLeft: -110, marginTop: -110, borderRadius: 110,
                background: S.red, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', boxShadow: '0 0 60px rgba(255,59,59,0.6)',
                ...popStyle(pop(t, scene.start + 1.3, 0.35))}}>
                <div style={{fontFamily: COND, fontWeight: 900, fontSize: 104, lineHeight: 0.9, color: '#fff'}}>{scene.badge.text}</div>
                {scene.badge.sub ? <div style={{fontFamily: MONO, fontWeight: 700, fontSize: 26, letterSpacing: 4, color: '#fff'}}>{scene.badge.sub}</div> : null}
              </div>
            ) : null}
          </div>
        </div>
      );
    }
    case 'checklist': {
      const n = scene.items.length;
      const span = Math.max(1, scene.end - scene.start - 1.5);
      return (
        <div style={{position: 'absolute', left: 0, width: W, top: 240, display: 'flex', justifyContent: 'center', ...popStyle(pop(t, scene.start, 0.4))}}>
          <Checklist kicker={scene.kicker} title={scene.title} sub={scene.sub} width={W * 0.9} size={66}
            items={scene.items.map((it, i) => ({text: it.text, sub: it.sub, at: cue(it.at, 0.4 + (i * span) / (n + 1))}))} />
        </div>
      );
    }
    case 'slam':
      return (
        <div style={{position: 'absolute', left: 0, width: W, top: H * 0.3, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 20}}>
          {scene.kicker ? <MonoLabel color={S.text} size={30}>{scene.kicker}</MonoLabel> : null}
          <Lines lines={scene.lines} size={170} />
          {scene.sub ? <Pill text={scene.sub} /> : null}
        </div>
      );
  }
  return null;
};

const SceneLayer: React.FC<{scene: Scene; spec: SurvivalSpec; t: number; W: number; H: number; frozen?: boolean}> = ({scene, spec, t, W, H, frozen}) => (
  <SurvivalCtx.Provider value={{t, words: spec.words, sceneStart: scene.start, sceneEnd: scene.end, W, H}}>
    {scene.bgMap ? <NightMap map={{dim: 0.55, ...scene.bgMap}} t={t} W={W} H={H} showStatus={false} /> : null}
    <SceneView scene={scene} spec={spec} frozen={frozen} />
    {scene.stamp ? <Stamp spec={scene.stamp} at={resolveStamp(scene, spec)} t={t} W={W} H={H} /> : null}
    {scene.tag ? <div style={{position: 'absolute', left: 40, top: 212, padding: '6px 16px', border: `3px solid ${S.red}`, background: 'rgba(20,6,6,0.85)',
      fontFamily: MONO, fontWeight: 700, fontSize: 28, letterSpacing: 5, color: S.red}}>{scene.tag}</div> : null}
  </SurvivalCtx.Provider>
);
function resolveStamp(scene: Scene, spec: SurvivalSpec) {
  const at = scene.stamp!.at;
  if (typeof at === 'number') return at;
  const m = /^@([^#+]+?)(?:#(\d+))?([+-][\d.]+)?$/.exec(at);
  if (!m) return scene.start;
  const target = m[1].toLowerCase().replace(/[^a-z0-9½]/g, '');
  let n = Number(m[2] ?? 1);
  for (const w of spec.words) if (w.start >= scene.start - 0.05 && w.word.toLowerCase().replace(/[^a-z0-9½]/g, '') === target && --n === 0) return w.start + Number(m[3] ?? 0);
  return scene.start;
}

/** Clock size: 1 = big read-out, 0 = top pill; eased over 0.4 s whenever a scene changes it. */
function bigness(spec: SurvivalSpec, t: number) {
  const mode = (x: number) => {
    const sc = spec.scenes.find((s) => x >= s.start && x < s.end);
    if (sc?.clock === 'hide') return -1;
    if (sc?.clock) return sc.clock === 'big' ? 1 : 0;
    return x < (spec.clock.bigUntil ?? 6) ? 1 : 0;
  };
  let acc = 0;
  // look ahead, so the big clock has shrunk by the time the next scene's content arrives
  for (let i = 0; i < 8; i++) acc += Math.max(0, mode(t + i * 0.05));
  return easeInOut(acc / 8);
}

export const SurvivalShort: React.FC<{spec: SurvivalSpec}> = ({spec}) => {
  const frame = useCurrentFrame();
  const {fps, width: W, height: H} = useVideoConfig();
  const t = frame / fps;
  const scene = spec.scenes.find((s) => t >= s.start && t < s.end) ?? spec.scenes[spec.scenes.length - 1];
  const loop = spec.loopSeconds ?? 0;
  const k = loop > 0 ? easeInOut((t - (spec.durationSeconds - loop)) / loop) : 0;
  const cover = spec.scenes[0];
  const hidden = scene.clock === 'hide';
  return (
    <AbsoluteFill style={{background: S.bg, overflow: 'hidden'}}>
      <Backdrop />
      {/* loop: the closing scene fades to the dark ground in the first half, the cover fades up in the second half
          (a straight crossfade double-exposed two headline stacks, review 2026-11-17) */}
      <AbsoluteFill style={{opacity: 1 - clamp01(k * 2)}}>
        <SceneLayer scene={scene} spec={spec} t={t} W={W} H={H} />
        {!hidden ? <Clock spec={spec.clock} t={t} big={bigness(spec, t)} W={W} /> : null}
      </AbsoluteFill>
      <Vignette />
      {k > 0.5 && cover ? (
        <AbsoluteFill style={{opacity: clamp01(k * 2 - 1)}}>
          <Backdrop />
          <SceneLayer scene={cover} spec={spec} t={0} W={W} H={H} frozen />
          {/* the clock exactly as frame 0 draws it, so the seam matches */}
          {cover.clock !== 'hide' ? <Clock spec={spec.clock} t={0} big={bigness(spec, 0)} W={W} /> : null}
          <Vignette />
        </AbsoluteFill>
      ) : null}
      {k < 0.5 ? <Captions words={spec.words} t={t} W={W} H={H} red={spec.redWords ?? []} plain={spec.plainWords ?? []} /> : null}
      {k >= 0.5 && spec.words.length ? <div style={{position: 'absolute', inset: 0, opacity: clamp01((k - 0.5) * 2)}}>
        <Captions words={spec.words} t={spec.words[0].start + 0.01} W={W} H={H} red={spec.redWords ?? []} plain={spec.plainWords ?? []} /></div> : null}
      {spec.source ? <div style={{position: 'absolute', left: 60, right: 60, top: H * 0.815, textAlign: 'center', fontFamily: MONO, fontWeight: 600,
        fontSize: 24, letterSpacing: 2, color: 'rgba(243,245,247,0.72)'}}>{spec.source}</div> : null}
    </AbsoluteFill>
  );
};

export const survivalMeta = ({props}: {props: {spec: SurvivalSpec}}) => ({
  durationInFrames: Math.max(1, Math.ceil(props.spec.durationSeconds * props.spec.fps)),
  fps: props.spec.fps, width: props.spec.width, height: props.spec.height,
});
