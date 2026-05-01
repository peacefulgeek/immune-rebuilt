/**
 * Read paths for the public surface. All MUST filter status='published'.
 * Master scope §15C. Any leak here will cause queued articles to surface.
 */
import { getPool, query } from "./db.mjs";

export async function getPublishedArticleBySlug(slug) {
  const p = getPool();
  if (!p) return null;
  const { rows } = await query(
    `SELECT id, slug, title, body, excerpt, category, tags,
            hero_url, asins_used, word_count,
            published_at, last_modified_at, queued_at
     FROM articles
     WHERE slug = $1 AND status = 'published'
     LIMIT 1`,
    [slug]
  );
  return rows[0] || null;
}

/**
 * @param {{ limit?: number, category?: string, includeBody?: boolean }} [opts]
 */
export async function listPublishedArticles(opts = {}) {
  const { limit = 60, category, includeBody = false } = opts;
  const p = getPool();
  if (!p) return [];
  const params = [];
  let where = `status = 'published'`;
  if (category) {
    params.push(category);
    where += ` AND category = $${params.length}`;
  }
  params.push(limit);

  const cols = includeBody
    ? `slug, title, excerpt, body, category, tags, hero_url, published_at, last_modified_at`
    : `slug, title, excerpt, category, tags, hero_url, published_at, last_modified_at`;
  const { rows } = await query(
    `SELECT ${cols}
     FROM articles WHERE ${where}
     ORDER BY published_at DESC NULLS LAST
     LIMIT $${params.length}`,
    params
  );
  return rows;
}

export async function listPublishedForSitemap() {
  const p = getPool();
  if (!p) return [];
  const { rows } = await query(
    `SELECT slug, last_modified_at, published_at, category
     FROM articles WHERE status = 'published'
     ORDER BY published_at DESC NULLS LAST`
  );
  return rows;
}

export async function searchPublishedArticles(q, { limit = 60 } = {}) {
  const p = getPool();
  if (!p) return [];
  const like = `%${q.replace(/[%_]/g, (c) => "\\" + c)}%`;
  const { rows } = await query(
    `SELECT slug, title, excerpt, category, tags, hero_url, published_at
     FROM articles WHERE status = 'published'
       AND (title ILIKE $1 OR excerpt ILIKE $1 OR body ILIKE $1)
     ORDER BY published_at DESC NULLS LAST
     LIMIT $2`,
    [like, limit]
  );
  return rows;
}

export async function countPublished() {
  const p = getPool();
  if (!p) return 0;
  const { rows } = await query(`SELECT count(*)::int AS c FROM articles WHERE status = 'published'`);
  return rows[0]?.c || 0;
}

export async function countQueued() {
  const p = getPool();
  if (!p) return 0;
  const { rows } = await query(`SELECT count(*)::int AS c FROM articles WHERE status = 'queued'`);
  return rows[0]?.c || 0;
}

export async function publishHistogramByDay() {
  const p = getPool();
  if (!p) return [];
  const { rows } = await query(
    `SELECT date_trunc('day', published_at)::date AS day, count(*)::int AS c
     FROM articles WHERE status = 'published'
     GROUP BY 1 ORDER BY 1 DESC LIMIT 30`
  );
  return rows;
}
