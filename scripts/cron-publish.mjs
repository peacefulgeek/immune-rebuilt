/**
 * Weekday publish tick. Promotes exactly 1 article from the Bunny queue JSON
 * to the published manifest. No DB. No fallback generation. When queue is
 * empty, it stops.
 *
 * Flow:
 * 1. Read queue-manifest.json (Bunny-backed, local copy in client/public/content/).
 * 2. Pick the first entry with status="queued" (ordered by publish_at ASC).
 * 3. Hydrate its body from Bunny via body_url.
 * 4. If body is missing or empty - skip and log. No generation fallback.
 * 5. Move the entry from queue-manifest to preview-manifest (published).
 * 6. Stamp published_at = now, assign hero from the article JSON.
 * 7. Upload the updated article JSON to Bunny with published_at set.
 * 8. Write both manifests back to disk (for next deploy / git commit).
 *
 * Cron schedule: weekdays only (Mon-Fri) at 13:17 UTC.
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { fetchArticleJson } from "../src/lib/bunny.mjs";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const CONTENT = path.resolve(__dirname, "..", "client", "public", "content");
const QUEUE_PATH = path.join(CONTENT, "queue-manifest.json");
const PUB_PATH = path.join(CONTENT, "preview-manifest.json");

const STORAGE = "https://ny.storage.bunnycdn.com/conscious-elder/immune-rebuilt";
const STORAGE_KEY = process.env.BUNNY_STORAGE_KEY || "";

async function uploadArticleJson(slug, json) {
  if (!STORAGE_KEY) {
    console.log("[publish] BUNNY_STORAGE_KEY not set - cannot write to Bunny. Skipping upload.");
    return;
  }
  const url = `${STORAGE}/articles/${slug}.json`;
  const r = await fetch(url, {
    method: "PUT",
    headers: { AccessKey: STORAGE_KEY, "Content-Type": "application/json" },
    body: JSON.stringify(json),
  });
  if (!r.ok) {
    throw new Error(`Bunny upload failed: ${r.status} ${await r.text()}`);
  }
}

async function main() {
  // Guard: only run on weekdays (Mon=1 ... Fri=5).
  const dow = new Date().getDay(); // 0=Sun, 6=Sat
  if (dow === 0 || dow === 6) {
    console.log("[publish] weekend - skipping");
    return;
  }

  if (!fs.existsSync(QUEUE_PATH)) {
    console.log("[publish] no queue manifest - nothing to publish");
    return;
  }
  if (!fs.existsSync(PUB_PATH)) {
    console.log("[publish] no published manifest - cannot publish");
    return;
  }

  const queue = JSON.parse(fs.readFileSync(QUEUE_PATH, "utf8"));
  const pub = JSON.parse(fs.readFileSync(PUB_PATH, "utf8"));

  const queueArticles = queue.articles || [];
  const pubArticles = pub.articles || [];

  // Find first queued entry.
  const idx = queueArticles.findIndex((a) => a.status === "queued");
  if (idx === -1) {
    console.log("[publish] queue empty - nothing to publish. Stopping.");
    return;
  }

  const item = queueArticles[idx];
  console.log(`[publish] promoting: ${item.slug} (queue position ${idx})`);

  // Hydrate body from Bunny.
  const bodyUrl = item.body_url || `https://conscious-elder.b-cdn.net/immune-rebuilt/articles/${item.slug}.json`;
  let full;
  try {
    full = await fetchArticleJson(bodyUrl);
  } catch (e) {
    console.error(`[publish] failed to hydrate body for ${item.slug}: ${e?.message || e}`);
    console.log("[publish] no fallback generation - skipping this article");
    // Mark it as skipped so we don't retry forever.
    queueArticles[idx] = { ...item, status: "skipped", skip_reason: "body_hydration_failed" };
    fs.writeFileSync(QUEUE_PATH, JSON.stringify({ ...queue, articles: queueArticles }, null, 2) + "\n");
    return;
  }

  if (!full || !full.body || String(full.body).length < 500) {
    console.log(`[publish] ${item.slug} has no body or body too short - skipping. No fallback generation.`);
    queueArticles[idx] = { ...item, status: "skipped", skip_reason: "empty_body" };
    fs.writeFileSync(QUEUE_PATH, JSON.stringify({ ...queue, articles: queueArticles }, null, 2) + "\n");
    return;
  }

  // Stamp published_at = now.
  const now = new Date().toISOString();
  const publishedEntry = {
    slug: item.slug,
    title: item.title,
    excerpt: item.excerpt || "",
    category: item.category,
    published_at: now,
    last_modified_at: now,
    status: "published",
    hero_url: item.hero_url || full.hero_url || "",
    hero_alt: item.hero_alt || full.hero_alt || item.title,
    word_count: item.word_count || full.word_count || 0,
    asins: item.asins || full.asins || [],
    related: item.related || full.related || [],
    body_url: bodyUrl,
    tags: item.tags || full.tags || [],
  };

  // Add to published manifest (prepend - newest first).
  pubArticles.unshift(publishedEntry);

  // Remove from queue.
  queueArticles.splice(idx, 1);

  // Update the article JSON on Bunny with published_at.
  const updatedFull = { ...full, published_at: now, last_modified_at: now, status: "published" };
  try {
    await uploadArticleJson(item.slug, updatedFull);
  } catch (e) {
    console.error(`[publish] Bunny upload failed for ${item.slug}: ${e?.message || e}`);
    // Still proceed with local manifest update - the body exists, just the metadata didn't sync.
  }

  // Write manifests.
  fs.writeFileSync(PUB_PATH, JSON.stringify({ ...pub, articles: pubArticles }, null, 2) + "\n");
  fs.writeFileSync(QUEUE_PATH, JSON.stringify({ ...queue, articles: queueArticles }, null, 2) + "\n");

  console.log(`[publish] OK: ${item.slug} published at ${now}. Queue remaining: ${queueArticles.length}`);
}

main().catch((e) => {
  console.error("[publish] tick error", e);
  process.exit(1);
});
