import React from 'react';
import {AbsoluteFill, Audio, Sequence, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import type {Episode as EpisodeT, Shot} from './scene';
import {C, COND, FONT, clamp01} from './theme';
import {Globe} from './components/Globe';
import {RegionMap} from './components/RegionMap';
import {CityMap} from './components/CityMap';
import {Bars, BigNumber, Chapter, Chrome, EndSlate, Isotype, Radar, Split, Stamp, TextCard, Timeline} from './components/Cards';

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

const ShotView: React.FC<{shot: Shot; subtitled?: boolean}> = ({shot: raw, subtitled}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const shot = React.useMemo(() => withDrift(raw), [raw]);
  const dur = shot.end - shot.start;
  // cards push in at about 1% a second (at least 4.5% in total), so long cards keep moving too
  const push = CARD_TYPES.has(shot.type) ? 1 + Math.max(0.045 * Math.min(1, t / Math.max(1, dur)), Math.min(0.14, 0.01 * t)) : 1;
  const fadeIn = clamp01(t / 0.35);
  const fadeOut = clamp01((dur - t) / 0.35);
  const dark = 1 - Math.min(fadeIn, fadeOut);
  return (
    <AbsoluteFill>
      <AbsoluteFill style={push !== 1 ? {transform: `scale(${push})`} : undefined}>
        <ShotBody shot={shot} t={t} />
      </AbsoluteFill>
      <Chrome tag={shot.tag} clock={shot.clock} clockLabel={shot.clockLabel} caption={subtitled ? undefined : shot.caption} source={shot.source} t={t} />
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
        maxWidth: W * 0.82, padding: '10px 22px 12px', background: 'rgba(8,10,14,0.74)', borderRadius: 4,
        textShadow: '0 2px 6px rgba(0,0,0,0.9)', opacity: k, transform: `translateY(${(1 - k) * 6}px)`}}>{cue.text}</div>
    </div>
  );
};

// Shorts: a fixed two-line title band under YouTube's top bar, so a viewer who lands mid-way knows the subject.
const ShortTitle: React.FC<{lines: [string, string]}> = ({lines}) => {
  const {width: W} = useVideoConfig();
  return (
    <div style={{position: 'absolute', left: 0, right: 0, top: 210, display: 'flex', flexDirection: 'column', alignItems: 'center', pointerEvents: 'none'}}>
      <div style={{background: 'rgba(8,10,14,0.78)', padding: '14px 30px 18px', borderTop: `4px solid ${C.red}`, maxWidth: W * 0.9, textAlign: 'center'}}>
        <div style={{fontFamily: COND, fontWeight: 800, fontSize: 76, lineHeight: 0.98, color: '#FFFFFF', letterSpacing: 1}}>{lines[0]}</div>
        <div style={{fontFamily: COND, fontWeight: 800, fontSize: 70, lineHeight: 0.98, color: '#FFD23F', letterSpacing: 1, marginTop: 4}}>{lines[1]}</div>
      </div>
    </div>
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
      {episode.shots.map((s) => (
        <Sequence key={s.id} name={s.id} from={Math.round(s.start * fps)} durationInFrames={Math.max(1, Math.round((s.end - s.start) * fps))} layout="none">
          <ShotView shot={s} subtitled={!!episode.subtitles?.length} />
        </Sequence>
      ))}
      {episode.subtitles?.length ? <Subtitles cues={episode.subtitles} /> : null}
      {episode.shortTitle ? <ShortTitle lines={episode.shortTitle} /> : null}
    </AbsoluteFill>
  );
};
