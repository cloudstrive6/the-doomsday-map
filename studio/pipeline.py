"""Mechanical pipeline steps for unattended production (the agents do the creative work; this does the rest).

Used by `python -m studio <command>` and by .github/workflows/produce.yml.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from .config import ROOT, episode_dir, load_config

VIDEO = ROOT / "video"
STAGES = ["idea", "researched", "scripted", "script_approved", "narrated", "shotlisted", "visual_approved",
          "packaged", "rendered", "qc_passed", "uploaded"]
NY = "America/New_York"


# ------------------------------------------------------------------ stages


def get_stage(ep: Path) -> str:
    p = ep / "status.json"
    if not p.exists():
        return "uploaded" if (ep / "metadata.json").exists() and json.loads(
            (ep / "metadata.json").read_text(encoding="utf-8")).get("youtube_id") else "idea"
    return json.loads(p.read_text(encoding="utf-8")).get("stage", "idea")


def set_stage(ep: Path, stage: str, note: str = "") -> None:
    if stage not in STAGES:
        raise SystemExit(f"unknown stage {stage}; one of {', '.join(STAGES)}")
    p = ep / "status.json"
    d = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"history": []}
    d["stage"] = stage
    d["history"].append({"stage": stage, "note": note, "at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")})
    p.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"{ep.name}: {stage}" + (f" ({note})" if note else ""))


def in_progress() -> list[Path]:
    return [d for d in sorted((ROOT / "episodes").iterdir())
            if d.is_dir() and (d / "status.json").exists() and get_stage(d) != "uploaded"]


# ------------------------------------------------------------------ schedule


def queue() -> dict:
    from .youtube import _parse_utc, taken_slots
    cfg = load_config()["schedule"]
    now = dt.datetime.now(dt.timezone.utc)
    queued = sum(1 for t in taken_slots() if _parse_utc(t) > now)
    wip = [d.name for d in in_progress()]
    target = int(cfg.get("episodes_ahead", 2))
    return {"queued": queued, "target": target, "in_progress": wip, "need": bool(wip) or queued < target}


def slot() -> dt.datetime:
    from .youtube import next_publish_slot, taken_slots
    return next_publish_slot(taken_slots())


def shorts_times(long_slot: dt.datetime) -> list[str]:
    """The day after the long video (New York), at shorts.publish_times."""
    from zoneinfo import ZoneInfo
    tz = ZoneInfo(NY)
    d = long_slot.astimezone(tz).date() + dt.timedelta(days=1)
    out = []
    for hhmm in load_config()["shorts"]["publish_times"]:
        h, m = map(int, hhmm.split(":"))
        t = dt.datetime(d.year, d.month, d.day, h, m, tzinfo=tz).astimezone(dt.timezone.utc)
        out.append(t.replace(microsecond=0).isoformat().replace("+00:00", "Z"))
    return out


def iso(t: dt.datetime) -> str:
    return t.astimezone(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


# ------------------------------------------------------------------ build steps


def shotlist(ep: Path) -> list[str]:
    """Run the episode's shotlist.py, stage episode.json (+ narration) for Remotion and stage the Shorts."""
    from .build import stage as stage_episode, validate
    subprocess.run([sys.executable, str(ep / "shotlist.py")], check=True, cwd=ROOT)
    stage_episode(ep)
    if (ep / "shorts.json").exists():
        from .shorts import stage as stage_shorts
        stage_shorts(ep)
    issues = validate(ep)
    for i in issues:
        print("validate:", i)
    # the visual screener reads this file: "retention:" lines are regressions of the 2026-11-09 retention rules
    (ep / "build").mkdir(exist_ok=True)
    (ep / "build" / "validate.txt").write_text("".join(f"{i}
" for i in issues) or "ok
", encoding="utf-8")
    return issues


def stills(ep: Path, times: list[str]) -> Path:
    out = ep / "build" / "stills"
    if out.exists():
        for f in out.glob("*.png"):
            f.unlink()
    out.mkdir(parents=True, exist_ok=True)
    ej = VIDEO / "public" / "episodes" / ep.name / "episode.json"
    subprocess.run(["node", "scripts/stills.mjs", str(ej), str(out), *times], check=True, cwd=VIDEO)
    frames = sorted(out.glob("f*.png"))
    if frames:
        cols = 4
        rows = (len(frames) + cols - 1) // cols
        ins = sum((["-i", str(f)] for f in frames), [])
        sc = "".join(f"[{i}:v]scale=480:270[v{i}];" for i in range(len(frames)))
        lay = "|".join(f"{(i % cols) * 480}_{(i // cols) * 270}" for i in range(len(frames)))
        stack = "".join(f"[v{i}]" for i in range(len(frames))) + f"xstack=inputs={len(frames)}:layout={lay}:fill=black[o]"
        if len(frames) == 1:
            stack = "[v0]null[o]"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *ins, "-filter_complex", sc + stack, "-map", "[o]",
                        str(out / "contact.png")], check=True)
        print(out / "contact.png", f"({rows} rows)")
    return out


def package(ep: Path) -> None:
    from .package import package as pkg
    if (ep / "thumbs.json").exists():
        subprocess.run(["node", "scripts/thumbs.mjs", str(ep)], check=True, cwd=VIDEO)
    pkg(ep, thumb="a")


