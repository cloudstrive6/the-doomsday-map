"""Facebook + Instagram cross-posting for The Doomsday Map (Meta Graph API), ported from Doomed Doug.

What goes out, only AFTER the video is public on YouTube (so the owner's review window covers Meta too):
  - each Short      -> Instagram Reel + Facebook Reel
  - each episode    -> native Facebook Page video (Instagram can't take 12-min videos)
Instagram fetches videos from a public URL: every episode's files are attached to a GitHub release (public repo).

Env: META_PAGE_ACCESS_TOKEN (never expires), META_PAGE_ID, META_IG_USER_ID; one-time: META_APP_ID,
META_APP_SECRET, META_USER_TOKEN for `python -m studio auth-meta`.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from .config import ROOT, load_config, load_dotenv

V = os.environ.get("META_GRAPH_VERSION", "v23.0")
REPO = os.environ.get("GITHUB_REPOSITORY", "cloudstrive6/the-doomsday-map")


def G(path: str) -> str:
    return f"https://graph.facebook.com/{V}/{path}"


def _req(url, data=None, method=None, headers=None, timeout=120):
    body = urllib.parse.urlencode(data).encode() if isinstance(data, dict) else data
    req = urllib.request.Request(url, data=body, method=method or ("POST" if body else "GET"), headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Meta API {e.code}: {e.read()[:500]!r}") from None


def _token():
    load_dotenv()
    return os.environ["META_PAGE_ACCESS_TOKEN"]


def post(path, params):
    return _req(G(path), {**params, "access_token": _token()})


# ------------------------------------------------------------------ one-time auth


def auth():
    """Short-lived user token -> never-expiring Page token + linked Instagram account. Saves to .env (and GitHub
    secrets with SAVE_SECRETS=1). Tokens are never printed."""
    load_dotenv()
    app_id, secret, short = (os.environ.get(k, "").strip() for k in ("META_APP_ID", "META_APP_SECRET", "META_USER_TOKEN"))
    if not (app_id and secret and short):
        raise SystemExit("Put META_APP_ID, META_APP_SECRET and META_USER_TOKEN in studio/.env first.")
    q = urllib.parse.urlencode({"grant_type": "fb_exchange_token", "client_id": app_id, "client_secret": secret,
                                "fb_exchange_token": short})
    long = _req(G(f"oauth/access_token?{q}"))["access_token"]
    pages = _req(G("me/accounts?fields=id,name,access_token,instagram_business_account{id,username}"
                   f"&access_token={long}")).get("data", [])
    for p in pages:
        print(f"  page: {p['name']} ({p['id']}) -> IG: {(p.get('instagram_business_account') or {}).get('username', 'none linked')}")
    page = next((p for p in pages if "doomsday" in p["name"].lower()), None)
    if not page:
        raise SystemExit("No Page named like 'The Doomsday Map' found for this login (is the Page ticked in the consent dialog?).")
    ig = page.get("instagram_business_account")
    dbg = _req(G(f"debug_token?input_token={page['access_token']}&access_token={app_id}|{secret}")).get("data", {})
    print("Page token expires:", "never" if not dbg.get("expires_at") else
          dt.datetime.fromtimestamp(dbg["expires_at"]).isoformat())
    vals = {"META_PAGE_ACCESS_TOKEN": page["access_token"], "META_PAGE_ID": page["id"]}
    if ig:
        vals["META_IG_USER_ID"] = ig["id"]
        print("Instagram linked:", "@" + ig.get("username", "?"))
    else:
        print("WARNING: no Instagram professional account linked to the Page (Page settings -> Linked accounts).")
    env = ROOT / ".env"
    lines = [l for l in env.read_text(encoding="utf-8").splitlines() if l.split("=", 1)[0] not in vals]
    lines += [f"{k}={v}" for k, v in vals.items()]
    env.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("Saved", ", ".join(vals), "to studio/.env")
    if os.environ.get("SAVE_SECRETS") == "1":
        for k, v in vals.items():
            subprocess.run(["gh", "secret", "set", k], input=v, text=True, check=True, cwd=ROOT)
        print("Saved them to GitHub secrets.")


# ------------------------------------------------------------------ media hosting
# build/ is not in git, so the cloud runner gets videos from GitHub releases: a DRAFT release ep-NNN (private)
# filled at upload time, and a public release only for files that are already live on YouTube.

PUBLIC_TAG = "public-media"


def _gh(*args, check=True):
    return subprocess.run(["gh", *args, "--repo", REPO], capture_output=True, text=True, check=check)


def release_assets(ep: Path) -> list[str]:
    tag = "ep-" + ep.name[:3]
    files = [p for p in [ep / "build" / "final.mp4", *sorted((ep / "build" / "shorts").glob("s[0-9].mp4"))] if p.exists()]
    if _gh("release", "view", tag, check=False).returncode != 0:
        subprocess.run(["gh", "release", "create", tag, "--repo", REPO, "--draft", "--title", f"Episode {ep.name}",
                        "--notes", "Private media store for cross-posting.", *map(str, files)], check=True)
    elif files:
        subprocess.run(["gh", "release", "upload", tag, "--repo", REPO, "--clobber", *map(str, files)], check=True)
    return [p.name for p in files]


def local_file(ep: Path, name: str) -> Path:
    f = (ep / "build" / name) if name == "final.mp4" else (ep / "build" / "shorts" / name)
    if not f.exists():
        f.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["gh", "release", "download", "ep-" + ep.name[:3], "--repo", REPO, "--pattern", name,
                        "--dir", str(f.parent), "--clobber"], check=True)
    return f


def public_url(ep: Path, name: str) -> str:
    """Publish one file to the public release (only called once the video is live on YouTube)."""
    f = local_file(ep, name)
    pub = f.parent / f"{ep.name[:3]}-{name}"
    if not pub.exists():
        pub.write_bytes(f.read_bytes())
    if _gh("release", "view", PUBLIC_TAG, check=False).returncode != 0:
        subprocess.run(["gh", "release", "create", PUBLIC_TAG, "--repo", REPO, "--title", "Published media",
                        "--notes", "Videos already public on YouTube, hosted for Facebook and Instagram to fetch."], check=True)
    subprocess.run(["gh", "release", "upload", PUBLIC_TAG, "--repo", REPO, "--clobber", str(pub)], check=True)
    return f"https://github.com/{REPO}/releases/download/{PUBLIC_TAG}/{pub.name}"


# ------------------------------------------------------------------ publishing


def _wait_ig(container: str, minutes=20):
    until = time.time() + minutes * 60
    while time.time() < until:
        j = _req(G(f"{container}?fields=status_code,status&access_token={_token()}"))
        if j.get("status_code") == "FINISHED":
            return
        if j.get("status_code") in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"IG container {container} {j.get('status_code')}: {j.get('status')}")
        time.sleep(10)
    raise RuntimeError(f"IG container {container} not ready after {minutes} min")


def instagram_reel(video_url: str, caption: str) -> dict:
    ig = os.environ["META_IG_USER_ID"]
    c = post(f"{ig}/media", {"media_type": "REELS", "video_url": video_url, "caption": caption, "share_to_feed": "true"})
    _wait_ig(c["id"])
    pid = post(f"{ig}/media_publish", {"creation_id": c["id"]})["id"]
    link = _req(G(f"{pid}?fields=permalink&access_token={_token()}")).get("permalink")
    return {"id": pid, "url": link}


def facebook_reel(file: Path, description: str) -> dict:
    page = os.environ["META_PAGE_ID"]
    start = post(f"{page}/video_reels", {"upload_phase": "start"})
    data = file.read_bytes()
    url = start.get("upload_url") or f"https://rupload.facebook.com/video-upload/{V}/{start['video_id']}"
    _req(url, data=data, method="POST", headers={"Authorization": f"OAuth {_token()}", "offset": "0",
                                                 "file_size": str(len(data))}, timeout=1800)
    post(f"{page}/video_reels", {"upload_phase": "finish", "video_id": start["video_id"], "video_state": "PUBLISHED",
                                 "description": description})
    return {"id": start["video_id"], "url": f"https://www.facebook.com/reel/{start['video_id']}"}


def instagram_story(video_url: str) -> dict:
    """Instagram Story (9:16 video, max 60 s). Stories take no caption and API stories can't carry link stickers."""
    ig = os.environ["META_IG_USER_ID"]
    c = post(f"{ig}/media", {"media_type": "STORIES", "video_url": video_url})
    _wait_ig(c["id"])
    return {"id": post(f"{ig}/media_publish", {"creation_id": c["id"]})["id"]}


