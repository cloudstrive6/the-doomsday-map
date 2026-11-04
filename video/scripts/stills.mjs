// Render sample frames of an episode as PNGs for visual QC.
//   node scripts/stills.mjs <episode.json> <outDir> <frame> [frame...]     (frames as numbers or seconds like 12.5s)
import fs from 'node:fs';
import path from 'node:path';
import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';

const [episodePath, outDir, ...framesArg] = process.argv.slice(2);
const episode = JSON.parse(fs.readFileSync(episodePath, 'utf8'));
const compositionId = episode.height > episode.width ? 'Short' : 'Episode';
const frames = framesArg.map((f) => f.endsWith('s') ? Math.round(parseFloat(f) * episode.fps) : parseInt(f, 10));
fs.mkdirSync(outDir, {recursive: true});
const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts'), publicDir: path.resolve('public'), onProgress: () => {}});
const inputProps = {episode};
const composition = await selectComposition({serveUrl, id: compositionId, inputProps, chromiumOptions: {gl: 'swangle'}});
for (const frame of frames) {
  const t0 = Date.now();
  const out = path.join(outDir, `f${String(frame).padStart(5, '0')}.png`);
  await renderStill({composition, serveUrl, inputProps, frame, output: out, imageFormat: 'png', chromiumOptions: {gl: 'swangle'}, timeoutInMilliseconds: 120000});
  console.log(`${out} ${((Date.now() - t0) / 1000).toFixed(1)}s`);
}
