"""Shorts cut from an episode as native vertical renders.

episodes/<ep>/shorts.json lists windows on the episode timeline (start, end in seconds), a two-line title band
and the YouTube title. For each one this writes a 1080x1920 shot list (video/public/episodes/<ep>-<id>/episode.json)
for the `render` workflow with composition Short, and later muxes the rendered video with the matching slice of
the episode's final mix, re-normalised to -14 LUFS."""
from __future__ import annotations

import copy
import json
import subprocess
from pathlib import Path

from .config import ROOT, load_config

VIDEO = ROOT / "video"
CITY_ZOOM = 0.8   # vertical frames are 1.78x taller: tighten city views so the data tile still fills the frame


def specs(ep: Path) -> list[dict]:
    return json.loads((ep / "shorts.json").read_text(encoding="utf-8"))


def shot_list(ep: Path, spec: dict) -> dict:
    src = json.loads((ep / "episode.json").read_text(encoding="utf-8"))
    cfg = load_config()["shorts"]
    a, b = spec["start"], spec["end"]
    shots = []
    for s in src["shots"]:
        if s["end"] <= a + 0.05 or s["start"] >= b - 0.05 or s["type"] in ("chapter", "endslate"):
            continue
        s = copy.deepcopy(s)
        if s["start"] < a - 0.05:
            raise SystemExit(f"{spec['id']}: window starts inside shot {s['id']}; move the start to a shot boundary")
        s["start"], s["end"] = round(s["start"] - a, 3), round(min(s["end"], b) - a, 3)
        if s["type"] == "city":
            s["view"]["widthKm"] = round(s["view"]["widthKm"] * CITY_ZOOM, 2)
            if s.get("zoomTo"):
                s["zoomTo"]["widthKm"] = round(s["zoomTo"]["widthKm"] * CITY_ZOOM, 2)
        shots.append(s)
    shots[0]["start"] = 0.0          # a dropped chapter card leaves a gap at the top: the first shot covers it
    shots[-1]["end"] = round(b - a, 3)
    subs = [{"start": round(x, 3), "end": round(y, 3), "text": txt}
            for x, y, txt in subtitle_cues(ep, spec)] if cfg.get("subtitles", True) else []
    return {"subtitles": subs, "slug": f"{ep.name}-{spec['id']}", "fps": src["fps"], "width": cfg["width"], "height": cfg["height"],
            "durationSeconds": round(b - a, 3), "shots": shots, "shortTitle": spec["title"],
            "attribution": src.get("attribution")}


def stage(ep: Path) -> list[Path]:
    out = []
    for spec in specs(ep):
        d = shot_list(ep, spec)
        dest = VIDEO / "public" / "episodes" / d["slug"] / "episode.json"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(d, indent=1, ensure_ascii=False), encoding="utf-8")
        out.append(dest)
        print(dest.parent.name, f"{d['durationSeconds']:.1f}s", len(d["shots"]), "shots")
    return out


def mux(ep: Path, spec: dict, silent: Path, out: Path) -> dict:
    """Cut the episode's final mix for this window, fade the edges, normalise, and put it under the Short."""
    from .mix import _normalize_stereo
    cfg = load_config()["video"]
    a, b = spec["start"], spec["end"]
    dur = b - a
    wav = out.with_suffix(".wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{a:.3f}", "-t", f"{dur:.3f}", "-i", str(ep / "build" / "final.mp4"),
                    "-vn", "-af", f"afade=t=in:d=0.12,afade=t=out:st={dur - 0.7:.3f}:d=0.7", "-ar", "48000", "-ac", "2", str(wav)], check=True)
    loud = _normalize_stereo(wav, cfg["loudness_lufs"], cfg["true_peak_db"])
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(silent), "-i", str(wav), "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", str(out)], check=True)
    wav.unlink()
    return loud


def _window_timing(ep: Path, spec: dict) -> dict:
    t = json.loads((ep / "narration" / "timing.json").read_text(encoding="utf-8"))
    a, b = spec["start"], spec["end"]
    return {"units": [dict(u, start=max(0.0, u["start"] - a), end=min(u["end"], b) - a)
                      for u in t["units"] if u["start"] >= a - 0.05 and u["start"] < b]}


def subtitle_cues(ep: Path, spec: dict, max_words: int = 6) -> list[tuple[float, float, str]]:
    """Burned-in subtitle phrases on the Short's timeline, timed from aligned words when narration/words.json exists."""
    from .package import cues, word_cues
    win = _window_timing(ep, spec)
    wpath = ep / "narration" / "words.json"
    if not wpath.exists():
        return cues(win, max_words)
    ids = {u["id"] for u in win["units"]}
    a, b = spec["start"], spec["end"]
    words = [dict(w, start=max(0.0, w["start"] - a), end=min(w["end"], b) - a)
             for w in json.loads(wpath.read_text(encoding="utf-8")) if w["unit"] in ids]
    return [(x, min(y, b - a), t) for x, y, t in word_cues(win, words, max_words)]


def captions_for(ep: Path, spec: dict) -> str:
    from .package import srt
    return srt(subtitle_cues(ep, spec, max_words=11))


def publish(ep: Path, times: list[str]) -> list[dict]:
    """Mux, QC and upload every Short of an episode. times: UTC ISO publishAt per Short, in shorts.json order."""
    from .youtube import upload_short
    out_dir = ep / "build" / "shorts"
    log_path = ep / "shorts_uploaded.json"
    done = json.loads(log_path.read_text(encoding="utf-8")) if log_path.exists() else []
    have = {d["id"] for d in done}
    for spec, when in zip(specs(ep), times):
        if spec["id"] in have:
            continue
        final = out_dir / f"{spec['id']}.mp4"
        loud = mux(ep, spec, out_dir / f"{spec['id']}_silent.mp4", final)
        r = upload_short(ep, spec, final, when, captions_for(ep, spec))
        r["loudness"] = loud
        done.append(r)
        log_path.write_text(json.dumps(done, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps(r))
    try:  # the Shorts files go into the episode's private release for the cross-poster
        from .meta import release_assets
        release_assets(ep)
    except Exception as e:
        print("release assets not stored:", e)
    return done
