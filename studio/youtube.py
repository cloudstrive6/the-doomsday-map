"""YouTube Data + Analytics API: auth, scheduled upload, captions, thumbnail, playlists, stats.

Env (same names as the InforMed blueprint): YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import statistics
import subprocess
from pathlib import Path

from .config import ROOT, load_config

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
    "https://www.googleapis.com/auth/yt-analytics-monetary.readonly",
]


def _load_dotenv():
    from .config import load_dotenv
    load_dotenv()


def credentials():
    _load_dotenv()
    from google.oauth2.credentials import Credentials
    missing = [k for k in ("YOUTUBE_CLIENT_ID", "YOUTUBE_CLIENT_SECRET", "YOUTUBE_REFRESH_TOKEN") if not os.environ.get(k)]
    if missing:
        raise RuntimeError(f"missing env: {', '.join(missing)} (run `python -m studio auth`)")
    return Credentials(None, refresh_token=os.environ["YOUTUBE_REFRESH_TOKEN"],
                       client_id=os.environ["YOUTUBE_CLIENT_ID"],
                       client_secret=os.environ["YOUTUBE_CLIENT_SECRET"],
                       token_uri="https://oauth2.googleapis.com/token", scopes=SCOPES)


def yt():
    from googleapiclient.discovery import build
    return build("youtube", "v3", credentials=credentials(), cache_discovery=False)


def yta():
    from googleapiclient.discovery import build
    return build("youtubeAnalytics", "v2", credentials=credentials(), cache_discovery=False)


# ------------------------------------------------------------------ auth


def auth():
    """One-time: authorize the channel, store the refresh token in .env (+ GitHub secrets if SAVE_SECRETS=1).
    The token is never printed."""
    _load_dotenv()
    from google_auth_oauthlib.flow import InstalledAppFlow
    cid, secret = os.environ.get("YOUTUBE_CLIENT_ID"), os.environ.get("YOUTUBE_CLIENT_SECRET")
    if not cid or not secret:
        raise SystemExit("Put YOUTUBE_CLIENT_ID and YOUTUBE_CLIENT_SECRET in studio/.env first.")
    flow = InstalledAppFlow.from_client_config(
        {"installed": {"client_id": cid, "client_secret": secret,
                       "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                       "token_uri": "https://oauth2.googleapis.com/token",
                       "redirect_uris": ["http://127.0.0.1:53682/"]}}, SCOPES)
    creds = flow.run_local_server(host="127.0.0.1", port=53682, prompt="consent", access_type="offline",
                                  open_browser=os.environ.get("AUTH_NO_BROWSER") != "1",
                                  authorization_prompt_message="AUTH_URL {url}")
    _set_env_value("YOUTUBE_REFRESH_TOKEN", creds.refresh_token)
    print("Saved YOUTUBE_REFRESH_TOKEN to studio/.env")
    if os.environ.get("SAVE_SECRETS") == "1":
        for k, v in (("YOUTUBE_CLIENT_ID", cid), ("YOUTUBE_CLIENT_SECRET", secret),
                     ("YOUTUBE_REFRESH_TOKEN", creds.refresh_token)):
            subprocess.run(["gh", "secret", "set", k], input=v, text=True, check=True, cwd=ROOT)
        print("Saved the three YouTube secrets to GitHub.")
    os.environ["YOUTUBE_REFRESH_TOKEN"] = creds.refresh_token
    me = yt().channels().list(part="snippet", mine=True).execute()
    print("Authorized channel:", me["items"][0]["snippet"]["title"] if me.get("items") else "(none found)")


def _set_env_value(key, value):
    env = ROOT / ".env"
    lines = env.read_text(encoding="utf-8").splitlines() if env.exists() else []
    lines = [l for l in lines if not l.startswith(key + "=")] + [f"{key}={value}"]
    env.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ------------------------------------------------------------------ scheduling


def local(ts: str | dt.datetime | None) -> str:
    """Format a UTC timestamp in the owner's display timezone (NZ), e.g. 'Wed 30 Sep 2:00 PM NZDT'."""
    if not ts:
        return ""
    from zoneinfo import ZoneInfo
    tz = ZoneInfo(load_config()["schedule"].get("display_timezone", "Pacific/Auckland"))
    d = _parse_utc(ts) if isinstance(ts, str) else ts
    return d.astimezone(tz).strftime("%a %d %b %I:%M %p %Z").replace(" 0", " ")


