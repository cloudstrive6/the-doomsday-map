"""Episode scorecard: each episode's numbers 7 and 28 days after it went public, against the channel targets.

Reads the daily snapshots in data/analytics/ (each holds lifetime numbers per video and cumulative thumbnail reach),
so the snapshot taken on or after publish day + N is that video's N-day result. Writes data/scorecard.md and
data/scorecard.json. No API calls; run it after `python -m studio analytics`.

Targets come from the orchestrated quality pass of 2026-11-10 (Bryce-Brain playbook doomsday-daily-episode) and
are judged on the median of the episodes from FIRST_JUDGED on.
"""
from __future__ import annotations

import datetime as dt
import json
import statistics
from pathlib import Path

from .config import ROOT

DATA = ROOT / "data"
FIRST_JUDGED = 4          # episodes before 004 were made before the 2026-11-09 retention rules: baseline only
HORIZONS = (7, 28)
HOLD_POINT = 0.11         # retention bin used for the opening hold (about 75 to 80 s of a 12 minute video)

# criterion id -> (label, metric key, target, kind)
TARGETS = {
    "C1": ("Long CTR", "ctr", 0.05, "long"),
    "C2": ("Hold at 11%", "hold", 0.60, "long"),
    "C3": ("Avg % viewed", "avp", 40.0, "long"),
    "C4": ("Long views", "views", 150, "long"),
    "C5a": ("Shorts views", "views", 300, "short"),
    "C5b": ("Shorts avg % viewed", "avp", 80.0, "short"),
}
SUBS_TARGET = (50, "2026-12-10")


def _snapshots() -> list[tuple[dt.date, dict]]:
    out = []
    for f in sorted((DATA / "analytics").glob("*.json")):
        try:
            out.append((dt.date.fromisoformat(f.stem), json.loads(f.read_text(encoding="utf-8"))))
        except (ValueError, json.JSONDecodeError):
            continue
    return out


def _hold(curve: list) -> float | None:
    if not curve:
        return None
    best = min(curve, key=lambda p: abs(p[0] - HOLD_POINT))
    return round(float(best[1]), 3) if abs(best[0] - HOLD_POINT) <= 0.03 else None


def _metrics(snap: dict, vid: str) -> dict | None:
    row = next((v for v in snap.get("videos", []) if v.get("video") == vid), None)
    reach = (snap.get("reach") or {}).get("videos", {}).get(vid, {})
    if row is None and not reach:
        return None
    row = row or {}
    return {
        "views": row.get("lifetime_views", row.get("views")),
        "avp": row.get("averageViewPercentage"),
        "avd": row.get("averageViewDuration"),
        "hold": _hold(row.get("retention_curve") or []),
        "subs": row.get("subscribersGained"),
        "ctr": reach.get("ctr"),
        "impressions": reach.get("impressions"),
    }


def _videos() -> list[dict]:
    vids = []
    for ep in sorted((ROOT / "episodes").iterdir()):
        meta = ep / "metadata.json"
        if not (ep.is_dir() and meta.exists() and ep.name[:3].isdigit()):
            continue
        m = json.loads(meta.read_text(encoding="utf-8"))
        if m.get("youtube_id") and m.get("publish_at"):
            vids.append({"episode": ep.name, "num": int(ep.name[:3]), "kind": "long", "id": m["youtube_id"],
                         "title": m.get("title", ""), "publish_at": m["publish_at"]})
        su = ep / "shorts_uploaded.json"
        if su.exists():
            for s in json.loads(su.read_text(encoding="utf-8")):
                if s.get("youtube_id") and s.get("publish_at"):
                    vids.append({"episode": ep.name, "num": int(ep.name[:3]), "kind": "short", "id": s["youtube_id"],
                                 "title": s.get("title", ""), "publish_at": s["publish_at"]})
    return vids


def build() -> dict:
    snaps = _snapshots()
    today = dt.datetime.now(dt.timezone.utc).date()
    rows = []
    for v in _videos():
        pub = dt.datetime.fromisoformat(v["publish_at"].replace("Z", "+00:00")).date()
        for h in HORIZONS:
            due = pub + dt.timedelta(days=h)
            snap = next(((d, s) for d, s in snaps if d >= due), None)
            m = _metrics(snap[1], v["id"]) if snap else None
            rows.append({**v, "horizon": h, "due": due.isoformat(), "snapshot": snap[0].isoformat() if snap else None,
                         "status": "measured" if m else ("missing" if snap else "pending"), **(m or {})})
    verdicts = {}
    for h in HORIZONS:
        for cid, (label, key, target, kind) in TARGETS.items():
            vals = [r[key] for r in rows if r["horizon"] == h and r["kind"] == kind and r["num"] >= FIRST_JUDGED
                    and r["status"] == "measured" and r.get(key) is not None]
            med = statistics.median(vals) if vals else None
            verdicts[f"{cid}@{h}d"] = {"label": label, "target": target, "median": med, "n": len(vals),
                                       "met": (med >= target) if med is not None else None}
    subs = None
    if snaps:
        subs = int(snaps[-1][1].get("channel", {}).get("subscriberCount") or 0)
    out = {"built": today.isoformat(), "latest_snapshot": snaps[-1][0].isoformat() if snaps else None,
           "subscribers": subs, "subs_target": SUBS_TARGET, "verdicts": verdicts, "rows": rows}
    (DATA / "scorecard.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    (DATA / "scorecard.md").write_text(_markdown(out), encoding="utf-8")
    return out


def _fmt(key: str, v) -> str:
    if v is None:
        return "-"
    if key in ("ctr", "hold"):
        return f"{v * 100:.1f}%"
    if key == "avp":
        return f"{v:.0f}%"
    return f"{v:,}" if isinstance(v, int) else f"{v}"


def _markdown(o: dict) -> str:
    L = [f"# Scorecard ({o['built']}, latest snapshot {o['latest_snapshot']})", "",
         f"Built by `python -m studio scorecard` from data/analytics/. Targets judged on the median of episodes "
         f"{FIRST_JUDGED:03d} onward; earlier episodes are the baseline. Small samples: read as tests, not proof.", "",
         f"Subscribers: {o['subscribers']} (target {o['subs_target'][0]} by {o['subs_target'][1]})", "",
         "## Targets", "", "| Criterion | Horizon | Target | Median | Episodes measured | Met |", "|---|---|---|---|---|---|"]
    for k, v in o["verdicts"].items():
        cid, h = k.split("@")
        key = TARGETS[cid][1]
        met = "-" if v["met"] is None else ("yes" if v["met"] else "no")
        L.append(f"| {cid} {v['label']} | {h} | {_fmt(key, v['target'])} | {_fmt(key, v['median'])} | {v['n']} | {met} |")
    for kind, cols in (("long", ("views", "ctr", "impressions", "hold", "avp", "avd")), ("short", ("views", "avp", "avd"))):
        L += ["", f"## {'Long videos' if kind == 'long' else 'Shorts'}", "",
              "| Episode | Video | Days | Status | " + " | ".join(cols) + " |", "|---" * (4 + len(cols)) + "|"]
        for r in o["rows"]:
            if r["kind"] != kind:
                continue
            st = r["status"] if r["status"] != "pending" else f"due {r['due']}"
            L.append(f"| {r['episode'][:3]} | {r['id']} | {r['horizon']} | {st} | " +
                     " | ".join(_fmt(c, r.get(c)) for c in cols) + " |")
    return "\n".join(L) + "\n"
