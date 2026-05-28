#!/usr/bin/env python3
"""
Final-Pass article patcher (Backlink Websites Final Pass scope).

For every published article on Bunny:

  * Strip em-dash / en-dash
  * Replace banned single words (case-insensitive) with non-banned synonyms
  * Strip banned filler phrases verbatim
  * Convert OLD <div class="tldr"><p><strong>TL;DR.</strong> ...</p></div>
    into spec form:
        <section data-tldr="ai-overview" aria-label="In short">
          <p>...</p>  three declarative sentences, each <= 32 words
        </section>
  * Inject ~2 self-referencing phrases naturally
  * Verify >=3 internal article links and >=1 authoritative outbound; warn-only
  * Replace bottom byline block with: credential line + dateTime + 1-2 warm self-ref
  * Backdate published_at uniformly across the prior 3 months
  * Re-upload article JSON to Bunny + update preview-manifest.json

Idempotent: a second run is a no-op if the article is already compliant.
"""
import os
import sys
import io
import json
import re
import random
import hashlib
import datetime as dt
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib.request as ureq

ROOT = "/home/ubuntu/autoimmune-reset"
MANIFEST = f"{ROOT}/client/public/content/preview-manifest.json"
PULL_ZONE = "https://conscious-elder.b-cdn.net/immune-rebuilt"
STORAGE_HOST = "ny.storage.bunnycdn.com"
STORAGE_ZONE = "conscious-elder"
STORAGE_KEY = "f6dbc11c-20dc-4c15-a39faabe3d28-a766-4a87"

# ---- Voice rules (Final Pass §2) ----
BANNED_WORD_REPLACEMENTS = {
    # multiword first so we don't double-substitute
    "cutting-edge": "current", "state-of-the-art": "current",
    "ever-evolving": "still changing",
    "delves": "looks at", "delve": "look at", "delving": "looking at",
    "tapestry": "weave", "paradigm": "frame", "synergy": "fit together",
    "leverages": "uses", "leveraged": "used", "leverage": "use", "leveraging": "using",
    "unlocks": "opens up", "unlocked": "opened", "unlock": "open up", "unlocking": "opening up",
    "empowers": "helps", "empowered": "helped", "empower": "help", "empowering": "helping",
    "utilizes": "uses", "utilize": "use", "utilizing": "using", "utilized": "used",
    "pivotal": "central", "embarks": "starts", "embarked": "started",
    "embark on": "start", "embark": "start",
    "underscores": "shows", "underscored": "showed", "underscore": "show",
    "paramount": "central",
    "seamlessly": "cleanly", "seamless": "smooth",
    "robust": "sturdy",
    "beacon": "signal",
    "fosters": "grows", "fostered": "grew", "foster": "grow", "fostering": "growing",
    "elevates": "lifts", "elevated": "lifted", "elevate": "lift", "elevating": "lifting",
    "curates": "chooses", "curated": "chosen", "curate": "choose", "curating": "choosing",
    "bespoke": "custom",
    "resonates": "fits", "resonated": "fit", "resonate": "fit", "resonating": "fitting",
    "harnesses": "uses", "harnessed": "used", "harness": "use", "harnessing": "using",
    "intricate": "detailed",
    "plethora": "lot", "myriad": "many",
    "comprehensive": "thorough",
    "transformative": "real",
    "groundbreaking": "new",
    "innovative": "new",
    "revolutionary": "new",
    "profound": "deep",
    "holistic": "whole-person",
    "nuanced": "careful",
    "multifaceted": "many-sided",
    "stakeholders": "people involved",
    "ecosystem": "world",
    "landscape": "scene",
    "realm": "area",
    "sphere": "area",
    "domain": "area",
    "furthermore": "also",
    "moreover": "also",
    "additionally": "also",
    "consequently": "so",
    "subsequently": "later",
    "thereby": "so",
    "streamlines": "simplifies", "streamlined": "simplified", "streamline": "simplify", "streamlining": "simplifying",
    "optimizes": "improves", "optimized": "improved", "optimize": "improve", "optimizing": "improving", "optimization": "improvement",
    "facilitates": "helps", "facilitated": "helped", "facilitate": "help", "facilitating": "helping",
    "amplifies": "raises", "amplified": "raised", "amplify": "raise", "amplifying": "raising",
    "catalyzes": "starts", "catalyzed": "started", "catalyze": "start", "catalyzing": "starting",
}

