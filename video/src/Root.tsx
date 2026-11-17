import React from 'react';
import {Composition, Still} from 'remotion';
import {Avatar, Banner, BannerGuide, Watermark} from './Branding';
import {Thumbnail, type ThumbProps} from './Thumbnail';
import type {Episode as EpisodeT} from './scene';
import {Episode} from './Episode';
import demo from '../public/episodes/demo/episode.json';
import {SurvivalShort, survivalMeta} from './survival/SurvivalShort';
import type {SurvivalSpec} from './survival/spec';
import survivalDemo from '../public/survival/demo.json';

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
    <Composition id="SurvivalShort" component={SurvivalShort} defaultProps={{spec: survivalDemo as unknown as SurvivalSpec}} fps={30} width={1080} height={1920} durationInFrames={300} calculateMetadata={survivalMeta} />
    <Still id="Avatar" component={Avatar} width={800} height={800} />
    <Still id="Banner" component={Banner} width={2560} height={1440} />
    <Still id="BannerGuide" component={BannerGuide} width={2560} height={1440} />
    <Still id="Thumbnail" component={Thumbnail} width={1280} height={720} defaultProps={{variant: 'globe', line1: '27 MINUTES', line2: 'TO OMAHA', tag: 'RUSSIA STRIKES FIRST'} as ThumbProps} />
    <Still id="Watermark" component={Watermark} width={150} height={150} />
  </>
);
