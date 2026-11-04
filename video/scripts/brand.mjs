// Render channel branding stills into ../channel/
import path from 'node:path';
import fs from 'node:fs';
import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';

const outDir = path.resolve('..', 'channel');
fs.mkdirSync(outDir, {recursive: true});
const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts'), publicDir: path.resolve('public'), onProgress: () => {}});
for (const [id, file] of [['Avatar', 'avatar.png'], ['Banner', 'banner.png'], ['Watermark', 'watermark.png']]) {
  const composition = await selectComposition({serveUrl, id, chromiumOptions: {gl: 'swangle'}});
  await renderStill({composition, serveUrl, frame: 0, output: path.join(outDir, file), imageFormat: 'png', chromiumOptions: {gl: 'swangle'}, timeoutInMilliseconds: 120000});
  console.log('wrote', path.join(outDir, file));
}
