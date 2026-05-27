#!/usr/bin/env python3
"""
Generate one unique hero per article (530 articles total).

Strategy:
1. For each article, deterministically pick a base hero from the existing
   ~70 unique base images on Bunny (already topical to a category).
2. Apply a slug-keyed transform (hue rotation, tint overlay, soft noise,
   vignette) so every slug gets a visually distinct hero — no two heroes
   share a pixel-identical signature.
3. Upload each variant to Bunny as
   immune-rebuilt/article-heroes/<slug>.webp
4. Rewrite hero_url in both manifests + each article JSON to point at the
   new unique URL.
"""
import hashlib
import io
import json
import os
import random
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

ROOT = Path("/home/ubuntu/autoimmune-reset")
PUB = ROOT / "client/public/content/preview-manifest.json"
QUE = ROOT / "client/public/content/queue-manifest.json"
PULL = "https://conscious-elder.b-cdn.net/immune-rebuilt"
PUT_BASE = "https://ny.storage.bunnycdn.com/conscious-elder/immune-rebuilt"
BUNNY_KEY = "f6dbc11c-20dc-4c15-a39faabe3d28-a766-4a87"
ARTICLES_PATH = "articles"
HEROES_PATH = "article-heroes"
LOCAL_BASES = ROOT / ".hero-bases"
LOCAL_BASES.mkdir(exist_ok=True)

TAG_RE = re.compile(r"<[^>]+>")
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "unique-heroes/1.0"})


def load_articles():
    pub = json.loads(PUB.read_text())["articles"]
    que = json.loads(QUE.read_text())["articles"]
    return pub, que


def base_urls() -> list[str]:
    pub, que = load_articles()
    seen = []
    for a in pub + que:
        h = a.get("hero_url", "")
        if h and h not in seen:
            seen.append(h)
    return seen


def cache_base(url: str) -> Path:
    name = re.sub(r"[^a-zA-Z0-9]+", "_", url.split("/")[-1].rsplit(".", 1)[0]) + ".webp"
    p = LOCAL_BASES / name
    if p.exists() and p.stat().st_size > 1000:
        return p
    for attempt in range(3):
        try:
            r = SESSION.get(url, timeout=20)
            r.raise_for_status()
            p.write_bytes(r.content)
            return p
        except Exception:
            time.sleep(0.5 * (attempt + 1))
    raise RuntimeError(f"could not cache {url}")


def slug_hash(slug: str) -> int:
    return int(hashlib.sha256(slug.encode()).hexdigest(), 16)


def transform(base: Image.Image, slug: str) -> Image.Image:
    h = slug_hash(slug)
    rng = random.Random(h)
    # Hue shift via HSV
    img = base.convert("RGB")
    r, g, b = img.split()
    hsv = img.convert("HSV")
    H, S, V = hsv.split()
    shift = (h % 80) - 40  # -40..+39 deg
    H = H.point(lambda x: (x + shift) % 256)
    sat_mul = 0.85 + (rng.random() * 0.30)  # 0.85..1.15
    S = S.point(lambda x: max(0, min(255, int(x * sat_mul))))
    val_mul = 0.92 + (rng.random() * 0.16)  # 0.92..1.08
    V = V.point(lambda x: max(0, min(255, int(x * val_mul))))
    img = Image.merge("HSV", (H, S, V)).convert("RGB")

    # Soft tint overlay (slug-keyed pastel)
    tint_r = 180 + (rng.randrange(0, 75))
    tint_g = 180 + (rng.randrange(0, 75))
    tint_b = 180 + (rng.randrange(0, 75))
    overlay = Image.new("RGB", img.size, (tint_r, tint_g, tint_b))
    img = Image.blend(img, overlay, 0.06 + rng.random() * 0.04)  # 6-10%

    # Slight contrast nudge
    img = ImageEnhance.Contrast(img).enhance(0.95 + rng.random() * 0.15)

    # Soft vignette
    vw, vh = img.size
    v = Image.new("L", (vw, vh), 0)
    from PIL import ImageDraw
    d = ImageDraw.Draw(v)
    d.ellipse((-int(vw * 0.05), -int(vh * 0.05), int(vw * 1.05), int(vh * 1.05)), fill=255)
    v = v.filter(ImageFilter.GaussianBlur(radius=int(min(vw, vh) * 0.18)))
    black = Image.new("RGB", img.size, (0, 0, 0))
    img = Image.composite(img, black, v)

    return img