def _parse_utc(s: str) -> dt.datetime:
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(dt.timezone.utc)


def in_launch_phase(uploaded_count: int | None = None) -> bool:
    launch = load_config()["schedule"].get("launch") or {}
    n = len(taken_slots()) if uploaded_count is None else uploaded_count
    return n < int(launch.get("episodes", 0))


def next_publish_slot(taken: list[str] | None = None) -> dt.datetime:
    """Next free publish slot >= review_window_days away. Launch phase (first N uploads): every launch day;
    afterwards: the weekly publish_days."""
    from zoneinfo import ZoneInfo
    cfg = load_config()["schedule"]
    tz = ZoneInfo(cfg["timezone"])
    days = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}
    taken = list(taken or [])
    launch = in_launch_phase(len(taken))
    wanted = {days[d] for d in (cfg["launch"]["publish_days"] if launch else cfg["publish_days"])}
    hh, mm = map(int, cfg["publish_time"].split(":"))
    earliest = dt.datetime.now(tz) + dt.timedelta(days=cfg["review_window_days"])
    used = {_parse_utc(t) for t in taken}
    d = earliest.date()
    for _ in range(400):
        cand = dt.datetime(d.year, d.month, d.day, hh, mm, tzinfo=tz)
        if cand.weekday() in wanted and cand >= earliest and cand.astimezone(dt.timezone.utc) not in used:
            return cand
        d += dt.timedelta(days=1)
    raise RuntimeError("no publish slot found")


def queue_status() -> dict:
    """How many episodes are scheduled but not yet public, and whether production should make another."""
    from .__main__ import get_stage
    cfg = load_config()["schedule"]
    now = dt.datetime.now(dt.timezone.utc)
    taken = taken_slots()
    queued = sum(1 for t in taken if _parse_utc(t) > now)
    in_progress = [d.name for d in sorted((ROOT / "episodes").iterdir())
                   if d.is_dir() and (d / "status.json").exists() and get_stage(d) != "uploaded"]
    launch = in_launch_phase(len(taken))
    target = int(cfg["launch"]["queue_target"]) if launch else int(cfg.get("episodes_ahead", 1))
    return {"uploaded_total": len(taken), "queued": queued, "target": target, "phase": "launch" if launch else "weekly",
            "in_progress": in_progress, "need_episode": bool(in_progress) or queued < target}


def taken_slots() -> list[str]:
    out = []
    for m in (ROOT / "episodes").glob("*/metadata.json"):
        j = json.loads(m.read_text(encoding="utf-8"))
        if j.get("publish_at") and j.get("youtube_id"):
            out.append(j["publish_at"])
    return out


# ------------------------------------------------------------------ upload


