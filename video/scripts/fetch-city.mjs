// Fetch OpenStreetMap vector tiles from OpenFreeMap for a city and write a compact JSON the CityMap component draws.
// Two levels: a wide pass (zoom 12: motorways to tertiary roads, water, rail, airports, parks, place names)
// over the whole view, and a detail pass (zoom 14: minor roads and buildings) in a small box around ground zero.
//
// usage: node scripts/fetch-city.mjs --slug omaha --lon -95.9345 --lat 41.2565 --width-km 60 --gz-lon -95.9145 --gz-lat 41.1183 --detail-km 12
// Attribution required in the video description: OpenFreeMap, OpenMapTiles, OpenStreetMap contributors (ODbL).
import fs from 'node:fs';
import path from 'node:path';
import {VectorTile} from '@mapbox/vector-tile';
import Pbf from 'pbf';

const args = Object.fromEntries(process.argv.slice(2).map((a, i, arr) => a.startsWith('--') ? [a.slice(2), arr[i + 1]] : null).filter(Boolean));
const slug = args.slug;
const lon = parseFloat(args.lon), lat = parseFloat(args.lat);
const widthKm = parseFloat(args['width-km'] ?? '60');
const gzLon = parseFloat(args['gz-lon'] ?? String(lon)), gzLat = parseFloat(args['gz-lat'] ?? String(lat));
const detailKm = parseFloat(args['detail-km'] ?? '12');
if (!slug || Number.isNaN(lon) || Number.isNaN(lat)) {
  console.error('need --slug --lon --lat');
  process.exit(2);
}

const manifest = await (await fetch('https://tiles.openfreemap.org/planet')).json();
const template = manifest.tiles[0];
console.log('tile template', template);

const cacheDir = path.resolve('public/city/.cache', slug);
fs.mkdirSync(cacheDir, {recursive: true});

const lon2x = (ln, z) => Math.floor(((ln + 180) / 360) * 2 ** z);
const lat2y = (la, z) => Math.floor(((1 - Math.log(Math.tan((la * Math.PI) / 180) + 1 / Math.cos((la * Math.PI) / 180)) / Math.PI) / 2) * 2 ** z);
const tile2lon = (x, z) => (x / 2 ** z) * 360 - 180;
const tile2lat = (y, z) => (Math.atan(Math.sinh(Math.PI * (1 - (2 * y) / 2 ** z))) * 180) / Math.PI;

function bboxAround(cLon, cLat, wKm, hKm) {
  const dLat = hKm / 2 / 111.32, dLon = wKm / 2 / (111.32 * Math.cos((cLat * Math.PI) / 180));
  return {w: cLon - dLon, e: cLon + dLon, s: cLat - dLat, n: cLat + dLat};
}

async function getTile(z, x, y) {
  const f = path.join(cacheDir, `${z}-${x}-${y}.pbf`);
  if (fs.existsSync(f)) return fs.readFileSync(f);
  const url = template.replace('{z}', z).replace('{x}', x).replace('{y}', y);
  for (let attempt = 0; attempt < 4; attempt++) {
    try {
      const r = await fetch(url, {headers: {'User-Agent': 'the-doomsday-map-studio/0.1 (map prep)'}});
      if (r.status === 404 || r.status === 204) { fs.writeFileSync(f, Buffer.alloc(0)); return Buffer.alloc(0); }
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const buf = Buffer.from(await r.arrayBuffer());
      fs.writeFileSync(f, buf);
      return buf;
    } catch (e) {
      if (attempt === 3) throw e;
      await new Promise((res) => setTimeout(res, 800 * (attempt + 1)));
    }
  }
}

const out = {
  slug, center: [lon, lat], gz: [gzLon, gzLat], widthKm, detailKm, fetched: new Date().toISOString(),
  attribution: 'OpenFreeMap, OpenMapTiles, OpenStreetMap contributors',
  roads: {motorway: [], primary: [], secondary: [], minor: [], rail: []},
  water: [], waterway: [], aeroway: [], parks: [], buildings: [], places: [],
};
const R = (v) => Math.round(v * 1e5) / 1e5;

function geomToLonLat(feature, z, x, y) {
  const extent = feature.extent;
  const n = 2 ** z;
  return feature.loadGeometry().map((ring) => ring.map((p) => {
    const gx = (p.x / extent + x) / n, gy = (p.y / extent + y) / n;
    return [R(gx * 360 - 180), R((Math.atan(Math.sinh(Math.PI * (1 - 2 * gy))) * 180) / Math.PI)];
  }));
}

