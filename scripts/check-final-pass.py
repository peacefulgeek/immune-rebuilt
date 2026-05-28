#!/usr/bin/env python3
"""Spot-check N random articles for Final-Pass compliance."""
import json, re, random, sys, urllib.request as ureq

PULL_ZONE = "https://conscious-elder.b-cdn.net/immune-rebuilt"
STORAGE = "https://ny.storage.bunnycdn.com/conscious-elder/immune-rebuilt"
STORAGE_KEY = "f6dbc11c-20dc-4c15-a39faabe3d28-a766-4a87"
BANNED_SAMPLE = ["delve","tapestry","leverage","unlock","empower","utilize","seamless","robust","foster","elevate","curate","resonate","harness","intricate","plethora","myriad","comprehensive","transformative","groundbreaking","innovative","revolutionary","holistic","nuanced","stakeholders","ecosystem","landscape","realm","sphere","furthermore","moreover","additionally","consequently","subsequently","thereby","streamline","optimize","facilitate","amplify","catalyze","paradigm","synergy","pivotal","embark","underscore","beacon"]

def get(slug):
    # Read from Bunny Storage origin (auth header) so we always see the freshest patched body,
    # bypassing the pull-zone CDN cache entirely.
    req = ureq.Request(
        f"{STORAGE}/articles/{slug}.json",
        headers={"AccessKey": STORAGE_KEY},
    )
    with ureq.urlopen(req, timeout=20) as r:
        return json.loads(r.read())

def check(slug):
    a = get(slug)
    body = a["body"]
    text = re.sub(r"<[^>]+>", " ", body).lower()
    em = body.count("—") + body.count("–")
    hits = []
    for w in BANNED_SAMPLE:
        if re.search(r"\b" + re.escape(w) + r"\b", text):
            hits.append(w)
    has_section = '<section data-tldr="ai-overview"' in body
    has_old = '<div class="tldr"' in body
    selfref_marker = "<!--self-ref-injected-->" in body
    byline = body.count('class="byline"')
    bctx = body.count('class="byline-context"')
    internal = len(re.findall(r'href="/articles/[^"]+"', body))
    outbound = re.findall(r'href="(https?://[^"]+)"', body)
    auth_rx = re.compile(
        r'(?:'
        r'\.gov|\.edu|\.who\.int'
        r'|nature\.com|sciencedirect|pubmed|ncbi\.nlm\.nih\.gov'
        r'|nejm\.org|bmj\.com|thelancet\.com|cell\.com|academic\.oup\.com'
        r'|jamanetwork\.com|frontiersin\.org|mdpi\.com|springer\.com'
        r'|onlinelibrary\.wiley\.com|liebertpub\.com|biomedcentral\.com'
        r'|tandfonline\.com|sagepub\.com|cochrane\.org|cochranelibrary\.com'
        r')',
        re.I,
    )
    auth = [u for u in outbound if auth_rx.search(u)]
    return {
        "slug": slug,
        "publish_at": a.get("publish_at"),
        "word_count": a.get("word_count"),
        "em_dash": em,
        "banned_hits": hits,
        "tldr_section": has_section,
        "tldr_old_div": has_old,
        "self_ref": selfref_marker,
        "byline": byline,
        "byline_context": bctx,
        "internal_links": internal,
        "outbound_total": len(outbound),
        "outbound_authoritative": len(auth),
    }

from concurrent.futures import ThreadPoolExecutor, as_completed
manifest = json.load(open("/home/ubuntu/autoimmune-reset/client/public/content/preview-manifest.json"))
slugs = [a["slug"] for a in manifest["articles"]]
print(f"checking all {len(slugs)} articles in parallel ...\n")

results = {}
fails = []
with ThreadPoolExecutor(max_workers=12) as ex:
    futs = {ex.submit(check, s): s for s in slugs}
    for i, fut in enumerate(as_completed(futs), start=1):
        s = futs[fut]
        try:
            r = fut.result()
            results[s] = r
            bad = []
            if r["em_dash"] > 0: bad.append("em_dash")
            if r["banned_hits"]: bad.append("banned:"+",".join(r["banned_hits"][:3]))
            if not r["tldr_section"]: bad.append("no-tldr-section")
            if r["tldr_old_div"]: bad.append("old-tldr-div")
            if not r["self_ref"]: bad.append("no-selfref")
            if r["byline"] < 1: bad.append("no-byline")
            if r["byline_context"] < 1: bad.append("no-byline-ctx")
            if r["internal_links"] < 3: bad.append("internal<3")
            if r["outbound_authoritative"] < 1: bad.append("no-authoritative-outbound")
            if bad:
                fails.append((s, r, bad))
        except Exception as e:
            fails.append((s, None, [f"exception:{e}"]))
        if i % 20 == 0:
            print(f"  ...{i}/{len(slugs)}")

print(f"\n{len(slugs) - len(fails)}/{len(slugs)} articles compliant")
if fails:
    print(f"FAILURES ({len(fails)}):")
    for s, r, bad in fails:
        if r:
            print(f"  {s}: {bad}  (em={r['em_dash']}, sec={r['tldr_section']}, byln={r['byline']}/{r['byline_context']}, int={r['internal_links']}, auth_out={r['outbound_authoritative']})")
        else:
            print(f"  {s}: {bad}")
sys.exit(1 if fails else 0)
