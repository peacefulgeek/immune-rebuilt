/**
 * Quarterly refresh (Bunny-JSON, Claude-powered). Master scope §14D + Final-Pass.
 *
 * Picks the oldest published article in each category, asks Claude to refresh
 * the body in voice, runs the quality gate, then re-uploads the new body to
 * Bunny CDN and bumps last_modified_at in the local manifest.
 *
 * No DB. Reads /client/public/content/preview-manifest.json. Hydrates each
 * body from Bunny via fetchArticleJson. Refresh content writes through to
 * Bunny via the storage API key.
 */
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { generate } from "../src/lib/engine.mjs";
import { fetchArticleJson } from "../src/lib/bunny.mjs";
import { checkText } from "../src/lib/gate.mjs";
import { SYSTEM_PROMPT, buildUserPrompt } from "../src/lib/voice.mjs";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const MANIFEST_PATH = path.resolve(__dirname, "../client/public/content/preview-manifest.json");

const STORAGE = "https://ny.storage.bunnycdn.com/conscious-elder/immune-rebuilt";
const STORAGE_KEY = process.env.BUNNY_STORAGE_KEY;

async function uploadArticleJson(slug, json) {
  if (!STORAGE_KEY) {
    throw new Error("BUNNY_STORAGE_KEY not set; cannot write to Bunny storage.");
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
  if (!fs.existsSync(MANIFEST_PATH)) {
    console.log("[refresh-quarterly] no manifest");
    return;
  }
  const manifest = JSON.parse(fs.readFileSync(MANIFEST_PATH, "utf8"));
  const articles = manifest.articles || [];
  if (articles.length === 0) {
    console.log("[refresh-quarterly] empty manifest");
    return;
  }

  // Pick oldest article per category by last_modified_at (or published_at as fallback).
  const byCategory = new Map();
  for (const a of articles) {
    const key = a.category || "Uncategorized";
    const cur = byCategory.get(key);
    const ts = new Date(a.last_modified_at || a.published_at || a.publish_at || 0).getTime();
    if (!cur || ts < cur.ts) byCategory.set(key, { article: a, ts });
  }

  let refreshed = 0;
  let failed = 0;
  for (const { article } of byCategory.values()) {
    try {
      // Hydrate full body from Bunny.
      const bodyUrl = article.body_url || `https://conscious-elder.b-cdn.net/immune-rebuilt/articles/${article.slug}.json`;
      const full = await fetchArticleJson(bodyUrl);
      if (!full || !full.body) {
        console.log(`[refresh-quarterly] skip ${article.slug}: no body on Bunny`);
        continue;
      }
      // Ask Claude (via engine.mjs) to refresh the body in voice.
      const userPrompt = buildUserPrompt({
        title: article.title,
        slug: article.slug,
        category: article.category,
        angle: "quarterly refresh - tighten prose, add 1-2 fresher references where natural, preserve voice, keep TL;DR <section> intact",
      }) + `\n\nCURRENT BODY (refresh this; output the refreshed full HTML body only):\n\n${full.body}`;
      const refreshedBody = await generate({
        system: SYSTEM_PROMPT,
        user: userPrompt,
        max_tokens: 6000,
        temperature: 0.5,
      });

      // Run the quality gate. Fail-closed: if gate flags it, keep the original body.
      let useBody = refreshedBody;
      try {
        const gate = checkText(refreshedBody);
        if (!gate.ok) {
          console.log(`[refresh-quarterly] gate fail ${article.slug}: ${(gate.issues || gate.reasons || []).join(",")}; keeping original`);
          useBody = full.body;
        }
      } catch (e) {
        console.log(`[refresh-quarterly] gate error ${article.slug}: ${e?.message || e}`);
        useBody = full.body;
      }

      const now = new Date().toISOString();
      const out = { ...full, body: useBody, last_modified_at: now };
      await uploadArticleJson(article.slug, out);

      // Bump in local manifest.
      const idx = articles.findIndex((a) => a.slug === article.slug);
      if (idx !== -1) {
        articles[idx] = { ...articles[idx], last_modified_at: now };
      }
      refreshed++;
    } catch (e) {
      failed++;
      console.error(`[refresh-quarterly] error ${article.slug}: ${e?.message || e}`);
    }
  }

  // Persist manifest.
  fs.writeFileSync(MANIFEST_PATH, JSON.stringify({ ...manifest, articles }, null, 2) + "\n");
  console.log(`[refresh-quarterly] refreshed=${refreshed} failed=${failed} categories=${byCategory.size}`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
