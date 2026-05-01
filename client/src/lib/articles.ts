/**
 * Article data layer for the React client.
 * In production: hits /api/articles served by Express + Postgres.
 * In static-preview mode: falls back to /content/preview-manifest.json
 * that ships with the build for design-time browsing.
 */

export type ArticleCard = {
  slug: string;
  title: string;
  excerpt: string;
  category: string;
  tags: string[];
  hero_url: string;
  published_at: string;
  last_modified_at?: string;
  word_count?: number;
  body?: string;
  asins_used?: string[];
};

const FALLBACK_URL = "/content/preview-manifest.json";

let _manifestCache: ArticleCard[] | null = null;

async function loadManifest(): Promise<ArticleCard[]> {
  if (_manifestCache) return _manifestCache;
  try {
    const r = await fetch(FALLBACK_URL, { cache: "force-cache" });
    if (!r.ok) throw new Error("no manifest");
    const j = (await r.json()) as { items: ArticleCard[] };
    _manifestCache = j.items || [];
    return _manifestCache;
  } catch {
    _manifestCache = [];
    return _manifestCache;
  }
}

export async function fetchList(opts: { q?: string; category?: string; limit?: number } = {}): Promise<ArticleCard[]> {
  const params = new URLSearchParams();
  if (opts.q) params.set("q", opts.q);
  if (opts.category) params.set("category", opts.category);
  if (opts.limit) params.set("limit", String(opts.limit));
  try {
    const r = await fetch(`/api/articles?${params.toString()}`, { cache: "no-store" });
    if (r.ok) {
      const j = await r.json();
      if (j?.ok && Array.isArray(j.items) && j.items.length) return j.items;
    }
  } catch {}
  // fallback
  let list = await loadManifest();
  if (opts.category) list = list.filter((a) => a.category === opts.category);
  if (opts.q) {
    const q = opts.q.toLowerCase();
    list = list.filter(
      (a) =>
        a.title.toLowerCase().includes(q) ||
        a.excerpt.toLowerCase().includes(q) ||
        (a.tags || []).some((t) => t.toLowerCase().includes(q))
    );
  }
  if (opts.limit) list = list.slice(0, opts.limit);
  return list;
}

export async function fetchOne(slug: string): Promise<ArticleCard | null> {
  try {
    const r = await fetch(`/api/articles/${encodeURIComponent(slug)}`);
    if (r.ok) {
      const j = await r.json();
      if (j?.ok && j.article) return j.article;
    }
  } catch {}
  const list = await loadManifest();
  return list.find((a) => a.slug === slug) || null;
}

export const CATEGORIES = [
  "Root Causes",
  "AIP & Diet",
  "Gut Healing",
  "Stress & Nervous System",
  "Emotional Roots",
  "Conditions",
  "Functional Medicine",
  "Recovery",
] as const;
