#!/usr/bin/env python3
"""
Article QA pass for the 100 published articles.

For each published article we:
1. Pull the JSON from Bunny.
2. Normalize the body:
   - collapse multi-blank lines
   - strip zero-width / weird unicode characters
   - normalize " "/" " into ASCII em-dashes
   - drop duplicate byline blocks (keep the first)
   - break any <p>...</p> longer than 90 words into shorter paragraphs at
     sentence boundaries
3. Count words inside the body (after stripping tags) and flag word counts
   outside the 1800-2500 band (we will not regenerate from this script,
   only flag for the report; the body content is already authored).
4. Track hero image URLs and report duplicates.
5. Re-upload the cleaned article JSON to Bunny only if it changed.
"""
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

ROOT = Path("/home/ubuntu/autoimmune-reset")
PULL = "https://conscious-elder.b-cdn.net/immune-rebuilt/articles"
PUT_BASE = "https://ny.storage.bunnycdn.com/conscious-elder/immune-rebuilt/articles"
ACCESS_KEY = "f6dbc11c-20dc-4c15-a39faabe3d28-a766-4a87"
PREVIEW = ROOT / "client/public/content/preview-manifest.json"
REPORT = ROOT / ".article-qa-report.json"

ZERO_WIDTH_RE = re.compile(r"[\u200b\u200c\u200d\u200e\u200f\ufeff]")
WEIRD_RE = re.compile(r"[\u2028\u2029\xa0]")
DOUBLE_SPACE_RE = re.compile(r"  +")
TAG_RE = re.compile(r"<[^>]+>")
PARA_RE = re.compile(r"<p\b[^>]*>(.*?)</p>", re.DOTALL | re.IGNORECASE)
BYLINE_RE = re.compile(r'<p\s+class="byline".*?</p>', re.DOTALL | re.IGNORECASE)
SENT_SPLIT_RE = re.compile(r"(?<=[\.\!\?])\s+(?=[A-Z])")

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "qa-articles/1.0", "Connection": "keep-alive"})


def load_published_slugs() -> list[dict]:
    j = json.loads(PREVIEW.read_text())
    return j.get("articles") or j.get("items") or []


def break_long_paragraphs(html: str) -> str:
    def replace(m: re.Match) -> str:
        attrs_match = re.match(r"<p\b([^>]*)>", m.group(0))
        attrs = attrs_match.group(1) if attrs_match else ""
        inner = m.group(1).strip()
        # ignore attributed paragraphs (byline, meta, etc.)
        if 'class="' in attrs:
            return m.group(0)
        text_only = TAG_RE.sub("", inner)
        if len(text_only.split()) <= 90:
            return m.group(0)
        # split inner into sentence-chunks
        sentences = SENT_SPLIT_RE.split(inner)
        if len(sentences) < 2:
            return m.group(0)
        # group sentences into ~3-sentence chunks
        chunks: list[str] = []
        cur: list[str] = []
        cur_words = 0
        for s in sentences:
            wc = len(TAG_RE.sub("", s).split())
            if cur and (cur_words + wc > 70 or len(cur) >= 4):
                chunks.append(" ".join(cur))
                cur, cur_words = [], 0
            cur.append(s)
            cur_words += wc
        if cur:
            chunks.append(" ".join(cur))
        return "\n".join(f"<p{attrs}>{c.strip()}</p>" for c in chunks)

    return PARA_RE.sub(replace, html)


def clean_body(body: str) -> str:
    if not body:
        return body
    out = body
    out = ZERO_WIDTH_RE.sub("", out)
    out = WEIRD_RE.sub(" ", out)
    out = out.replace("â€”", "—").replace("â€“", "–")
    out = out.replace("â€™", "'").replace("â€œ", "\u201c").replace("â€\x9d", "\u201d")
    # collapse repeated bylines: keep only the first byline paragraph
    bylines = BYLINE_RE.findall(out)
    if len(bylines) > 1:
        first = bylines[0]
        # drop the others
        out = BYLINE_RE.sub("", out)
        # re-insert first at the very top
        out = first + "\n\n" + out.lstrip()
    out = DOUBLE_SPACE_RE.sub(" ", out)
    out = re.sub(r"\n{3,}", "\n\n", out)
    out = break_long_paragraphs(out)
    return out.strip()


