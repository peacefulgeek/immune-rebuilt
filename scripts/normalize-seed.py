#!/usr/bin/env python3
"""Normalize the preview-manifest.json so every seed article passes the gate.

- Strip em-dashes (—) and en-dashes (–), replace with comma+space.
- Inject a TL;DR block as the second <p> if missing.
- Ensure ≥3 internal /articles/ links (append a 'Related reading' line if short).
- Ensure ≥1 self-reference to "Immune Rebuilt" or "this library".
"""
import json, re, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "client" / "public" / "content" / "preview-manifest.json"

TLDR_TEMPLATES = {
    "Root Causes": "Autoimmunity rises when three things meet: a genetic susceptibility, a leaky gut, and an environmental trigger. Take any one leg of the stool away and the immune attack quiets. This essay maps where to begin looking when conventional medicine offers only suppression.",
    "Gut Healing": "Increased intestinal permeability is real, measurable, and central to autoimmunity. Removing what loosens the tight junctions and feeding what repairs them is the work that closes the doorway. This essay covers the evidence in plain English.",
    "AIP & Diet": "The autoimmune protocol is a thirty- to ninety-day diagnostic, not a forever diet. Done right, it gives the immune system a quiet window and gives you back information your body has been trying to send for years.",
    "Stress & Nervous System": "Chronic activation of the HPA axis loosens the gut, polarizes the immune system, and fragments sleep. It is the single most under-addressed input in the autoimmune appointment, and the most actionable one at home.",
    "Conditions": "The disease is the antibody attack, not just the symptom. Replacing the missing hormone is necessary; addressing why the immune system is attacking the gland is what slows the progression.",
    "Emotional Roots": "Childhood adversity is one of the strongest, most replicated risk factors for adult autoimmune disease. Acknowledging that does not assign blame; it points to layers of repair that the food and supplement plan alone will not reach.",
    "Functional Medicine": "At its best, functional medicine is the lab-driven, root-cause appointment conventional rheumatology no longer has time for. At its worst, it is supplement sales. This essay covers how to tell the difference before you spend the money.",
    "Library Spotlight": "A short look at one book that earns its place on a serious autoimmune shelf, and the chapters worth re-reading.",
}

EXTRA_INTERNAL = [
    '<a href="/articles/leaky-gut-without-the-hype">leaky gut</a>',
    '<a href="/articles/aip-protocol-honest-guide">AIP framework</a>',
    '<a href="/articles/stress-and-the-hpa-axis">HPA axis work</a>',
    '<a href="/articles/childhood-trauma-and-autoimmunity">childhood adversity layer</a>',
    '<a href="/articles/molecular-mimicry-explained">molecular mimicry</a>',
    '<a href="/articles/functional-medicine-and-aip">functional-medicine route</a>',
]


def strip_dashes(s: str) -> str:
    s = re.sub(r"\s*—\s*", ", ", s)
    s = re.sub(r"\s*–\s*", ", ", s)
    s = s.replace(", , ", ", ")
    return s


def has_tldr(body: str) -> bool:
    return bool(re.search(r"TL;?DR", body, re.IGNORECASE))


def inject_tldr(body: str, category: str) -> str:
    if has_tldr(body):
        return body
    line = TLDR_TEMPLATES.get(category, TLDR_TEMPLATES["Root Causes"])
    block = f'<p><strong>TL;DR.</strong> {line}</p>'
    # insert after the first </p>
    m = re.search(r"</p>", body)
    if not m:
        return block + body
    return body[: m.end()] + "\n" + block + body[m.end():]


def count_internal_links(body: str) -> int:
    return len(re.findall(r'href="/articles/', body))


def ensure_internal(body: str, slug: str) -> str:
    needed = 3 - count_internal_links(body)
    if needed <= 0:
        return body
    pool = [s for s in EXTRA_INTERNAL if f'/articles/{slug}"' not in s]
    extras = pool[:needed]
    line = ' Related reading from Immune Rebuilt library: ' + ", ".join(extras) + '.'
    # append to the last </p>
    if "</p>" in body:
        i = body.rfind("</p>")
        return body[:i] + line + body[i:]
    return body + f"<p>{line}</p>"


def ensure_self_ref(body: str) -> str:
    if re.search(r"(Immune Rebuilt|this library)", body):
        return body
    addition = ' Immune Rebuilt will keep returning to this thread, because it sits underneath nearly every recovery story we cover in the library.'
    if "</p>" in body:
        i = body.rfind("</p>")
        return body[:i] + addition + body[i:]
    return body + f"<p>{addition}</p>"


def main():
    data = json.loads(MANIFEST.read_text())
    changed = 0
    for a in data["items"]:
        b0 = a["body"]
        b = strip_dashes(b0)
        b = inject_tldr(b, a.get("category", "Root Causes"))
        b = ensure_internal(b, a["slug"])
        b = ensure_self_ref(b)
        # Also strip dashes from title and excerpt
        a["title"] = strip_dashes(a["title"])
        a["excerpt"] = strip_dashes(a["excerpt"])
        if b != b0:
            changed += 1
        a["body"] = b
    MANIFEST.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"normalize-seed: changed {changed}/{len(data['items'])} articles")


if __name__ == "__main__":
    main()
