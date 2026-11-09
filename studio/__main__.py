"""Studio CLI:  python -m studio <command> ...

Commands: new <slug> | status | scenario <ep> | narrate <ep> | build <ep> | upload <ep> [--dry-run] | auth | competitors | analytics
"""
from __future__ import annotations

import argparse
import json
import os
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


def cmd_auth_meta(a):
    from .meta import auth
    auth()


def cmd_social(a):
    from . import meta
    if a.action == "release":
        print(meta.release_assets(episode_dir(a.episode)))
    elif a.action == "publish-due":
        meta.publish_due(dry_run=a.dry_run)


def cmd_competitors(a):
    from .youtube import pull_competitors
    print(pull_competitors())


def cmd_analytics(a):
    from .youtube import pull_analytics
    print(pull_analytics(a.days))


def cmd_stage(a):
    from .pipeline import set_stage
    set_stage(episode_dir(a.episode), a.stage, a.note or "")


def cmd_align(a):
    from .align import align
    print(align(episode_dir(a.episode)))


def cmd_shotlist(a):
    from .pipeline import shotlist
    issues = shotlist(episode_dir(a.episode))
    if any("overlap" in i or "end <= start" in i for i in issues):
        raise SystemExit("shot list has overlaps or empty shots")


def cmd_stills(a):
    from .pipeline import stills
    stills(episode_dir(a.episode), a.times)


def cmd_package(a):
    from .pipeline import package
    package(episode_dir(a.episode))


def cmd_thumbimages(a):
    from .imagegen import generate
    generate(episode_dir(a.episode), force=a.force)


def cmd_thumbcheck(a):
    from .thumbcheck import check
    r = check(episode_dir(a.episode))
    if a.strict and not r["ok"]:
        raise SystemExit(1)


def cmd_slot(a):
    from .pipeline import iso, shorts_times, slot
    from .youtube import local
    t = slot()
    print(json.dumps({"long": iso(t), "long_local": local(t), "shorts": shorts_times(t)}, indent=1))


def cmd_queue(a):
    from .pipeline import queue
    q = queue()
    print(json.dumps(q))
    if a.github_output and os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as f:
            f.write(f"need={'true' if q['need'] else 'false'}\n")


def cmd_notify(a):
    from .notify import send
    send(a.text)


def cmd_finish(a):
    from .pipeline import finish
    r = finish(episode_dir(a.episode))
    if a.strict and not r["ok"]:
        raise SystemExit(1)


def cmd_review_frames(a):
    from .pipeline import frames_for_review
    frames_for_review(episode_dir(a.episode))


def cmd_gate(a):
    from .pipeline import gate
    if not gate(episode_dir(a.episode)):
        raise SystemExit(1)


def cmd_upload_all(a):
    from .pipeline import upload_all
    print(json.dumps(upload_all(episode_dir(a.episode)), indent=1, default=str))



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
    s = sub.add_parser("stage"); s.add_argument("episode"); s.add_argument("stage"); s.add_argument("--note"); s.set_defaults(fn=cmd_stage)
    s = sub.add_parser("align"); s.add_argument("episode"); s.set_defaults(fn=cmd_align)
    s = sub.add_parser("shotlist"); s.add_argument("episode"); s.set_defaults(fn=cmd_shotlist)
    s = sub.add_parser("stills"); s.add_argument("episode"); s.add_argument("times", nargs="+"); s.set_defaults(fn=cmd_stills)
    s = sub.add_parser("package"); s.add_argument("episode"); s.set_defaults(fn=cmd_package)
    s = sub.add_parser("thumbimages"); s.add_argument("episode"); s.add_argument("--force", action="store_true"); s.set_defaults(fn=cmd_thumbimages)
    s = sub.add_parser("thumbcheck"); s.add_argument("episode"); s.add_argument("--strict", action="store_true"); s.set_defaults(fn=cmd_thumbcheck)
    s = sub.add_parser("slot"); s.set_defaults(fn=cmd_slot)
    s = sub.add_parser("queue"); s.add_argument("--github-output", action="store_true"); s.set_defaults(fn=cmd_queue)
    s = sub.add_parser("notify"); s.add_argument("text"); s.set_defaults(fn=cmd_notify)
    s = sub.add_parser("finish"); s.add_argument("episode"); s.add_argument("--strict", action="store_true"); s.set_defaults(fn=cmd_finish)
    s = sub.add_parser("review-frames"); s.add_argument("episode"); s.set_defaults(fn=cmd_review_frames)
    s = sub.add_parser("gate"); s.add_argument("episode"); s.set_defaults(fn=cmd_gate)
    s = sub.add_parser("upload-all"); s.add_argument("episode"); s.set_defaults(fn=cmd_upload_all)
    s = sub.add_parser("auth-meta"); s.set_defaults(fn=cmd_auth_meta)
    s = sub.add_parser("social"); s.add_argument("action", choices=["release", "publish-due"]); s.add_argument("episode", nargs="?"); s.add_argument("--dry-run", action="store_true"); s.set_defaults(fn=cmd_social)
    s = sub.add_parser("competitors"); s.set_defaults(fn=cmd_competitors)
    s = sub.add_parser("analytics"); s.add_argument("--days", type=int, default=28); s.set_defaults(fn=cmd_analytics)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
