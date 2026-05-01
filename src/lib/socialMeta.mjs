/**
 * Open Graph + Twitter card meta. Master scope §16F.
 */
function esc(s) {
  return String(s || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

export function buildSocialMeta({ title, description, url, image, author, section, publishedTime, modifiedTime }) {
  const t = esc(title);
  const d = esc(description);
  const u = esc(url);
  const i = esc(image);
  const a = esc(author);
  const sec = esc(section || "");
  const pt = publishedTime ? new Date(publishedTime).toISOString() : "";
  const mt = modifiedTime ? new Date(modifiedTime).toISOString() : "";
  return [
    `<meta property="og:type" content="article">`,
    `<meta property="og:title" content="${t}">`,
    `<meta property="og:description" content="${d}">`,
    `<meta property="og:url" content="${u}">`,
    `<meta property="og:image" content="${i}">`,
    pt ? `<meta property="article:published_time" content="${pt}">` : "",
    mt ? `<meta property="article:modified_time" content="${mt}">` : "",
    `<meta property="article:author" content="${a}">`,
    sec ? `<meta property="article:section" content="${sec}">` : "",
    `<meta name="twitter:card" content="summary_large_image">`,
    `<meta name="twitter:title" content="${t}">`,
    `<meta name="twitter:description" content="${d}">`,
    `<meta name="twitter:image" content="${i}">`,
  ]
    .filter(Boolean)
    .join("\n");
}