def upload_episode(ep_dir: Path, dry_run: bool = False, publish_at_override: str | None = None) -> dict:
    from googleapiclient.http import MediaFileUpload
    cfg = load_config()
    meta_path = ep_dir / "metadata.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    if meta.get("youtube_id"):
        return meta
    video = ep_dir / "build" / "final.mp4"
    thumb = ep_dir / "build" / "thumbnail.png"
    srt = ep_dir / "build" / "captions.srt"
    chapters = ep_dir / "build" / "chapters.txt"
    ch_text = chapters.read_text(encoding="utf-8").strip() if chapters.exists() else ""
    meta["description"] = meta["description"].replace("{{CHAPTERS}}", ch_text).replace("\n\n\n", "\n\n")
    slot = _parse_utc(publish_at_override) if publish_at_override else next_publish_slot(taken_slots())
    publish_at = slot.astimezone(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    body = {
        "snippet": {
            "title": meta["title"][:100],
            "description": meta["description"][:5000],
            "tags": (meta.get("tags") or cfg["channel"]["default_tags"])[:30],
            "categoryId": cfg["channel"]["category_id"],
            "defaultLanguage": "en", "defaultAudioLanguage": "en",
        },
        "status": {
            "privacyStatus": "private",
            "publishAt": publish_at,
            "selfDeclaredMadeForKids": bool(cfg["channel"]["made_for_kids"]),
            "embeddable": True,
            "license": "youtube",
            "containsSyntheticMedia": bool(meta.get("synthetic_media", False)),  # AI narration + simulated events: disclosed per episode
        },
        # always answer YouTube's "Paid promotion" question: No, unless the episode really has a sponsor
        "paidProductPlacementDetails": {"hasPaidProductPlacement": bool(meta.get("paid_promotion", False))},
    }
    if dry_run:
        print(json.dumps(body, indent=1))
        return meta
    api = yt()
    req = api.videos().insert(part="snippet,status,paidProductPlacementDetails", body=body,
                              media_body=MediaFileUpload(str(video), chunksize=16 * 1024 * 1024, resumable=True))
    resp = None
    while resp is None:
        status, resp = req.next_chunk()
        if status:
            print(f"upload {int(status.progress() * 100)}%")
    vid = resp["id"]
    meta.update(youtube_id=vid, publish_at=publish_at, url=f"https://youtu.be/{vid}",
                uploaded_at=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"))
    try:  # length of the appended end slate, so marathons can trim it (studio/compile.py)
        tm = json.loads((ep_dir / "build" / "timing.json").read_text(encoding="utf-8"))["shots"]
        meta["end_slate_s"] = next((x["duration"] for x in tm if x["id"] == "endslate"), 0)
    except Exception:
        pass
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    warnings = []
    try:
        if thumb.exists():
            api.thumbnails().set(videoId=vid, media_body=MediaFileUpload(str(thumb))).execute()
    except Exception as e:
        warnings.append(f"thumbnail not set ({e}); is the channel phone-verified?")
    try:
        if srt.exists():
            api.captions().insert(part="snippet", body={"snippet": {"videoId": vid, "language": "en",
                                                                     "name": "English", "isDraft": False}},
                                  media_body=MediaFileUpload(str(srt), mimetype="application/octet-stream")).execute()
    except Exception as e:
        warnings.append(f"captions not uploaded ({e})")
    if meta.get("playlist"):
        import time
        for attempt in range(4):  # YouTube sometimes answers 409 SERVICE_UNAVAILABLE right after an upload
            try:
                add_to_playlist(api, vid, meta["playlist"])
                break
            except Exception as e:
                if attempt == 3:
                    warnings.append(f"playlist add failed ({e})")
                time.sleep(10 * (attempt + 1))
    # Unverified API projects force uploads to stay private: detect and warn.
    got = api.videos().list(part="status", id=vid).execute()["items"][0]["status"]
    if not got.get("publishAt"):
        warnings.append("YouTube did not keep the publishAt schedule. The Google Cloud project is probably "
                        "unaudited (uploads locked private). Schedule it manually in Studio, and apply for the "
                        "YouTube API audit (see README).")
    meta["upload_warnings"] = warnings
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    return meta


def add_to_playlist(api, video_id: str, key_or_title: str):
    title = load_config()["youtube"]["playlists"].get(key_or_title, key_or_title)
    pl_id = None
    page = None
    while True:
        r = api.playlists().list(part="snippet", mine=True, maxResults=50, pageToken=page).execute()
        for p in r.get("items", []):
            if p["snippet"]["title"] == title:
                pl_id = p["id"]
        page = r.get("nextPageToken")
        if pl_id or not page:
            break
    if not pl_id:
        pl_id = api.playlists().insert(part="snippet,status", body={
            "snippet": {"title": title}, "status": {"privacyStatus": "public"}}).execute()["id"]
    api.playlistItems().insert(part="snippet", body={"snippet": {
        "playlistId": pl_id, "resourceId": {"kind": "youtube#video", "videoId": video_id}}}).execute()


def set_channel_branding(description: str | None = None, keywords: str | None = None, banner: Path | None = None):
    from googleapiclient.http import MediaFileUpload
    api = yt()
    ch = api.channels().list(part="brandingSettings", mine=True).execute()["items"][0]
    bs = ch["brandingSettings"]
    if description:
        bs.setdefault("channel", {})["description"] = description
    if keywords:
        bs.setdefault("channel", {})["keywords"] = keywords
    if banner:
        url = api.channelBanners().insert(media_body=MediaFileUpload(str(banner))).execute()["url"]
        bs.setdefault("image", {})["bannerExternalUrl"] = url
    api.channels().update(part="brandingSettings", body={"id": ch["id"], "brandingSettings": bs}).execute()
    print("Channel branding updated. (Profile picture must be set by hand in YouTube Studio: the API can't.)")


# ------------------------------------------------------------------ analytics


def pull_analytics(days: int = 28) -> Path:
    api, an = yt(), yta()
    today = dt.date.today()
    start = (today - dt.timedelta(days=days)).isoformat()
    ch = api.channels().list(part="snippet,statistics", mine=True).execute()["items"][0]
    out = {"date": today.isoformat(), "channel": ch["statistics"], "videos": [], "errors": []}

    def q(**kw):
        try:
            return an.reports().query(ids="channel==MINE", startDate=start, endDate=today.isoformat(), **kw).execute()
        except Exception as e:  # metric not available for this channel / scope
            out["errors"].append(f"{kw.get('metrics')}: {e}")
            return None

    r = q(metrics="views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,subscribersGained,likes,comments,shares",
          dimensions="video", sort="-views", maxResults=50)
    cols = [c["name"] for c in (r or {}).get("columnHeaders", [])]
    for row in (r or {}).get("rows", []):
        out["videos"].append(dict(zip(cols, row)))
    ids = [v["video"] for v in out["videos"]]
    if ids:
        info = api.videos().list(part="snippet,statistics,contentDetails", id=",".join(ids[:50])).execute()
        titles = {i["id"]: {"title": i["snippet"]["title"], "published": i["snippet"]["publishedAt"],
                            "lifetime_views": int(i["statistics"].get("viewCount", 0))} for i in info["items"]}
        for v in out["videos"]:
            v.update(titles.get(v["video"], {}))
        for v in out["videos"][:10]:
            rr = q(metrics="audienceWatchRatio,relativeRetentionPerformance", dimensions="elapsedVideoTimeRatio",
                   filters=f"video=={v['video']}")
            if rr and rr.get("rows"):
                v["retention_curve"] = [[round(a, 2), round(b, 3), round(c, 3)] for a, b, c in rr["rows"][::5]]
    for name, kw in {
        "traffic_sources": dict(metrics="views,estimatedMinutesWatched", dimensions="insightTrafficSourceType", sort="-views"),
        "countries": dict(metrics="views", dimensions="country", sort="-views", maxResults=15),
        "revenue": dict(metrics="estimatedRevenue,playbackBasedCpm,monetizedPlaybacks"),
    }.items():
        rr = q(**kw)
        if rr:
            out[name] = {"columns": [c["name"] for c in rr.get("columnHeaders", [])], "rows": rr.get("rows", [])}
    try:  # thumbnail impressions + CTR come from the Reporting API (not available in the Analytics API)
        out["reach"] = pull_reach()
    except Exception as e:
        out["errors"].append(f"reach report: {e}")
    path = ROOT / "data" / "analytics" / f"{today.isoformat()}.json"
    path.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    return path


def pull_reach() -> dict:
    """Thumbnail impressions + click-through rate per video. The Analytics API doesn't expose these; the bulk
    Reporting API does (report type channel_reach_basic_a1, one CSV per day, first files ~48 h after the job is
    created). Downloads new daily files into data/reach/ and returns per-video totals."""
    import csv
    import io
    from google.auth.transport.requests import AuthorizedSession
    from googleapiclient.discovery import build
    creds = credentials()
    rep = build("youtubereporting", "v1", credentials=creds, cache_discovery=False)
    jobs = rep.jobs().list().execute().get("jobs", [])
    job = next((j for j in jobs if j["reportTypeId"] == "channel_reach_basic_a1"), None)
    if not job:
        job = rep.jobs().create(body={"reportTypeId": "channel_reach_basic_a1", "name": "doomsday-map-reach"}).execute()
    folder = ROOT / "data" / "reach"
    folder.mkdir(parents=True, exist_ok=True)
    have = {p.stem for p in folder.glob("*.csv")}
    session = AuthorizedSession(creds)
    page = None
    while True:
        r = rep.jobs().reports().list(jobId=job["id"], pageToken=page).execute()
        for report in r.get("reports", []):
            day = report["startTime"][:10]
            if day not in have:
                (folder / f"{day}.csv").write_bytes(session.get(report["downloadUrl"]).content)
                have.add(day)
        page = r.get("nextPageToken")
        if not page:
            break
    totals: dict = {}
    for f in sorted(folder.glob("*.csv")):
        for row in csv.DictReader(io.StringIO(f.read_text(encoding="utf-8"))):
            v = totals.setdefault(row.get("video_id", "?"), {"impressions": 0, "clicks": 0.0})
            imp = int(float(row.get("video_thumbnail_impressions") or 0))
            v["impressions"] += imp
            v["clicks"] += imp * float(row.get("video_thumbnail_impressions_ctr") or 0)
    for v in totals.values():
        v["ctr"] = round(v["clicks"] / v["impressions"], 4) if v["impressions"] else None
        v["clicks"] = round(v["clicks"])
    return {"job": job["id"], "days": len(have), "videos": totals}


def pull_competitors() -> Path:
    api = yt()
    cfg = load_config()
    today = dt.date.today()
    now = dt.datetime.now(dt.timezone.utc)
    stamp = now.replace(microsecond=0).isoformat().replace("+00:00", "Z")
    res = {"date": today.isoformat(), "at": stamp, "channels": []}
    # previous snapshot (most recent earlier file) -> per-video views at that time, for views/hour right now
    prev = {}
    snaps = sorted((ROOT / "data" / "competitors").glob("*.json"))
    older = [s for s in snaps if s.stem < today.isoformat()]
    if older:
        pj = json.loads(older[-1].read_text(encoding="utf-8"))
        at = pj.get("at") or (pj["date"] + "T12:00:00Z")
        for c in pj.get("channels", []):
            for v in c.get("videos", []):
                prev[v["id"]] = {"views": v["views"], "at": at}
    for handle in cfg["competitors"]:
        try:
            ch = api.channels().list(part="snippet,statistics,contentDetails", forHandle=handle).execute().get("items")
            if not ch:
                res["channels"].append({"handle": handle, "error": "not found"})
                continue
            ch = ch[0]
            uploads = ch["contentDetails"]["relatedPlaylists"]["uploads"]
            items = api.playlistItems().list(part="contentDetails", playlistId=uploads, maxResults=50).execute()["items"]
            ids = [i["contentDetails"]["videoId"] for i in items]
            vids = api.videos().list(part="snippet,statistics,contentDetails", id=",".join(ids)).execute()["items"]
            rows = []
            for v in vids:
                dur = _iso_dur(v["contentDetails"]["duration"])
                rows.append({"id": v["id"], "title": v["snippet"]["title"], "published": v["snippet"]["publishedAt"],
                             "views": int(v["statistics"].get("viewCount", 0)), "seconds": dur,
                             "short": dur <= 180})
            longs = [r for r in rows if not r["short"]]
            med = statistics.median([r["views"] for r in longs]) if longs else 0
            for r in rows:
                r["outlier_x"] = round(r["views"] / med, 2) if med else None
                age_h = max(1.0, (now - _parse_utc(r["published"])).total_seconds() / 3600)
                r["age_days"] = round(age_h / 24, 1)
                r["vph_lifetime"] = round(r["views"] / age_h, 1)  # average views/hour since upload
                p = prev.get(r["id"])
                if p:  # views/hour RIGHT NOW: growth since the previous snapshot
                    dh = (now - _parse_utc(p["at"])).total_seconds() / 3600
                    if dh >= 1:
                        r["vph_recent"] = round((r["views"] - p["views"]) / dh, 1)
            res["channels"].append({"handle": handle, "title": ch["snippet"]["title"],
                                    "subs": ch["statistics"].get("subscriberCount"),
                                    "median_long_views_last50": med,
                                    "videos": sorted(rows, key=lambda r: r["published"], reverse=True)})
        except Exception as e:
            res["channels"].append({"handle": handle, "error": str(e)})
    path = ROOT / "data" / "competitors" / f"{today.isoformat()}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    for old in snaps:  # keep 60 days of daily snapshots
        if old.stem < (today - dt.timedelta(days=60)).isoformat():
            old.unlink()
    return path


def _iso_dur(s: str) -> int:
    import re
    m = re.match(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", s)
    d, h, mi, se = (int(x) if x else 0 for x in m.groups())
    return d * 86400 + h * 3600 + mi * 60 + se


# ------------------------------------------------------------------ shorts and thumbnails


def set_thumbnail(ep_dir: Path) -> str:
    from googleapiclient.http import MediaFileUpload
    meta = json.loads((ep_dir / "metadata.json").read_text(encoding="utf-8"))
    yt().thumbnails().set(videoId=meta["youtube_id"], media_body=MediaFileUpload(str(ep_dir / "build" / "thumbnail.png"))).execute()
    return meta["youtube_id"]


def upload_short(ep_dir: Path, spec: dict, video: Path, publish_at: str, captions_srt: str | None = None) -> dict:
    """Upload one Short private with publishAt; its description links the episode it was cut from.
    (YouTube's Shorts 'related video' link has no API: set it in Studio.)"""
    from googleapiclient.http import MediaFileUpload
    cfg = load_config()
    ep_meta = json.loads((ep_dir / "metadata.json").read_text(encoding="utf-8"))
    long_url = ep_meta["url"]
    desc = (f"{spec['hook']}\n\nWatch the full simulation: {long_url}\n\n"
            f"{cfg['channel']['disclosure']}\n\n#shorts #nuclearwar #simulation")
    body = {
        "snippet": {"title": spec["yt_title"][:100], "description": desc,
                    "tags": (ep_meta.get("tags") or cfg["channel"]["default_tags"])[:20] + ["shorts"],
                    "categoryId": cfg["channel"]["category_id"], "defaultLanguage": "en", "defaultAudioLanguage": "en"},
        "status": {"privacyStatus": "private", "publishAt": publish_at, "embeddable": True, "license": "youtube",
                   "selfDeclaredMadeForKids": bool(cfg["channel"]["made_for_kids"]),
                   "containsSyntheticMedia": bool(ep_meta.get("synthetic_media", False))},
        "paidProductPlacementDetails": {"hasPaidProductPlacement": False},
    }
    api = yt()
    req = api.videos().insert(part="snippet,status,paidProductPlacementDetails", body=body,
                              media_body=MediaFileUpload(str(video), chunksize=16 * 1024 * 1024, resumable=True))
    resp = None
    while resp is None:
        _, resp = req.next_chunk()
    vid = resp["id"]
    out = {"id": spec["id"], "youtube_id": vid, "url": f"https://youtube.com/shorts/{vid}", "publish_at": publish_at,
           "title": spec["yt_title"], "warnings": []}
    if captions_srt:
        try:
            from googleapiclient.http import MediaInMemoryUpload
            api.captions().insert(part="snippet", body={"snippet": {"videoId": vid, "language": "en", "name": "English", "isDraft": False}},
                                  media_body=MediaInMemoryUpload(captions_srt.encode("utf-8"), mimetype="application/octet-stream")).execute()
        except Exception as e:
            out["warnings"].append(f"captions: {e}")
    try:
        add_to_playlist(api, vid, "shorts")
    except Exception as e:
        out["warnings"].append(f"playlist: {e}")
    got = api.videos().list(part="status", id=vid).execute()["items"][0]["status"]
    if not got.get("publishAt"):
        out["warnings"].append("publishAt not kept")
    return out
