"""
Final-Pass patcher for QUEUE articles (430 gated articles on Bunny).

Same voice/format treatment as published articles:
  * Strip em-dash / en-dash
  * Replace banned words, strip banned filler phrases
  * Convert OLD <div class="tldr"> to spec <section data-tldr="ai-overview">
  * Inject self-ref phrases
  * Ensure authoritative outbound link
  * Rewrite byline block
  * Re-upload article JSON to Bunny
  * Update queue-manifest.json

Does NOT backdate (queue articles keep their future publish_at dates).
"""
import os
import sys
import json
import re
import hashlib
import datetime as dt
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib.request as ureq

ROOT = "/home/ubuntu/autoimmune-reset"
MANIFEST = f"{ROOT}/client/public/content/queue-manifest.json"
PULL_ZONE = "https://conscious-elder.b-cdn.net/immune-rebuilt"
STORAGE_HOST = "ny.storage.bunnycdn.com"
STORAGE_ZONE = "conscious-elder"
STORAGE_KEY = "f6dbc11c-20dc-4c15-a39faabe3d28-a766-4a87"

# Import all patch functions from the published patcher
sys.path.insert(0, os.path.dirname(__file__))

# ---- HTTP helpers ----
def http_get(url, retries=3):
    for attempt in range(retries):
        try:
            req = ureq.Request(url, headers={"User-Agent": "ImmuneRebuilt/1.0"})
            with ureq.urlopen(req, timeout=30) as r:
                return r.read()
        except Exception as e:
            if attempt == retries - 1:
                raise
    return b""

def http_get_storage(path, retries=3):
    """Read directly from Bunny storage origin (bypasses CDN cache)."""
    url = f"https://{STORAGE_HOST}/{STORAGE_ZONE}/{path}"
    for attempt in range(retries):
        try:
            req = ureq.Request(url, headers={
                "AccessKey": STORAGE_KEY,
                "Accept": "application/json",
            })
            with ureq.urlopen(req, timeout=30) as r:
                return r.read()
        except Exception as e:
            if attempt == retries - 1:
                raise
    return b""

def http_put(path, data, content_type="application/octet-stream"):
    url = f"https://{STORAGE_HOST}/{STORAGE_ZONE}/{path}"
    req = ureq.Request(url, data=data, method="PUT", headers={
        "AccessKey": STORAGE_KEY,
        "Content-Type": content_type,
    })
    with ureq.urlopen(req, timeout=60) as r:
        return r.read()

# ---- Voice rules ----
BANNED_WORD_REPLACEMENTS = {
    "cutting-edge": "current", "state-of-the-art": "current",
    "ever-evolving": "still changing",
    "delves": "looks at", "delve": "look at", "delving": "looking at",
    "tapestry": "weave", "paradigm": "frame", "synergy": "fit together",
    "leverages": "uses", "leveraged": "used", "leverage": "use", "leveraging": "using",
    "unlocks": "opens up", "unlocked": "opened", "unlock": "open up", "unlocking": "opening up",
    "empowers": "helps", "empowered": "helped", "empower": "help", "empowering": "helping",
    "elevates": "lifts", "elevated": "lifted", "elevate": "lift", "elevating": "lifting",
    "transformative": "meaningful", "revolutionary": "new", "groundbreaking": "new",
    "innovative": "fresh", "navigate": "move through", "navigating": "moving through",
    "embark": "begin", "embarking": "beginning", "embarked": "began",
    "journey": "path", "landscape": "field", "ecosystem": "system",
    "robust": "strong", "seamless": "smooth", "indispensable": "necessary",
    "pivotal": "important", "crucial": "important", "vital": "important",
    "paramount": "central", "holistic": "whole-body", "comprehensive": "thorough",
    "multifaceted": "layered", "moreover": "and", "furthermore": "and",
    "nonetheless": "still", "nevertheless": "still", "additionally": "also",
    "consequently": "so", "subsequently": "then", "thereby": "by doing so",
    "hereby": "here", "wherein": "where", "henceforth": "from now on",
    "thus": "so", "hence": "so", "therefore": "so", "ergo": "so",
    "albeit": "even though", "whilst": "while", "amongst": "among",
}

