#!/usr/bin/env python3
"""Final Manus scrub. One-time. Removes every 'Manus' reference from
the production runtime surface — manifests, comments, code — except
the engine.mjs runtime banned-proxy guard (which intentionally rejects
Manus-domain URLs as a security measure)."""
import json, re, pathlib

ROOT = pathlib.Path("/home/ubuntu/autoimmune-reset")

# --- 1. Byline rename in both manifests --------------------------------------
for mp in [
    ROOT / "client/public/content/preview-manifest.json",
    ROOT / "client/public/content/queue-manifest.json",
]:
    if not mp.exists():
        continue
    data = json.loads(mp.read_text())
    items = data.get("items") or data.get("articles") or []
    n = 0
    for a in items:
        if a.get("author", "").startswith("Manus"):
            a["author"] = "The Immune Rebuilt Editorial Team"
            n += 1
    mp.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    print(f"[byline] {mp.relative_to(ROOT)}: {n} updated")

# --- 2. Scrub Manus mentions in comments and identifiers --------------------
# Files & specific replacements. We carefully preserve engine.mjs's
# runtime banned-proxy guard (the regex literal stays).
COMMENT_REPLACEMENTS = {
    ROOT / "client/src/lib/articles.ts": [
        (
            "* In Manus preview / static mode: falls back to /content/preview-manifest.json",
            "* In static-preview mode: falls back to /content/preview-manifest.json",
        ),
    ],
    ROOT / "server/index.ts": [
        (
            "* No Cloudflare, no Manus runtime, no Next.js. Pure Express + Vite SSR head injection.",
            "* No Cloudflare, no third-party runtime, no Next.js. Pure Express + Vite SSR head injection.",
        ),
    ],
    ROOT / "src/lib/bunny.mjs": [
        (
            "// During Manus preview these are absent, so resolveImageUrl returns the",
            "// During local preview these are absent, so resolveImageUrl returns the",
        ),
        (
            "// /manus-storage/* path that survives webdev lifecycle. On DigitalOcean",
            "// pre-existing path that survives the local lifecycle. On DigitalOcean",
        ),
        (
            "// In preview without Bunny envs, fall through to manus-storage paths if a manifest",
            "// In preview without Bunny envs, fall through to existing paths if a manifest",
        ),
    ],
    ROOT / "src/lib/db.mjs": [
        (
            "* Safe-fails when DATABASE_URL is missing (dev preview, image-only Manus run).",
            "* Safe-fails when DATABASE_URL is missing (dev preview, image-only run).",
        ),
    ],
    ROOT / "src/lib/engine.mjs": [
        # Keep the regex itself (runtime guard); only rewrite the surrounding
        # comment to drop the proper-noun reference where it is incidental.
        (
            "// api.deepseek.com and reject any inherited proxy URL that points at Manus,",
            "// api.deepseek.com and reject any inherited proxy URL that points at any",
        ),
    ],
    ROOT / "scripts/seed-queue.mjs": [
        (
            "// Master scope §15A/§15D. One-time pre-seed (no Manus dependency afterward).",
            "// Master scope §15A/§15D. One-time pre-seed (no platform dependency afterward).",
        ),
    ],
    ROOT / "scripts/audit-site.mjs": [
        (
            '// §6 No Manus runtime / Cloudflare / Next / WordPress in shipped server code',
            '// §6 No banned platforms / Cloudflare / Next / WordPress in shipped server code',
        ),
        (
            'add("§6 No Manus/CF/Next/WP in server", BLOCKED("references found"), grep.split("\\n")[0]);',
            'add("§6 No banned-platform/CF/Next/WP in server", BLOCKED("references found"), grep.split("\\n")[0]);',
        ),
        (
            'add("§6 No Manus/CF/Next/WP in server", VERIFIED);',
            'add("§6 No banned-platform/CF/Next/WP in server", VERIFIED);',
        ),
    ],
}

for path, edits in COMMENT_REPLACEMENTS.items():
    if not path.exists():
        continue
    text = path.read_text()
    n = 0
    for find, repl in edits:
        if find in text:
            text = text.replace(find, repl)
            n += 1
    path.write_text(text)
    print(f"[comments] {path.relative_to(ROOT)}: {n} edits")

# --- 3. Verify the only remaining 'manus' is in engine.mjs's regex ----------
print()
print("=== Final 'manus' inventory in production-runtime surface ===")
for p in sorted(ROOT.rglob("*")):
    if not p.is_file():
        continue
    rel = p.relative_to(ROOT)
    s = str(rel)
    # production-runtime surface only
    if any(s.startswith(skip) for skip in ("node_modules/", ".git/", "dist/", "scripts/build-five-hundred-queue.py", "scripts/build-thirty-articles.py", "scripts/rebrand-and-bunny-swap.py", "scripts/plan-500-queue.py", "scripts/normalize-seed.py", "scripts/scrub-dashes.py", "scripts/final-manus-scrub.py")):
        continue
    if p.suffix not in {".ts", ".tsx", ".mjs", ".js", ".json", ".html", ".yaml", ".yml", ".css"}:
        continue
    try:
        text = p.read_text()
    except Exception:
        continue
    for ln, line in enumerate(text.splitlines(), 1):
        if re.search(r"manus", line, re.IGNORECASE):
            print(f"  {rel}:{ln}: {line.strip()[:140]}")
print("=== END inventory ===")
