// One shared cache for the painted base maps of region and city shots.
// Chrome caps total canvas memory per page and silently returns blank canvases past it, so the cache holds at most
// MAX canvases and releases evicted ones (width = 0 frees the backing store immediately).
const MAX = 3;
const cache = new Map<string, HTMLCanvasElement>();

export function getBase(key: string, paint: () => HTMLCanvasElement): HTMLCanvasElement {
  const hit = cache.get(key);
  if (hit) {
    cache.delete(key);
    cache.set(key, hit); // most recently used last
    return hit;
  }
  const cv = paint();
  cache.set(key, cv);
  while (cache.size > MAX) {
    const oldest = cache.keys().next().value as string;
    const old = cache.get(oldest);
    cache.delete(oldest);
    if (old) { old.width = 0; old.height = 0; }
  }
  return cv;
}
