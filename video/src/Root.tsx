import React from 'react';
import {Composition, Still} from 'remotion';
import {Avatar, Banner, Watermark} from './Branding';
import type {Episode as EpisodeT} from './scene';
import {Episode} from './Episode';
import demo from '../public/episodes/demo/episode.json';

const meta = ({props}: {props: {episode: EpisodeT}}) => ({
  durationInFrames: Math.max(1, Math.ceil(props.episode.durationSeconds * props.episode.fps)),
  fps: props.episode.fps,
  width: props.episode.width,
  height: props.episode.height,
});

export const Root: React.FC = () => (
  <>
    <Composition id="Episode" component={Episode} defaultProps={{episode: demo as unknown as EpisodeT}} fps={60} width={1920} height={1080} durationInFrames={600} calculateMetadata={meta} />
    <Composition id="Short" component={Episode} defaultProps={{episode: {...(demo as unknown as EpisodeT), width: 1080, height: 1920}}} fps={60} width={1080} height={1920} durationInFrames={600} calculateMetadata={meta} />
    <Still id="Avatar" component={Avatar} width={800} height={800} />
    <Still id="Banner" component={Banner} width={2560} height={1440} />
    <Still id="Watermark" component={Watermark} width={150} height={150} />
  </>
);
