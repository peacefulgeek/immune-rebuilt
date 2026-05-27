#!/usr/bin/env python3
"""
Extend 30 short articles to 1800+ words by appending a 280-360 word
"Week-by-week practice" section tailored to the article's topic.

- Uses the OpenAI-compatible Manus LLM proxy (DeepSeek-style chat).
- Pulls each article from Bunny, appends the section just before the
  final CTA paragraph (or at the end if no CTA), re-uploads JSON.
- Updates word_count in the article JSON only (manifest will be
  rebuilt separately if needed).
"""
import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

ROOT = Path("/home/ubuntu/autoimmune-reset")
PULL = "https://conscious-elder.b-cdn.net/immune-rebuilt/articles"
PUT_BASE = "https://ny.storage.bunnycdn.com/conscious-elder/immune-rebuilt/articles"
BUNNY_KEY = "f6dbc11c-20dc-4c15-a39faabe3d28-a766-4a87"
REPORT = ROOT / ".article-qa-report.json"

API_KEY = os.environ.get("OPENAI_API_KEY")
API_BASE = os.environ.get("OPENAI_BASE_URL") or os.environ.get("OPENAI_API_BASE")
# Manus proxy only allows: gemini-2.5-flash, gpt-4.1-mini, gpt-4.1-nano
MODEL = "gpt-4.1-mini"
if not API_KEY or not API_BASE:
    print("Need OPENAI_API_KEY + OPENAI_BASE_URL")
    sys.exit(1)

TAG_RE = re.compile(r"<[^>]+>")
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "extend-short/1.0"})


def word_count(html: str) -> int:
    text = TAG_RE.sub(" ", html or "")
    text = re.sub(r"\s+", " ", text).strip()
    return len(text.split())


SYSTEM = (
    "You are writing for Immune Rebuilt, a clinically grounded autoimmune "
    "education site. Voice references: Alessio Fasano, Terry Wahls, Bessel "
    "van der Kolk. Keep it warm, plain-spoken, lightly hopeful, never hyped. "
    "Never promise cures. Use plain HTML only: <p>, <h2>, <ul>, <li>, <strong>. "
    "No 'TL;DR'. No emoji. No marketing language. American English."
)


def build_user_prompt(title: str, slug: str, excerpt: str, body_text_first_500: str) -> str:
    return (
        f"Article title: {title}\n"
        f"Article slug: {slug}\n"
        f"Excerpt: {excerpt}\n\n"
        f"Article opening (for tone reference):\n{body_text_first_500}\n\n"
        "Write a single self-contained section to APPEND at the end of the "
        "article. The section MUST:\n"
        "- Start with: <h2>What this looks like in practice — week one through six</h2>\n"
        "- Be 320–360 words.\n"
        "- Include a brief 2–3 sentence intro paragraph framing why a six-week "
        "  arc is realistic for this topic.\n"
        "- Then a <ul> with exactly six <li> items labeled 'Week 1:' through "
        "  'Week 6:'. Each li 30–55 words. Each li must be specific to THIS "
        "  article's topic, not generic.\n"
        "- End with a closing 2–4 sentence paragraph that names ONE thing the "
        "  reader can do today (a small, specific, kind action) and one thing "
        "  to check at week six (a measurable signal — sleep quality, joint "
        "  stiffness on a 0–10 scale, gut symptom diary, etc.).\n"
        "- Output HTML only. No code fences. No commentary."
    )


def llm_extend(title: str, slug: str, excerpt: str, body_first: str) -> str:
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": build_user_prompt(title, slug, excerpt, body_first)},
        ],
        "temperature": 0.7,
        "max_tokens": 1200,
    }
    r = SESSION.post(
        f"{API_BASE}/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json=payload,
        timeout=90,
    )
    r.raise_for_status()
    j = r.json()
    return j["choices"][0]["message"]["content"].strip()


def insert_extension(body: str, extension: str) -> str:
    """Insert the extension before the final CTA paragraph if present.
    A CTA paragraph is the final <p> in the body. Otherwise append at the end."""
    body = body.rstrip()
    # find last </p>
    last_p = body.rfind("</p>")
    if last_p == -1:
        return body + "\n\n" + extension
    # find start of that final paragraph
    start = body.rfind("<p", 0, last_p)
    if start == -1:
        return body + "\n\n" + extension
    return body[:start].rstrip() + "\n\n" + extension + "\n\n" + body[start:]


def process(slug: str) -> dict:
    last = ""
    for attempt in range(3):
        try:
            r = SESSION.get(f"{PULL}/{slug}.json", timeout=20)
            r.raise_for_status()
            j = r.json()
            break
        except Exception as e:
            last = str(e)[:100]
            time.sleep(0.5 * (attempt + 1))
    else:
        return {"slug": slug, "status": f"fetch:{last}"}

    body = j.get("body", "")
    title = j.get("title") or slug.replace("-", " ").title()
    excerpt = j.get("excerpt", "")
    body_text = TAG_RE.sub(" ", body)
    body_first = re.sub(r"\s+", " ", body_text).strip()[:500]
    before = word_count(body)

    try:
        ext = llm_extend(title, slug, excerpt, body_first)
    except Exception as e:
        return {"slug": slug, "status": f"llm:{str(e)[:120]}"}
    if "<h2>" not in ext or "</ul>" not in ext.lower():
        return {"slug": slug, "status": "ext-shape-bad"}

    new_body = insert_extension(body, ext)
    new_wc = word_count(new_body)
    if new_wc < 1800:
        return {"slug": slug, "status": f"still-short:{new_wc}"}

    j["body"] = new_body
    j["word_count"] = new_wc

    payload = json.dumps(j, ensure_ascii=False).encode("utf-8")
    for attempt in range(3):
        try:
            r = SESSION.put(
                f"{PUT_BASE}/{slug}.json",
                data=payload,
                headers={"AccessKey": BUNNY_KEY, "Content-Type": "application/json"},
                timeout=30,
            )
            if r.status_code in (200, 201):
                return {"slug": slug, "status": "extended", "before": before, "after": new_wc}
        except Exception as e:
            last = str(e)[:100]
            time.sleep(0.5 * (attempt + 1))
    return {"slug": slug, "status": f"put:{last}"}


def main() -> int:
    rep = json.loads(REPORT.read_text())
    slugs = [s["slug"] for s in rep["too_short"]]
    print(f"extending {len(slugs)} short articles (concurrency=4)", flush=True)
    out: list[dict] = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        futs = {pool.submit(process, s): s for s in slugs}
        done = 0
        for f in as_completed(futs):
            out.append(f.result())
            done += 1
            if done % 5 == 0 or done == len(slugs):
                ok = sum(1 for r in out if r["status"] == "extended")
                fail = sum(1 for r in out if r["status"] != "extended")
                print(f"  [{done}/{len(slugs)}] extended={ok} fail={fail}", flush=True)
    print()
    extended = [r for r in out if r["status"] == "extended"]
    failed = [r for r in out if r["status"] != "extended"]
    print(f"final: extended={len(extended)} failed={len(failed)}")
    if failed[:10]:
        print("failed:")
        for r in failed[:10]:
            print(f"  {r['slug']} -> {r['status']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