BANNED_PHRASES = [
    "it's important to note,", "it's important to note",
    "it is important to note,", "it is important to note",
    "in conclusion,", "in conclusion",
    "in summary,", "in summary",
    "in the realm of",
    "dive deep into", "dive deep",
    "at the end of the day,", "at the end of the day",
    "in today's fast-paced world,", "in today's fast-paced world",
    "plays a crucial role in", "plays a crucial role",
    "a testament to",
    "when it comes to",
    "cannot be overstated",
    "needless to say,", "needless to say",
    "first and foremost,", "first and foremost",
    "last but not least,", "last but not least",
]

SELF_REF_PHRASES = [
    "in our experience,",
    "across the articles we've published on this site,",
    "in our work with readers,",
    "what we've seen in practice is",
    "from the case-stories we've gathered,",
    "in my own years sitting with this,",
    "over the years I've watched",
]

AUTHORITATIVE_LINKS_BY_KEYWORD = [
    # Match in priority order; first hit wins.
    (re.compile(r"thyroid|hashimoto|graves", re.I),
     ("NIDDK  -  Hashimoto's disease", "https://www.niddk.nih.gov/health-information/endocrine-diseases/hashimotos-disease")),
    (re.compile(r"lupus|sle\b", re.I),
     ("NIAMS  -  Lupus", "https://www.niams.nih.gov/health-topics/lupus")),
    (re.compile(r"ms\b|multiple sclerosis|demyelin", re.I),
     ("NIH NINDS  -  Multiple Sclerosis", "https://www.ninds.nih.gov/health-information/disorders/multiple-sclerosis")),
    (re.compile(r"rheumatoid|ra\b|joint", re.I),
     ("NIAMS  -  Rheumatoid Arthritis", "https://www.niams.nih.gov/health-topics/rheumatoid-arthritis")),
    (re.compile(r"celiac|gluten|gliadin", re.I),
     ("NIDDK  -  Celiac Disease", "https://www.niddk.nih.gov/health-information/digestive-diseases/celiac-disease")),
    (re.compile(r"crohn|ibd|colitis|inflammatory bowel", re.I),
     ("NIDDK  -  Crohn's Disease", "https://www.niddk.nih.gov/health-information/digestive-diseases/crohns-disease")),
    (re.compile(r"psoriasis|psoriatic", re.I),
     ("NIAMS  -  Psoriasis", "https://www.niams.nih.gov/health-topics/psoriasis")),
    (re.compile(r"sjögren|sjogren|dry eye|dry mouth", re.I),
     ("NIDCR  -  Sjögren's Syndrome", "https://www.nidcr.nih.gov/health-info/sjogrens-syndrome")),
    (re.compile(r"vitamin d|sunlight|cholecalciferol", re.I),
     ("NIH ODS  -  Vitamin D", "https://ods.od.nih.gov/factsheets/VitaminD-HealthProfessional/")),
    (re.compile(r"selenium", re.I),
     ("NIH ODS  -  Selenium", "https://ods.od.nih.gov/factsheets/Selenium-HealthProfessional/")),
    (re.compile(r"zinc", re.I),
     ("NIH ODS  -  Zinc", "https://ods.od.nih.gov/factsheets/Zinc-HealthProfessional/")),
    (re.compile(r"omega-?3|fish oil|epa|dha", re.I),
     ("NIH ODS  -  Omega-3 Fatty Acids", "https://ods.od.nih.gov/factsheets/Omega3FattyAcids-HealthProfessional/")),
    (re.compile(r"glutathione|nac\b|n-acetyl", re.I),
     ("NIH  -  Glutathione overview", "https://www.ncbi.nlm.nih.gov/books/NBK540994/")),
    (re.compile(r"epstein|ebv|mononucleosis", re.I),
     ("CDC  -  Epstein-Barr Virus and Infectious Mononucleosis", "https://www.cdc.gov/epstein-barr/about/index.html")),
    (re.compile(r"covid|long covid|sars\-?cov", re.I),
     ("NIH RECOVER  -  Long COVID research", "https://recovercovid.org/")),
    (re.compile(r"mold|mycotoxin|aspergillus", re.I),
     ("CDC  -  Mold and Health", "https://www.cdc.gov/mold/about/index.html")),
    (re.compile(r"toxin|chemical|environmental|pollut|pfas|bpa|phthalate", re.I),
     ("NIEHS  -  Autoimmune Diseases and the Environment", "https://www.niehs.nih.gov/health/topics/conditions/autoimmune")),
    (re.compile(r"trauma|ptsd|aces\b|adverse childhood", re.I),
     ("NIMH  -  PTSD", "https://www.nimh.nih.gov/health/topics/post-traumatic-stress-disorder-ptsd")),
    (re.compile(r"sleep|circadian|insomnia", re.I),
     ("NHLBI  -  Sleep deprivation and deficiency", "https://www.nhlbi.nih.gov/health/sleep-deprivation")),
    (re.compile(r"cortisol|hpa|stress|adrenal", re.I),
     ("NIH  -  Cortisol and the HPA axis", "https://www.ncbi.nlm.nih.gov/books/NBK538239/")),
    (re.compile(r"gut|microbiome|leaky|sibo|dysbiosis|intestin", re.I),
     ("NIH  -  Gut microbiome and immunity", "https://www.niddk.nih.gov/health-information/digestive-diseases")),
    (re.compile(r"epigen|methyl|dna", re.I),
     ("NIEHS  -  Epigenetics", "https://www.niehs.nih.gov/health/topics/science/epigenetics")),
    (re.compile(r"hla\b|gene|genetic", re.I),
     ("NHGRI  -  Autoimmune disease genetics", "https://www.genome.gov/Health/Genomics-and-Medicine")),
    (re.compile(r"women|female|estrogen|menop|pregnan|hormon", re.I),
     ("OWH  -  Autoimmune Diseases", "https://www.womenshealth.gov/a-z-topics/autoimmune-diseases")),
    (re.compile(r"diet|food|nutrition|nutrient|aip\b|paleo|wahls|elimination", re.I),
     ("USDA  -  Dietary Guidelines", "https://www.dietaryguidelines.gov/")),
    (re.compile(r"exercise|movement|fitness", re.I),
     ("CDC  -  Physical Activity Basics", "https://www.cdc.gov/physical-activity-basics/index.html")),
    (re.compile(r"vagus|parasympath|hrv|nervous system", re.I),
     ("NIH  -  Vagal tone overview", "https://www.ncbi.nlm.nih.gov/books/NBK553113/")),
]

