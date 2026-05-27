#!/usr/bin/env python3
"""
Parallel TL;DR stripper for Bunny-hosted article JSONs.
Removes the <div class="tldr">...</div> block, any leftover <strong>TL;DR.</strong>
prefix, and bare "TL;DR." sentences from every article body, then re-uploads
the cleaned JSON to Bunny storage.

Idempotent — running again is a no-op once stripped. Tolerates network
flakiness via a small retry loop and a 15s timeout per request.
"""
import json
import re
import sys
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

ROOT = Path("/home/ubuntu/autoimmune-reset")
PULL = "https://conscious-elder.b-cdn.net/immune-rebuilt/articles"
PUT_BASE = "https://ny.storage.bunnycdn.com/conscious-elder/immune-rebuilt/articles"
ACCESS_KEY = "f6dbc11c-20dc-4c15-a39faabe3d28-a766-4a87"

RE_TLDR_DIV = re.compile(
    r'<div\s+class=["\']tldr["\']>.*?</div>\s*',
    re.IGNORECASE | re.DOTALL,
)
RE_TLDR_P = re.compile(
    r'<p[^>]*>\s*<strong>\s*TL[;:]?DR\.?\s*</strong>.*?</p>\s*',
    re.IGNORECASE | re.DOTALL,
)
RE_TLDR_INLINE_STRONG = re.compile(r'<strong>\s*TL[;:]?DR\.?\s*</strong>\s*', re.IGNORECASE)
RE_TLDR_BARE = re.compile(r'(?<![A-Za-z])TL[;:]?DR[\.\s:]+', re.IGNORECASE)


def clean_body(body: str) -> str:
    if not body:
        return body
    out = RE_TLDR_DIV.sub("", body)
    out = RE_TLDR_P.sub("", out)
    out = RE_TLDR_INLINE_STRONG.sub("", out)
    out = RE_TLDR_BARE.sub("", out)
    out = re.sub(r"\n{3,}", "\n\n", out)
    return out.lstrip()


def load_slugs() -> list[str]:
    slugs: list[str] = []
    seen: set[str] = set()
    for p in [
        ROOT / "client/public/content/preview-manifest.json",
        ROOT / "client/public/content/queue-manifest.json",
    ]:
        if not p.exists():
            continue
        j = json.loads(p.read_text())
        items = j.get("articles") or j.get("items") or []
        for a in items:
            s = a.get("slug")
            if s and s not in seen:
                slugs.append(s)
                seen.add(s)
    return slugs


SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "tldr-strip/2.0", "Connection": "keep-alive"})


def process_one(slug: str) -> tuple[str, str, int]:
    """returns (slug, status, bytes_removed)"""
    url = f"{PULL}/{slug}.json"
    last_err = ""
    for attempt in range(3):
        try:
            r = SESSION.get(url, timeout=15)
            if r.status_code == 404:
                return slug, "missing-on-bunny", 0
            r.raise_for_status()
            a = r.json()
            break
        except Exception as e:
            last_err = str(e)[:80]
            time.sleep(0.5 * (attempt + 1))
    else:
        return slug, f"fetch-fail:{last_err}", 0

    body = a.get("body", "")
    new_body = clean_body(body)
    if new_body == body:
        return slug, "noop", 0

    a["body"] = new_body
    payload = json.dumps(a, ensure_ascii=False).encode("utf-8")
    last_err = ""
    for attempt in range(3):
        try:
            r = SESSION.put(
                f"{PUT_BASE}/{slug}.json",
                data=payload,
                headers={"AccessKey": ACCESS_KEY, "Content-Type": "application/json"},
                timeout=20,
            )
            if r.status_code in (200, 201):
                return slug, "updated", len(body) - len(new_body)
            last_err = f"http-{r.status_code}"
        except Exception as e:
            last_err = str(e)[:80]
        time.sleep(0.5 * (attempt + 1))
    return slug, f"put-fail:{last_err}", 0


def main() -> int:
    slugs = load_slugs()
    print(f"slugs: {len(slugs)} | concurrency: 12", flush=True)
    if not slugs:
        return 0

    counts = {"updated": 0, "noop": 0, "fail": 0}
    failed: list[str] = []

    started = time.monotonic()
    with ThreadPoolExecutor(max_workers=12) as pool:
        futs = {pool.submit(process_one, s): s for s in slugs}
        done = 0
        for f in as_completed(futs):
            slug, status, _bytes = f.result()
            done += 1
            if status == "updated":
                counts["updated"] += 1
            elif status == "noop":
                counts["noop"] += 1
            else:
                counts["fail"] += 1
                failed.append(f"{slug}:{status}")
            if done % 25 == 0 or done == len(slugs):
                elapsed = time.monotonic() - started
                print(
                    f"  [{done}/{len(slugs)}] updated={counts['updated']} "
                    f"noop={counts['noop']} fail={counts['fail']} t={elapsed:.0f}s",
                    flush=True,
                )

    print()
    print("done.", counts)
    if failed:
        print("first 10 failures:", failed[:10])
    return 0 if counts["fail"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
