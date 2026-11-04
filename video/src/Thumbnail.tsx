// Episode thumbnails, 1280x720. Two code-rendered variants for YouTube's Test and compare:
//   "globe": our own night-side globe with the strike arcs and flashes, headline right
//   "card":  typographic big-number card on the HUD ground with a small map inset
// Rules (plan page section 10): number first, consequence second, at most five words over two lines,
// a small red tag naming the actor, orange and white on dark blue, readable at 160 px wide.
import React from 'react';
import {AbsoluteFill} from 'remotion';
import {Globe} from './components/Globe';
import {C, COND} from './theme';
import type {GlobeShot} from './scene';

export type ThumbProps = {
  variant: 'globe' | 'card';
  line1: string;          // white, e.g. "27 MINUTES"
  line2: string;          // yellow, e.g. "TO OMAHA"
  tag?: string;           // red box, e.g. "RUSSIA STRIKES FIRST"
  globe?: Partial<GlobeShot>;
};

const Headline: React.FC<{p: ThumbProps; align: 'left' | 'right'; size: number}> = ({p, align, size}) => (
  <div style={{display: 'flex', flexDirection: 'column', alignItems: align === 'right' ? 'flex-end' : 'flex-start', textAlign: align}}>
    <div style={{fontFamily: COND, fontWeight: 800, fontSize: size, lineHeight: 0.92, color: '#FFFFFF', letterSpacing: 1,
      textShadow: '0 4px 18px rgba(0,0,0,0.9), 0 0 3px rgba(0,0,0,1)'}}>{p.line1}</div>
    <div style={{fontFamily: COND, fontWeight: 800, fontSize: size * 0.92, lineHeight: 0.95, color: '#FFD23F', letterSpacing: 1, marginTop: 4,
      textShadow: '0 4px 18px rgba(0,0,0,0.9), 0 0 3px rgba(0,0,0,1)'}}>{p.line2}</div>
    {p.tag ? (
      <div style={{marginTop: 18, background: '#E01E1E', color: '#fff', fontFamily: COND, fontWeight: 700, fontSize: size * 0.3, letterSpacing: 2,
        padding: '6px 16px', boxShadow: '0 4px 14px rgba(0,0,0,0.6)'}}>{p.tag}</div>
    ) : null}
  </div>
);

export const Thumbnail: React.FC<ThumbProps> = (p) => {
  if (p.variant === 'card') {
    return (
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at 70% 60%, #3A0D0D 0%, #14080A 45%, #07080B 100%)'}}>
        <div style={{position: 'absolute', inset: 0, transform: 'translate(330px, 170px)', mixBlendMode: 'lighten', opacity: 0.9}}>
          <Globe shot={{id: 't', type: 'globe', start: 0, end: 1, camera: [{t: 0, lat: 45, lon: -95, scale: 400}], sun: {lat: 0, lon: 85}, graticule: false,
            ...p.globe} as GlobeShot} t={30} />
        </div>
        <AbsoluteFill style={{background: 'linear-gradient(90deg, rgba(7,8,11,0.95) 0%, rgba(7,8,11,0.6) 50%, rgba(7,8,11,0) 75%)'}} />
        <div style={{position: 'absolute', left: 60, top: 110}}>
          <Headline p={p} align="left" size={168} />
        </div>
      </AbsoluteFill>
    );
  }
  return (
    <AbsoluteFill style={{background: '#05070A'}}>
      <div style={{position: 'absolute', inset: 0, transform: 'translateX(-250px)'}}>
        <Globe shot={{id: 't', type: 'globe', start: 0, end: 1, camera: [{t: 0, lat: 62, lon: -40, scale: 470}], sun: {lat: -16, lon: 160}, graticule: false,
          ...p.globe} as GlobeShot} t={30} />
      </div>
      <AbsoluteFill style={{background: 'linear-gradient(270deg, rgba(5,7,10,0.92) 0%, rgba(5,7,10,0.55) 35%, rgba(5,7,10,0) 55%)'}} />
      <div style={{position: 'absolute', right: 50, top: 70}}>
        <Headline p={p} align="right" size={150} />
      </div>
    </AbsoluteFill>
  );
};
