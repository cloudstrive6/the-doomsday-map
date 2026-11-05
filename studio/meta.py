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
