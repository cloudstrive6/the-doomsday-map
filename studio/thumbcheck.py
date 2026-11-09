"""Thumbnail brightness gate and review sheet (added 2026-11-09).

Our first three thumbnails were dark maps: mean brightness 48 to 70 (of 255) with 70 to 82% of the frame near-black,
while the competitor thumbnails taking 100k+ views sat at 79 to 130 with a large, bright, saturated subject (fire,
a fireball, a launch) covering 11 to 20% of the frame. This module measures each thumbnail against those numbers and
builds a sheet comparing ours, at desktop and phone size, with the current top competitor thumbnails, so the
thumbnail reviewer (.claude/agents/thumbnail-reviewer.md) judges them side by side.

    python -m studio thumbcheck <episode>      -> build/thumbcheck.json + build/thumb_review.png
"""
from __future__ import annotations

import io
import json
import urllib.request
from pathlib import Path

from .config import ROOT

# Calibrated on 2026-11-09: the niche's 100k+ view thumbnails (dark night scenes lit by a big fire, fireball or launch)
# measure brightness 79 to 130, glow 11 to 20%, dark 24 to 59%; our 001/002 measured 70/48, glow 7%, dark 70/82%.
# Glow (a big bright subject) separates them best; brightness and dark share catch an empty black frame.
MIN_BRIGHTNESS = 75      # mean HSV value, 0 to 255
MIN_GLOW_PCT = 10        # share of pixels that are bright and saturated (the subject: fire, flash, launch)
MAX_DARK_PCT = 62        # share of pixels with luminance under 40


def measure(img) -> dict:
    from PIL import Image
    im = img.convert("RGB").resize((320, 180), Image.BILINEAR)
    hsv = im.convert("HSV").tobytes()
    lum = im.convert("L").tobytes()
    n = len(lum)
    vals = [hsv[i + 2] for i in range(0, len(hsv), 3)]
    sats = [hsv[i + 1] for i in range(0, len(hsv), 3)]
    return {
        "brightness": round(sum(vals) / n),
        "glow_pct": round(100 * sum(1 for s, v in zip(sats, vals) if s > 110 and v > 150) / n, 1),
        "dark_pct": round(100 * sum(1 for x in lum if x < 40) / n, 1),
        "saturation": round(sum(sats) / n),
    }


def verdict(m: dict) -> list[str]:
    issues = []
    if m["brightness"] < MIN_BRIGHTNESS:
        issues.append(f"too dim: brightness {m['brightness']} (need {MIN_BRIGHTNESS}+)")
    if m["glow_pct"] < MIN_GLOW_PCT:
        issues.append(f"subject too small or dull: glow {m['glow_pct']}% (need {MIN_GLOW_PCT}%+)")
    if m["dark_pct"] > MAX_DARK_PCT:
        issues.append(f"mostly black: {m['dark_pct']}% dark (max {MAX_DARK_PCT}%)")
    return issues


NICHE = __import__("re").compile(r"nuke|nuclear|missile|warhead|war|strike|invade|invasion|blockade|what if|simulat", 2)


def _competitor_thumbs(k: int = 6) -> list[tuple[str, int, bytes]]:
    """The k most-viewed long videos in the latest competitor snapshot, with their thumbnails (fetched, not stored)."""
    snaps = sorted((ROOT / "data" / "competitors").glob("*.json"))
    if not snaps:
        return []
    rows = []
    for c in json.loads(snaps[-1].read_text(encoding="utf-8")).get("channels", []):
        for v in c.get("videos", []):
            if not v.get("short") and v.get("age_days", 99) <= 30 and NICHE.search(v.get("title", "")):
                rows.append((v.get("views", 0), v["id"], v.get("title", "")))
    out = []
    for views, vid, title in sorted(rows, reverse=True)[:k]:
        data = None
        for q in ("maxresdefault", "hqdefault"):
            try:
                data = urllib.request.urlopen(f"https://i.ytimg.com/vi/{vid}/{q}.jpg", timeout=20).read()
                break
            except Exception:
                pass
        if data:
            out.append((title, views, _crop_16x9(data)))
    return out


def _crop_16x9(data: bytes) -> bytes:
    """hqdefault is 4:3 with black bars above and below a 16:9 picture: cut them off so they do not count as dark."""
    from PIL import Image
    im = Image.open(io.BytesIO(data)).convert("RGB")
    w, h = im.size
    if h * 16 > w * 9 + 16:
        ch = round(w * 9 / 16)
        im = im.crop((0, (h - ch) // 2, w, (h - ch) // 2 + ch))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=92)
    return buf.getvalue()


def check(ep: Path) -> dict:
    from PIL import Image, ImageDraw
    b = ep / "build"
    thumbs = sorted(b.glob("thumb_[a-z].png"))
    report = {"thumbs": {}, "ok": bool(thumbs)}
    for t in thumbs:
        m = measure(Image.open(t))
        issues = verdict(m)
        report["thumbs"][t.stem] = {**m, "issues": issues}
        report["ok"] = report["ok"] and not issues
    comp = _competitor_thumbs()
    comp_stats = [measure(Image.open(io.BytesIO(d))) for _, _, d in comp]
    report["competitors"] = [{"title": t, "views": v, **s} for (t, v, _), s in zip(comp, comp_stats)]

    # review sheet: row 1 ours at desktop size (480x270), row 2 ours at phone size (246x138, as in the home feed),
    # rows 3 and 4 the top competitors at desktop size
    W, H = 480, 270
    cols = max(3, len(thumbs))
    rows_comp = (len(comp) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (W + 10) + 10, 30 + (H + 40) + (138 + 40) + rows_comp * (H + 40) + 10), (18, 18, 18))
    d = ImageDraw.Draw(sheet)
    y = 10
    d.text((10, y), "OURS (desktop)", fill=(255, 255, 255)); y += 20
    for i, t in enumerate(thumbs):
        x = 10 + i * (W + 10)
        sheet.paste(Image.open(t).convert("RGB").resize((W, H)), (x, y))
        m = report["thumbs"][t.stem]
        d.text((x, y + H + 4), f"{t.stem}: bright {m['brightness']} glow {m['glow_pct']}% dark {m['dark_pct']}%",
               fill=(255, 120, 120) if m["issues"] else (140, 255, 140))
    y += H + 30
    d.text((10, y), "OURS (phone size, how most viewers see it)", fill=(255, 255, 255)); y += 20
    for i, t in enumerate(thumbs):
        sheet.paste(Image.open(t).convert("RGB").resize((246, 138)), (10 + i * (W + 10), y))
    y += 138 + 20
    d.text((10, y), "TOP COMPETITORS THIS MONTH (views)", fill=(255, 255, 255)); y += 20
    for i, ((title, views, data), s) in enumerate(zip(comp, comp_stats)):
        x, yy = 10 + (i % cols) * (W + 10), y + (i // cols) * (H + 40)
        sheet.paste(Image.open(io.BytesIO(data)).convert("RGB").resize((W, H)), (x, yy))
        d.text((x, yy + H + 4), f"{views:,} views: bright {s['brightness']} glow {s['glow_pct']}%", fill=(200, 200, 200))
    sheet.save(b / "thumb_review.png")
    (b / "thumbcheck.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    for k, v in report["thumbs"].items():
        print(k, "OK" if not v["issues"] else "; ".join(v["issues"]))
    print("thumbcheck:", "ok" if report["ok"] else "FAIL", "| sheet:", b / "thumb_review.png")
    return report