def facebook_story(file: Path) -> dict:
    """Facebook Page Story (9:16 video, max 60 s): start -> binary upload -> finish."""
    page = os.environ["META_PAGE_ID"]
    start = post(f"{page}/video_stories", {"upload_phase": "start"})
    data = file.read_bytes()
    url = start.get("upload_url") or f"https://rupload.facebook.com/video-upload/{V}/{start['video_id']}"
    _req(url, data=data, method="POST", headers={"Authorization": f"OAuth {_token()}", "offset": "0",
                                                 "file_size": str(len(data))}, timeout=1800)
    j = post(f"{page}/video_stories", {"upload_phase": "finish", "video_id": start["video_id"]})
    return {"id": j.get("post_id") or start["video_id"]}


def facebook_video(video_url: str, title: str, description: str) -> dict:
    page = os.environ["META_PAGE_ID"]
    j = _req(f"https://graph-video.facebook.com/{V}/{page}/videos",
             {"file_url": video_url, "title": title, "description": description, "access_token": _token()}, timeout=600)
    return {"id": j["id"], "url": f"https://www.facebook.com/{page}/videos/{j['id']}"}



def _is_live(ts: str | None) -> bool:
    if not ts:
        return False
    return dt.datetime.fromisoformat(ts.replace("Z", "+00:00")) <= dt.datetime.now(dt.timezone.utc)


