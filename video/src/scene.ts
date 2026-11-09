// Scene schema: the director agent writes an episode JSON made only of these shot types.
// Times are seconds. `start`/`end` are absolute within the episode; everything else inside a shot is shot-local.

export type LonLat = [number, number]; // [lon, lat]
export type Tag = 'REAL DATA' | 'SIMULATION' | 'REAL HISTORY' | '';

export interface ShotBase {
  id: string;
  start: number;
  end: number;
  tag?: Tag;
  caption?: string;   // lower-third line (short, one sentence)
  clock?: string;     // top-right HUD clock text, e.g. "T+00:06" or "04:12 LOCAL"
  clockLabel?: string;
  source?: string;    // tiny footer credit, e.g. "FAS, Status of World Nuclear Forces 2025"
}

export interface CameraKey { t: number; lat: number; lon: number; scale: number } // scale = globe radius in px
export interface Arc { from: LonLat; to: LonLat; t0: number; t1: number; color?: string; width?: number; loft?: number }
export interface Marker { at: LonLat; label?: string; color?: string; size?: number; t?: number; kind?: 'dot' | 'ring' | 'target' | 'base' | 'sub' }
export interface Flash { at: LonLat; t: number; radius?: number; color?: string; hold?: number }

export interface GlobeShot extends ShotBase {
  type: 'globe';
  camera: CameraKey[];
  sun?: { lat: number; lon: number };
  arcs?: Arc[];
  markers?: Marker[];
  flashes?: Flash[];
  borders?: boolean;
  highlight?: { iso: string; color: string }[]; // ISO numeric id as string from world-atlas, e.g. "643" Russia
  graticule?: boolean;
  dim?: number;       // 0..1 darken the raster (default 0)
}

export interface RegionView { center: LonLat; widthKm: number }
export interface RegionShot extends ShotBase {
  type: 'region';
  view: RegionView;
  zoomTo?: RegionView;        // animate from view to zoomTo over the shot
  highlight?: { iso: string; color: string; fill?: string }[];
  cities?: Marker[];
  rings?: { at: LonLat; km: number; label?: string; color?: string; t?: number; dashed?: boolean }[];
  lines?: { from: LonLat; to: LonLat; label?: string; color?: string; dashed?: boolean; t0?: number; t1?: number }[];
  plume?: { at: LonLat; bearing: number; lengthKm: number; widthKm: number; t0: number; t1: number; color?: string; label?: string };
  labels?: { at: LonLat; text: string; color?: string; t?: number }[];
  scaleBar?: boolean;
  countryLabels?: { iso: string; text: string; color?: string }[];
  zones?: Zone[];            // declared areas (closure zones, exclusion zones), drawn as shaded polygons
  ships?: Ship[];            // vessels moving along a path, drawn as chevrons pointing along their heading
  burst?: { at: LonLat; t: number; km: number; fade?: number };  // fade: seconds the fireball glow takes to die away (default 7)  // nuclear detonation: full-frame white flash, then a glowing fireball of radius km
}

export interface Zone { points: LonLat[]; label?: string; color?: string; t?: number; pulse?: boolean }
export type ShipKind = 'pla' | 'coastguard' | 'us' | 'ally' | 'cargo' | 'tanker';
export interface Ship {
  path: LonLat[];            // positions over [t0, t1] (shot-local seconds); the ship holds at the last point
  t0?: number; t1?: number;
  kind?: ShipKind; color?: string; label?: string; size?: number;
  t?: number;                // appears at t (default 0)
  sunkAt?: number;           // flash and fade out at this time
  wake?: boolean;            // short fading trail behind it (default true)
}

export interface CityShot extends ShotBase {
  type: 'city';
  city: string;               // slug of public/city/<slug>.json (prepared by scripts/fetch-city.mjs)
  view: RegionView;
  zoomTo?: RegionView;
  gz: LonLat;                 // ground zero
  rings: { km: number; label: string; color?: string; t: number }[];
  flashT?: number;
  labels?: { at: LonLat; text: string; color?: string; t?: number }[];
  legend?: { text: string; color?: string }[];
}

export interface StampShot extends ShotBase { type: 'stamp'; text: string; line?: string; color?: string }
export interface NumberShot extends ShotBase {
  type: 'number'; value: string; label?: string; sub?: string; color?: string;
  countTo?: number; decimals?: number; suffix?: string; prefix?: string;  // if countTo is set, animates 0 -> countTo and replaces value
}
export interface ChapterShot extends ShotBase { type: 'chapter'; kicker?: string; title: string }
export interface IsotypeShot extends ShotBase {
  type: 'isotype'; headline: string; label: string; total: number; filled: number; per: string; color?: string; cols?: number; sub?: string;
}
export interface BarsShot extends ShotBase {
  type: 'bars'; title: string; sub?: string; bars: { label: string; value: number; display?: string; color?: string }[];
}
export interface TimelineShot extends ShotBase {
  type: 'timeline'; title: string; sub?: string; total: number; unit?: string;
  segments: { from: number; to: number; label: string; color?: string }[];
  highlight?: { from: number; to: number; label: string };
  cursorTo?: number;          // cursor animates 0 -> cursorTo over the shot
}
export interface RadarShot extends ShotBase {
  type: 'radar'; title: string; lines: { k: string; v: string }[]; tracks?: number; big?: string; bigColor?: string; footer?: string;
}
export interface TextShot extends ShotBase { type: 'text'; lines: string[]; size?: number; color?: string; align?: 'left' | 'center' }
export interface SplitShot extends ShotBase {
  type: 'split'; left: { title: string; sub: string; color?: string; kind: 'airburst' | 'groundburst' }; right: { title: string; sub: string; color?: string; kind: 'airburst' | 'groundburst' };
}
export interface EndSlateShot extends ShotBase { type: 'endslate'; title: string; line?: string }

export type Shot =
  | GlobeShot | RegionShot | CityShot | StampShot | NumberShot | ChapterShot | IsotypeShot
  | BarsShot | TimelineShot | RadarShot | TextShot | SplitShot | EndSlateShot;

// Moving disclaimer (from episode 004, 2026-11-09): replaces the old static "this is a simulation" text card.
// Episode-level and in absolute seconds, so it rides across a cut. Draw it over a globe, region or city shot only.
export interface Banner {
  start: number;
  end: number;               // 2.5 to 3.5 s after start
  text?: string;             // default "SIMULATION · NOT REAL EVENTS"
  line?: string;             // optional small second line, e.g. "BUILT FROM PUBLISHED MODELS"
}

export interface Episode {
  slug: string;
  fps: number;
  width: number;
  height: number;
  durationSeconds: number;
  narration?: string;        // path under public/, e.g. "episodes/001-slug/narration.wav"
  music?: { src: string; volume: number };
  sfx?: { src: string; t: number; volume?: number }[];
  shots: Shot[];
  banner?: Banner;           // the moving disclaimer: a 2.5 to 3 s HUD band over moving footage early in the cold open
  attribution?: string;
  shortTitle?: [string, string];
  subtitles?: { start: number; end: number; text: string }[];  // burned-in narration subtitles (Shorts and Reels)  // Shorts only: two-line title band at the top (white, then yellow)
}
