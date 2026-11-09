"""Turn an episode script.md into narration: one Chirp 3 HD clip per paragraph, a timing file and a normalised WAV.

Script format: `## Section title [TAG]` headers, blank-line-separated paragraphs. Bracketed research references
like [A1, C] are stripped before synthesis. The timing file lists every paragraph with its section, tag, start,
end and duration, so the director can place shots.

usage: python -m studio narrate <episode> [--gap 0.55] [--section-gap 1.0]
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from .config import ROOT, load_config
from . import tts

REF = re.compile(r"\s*\[(?:[A-DS][0-9]*|engine)(?:,\s*(?:[A-DS][0-9]*|engine))*\]")


def parse_script(text: str) -> list[dict]:
    units = []
    section, tag, idx = "", "", 0
    for block in re.split(r"\n\s*\n", text.strip()):
        b = block.strip()
        if not b or b.startswith("# ") or b.lower().startswith("episode 0"):
            continue
        m = re.match(r"^##\s+(.*?)\s*(?:\[([A-Z ]+)\])?\s*$", b)
        if m:
            section, tag = m.group(1).strip(), (m.group(2) or "").strip()
            continue
        if b.startswith("#"):
            continue
        idx += 1
        units.append({"id": f"p{idx:02d}", "section": section, "tag": tag, "text": REF.sub("", b).replace("\n", " ").strip()})
    return units


def narrate(ep: Path, gap: float = 0.55, section_gap: float = 1.0) -> Path:
    cfg = load_config()
    voice = dict(cfg["voice"])
    units = parse_script((ep / "script.md").read_text(encoding="utf-8"))
    out = ep / "narration"
    out.mkdir(exist_ok=True)
    cache = ROOT / "data" / "tts_cache"
    pcm_all = b""
    t = 0.0
    last_section = None
    timing = []
    for u in units:
        if last_section is not None and u["section"] != last_section:
            pcm_all += tts._silence(section_gap - gap) if section_gap > gap else b""
            t += max(0.0, section_gap - gap)
        pcm, real = tts.synthesize(u["text"], voice, cache)
        d = tts.pcm_seconds(pcm)
        timing.append({**u, "start": round(t, 3), "end": round(t + d, 3), "duration": round(d, 3), "words": len(u["text"].split()), "real_voice": real})
        pcm_all += pcm + tts._silence(gap)
        t += d + gap
        last_section = u["section"]
    pcm_all += tts._silence(1.5)
    t += 1.5
    wav = out / "narration.wav"
    tts.write_wav(wav, pcm_all)
    tts.normalize_wav(wav, cfg["video"]["loudness_lufs"], cfg["video"]["true_peak_db"])
    words = sum(x["words"] for x in timing)
    spoken = sum(x["duration"] for x in timing)
    meta = {"voice": voice["name"], "speaking_rate": voice.get("speaking_rate", 1.0), "total_seconds": round(t, 2),
            "words": words, "wpm_speech": round(words / spoken * 60, 1) if spoken else None, "units": timing}
    (out / "timing.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"{ep.name}: {len(timing)} units, {words} words, {t/60:.1f} min, {meta['wpm_speech']} wpm, voice {voice['name']}")
    return wav
