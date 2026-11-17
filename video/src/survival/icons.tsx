// Flat line icons for Survival Clock Shorts, drawn on a 100x100 grid with round strokes, so they stay crisp at any size.
// `fill` (0..1) floods the icon's body from the bottom in the fill colour (a bathtub filling, a tank emptying).
import React, {useId} from 'react';
import type {IconName} from './spec';

const P: Record<IconName, {d: string[]; body?: string}> = {
  wifi: {d: ['M14 40 Q50 8 86 40', 'M26 52 Q50 30 74 52', 'M38 64 Q50 54 62 64', 'M50 76 L50 77']},
  sos: {d: ['M20 20 L80 80', 'M80 20 L20 80', 'M50 12 Q88 12 88 50 Q88 88 50 88 Q12 88 12 50 Q12 12 50 12']},
  tap: {d: ['M10 30 L52 30 Q64 30 64 42 L64 50', 'M10 44 L44 44', 'M30 30 L30 18', 'M20 16 L40 16', 'M64 58 L64 92'],
    body: 'M58 58 L70 58 L70 94 L58 94 Z'},
  bath: {d: ['M8 50 L92 50', 'M14 50 L18 76 Q20 82 28 82 L72 82 Q80 82 82 76 L86 50', 'M24 50 L24 22 Q24 12 34 12 Q42 12 42 22',
    'M28 82 L24 92', 'M72 82 L76 92'], body: 'M16 54 L84 54 L80 76 Q78 80 72 80 L28 80 Q22 80 20 76 Z'},
  pot: {d: ['M14 36 L86 36', 'M20 36 L22 78 Q22 86 30 86 L70 86 Q78 86 78 78 L80 36', 'M6 44 L20 44', 'M80 44 L94 44', 'M40 24 L60 24'],
    body: 'M23 40 L77 40 L76 78 Q76 83 70 83 L30 83 Q24 83 24 78 Z'},
  bottle: {d: ['M40 8 L60 8', 'M42 8 L42 22 Q30 30 30 42 L30 86 Q30 92 36 92 L64 92 Q70 92 70 86 L70 42 Q70 30 58 22 L58 8'],
    body: 'M33 44 L67 44 L67 86 Q67 89 64 89 L36 89 Q33 89 33 86 Z'},
  radio: {d: ['M10 36 L90 36 L90 84 L10 84 Z', 'M22 36 L70 12', 'M36 60 m-12 0 a12 12 0 1 0 24 0 a12 12 0 1 0 -24 0', 'M60 52 L80 52',
    'M60 66 L80 66']},
  lock: {d: ['M22 46 L78 46 L78 90 L22 90 Z', 'M32 46 L32 32 Q32 12 50 12 Q68 12 68 32 L68 46', 'M50 62 L50 74']},
  cash: {d: ['M8 28 L92 28 L92 72 L8 72 Z', 'M50 50 m-12 0 a12 12 0 1 0 24 0 a12 12 0 1 0 -24 0', 'M18 38 L18 38', 'M82 62 L82 62']},
  fuel: {d: ['M16 90 L16 18 Q16 10 24 10 L56 10 Q64 10 64 18 L64 90', 'M8 90 L72 90', 'M24 22 L56 22 L56 42 L24 42 Z',
    'M64 40 L76 52 L76 78 Q76 84 82 84 Q88 84 88 78 L88 44 L80 34'], body: 'M19 46 L61 46 L61 88 L19 88 Z'},
  fridge: {d: ['M24 8 L76 8 L76 92 L24 92 Z', 'M24 38 L76 38', 'M34 18 L34 30', 'M34 48 L34 64']},
  plug: {d: ['M36 8 L36 28', 'M64 8 L64 28', 'M24 28 L76 28 L76 46 Q76 64 50 64 Q24 64 24 46 Z', 'M50 64 L50 92']},
  tower: {d: ['M50 30 L30 92', 'M50 30 L70 92', 'M36 72 L64 72', 'M41 54 L59 54', 'M50 30 m-6 0 a6 6 0 1 0 12 0 a6 6 0 1 0 -12 0',
    'M28 14 Q20 30 28 46', 'M72 14 Q80 30 72 46', 'M18 6 Q6 30 18 54', 'M82 6 Q94 30 82 54']},
  house: {d: ['M10 46 L50 12 L90 46', 'M20 38 L20 90 L80 90 L80 38', 'M42 90 L42 64 L58 64 L58 90']},
  radiation: {d: ['M50 50 m-7 0 a7 7 0 1 0 14 0 a7 7 0 1 0 -14 0', 'M50 38 L38 16 Q50 10 62 16 Z', 'M60 56 L84 58 Q82 72 72 80 Z',
    'M40 56 L28 80 Q18 72 16 58 Z', 'M50 6 Q94 6 94 50 Q94 94 50 94 Q6 94 6 50 Q6 6 50 6']},
  siren: {d: ['M26 80 L26 50 Q26 26 50 26 Q74 26 74 50 L74 80', 'M16 80 L84 80 L84 92 L16 92 Z', 'M50 10 L50 16', 'M20 20 L25 25',
    'M80 20 L75 25', 'M42 64 L42 50 Q42 42 50 42']},
  car: {d: ['M8 62 L8 50 L22 30 L78 30 L92 50 L92 62 Z', 'M28 70 m-9 0 a9 9 0 1 0 18 0 a9 9 0 1 0 -18 0',
    'M72 70 m-9 0 a9 9 0 1 0 18 0 a9 9 0 1 0 -18 0', 'M26 46 L74 46']},
  pill: {d: ['M30 70 L70 30 Q80 20 90 30 Q100 40 90 50 L50 90 Q40 100 30 90 Q20 80 30 70 Z', 'M50 50 L70 70']},
  shirt: {d: ['M36 10 L20 16 L6 36 L20 46 L26 38 L26 90 L74 90 L74 38 L80 46 L94 36 L80 16 L64 10 Q50 26 36 10 Z']},
  shower: {d: ['M20 92 L20 20 Q20 10 30 10 L52 10 Q62 10 62 20 L62 26', 'M46 34 L78 34 L72 26 L52 26 Z', 'M52 46 L50 54', 'M62 46 L62 56',
    'M72 46 L74 54', 'M56 64 L54 72', 'M68 64 L70 72']},
  door: {d: ['M22 92 L22 8 L78 8 L78 92', 'M10 92 L90 92', 'M64 52 L64 52']},
  window: {d: ['M14 14 L86 14 L86 86 L14 86 Z', 'M50 14 L50 86', 'M14 50 L86 50']},
  battery: {d: ['M10 30 L82 30 L82 74 L10 74 Z', 'M82 42 L92 42 L92 62 L82 62'], body: 'M14 34 L78 34 L78 70 L14 70 Z'},
  phone: {d: ['M28 6 L72 6 Q80 6 80 14 L80 86 Q80 94 72 94 L28 94 Q20 94 20 86 L20 14 Q20 6 28 6 Z', 'M44 84 L56 84']},
  food: {d: ['M14 30 L86 30 L86 86 L14 86 Z', 'M14 30 L22 14 L78 14 L86 30', 'M14 48 L86 48', 'M14 68 L86 68']},
  clock: {d: ['M50 8 Q92 8 92 50 Q92 92 50 92 Q8 92 8 50 Q8 8 50 8', 'M50 24 L50 50 L68 62']},
  bunker: {d: ['M6 86 L94 86', 'M14 86 L14 54 Q50 18 86 54 L86 86', 'M40 86 L40 62 L60 62 L60 86', 'M24 60 L24 60', 'M76 60 L76 60']},
  person: {d: ['M50 24 m-11 0 a11 11 0 1 0 22 0 a11 11 0 1 0 -22 0', 'M30 92 L30 58 Q30 42 50 42 Q70 42 70 58 L70 92']},
  tv: {d: ['M8 22 L92 22 L92 78 L8 78 Z', 'M36 90 L64 90', 'M36 8 L50 22 L64 8']},
  alert: {d: ['M50 8 L94 88 L6 88 Z', 'M50 36 L50 62', 'M50 74 L50 75']},
  check: {d: ['M14 52 L40 78 L88 22']},
  cross: {d: ['M18 18 L82 82', 'M82 18 L18 82']},
};

export const Icon: React.FC<{name: IconName; size: number; color: string; stroke?: number; fill?: number; fillColor?: string;
  glow?: boolean}> = ({name, size, color, stroke = 6, fill = 0, fillColor, glow}) => {
  const id = useId().replace(/:/g, '');
  const p = P[name] ?? P.alert;
  const level = Math.max(0, Math.min(1, fill));
  return (
    <svg width={size} height={size} viewBox="0 0 100 100" style={{overflow: 'visible', filter: glow ? `drop-shadow(0 0 10px ${color})` : undefined}}>
      {p.body && level > 0 ? (
        <>
          <clipPath id={`c${id}`}><rect x={0} y={100 - level * 100} width={100} height={level * 100} /></clipPath>
          <path d={p.body} fill={fillColor ?? color} clipPath={`url(#c${id})`} />
        </>
      ) : null}
      {p.d.map((d, i) => <path key={i} d={d} fill="none" stroke={color} strokeWidth={stroke} strokeLinecap="round" strokeLinejoin="round" />)}
    </svg>
  );
};
