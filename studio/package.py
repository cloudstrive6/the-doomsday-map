"""Upload package for an episode: build/chapters.txt, build/captions.srt and build/thumbnail.png from the
narration timing. metadata.json (title, description, tags) is written by hand or by the packaging agent."""
from __future__ import annotations

import json
import math
import re
import shutil
from pathlib import Path


def _ts(s: float) -> str:
    s = int(s)
    return f"{s // 60}:{s % 60:02d}" if s < 3600 else f"{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}"


def _srt_ts(s: float) -> str:
    ms = int(round(s * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def chapters(timing: dict) -> str:
    out, seen = [], set()
    for u in timing["units"]:
        sec = u["section"]
        if sec in seen or sec.lower().startswith("end slate"):
            continue
        seen.add(sec)
        title = re.sub(r"^Chapter \d+:\s*", "", sec)
        title = title[:1].upper() + title[1:]
        out.append(f"{_ts(0 if not out else u['start'])} {title}")
    return "\n".join(out)


def _phrases(text: str, max_words: int) -> list[str]:
    """Clauses first (split after . , ; : ? !), then each clause cut into near-equal pieces of at most max_words."""
    clauses, cur = [], []
    for w in text.split():
        cur.append(w)
        if w[-1] in ".?!,;:":
            clauses.append(cur)
            cur = []
    if cur:
        clauses.append(cur)
    merged = []                       # glue tiny clauses ("Then another.") onto their neighbour when it fits
    for c in clauses:
        if merged and (len(c) <= 2 or len(merged[-1]) <= 2) and len(merged[-1]) + len(c) <= max_words:
            merged[-1] = merged[-1] + c
        else:
            merged.append(c)
    out = []
    for c in merged:
        n = math.ceil(len(c) / max_words)
        size = math.ceil(len(c) / n)
        out += [" ".join(c[i:i + size]) for i in range(0, len(c), size)]
    return out


def cues(timing: dict, max_words: int = 11) -> list[tuple[float, float, str]]:
    """Narration units cut into phrases, timed in proportion to their character length."""
    out = []
    for u in timing["units"]:
        chunks = _phrases(u["text"], max_words)
        total = sum(len(c) for c in chunks) or 1
        t = u["start"]
        for c in chunks:
            d = (u["end"] - u["start"]) * len(c) / total
            out.append((t, t + d, c))
            t += d
    return out


def captions(timing: dict, max_words: int = 11) -> str:
    return "\n".join(f"{i}\n{_srt_ts(a)} --> {_srt_ts(b)}\n{txt}\n" for i, (a, b, txt) in enumerate(cues(timing, max_words), 1))


def package(ep: Path, thumb: str = "a") -> None:
    timing = json.loads((ep / "narration" / "timing.json").read_text(encoding="utf-8"))
    build = ep / "build"
    (build / "chapters.txt").write_text(chapters(timing) + "\n", encoding="utf-8")
    (build / "captions.srt").write_text(captions(timing), encoding="utf-8")
    shutil.copyfile(build / f"thumb_{thumb}.png", build / "thumbnail.png")
    print((build / "chapters.txt").read_text(encoding="utf-8"))
