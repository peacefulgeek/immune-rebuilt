// Bulk seed of the 500-article pre-seed into article_queue.
// Idempotent: ON CONFLICT (slug) DO NOTHING. Status='queued' so cron drips them.
// Master scope §15A/§15D. One-time pre-seed (no platform dependency afterward).

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { getPool, query } from "../src/lib/db.mjs";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const MANIFEST = path.resolve(
  __dirname, "..", "client", "public", "content", "queue-manifest.json"
);

async function main() {
  const pool = getPool();
  if (!pool) {
    console.log("[queue-seed] DATABASE_URL not set — skipping (preview/dev mode).");
    return;
  }

  if (!fs.existsSync(MANIFEST)) {
    console.log(`[queue-seed] no queue manifest at ${MANIFEST} — skipping.`);
    return;
  }

  const raw = fs.readFileSync(MANIFEST, "utf8");
  const manifest = JSON.parse(raw);
  const items = manifest.items || [];
  console.log(`[queue-seed] ${items.length} queued items in manifest`);

  let inserted = 0, skipped = 0;

  for (const q of items) {
    const r = await query(
      `INSERT INTO article_queue
         (slug, title, category, angle, asins, related_slugs,
          excerpt, body, hero_url, hero_alt,
          scheduled_for, status, priority, attempts, word_count)
       VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,'queued',100,0,$12)
       ON CONFLICT (slug) DO NOTHING
       RETURNING id`,
      [
        q.slug,
        q.title,
        q.category,
        q.excerpt || "",
        q.asins || [],
        q.related || [],
        q.excerpt,
        q.body,
        q.hero_url,
        q.hero_alt || q.title,
        q.publish_at,
        q.word_count || null,
      ]
    );
    if (r.rows.length) inserted++; else skipped++;
  }

  await query(
    `INSERT INTO publish_log (slug, action, detail)
     VALUES ($1, $2, $3)`,
    [
      "__queue_seed__",
      "bulk_queue_seed",
      JSON.stringify({ inserted, skipped, total: items.length }),
    ]
  );

  console.log(`[queue-seed] inserted=${inserted} skipped=${skipped}`);
}

main().catch((e) => {
  console.error("[queue-seed] FAIL", e);
  process.exit(1);
});