# ------------------------------------------------------------------ finish (after the cloud render)


def _detect(video: Path) -> dict:
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(video), "-vf",
                        "freezedetect=n=0.001:d=4,blackdetect=d=1.0:pix_th=0.05", "-an", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    freezes = [(float(a), float(b)) for a, b in zip(re.findall(r"freeze_start: ([0-9.]+)", r),
                                                     re.findall(r"freeze_duration: ([0-9.]+)", r))]
    blacks = [(float(a), float(b)) for a, b in re.findall(r"black_start:([0-9.]+) black_end:([0-9.]+)", r)]
    return {"freezes": freezes, "blacks": blacks}


def finish(ep: Path) -> dict:
    """build/video_silent.mp4 (from the render job) -> build/final.mp4, then QC -> build/qc.json."""
    from .build import qc as basic_qc
    from .mix import mix
    from .tts import measure
    b = ep / "build"
    mix(ep, b / "video_silent.mp4", b / "final.mp4")
    issues = list(basic_qc(b / "final.mp4"))
    cfg = load_config()["video"]
    loud = measure(b / "final.mp4")
    if abs(loud["I"] - cfg["loudness_lufs"]) > 1.0:
        issues.append(f"loudness {loud['I']} LUFS")
    if loud["TP"] > cfg["true_peak_db"]:
        issues.append(f"true peak {loud['TP']} dBTP")
    det = _detect(b / "final.mp4")
    # the end slate is meant to hold still: YouTube's end-screen elements sit on fixed spots of it
    # (its empty "NEXT SCENARIO" box is the target for the end-screen video), so freezes there are not issues
    slate_start = None
    ej = ep / "episode.json"
    if ej.exists():
        slate = [s for s in json.loads(ej.read_text(encoding="utf-8")).get("shots", []) if s.get("type") == "endslate"]
        slate_start = min(s["start"] for s in slate) if slate else None
    for s, d in det["freezes"]:
        if slate_start is not None and s >= slate_start - 0.5:
            print(f"QC: freeze {d:.1f}s at {s:.1f}s is on the end slate (from {slate_start:.1f}s): allowed")
            continue
        issues.append(f"frozen {d:.1f}s at {s:.1f}s")
    for s, e in det["blacks"]:
        issues.append(f"black {e - s:.1f}s at {s:.1f}s")
    for sh in sorted((b / "shorts").glob("s[0-9]_silent.mp4")):
        for s, d in _detect(sh)["freezes"]:
            issues.append(f"{sh.stem}: frozen {d:.1f}s at {s:.1f}s")
    # shot-list checks (end slate length, music to the end, retention rules): findings for the final screener, not blocking
    from .build import validate
    checks = validate(ep) if ej.exists() else []
    report = {"ok": not issues, "issues": issues, "shotlist_checks": checks, "loudness": loud, "at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
    (b / "qc.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (ep / "qc.json").write_text(json.dumps(report, indent=2), encoding="utf-8")  # tracked copy for the record
    print("QC:", "ok" if report["ok"] else issues)
    return report


def frames_for_review(ep: Path, n: int = 16) -> Path:
    """Evenly spaced frames from the finished video (and each Short) for the final screener."""
    b = ep / "build"
    out = b / "review"
    out.mkdir(parents=True, exist_ok=True)
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                str(b / "final.mp4")], capture_output=True, text=True).stdout.strip() or 0)
    for i in range(n):
        t = dur * (i + 0.5) / n
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", str(b / "final.mp4"), "-frames:v", "1",
                        "-vf", "scale=960:540", str(out / f"long_{i:02d}_{int(t)}s.png")], check=True)
    for sh in sorted((b / "shorts").glob("s[0-9]_silent.mp4")):
        for k, frac in enumerate((0.1, 0.5, 0.9)):
            sd = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                       str(sh)], capture_output=True, text=True).stdout.strip() or 0)
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{sd * frac:.2f}", "-i", str(sh), "-frames:v", "1",
                            "-vf", "scale=360:640", str(out / f"{sh.stem}_{k}.png")], check=True)
    print(out)
    return out


def gate(ep: Path) -> bool:
    qc = json.loads((ep / "build" / "qc.json").read_text(encoding="utf-8")) if (ep / "build" / "qc.json").exists() else {"ok": False}
    rv = ep / "review_final.md"
    verdict = rv.read_text(encoding="utf-8").strip().splitlines()[0].upper() if rv.exists() else ""
    ok = bool(qc.get("ok")) and verdict.startswith("PASS")
    print("gate:", "OPEN" if ok else "CLOSED", "| qc", qc.get("ok"), "| screener", verdict or "missing")
    return ok


def upload_all(ep: Path) -> dict:
    from .shorts import publish
    from .youtube import upload_episode
    when = slot()
    meta = upload_episode(ep, publish_at_override=iso(when))
    out = {"long": {k: meta.get(k) for k in ("youtube_id", "publish_at", "url", "upload_warnings")}}
    if (ep / "shorts.json").exists():
        out["shorts"] = publish(ep, shorts_times(when))
    set_stage(ep, "uploaded", f"{meta.get('url')} at {meta.get('publish_at')}")
    return out
