# 500-article one-time pre-seed — Immune Rebuilt

- [ ] Plan 500 distinct slugs across the existing 6 categories, with related-graph + ASIN rotation
- [ ] Generate 500 unique watercolor hero illustrations matching the site palette (light, warm, soft) — parallel batches of 4–5
- [ ] Compress all to WebP and upload to Bunny conscious-elder/immune-rebuilt/articles/
- [ ] Write 500 long-form bodies via DeepSeek (≥1800 words each, in voice, gated by §12 union list)
- [ ] Re-pass any gate-failed body once with corrective prompt; if still failing, mark and skip
- [ ] Insert all 500 into article_queue.json (status='queued') — NOT published
- [ ] Confirm: only the original 30 articles in published manifest; queue holds 500
- [ ] Verify zero Manus runtime/CDN dependency in deployed code
- [ ] Run §22 audit; production build; commit + push to peacefulgeek/immune-rebuilt
- [ ] Emit final §23 report with hashtag

## Railway deploy + 100-cap (one-time)
- [ ] Add `railway.json` and `nixpacks.toml` for Railway build/start
- [ ] Add `Procfile` for Railway worker discovery
- [ ] Reshape preview-manifest.json: cap at 100 published
- [ ] Promote 70 best slugs from queue to published (total = 30 + 70 = 100)
- [ ] Demote nothing FROM the original 30 (they stay published)
- [ ] Update bulk-seed.mjs to honor PUBLISH_CAP=100 env
- [ ] Update cron-publish.mjs to refuse to exceed PUBLISH_CAP (extra safety)
- [ ] Re-run §22 audit (expect 22/22 green; published=100, queued=430)
- [ ] Production build clean
- [ ] Commit + push to peacefulgeek/immune-rebuilt
- [ ] Emit §23 + Railway report block with hashtag


---

# Production hardening — round 2

## Phase 1 — Strip TL;DR
- [ ] Re-run scripts/strip-tldr.py against all 530 articles on Bunny
- [ ] Verify a random sample of 10 published + 10 queued: no `tldr` div, no `<strong>TL;DR</strong>`, no bare "TL;DR." text
- [ ] Update local manifest if any TL;DR text was duplicated into excerpt fields

## Phase 2 — Apothecary (100-200 items, ASIN triple-verified)
- [ ] Inventory current /apothecary page items + their ASINs
- [ ] Verify every ASIN with Amazon HTTP 200 + product title scrape (3 retries each)
- [ ] Replace any 404 ASINs with current live alternatives
- [ ] Confirm every URL is `https://www.amazon.com/dp/<ASIN>?tag=spankyspinola-20`
- [ ] Expand list to 150 items (herbs, supplements, TCM, tinctures, adaptogens)
- [ ] Persist as Bunny JSON (no DB)

## Phase 3 — Article QA
- [ ] Loop 100 published articles: strip weird chars, fix double spaces, normalize em-dashes
- [ ] Ensure each has a single, healthy byline block
- [ ] Break paragraphs > 90 words into sub-paragraphs
- [ ] Verify word count 1800-2500 — flag and regenerate any outside band
- [ ] Verify hero image: SHA-256 set has 100 unique entries (zero dup heroes across 100)
- [ ] Re-upload cleaned JSONs to Bunny

## Phase 4 — Gated queue
- [ ] Count current queue manifest items
- [ ] If < 400, generate the delta (target: 430 queued)
- [ ] Each new article: unique custom hero (sha-256 verified), 1800-2500 words
- [ ] Status = `queued`, publish_at scheduled daily after current last publish_at
- [ ] Upload bodies + heroes to Bunny

## Phase 5 — Code path verification
- [ ] Confirm src/lib/repo.mjs reads from manifest+Bunny (no DB required)
- [ ] Confirm cron-publish.mjs daily 13:00 UTC ticks one queue→published, respects PUBLISH_CAP
- [ ] Confirm scripts/start-with-cron.mjs spawns the cron child and registers global error handlers
- [ ] Confirm no Manus runtime dependencies in package.json
- [ ] Confirm /healthz, /sitemap.xml (108 urls), /llms.txt (100 entries), /api/articles, /api/articles/<slug>

## Phase 6 — Final + push
- [ ] 10x audit
- [ ] commit + push to peacefulgeek/immune-rebuilt
- [ ] webdev_save_checkpoint
- [ ] Concise report



---

# Final-Pass Scope — BacklinkWebsites

