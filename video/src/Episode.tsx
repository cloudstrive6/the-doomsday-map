import React from 'react';
import {AbsoluteFill, Audio, Sequence, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import type {Episode as EpisodeT, Shot} from './scene';
import {C, COND, FONT, MONO, clamp01} from './theme';
import {Globe} from './components/Globe';
import {RegionMap} from './components/RegionMap';
import {CityMap} from './components/CityMap';
import {LabelScope} from './components/SafeLabel';
import {Banner, Bars, BigNumber, Chapter, Chrome, EndSlate, Isotype, Radar, Split, Stamp, TextCard, Timeline} from './components/Cards';

const ShotBody: React.FC<{shot: Shot; t: number}> = ({shot, t}) => {
  switch (shot.type) {
    case 'globe': return <Globe shot={shot} t={t} />;
    case 'region': return <RegionMap shot={shot} t={t} />;
    case 'city': return <CityMap shot={shot} t={t} />;
    case 'stamp': return <Stamp shot={shot} t={t} />;
    case 'number': return <BigNumber shot={shot} t={t} />;
    case 'chapter': return <Chapter shot={shot} t={t} />;
    case 'isotype': return <Isotype shot={shot} t={t} />;
    case 'bars': return <Bars shot={shot} t={t} />;
    case 'timeline': return <Timeline shot={shot} t={t} />;
    case 'radar': return <Radar shot={shot} t={t} />;
    case 'text': return <TextCard shot={shot} t={t} />;
    case 'split': return <Split shot={shot} t={t} />;
    case 'endslate': return <EndSlate shot={shot} t={t} />;
    default: return <AbsoluteFill style={{background: C.bg}} />;
  }
};

// Every shot keeps moving (house rule: no still stretch over 6 s). Maps and globes without an authored camera move
// get a slow drift; cards get a slow push-in on the whole card (the HUD chrome stays fixed).
// Motion is a rate, not a total: a fixed zoom spread over a long shot moves too slowly per frame and fails the
// 4 s freeze check (003, 2026-11-09: an 11 s text card, a 7.5 s region map and a globe with an early last key).
function withDrift(shot: Shot): Shot {
  const dur = shot.end - shot.start;
  if ((shot.type === 'region' || shot.type === 'city') && !shot.zoomTo) {
    return {...shot, zoomTo: {center: shot.view.center, widthKm: shot.view.widthKm * Math.max(0.8, 1 - 0.014 * dur)}};
  }
  if (shot.type === 'globe' && shot.camera.length === 1) {
    const c = shot.camera[0];
    return {...shot, camera: [c, {...c, t: c.t + dur, lon: c.lon - Math.max(4, 0.6 * dur), scale: c.scale * (1 + Math.max(0.05, 0.008 * dur))}]};
  }
  if (shot.type === 'globe' && shot.camera.length > 1) {
    // an authored move that ends early leaves the rest of the shot still: keep drifting the same way to the end
    const last = shot.camera[shot.camera.length - 1];
    const prev = shot.camera[shot.camera.length - 2];
    const rest = dur - last.t;
    if (rest > 2) {
      const dLon = last.lon - prev.lon || -4;
      return {...shot, camera: [...shot.camera, {...last, t: dur, lon: last.lon + Math.sign(dLon) * Math.max(2, 0.5 * rest), scale: last.scale * (1 + 0.008 * rest)}]};
    }
  }
  return shot;
}
const CARD_TYPES = new Set(['stamp', 'number', 'chapter', 'isotype', 'bars', 'timeline', 'radar', 'text', 'split', 'endslate']);

// The moving disclaimer runs on its own timeline so it can cross a cut between two moving shots.
const BannerView: React.FC<{banner: NonNullable<EpisodeT['banner']>}> = ({banner}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return <Banner banner={banner} t={frame / fps} dur={banner.end - banner.start} />;
};

// Transitions (2026-11-10 quality pass): every cut used to dip through black (69 dips, about 48 s of dark frames in
// 005, a black frame 0, and a flash that fired inside the fade and peaked grey). Now shots cut straight to each other;
// only chapter cards and the end slate dip, a shot may ask for a dip or a cut on the way in with `transition`, frame 0
// is always a finished frame, and a Short never fades at its end (so it loops).
const DIP_TYPES = new Set(['chapter', 'endslate']);
const DIP = 0.35;
function flashTime(s: Shot): number | undefined {
  if (s.type === 'region') return s.burst?.t;
  if (s.type === 'city') return s.flashT;
  return undefined;
}
function dips(shots: Shot[], i: number, short: boolean): {din: boolean; dout: boolean} {
  const s = shots[i], prev = shots[i - 1], next = shots[i + 1];
  const into = (a: Shot | undefined, b: Shot | undefined) => !!a && !!b && b.transition !== 'cut'
    && (b.transition === 'dip' || DIP_TYPES.has(b.type) || DIP_TYPES.has(a.type));
  const ft = flashTime(s);
  const din = into(prev, s) && !(ft !== undefined && ft >= 0 && ft < DIP + 0.05);   // a flash at the cut: hard cut to white
  const dout = next ? into(s, next) : !short;                             // the long video still fades out at its very end
  return {din, dout};
}

const ShotView: React.FC<{shot: Shot; subtitled?: boolean; din?: boolean; dout?: boolean}> = ({shot: raw, subtitled, din = false, dout = false}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const shot = React.useMemo(() => withDrift(raw), [raw]);
  const dur = shot.end - shot.start;
  // cards push in at about 1% a second (at least 4.5% in total), so long cards keep moving too. The end slate keeps the
  // original gentle 4.5% push: YouTube's end-screen elements sit on fixed spots of it (QC allows it to hold still).
  const slow = 1 + 0.045 * Math.min(1, t / Math.max(1, dur));
  const push = shot.type === 'endslate' ? slow : CARD_TYPES.has(shot.type) ? Math.max(slow, 1 + Math.min(0.14, 0.01 * t)) : 1;
  // the push stops at 14% after 14 s; a longer card then pans sideways inside that zoomed margin (6 px/s, at most
  // 120 px: no new crop) so it never holds still (004, 2026-11-10: a 20 s split card froze 4.2 s and failed QC)
  const pan = CARD_TYPES.has(shot.type) && shot.type !== 'endslate' ? Math.min(120, 6 * Math.max(0, t - 14)) : 0;
  const fadeIn = din ? clamp01(t / DIP) : 1;
  const fadeOut = dout ? clamp01((dur - t) / DIP) : 1;
  const dark = 1 - Math.min(fadeIn, fadeOut);
  // the blast: a short decaying camera shake and an orange afterglow grade over the whole frame
  const ft = flashTime(shot);
  const since = ft !== undefined && t >= ft ? t - ft : -1;
  const shake = since >= 0 && since < 1.4 ? 11 * Math.exp(-4.5 * since) : 0;
  const sx = shake * Math.sin(since * 57), sy = shake * 0.7 * Math.cos(since * 43);
  const glow = since >= 0 ? 0.12 * Math.exp(-since / 1.4) : 0;
  // a shot with a blast is drawn 1.5% oversize from its first frame, so the shake never shows an edge (and the scale
  // never jumps when the shake starts)
  const over = ft !== undefined && ft >= 0 ? 1.015 : 1;
  const tf = [push !== 1 ? `scale(${push}) translateX(${(-pan / push).toFixed(2)}px)` : '', over !== 1 ? `scale(${over})` : '',
    shake ? `translate(${sx.toFixed(1)}px, ${sy.toFixed(1)}px)` : ''].join(' ').trim();
  return (
    <AbsoluteFill>
      <AbsoluteFill style={tf ? {transform: tf} : undefined}>
        <LabelScope.Provider value={shot.id}><ShotBody shot={shot} t={t} /></LabelScope.Provider>
      </AbsoluteFill>
      {glow > 0.004 ? <AbsoluteFill style={{background: '#FF7A1A', opacity: glow, mixBlendMode: 'screen'}} /> : null}
      <Chrome tag={shot.tag} clock={shot.clock} clockLabel={shot.clockLabel} clockRate={shot.clockRate} caption={subtitled ? undefined : shot.caption} source={shot.source} t={t} />
      {dark > 0 ? <AbsoluteFill style={{background: '#000', opacity: dark}} /> : null}
    </AbsoluteFill>
  );
};

// Narration subtitles for Shorts and Reels: one short phrase at a time, sized to sit with the HUD rather than shout.
// They replace the shot captions (which paraphrase the same narration) and sit above YouTube's bottom overlay.
const Subtitles: React.FC<{cues: {start: number; end: number; text: string}[]}> = ({cues}) => {
  const frame = useCurrentFrame();
  const {fps, width: W} = useVideoConfig();
  const t = frame / fps;
  const cue = cues.find((c) => t >= c.start && t < c.end);
  if (!cue) return null;
  const k = clamp01((t - cue.start) / 0.08);
  return (
    <div style={{position: 'absolute', left: 0, right: 0, bottom: 560, display: 'flex', justifyContent: 'center', pointerEvents: 'none'}}>
      <div style={{fontFamily: FONT, fontWeight: 700, fontSize: 50, lineHeight: 1.22, color: '#FFFFFF', textAlign: 'center',
        maxWidth: W * 0.74, padding: '10px 22px 12px', background: 'rgba(8,10,14,0.74)', borderRadius: 4,
        textShadow: '0 2px 6px rgba(0,0,0,0.9)', opacity: k, transform: `translateY(${(1 - k) * 6}px)`}}>{cue.text}</div>
    </div>
  );
};

// Shorts: a fixed two-line title band under YouTube's top bar, so a viewer who lands mid-way knows the subject.
const ShortTitle: React.FC<{lines: [string, string]; bridge?: string}> = ({lines, bridge}) => {
  const {width: W, fps, durationInFrames} = useVideoConfig();
  const frame = useCurrentFrame();
  // the last 3 s point to the full episode (Shorts brought 92% of views and almost no subscribers)
  const left = (durationInFrames - frame) / fps;
  const b = bridge ? clamp01((3 - left) / 0.3) : 0;
  return (
    <>
      <div style={{position: 'absolute', left: 0, right: 0, top: 210, display: 'flex', flexDirection: 'column', alignItems: 'center', pointerEvents: 'none'}}>
        <div style={{background: 'rgba(8,10,14,0.78)', padding: '14px 30px 18px', borderTop: `4px solid ${C.red}`, maxWidth: W * 0.9, textAlign: 'center'}}>
          <div style={{fontFamily: COND, fontWeight: 800, fontSize: 76, lineHeight: 0.98, color: '#FFFFFF', letterSpacing: 1}}>{lines[0]}</div>
          <div style={{fontFamily: COND, fontWeight: 800, fontSize: 70, lineHeight: 0.98, color: '#FFD23F', letterSpacing: 1, marginTop: 4}}>{lines[1]}</div>
        </div>
      </div>
      {b > 0 ? (
        // its own pill under the tag and clock row, so the band never grows over the SIMULATION tag
        <div style={{position: 'absolute', left: 0, right: 0, top: 486, display: 'flex', justifyContent: 'center', pointerEvents: 'none', opacity: b}}>
          <div style={{fontFamily: MONO, fontWeight: 600, fontSize: 30, letterSpacing: 3, color: C.white, background: 'rgba(184,30,30,0.92)', padding: '6px 16px'}}>{bridge}</div>
        </div>
      ) : null}
    </>
  );
};

export const Episode: React.FC<{episode: EpisodeT}> = ({episode}) => {
  const {fps} = useVideoConfig();
  return (
    <AbsoluteFill style={{background: C.bg}}>
      {episode.narration ? <Audio src={staticFile(episode.narration)} /> : null}
      {episode.music ? <Audio src={staticFile(episode.music.src)} volume={episode.music.volume} loop /> : null}
      {(episode.sfx ?? []).map((s, i) => (
        <Sequence key={`sfx${i}`} from={Math.round(s.t * fps)} layout="none"><Audio src={staticFile(s.src)} volume={s.volume ?? 1} /></Sequence>
      ))}
      {episode.shots.map((s, i) => {
        const d = dips(episode.shots, i, !!episode.shortTitle);
        return (
          <Sequence key={s.id} name={s.id} from={Math.round(s.start * fps)} durationInFrames={Math.max(1, Math.round((s.end - s.start) * fps))} layout="none">
            <ShotView shot={s} subtitled={!!episode.subtitles?.length} din={d.din} dout={d.dout} />
          </Sequence>
        );
      })}
      {episode.banner ? (
        <Sequence name="banner" from={Math.round(episode.banner.start * fps)} durationInFrames={Math.max(1, Math.round((episode.banner.end - episode.banner.start) * fps))} layout="none">
          <BannerView banner={episode.banner} />
        </Sequence>
      ) : null}
      {episode.subtitles?.length ? <Subtitles cues={episode.subtitles} /> : null}
      {episode.shortTitle ? <ShortTitle lines={episode.shortTitle} bridge={episode.bridge === undefined ? 'FULL SIMULATION ON THE CHANNEL' : episode.bridge || undefined} /> : null}
    </AbsoluteFill>
  );
};