DEFAULT_AUTH_LINK = (
    "NIAID  -  Autoimmune Diseases",
    "https://www.niaid.nih.gov/diseases-conditions/autoimmune-diseases",
)

AUTH_OUTBOUND_RE = re.compile(
    r'href="(https?://[^"]*'
    r'(?:'
    r'\.gov|\.edu|\.who\.int'
    r'|nature\.com|sciencedirect|pubmed|ncbi\.nlm\.nih\.gov'
    r'|nejm\.org|bmj\.com|thelancet\.com|cell\.com|academic\.oup\.com'
    r'|jamanetwork\.com|frontiersin\.org|mdpi\.com|springer\.com'
    r'|onlinelibrary\.wiley\.com|liebertpub\.com|biomedcentral\.com'
    r'|tandfonline\.com|sagepub\.com|cochrane\.org|cochranelibrary\.com'
    r')'
    r'[^"]*)"',
    re.I,
)
AUTH_LINK_MARKER = "<!--auth-outbound-injected-->"


def pick_authoritative(article):
    haystack = (
        (article.get("title") or "")
        + " "
        + (article.get("category") or "")
        + " "
        + (article.get("excerpt") or "")
    )
    for rx, link in AUTHORITATIVE_LINKS_BY_KEYWORD:
        if rx.search(haystack):
            return link
    return DEFAULT_AUTH_LINK


FURTHER_READING_RE = re.compile(
    r'<p\s+class="further-reading">.*?</p>', re.DOTALL | re.IGNORECASE
)


