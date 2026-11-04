"""Narration via Google Cloud Text-to-Speech (Chirp 3: HD voices), REST + API key.

Env: GOOGLE_TTS_API_KEY (restrict the key to the Text-to-Speech API only).
Without a key (local dry runs) a silent track with an estimated duration is produced
so the rest of the pipeline can still be tested.
"""
from __future__ import annotations

import base64
import hashlib
import io
import json
import os
import time
import urllib.error
import urllib.request
import wave
from pathlib import Path

SAMPLE_RATE = 24000
ENDPOINT = "https://texttospeech.googleapis.com/v1/text:synthesize"


def _silence(seconds: float) -> bytes:
    return b"\x00\x00" * int(SAMPLE_RATE * seconds)


def wav_bytes_to_pcm(data: bytes) -> bytes:
    with wave.open(io.BytesIO(data)) as w:
        if w.getframerate() != SAMPLE_RATE or w.getnchannels() != 1 or w.getsampwidth() != 2:
            raise ValueError("unexpected TTS audio format")
        return w.readframes(w.getnframes())


def synthesize(text: str, voice: dict, cache_dir: Path) -> tuple[bytes, bool]:
    """Return (pcm16 mono 24 kHz, is_real_voice)."""
    from .config import load_dotenv
    load_dotenv()
    key = os.environ.get("GOOGLE_TTS_API_KEY")
    cache_dir.mkdir(parents=True, exist_ok=True)
    import re
    prons = [p for p in voice.get("pronunciations", []) if re.search(rf"\b{re.escape(p['phrase'])}\b", text)]
    voice = {k: v for k, v in voice.items() if k != "pronunciations"}
    # cache key only changes for lines that actually contain a custom-pronounced phrase
    h = hashlib.sha1(json.dumps([text, voice] + ([prons] if prons else []), sort_keys=True).encode()).hexdigest()[:16]
    cached = cache_dir / f"{h}.pcm"
    if cached.exists():
        os.utime(cached)  # mark as recently used (CI prunes clips unused for 21 days)
        return cached.read_bytes(), True
    if not key:
        words = max(1, len(text.split()))
        wpm = voice.get("fallback_wpm", 165) * voice.get("speaking_rate", 1.0)
        return _silence(words / wpm * 60), False

    body = {
        "input": {"text": text},
        "voice": {"languageCode": voice.get("language", "en-US"), "name": voice["name"]},
        "audioConfig": {"audioEncoding": "LINEAR16", "sampleRateHertz": SAMPLE_RATE},
    }
    if prons:
        body["input"]["customPronunciations"] = {"pronunciations": [
            {"phrase": p["phrase"], "phoneticEncoding": "PHONETIC_ENCODING_IPA", "pronunciation": p["ipa"]} for p in prons]}
    if voice.get("speaking_rate", 1.0) != 1.0:
        body["audioConfig"]["speakingRate"] = voice["speaking_rate"]
    last = None
    for attempt in range(6):
        req = urllib.request.Request(f"{ENDPOINT}?key={key}", data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                audio = base64.b64decode(json.loads(r.read())["audioContent"])
            pcm = wav_bytes_to_pcm(audio)
            cached.write_bytes(pcm)
            return pcm, True
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}: {e.read()[:300]!r}"
            if e.code == 400 and "speakingRate" in last and "speakingRate" in body["audioConfig"]:
                body["audioConfig"].pop("speakingRate")  # voice doesn't support pace control
                continue
            if e.code == 400 and "ustomPronunciation" in last and "customPronunciations" in body["input"]:
                body["input"].pop("customPronunciations")  # voice/API doesn't support it
                continue
            if e.code not in (429, 500, 502, 503, 504):
                break
        except Exception as e:  # network hiccup
            last = repr(e)
        time.sleep(2 ** attempt)
    raise RuntimeError(f"TTS failed for text {text[:60]!r}: {last}")


def write_wav(path: Path, pcm: bytes):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        w.writeframes(pcm)


def normalize_wav(path: Path, lufs: float = -14.0, true_peak: float = -1.5):
    """Bring a narration WAV to YouTube's playback reference loudness (-14 LUFS integrated): YouTube turns louder
    uploads down but never turns quiet ones up, and raw Chirp 3 HD sits near -20 LUFS. One gain for the whole track
    (the voice keeps its dynamics) plus a peak limiter that only touches the few plosives above the ceiling; the
    sample rate and length stay the same, so shot timing is unchanged."""
    import re
    import subprocess

    def measure(p: Path) -> float | None:
        r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(p), "-af", "ebur128", "-f", "null", "-"],
                           capture_output=True, text=True)
        m = re.findall(r"I:\s+(-?[\d.]+|-inf) LUFS", r.stderr)
        if r.returncode or not m:
            raise RuntimeError(f"loudness measure failed for {p.name}: {r.stderr[-300:]}")
        return None if m[-1] == "-inf" else float(m[-1])

    now = measure(path)
    if now is None or abs(now - lufs) < 0.5:
        return
    tmp = path.with_suffix(".norm.wav")
    ceiling = 10 ** ((true_peak - 0.5) / 20)  # 0.5 dB extra headroom for inter-sample peaks after AAC encoding
    gain = lufs - now
    for _ in range(4):  # always from the original; the gain is corrected for what the compressor/limiter took
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(path), "-af",
                        # gentle voice compression evens out syllable peaks so the limiter only catches plosives
                        f"acompressor=threshold=0.1:ratio=2.5:attack=5:release=120:knee=4,volume={gain:.2f}dB,"
                        f"alimiter=limit={ceiling:.4f}:attack=1:release=50:level=false",
                        "-ar", str(SAMPLE_RATE), "-ac", "1", "-c:a", "pcm_s16le", str(tmp)], check=True)
        got = measure(tmp)
        if got is None or abs(got - lufs) < 0.3:
            break
        gain += lufs - got
    tmp.replace(path)


def pcm_seconds(pcm: bytes) -> float:
    return len(pcm) / 2 / SAMPLE_RATE
