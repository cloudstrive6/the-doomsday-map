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
  const start = Math.floor((i * composition.durationInFrames) / n);
  const end = Math.floor(((i + 1) * composition.durationInFrames) / n) - 1;
  frameRange = [start, end];
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