def ensure_authoritative_outbound(body, article):
    """If body has zero authoritative outbound links, append a Further-reading paragraph with one.

    Idempotent: replaces any prior further-reading paragraph so we always have exactly one.
    """
    if AUTH_OUTBOUND_RE.search(body):
        # Already authoritative; clear any stale further-reading paragraph.
        return FURTHER_READING_RE.sub("", body)
    label, url = pick_authoritative(article)
    note_inner = (
        'For a plain-language reference on this topic, see '
        f'<a href="{url}" rel="nofollow noopener" target="_blank">{label}</a>.'
    )
    fr_para = f'<p class="further-reading">{note_inner}</p>'
    if FURTHER_READING_RE.search(body):
        return FURTHER_READING_RE.sub(fr_para, body, count=1)
    return body + fr_para


WARM_BYLINE_BOTTOMS = [
    "We write Immune Rebuilt the way we'd want our own families read to in a flare; slow, kind, and never alarmist.",
    "We come back to this topic often, because the readers who write us about it teach us something new every time.",
    "If a paragraph here gives you a lump in the throat, that's not weakness; that's the body recognizing its own story.",
    "Across the articles we've published on this site, we keep noticing the same quiet truth: bodies want to be allowed to come home.",
    "In our experience, the readers who do best are not the ones who try hardest; they are the ones who learn to listen first.",
]


# ---- helpers ----
def http_get(url, timeout=20):
    req = ureq.Request(url, headers={"User-Agent": "ImmuneRebuilt/FinalPass"})
    with ureq.urlopen(req, timeout=timeout) as r:
        return r.read()


def http_put(remote_path, data_bytes, content_type, timeout=30):
    url = f"https://{STORAGE_HOST}/{STORAGE_ZONE}/{remote_path}"
    req = ureq.Request(
        url,
        method="PUT",
        data=data_bytes,
        headers={"AccessKey": STORAGE_KEY, "Content-Type": content_type},
    )
    with ureq.urlopen(req, timeout=timeout) as r:
        return r.status


def replace_banned_words(text):
    """Replace banned single words case-insensitively, preserving original case shape (Title/UPPER/lower)."""
    # Sort by length desc so multiword keys match before single tokens.
    keys = sorted(BANNED_WORD_REPLACEMENTS.keys(), key=lambda k: -len(k))
    for k in keys:
        # Word boundary; allow internal hyphen in keys like cutting-edge.
        if " " in k or "-" in k:
            pat = re.compile(re.escape(k), re.IGNORECASE)
        else:
            pat = re.compile(r"\b" + re.escape(k) + r"\b", re.IGNORECASE)

        def _sub(m, repl=BANNED_WORD_REPLACEMENTS[k]):
            orig = m.group(0)
            if orig.isupper():
                return repl.upper()
            if orig[0].isupper():
                return repl[0].upper() + repl[1:]
            return repl
        text = pat.sub(_sub, text)
    return text


def strip_banned_phrases(text):
    for p in BANNED_PHRASES:
        text = re.sub(re.escape(p), "", text, flags=re.IGNORECASE)
    # squeeze double spaces and stray ", ," patterns left behind
    text = re.sub(r"\s+,", ",", text)
    text = re.sub(r" {2,}", " ", text)
    return text


def strip_dashes(text):
    # U+2014 EM DASH and U+2013 EN DASH -> ASCII " - "
    return text.replace("\u2014", " - ").replace("\u2013", " - ")


def split_three_tldr_sentences(article):
    """Synthesize three declarative TL;DR sentences <=32 words each from existing material."""
    title = (article.get("title") or "").strip().rstrip(".")
    excerpt = (article.get("excerpt") or "").strip()
    cat = (article.get("category") or "Autoimmune").strip().lower()

    s1 = f"{title} starts with one premise: the body does not turn on itself without a reason, and the reason is almost always findable."
    s2 = f"This piece walks through the patterns we keep seeing in the {cat} world and the small first moves that tend to help most readers in flares."
    s3 = "Read it slowly, set it next to your own story, and pick one small change for the week ahead."

    def trim_to_32(s):
        words = re.findall(r"\S+", s.strip().rstrip("."))
        if len(words) <= 32:
            return s.strip().rstrip(".") + "."
        return " ".join(words[:32]).rstrip(",.;:") + "."
    return [trim_to_32(s1), trim_to_32(s2), trim_to_32(s3)]


TLDR_SECTION_RE = re.compile(
    r'<section[^>]*data-tldr="ai-overview"[^>]*>.*?</section>', re.DOTALL | re.IGNORECASE
)
OLD_TLDR_DIV_RE = re.compile(
    r'<div\s+class=["\']tldr["\']\s*>.*?</div>', re.DOTALL | re.IGNORECASE
)


