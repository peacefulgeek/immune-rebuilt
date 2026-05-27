/**
 * Read paths for the public surface. All MUST filter status='published'.
 * Master scope §15C. Any leak here will cause queued articles to surface.
 *
 * Two-tier read strategy (fixes the empty-site failure mode):
 *   1. If a Postgres pool is configured AND has rows, read from DB.
 *   2. Else, fall back to the slim manifest at
 *      client/public/content/preview-manifest.json (which Vite copies into
 *      dist/public/content/) + hydrate bodies from Bunny on demand.
 *
 * This means the site renders 100 published articles immediately on first
 * boot — even before bulk-seed.mjs has populated Postgres, even if
 * DATABASE_URL is misconfigured, even if the DB is unreachable.
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { getPool, query } from "./db.mjs";
import { fetchArticleJsonCached } from "./bunny.mjs";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// ── Manifest loader (cached for process lifetime; manifest is shipped at build time)
let _manifestCache = null;
function loadManifest() {
  if (_manifestCache) return _manifestCache;
  const cwd = process.cwd();
  // The bundled server lives at dist/index.js; __dirname there is the dist/ folder.
  // Source __dirname is src/lib/. Cover every plausible location.
  const candidates = [
    // bundled server: dist/index.js → dist/public/content/...
    path.resolve(__dirname, "public", "content", "preview-manifest.json"),
    // run-from-repo-root
    path.resolve(cwd, "dist", "public", "content", "preview-manifest.json"),
    path.resolve(cwd, "client", "public", "content", "preview-manifest.json"),
    // source __dirname (src/lib) → ../../dist/...
    path.resolve(__dirname, "..", "..", "dist", "public", "content", "preview-manifest.json"),
    path.resolve(__dirname, "..", "..", "client", "public", "content", "preview-manifest.json"),
    // dist/index.js → ../client/...
    path.resolve(__dirname, "..", "client", "public", "content", "preview-manifest.json"),
  ];
  for (const p of candidates) {
    if (fs.existsSync(p)) {
      try {
        const raw = fs.readFileSync(p, "utf8");
        const j = JSON.parse(raw);
        const items = Array.isArray(j?.articles) ? j.articles : Array.isArray(j?.items) ? j.items : [];
        _manifestCache = items.filter((a) => a && a.slug);
        console.log(`[repo] manifest loaded from ${p} — ${_manifestCache.length} articles`);
        return _manifestCache;
      } catch (e) {
        console.error(`[repo] manifest parse failed at ${p}:`, e?.message || e);
      }
    }
  }
  console.warn("[repo] no manifest found in dist/ or client/ — fallback will be empty");
  _manifestCache = [];
  return _manifestCache;
}

// ── Manifest → row shape used by the rest of the app
function manifestToRow(a, { includeBody = false, body = null } = {}) {
  const row = {
    id: a.slug,
    slug: a.slug,
    title: a.title,
    excerpt: a.excerpt || "",
    category: a.category || "",
    category_slug: a.category_slug || "",
    tags: a.tags || [],
    hero_url: a.hero_url || "",
    asins_used: a.asins || a.asins_used || [],
    word_count: a.word_count || 0,
    published_at: a.publish_at || a.published_at || null,
    last_modified_at: a.last_modified_at || a.publish_at || a.published_at || null,
    queued_at: a.queued_at || null,
    status: a.status || "published",
    body_url: a.body_url || "",
  };
  if (includeBody) row.body = body || "";
  return row;
}

async function manifestPublished({ category, limit, includeBody, slug } = {}) {
  let items = loadManifest().filter((a) => (a.status || "published") === "published");
  if (slug) items = items.filter((a) => a.slug === slug);
  if (category) items = items.filter((a) => a.category === category || a.category_slug === category);
  // Sort newest first by published date
  items.sort((a, b) => {
    const ta = Date.parse(a.publish_at || a.published_at || 0) || 0;
    const tb = Date.parse(b.publish_at || b.published_at || 0) || 0;
    return tb - ta;
  });
  if (typeof limit === "number") items = items.slice(0, limit);
  if (!includeBody) return items.map((a) => manifestToRow(a));
  // Hydrate bodies from Bunny in parallel (capped at 8 in flight to avoid storms)
  const out = [];
  const concurrency = 8;
  for (let i = 0; i < items.length; i += concurrency) {
    const chunk = items.slice(i, i + concurrency);
    const bodies = await Promise.all(
      chunk.map(async (a) => {
        if (!a.body_url) return "";
        const j = await fetchArticleJsonCached(a.body_url);
        return j?.body || "";
      })
    );
    chunk.forEach((a, idx) => out.push(manifestToRow(a, { includeBody: true, body: bodies[idx] })));
  }
  return out;
}

// ── Public read API ──────────────────────────────────────────────────────────

export async function getPublishedArticleBySlug(slug) {
  const p = getPool();
  if (p) {
    try {
      const { rows } = await query(
        `SELECT id, slug, title, body, excerpt, category, tags,
                hero_url, asins_used, word_count,
                published_at, last_modified_at, queued_at
         FROM articles
         WHERE slug = $1 AND status = 'published'
         LIMIT 1`,
        [slug]
      );
      if (rows[0]) return rows[0];
    } catch (e) {
      console.warn("[repo] DB read failed for slug; falling back to manifest:", e?.message || e);
    }
  }
  // Manifest+Bunny fallback (always populated)
  const items = await manifestPublished({ slug, includeBody: true, limit: 1 });
  return items[0] || null;
}

/**
 * @param {{ limit?: number, category?: string, includeBody?: boolean }} [opts]
 */
