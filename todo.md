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