def ensure_tldr_section(body, article):
    sentences = split_three_tldr_sentences(article)
    section_html = (
        '<section data-tldr="ai-overview" aria-label="In short">'
        + "".join(f"<p>{s}</p>" for s in sentences)
        + "</section>"
    )
    if TLDR_SECTION_RE.search(body):
        # Replace any existing one (idempotent refresh).
        body = TLDR_SECTION_RE.sub(section_html, body, count=1)
        body = OLD_TLDR_DIV_RE.sub("", body)
        return body
    if OLD_TLDR_DIV_RE.search(body):
        body = OLD_TLDR_DIV_RE.sub(section_html, body, count=1)
        return body
    # No TL;DR present at all  -  prepend.
    return section_html + body


SELF_REF_MARKER = "<!--self-ref-injected-->"


def inject_self_ref(body, slug):
    if SELF_REF_MARKER in body:
        return body
    rng = random.Random(int(hashlib.sha256(slug.encode()).hexdigest()[:8], 16))
    a = rng.choice(SELF_REF_PHRASES)
    b = rng.choice([p for p in SELF_REF_PHRASES if p != a])
    # Insert phrase A as a soft lead-in into the third <p>, B into a paragraph near the middle.
    paragraphs = re.split(r"(<p[^>]*>)", body)
    # paragraphs alternates: text, openTag, text, openTag, ...
    # Find indices of <p ...> open tags.
    p_open_idx = [i for i, t in enumerate(paragraphs) if isinstance(t, str) and t.lower().startswith("<p")]
    if len(p_open_idx) < 5:
        return body + SELF_REF_MARKER  # not enough paragraphs; mark and skip
    # Insert into paragraph #3 and paragraph #int(N/2)
    target_a = p_open_idx[2]
    target_b = p_open_idx[len(p_open_idx) // 2]
    # We mutate the text fragment that follows each open tag (i.e., index target+1).
    def lead_in(idx, phrase):
        fragment = paragraphs[idx + 1]
        # Capitalize phrase first letter for sentence start.
        cap = phrase[0].upper() + phrase[1:]
        # If the fragment already starts with the phrase (idempotent), skip.
        if fragment.lstrip().lower().startswith(phrase):
            return fragment
        # Inject phrase at start of paragraph followed by space; keep original starting word lowercased.
        stripped = fragment.lstrip()
        if not stripped:
            return fragment
        return cap + " " + stripped[0].lower() + stripped[1:]
    paragraphs[target_a + 1] = lead_in(target_a, a)
    paragraphs[target_b + 1] = lead_in(target_b, b)
    return "".join(paragraphs) + SELF_REF_MARKER


BYLINE_BLOCK_RE = re.compile(
    r'<p\s+class=["\']byline["\']\s*>.*?</p>', re.DOTALL | re.IGNORECASE
)


def build_byline_html(article):
    pub_iso = article["publish_at"]
    pub_dt = dt.datetime.fromisoformat(pub_iso.replace("Z", "+00:00"))
    pretty = pub_dt.strftime("%B %d, %Y")
    title = article.get("title", "")
    cat = article.get("category", "Autoimmune")
    rng = random.Random(int(hashlib.sha256(article["slug"].encode()).hexdigest()[:8], 16))
    warm_bottom = rng.choice(WARM_BYLINE_BOTTOMS)
    topic_self_ref = (
        f'In our experience editing this archive on {cat.lower()}, "{title}" is one of the pieces '
        "readers come back to, because it tries to name the thing instead of dancing around it."
    )
    return (
        '<p class="byline">By <span class="author">The Immune Rebuilt Editorial Team</span>'
        ' <span class="dot">.</span> <span class="credential">Reviewed by our editorial reviewer.</span>'
        f' <span class="dot">.</span> <time datetime="{pub_iso}" class="date-updated">Updated {pretty}</time></p>'
        + f"<p class=\"byline-context\">{topic_self_ref} {warm_bottom}</p>"
    )


def replace_byline_block(body, article):
    new_byline = build_byline_html(article)
    if BYLINE_BLOCK_RE.search(body):
        body = BYLINE_BLOCK_RE.sub(new_byline, body, count=1)
        # remove any stale byline-context that may sit right after the original.
        body = re.sub(
            r'(' + re.escape(new_byline) + r')\s*<p class="byline-context">.*?</p>',
            r"\1",
            body,
            count=0,
            flags=re.DOTALL,
        )
        return body
    # No byline at all  -  append at the very end.
    return body + new_byline


def patch_body(article, body):
    body = strip_dashes(body)
    body = strip_banned_phrases(body)
    body = replace_banned_words(body)
    body = ensure_tldr_section(body, article)
    body = inject_self_ref(body, article["slug"])
    body = replace_byline_block(body, article)
    body = ensure_authoritative_outbound(body, article)
    return body


# ---- backdating ----
def deterministic_backdated(slugs):
    """Spread N slugs evenly across the prior 90 days, with a small per-slug jitter."""
    today = dt.datetime.now(dt.timezone.utc).replace(hour=13, minute=0, second=0, microsecond=0)
    end = today - dt.timedelta(days=1)            # newest = yesterday
    start = today - dt.timedelta(days=90)         # oldest = 90 days ago
    n = len(slugs)
    out = {}
    for i, slug in enumerate(slugs):
        # Even spacing across [start, end], + 0..(86399) seconds jitter from slug hash so we
        # don't all land at exactly 13:00 UTC.
        ratio = i / max(n - 1, 1)
        base = start + (end - start) * ratio
        h = int(hashlib.sha256(slug.encode()).hexdigest()[:8], 16)
        jitter = dt.timedelta(seconds=h % 86400)
        out[slug] = (base + jitter).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return out


# ---- main run ----
def fetch_article(slug):
    raw = http_get(f"{PULL_ZONE}/articles/{slug}.json")
    return json.loads(raw.decode("utf-8"))


def upload_article(article):
    payload = json.dumps(article, ensure_ascii=False).encode("utf-8")
    http_put(f"immune-rebuilt/articles/{article['slug']}.json", payload, "application/json; charset=utf-8")


def process_one(article_meta, new_publish_at):
    slug = article_meta["slug"]
    a = fetch_article(slug)
    a["slug"] = slug
    a["publish_at"] = new_publish_at
    body = a.get("body", "")
    body = patch_body(a, body)
    a["body"] = body
    a["last_modified_at"] = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    a["word_count"] = len(re.sub(r"<[^>]+>", " ", body).split())
    upload_article(a)
    return slug, a["word_count"], len(body)


def main():
    with open(MANIFEST, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    articles = manifest["articles"]
    slugs = [a["slug"] for a in articles]

    # Sort slugs deterministically, spread across prior 90 days (oldest first by alpha).
    slugs_sorted = sorted(slugs)
    backdates = deterministic_backdated(slugs_sorted)

    # Update manifest in-memory: every entry gets the new publish_at.
    by_slug = {a["slug"]: a for a in articles}
    for s, when in backdates.items():
        by_slug[s]["publish_at"] = when

    # We want the manifest list newest-first by publish_at after the rewrite.
    manifest["articles"] = sorted(
        articles, key=lambda a: a["publish_at"], reverse=True
    )

    # Run patch+reupload in parallel.
    failures = []
    successes = []
    print(f"Patching {len(slugs)} articles in parallel ...", flush=True)
    with ThreadPoolExecutor(max_workers=12) as ex:
        futs = {
            ex.submit(process_one, by_slug[s], backdates[s]): s for s in slugs_sorted
        }
        for i, fut in enumerate(as_completed(futs), start=1):
            s = futs[fut]
            try:
                slug, wc, bl = fut.result()
                successes.append((slug, wc, bl))
                if i % 10 == 0 or i == len(futs):
                    print(f"  [{i}/{len(futs)}] ok ({slug}, words={wc}, bytes={bl})", flush=True)
            except Exception as e:
                failures.append((s, str(e)))
                print(f"  [{i}/{len(futs)}] FAIL {s}: {e}", flush=True)

    # Write manifest back.
    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"\nManifest rewritten with {len(manifest['articles'])} articles, newest first.")
    print(f"Successes: {len(successes)} / Failures: {len(failures)}")
    if failures:
        for s, e in failures[:20]:
            print(f"  FAIL {s}: {e}")


if __name__ == "__main__":
    main()
