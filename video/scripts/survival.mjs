// Render a Survival Clock Short (silent; audio is mixed afterwards) or stills from it.
//   node scripts/survival.mjs <spec.json> <out.mp4> [--concurrency n]
//   node scripts/survival.mjs <spec.json> --stills <outdir> <t1> <t2> ...   (seconds)
import fs from 'node:fs';
import path from 'node:path';
import {bundle} from '@remotion/bundler';
import {renderMedia, renderStill, selectComposition} from '@remotion/renderer';

const argv = process.argv.slice(2);
const specPath = argv[0];
if (!specPath) { console.error('usage: survival.mjs <spec.json> <out.mp4> | --stills <dir> <t...>'); process.exit(2); }
const spec = JSON.parse(fs.readFileSync(specPath, 'utf8'));
delete spec.narration;
const inputProps = {spec};
const chromiumOptions = {gl: 'swangle'};
const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts'), publicDir: path.resolve('public'), onProgress: () => {}});
const composition = await selectComposition({serveUrl, id: 'SurvivalShort', inputProps, chromiumOptions});

if (argv[1] === '--stills') {
  const dir = argv[2];
  fs.mkdirSync(dir, {recursive: true});
  for (const ts of argv.slice(3)) {
    const frame = Math.min(composition.durationInFrames - 1, Math.round(Number(ts) * spec.fps));
    const output = path.join(dir, `f_${String(ts).replace('.', '_')}.png`);
    await renderStill({composition, serveUrl, inputProps, frame, output, imageFormat: 'png', chromiumOptions, timeoutInMilliseconds: 120000});
    console.log('wrote', output);
  }
} else {
  const ci = argv.indexOf('--concurrency');
  await renderMedia({composition, serveUrl, inputProps, codec: 'h264', outputLocation: argv[1], chromiumOptions, muted: true,
    concurrency: ci >= 0 ? Number(argv[ci + 1]) : null, crf: 18, timeoutInMilliseconds: 120000,
    onProgress: ({progress}) => { if (Math.round(progress * 100) % 10 === 0) process.stdout.write(`\r${Math.round(progress * 100)}%`); }});
  console.log('\nwrote', argv[1]);
}