const ROAD = {motorway: 'motorway', trunk: 'motorway', primary: 'primary', secondary: 'secondary', tertiary: 'secondary', minor: 'minor', service: 'minor', rail: 'rail', transit: 'rail'};

async function pass(z, box, {minor, buildings}) {
  const x0 = lon2x(box.w, z), x1 = lon2x(box.e, z), y0 = lat2y(box.n, z), y1 = lat2y(box.s, z);
  const tiles = [];
  for (let x = x0; x <= x1; x++) for (let y = y0; y <= y1; y++) tiles.push([x, y]);
  console.log(`zoom ${z}: ${tiles.length} tiles`);
  let done = 0;
  const queue = [...tiles];
  async function worker() {
    while (queue.length) {
      const [x, y] = queue.shift();
      const buf = await getTile(z, x, y);
      done++;
      if (!buf.length) continue;
      const vt = new VectorTile(new Pbf(buf));
      const L = vt.layers;
      const take = (layerName, fn) => {
        const layer = L[layerName];
        if (!layer) return;
        for (let i = 0; i < layer.length; i++) fn(layer.feature(i));
      };
      take('transportation', (f) => {
        const cls = ROAD[f.properties.class];
        if (!cls || (cls === 'minor' && !minor)) return;
        if (f.properties.brunnel === 'tunnel') return;
        if (f.type !== 2) return;
        for (const line of geomToLonLat(f, z, x, y)) if (line.length > 1) out.roads[cls].push(line);
      });
      if (!minor) {
        take('water', (f) => { if (f.type === 3) for (const ring of geomToLonLat(f, z, x, y)) out.water.push(ring); });
        take('waterway', (f) => { if (f.type === 2) for (const line of geomToLonLat(f, z, x, y)) out.waterway.push(line); });
        take('aeroway', (f) => { if (['runway', 'taxiway', 'aerodrome', 'apron'].includes(f.properties.class)) for (const g of geomToLonLat(f, z, x, y)) out.aeroway.push({type: f.type, pts: g}); });
        take('park', (f) => { if (f.type === 3) for (const ring of geomToLonLat(f, z, x, y)) out.parks.push(ring); });
        take('place', (f) => {
          const cls = f.properties.class;
          if (!['city', 'town', 'village', 'suburb', 'neighbourhood'].includes(cls) || !f.properties.name) return;
          const [[p]] = geomToLonLat(f, z, x, y);
          out.places.push({name: f.properties['name:en'] || f.properties.name, at: p, cls, rank: f.properties.rank ?? 99});
        });
      }
      if (buildings) {
        take('building', (f) => { if (f.type === 3) for (const ring of geomToLonLat(f, z, x, y)) if (ring.length >= 4) out.buildings.push(ring); });
      }
      if (done % 20 === 0) console.log(`  ${done}/${tiles.length}`);
    }
  }
  await Promise.all(Array.from({length: 4}, worker));
}

const wide = bboxAround(lon, lat, widthKm * 1.25, widthKm * 0.5625 * 1.25);
await pass(12, wide, {minor: false, buildings: false});
const detail = bboxAround(gzLon, gzLat, detailKm, detailKm);
await pass(14, detail, {minor: true, buildings: true});

// de-duplicate places by name (tiles overlap)
const seen = new Set();
out.places = out.places.filter((p) => { const k = p.name + p.cls; if (seen.has(k)) return false; seen.add(k); return true; }).sort((a, b) => a.rank - b.rank);
if (out.buildings.length > 80000) out.buildings = out.buildings.filter((_, i) => i % Math.ceil(out.buildings.length / 80000) === 0);

const dest = path.resolve('public/city', `${slug}.json`);
fs.mkdirSync(path.dirname(dest), {recursive: true});
fs.writeFileSync(dest, JSON.stringify(out));
const mb = (fs.statSync(dest).size / 1e6).toFixed(1);
console.log(`wrote ${dest} (${mb} MB): roads`, Object.fromEntries(Object.entries(out.roads).map(([k, v]) => [k, v.length])),
  'water', out.water.length, 'aeroway', out.aeroway.length, 'buildings', out.buildings.length, 'places', out.places.length);
