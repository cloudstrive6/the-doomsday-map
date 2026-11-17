"""Survival Clock Shorts (2026-11-17): native vertical protective-advice Shorts built from a scene spec.

Folder per Short: shorts/survival/<NNN-slug>/ with
  facts.md      sourced facts (researcher), checked by the fact screener
  script.md     narration (`## Section` headers, paragraphs; numbers written as digits so captions show digits)
  scenes.json   the director's scene list (video/src/survival/spec.ts), times in seconds or word cues ("@pumps")
Produced here:
  narration/    narration.wav, timing.json, words.json (Chirp 3 HD voice, Whisper word timings)
  build/spec.json, build/silent.mp4, build/final.mp4, build/sheet.png

    python -m studio survival narrate <slug>     voice + word timings
    python -m studio survival build <slug>       merge words into the spec, check every cue resolves
    python -m studio survival render <slug>      silent render + mix (narration at -14 LUFS, a quiet music bed)
    python -m studio survival sheet <slug>       contact sheet of one frame every 3 s for review
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

from .config import ROOT

BASE = ROOT / "shorts" / "survival"
VIDEO = ROOT / "video"
CUE = re.compile(r"^@([^#+]+?)(?:#(\d+))?([+-][\d.]+)?$")


def short_dir(slug: str) -> Path:
    d = BASE / slug
    if not d.exists():
        hits = [p for p in BASE.iterdir() if p.is_dir() and p.name.startswith(slug)] if BASE.exists() else []
        if len(hits) == 1:
            return hits[0]
        raise SystemExit(f"no Short folder {d}")
    return d


def _norm(w: str) -> str:
    return re.sub(r"[^a-z0-9½]", "", w.lower())


def resolve(at, words: list[dict], start: float) -> float | None:
    if isinstance(at, (int, float)):
        return float(at)
    m = CUE.match(str(at).strip())
    if not m:
        return None
    target, n, off = _norm(m.group(1)), int(m.group(2) or 1), float(m.group(3) or 0)
    for w in words:
        if w["start"] >= start - 0.05 and _norm(w["word"]) == target:
            n -= 1
            if n == 0:
                return w["start"] + off
    return None


def _cues(obj, path=""):
    """Every word cue in a scene, with where it sits (for error messages)."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("at", "offAt", "spikeAt", "stopwatchAt", "dimAt", "countAt") and isinstance(v, str):
                yield f"{path}.{k}", v
            else:
                yield from _cues(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _cues(v, f"{path}[{i}]")


def narrate(slug: str) -> None:
    from .align import align
    from .narrate import narrate as _narrate
    d = short_dir(slug)
    # Shorts run faster than the documentary voice (0.93 measured 127 wpm on the pilot; the reference reel is ~165)
    _narrate(d, gap=0.12, section_gap=0.25, voice_override={"speaking_rate": 1.18})
    align(d)


def build(slug: str) -> Path:
    d = short_dir(slug)
    scenes = json.loads((d / "scenes.json").read_text(encoding="utf-8"))
    words = json.loads((d / "narration" / "words.json").read_text(encoding="utf-8"))
    timing = json.loads((d / "narration" / "timing.json").read_text(encoding="utf-8"))
    words = [{"word": w["word"], "start": w["start"], "end": w["end"]} for w in words]
    # end loopSeconds after the last word, so the crossfade into the cover starts on the closing line, not dead air
    total = round(min(timing["total_seconds"] + float(scenes.get("tail", 0.6)),
                      words[-1]["end"] + float(scenes.get("loopSeconds", 0)) + 0.2), 2)
    errs = []
    sc = scenes["scenes"]
    # scene starts may be cues too; an end defaults to the next scene's start
    for i, s in enumerate(sc):
        st = resolve(s["start"], words, 0.0)
        if st is None:
            errs.append(f"scene {i} start {s['start']!r} not found in the narration")
            st = 0.0
        s["start"] = round(st, 3)
    for i, s in enumerate(sc):
        s["end"] = sc[i + 1]["start"] if i + 1 < len(sc) else total
        for where, cue in _cues({k: v for k, v in s.items() if k not in ("start", "end")}, f"scene {i} ({s['kind']})"):
            if resolve(cue, words, s["start"]) is None:
                errs.append(f"{where}: cue {cue!r} not found after {s['start']:.2f}s")
    for i in range(1, len(sc)):
        if sc[i]["start"] <= sc[i - 1]["start"]:
            errs.append(f"scene {i} starts at {sc[i]['start']}s, not after scene {i - 1}")
    longest = max((s["end"] - s["start"], i) for i, s in enumerate(sc))
    if longest[0] > 10:
        errs.append(f"scene {longest[1]} runs {longest[0]:.1f}s; keep scenes at 10 s or less (something new every 1 to 2 s inside)")
    if errs:
        raise SystemExit("scenes.json has problems:\n  " + "\n  ".join(errs))
    spec = {k: v for k, v in scenes.items() if k not in ("scenes", "tail")}
    spec.update({"slug": d.name, "fps": scenes.get("fps", 30), "width": 1080, "height": 1920, "durationSeconds": total,
                 "words": words, "scenes": sc})
    out = d / "build"
    out.mkdir(exist_ok=True)
    (out / "spec.json").write_text(json.dumps(spec, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"{d.name}: {len(sc)} scenes, {len(words)} words, {total:.1f}s -> build/spec.json")
    return out / "spec.json"


def render(slug: str, concurrency: int | None = None) -> Path:
    d = short_dir(slug)
    spec = build(slug)
    silent = d / "build" / "silent.mp4"
    cmd = ["node", "scripts/survival.mjs", str(spec), str(silent)]
    if concurrency:
        cmd += ["--concurrency", str(concurrency)]
    subprocess.run(cmd, check=True, cwd=VIDEO)
    return mix(slug)


def mix(slug: str) -> Path:
    """Narration (padded to the picture so the loop crossfade is not cut) over a quiet music bed, -14 LUFS."""
    d = short_dir(slug)
    silent = d / "build" / "silent.mp4"
    final = d / "build" / "final.mp4"
    music = VIDEO / "public" / "music" / "bed_tense.mp3"
    nar = d / "narration" / "narration.wav"
    if music.exists():
        fc = ("[1:a]apad[n];[2:a]volume=0.10,afade=t=in:d=1[m];[n][m]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,"
              "loudnorm=I=-14:TP=-1.5:LRA=11[a]")
        args = ["-i", str(silent), "-i", str(nar), "-stream_loop", "-1", "-i", str(music), "-filter_complex", fc, "-map", "0:v", "-map", "[a]"]
    else:
        args = ["-i", str(silent), "-i", str(nar), "-filter_complex", "[1:a]apad[a]", "-map", "0:v", "-map", "[a]"]
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(final)], check=True)
    print("wrote", final)
    return final


def sheet(slug: str, every: float = 3.0) -> Path:
    from PIL import Image
    d = short_dir(slug)
    spec = json.loads((d / "build" / "spec.json").read_text(encoding="utf-8"))
    times = [round(x * every + 0.5, 2) for x in range(int(spec["durationSeconds"] // every) + 1)]
    frames = d / "build" / "frames"
    if frames.exists():
        shutil.rmtree(frames)
    subprocess.run(["node", "scripts/survival.mjs", str(d / "build" / "spec.json"), "--stills", str(frames), *map(str, times)], check=True, cwd=VIDEO)
    fs = sorted(frames.glob("f_*.png"), key=lambda p: float(p.stem[2:].replace("_", ".")))
    w, h, cols = 270, 480, 8
    rows = (len(fs) + cols - 1) // cols
    im = Image.new("RGB", (cols * (w + 6) + 6, rows * (h + 6) + 6), (30, 30, 30))
    for i, f in enumerate(fs):
        im.paste(Image.open(f).convert("RGB").resize((w, h)), (6 + (i % cols) * (w + 6), 6 + (i // cols) * (h + 6)))
    out = d / "build" / "sheet.png"
    im.save(out)
    print("wrote", out)
    return out
