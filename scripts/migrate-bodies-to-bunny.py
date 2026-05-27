#!/usr/bin/env python3
"""Migrate every article body from the in-repo manifests up to Bunny CDN as JSON.

For each article:
  1. Build a per-slug JSON file with the full record (slug, title, body, etc.).
  2. Upload it to Bunny at  /immune-rebuilt/articles/<slug>.json
  3. Rewrite the manifests so each entry keeps only metadata + body_url; the body
     field is dropped. The server fetches the body from Bunny on demand.

Idempotent — re-running just re-uploads + re-slims.
"""
import json
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "client" / "public" / "content"
LOCAL_DUMP = ROOT / ".bunny-articles"           # local mirror, gitignored
LOCAL_DUMP.mkdir(exist_ok=True)

BUNNY_STORAGE_HOST = "ny.storage.bunnycdn.com"
BUNNY_ZONE = "conscious-elder"
BUNNY_KEY = "f6dbc11c-20dc-4c15-a39faabe3d28-a766-4a87"
BUNNY_PULL = "https://conscious-elder.b-cdn.net"
REMOTE_PREFIX = "immune-rebuilt/articles"        # canonical path on Bunny

def upload(slug: str, payload: dict) -> str:
    """PUT the JSON to Bunny storage, return the public pull-zone URL."""
    body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
    remote = f"{REMOTE_PREFIX}/{slug}.json"
    url = f"https://{BUNNY_STORAGE_HOST}/{BUNNY_ZONE}/{remote}"
    req = urllib.request.Request(url, method="PUT", data=body, headers={
        "AccessKey": BUNNY_KEY,
        "Content-Type": "application/json",
    })
    last_err = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                if 200 <= r.status < 300:
                    return f"{BUNNY_PULL}/{remote}"
                last_err = f"HTTP {r.status}"
        except urllib.error.HTTPError as e:
            last_err = f"HTTP {e.code} {e.reason}"
        except Exception as e:
            last_err = str(e)
        time.sleep(0.5 * (attempt + 1))
    raise RuntimeError(f"upload failed for {slug}: {last_err}")

def process_manifest(path: Path, status_default: str) -> dict:
    m = json.loads(path.read_text(encoding="utf-8"))
    arts = m.get("articles") or m.get("items") or []
    slimmed = []
    n = len(arts)
    print(f"[migrate] {path.name}: {n} articles", flush=True)
    for i, a in enumerate(arts, 1):
        slug = a["slug"]
        # Full record persisted on Bunny.
        full = {
            "slug": slug,
            "title": a.get("title"),
            "excerpt": a.get("excerpt"),
            "author": a.get("author") or "The Immune Rebuilt Editorial Team",
            "category": a.get("category"),
            "category_slug": a.get("category_slug"),
            "publish_at": a.get("publish_at") or a.get("published_at"),
            "status": a.get("status") or status_default,
            "hero_url": a.get("hero_url"),
            "hero_alt": a.get("hero_alt"),
            "word_count": a.get("word_count"),
            "asins": a.get("asins") or [],
            "related": a.get("related") or [],
            "body": a.get("body") or "",
        }
        # Local mirror for inspection / future re-uploads.
        (LOCAL_DUMP / f"{slug}.json").write_text(
            json.dumps(full, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        body_url = upload(slug, full)
        # Manifest entry now carries only metadata + body_url.
        slim = {k: v for k, v in full.items() if k != "body"}
        slim["body_url"] = body_url
        slimmed.append(slim)
        if i % 25 == 0 or i == n:
            print(f"  [{path.name}] {i}/{n} uploaded", flush=True)
    out = dict(m)
    if "articles" in m:
        out["articles"] = slimmed
    elif "items" in m:
        out["items"] = slimmed
    out["body_storage"] = {
        "kind": "bunny-cdn",
        "pull_zone": BUNNY_PULL,
        "prefix": f"/{REMOTE_PREFIX}/",
        "format": "json",
        "schema": "v1",
    }
    return out

def main():
    for fname, status in [
        ("preview-manifest.json", "published"),
        ("queue-manifest.json", "queued"),
    ]:
        path = CONTENT / fname
        if not path.exists():
            print(f"[migrate] {fname} missing, skipping", file=sys.stderr)
            continue
        out = process_manifest(path, status)
        path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
        size = path.stat().st_size
        print(f"[migrate] wrote slim {fname} — {size:,} bytes", flush=True)

if __name__ == "__main__":
    main()