def _hashtags() -> str:
    return load_config().get("social", {}).get("hashtags", "#nuclearwar #whatif #simulation #TheDoomsdayMap")


def _try(fn, label, store, key, errors, tries_key):
    try:
        store[key] = fn()
        store.pop(key + "_error", None)
        return f"{label}: {store[key].get('url') or store[key].get('id')}"
    except Exception as e:
        store[key + "_error"] = str(e)[:300]
        store[tries_key] = store.get(tries_key, 0) + 1
        errors.append(f"{label} failed: {str(e)[:200]}")
        return None


def publish_due(dry_run: bool = False) -> list[str]:
    """Cross-post everything whose YouTube publish time has passed and has not gone to Meta yet. Idempotent: what was
    posted is recorded in metadata.json (episode) and shorts_uploaded.json (Shorts); 3 tries per item."""
    load_dotenv()
    cfg = load_config().get("social", {})
    if not os.environ.get("META_PAGE_ACCESS_TOKEN"):
        print("Meta not configured (META_PAGE_ACCESS_TOKEN missing); nothing to do.")
        return []
    from . import notify
    done, errors = [], []
    has_ig = bool(os.environ.get("META_IG_USER_ID"))
    start = str(cfg.get("instagram_start") or "")
    if has_ig and start and dt.date.today().isoformat() < start:
        has_ig = False  # warm-up: a brand-new Instagram account posts by hand first (config social.instagram_start)
    for ep in sorted(p for p in (ROOT / "episodes").iterdir() if p.is_dir()):
        mp = ep / "metadata.json"
        if not mp.exists():
            continue
        meta = json.loads(mp.read_text(encoding="utf-8"))
        if not meta.get("youtube_id"):
            continue
        social = meta.setdefault("social", {})
        yt_url = meta.get("url") or f"https://youtu.be/{meta['youtube_id']}"
        if cfg.get("facebook_long", True) and _is_live(meta.get("publish_at") or meta.get("uploaded_at")) \
                and not social.get("facebook_video") and social.get("facebook_video_tries", 0) < 3:
            premise = meta["description"].split("\n\n")[0]
            desc = f"{premise}\n\nWatch on YouTube: {yt_url}\n\n{_hashtags()}"
            if dry_run:
                print("[dry] FB video:", meta["title"])
            else:
                r = _try(lambda: facebook_video(public_url(ep, "final.mp4"), meta["title"], desc),
                         f"FB video {meta['title']}", social, "facebook_video", errors, "facebook_video_tries")
                if r:
                    done.append(r)
                mp.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
        sp = ep / "shorts_uploaded.json"
        if not sp.exists():
            continue
        shorts = json.loads(sp.read_text(encoding="utf-8"))
        for s in shorts:
            if not (s.get("youtube_id") and _is_live(s.get("publish_at"))):
                continue
            sm = s.setdefault("social", {})
            name = f"{s['id']}.mp4"
            title = s["title"].replace(" #shorts", "")
            fb_caption = f"{title}\n\nFull simulation on YouTube: {yt_url}\n\n{_hashtags()}"
            ig_caption = f"{title}\n\nFull simulation on YouTube: The Doomsday Map (link in bio)\n\n{_hashtags()}"
            fresh = dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(
                s["publish_at"].replace("Z", "+00:00")) < dt.timedelta(hours=24)
            jobs = []
            if cfg.get("facebook_reels", True):
                jobs.append(("facebook", f"FB reel {title}", lambda: facebook_reel(local_file(ep, name), fb_caption)))
            if has_ig and cfg.get("instagram_reels", True):
                jobs.append(("instagram", f"IG reel {title}", lambda: instagram_reel(public_url(ep, name), ig_caption)))
            if fresh and cfg.get("facebook_stories", True):
                jobs.append(("facebook_story", f"FB story {title}", lambda: facebook_story(local_file(ep, name))))
            if fresh and has_ig and cfg.get("instagram_stories", True):
                jobs.append(("instagram_story", f"IG story {title}", lambda: instagram_story(public_url(ep, name))))
            for key, label, fn in jobs:
                if sm.get(key) or sm.get(key + "_tries", 0) >= 3:
                    continue
                if dry_run:
                    print("[dry]", label)
                    continue
                r = _try(fn, label, sm, key, errors, key + "_tries")
                if r:
                    done.append(r)
            sp.write_text(json.dumps(shorts, indent=2, ensure_ascii=False), encoding="utf-8")
    if done:
        notify.send("Posted to Facebook/Instagram:\n" + "\n".join(done))
    if errors:
        notify.send("Cross-posting problems:\n" + "\n".join(errors))
    for line in done + errors:
        print(line.encode("ascii", "replace").decode())
    return done
