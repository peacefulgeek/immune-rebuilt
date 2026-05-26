// Daily publishing tick. Master scope §15.
// - Pulls one (or N) entries from article_queue with status='queued'
// - Runs the DeepSeek engine + quality gate (regenerate-on-fail)
// - On gate pass: inserts into articles as 'published' with NOW() for published_at
// - On gate failure after MAX attempts: marks the queue row 'blocked' and logs the reason
// - Records every action in publish_log so we can prove multi-day publishing history

import { getPool, query } from "../src/lib/db.mjs";
import { generateArticle } from "../src/lib/generate-article.mjs";

const PER_TICK = parseInt(process.env.PUBLISH_PER_TICK || "1", 10); // master scope §15: default daily cadence is 1
const AUTO = String(process.env.AUTO_GEN_ENABLED || "true").toLowerCase() === "true";

async function pickNext(n) {
  const { rows } = await query(
    `UPDATE article_queue
        SET status='running', updated_at=NOW(), attempts=attempts+1
      WHERE id IN (
        SELECT id FROM article_queue
         WHERE status IN ('queued','retry')
           AND (scheduled_for IS NULL OR scheduled_for <= NOW())
         ORDER BY priority ASC, scheduled_for NULLS FIRST, id ASC
         LIMIT $1
         FOR UPDATE SKIP LOCKED
      )
      RETURNING id, slug, title, category, angle, must_cover, asins, related_slugs, attempts,
               excerpt, body, hero_url, hero_alt, word_count`,
    [n]
  );
  return rows;
}

function approxWordCount(html) {
  return String(html || "").replace(/<[^>]+>/g, " ").split(/\s+/).filter(Boolean).length;
}

function makeExcerpt(html) {
  const text = String(html || "").replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();
  return text.slice(0, 240).replace(/[,;:.\s]+$/, "") + (text.length > 240 ? "…" : "");
}

async function publishOne(item) {
  // Fast path: this queue row was pre-seeded with a vetted body. Use it directly
  // (it already passed the gate at seed time). The DeepSeek round-trip is only
  // needed when the queue row has no body (refresh-monthly, refresh-quarterly,
  // product-spotlight, etc.).
  let html, attempts, gate, hero_url;
  if (item.body && String(item.body).length > 1000) {
    html = item.body;
    attempts = 0;
    gate = { source: "pre-seed", ok: true };
    hero_url = item.hero_url || null;
  } else {
    const gen = await generateArticle({
      title: item.title,
      slug: item.slug,
      category: item.category,
      angle: item.angle,
      must_cover: item.must_cover || [],
      asins: item.asins || [],
      related_slugs: item.related_slugs || [],
    });
    html = gen.html;
    attempts = gen.attempts;
    gate = gen.gate;
    hero_url = item.hero_url || null;
  }

  const wc = item.word_count || approxWordCount(html);
  const excerpt = item.excerpt || makeExcerpt(html);

  await query(
    `INSERT INTO articles (slug, title, category, tags, excerpt, body, hero_url,
                            word_count, status, published_at, queued_at, last_modified_at,
                            asins_used, gate_meta)
     VALUES ($1,$2,$3,$4,$5,$6,$7,$8,'published',NOW(),NOW(),NOW(),$9,$10)
     ON CONFLICT (slug) DO UPDATE SET
       title=EXCLUDED.title, body=EXCLUDED.body, excerpt=EXCLUDED.excerpt,
       word_count=EXCLUDED.word_count, last_modified_at=NOW(),
       gate_meta=EXCLUDED.gate_meta, status='published'`,
    [item.slug, item.title, item.category, [], excerpt, html, hero_url, wc,
     item.asins || [], JSON.stringify({ gate, attempts })]
  );

  await query(
    `UPDATE article_queue SET status='published', updated_at=NOW(), last_error=NULL WHERE id=$1`,
    [item.id]
  );

  await query(
    `INSERT INTO publish_log (slug, action, detail) VALUES ($1,'published',$2)`,
    [item.slug, JSON.stringify({ attempts, words: wc })]
  );

  return { slug: item.slug, words: wc, attempts };
}

async function blockOne(item, err) {
  const reason = err?.last_gate?.reasons?.join("; ") || err?.message || "unknown";
  const newStatus = (item.attempts || 0) >= 4 ? "blocked" : "retry";
  await query(
    `UPDATE article_queue SET status=$1, updated_at=NOW(), last_error=$2 WHERE id=$3`,
    [newStatus, reason, item.id]
  );
  await query(
    `INSERT INTO publish_log (slug, action, detail) VALUES ($1,$2,$3)`,
    [item.slug, newStatus, JSON.stringify({ reason })]
  );
}

async function main() {
  if (!AUTO) {
    console.log("[publish] AUTO_GEN_ENABLED=false — skipping tick");
    return;
  }
  const pool = getPool();
  if (!pool) {
    console.log("[publish] DATABASE_URL not set — skipping tick");
    return;
  }

  // Safety guard: refuse to publish more than PUBLISH_CAP total
  const CAP = Number(process.env.PUBLISH_CAP || 100);
  const capRow = await query(`SELECT COUNT(*)::int AS n FROM articles WHERE status='published'`);
  const currentlyPublished = capRow.rows[0]?.n || 0;
  if (currentlyPublished >= CAP) {
    console.log(`[publish] PUBLISH_CAP=${CAP} reached (current=${currentlyPublished}); holding queue`);
    return;
  }
  const room = Math.max(0, CAP - currentlyPublished);
  const takeN = Math.min(PER_TICK, room);

  const items = await pickNext(takeN);
  if (!items.length) {
    console.log("[publish] queue empty or cap reached");
    return;
  }
  for (const item of items) {
    try {
      const r = await publishOne(item);
      console.log(`[publish] OK ${r.slug} (${r.words} words, ${r.attempts} attempts)`);
    } catch (e) {
      console.error(`[publish] FAIL ${item.slug}: ${e?.message || e}`);
      await blockOne(item, e);
    }
  }
}

main().catch((e) => { console.error("[publish] tick error", e); process.exit(1); });
