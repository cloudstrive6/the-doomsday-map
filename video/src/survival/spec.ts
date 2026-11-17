// Survival Clock Shorts (2026-11-17): a native vertical format modelled on a 95 s blackout-survival reel that drew
// 38K shares (study: Bryce-Brain wiki/answers/survival-clock-reel-breakdown.md). One JSON spec per Short; no code per
// topic. Times are seconds from the start, or a word cue: "@word" (first match at or after the scene start),
// "@word#2" (second match), "@word+0.3" (offset). Cues are resolved against the narration's word timings.

export type Cue = number | string;
export type Tone = 'ok' | 'warn' | 'red' | 'info' | 'dim';
export type IconName =
  | 'wifi' | 'sos' | 'tap' | 'bath' | 'pot' | 'bottle' | 'radio' | 'lock' | 'cash' | 'fuel' | 'fridge' | 'plug'
  | 'tower' | 'house' | 'radiation' | 'siren' | 'car' | 'pill' | 'shirt' | 'shower' | 'door' | 'window' | 'battery'
  | 'phone' | 'food' | 'clock' | 'bunker' | 'person' | 'tv' | 'alert' | 'check' | 'cross';

export interface Word { word: string; start: number; end: number }

export interface ClockSpec {
  label?: string;          // "NUCLEAR WARNING // SURVIVAL CLOCK"
  from: number;            // clock value at t = 0, in seconds (900 = 00:15:00)
  rate?: number;           // clock seconds per video second (1 = real time; negative counts up)
  bigUntil?: number;       // video time when the big clock shrinks into the top pill (default 6)
  pillLabel?: string;      // "SURVIVAL CLOCK"
}

export interface StateStep { at: Cue; text: string; tone?: Tone }

export type Widget =
  | {type: 'state'; label: string; states: StateStep[]; at?: Cue}
  | {type: 'gauge'; labels?: [string, string, string]; from: number; to: number; at?: Cue; dur?: number;
      caption?: StateStep[]; steps?: {at: Cue; value: number}[]}   // steps: the needle moves to each value on its word
  | {type: 'counter'; label?: string; from: number; to: number; at?: Cue; dur?: number; decimals?: number;
      unit?: string; tone?: Tone; size?: number; sub?: string}
  | {type: 'bar'; label?: string; from: number; to: number; at?: Cue; dur?: number; tone?: Tone; hazard?: boolean;
      right?: string; ticks?: string[]}
  | {type: 'tiles'; items: {icon: IconName; label: string; at?: Cue}[]; tone?: Tone; at?: Cue}
  | {type: 'row'; icon: IconName; count: number; fill: number; at?: Cue; dur?: number; tone?: Tone; label?: string}
  | {type: 'pill'; text: string; tone?: Tone; at?: Cue}
  | {type: 'text'; text: string; size?: number; tone?: Tone; at?: Cue; mono?: boolean}
  | {type: 'compare'; at?: Cue; left: CompareSide; right: CompareSide}
  | {type: 'wave'; spikeAt?: Cue; label?: string; spikeLabel?: string; at?: Cue}
  | {type: 'photo'; src: string; credit: string; at?: Cue; height?: number}
  | {type: 'icon'; icon: IconName; tone?: Tone; at?: Cue; size?: number; label?: string};

export interface CompareSide { title: string; value: string; unit?: string; label: string; tone: Tone; icon?: IconName }

export interface StampSpec { at: Cue; text: string; kicker?: string; tone?: Tone; rotate?: number; y?: number }

export interface LineSpec { text: string; tone?: Tone | 'white' | 'yellow'; at?: Cue }

export interface MapSpec {
  center: [number, number];   // lon, lat
  widthKm: number;
  lights?: boolean;           // city lights (from public/data/cities.json)
  links?: boolean;            // schematic links between nearby lights
  offAt?: Cue;                // lights die and links turn red
  status?: {on: string; off: string};   // "GRID: ONLINE" / "GRID: OFFLINE"
  arcs?: {from: [number, number]; to: [number, number]; at: Cue; dur?: number}[];
  flashes?: {at: Cue; lonlat: [number, number]; km?: number}[];
  note?: string;              // honesty label, e.g. "SCHEMATIC // NOT A REAL NETWORK MAP"
  dim?: number;               // 0..1 opacity when used as a background
}

interface SceneBase { start: number; end: number; clock?: 'big' | 'pill' | 'hide'; bgMap?: MapSpec; stamp?: StampSpec;
  tag?: string }   // tag: a corner label such as SIMULATION or ILLUSTRATIVE

export type Scene = SceneBase & (
  | {kind: 'cover'; lines: LineSpec[]; checklist?: {title: string; items: {text: string; checked?: boolean}[]}}
  | {kind: 'map'; map: MapSpec; lines?: LineSpec[]}
  | {kind: 'stat'; value: string; countFrom?: number; countAt?: Cue; unit: string; tone?: Tone; aside?: {title: string; sub?: string};
      bar?: {ticks: string[]; from: number; to: number; at?: Cue; dur?: number; tone?: Tone; hazard?: boolean; label?: string}}
  | {kind: 'phone'; time?: string; states: {at: Cue; icon: IconName; title: string; sub?: string; tone?: Tone}[]}
  | {kind: 'document'; header: string; kicker?: string; title: string; lines: {text: string; mark?: (string | {text: string; at: Cue})[]; at?: Cue; bold?: boolean}[];
      footer?: string; stopwatchAt?: Cue; dimAt?: Cue; credit?: string}
  | {kind: 'rule'; num: string; icon?: IconName; kicker: string; lines: LineSpec[]}
  | {kind: 'board'; num?: string; title: string; sub?: string; widgets: Widget[]}
  | {kind: 'grid'; title: string; items: {num: string; label: string}[]; badge?: {text: string; sub?: string}}
  | {kind: 'checklist'; kicker: string; title: string; sub?: string; items: {text: string; sub?: string; at?: Cue}[]}
  | {kind: 'slam'; kicker?: string; lines: LineSpec[]; sub?: string}
);

export interface SurvivalSpec {
  slug: string;
  fps: number;
  width: number;
  height: number;
  durationSeconds: number;
  narration?: string;          // staticFile path; renders are silent by default and audio is mixed after
  words: Word[];
  redWords?: string[];         // caption words that get the red pill instead of yellow
  plainWords?: string[];       // short words never highlighted ("the", "a")
  clock: ClockSpec;
  scenes: Scene[];
  loopSeconds?: number;        // the last N seconds crossfade into the cover (frame 0) so the replay is seamless
  source?: string;             // tiny source line at the bottom of every frame
}
