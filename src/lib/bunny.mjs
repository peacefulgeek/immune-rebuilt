// Bunny CDN library. Master scope §9: ALL images served from Bunny as compressed WebP.
// We accept multiple env names so production secrets can be wired without code changes.
//
//   BUNNY_PULL_ZONE_URL   e.g. https://immune-rebuilt.b-cdn.net
//   BUNNY_STORAGE_ZONE    e.g. immune-rebuilt
//   BUNNY_STORAGE_KEY     password for Storage API uploads
//   BUNNY_STORAGE_HOST    storage.bunnycdn.com (default) or regional host
//
// During local preview these are absent, so resolveImageUrl returns the
// pre-existing path that survives the local lifecycle. On DigitalOcean
// production deploy with envs set, image URLs become https://<pullzone>/<path>.

import fs from "node:fs";
import path from "node:path";

export const BUNNY = {
  pullZoneUrl:    (process.env.BUNNY_PULL_ZONE_URL || "").replace(/\/+$/, ""),
  storageZone:    process.env.BUNNY_STORAGE_ZONE || "",
  storageKey:     process.env.BUNNY_STORAGE_KEY || "",
  storageHost:    process.env.BUNNY_STORAGE_HOST || "storage.bunnycdn.com",
  enabled() { return Boolean(this.pullZoneUrl && this.storageZone && this.storageKey); },
};

// Resolve a stored asset key (e.g. "art/01-rootcauses.webp") to a public URL.
// In preview without Bunny envs, fall through to existing paths if a manifest
// mapping is provided.
export function resolveImageUrl(key, fallbackMap = {}) {
  if (!key) return "";
  if (/^https?:\/\//i.test(key)) return key;
  if (BUNNY.enabled()) {
    const clean = key.replace(/^\/+/, "");
    return `${BUNNY.pullZoneUrl}/${clean}`;
  }
  return fallbackMap[key] || key;
}

// Upload a local file (PNG/JPG) as compressed WebP to Bunny storage.
// Master scope §9B: zero images in repo (favicon excepted), all on Bunny as WebP.
// Requires `sharp` only when actually uploading; we lazy-import to keep base deploy slim.
export async function uploadAsWebp(localPath, remoteKey, { quality = 78, maxWidth = 1800 } = {}) {
  if (!BUNNY.enabled()) {
    throw new Error("Bunny CDN not configured. Set BUNNY_PULL_ZONE_URL, BUNNY_STORAGE_ZONE, BUNNY_STORAGE_KEY.");
  }
  const buf = fs.readFileSync(localPath);
  let webp = buf;
  try {
    const sharp = (await import("sharp")).default;
    const img = sharp(buf);
    const meta = await img.metadata();
    if (meta.width && meta.width > maxWidth) img.resize({ width: maxWidth });
    webp = await img.webp({ quality }).toBuffer();
  } catch {
    // No sharp available — push the raw bytes; Bunny will still serve them but the spec
    // requires WebP, so production should always include sharp. We log loudly.
    console.warn("sharp not available; uploading original bytes. Install sharp for WebP compression.");
  }
  const url = `https://${BUNNY.storageHost}/${BUNNY.storageZone}/${remoteKey.replace(/^\/+/, "")}`;
  const res = await fetch(url, {
    method: "PUT",
    headers: {
      "AccessKey": BUNNY.storageKey,
      "Content-Type": "image/webp",
    },
    body: webp,
  });
  if (!res.ok) {
    const t = await res.text().catch(() => "");
    throw new Error(`Bunny upload failed (${res.status}): ${t.slice(0, 200)}`);
  }
  return `${BUNNY.pullZoneUrl}/${remoteKey.replace(/^\/+/, "")}`;
}

// Walk client/public to ensure no images are ever shipped in the repo.
// Used by audit-site.mjs §9.
export function findImagesInRepo(repoRoot) {
  const exts = new Set([".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tiff", ".avif"]);
  const offenders = [];
  function walk(p) {
    let entries;
    try { entries = fs.readdirSync(p, { withFileTypes: true }); } catch { return; }
    for (const e of entries) {
      if (e.name === "node_modules" || e.name === ".git" || e.name === "dist") continue;
      const full = path.join(p, e.name);
      if (e.isDirectory()) walk(full);
      else if (exts.has(path.extname(e.name).toLowerCase())) {
        // Master scope §9: only public/favicon.svg is allowed (and SVG is not in this set anyway).
        offenders.push(full);
      }
    }
  }
  walk(repoRoot);
  return offenders;
}
