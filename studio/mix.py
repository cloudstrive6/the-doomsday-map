"""Audio mix for an episode: narration + looped music beds (crossfaded) ducked under the voice + sound effects,
then two-pass loudness normalisation of the whole mix to YouTube's reference (-14 LUFS, true peak -1.5 dBTP).

episode.json fields used:
  "musicPlan": [{"src": "bed.mp3", "from": 0, "to": 284.5, "loop": [0, 176], "gain_db": -20}, ...]
      src under assets/music; loop = clean section of the source to repeat (seconds); gain relative to the source
  "sfxPlan": [{"src": "impact.mp3", "t": 45.4, "gain_db": -8}, ...]   src under assets/sfx
  "slateMusicLiftDb": 10  optional; after the last spoken word the music rises by this much (default 10 dB) so the end
      slate is not quiet (measured on 003, 2026-11-09: the bed alone sat at -24 LUFS against -14 for the voice;
      a 10 dB lift brings the slate to about -18.5 LUFS)
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from .config import ROOT, load_config
from . import tts

XFADE = 4.0
FADE = 2.0
SLATE_LIFT_DB = 10.0
SLATE_RAMP = 1.5


def _music_segment_filter(idx: int, seg: dict, label: str) -> str:
    """Filter graph for one music segment from input #idx: loop its clean section with crossfades, cut to length,
    fade in and out, apply gain and place it on the timeline."""
    a, b = seg.get("loop", [0, 170])
    piece = b - a
    dur = seg["to"] - seg["from"]
    copies = max(1, int((dur + XFADE) // (piece - XFADE)) + 1)
    parts = [f"[{idx}:a]aformat=sample_rates=48000:channel_layouts=stereo,asplit={copies}" + "".join(f"[{label}s{i}]" for i in range(copies)) + ";"]
    for i in range(copies):
        parts.append(f"[{label}s{i}]atrim={a}:{b},asetpts=PTS-STARTPTS[{label}p{i}];")
    cur = f"{label}p0"
    for i in range(1, copies):
        nxt = f"{label}x{i}"
        parts.append(f"[{cur}][{label}p{i}]acrossfade=d={XFADE}:c1=tri:c2=tri[{nxt}];")
        cur = nxt
    gain = seg.get("gain_db", -18)
    delay_ms = int(round(seg["from"] * 1000))
    parts.append(f"[{cur}]atrim=0:{dur:.3f},asetpts=PTS-STARTPTS,afade=t=in:st=0:d={FADE},afade=t=out:st={max(0, dur - FADE):.3f}:d={FADE},"
                 f"volume={gain}dB,adelay={delay_ms}|{delay_ms}[{label}];")
    return "".join(parts)


def mix(ep: Path, video_in: Path, out: Path) -> dict:
    cfg = load_config()["video"]
    shot = json.loads((ep / "episode.json").read_text(encoding="utf-8"))
    nar = ep / "narration" / "narration.wav"
    total = float(shot["durationSeconds"])
    inputs = ["-i", str(nar)]
    fc = ["[0:a]aformat=sample_rates=48000:channel_layouts=stereo,apad,atrim=0:%.3f[voice];" % total]
    music_labels, n = [], 1
    for k, seg in enumerate(shot.get("musicPlan", [])):
        src = ROOT / "assets" / "music" / seg["src"]
        if not src.exists():
            print("missing music", src)
            continue
        inputs += ["-i", str(src)]
        lab = f"m{k}"
        fc.append(_music_segment_filter(n, seg, lab))
        music_labels.append(lab)
        n += 1
    sfx_labels = []
    for k, fx in enumerate(shot.get("sfxPlan", [])):
        src = ROOT / "assets" / "sfx" / fx["src"]
        if not src.exists():
            continue
        inputs += ["-i", str(src)]
        d = int(round(fx["t"] * 1000))
        lab = f"f{k}"
        fc.append(f"[{n}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={fx.get('gain_db', -10)}dB,adelay={d}|{d}[{lab}];")
        sfx_labels.append(lab)
        n += 1
    if music_labels:
        fc.append("".join(f"[{l}]" for l in music_labels) + f"amix=inputs={len(music_labels)}:normalize=0:duration=longest,apad,atrim=0:{total:.3f}[musicraw];")
        # lift the music over the end slate, from the last spoken word to the end (ramped, so it swells rather than jumps)
        lift = float(shot.get("slateMusicLiftDb", SLATE_LIFT_DB))
        timing_p = ep / "narration" / "timing.json"
        last_word = json.loads(timing_p.read_text(encoding="utf-8"))["total_seconds"] if timing_p.exists() else None
        if lift and last_word and last_word < total:
            k = 10 ** (lift / 20) - 1
            fc.append(f"[musicraw]volume=eval=frame:volume='1+{k:.4f}*clip((t-{last_word:.3f})/{SLATE_RAMP},0,1)'[music];")
        else:
            fc.append("[musicraw]anull[music];")
        # duck the music under the narration (sidechain), keep it full in the pauses
        fc.append("[voice]asplit=2[v1][vkey];[music][vkey]sidechaincompress=threshold=0.03:ratio=5:attack=60:release=700:makeup=1[mduck];")
        bus = ["[v1]", "[mduck]"]
    else:
        bus = ["[voice]"]
    bus += [f"[{l}]" for l in sfx_labels]
    fc.append("".join(bus) + f"amix=inputs={len(bus)}:normalize=0:duration=first,atrim=0:{total:.3f}[mix]")
    wav = out.with_suffix(".mix.wav")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", "".join(fc), "-map", "[mix]", "-ar", "48000", "-c:a", "pcm_s16le", str(wav)]
    subprocess.run(cmd, check=True)
    loud = _normalize_stereo(wav, cfg["loudness_lufs"], cfg["true_peak_db"])
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video_in), "-i", str(wav), "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-shortest", "-movflags", "+faststart", str(out)], check=True)
    wav.unlink(missing_ok=True)
    return loud


def _normalize_stereo(path: Path, lufs: float, true_peak: float) -> dict:
    tgt = f"I={lufs}:TP={true_peak - 0.3}:LRA=11"
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", f"loudnorm={tgt}:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    m = json.loads(r[r.rindex("{"):r.rindex("}") + 1])
    tmp = path.with_suffix(".n.wav")
    af = (f"loudnorm={tgt}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
          f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(path), "-af", af, "-ar", "48000", "-c:a", "pcm_s16le", str(tmp)], check=True)
    tmp.replace(path)
    got = tts.measure(path)
    if got["I"] < lufs - 1.0:
        # linear mode was capped by the peak ceiling: limit the peaks once, then normalise again
        lim = path.with_suffix(".l.wav")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(path), "-af",
                        "aresample=192000,alimiter=limit=0.7:attack=1:release=60:level=false,aresample=48000",
                        "-c:a", "pcm_s16le", str(lim)], check=True)
        lim.replace(path)
        return _normalize_stereo(path, lufs, true_peak)
    print(f"mix loudness {got['I']} LUFS, true peak {got['TP']} dBTP")
    return got
