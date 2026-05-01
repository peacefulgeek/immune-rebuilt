/**
 * JSON-LD builders. Master scope §16E. Includes Article, Breadcrumb, FAQ,
 * Organization, WebSite (with SearchAction), Person, ImageObject.
 */

import { htmlToPlainText } from "./aeo.mjs";

export function buildOrgJsonLd({ siteApex, siteName, sameAs = [] }) {
  return {
    "@context": "https://schema.org",
    "@type": "Organization",
    name: siteName,
    url: `https://${siteApex}/`,
    logo: `https://${siteApex}/favicon.svg`,
    sameAs,
    knowsAbout: [
      "Autoimmune disease",
      "AIP protocol",
      "Leaky gut",
      "Functional medicine",
      "Hashimoto's thyroiditis",
      "Lupus",
      "Rheumatoid arthritis",
      "Multiple sclerosis",
      "Psoriasis",
      "Chronic illness recovery",
    ],
  };
}

export function buildWebsiteJsonLd({ siteApex, siteName }) {
  return {
    "@context": "https://schema.org",
    "@type": "WebSite",
    url: `https://${siteApex}/`,
    name: siteName,
    potentialAction: {
      "@type": "SearchAction",
      target: `https://${siteApex}/articles?q={search_term_string}`,
      "query-input": "required name=search_term_string",
    },
  };
}

export function buildPersonJsonLd({ name, url, knowsAbout = [] }) {
  return {
    "@context": "https://schema.org",
    "@type": "Person",
    name,
    url,
    sameAs: [url],
    jobTitle: "Writer and editor",
    description:
      "Spiritual writer and longtime student of contemplative practice; editor and reviewer for The Autoimmune Reset.",
    knowsAbout,
  };
}

export function buildArticleJsonLd(article, { siteApex, siteName, author, sisterSiteUrl, bunnyZone }) {
  const url = `https://${siteApex}/articles/${article.slug}`;
  const image = article.hero_url || `${bunnyZone}/og/default.webp`;
  const publishedAt = article.published_at ? new Date(article.published_at).toISOString() : new Date().toISOString();
  const modifiedAt = article.last_modified_at
    ? new Date(article.last_modified_at).toISOString()
    : publishedAt;
  const wordCount = article.word_count || (htmlToPlainText(article.body || "").split(/\s+/).length);

  return {
    "@context": "https://schema.org",
    "@type": "Article",
    headline: article.title,
    description: (article.excerpt || article.title).slice(0, 200),
    inLanguage: "en",
    isAccessibleForFree: true,
    datePublished: publishedAt,
    dateModified: modifiedAt,
    url,
    mainEntityOfPage: url,
    image,
    articleSection: article.category || "Autoimmune",
    wordCount,
    author: {
      "@type": "Person",
      name: author,
      url: sisterSiteUrl,
    },
    publisher: {
      "@type": "Organization",
      name: siteName,
      logo: { "@type": "ImageObject", url: `https://${siteApex}/favicon.svg` },
    },
    reviewedBy: {
      "@type": "Person",
      name: author,
      url: sisterSiteUrl,
    },
    speakable: {
      "@type": "SpeakableSpecification",
      cssSelector: ['[data-tldr="ai-overview"]'],
    },
  };
}

export function buildBreadcrumbJsonLd(article, { siteApex }) {
  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: [
      { "@type": "ListItem", position: 1, name: "Home", item: `https://${siteApex}/` },
      { "@type": "ListItem", position: 2, name: "Articles", item: `https://${siteApex}/articles` },
      ...(article.category
        ? [
            {
              "@type": "ListItem",
              position: 3,
              name: article.category,
              item: `https://${siteApex}/articles?category=${encodeURIComponent(article.category)}`,
            },
            { "@type": "ListItem", position: 4, name: article.title, item: `https://${siteApex}/articles/${article.slug}` },
          ]
        : [{ "@type": "ListItem", position: 3, name: article.title, item: `https://${siteApex}/articles/${article.slug}` }]),
    ],
  };
}

export function buildFaqJsonLd(article) {
  const body = article.body || "";
  // Extract H2/H3/H4 questions and the immediately following paragraph.
  const reHeading = /<h([234])[^>]*>([^<]+)<\/h\1>\s*([\s\S]*?)(?=<h[234][^>]*>|<\/article>|$)/gi;
  const items = [];
  let m;
  while ((m = reHeading.exec(body)) !== null && items.length < 6) {
    const q = m[2].trim();
    if (!/[\?]/.test(q)) continue;
    const a = htmlToPlainText(m[3] || "")
      .split(/\n+/)
      .map((s) => s.trim())
      .filter(Boolean)
      .slice(0, 2)
      .join(" ");
    if (!a) continue;
    items.push({
      "@type": "Question",
      name: q,
      acceptedAnswer: { "@type": "Answer", text: a.slice(0, 800) },
    });
  }
  if (items.length === 0) return null;
  return {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: items,
  };
}

export function buildImageObjectJsonLd(heroUrl, { siteApex, author }) {
  return {
    "@context": "https://schema.org",
    "@type": "ImageObject",
    contentUrl: heroUrl,
    creditText: `Original illustration for ${siteApex}`,
    creator: { "@type": "Person", name: author },
    license: `https://${siteApex}/disclosures`,
    acquireLicensePage: `https://${siteApex}/disclosures`,
  };
}
