// Monthly freshness pass: bump last_modified_at on the oldest 5% of published articles
// AND re-run the gate; flag any new banned hits as a 'refresh_needed' publish_log entry.
// Master scope §14C.
import { getPool, query } from "../src/lib/db.mjs";
import { checkText } from "../src/lib/gate.mjs";

async function main() {
  const pool = getPool();
  if (!pool) { console.log("[refresh-monthly] no DB"); return; }
  const { rows } = await query(
    `SELECT slug, title, body FROM articles
      WHERE status='published'
      ORDER BY last_modified_at ASC
      LIMIT GREATEST(1, (SELECT count(*)/20 FROM articles WHERE status='published'))`
  );
  let touched = 0, flagged = 0;
  for (const r of rows) {
    const g = checkText(r.body || "");
    if (!g.ok) {
      await query(`INSERT INTO publish_log (slug, action, detail) VALUES ($1,'refresh_needed',$2)`,
        [r.slug, JSON.stringify({ reasons: g.reasons })]);
      flagged++;
    } else {
      await query(`UPDATE articles SET last_modified_at=NOW() WHERE slug=$1`, [r.slug]);
      touched++;
    }
  }
  console.log(`[refresh-monthly] touched=${touched} flagged=${flagged}`);
}
main().catch(e => { console.error(e); process.exit(1); });
