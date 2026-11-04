import React from 'react';
import {AbsoluteFill, Audio, Sequence, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import type {Episode as EpisodeT, Shot} from './scene';
import {C, clamp01} from './theme';
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
function withDrift(shot: Shot): Shot {
  if ((shot.type === 'region' || shot.type === 'city') && !shot.zoomTo) {
    return {...shot, zoomTo: {center: shot.view.center, widthKm: shot.view.widthKm * 0.92}};
  }
  if (shot.type === 'globe' && shot.camera.length === 1) {
    const c = shot.camera[0];
    return {...shot, camera: [c, {...c, t: c.t + (shot.end - shot.start), lon: c.lon - 4, scale: c.scale * 1.05}]};
  }
  return shot;
}
const CARD_TYPES = new Set(['stamp', 'number', 'chapter', 'isotype', 'bars', 'timeline', 'radar', 'text', 'split', 'endslate']);

const ShotView: React.FC<{shot: Shot}> = ({shot: raw}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const shot = React.useMemo(() => withDrift(raw), [raw]);
  const dur = shot.end - shot.start;
  const push = CARD_TYPES.has(shot.type) ? 1 + 0.045 * Math.min(1, t / Math.max(1, dur)) : 1;
  const fadeIn = clamp01(t / 0.35);
  const fadeOut = clamp01((dur - t) / 0.35);
  const dark = 1 - Math.min(fadeIn, fadeOut);
  return (
    <AbsoluteFill>
      <AbsoluteFill style={push !== 1 ? {transform: `scale(${push})`} : undefined}>
        <ShotBody shot={shot} t={t} />
      </AbsoluteFill>
      <Chrome tag={shot.tag} clock={shot.clock} clockLabel={shot.clockLabel} caption={shot.caption} source={shot.source} t={t} />
      {dark > 0 ? <AbsoluteFill style={{background: '#000', opacity: dark}} /> : null}
    </AbsoluteFill>
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
          <ShotView shot={s} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
