// Render an episode JSON with Remotion, whole or as one chunk of N (for the GitHub Actions matrix).
//   node scripts/render.mjs <episode.json> <out.mp4> [--chunk i/N] [--composition Episode|Short] [--concurrency n] [--audio]
//   node scripts/render.mjs <episode.json> --frames-only
import fs from 'node:fs';
import path from 'node:path';
import {bundle} from '@remotion/bundler';
import {renderMedia, selectComposition} from '@remotion/renderer';

const argv = process.argv.slice(2);
const positional = argv.filter((a) => !a.startsWith('--'));
const flag = (name, def) => { const i = argv.indexOf(`--${name}`); return i >= 0 ? argv[i + 1] : def; };
const has = (name) => argv.includes(`--${name}`);

const episodePath = positional[0];
if (!episodePath) { console.error('usage: render.mjs <episode.json> <out.mp4> [--chunk i/N]'); process.exit(2); }
const episode = JSON.parse(fs.readFileSync(episodePath, 'utf8'));
// audio is mixed in Python (studio/mix.py); renders are always silent, so drop audio refs (narration is not in git)
if (!argv.includes('--audio')) { delete episode.narration; delete episode.music; delete episode.sfx; }
const compositionId = flag('composition', episode.height > episode.width ? 'Short' : 'Episode');
const totalFrames = Math.ceil(episode.durationSeconds * episode.fps);

// Cost-weighted chunks: a zoomed globe frame costs several times a card frame, so equal frame counts leave one
// runner far behind. Weights per frame by shot type (measured 2026-11-05 on 2-core runners).
function frameWeights(ep, total) {
  const w = new Float64Array(total).fill(0.35);
  for (const s of ep.shots ?? []) {
    let k = 0.35;
    if (s.type === 'globe') {
      // raster cost follows the globe's on-screen area, which stops growing once it fills the frame
      const sc = Math.max(...(s.camera ?? [{scale: 450}]).map((c) => c.scale));
      const area = Math.min(Math.PI * sc * sc, ep.width * ep.height) / (ep.width * ep.height);
      k = 0.35 + 3 * area + 0.01 * (s.arcs?.length ?? 0);
    } else if (s.type === 'city' || s.type === 'region') k = 0.6;
    const a = Math.max(0, Math.floor(s.start * ep.fps)), b = Math.min(total, Math.ceil(s.end * ep.fps));
    for (let f = a; f < b; f++) w[f] = k;
  }
  return w;
}
function chunkBounds(ep, total, n) {
  const w = frameWeights(ep, total);
  const sum = w.reduce((x, y) => x + y, 0);
  const bounds = [0];
  let acc = 0, next = sum / n;
  for (let f = 0; f < total && bounds.length < n; f++) { acc += w[f]; if (acc >= next) { bounds.push(f + 1); next += sum / n; } }
  while (bounds.length < n) bounds.push(total);
  bounds.push(total);
  return bounds;
}
if (flag('plan-chunks')) {
  const n = Number(flag('plan-chunks'));
  const b = chunkBounds(episode, totalFrames, n);
  for (let i = 0; i < n; i++) console.log(`chunk ${i}: frames ${b[i]}-${b[i + 1] - 1} (${b[i + 1] - b[i]})`);
  process.exit(0);
}
if (has('frames-only')) { console.log(totalFrames); process.exit(0); }

const out = positional[1];
if (!out) { console.error('missing output path'); process.exit(2); }
const t0 = Date.now();
const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts'), publicDir: path.resolve('public'), onProgress: () => {}});
console.log(`bundled in ${((Date.now() - t0) / 1000).toFixed(1)}s`);
const inputProps = {episode};
const composition = await selectComposition({serveUrl, id: compositionId, inputProps, chromiumOptions: {gl: 'swangle'}});

let frameRange = null;
const chunk = flag('chunk');
if (chunk) {
  const [i, n] = chunk.split('/').map(Number);
  const bounds = chunkBounds(episode, composition.durationInFrames, n);
  frameRange = [bounds[i], Math.max(bounds[i], bounds[i + 1] - 1)];
  console.log(`chunk ${i}/${n}: frames ${frameRange[0]} to ${frameRange[1]} (${frameRange[1] - frameRange[0] + 1} frames, weighted)`);
}
const concurrency = flag('concurrency') ? Number(flag('concurrency')) : null;
fs.mkdirSync(path.dirname(path.resolve(out)), {recursive: true});
let lastPct = -1;
const t1 = Date.now();
await renderMedia({
  composition, serveUrl, inputProps, codec: 'h264', outputLocation: out, frameRange,
  muted: !has('audio'), crf: 18, x264Preset: 'medium', pixelFormat: 'yuv420p', imageFormat: 'jpeg', jpegQuality: 92,
  chromiumOptions: {gl: 'swangle'}, concurrency, timeoutInMilliseconds: 120000,
  onProgress: ({progress, renderedFrames}) => {
    const pct = Math.floor(progress * 20) * 5;
    if (pct !== lastPct) { lastPct = pct; console.log(`${pct}% (${renderedFrames} frames, ${((Date.now() - t1) / 1000).toFixed(0)}s)`); }
  },
});
const frames = frameRange ? frameRange[1] - frameRange[0] + 1 : composition.durationInFrames;
const secs = (Date.now() - t1) / 1000;
console.log(`rendered ${frames} frames to ${out} in ${secs.toFixed(0)}s (${(frames / secs).toFixed(2)} fps)`);
