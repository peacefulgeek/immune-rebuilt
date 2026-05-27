// Bulk seed from client/public/content/preview-manifest.json into Postgres.
// Idempotent: ON CONFLICT (slug) DO UPDATE. Master scope §15D.

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { getPool, query } from "../src/lib/db.mjs";
import { checkText } from "../src/lib/gate.mjs";
import { fetchArticleJson } from "../src/lib/bunny.mjs";

async function hydrateBody(a) {
  if (a.body && String(a.body).length > 0) return a.body;
  if (a.body_url) {
    const j = await fetchArticleJson(a.body_url);
    if (j && j.body) return j.body;
  }
  return "";
}

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const MANIFEST = path.resolve(__dirname, "..", "client", "public", "content", "preview-manifest.json");

async function main() {
  const pool = getPool();
  if (!pool) {
    console.log("[seed] DATABASE_URL not set — skipping (preview/dev mode).");
    return;
  }

  const raw = fs.readFileSync(MANIFEST, "utf8");
  const manifest = JSON.parse(raw);
  let items = manifest.articles || manifest.items || [];
  const CAP = Number(process.env.PUBLISH_CAP || 100);
  if (items.length > CAP) {
    console.log(`[seed] capping publishes at PUBLISH_CAP=${CAP} (manifest has ${items.length})`);
    items = items.slice(0, CAP);
  }
  console.log(`[seed] ${items.length} articles will be seeded as published (cap=${CAP})`);

  let inserted = 0, updated = 0, skipped = 0;

  for (const a of items) {
    const body = await hydrateBody(a);
    const gate = checkText(body || "");
    // Seed entries are pre-vetted; we still record gate meta. We do NOT block seed
    // on internal-link counts because the manifest is the canonical seed source.
    const wc = a.word_count || (String(body || "").split(/\s+/).length);
    const r = await query(
      `INSERT INTO articles (slug, title, category, tags, excerpt, body,
                             hero_url, word_count, status, published_at,
                             queued_at, last_modified_at, asins_used, gate_meta)
       VALUES ($1,$2,$3,$4,$5,$6,$7,$8,'published',$9,$10,$11,$12,$13)
       ON CONFLICT (slug) DO UPDATE SET
         title = EXCLUDED.title,
         category = EXCLUDED.category,
         tags = EXCLUDED.tags,
         excerpt = EXCLUDED.excerpt,
         body = EXCLUDED.body,
         hero_url = EXCLUDED.hero_url,
         word_count = EXCLUDED.word_count,
         published_at = COALESCE(articles.published_at, EXCLUDED.published_at),
         last_modified_at = EXCLUDED.last_modified_at,
         asins_used = EXCLUDED.asins_used,
         gate_meta = EXCLUDED.gate_meta
       RETURNING (xmax = 0) AS was_inserted`,
      [
        a.slug,
        a.title,
        a.category,
        a.tags || [],
        a.excerpt,
        body,
        a.hero_url,
        wc,
        a.published_at,
        a.published_at,
        a.last_modified_at || a.published_at,
        a.asins_used || [],
        JSON.stringify({ gate, source: "manifest" }),
      ]
    );
    if (r.rows[0]?.was_inserted) inserted++; else updated++;
  }

  // Log a publish_log entry summarising the seed run
  await query(
    `INSERT INTO publish_log (slug, action, detail) VALUES ($1, $2, $3)`,
    ["__seed__", "bulk_seed", JSON.stringify({ inserted, updated, total: items.length })]
  );

  console.log(`[seed] inserted=${inserted} updated=${updated} skipped=${skipped}`);
}

main().catch((e) => { console.error("[seed] FAIL", e); process.exit(1); });