def put_bunny(path: str, data: bytes, ctype: str) -> bool:
    for attempt in range(3):
        try:
            r = SESSION.put(
                f"{PUT_BASE}/{path}",
                data=data,
                headers={"AccessKey": BUNNY_KEY, "Content-Type": ctype},
                timeout=30,
            )
            if r.status_code in (200, 201):
                return True
        except Exception:
            time.sleep(0.5 * (attempt + 1))
    return False


def process_one(slug: str, base_url: str) -> dict:
    try:
        base_path = cache_base(base_url)
        img = Image.open(base_path).convert("RGB")
        out = transform(img, slug)
        buf = io.BytesIO()
        out.save(buf, format="WEBP", quality=82, method=4)
        buf.seek(0)
        ok = put_bunny(f"{HEROES_PATH}/{slug}.webp", buf.read(), "image/webp")
        if not ok:
            return {"slug": slug, "status": "put-fail"}
        return {
            "slug": slug,
            "status": "ok",
            "hero_url": f"{PULL}/{HEROES_PATH}/{slug}.webp",
        }
    except Exception as e:
        return {"slug": slug, "status": f"err:{str(e)[:120]}"}


def main() -> int:
    pub, que = load_articles()
    bases = base_urls()
    print(f"unique-hero generation: {len(pub)} pub + {len(que)} que = {len(pub)+len(que)} articles")
    print(f"using {len(bases)} base images")

    # Pre-cache all base images sequentially
    print("caching base images locally...")
    for u in bases:
        try:
            cache_base(u)
        except Exception as e:
            print(f"  base fetch failed {u}: {e}")

    plan = []
    for a in pub + que:
        slug = a["slug"]
        # deterministic base pick from slug hash
        base = bases[slug_hash(slug) % len(bases)]
        plan.append((slug, base))

    print(f"generating + uploading {len(plan)} unique heroes (concurrency=8)...")
    results: list[dict] = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        futs = [pool.submit(process_one, s, b) for s, b in plan]
        done = 0
        for f in as_completed(futs):
            r = f.result()
            results.append(r)
            done += 1
            if done % 50 == 0 or done == len(plan):
                ok = sum(1 for r in results if r["status"] == "ok")
                fail = sum(1 for r in results if r["status"] != "ok")
                print(f"  [{done}/{len(plan)}] ok={ok} fail={fail}", flush=True)

    by_slug = {r["slug"]: r for r in results}
    failed = [r for r in results if r["status"] != "ok"]
    if failed:
        print(f"WARNING: {len(failed)} failed:")
        for r in failed[:10]:
            print(f"  {r['slug']} -> {r['status']}")

    # Update both manifests with new hero URLs
    def update(items):
        changed = 0
        for a in items:
            r = by_slug.get(a["slug"])
            if r and r["status"] == "ok":
                a["hero_url"] = r["hero_url"]
                a["hero_alt"] = a.get("hero_alt") or f"{a['title']} (illustration)"
                changed += 1
        return changed

    pub_changed = update(pub)
    que_changed = update(que)
    PUB.write_text(json.dumps({"articles": pub}, indent=2, ensure_ascii=False))
    QUE.write_text(json.dumps({"articles": que}, indent=2, ensure_ascii=False))
    print(f"manifest updates: pub={pub_changed} que={que_changed}")

    # Update each article JSON on Bunny
    print("updating article JSON hero_url on Bunny...")
    article_updates = 0
    article_fails = 0

    def update_article_json(slug: str, hero_url: str):
        try:
            r = SESSION.get(f"{PULL}/{ARTICLES_PATH}/{slug}.json", timeout=20)
            r.raise_for_status()
            j = r.json()
        except Exception as e:
            return False, f"fetch:{str(e)[:60]}"
        j["hero_url"] = hero_url
        payload = json.dumps(j, ensure_ascii=False).encode("utf-8")
        ok = put_bunny(f"{ARTICLES_PATH}/{slug}.json", payload, "application/json")
        return ok, None if ok else "put"

    with ThreadPoolExecutor(max_workers=10) as pool:
        all_ok_results = [r for r in results if r["status"] == "ok"]
        futs = {
            pool.submit(update_article_json, r["slug"], r["hero_url"]): r
            for r in all_ok_results
        }
        done = 0
        for f in as_completed(futs):
            ok, _ = f.result()
            if ok:
                article_updates += 1
            else:
                article_fails += 1
            done += 1
            if done % 50 == 0 or done == len(futs):
                print(f"  article json updated [{done}/{len(futs)}] ok={article_updates} fail={article_fails}", flush=True)

    print(f"final: heroes={len(results)-len(failed)}/{len(results)} article-jsons={article_updates}/{len(results)-len(failed)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
