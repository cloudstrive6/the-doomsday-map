"""Studio CLI:  python -m studio <command> ...

Commands: new <slug> | status | scenario <ep> | narrate <ep> | build <ep> | upload <ep> [--dry-run] | auth
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .config import ROOT, episode_dir, load_config


def cmd_new(a):
    eps = ROOT / "episodes"
    nums = [int(d.name[:3]) for d in eps.iterdir() if d.is_dir() and d.name[:3].isdigit()]
    n = max(nums, default=0) + 1
    ep = eps / f"{n:03d}-{a.slug}"
    ep.mkdir(parents=True)
    (ep / "brief.md").write_text(f"# Episode {n:03d}: {a.slug}\n", encoding="utf-8")
    print(ep)


def cmd_status(a):
    for d in sorted((ROOT / "episodes").iterdir()):
        if d.is_dir():
            meta = d / "metadata.json"
            m = json.loads(meta.read_text(encoding="utf-8")) if meta.exists() else {}
            have = [f for f in ("research.md", "scenario.json", "script.md", "narration/timing.json", "episode.json", "build/final.mp4") if (d / f).exists()]
            print(f"{d.name:40} {m.get('youtube_id') or '-':14} {', '.join(have)}")


def cmd_scenario(a):
    from .scenario import compute_file
    out = compute_file(episode_dir(a.episode) / "scenario.json")
    d = json.loads(out.read_text(encoding="utf-8"))
    print(out)
    print("totals", d["totals"], "sun", d["sun"])
    for r in d["strikes"]:
        e = r["effects"]
        if e is None:
            print(f"  {r['id']:16} impact {r['impact_min']:5.1f} min  conventional  {r['distance_km']:.0f} km, flight {r['flight_min']} min")
            continue
        print(f"  {r['id']:16} impact {r['impact_min']:5.1f} min  {r['yield_kt']:>5} kt {r['burst']:6}  psi5 {e['psi5_km']:5.2f} km  burns {e['thermal3_km']:5.2f} km")


def cmd_narrate(a):
    from .narrate import narrate
    narrate(episode_dir(a.episode), gap=a.gap, section_gap=a.section_gap)


def cmd_build(a):
    from .build import build
    build(episode_dir(a.episode), chunks=a.chunks, local=a.local)


def cmd_upload(a):
    from .youtube import upload_episode
    meta = upload_episode(episode_dir(a.episode), dry_run=a.dry_run, publish_at_override=a.publish_at)
    print(json.dumps({k: meta.get(k) for k in ("title", "youtube_id", "publish_at", "url", "upload_warnings")}, indent=1))


def cmd_auth(a):
    from .youtube import auth
    auth()


def main(argv=None):
    p = argparse.ArgumentParser(prog="studio")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("new"); s.add_argument("slug"); s.set_defaults(fn=cmd_new)
    s = sub.add_parser("status"); s.set_defaults(fn=cmd_status)
    s = sub.add_parser("scenario"); s.add_argument("episode"); s.set_defaults(fn=cmd_scenario)
    s = sub.add_parser("narrate"); s.add_argument("episode"); s.add_argument("--gap", type=float, default=0.55); s.add_argument("--section-gap", type=float, default=1.1); s.set_defaults(fn=cmd_narrate)
    s = sub.add_parser("build"); s.add_argument("episode"); s.add_argument("--chunks", type=int, default=8); s.add_argument("--local", action="store_true"); s.set_defaults(fn=cmd_build)
    s = sub.add_parser("upload"); s.add_argument("episode"); s.add_argument("--dry-run", action="store_true"); s.add_argument("--publish-at"); s.set_defaults(fn=cmd_upload)
    s = sub.add_parser("auth"); s.set_defaults(fn=cmd_auth)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