def word_count(html: str) -> int:
    text = TAG_RE.sub(" ", html or "")
    text = re.sub(r"\s+", " ", text).strip()
    return len(text.split())


def process_one(art: dict) -> dict:
    slug = art["slug"]
    url = f"{PULL}/{slug}.json"
    last_err = ""
    for attempt in range(3):
        try:
            r = SESSION.get(url, timeout=15)
            r.raise_for_status()
            j = r.json()
            break
        except Exception as e:
            last_err = str(e)[:80]
            time.sleep(0.5 * (attempt + 1))
    else:
        return {"slug": slug, "status": f"fetch-fail:{last_err}"}
    body = j.get("body", "")
    new_body = clean_body(body)
    wc = word_count(new_body)
    hero = j.get("hero_image_url") or j.get("hero") or ""

    changed = new_body != body
    if changed:
        j["body"] = new_body
        payload = json.dumps(j, ensure_ascii=False).encode("utf-8")
        for attempt in range(3):
            try:
                r = SESSION.put(
                    f"{PUT_BASE}/{slug}.json",
                    data=payload,
                    headers={"AccessKey": ACCESS_KEY, "Content-Type": "application/json"},
                    timeout=20,
                )
                if r.status_code in (200, 201):
                    break
            except Exception:
                time.sleep(0.5 * (attempt + 1))
        else:
            return {"slug": slug, "status": "put-fail", "wc": wc, "hero": hero}
    return {
        "slug": slug,
        "status": "updated" if changed else "noop",
        "wc": wc,
        "hero": hero,
    }


def main() -> int:
    published = load_published_slugs()
    print(f"qa pass over {len(published)} published articles", flush=True)

    results: list[dict] = []
    with ThreadPoolExecutor(max_workers=10) as pool:
        futs = {pool.submit(process_one, a): a for a in published}
        done = 0
        for f in as_completed(futs):
            r = f.result()
            results.append(r)
            done += 1
            if done % 25 == 0 or done == len(published):
                up = sum(1 for r in results if r.get("status") == "updated")
                noop = sum(1 for r in results if r.get("status") == "noop")
                fail = sum(1 for r in results if r.get("status", "").startswith(("fetch-fail", "put-fail")))
                print(f"  [{done}/{len(published)}] updated={up} noop={noop} fail={fail}", flush=True)

    # Stats: word count band
    in_band = [r for r in results if "wc" in r and 1800 <= r["wc"] <= 2500]
    too_short = [r for r in results if "wc" in r and r["wc"] < 1800]
    too_long = [r for r in results if "wc" in r and r["wc"] > 2500]
    print(f"\nword count: in-band={len(in_band)} short={len(too_short)} long={len(too_long)}")
    if too_short[:10]:
        print("first 10 too-short:")
        for r in too_short[:10]:
            print(f"  {r['slug']}: {r['wc']} words")
    if too_long[:10]:
        print("first 10 too-long:")
        for r in too_long[:10]:
            print(f"  {r['slug']}: {r['wc']} words")

    # Hero uniqueness
    heroes = [(r["slug"], r.get("hero", "")) for r in results if r.get("hero")]
    seen: dict[str, list[str]] = {}
    for slug, h in heroes:
        seen.setdefault(h, []).append(slug)
    dup_hero_groups = {h: slugs for h, slugs in seen.items() if len(slugs) > 1}
    print(f"\nhero images: total={len(heroes)} unique={len(seen)} dup_groups={len(dup_hero_groups)}")
    if dup_hero_groups:
        print("first 5 dup-hero groups:")
        for h, slugs in list(dup_hero_groups.items())[:5]:
            print(f"  {h}")
            for s in slugs:
                print(f"    - {s}")

    REPORT.write_text(json.dumps({
        "results": results,
        "in_band": [r["slug"] for r in in_band],
        "too_short": [{"slug": r["slug"], "wc": r["wc"]} for r in too_short],
        "too_long": [{"slug": r["slug"], "wc": r["wc"]} for r in too_long],
        "duplicate_heroes": dup_hero_groups,
    }, indent=2))
    print(f"\nfull report: {REPORT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
