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

