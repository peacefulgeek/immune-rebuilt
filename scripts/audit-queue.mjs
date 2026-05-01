// Lightweight queue audit. Useful for ops.
import { getPool, query } from "../src/lib/db.mjs";
async function main() {
  const pool = getPool();
  if (!pool) { console.log("[audit-queue] no DB"); return; }
  const { rows } = await query(
    `SELECT status, count(*)::int AS c
       FROM article_queue GROUP BY status ORDER BY status`
  );
  for (const r of rows) console.log(r.status.padEnd(12), r.c);
  const { rows: l } = await query(
    `SELECT created_at, slug, action, detail FROM publish_log ORDER BY created_at DESC LIMIT 20`
  );
  console.log("\nrecent log:");
  for (const r of l) console.log(r.created_at.toISOString(), r.slug, r.action);
}
main().catch(e => { console.error(e); process.exit(1); });
