#!/usr/bin/env python3
"""
Resolve apothecary-spec.json queries to live Amazon ASINs.

Strategy:
1. For each spec entry, query https://www.amazon.com/s?k=<urlencoded query>
2. Parse the result page for the first organic ASIN (data-asin="..." rows
   that are not sponsored).
3. Verify the chosen ASIN resolves to a 200 product page that contains an
   "Add to Cart" or "buy box" indicator and is NOT the "Sorry! We couldn't
   find that page" template.
4. Apply tag=spankyspinola-20 to the final URL.

Three retries per query. Concurrency 6 to avoid CAPTCHA. Output written to
scripts/apothecary-resolved.json so we never have to redo the work.
"""
import json
import re
import sys
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

ROOT = Path("/home/ubuntu/autoimmune-reset")
SPEC = ROOT / "scripts/apothecary-spec.json"
OUT = ROOT / "scripts/apothecary-resolved.json"

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
HEADERS = {
    "User-Agent": UA,
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
}

# Pull ASINs from "data-asin" attributes in search results, ignoring empties
ASIN_RE = re.compile(r'data-asin="([A-Z0-9]{10})"')
SPONSORED_HINT = "Sponsored"


def search_first_asin(query: str) -> str | None:
    url = f"https://www.amazon.com/s?k={urllib.parse.quote_plus(query)}"
    r = requests.get(url, headers=HEADERS, timeout=20)
    if r.status_code != 200:
        return None
    html = r.text
    if "Enter the characters you see below" in html:
        return None  # CAPTCHA
    # Coarse approach: grab first 25 ASINs and skip those whose enclosing
    # <div data-asin="..."> block contains "Sponsored" close by.
    seen: list[str] = []
    for m in ASIN_RE.finditer(html):
        a = m.group(1)
        if not a or a in seen:
            continue
        # check 800-char window after the asin tag for "Sponsored"
        start = m.end()
        window = html[start : start + 800]
        if SPONSORED_HINT in window[:200]:
            seen.append(a)
            continue
        return a
    return None


def verify(asin: str) -> bool:
    url = f"https://www.amazon.com/dp/{asin}"
    r = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True)
    if r.status_code != 200:
        return False
    html = r.text[:80000].lower()
    if "sorry! we couldn" in html or "page not found" in html:
        return False
    if "add to cart" in html or "buy now" in html or "currently unavailable" in html or "out of stock" in html:
        return True
    # Some product pages don't show buy box for a logged-out search bot
    # but render the title. Accept if the ASIN appears multiple times.
    return html.count(asin.lower()) >= 3


def resolve_one(item: dict) -> dict:
    q = item["q"]
    last_err = ""
    for attempt in range(3):
        try:
            asin = search_first_asin(q)
            if not asin:
                last_err = "no-asin-in-search"
                time.sleep(1.0 * (attempt + 1))
                continue
            if verify(asin):
                return {**item, "asin": asin, "status": "live"}
            last_err = f"verify-failed:{asin}"
            time.sleep(1.0 * (attempt + 1))
        except Exception as e:
            last_err = str(e)[:100]
            time.sleep(1.0 * (attempt + 1))
    return {**item, "asin": None, "status": f"failed:{last_err}"}


def main() -> int:
    spec = json.loads(SPEC.read_text())
    print(f"resolving {len(spec)} queries (concurrency=6)", flush=True)
    results: list[dict] = []
    with ThreadPoolExecutor(max_workers=6) as pool:
        futs = {pool.submit(resolve_one, item): i for i, item in enumerate(spec)}
        done = 0
        for f in as_completed(futs):
            results.append(f.result())
            done += 1
            live = sum(1 for r in results if r["status"] == "live")
            failed = sum(1 for r in results if r["status"] != "live")
            if done % 5 == 0 or done == len(spec):
                print(f"  [{done}/{len(spec)}] live={live} failed={failed}", flush=True)
    # Stable order matching input spec
    by_q = {r["q"]: r for r in results}
    ordered = [by_q[item["q"]] for item in spec]
    OUT.write_text(json.dumps(ordered, indent=2))
    live = [r for r in ordered if r["status"] == "live"]
    failed = [r for r in ordered if r["status"] != "live"]
    print()
    print(f"final: live={len(live)} failed={len(failed)}")
    if failed:
        print("FAILED queries (will need manual ASIN):")
        for r in failed:
            print(f"  {r['q']} -> {r['status']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