BANNED_PHRASES = [
    "the truth is", "the reality is", "in conclusion", "deep dive", "deep-dive",
    "needle in a haystack", "tip of the iceberg", "game changer", "game-changer",
    "at the end of the day", "when it comes to", "in today's world",
    "in this day and age", "make no mistake", "let's face it", "as we all know",
    "needless to say", "in summary", "to summarize", "in essence",
    "the bottom line", "bottom line", "in a nutshell", "long story short",
    "all things considered", "by and large", "for what it's worth",
    "suffice it to say", "as a matter of fact", "for all intents and purposes",
    "in this article", "this article will", "this article explores",
    "this guide will", "this post will", "in this post",
    "let's dive in", "let's get started", "without delay",
    "first and foremost", "to begin with", "to start with", "first off",
    "i hope this helps", "thanks for reading", "happy reading", "stay tuned",
    "without further ado", "rest assured", "look no further",
]

def strip_dashes(body):
    body = body.replace("\u2014", " - ")
    body = body.replace("\u2013", " - ")
    return body

def strip_banned_phrases(body):
    for phrase in BANNED_PHRASES:
        pattern = re.compile(re.escape(phrase), re.IGNORECASE)
        body = pattern.sub("", body)
    # Clean up double spaces left behind.
    body = re.sub(r"  +", " ", body)
    body = re.sub(r" ([.,;:!?])", r"\1", body)
    return body

def replace_banned_words(body):
    for word, replacement in BANNED_WORD_REPLACEMENTS.items():
        pattern = re.compile(r"\b" + re.escape(word) + r"\b", re.IGNORECASE)
        def _repl(m, rep=replacement):
            if m.group()[0].isupper():
                return rep[0].upper() + rep[1:]
            return rep
        body = pattern.sub(_repl, body)
    return body

# ---- TL;DR conversion ----
def ensure_tldr_section(body, article):
    """Convert old TL;DR div to spec-compliant section."""
    # Already has the new format?
    if 'data-tldr="ai-overview"' in body:
        return body

    # Extract old TL;DR text if present.
    old_match = re.search(
        r'<div class="tldr">\s*<p>\s*<strong>TL;DR\.?</strong>\s*(.*?)</p>\s*</div>',
        body, re.DOTALL | re.IGNORECASE
    )
    
    title = article.get("title", "")
    category = article.get("category", "")
    
    # Build three declarative sentences (<=32 words each).
    s1 = f"This piece covers {title.lower().rstrip('.')} within the context of autoimmune health."
    s2 = f"The focus is on practical, evidence-informed steps that fit into daily life without adding stress."
    s3 = f"Read slowly, compare against your own experience, and pick one small move for this week."
    
    # Trim each to 32 words max.
    def cap32(s):
        words = s.split()
        if len(words) <= 32:
            return s
        return " ".join(words[:32]).rstrip(",;:") + "."
    
    new_section = (
        '<section data-tldr="ai-overview" aria-label="In short">\n'
        f"  <p>{cap32(s1)}</p>\n"
        f"  <p>{cap32(s2)}</p>\n"
        f"  <p>{cap32(s3)}</p>\n"
        "</section>"
    )
    
    if old_match:
        body = body[:old_match.start()] + new_section + body[old_match.end():]
    else:
        # Prepend before first <h2> or at top.
        h2_pos = body.find("<h2")
        if h2_pos > 0:
            body = body[:h2_pos] + new_section + "\n" + body[h2_pos:]
        else:
            body = new_section + "\n" + body
    return body

# ---- Self-referencing ----
SELF_REF_PHRASES = [
    "In our experience across the Immune Rebuilt library, ",
    "Across the articles we have published here, ",
    "Readers of this site often find that ",
    "In the years we have spent writing this library, ",
    "Many readers write in to say ",
    "From what we have seen in this community, ",
    "The pattern we notice across our readership is that ",
    "In our ongoing work at Immune Rebuilt, ",
]

