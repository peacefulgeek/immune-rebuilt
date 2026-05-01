/**
 * AEO / discoverability helpers. Master scope §16.
 * Canonicals strip tracking params; sitemap & llms files filter to published only.
 */

export const STRIP_PARAMS = new Set([
  "utm_source",
  "utm_medium",
  "utm_campaign",
  "utm_term",
  "utm_content",
  "fbclid",
  "gclid",
  "mc_eid",
  "mc_cid",
  "ref",
  "ref_",
  "source",
  "via",
]);

export function buildCanonical(req, siteApex) {
  const url = new URL(req.originalUrl || req.url || "/", `https://${siteApex}`);
  for (const p of [...url.searchParams.keys()]) {
    if (STRIP_PARAMS.has(p.toLowerCase())) url.searchParams.delete(p);
  }
  let pathname = url.pathname;
  if (pathname.length > 1 && pathname.endsWith("/")) pathname = pathname.slice(0, -1);
  return `https://${siteApex}${pathname}${url.search}`;
}

export function buildSitemapXml(rows, siteApex) {
  const head = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">`;
  const tail = `</urlset>`;
  const staticPages = [
    { loc: `https://${siteApex}/`, priority: "1.0" },
    { loc: `https://${siteApex}/articles`, priority: "0.9" },
    { loc: `https://${siteApex}/assessments`, priority: "0.85" },
    { loc: `https://${siteApex}/apothecary`, priority: "0.85" },
    { loc: `https://${siteApex}/about`, priority: "0.7" },
    { loc: `https://${siteApex}/disclosures`, priority: "0.5" },
    { loc: `https://${siteApex}/privacy`, priority: "0.5" },
    { loc: `https://${siteApex}/contact`, priority: "0.5" },
  ];
  const articleEntries = (rows || []).map((r) => ({
    loc: `https://${siteApex}/articles/${r.slug}`,
    lastmod: (r.last_modified_at || r.published_at || new Date()).toISOString(),
    priority: "0.8",
  }));
  const all = [
    ...staticPages.map(
      (p) =>
        `  <url><loc>${p.loc}</loc><changefreq>weekly</changefreq><priority>${p.priority}</priority></url>`
    ),
    ...articleEntries.map(
      (p) =>
        `  <url><loc>${p.loc}</loc><lastmod>${p.lastmod}</lastmod><changefreq>monthly</changefreq><priority>${p.priority}</priority></url>`
    ),
  ];
  return `${head}\n${all.join("\n")}\n${tail}\n`;
}

export function buildLlmsTxt(rows, { siteApex, siteName }) {
  const lines = [];
  lines.push(`# ${siteName}`);
  lines.push("");
  lines.push(
    `${siteName} is an editorial site about autoimmune root causes, the AIP protocol, leaky gut, functional medicine, and the emotional roots of chronic illness. Independent. Reader supported. Written for people whose immune systems aren't broken — they're responding to something.`
  );
  lines.push("");
  lines.push(`Apex: https://${siteApex}/`);
  lines.push(`Sitemap: https://${siteApex}/sitemap.xml`);
  lines.push(`Full corpus: https://${siteApex}/llms-full.txt`);
  lines.push("");

  const byCat = new Map();
  for (const r of rows || []) {
    const cat = r.category || "Articles";
    if (!byCat.has(cat)) byCat.set(cat, []);
    byCat.get(cat).push(r);
  }
  const cats = [...byCat.keys()].sort();
  for (const cat of cats) {
    lines.push(`## ${cat}`);
    lines.push("");
    for (const r of byCat.get(cat)) {
      const desc = (r.excerpt || "").replace(/\s+/g, " ").trim().slice(0, 160);
      lines.push(`- [${r.title}](https://${siteApex}/articles/${r.slug}): ${desc}`);
    }
    lines.push("");
  }
  return lines.join("\n");
}

export function buildLlmsFullTxt(rows, { siteApex, siteName }) {
  const out = [];
  out.push(`# ${siteName} — full corpus`);
  out.push(`# https://${siteApex}/`);
  out.push("");
  for (const r of rows || []) {
    out.push("---");
    out.push(`slug: ${r.slug}`);
    out.push(`title: ${r.title}`);
    out.push(`category: ${r.category || ""}`);
    out.push(`url: https://${siteApex}/articles/${r.slug}`);
    out.push(`published_at: ${r.published_at ? new Date(r.published_at).toISOString() : ""}`);
    out.push(`modified_at: ${r.last_modified_at ? new Date(r.last_modified_at).toISOString() : ""}`);
    out.push("---");
    out.push("");
    const text = htmlToPlainText(r.body || "");
    out.push(text);
    out.push("");
    out.push("");
  }
  return out.join("\n");
}

export function htmlToPlainText(html) {
  if (!html) return "";
  return String(html)
    .replace(/<script[\s\S]*?<\/script>/gi, " ")
    .replace(/<style[\s\S]*?<\/style>/gi, " ")
    .replace(/<\/?(p|h\d|li|ul|ol|aside|section|div|article|header|footer|br|tr|td|th|table)[^>]*>/gi, "\n")
    .replace(/<[^>]+>/g, " ")
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/[ \t]+\n/g, "\n")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}