export async function listPublishedArticles(opts = {}) {
  const { limit = 60, category, includeBody = false } = opts;
  const p = getPool();
  if (p) {
    try {
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
      if (rows.length) return rows;
    } catch (e) {
      console.warn("[repo] DB list failed; falling back to manifest:", e?.message || e);
    }
  }
  return manifestPublished({ category, limit, includeBody });
}

export async function listPublishedForSitemap() {
  const p = getPool();
  if (p) {
    try {
      const { rows } = await query(
        `SELECT slug, last_modified_at, published_at, category
         FROM articles WHERE status = 'published'
         ORDER BY published_at DESC NULLS LAST`
      );
      if (rows.length) return rows;
    } catch (e) {
      console.warn("[repo] DB sitemap read failed; falling back:", e?.message || e);
    }
  }
  // Manifest fallback — return the same shape
  return manifestPublished({ limit: 1000 }).then((rows) =>
    rows.map((r) => ({
      slug: r.slug,
      last_modified_at: r.last_modified_at,
      published_at: r.published_at,
      category: r.category,
    }))
  );
}

export async function searchPublishedArticles(q, { limit = 60 } = {}) {
  const p = getPool();
  if (p) {
    try {
      const like = `%${q.replace(/[%_]/g, (c) => "\\" + c)}%`;
      const { rows } = await query(
        `SELECT slug, title, excerpt, category, tags, hero_url, published_at
         FROM articles WHERE status = 'published'
           AND (title ILIKE $1 OR excerpt ILIKE $1 OR body ILIKE $1)
         ORDER BY published_at DESC NULLS LAST
         LIMIT $2`,
        [like, limit]
      );
      if (rows.length) return rows;
    } catch (e) {
      console.warn("[repo] DB search failed; falling back:", e?.message || e);
    }
  }
  // Manifest fallback — match title/excerpt/category client-side
  const all = await manifestPublished({ limit: 500 });
  const needle = (q || "").toLowerCase();
  if (!needle) return all.slice(0, limit);
  return all
    .filter((r) =>
      r.title?.toLowerCase().includes(needle) ||
      r.excerpt?.toLowerCase().includes(needle) ||
      r.category?.toLowerCase().includes(needle)
    )
    .slice(0, limit);
}

export async function countPublished() {
  const p = getPool();
  if (p) {
    try {
      const { rows } = await query(`SELECT count(*)::int AS c FROM articles WHERE status = 'published'`);
      const c = rows[0]?.c || 0;
      if (c > 0) return c;
    } catch (e) {
      console.warn("[repo] DB count failed; falling back:", e?.message || e);
    }
  }
  return loadManifest().filter((a) => (a.status || "published") === "published").length;
}

export async function countQueued() {
  const p = getPool();
  if (p) {
    try {
      const { rows } = await query(`SELECT count(*)::int AS c FROM articles WHERE status = 'queued'`);
      return rows[0]?.c || 0;
    } catch (e) {
      console.warn("[repo] DB queued count failed:", e?.message || e);
    }
  }
  // Try queue manifest
  try {
    const cwd = process.cwd();
    const queueCandidates = [
      path.resolve(__dirname, "public", "content", "queue-manifest.json"),
      path.resolve(cwd, "dist", "public", "content", "queue-manifest.json"),
      path.resolve(cwd, "client", "public", "content", "queue-manifest.json"),
      path.resolve(__dirname, "..", "..", "dist", "public", "content", "queue-manifest.json"),
      path.resolve(__dirname, "..", "..", "client", "public", "content", "queue-manifest.json"),
    ];
    for (const p2 of queueCandidates) {
      if (fs.existsSync(p2)) {
        const j = JSON.parse(fs.readFileSync(p2, "utf8"));
        const items = j?.items || j?.articles || [];
        return items.length;
      }
    }
  } catch {}
  return 0;
}

export async function publishHistogramByDay() {
  const p = getPool();
  if (!p) return [];
  try {
    const { rows } = await query(
      `SELECT date_trunc('day', published_at)::date AS day, count(*)::int AS c
       FROM articles WHERE status = 'published'
       GROUP BY 1 ORDER BY 1 DESC LIMIT 30`
    );
    return rows;
  } catch {
    return [];
  }
}