def inject_self_ref(body, slug):
    """Inject 2 self-referencing phrases into the body at natural points."""
    # Don't double-inject.
    count = sum(1 for p in SELF_REF_PHRASES if p.lower() in body.lower())
    if count >= 2:
        return body
    
    needed = 2 - count
    h = int(hashlib.sha256(slug.encode()).hexdigest()[:8], 16)
    phrases_to_use = []
    for i in range(needed):
        idx = (h + i * 3) % len(SELF_REF_PHRASES)
        phrases_to_use.append(SELF_REF_PHRASES[idx])
    
    # Find paragraphs to inject into (after first 2 paragraphs).
    p_positions = [m.start() for m in re.finditer(r"<p>", body)]
    if len(p_positions) < 4:
        return body
    
    # Inject at positions 3 and 5 (0-indexed).
    inject_positions = []
    for i, target in enumerate([3, 5]):
        if target < len(p_positions):
            inject_positions.append((p_positions[target], phrases_to_use[i] if i < len(phrases_to_use) else None))
    
    # Apply in reverse order so positions don't shift.
    for pos, phrase in reversed(inject_positions):
        if phrase:
            body = body[:pos + 3] + phrase.lower() + body[pos + 3:]
    
    return body

# ---- Byline ----
SITE_TITLE = "Immune Rebuilt"
AUTHOR = "The Immune Rebuilt Editorial Team"

def replace_byline_block(body, article):
    slug = article.get("slug", "")
    publish_at = article.get("publish_at", dt.datetime.now(dt.timezone.utc).isoformat())
    
    try:
        d = dt.datetime.fromisoformat(publish_at.replace("Z", "+00:00"))
        pretty_date = d.strftime("%B %-d, %Y")
    except:
        pretty_date = "2026"
    
    h = int(hashlib.sha256(slug.encode()).hexdigest()[:6], 16)
    context_variants = [
        f"This piece is part of the {SITE_TITLE} library on autoimmune health, written to be read slowly and returned to when needed.",
        f"Written for the {SITE_TITLE} community by a team that reads the research carefully and writes for the patient, not the algorithm.",
        f"Part of the {SITE_TITLE} collection, where every article is written with the same care we would bring to a conversation with a friend in a hard week.",
    ]
    context = context_variants[h % len(context_variants)]
    
    new_byline = (
        f'\n<p class="byline">'
        f'By <span class="author">{AUTHOR}</span> for '
        f'<a href="/about">{SITE_TITLE}</a> '
        f'<span class="dot">.</span> '
        f'<time datetime="{publish_at}">{pretty_date}</time>'
        f'</p>\n'
        f'<p class="byline-context">{context}</p>\n'
    )
    
    # Replace existing byline block.
    old_byline_re = re.compile(
        r'<p class="byline">.*?</p>(\s*<p class="byline-context">.*?</p>)?',
        flags=re.DOTALL,
    )
    if old_byline_re.search(body):
        body = old_byline_re.sub(new_byline, body, count=1)
        return body
    # No byline - append at end.
    return body + new_byline

# ---- Authoritative outbound ----
AUTH_OUTBOUND_RE = re.compile(
    r'href="https?://[^"]*?(\.gov|\.edu|nih\.gov|cdc\.gov|who\.int|nature\.com|sciencedirect|pubmed|ncbi\.nlm\.nih\.gov|nejm\.org|bmj\.com|thelancet\.com|academic\.oup\.com|cell\.com|jamanetwork\.com|frontiersin\.org|mdpi\.com|springer\.com|wiley\.com)',
    re.IGNORECASE
)

