"""Word-level timing for the narration: faster-whisper word timestamps on narration.wav, matched back to the
script's own words (so subtitles keep the script's spelling and punctuation). Writes narration/words.json:
[{"unit": "p01", "word": "Twenty", "start": 0.12, "end": 0.41}, ...] on the narration timeline."""
from __future__ import annotations

import difflib
import json
import re
from pathlib import Path


def _norm(w: str) -> str:
    return re.sub(r"[^a-z0-9]", "", w.lower())


def transcribe(wav: Path, model: str = "large-v3-turbo") -> list[dict]:
    from faster_whisper import WhisperModel
    # CPU int8: this PC has no CUDA runtime libraries (cublas64_12.dll), and 12 minutes of audio takes a few minutes
    m = WhisperModel(model, device="cpu", compute_type="int8")
    import subprocess
    import numpy as np
    # decode with ffmpeg ourselves (the bundled PyAV build does not match faster-whisper's decoder call)
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(wav), "-f", "s16le", "-ac", "1", "-ar", "16000", "-"],
                         capture_output=True, check=True).stdout
    audio = np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0
    segs, _ = m.transcribe(audio, language="en", word_timestamps=True, vad_filter=False, beam_size=5,
                           condition_on_previous_text=False)
    out = []
    for s in segs:
        for w in s.words or []:
            out.append({"word": w.word.strip(), "start": float(w.start), "end": float(w.end)})
    return out


def align(ep: Path, heard: list[dict] | None = None) -> Path:
    timing = json.loads((ep / "narration" / "timing.json").read_text(encoding="utf-8"))
    heard = heard or transcribe(ep / "narration" / "narration.wav")
    (ep / "narration" / "heard.json").write_text(json.dumps(heard), encoding="utf-8")
    script = [(u["id"], w, u) for u in timing["units"] for w in u["text"].split()]
    # whisper writes numbers as digits ("1979", "46"); expand the heard side's tokens so they can match words
    a = [_norm(w) for _, w, _ in script]
    b = [_norm(h["word"]) for h in heard]
    times: list[tuple[float, float] | None] = [None] * len(script)
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                times[i1 + k] = (heard[j1 + k]["start"], heard[j1 + k]["end"])
        elif tag == "replace" and j2 > j1:
            # spread the script words over the heard span (e.g. "nineteen seventy-nine" heard as "1979")
            t0, t1 = heard[j1]["start"], heard[j2 - 1]["end"]
            n = i2 - i1
            lens = [max(1, len(a[i1 + k])) for k in range(n)]
            tot, acc = sum(lens), 0
            for k in range(n):
                s = t0 + (t1 - t0) * acc / tot
                acc += lens[k]
                times[i1 + k] = (s, t0 + (t1 - t0) * acc / tot)
    # anything still unmatched: interpolate inside its unit
    out, matched = [], 0
    for idx, (uid, w, u) in enumerate(script):
        if times[idx] is not None:
            matched += 1
        else:
            prev = next((times[j][1] for j in range(idx - 1, -1, -1) if times[j] and script[j][0] == uid), u["start"])
            nxt = next((times[j][0] for j in range(idx + 1, len(script)) if times[j] and script[j][0] == uid), u["end"])
            times[idx] = (prev, max(prev, nxt))
        s, e = times[idx]
        out.append({"unit": uid, "word": w, "start": round(s, 3), "end": round(e, 3)})
    out = snap(out, timing, silences(ep / "narration" / "narration.wav"))
    path = ep / "narration" / "words.json"
    path.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    print(f"aligned {matched}/{len(script)} script words directly to the audio; heard {len(heard)} words")
    return path


def silences(wav: Path, noise_db: int = -30, min_s: float = 0.1) -> list[tuple[float, float]]:
    """Pauses in the narration. -30 dB suits the compressed Chirp narration (its pauses sit around -35 dB with
    breath noise); gaps under 60 ms between pauses are merged."""
    import subprocess
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(wav), "-af", f"silencedetect=noise={noise_db}dB:d={min_s}",
                        "-f", "null", "-"], capture_output=True, text=True).stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", r)]
    ends = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", r)]
    merged: list[list[float]] = []
    for s0, s1 in zip(starts, ends):
        if merged and s0 - merged[-1][1] < 0.06:
            merged[-1][1] = s1
        else:
            merged.append([s0, s1])
    return [(x, y) for x, y in merged]


def snap(words: list[dict], timing: dict, sil: list[tuple[float, float]]) -> list[dict]:
    """Whisper stretches a word over the pause before it. If a measured pause lies inside a word's span, the word
    is spoken after the pause: move its start there (and end the previous word where the pause began).
    Every word is kept inside its narration unit."""
    units = {u["id"]: u for u in timing["units"]}
    j = 0
    for n, w in enumerate(words):
        u = units[w["unit"]]
        s, e = max(w["start"], u["start"]), min(max(w["end"], w["start"]), u["end"])
        while j < len(sil) and sil[j][1] <= s:
            j += 1
        k = j
        while k < len(sil) and sil[k][0] < e:
            p0, p1 = sil[k]
            if p1 - p0 >= 0.15 and p1 < e - 0.04:
                s = max(s, p1)
                if n and words[n - 1]["unit"] == w["unit"] and words[n - 1]["end"] > p0:
                    words[n - 1]["end"] = round(max(words[n - 1]["start"], p0), 3)
            k += 1
        w["start"], w["end"] = round(s, 3), round(max(s, e), 3)
    return words
