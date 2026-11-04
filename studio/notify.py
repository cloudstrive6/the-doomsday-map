"""Telegram notifications (optional). Env: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID."""
from __future__ import annotations

import json
import os
import urllib.request
import uuid
from pathlib import Path


def send(text: str, photo: Path | None = None) -> bool:
    from .config import load_dotenv
    load_dotenv()
    token, chat = os.environ.get("TELEGRAM_BOT_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat:
        print(("[notify] Telegram not configured; message was:\n" + text).encode("ascii", "replace").decode())
        return False
    base = f"https://api.telegram.org/bot{token}"
    if photo and Path(photo).exists():
        boundary = uuid.uuid4().hex
        parts = []
        for k, v in (("chat_id", chat), ("caption", text[:1024])):
            parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="photo"; filename="t.png"\r\n'
                     f"Content-Type: image/png\r\n\r\n".encode() + Path(photo).read_bytes() + b"\r\n")
        parts.append(f"--{boundary}--\r\n".encode())
        req = urllib.request.Request(f"{base}/sendPhoto", data=b"".join(parts),
                                     headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    else:
        req = urllib.request.Request(f"{base}/sendMessage",
                                     data=json.dumps({"chat_id": chat, "text": text[:4000],
                                                      "disable_web_page_preview": True}).encode(),
                                     headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=30).read()
        return True
    except Exception as e:
        print(f"[notify] failed: {e}")
        return False
