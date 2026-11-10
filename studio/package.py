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
    from .numbers import number_spans
    out = []
    for c in merged:
        n = math.ceil(len(c) / max_words)
        size = math.ceil(len(c) / n)
        # cut only between atoms: a spoken number with its unit ("one point nine one kilometres") is one atom, so a
        # subtitle never shows half a number (2026-11-10: "point nine kilometres," appeared on its own)
        spans = {a: b for a, b in number_spans(c)}
        atoms, i = [], 0
        while i < len(c):
            j = spans.get(i, i + 1)
            atoms.append(c[i:j])
            i = j
        pieces: list[list[str]] = []
        piece: list[str] = []
        for at in atoms:
            if piece and len(piece) + len(at) > size:
                pieces.append(piece)
                piece = []
            piece += at
        if piece:
            pieces.append(piece)
        # a one-word cue flashes by: fold it into its neighbour in the same clause (a little over max_words is fine)
        k = 0
        while len(pieces) > 1 and k < len(pieces):
            if len(pieces[k]) == 1:
                if k > 0:
                    pieces[k - 1] += pieces.pop(k)
                    continue
                first = pieces.pop(0)
                pieces[0] = first + pieces[0]
                continue
            k += 1
        out += [" ".join(p) for p in pieces]
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
    from .numbers import display
    return [(a, b, display(c)) for a, b, c in out]


def captions(timing: dict, max_words: int = 11, words: list[dict] | None = None) -> str:
    cs = word_cues(timing, words, max_words) if words else cues(timing, max_words)
    return srt(cs)


def srt(cs: list[tuple[float, float, str]]) -> str:
    return "\n".join(f"{i}\n{_srt_ts(a)} --> {_srt_ts(b)}\n{txt}\n" for i, (a, b, txt) in enumerate(cs, 1))


def package(ep: Path, thumb: str = "a") -> None:
    timing = json.loads((ep / "narration" / "timing.json").read_text(encoding="utf-8"))
    build = ep / "build"
    (build / "chapters.txt").write_text(chapters(timing) + "\n", encoding="utf-8")
    wpath = ep / "narration" / "words.json"
    words = json.loads(wpath.read_text(encoding="utf-8")) if wpath.exists() else None
    (build / "captions.srt").write_text(captions(timing, words=words), encoding="utf-8")
    shutil.copyfile(build / f"thumb_{thumb}.png", build / "thumbnail.png")
    print((build / "chapters.txt").read_text(encoding="utf-8"))


def word_cues(timing: dict, words: list[dict], max_words: int = 11, hold: float = 0.35, bridge: float = 0.5) -> list[tuple[float, float, str]]:
    """Phrases timed from the aligned words (narration/words.json): a phrase appears when its first word is spoken
    and stays until the next phrase starts, or `hold` seconds after its last word when a pause follows."""
    by_unit: dict[str, list[dict]] = {}
    for w in words:
        by_unit.setdefault(w["unit"], []).append(w)
    raw = []
    for u in timing["units"]:
        ws = by_unit.get(u["id"], [])
        i = 0
        for ph in _phrases(u["text"], max_words):
            n = len(ph.split())
            chunk = ws[i:i + n]
            i += n
            if chunk:
                raw.append([chunk[0]["start"], chunk[-1]["end"], ph])
    for k in range(len(raw)):
        nxt = raw[k + 1][0] if k + 1 < len(raw) else None
        end = raw[k][1] + hold
        if nxt is not None:
            end = nxt if nxt - raw[k][1] < bridge else min(end, nxt)
        raw[k][1] = end
    from .numbers import display
    return [(a, b, display(t)) for a, b, t in raw]   # timed on the spoken words, shown with digits
