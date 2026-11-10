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
        words_p = ep / "narration" / "words.json"
        last_word = t["total_seconds"]
        if words_p.exists():
            ws = json.loads(words_p.read_text(encoding="utf-8"))
            if ws:
                last_word = ws[-1]["end"]
        tail = total - last_word
        if not (SLATE_TAIL - 0.5 <= tail <= SLATE_TAIL + 0.5):
            issues.append(f"durationSeconds {total} vs last word {last_word}: the end slate must run "
                          f"{SLATE_TAIL:.0f} s after the last word (YouTube end screens need at least 5 s), not {tail:.1f} s")
        if prev_end < t["total_seconds"] - 0.5:
            issues.append(f"shots end at {prev_end} but narration runs to {t['total_seconds']}")
    plan = shot.get("musicPlan") or []
    if plan and max(seg["to"] for seg in plan) < total - 0.5:
        issues.append(f"music ends at {max(seg['to'] for seg in plan):.1f} s but the video runs to {total:.1f} s: "
                      "the last musicPlan segment must run to durationSeconds so the end slate is not quiet")
    issues += retention_issues(shot)
    issues += pace_issues(shot)
    return issues


SLATE_TAIL = 10.0                 # end slate after the last spoken word, seconds (was 15 s up to episode 003)
EARLY_WINDOW = 60.0               # the opening minute, where 001 and 002 lost half their viewers on static cards
EARLY_CARD_MAX = 4.0              # longest text, stamp, number or chapter card allowed in the opening minute
EARLY_CARDS = ("text", "stamp", "number", "chapter")
MOVING = ("globe", "region", "city")


def retention_issues(shot: dict) -> list[str]:
    """Retention rules from the 2026-11-09 analysis (T1): no static disclaimer card, no card over 4 s in the first
    minute, and a short moving SIMULATION banner over moving footage. Lines start with "retention:" so the screeners
    can find them."""
    issues = []
    shots = sorted(shot.get("shots", []), key=lambda s: s["start"])
    for s in shots:
        dur = s["end"] - s["start"]
        if s["start"] < EARLY_WINDOW and s["type"] in EARLY_CARDS and dur > EARLY_CARD_MAX + 1e-6:
            issues.append(f"retention: {s['id']} is a {s['type']} card held {dur:.1f} s at {s['start']:.1f} s; "
                          f"in the first {EARLY_WINDOW:.0f} s no card may run over {EARLY_CARD_MAX:.0f} s (cut to moving footage)")
    b = shot.get("banner")
    if not b:
        issues.append("retention: no banner. Add the episode-level `banner` (SIMULATION, NOT REAL EVENTS, 2.5 to 3.5 s "
                      "over a moving globe, region or city shot in the cold open); it replaces the static disclaimer card")
        return issues
    dur = b["end"] - b["start"]
    if not 2.5 - 1e-6 <= dur <= 3.5 + 1e-6:
        issues.append(f"retention: banner runs {dur:.1f} s; keep it 2.5 to 3.5 s")
    if b["start"] >= EARLY_WINDOW:
        issues.append(f"retention: banner starts at {b['start']:.1f} s; it belongs in the cold open (first {EARLY_WINDOW:.0f} s)")
    under = [s for s in shots if s["start"] < b["end"] and s["end"] > b["start"]]
    for s in under:
        if s["type"] not in MOVING:
            issues.append(f"retention: banner sits over {s['id']} ({s['type']}); put it over a moving globe, region or city shot")
    return issues


PACE_EARLY_END = 90.0             # pacing rule from the 2026-11-10 orchestrated pass: something new arrives on screen
PACE_EARLY_GAP = 4.0              # at least every 4 s up to 90 s (the opening hold is measured at about 75 to 80 s)
PACE_GAP = 6.0                    # and at least every 6 s after that
_ITEM_TIMES = ("t", "t0")


def arrivals(shot: dict) -> list[float]:
    """Every moment something new appears: shot starts, and each timed item inside a shot (labels, cities, rings,
    arcs, lines, ships, zones, markers, flashes, plumes, camera keys). Item times are relative to the shot start."""
    out = []
    for s in shot.get("shots", []):
        st = s["start"]
        out.append(st)
        for k, v in s.items():
            if isinstance(v, list):
                for it in v:
                    if isinstance(it, dict):
                        for tk in _ITEM_TIMES:
                            if isinstance(it.get(tk), (int, float)):
                                out.append(st + it[tk]); break
            elif isinstance(v, dict):
                if isinstance(v.get("t0"), (int, float)):
                    out.append(st + v["t0"])
        if isinstance(s.get("flashT"), (int, float)):
            out.append(st + s["flashT"])
    return sorted(t for t in out if t >= 0)


def pace_issues(shot: dict) -> list[str]:
    """Gaps with nothing new on screen. Lines start with "pace:"; the end slate is exempt. Findings for the director
    and the screeners (not a blocking QC fail)."""
    shots = sorted(shot.get("shots", []), key=lambda s: s["start"])
    slate = min((s["start"] for s in shots if s.get("type") == "endslate"), default=shot.get("durationSeconds", 0))
    times = [t for t in arrivals(shot) if t < slate] + [slate]
    issues = []
    for a, b in zip(times, times[1:]):
        limit = PACE_EARLY_GAP if a < PACE_EARLY_END else PACE_GAP
        if b - a > limit + 0.3:   # small tolerance so a 4.1 s gap is not noise
            sid = next((s["id"] for s in shots if s["start"] <= a + 1e-6 < s["end"]), "?")
            issues.append(f"pace: nothing new on screen for {b - a:.1f} s from {a:.1f} s ({sid}); add an arrival "
                          f"(label, ring, marker, camera key or cut) at least every {limit:.0f} s")
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
    from .mix import mix
    mix(ep, silent, final)
    problems = qc(final)
    print("QC:", "ok" if not problems else problems)
    return final
