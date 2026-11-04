"""Assemble an episode: stage the shot list and narration for Remotion, render (locally or via the GitHub
workflow), mix narration with music, run QC and write build/final.mp4.

Files per episode:
  episode.json            shot list written by the director (video/src/scene.ts schema), times in seconds
  narration/narration.wav normalised narration from `studio narrate`
  build/final.mp4         delivered video
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from .config import ROOT, load_config

VIDEO = ROOT / "video"


def stage(ep: Path) -> Path:
    """Copy episode.json and narration into video/public/episodes/<slug>/ so Remotion can serve them."""
    slug = ep.name
    dest = VIDEO / "public" / "episodes" / slug
    dest.mkdir(parents=True, exist_ok=True)
    shot = json.loads((ep / "episode.json").read_text(encoding="utf-8"))
    cfg = load_config()["video"]
    nar = ep / "narration" / "narration.wav"
    if nar.exists():
        shutil.copy2(nar, dest / "narration.wav")
        shot["narration"] = f"episodes/{slug}/narration.wav"
    music_dir = VIDEO / "public" / "music"
    music_dir.mkdir(parents=True, exist_ok=True)
    for m in (ROOT / "assets" / "music").glob("*.mp3"):
        shutil.copy2(m, music_dir / m.name)
    if shot.get("music") and not (VIDEO / "public" / shot["music"]["src"]).exists():
        print("no music file at", shot["music"]["src"], "(rendering without music)")
        shot.pop("music")
    shot.setdefault("fps", cfg["fps"]); shot.setdefault("width", cfg["width"]); shot.setdefault("height", cfg["height"])
    shot["slug"] = slug
    (dest / "episode.json").write_text(json.dumps(shot, indent=1, ensure_ascii=False), encoding="utf-8")
    return dest / "episode.json"


def validate(ep: Path) -> list[str]:
    """Static checks on the shot list against the narration timing."""
    issues = []
    shot = json.loads((ep / "episode.json").read_text(encoding="utf-8"))
    timing_p = ep / "narration" / "timing.json"
    total = shot.get("durationSeconds", 0)
    shots = sorted(shot["shots"], key=lambda s: s["start"])
    prev_end = 0.0
    for s in shots:
        if s["end"] <= s["start"]:
            issues.append(f"{s['id']}: end <= start")
        if s["start"] < prev_end - 1e-6:
            issues.append(f"{s['id']}: overlaps previous shot (starts {s['start']}, previous ended {prev_end})")
        if s["start"] > prev_end + 0.05:
            issues.append(f"{s['id']}: gap of {s['start'] - prev_end:.2f}s before it")
        if s["end"] - s["start"] > 25 and s["type"] not in ("globe", "region", "city"):
            issues.append(f"{s['id']}: static card held {s['end'] - s['start']:.1f}s (max 25)")
        prev_end = s["end"]
    if timing_p.exists():
        t = json.loads(timing_p.read_text(encoding="utf-8"))
        if abs(total - t["total_seconds"]) > 16:
            issues.append(f"durationSeconds {total} vs narration {t['total_seconds']} (end slate may add up to 15 s)")
        if prev_end < t["total_seconds"] - 0.5:
            issues.append(f"shots end at {prev_end} but narration runs to {t['total_seconds']}")
    return issues


def mix_audio(ep: Path, video_in: Path, out: Path):
    """Mux narration (already -14 LUFS) with an optional music bed ducked under the voice."""
    cfg = load_config()["video"]
    shot = json.loads((ep / "episode.json").read_text(encoding="utf-8"))
    nar = ep / "narration" / "narration.wav"
    music = shot.get("music", {}).get("src")
    music_path = (VIDEO / "public" / music) if music else None
    if music_path and music_path.exists():
        vol = shot.get("music", {}).get("volume", cfg.get("music_volume", 0.1))
        fc = (f"[1:a]volume={vol},aloop=loop=-1:size=2e9[m];[2:a][m]sidechaincompress=threshold=0.05:ratio=6:attack=40:release=600[mduck];"
              f"[2:a][mduck]amix=inputs=2:duration=first:dropout_transition=2,alimiter=limit=0.89[a]")
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(video_in), "-i", str(music_path), "-i", str(nar),
               "-filter_complex", fc, "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(out)]
    else:
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(video_in), "-i", str(nar), "-map", "0:v", "-map", "1:a",
               "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(out)]
    subprocess.run(cmd, check=True)


def qc(final: Path) -> list[str]:
    cfg = load_config()["video"]
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate,nb_frames,duration",
                        "-of", "json", str(final)], capture_output=True, text=True)
    st = json.loads(r.stdout)["streams"][0]
    issues = []
    if int(st["width"]) != cfg["width"] or int(st["height"]) != cfg["height"]:
        issues.append(f"size {st['width']}x{st['height']}")
    num, den = st["r_frame_rate"].split("/")
    if abs(int(num) / int(den) - cfg["fps"]) > 0.01:
        issues.append(f"fps {st['r_frame_rate']}")
    a = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=codec_name,sample_rate", "-of", "json", str(final)], capture_output=True, text=True)
    if not json.loads(a.stdout).get("streams"):
        issues.append("no audio stream")
    return issues


def render_local(episode_json: Path, out: Path, concurrency: int | None = None):
    cmd = ["node", "scripts/render.mjs", str(episode_json), str(out)]
    if concurrency:
        cmd += ["--concurrency", str(concurrency)]
    subprocess.run(cmd, cwd=VIDEO, check=True, shell=True)


def build(ep: Path, chunks: int = 8, local: bool = False):
    staged = stage(ep)
    issues = validate(ep)
    for i in issues:
        print("validate:", i)
    if any("overlap" in i or "end <= start" in i for i in issues):
        raise SystemExit("fix the shot list first")
    build_dir = ep / "build"
    build_dir.mkdir(exist_ok=True)
    silent = build_dir / "video_silent.mp4"
    if local:
        render_local(staged, silent)
    else:
        print("Cloud render: run the `render` workflow with episode =", ep.name, "and chunks =", chunks,
              "then download the artifact to", silent)
        if not silent.exists():
            return
    final = build_dir / "final.mp4"
    mix_audio(ep, silent, final)
    problems = qc(final)
    print("QC:", "ok" if not problems else problems)
    return final
