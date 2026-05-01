// Ambient module declarations for the plain-ESM .mjs files in src/lib.
// We don't type-check the .mjs files themselves; this just declares them.

declare module "../src/lib/aeo.mjs" {
  export const STRIP_PARAMS: Set<string>;
  export function buildCanonical(req: any, siteApex: string): string;
  export function buildSitemapXml(rows: any[], siteApex: string): string;
  export function buildLlmsTxt(rows: any[], opts: { siteApex: string; siteName: string }): string;
  export function buildLlmsFullTxt(rows: any[], opts: { siteApex: string; siteName: string }): string;
  export function htmlToPlainText(html: string): string;
}

declare module "../src/lib/articleJsonLd.mjs" {
  export function buildOrgJsonLd(opts: { siteApex: string; siteName: string; sameAs?: string[] }): any;
  export function buildWebsiteJsonLd(opts: { siteApex: string; siteName: string }): any;
  export function buildPersonJsonLd(opts: { name: string; url: string; knowsAbout?: string[] }): any;
  export function buildArticleJsonLd(article: any, opts: { siteApex: string; siteName: string; author: string; sisterSiteUrl: string; bunnyZone: string }): any;
  export function buildBreadcrumbJsonLd(article: any, opts: { siteApex: string }): any;
  export function buildFaqJsonLd(article: any): any | null;
  export function buildImageObjectJsonLd(heroUrl: string, opts: { siteApex: string; author: string }): any;
}

declare module "../src/lib/socialMeta.mjs" {
  export function buildSocialMeta(opts: {
    title: string;
    description: string;
    url: string;
    image: string;
    author: string;
    section?: string;
    publishedTime?: string;
    modifiedTime?: string;
  }): string;
}

declare module "../src/lib/repo.mjs" {
  export function getPublishedArticleBySlug(slug: string): Promise<any | null>;
  export function listPublishedArticles(opts?: {
    limit?: number;
    category?: string;
    includeBody?: boolean;
  }): Promise<any[]>;
  export function listPublishedForSitemap(): Promise<any[]>;
  export function searchPublishedArticles(q: string, opts?: { limit?: number }): Promise<any[]>;
  export function countPublished(): Promise<number>;
  export function countQueued(): Promise<number>;
  export function publishHistogramByDay(): Promise<{ day: string; c: number }[]>;
}

declare module "../src/lib/mail.mjs" {
  export function sendContactEmail(opts: {
    name: string;
    email: string;
    message: string;
    site: string;
  }): Promise<{ ok: boolean; reason?: string }>;
}