Status legend: `[ ]` todo · `[~]` doing · `[x]` FIXED · `[V]` VERIFIED ALREADY GOOD · `[B]` BLOCKED + reason

## §1 Engine — Claude
- [ ] Add `CLAUDE_API_KEY` to .env.example + RAILWAY-ENV.md (placeholder; do NOT commit live key)
- [ ] Replace DeepSeek calls with Claude `claude-sonnet-4-6` everywhere (engine.mjs, refresh, rewrite)
- [ ] Engine guard accepts `api.anthropic.com` and rejects others when CLAUDE_API_KEY is set

## §2 Voice rules across 100 published article bodies
- [ ] Strip em-dashes (— and –) → " - "
- [ ] Replace banned single words (case-insensitive) with non-banned synonyms
- [ ] Strip banned filler phrases verbatim
- [ ] Verify ≥2 conversational openers per article (first 3 paragraphs)

## §3 E-E-A-T per article
- [ ] TL;DR `<section data-tldr="ai-overview" aria-label="In short">` 3 sentences ≤32 words each
- [ ] ≥1 self-referencing phrase woven into body
- [ ] ≥3 internal links with varied anchors in prose
- [ ] ≥1 outbound link `rel="nofollow noopener" target="_blank"` to .gov/.edu/NIH/CDC/WHO/PubMed/Nature/ScienceDirect
- [ ] Visible last-updated date in byline w/ datetime attribute
- [ ] Bottom byline block w/ credential, datetime, 1-2 warm self-ref sentences

## §4 AEO / SSR head + JSON-LD
- [ ] Canonical w/ UTM/fbclid/gclid/mc_eid stripped
- [ ] Robots meta `index,follow,max-snippet:-1,max-image-preview:large,max-video-preview:-1`
- [ ] OG + Twitter card per page (twitter:card=summary_large_image)
- [ ] Article JSON-LD per article (incl. SpeakableSpecification → TL;DR)
- [ ] BreadcrumbList JSON-LD per article
- [ ] FAQPage JSON-LD if real Q-shaped headings (cap 6)
- [ ] HowTo JSON-LD if ordered steps (mutually exclusive w/ MedicalCondition)
- [ ] WebSite JSON-LD + SearchAction on home
- [ ] Organization JSON-LD sitewide
- [ ] AboutPage + Organization on /about
- [ ] CollectionPage + ItemList on /articles
- [ ] Person JSON-LD for author
- [ ] All head + JSON-LD server-rendered before React shell

## §5 Routes
- [ ] /sitemap.xml: all published, ISO-8601 lastmod, newest first
- [ ] /robots.txt: GPTBot, ChatGPT-User, OAI-SearchBot, ClaudeBot, Claude-Web, anthropic-ai, PerplexityBot, Perplexity-User, Google-Extended, Bingbot, CCBot, Applebot, Applebot-Extended, DuckAssistBot, Meta-ExternalAgent, YouBot, MistralAI-User, Cohere-AI; sitemap+llms advertised at bottom
- [ ] /llms.txt: markdown index of all published articles, by category
- [ ] /llms-full.txt: full corpus, frontmatter-delimited

## §6 Storage
- [ ] Confirm articles stored as JSON on Bunny only (no DB body)
- [ ] DB schema doc updated to: slug, status, published_at, queued_at, last_modified_at, hero_url, category, tags, asins_used, bunny_url

## §7 Counts + dates
- [ ] 30-100 published / 400-500 queued (currently 100/430 ✓)
- [ ] Backdate published_at across prior 3 months

## §8 Quarterly refresh cron
- [ ] Calls Claude, runs quality gate, updates Bunny + byline date + dateModified

## §9 Bylines
- [ ] Every article: warm credential line + datetime matching published_at + 1-2 warm self-ref sentences specific to topic

## §10 Leakage
- [ ] Zero `paulwagner.com` or `Paul Wagner` references anywhere

## §11 Validation
- [ ] curl GPTBot UA confirms head + JSON-LD before `<div id="root">`
- [ ] /sitemap.xml 200 + only published
- [ ] /llms.txt 200 + Content-Type text/markdown
- [ ] /robots.txt 200 + names every AI crawler
- [ ] Sample article passes Schema.org shape

## §12 Push
- [ ] Commit + force-push to peacefulgeek/immune-rebuilt
- [ ] Deliver FIXED/VERIFIED/BLOCKED report
