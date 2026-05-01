// Quarterly refresh: pick the oldest article in each category and queue an updated rewrite.
// Master scope §14D.
import { getPool, query } from "../src/lib/db.mjs";

async function main() {
  const pool = getPool();
  if (!pool) { console.log("[refresh-quarterly] no DB"); return; }
  const { rows } = await query(
    `SELECT DISTINCT ON (category) slug, title, category
       FROM articles WHERE status='published'
       ORDER BY category, last_modified_at ASC`
  );
  let queued = 0;
  for (const r of rows) {
    await query(
      `INSERT INTO article_queue (slug, title, category, angle, status, priority)
       VALUES ($1,$2,$3,'quarterly refresh','queued',50)
       ON CONFLICT (slug) DO UPDATE SET status='queued', priority=50, updated_at=NOW()`,
      [r.slug + "-refresh-" + new Date().toISOString().slice(0,7), r.title, r.category]
    );
    queued++;
  }
  console.log(`[refresh-quarterly] queued=${queued}`);
}
main().catch(e => { console.error(e); process.exit(1); });