AUTH_LINKS_BY_CATEGORY = {
    "Root Causes": ("NIH autoimmune overview", "https://www.niaid.nih.gov/diseases-conditions/autoimmune-diseases"),
    "Gut Healing": ("NIH gut microbiome and immunity", "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7213601/"),
    "AIP & Diet": ("NIH elimination diets and autoimmunity", "https://pubmed.ncbi.nlm.nih.gov/28727633/"),
    "Stress & Nervous System": ("NIH stress and immune function", "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1361287/"),
    "Functional Medicine": ("NIH integrative approaches", "https://www.nccih.nih.gov/health/autoimmune-diseases"),
    "Emotional Roots": ("CDC adverse childhood experiences", "https://www.cdc.gov/violenceprevention/aces/index.html"),
}
DEFAULT_AUTH = ("NIH autoimmune diseases", "https://www.niaid.nih.gov/diseases-conditions/autoimmune-diseases")

def ensure_authoritative_outbound(body, article):
    if AUTH_OUTBOUND_RE.search(body):
        return body
    
    category = article.get("category", "")
    label, url = AUTH_LINKS_BY_CATEGORY.get(category, DEFAULT_AUTH)
    
    link_html = (
        f'\n<p class="further-reading">For further reading from an authoritative source, see '
        f'<a href="{url}" rel="nofollow noopener" target="_blank">{label}</a>.</p>\n'
    )
    
    # Insert before the last </p> or at end.
    last_p = body.rfind("</p>")
    if last_p > 0:
        body = body[:last_p + 4] + link_html + body[last_p + 4:]
    else:
        body += link_html
    return body

# ---- Patch pipeline ----
def patch_body(article, body):
    body = strip_dashes(body)
    body = strip_banned_phrases(body)
    body = replace_banned_words(body)
    body = ensure_tldr_section(body, article)
    body = inject_self_ref(body, article["slug"])
    body = replace_byline_block(body, article)
    body = ensure_authoritative_outbound(body, article)
    return body

# ---- Main ----
def fetch_article(slug):
    raw = http_get_storage(f"immune-rebuilt/articles/{slug}.json")
    return json.loads(raw.decode("utf-8"))

def upload_article(article):
    payload = json.dumps(article, ensure_ascii=False).encode("utf-8")
    http_put(f"immune-rebuilt/articles/{article['slug']}.json", payload, "application/json; charset=utf-8")

def process_one(article_meta):
    slug = article_meta["slug"]
    a = fetch_article(slug)
    a["slug"] = slug
    # Keep existing publish_at (future date for queue articles).
    a["category"] = article_meta.get("category", a.get("category", ""))
    a["title"] = article_meta.get("title", a.get("title", ""))
    body = a.get("body", "")
    if not body or len(body) < 200:
        return slug, 0, 0, "SKIP:no_body"
    body = patch_body(a, body)
    a["body"] = body
    a["last_modified_at"] = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    a["word_count"] = len(re.sub(r"<[^>]+>", " ", body).split())
    upload_article(a)
    return slug, a["word_count"], len(body), "OK"

def main():
    with open(MANIFEST, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    articles = manifest["articles"]
    print(f"Queue articles to patch: {len(articles)}", flush=True)

    failures = []
    successes = []
    skipped = []
    
    with ThreadPoolExecutor(max_workers=12) as ex:
        futs = {ex.submit(process_one, a): a["slug"] for a in articles}
        for i, fut in enumerate(as_completed(futs), start=1):
            s = futs[fut]
            try:
                slug, wc, bl, status = fut.result()
                if status == "OK":
                    successes.append((slug, wc, bl))
                else:
                    skipped.append((slug, status))
                if i % 25 == 0 or i == len(futs):
                    print(f"  [{i}/{len(futs)}] {status} ({slug}, words={wc})", flush=True)
            except Exception as e:
                failures.append((s, str(e)))
                if i % 25 == 0 or i == len(futs):
                    print(f"  [{i}/{len(futs)}] FAIL {s}: {e}", flush=True)

    print(f"\nDone. Successes: {len(successes)} / Skipped: {len(skipped)} / Failures: {len(failures)}")
    if failures:
        for s, e in failures[:20]:
            print(f"  FAIL {s}: {e}")
    if skipped:
        print(f"  Skipped (no body): {len(skipped)}")

if __name__ == "__main__":
    main()
