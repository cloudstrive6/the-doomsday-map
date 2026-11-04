// Render an episode's thumbnails from episodes/<slug>/thumbs.json into episodes/<slug>/build/thumb_<id>.png
//   node scripts/thumbs.mjs ../episodes/001-russia-first-strike-america
// thumbs.json: [{"id": "a", "variant": "globe", "line1": "...", "line2": "...", "tag": "...", "camera": {...}?}]
// Strike arcs and flashes come from scenario.computed.json so the image matches the episode.
import fs from 'node:fs';
import path from 'node:path';
import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';

const epDir = path.resolve(process.argv[2]);
const thumbs = JSON.parse(fs.readFileSync(path.join(epDir, 'thumbs.json'), 'utf8'));
const sc = JSON.parse(fs.readFileSync(path.join(epDir, 'scenario.computed.json'), 'utf8'));
const arcs = sc.strikes.map((s) => ({from: [s.launch_lon, s.launch_lat], to: [s.target_lon, s.target_lat], t0: 0, t1: 25,
  color: s.weapon_class === 'slbm' ? '#FF7A1A' : '#FF3B3B', loft: s.weapon_class === 'icbm' ? 0.16 : 0.1, width: 2.4}));
const flashes = sc.strikes.map((s) => ({at: [s.target_lon, s.target_lat], t: 29.2, hold: 2.5, radius: s.yield_kt >= 300 ? 26 : 18}));
const outDir = path.join(epDir, 'build');
fs.mkdirSync(outDir, {recursive: true});
const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts'), publicDir: path.resolve('public'), onProgress: () => {}});
for (const th of thumbs) {
  const inputProps = {variant: th.variant, line1: th.line1, line2: th.line2, tag: th.tag,
    globe: {arcs, flashes, ...(th.camera ? {camera: [th.camera]} : {})}};
  const composition = await selectComposition({serveUrl, id: 'Thumbnail', inputProps, chromiumOptions: {gl: 'swangle'}});
  const out = path.join(outDir, `thumb_${th.id}.png`);
  await renderStill({composition, serveUrl, inputProps, frame: 0, output: out, imageFormat: 'png', chromiumOptions: {gl: 'swangle'}, timeoutInMilliseconds: 120000});
  console.log('wrote', out);
}
