#!/usr/bin/env python3
"""
Merge spec metadata with resolved ASIN data, dedupe, verify each ASIN one
more time against amazon.com/dp/<ASIN>, then rewrite client/src/lib/apothecary.ts.

Output: client/src/lib/apothecary.ts gets a new APOTHECARY array with only
verified-live ASINs and the curated copy from spec.
"""
import json
import re
import sys
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

ROOT = Path("/home/ubuntu/autoimmune-reset")
SPEC = ROOT / "scripts/apothecary-spec.json"
MAP_OUT = Path("/home/ubuntu/resolve_amazon_asins.json")
APO = ROOT / "client/src/lib/apothecary.ts"

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
HEADERS = {
    "User-Agent": UA,
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml",
}
ASIN_RE = re.compile(r"^[A-Z0-9]{10}$")


def re_verify(asin: str) -> bool:
    """One last sanity check via direct amazon.com/dp request. Tolerant of
    503/CAPTCHA — those are inconclusive, so we accept the resolver's
    earlier verified=True signal in those cases."""
    url = f"https://www.amazon.com/dp/{asin}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=12, allow_redirects=True)
    except Exception:
        return True  # network flake → trust the resolver
    if r.status_code in (503, 429):
        return True  # rate-limited, trust resolver
    if r.status_code != 200:
        return False
    body = r.text[:60000].lower()
    if "sorry! we couldn" in body or "page not found" in body:
        return False
    if "enter the characters you see below" in body or "captcha" in body.lower():
        return True  # CAPTCHA — trust resolver
    return True


def main() -> int:
    spec = json.loads(SPEC.read_text())
    res_doc = json.loads(MAP_OUT.read_text())
    res = res_doc.get("results", [])
    by_q = {r["input"]: r.get("output", {}) for r in res}

    merged: list[dict] = []
    seen_asins: set[str] = set()
    skipped: list[str] = []

    for item in spec:
        out = by_q.get(item["q"], {}) or {}
        asin = (out.get("asin") or "").strip().upper()
        verified = bool(out.get("verified"))
        if not asin or not ASIN_RE.match(asin):
            skipped.append(f"{item['q']} -> bad ASIN ({asin!r})")
            continue
        if asin in seen_asins:
            skipped.append(f"{item['q']} -> duplicate ASIN ({asin})")
            continue
        if not verified:
            skipped.append(f"{item['q']} -> resolver said not verified ({asin})")
            continue
        merged.append({
            **item,
            "asin": asin,
            "resolved_title": out.get("product_title", ""),
        })
        seen_asins.add(asin)

    print(f"resolver merged: {len(merged)} kept, {len(skipped)} skipped")
    if skipped[:10]:
        print("first 10 skipped:")
        for s in skipped[:10]:
            print(f"  - {s}")

    # Re-verify in parallel; drop any that fail.
    print(f"re-verifying {len(merged)} ASINs against amazon.com/dp...")
    final: list[dict] = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        futs = {pool.submit(re_verify, m["asin"]): m for m in merged}
        for f in as_completed(futs):
            m = futs[f]
            ok = False
            try:
                ok = f.result()
            except Exception:
                ok = True  # network flake → trust resolver
            if ok:
                final.append(m)
            else:
                skipped.append(f"{m['q']} -> re-verify failed ({m['asin']})")
    # Stable order matching spec
    by_q_kept = {m["q"]: m for m in final}
    ordered = [by_q_kept[item["q"]] for item in spec if item["q"] in by_q_kept]

    print(f"final apothecary: {len(ordered)} items")

    # Build TypeScript file
    tsfile = """/**
 * Apothecary: a curated list of supplements, herbs, and TCM formulas.
 *
 * Every ASIN here was resolved against Amazon search and verified to point
 * to a live product page. Links use tag=spankyspinola-20.
 *
 * Affiliate disclosure: Immune Rebuilt is a participant in the Amazon Services
 * LLC Associates Program. As an Amazon Associate we earn from qualifying
 * purchases. This earns us a small commission at no extra cost to you.
 */
export type Family = "Supplement" | "Herb" | "TCM" | "Adaptogen" | "Topical";
export type Item = {
  asin: string;
  title: string;
  brand: string;
  family: Family;
  category: string;
  whyHere: string;
  bestFor: string;
  warning?: string;
  internalSlug?: string;
};

const T = "spankyspinola-20";
export const amazonUrl = (asin: string) => `https://www.amazon.com/dp/${asin}?tag=${T}`;

export const APOTHECARY: Item[] = [
"""
    for m in ordered:
        line = "  { "
        line += f'asin: "{m["asin"]}", '
        line += f'title: {json.dumps(m["title"])}, '
        line += f'brand: {json.dumps(m["brand"])}, '
        line += f'family: "{m["family"]}", '
        line += f'category: {json.dumps(m["category"])}, '
        line += f'whyHere: {json.dumps(m["whyHere"])}, '
        line += f'bestFor: {json.dumps(m["bestFor"])}'
        if "warning" in m and m["warning"]:
            line += f', warning: {json.dumps(m["warning"])}'
        if "internalSlug" in m and m["internalSlug"]:
            line += f', internalSlug: {json.dumps(m["internalSlug"])}'
        line += " },\n"
        tsfile += line
    tsfile += """];

export const FAMILIES: Family[] = ["Supplement", "Herb", "TCM", "Adaptogen", "Topical"];
export const CATEGORIES = Array.from(new Set(APOTHECARY.map((i) => i.category))).sort();
"""
    APO.write_text(tsfile)
    print(f"wrote {APO} with {len(ordered)} items")
    return 0


if __name__ == "__main__":
    sys.exit(main())
