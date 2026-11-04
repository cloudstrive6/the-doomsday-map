// The Doomsday Map HUD kit: one type family, three accents, near-black ground.
import {loadFont as loadBarlow} from '@remotion/google-fonts/Barlow';
import {loadFont as loadBarlowCondensed} from '@remotion/google-fonts/BarlowCondensed';
import {loadFont as loadMono} from '@remotion/google-fonts/IBMPlexMono';

const barlow = loadBarlow('normal', {weights: ['400', '500', '600', '700'], subsets: ['latin']});
const cond = loadBarlowCondensed('normal', {weights: ['500', '600', '700', '800'], subsets: ['latin']});
const mono = loadMono('normal', {weights: ['400', '500', '600'], subsets: ['latin']});

export const FONT = barlow.fontFamily;
export const COND = cond.fontFamily;
export const MONO = mono.fontFamily;

export const C = {
  bg: '#0B0E12',
  bg2: '#11161C',
  panel: 'rgba(16, 21, 27, 0.78)',
  grid: 'rgba(120, 150, 170, 0.07)',
  land: '#1A2128',
  landHi: '#222B34',
  border: 'rgba(120, 190, 200, 0.55)',
  text: '#ECEFF2',
  dim: 'rgba(236, 239, 242, 0.62)',
  faint: 'rgba(236, 239, 242, 0.30)',
  teal: '#3ED6C8',
  red: '#FF3B3B',
  redDeep: '#B81E1E',
  amber: '#F2B01E',
  orange: '#FF7A1A',
  blue: '#5B8DEF',
  white: '#FFFFFF',
};

export const TAG_COLOR: Record<string, string> = {
  'REAL DATA': C.teal,
  'SIMULATION': C.red,
  'REAL HISTORY': C.amber,
};

export const W = 1920;
export const H = 1080;

export const ease = (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
export const easeOut = (t: number) => 1 - Math.pow(1 - t, 3);
export const clamp01 = (t: number) => Math.max(0, Math.min(1, t));
export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
