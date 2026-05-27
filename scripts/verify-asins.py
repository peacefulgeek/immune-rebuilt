#!/usr/bin/env python3
"""
Verify every ASIN in client/src/lib/apothecary.ts against Amazon.

For each ASIN we try https://www.amazon.com/dp/<ASIN> with a normal browser
User-Agent. We accept the ASIN as live if the response is 200 AND the page
does not contain the classic Amazon "dogs of Amazon" 404 strings nor the
"currently unavailable" / "page not found" markers.

Three attempts per ASIN with backoff. Output: a JSON report listing live,
dead, and uncertain ASINs so we can decide what to keep, swap, or remove.
"""
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

APO = Path("/home/ubuntu/autoimmune-reset/client/src/lib/apothecary.ts")
OUT = Path("/home/ubuntu/autoimmune-reset/.asin-report.json")

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

# Strings that mean "this ASIN no longer points to a live product".
DEAD_MARKERS = [
    "Sorry! We couldn",  # "Sorry! We couldn't find that page"
    "Looking for something",
    "dogs-of-amazon",
    "Page Not Found",
    "currently unavailable",
]


def extract_asins() -> list[tuple[str, str]]:
    """Returns [(asin, short label) ...] from apothecary.ts"""
    src = APO.read_text()
    pat = re.compile(r'\{\s*asin:\s*"([A-Z0-9]{10})",\s*title:\s*"([^"]+)"')
    return [(m.group(1), m.group(2)) for m in pat.finditer(src)]


def verify(asin: str) -> tuple[str, str, int]:
    """returns (asin, status, http_code)
       status in {live, dead, uncertain}"""
    url = f"https://www.amazon.com/dp/{asin}"
    last_code = 0
    for attempt in range(3):
        try:
            r = requests.get(
                url,
                headers={
                    "User-Agent": UA,
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept": "text/html,application/xhtml+xml",
                },
                timeout=15,
                allow_redirects=True,
            )
            last_code = r.status_code
            if r.status_code == 200:
                body = r.text[:50000]
                # Heuristic: if any dead-marker phrase is present AND no buy box, consider dead
                if any(m.lower() in body.lower() for m in DEAD_MARKERS):
                    # one more chance — Amazon throws CAPTCHA pages too
                    if "Enter the characters you see below" in body or "captcha" in body.lower():
                        time.sleep(0.8 * (attempt + 1))
                        continue
                    return asin, "dead", 200
                if asin in body or "buybox" in body.lower() or "add to cart" in body.lower() or "out of stock" in body.lower():
                    return asin, "live", 200
                # 200 but ambiguous — try again
                time.sleep(0.8 * (attempt + 1))
                continue
            elif r.status_code in (404, 410):
                return asin, "dead", r.status_code
            elif r.status_code in (503, 429):
                # rate limited — back off and retry
                time.sleep(1.5 * (attempt + 1))
                continue
            else:
                time.sleep(0.8 * (attempt + 1))
        except Exception:
            time.sleep(0.8 * (attempt + 1))
    return asin, "uncertain", last_code


def main() -> int:
    asins = extract_asins()
    print(f"verifying {len(asins)} ASINs (3 attempts each, concurrency=8)", flush=True)
    results: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=8) as pool:
        futs = {pool.submit(verify, a): (a, t) for a, t in asins}
        done = 0
        for f in as_completed(futs):
            asin, t = futs[f]
            res = f.result()
            results[asin] = {"title": t, "status": res[1], "http": res[2]}
            done += 1
            if done % 5 == 0 or done == len(asins):
                live = sum(1 for v in results.values() if v["status"] == "live")
                dead = sum(1 for v in results.values() if v["status"] == "dead")
                unc = sum(1 for v in results.values() if v["status"] == "uncertain")
                print(f"  [{done}/{len(asins)}] live={live} dead={dead} uncertain={unc}", flush=True)
    OUT.write_text(json.dumps(results, indent=2))
    live = [a for a, v in results.items() if v["status"] == "live"]
    dead = [a for a, v in results.items() if v["status"] == "dead"]
    unc = [a for a, v in results.items() if v["status"] == "uncertain"]
    print()
    print(f"final: live={len(live)} dead={len(dead)} uncertain={len(unc)}")
    if dead:
        print("DEAD ASINs:")
        for a in dead:
            print(f"  {a} — {results[a]['title']}")
    if unc:
        print("UNCERTAIN ASINs:")
        for a in unc:
            print(f"  {a} — {results[a]['title']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
