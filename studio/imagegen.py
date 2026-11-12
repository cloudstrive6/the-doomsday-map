"""Photoreal thumbnail backgrounds from Google's Gemini image model (added 2026-11-09).

Env: GEMINI_API_KEY (GitHub secret and studio .env; key "Doomsday Map Gemini thumbnails" in the the-doomsday-map
Google Cloud project, restricted to the Gemini API, bound to service account gemini-thumbnails, no roles).
Cost: about US$0.04 an image. The packager writes `image_prompt` on each thumbs.json variant; `generate(ep)` makes
the missing images into video/public/thumbs/<episode>-<id>.jpg and sets `variant: image` and `image` on that variant.

    python -m studio thumbimages <episode> [--force]
"""
from __future__ import annotations

import base64
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

from .config import ROOT

MODEL = os.environ.get("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image")
URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

# Appended to every prompt. Until 2026-11-12 one style ("orange fire against a deep blue night, the subject large and
# glowing") went on every image, and with fixed a/b/c roles every episode got the same mushroom cloud over a dusk
# skyline. Now each variant names a `palette` (packager.md, concept library) and only the frame rules are shared.
STYLE = ("Photorealistic, cinematic, 16:9 landscape, high contrast, one clear subject large in the frame. "
         "{palette} Leave a clear, simple area in the upper {side} third for a headline. No text, no letters, no "
         "logos, no flags, no watermark, no people's faces.")
PALETTES = {
    "fire-night": "Intense orange and yellow fire light against a deep blue night, high saturation.",
    "daylight": "Bright midday daylight, clear pale-blue sky, crisp white and grey tones, the event white-hot and "
                "blinding against the blue; no night, no orange sunset.",
    "red-alert": "Deep red emergency lighting in near darkness, glowing red and amber screens and lamps, strong rim light.",
    "radar-green": "Dark scene lit by glowing green and cyan screens and instruments, cool tones, sharp highlights.",
    "ash": "Overcast ash-grey sky and muted desaturated tones, with one vivid red or orange accent on the subject.",
    "dawn-gold": "Soft golden sunrise light, pink and teal sky, warm highlights, calm before the event.",
    "map": "A bright stylised 3D relief map seen from high above: vivid blue sea, light beige and green land, sharp "
           "coastlines, glowing red strike arcs and markers; clean, like a high-end infographic.",
}


def image(prompt: str, out: Path, side: str = "left", palette: str = "fire-night") -> Path:
    from .config import load_dotenv
    load_dotenv()
    key = (os.environ.get("GEMINI_API_KEY") or "").replace("﻿", "").strip()
    if not key:
        raise SystemExit("GEMINI_API_KEY is not set")
    body = {"contents": [{"parts": [{"text": f"{prompt.strip()} {STYLE.format(side=side, palette=PALETTES.get(palette, PALETTES['fire-night']))}"}]}],
            "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": "16:9"}}}
    req = urllib.request.Request(URL.format(model=MODEL), data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", "x-goog-api-key": key})
    last = None
    for attempt in range(3):
        try:
            data = json.loads(urllib.request.urlopen(req, timeout=180).read())
            for part in data.get("candidates", [{}])[0].get("content", {}).get("parts", []):
                inline = part.get("inlineData") or part.get("inline_data")
                if inline and inline.get("data"):
                    raw = base64.b64decode(inline["data"])
                    return _to_png(raw, out)
            last = f"no image in response: {json.dumps(data)[:300]}"
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}: {e.read().decode(errors='replace')[:300]}"
        time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"Gemini image failed: {last}")


def _to_png(raw: bytes, out: Path) -> Path:
    """Save as a 1920x1080 JPEG (cover-cropped to 16:9) for the Remotion thumbnail."""
    import io
    from PIL import Image
    im = Image.open(io.BytesIO(raw)).convert("RGB")
    w, h = im.size
    tw, th = (w, round(w * 9 / 16)) if w * 9 / 16 <= h else (round(h * 16 / 9), h)
    im = im.crop(((w - tw) // 2, (h - th) // 2, (w - tw) // 2 + tw, (h - th) // 2 + th)).resize((1920, 1080), Image.LANCZOS)
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out, "JPEG", quality=92)
    return out


def generate(ep: Path, force: bool = False) -> list[str]:
    tj = ep / "thumbs.json"
    thumbs = json.loads(tj.read_text(encoding="utf-8"))
    made = []
    for th in thumbs:
        prompt = th.get("image_prompt")
        if not prompt:
            continue
        # a variant keeps its own image file: the thumbnail-reviewer may swap ids so the best variant is "a"
        rel = th.get("image") if str(th.get("image", "")).startswith("thumbs/") else f"thumbs/{ep.name[:3]}-{th['id']}.jpg"
        out = ROOT / "video" / "public" / rel
        if force or not out.exists():
            image(prompt, out, side="right" if th.get("align") == "right" else "left", palette=th.get("palette", "fire-night"))
            made.append(rel)
            print("generated", out)
        th["variant"], th["image"] = "image", rel
    tj.write_text(json.dumps(thumbs, indent=1, ensure_ascii=False), encoding="utf-8")
    return made
