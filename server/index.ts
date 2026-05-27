/**
 * Site 86 — Immune Rebuilt
 * Express server. Master scope §7. WWW→apex 301 is the FIRST middleware.
 * No Cloudflare, no third-party runtime, no Next.js. Pure Express + Vite SSR head injection.
 */
import express, { type Request, type Response, type NextFunction } from "express";
import compression from "compression";
import helmet from "helmet";
import { createServer } from "http";
import path from "path";
import { fileURLToPath } from "url";
import fs from "fs";

import { buildCanonical, STRIP_PARAMS } from "../src/lib/aeo.mjs";
import {
  buildArticleJsonLd,
  buildBreadcrumbJsonLd,
  buildFaqJsonLd,
  buildOrgJsonLd,
  buildWebsiteJsonLd,
  buildPersonJsonLd,
  buildImageObjectJsonLd,
} from "../src/lib/articleJsonLd.mjs";
import { buildSocialMeta } from "../src/lib/socialMeta.mjs";
import {
  getPublishedArticleBySlug,
  listPublishedArticles,
  listPublishedForSitemap,
  searchPublishedArticles,
  countPublished,
} from "../src/lib/repo.mjs";
import { buildSitemapXml, buildLlmsTxt, buildLlmsFullTxt } from "../src/lib/aeo.mjs";
import { sendContactEmail } from "../src/lib/mail.mjs";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const SITE_APEX = process.env.SITE_APEX || "immunerebuilt.com";
const SITE_NAME = process.env.SITE_NAME || "Immune Rebuilt";
const SITE_AUTHOR = process.env.SITE_AUTHOR || "The Oracle Lover";
const SISTER_SITE_URL = process.env.SISTER_SITE_URL || "https://theoraclelover.com";
const BUNNY_PULL_ZONE = process.env.BUNNY_PULL_ZONE || "https://immune-rebuilt.b-cdn.net";

async function startServer() {
  const app = express();
  const server = createServer(app);

  app.set("trust proxy", 1);

  // ── §7A: WWW → apex 301 — MUST RUN FIRST. Before everything.
  app.use((req: Request, res: Response, next: NextFunction) => {
    const host = (req.headers.host || "").toLowerCase();
    if (host.startsWith("www.")) {
      const apex = host.slice(4);
      const proto = (req.headers["x-forwarded-proto"] as string) || "https";
      return res.redirect(301, `${proto}://${apex}${req.originalUrl}`);
    }
    next();
  });

  // ── Strip tracking params (§16A) before canonicalization & analytics.
  app.use((req, _res, next) => {
    if (req.query && Object.keys(req.query).length > 0) {
      for (const k of Object.keys(req.query)) {
        if (STRIP_PARAMS.has(k.toLowerCase())) delete (req.query as any)[k];
      }
    }
    next();
  });

  app.use(compression());
  app.use(
    helmet({
      contentSecurityPolicy: false, // we ship inline JSON-LD; loosen here, harden via meta CSP per route if needed
      crossOriginEmbedderPolicy: false,
    })
  );
  app.use(express.json({ limit: "100kb" }));
  app.use(express.urlencoded({ extended: true, limit: "100kb" }));

  // ── Health check for DigitalOcean App Platform.
  app.get("/healthz", (_req, res) => {
    res.status(200).json({ ok: true, ts: new Date().toISOString(), site: SITE_APEX });
  });

  // ── /robots.txt — opt-IN to AI bots. §16C.
  app.get("/robots.txt", (_req, res) => {
    res.type("text/plain").send(
      [
        "User-agent: *",
        "Allow: /",
        "",
        "User-agent: GPTBot",
        "Allow: /",
        "User-agent: ChatGPT-User",
        "Allow: /",
        "User-agent: OAI-SearchBot",
        "Allow: /",
        "User-agent: ClaudeBot",
        "Allow: /",
        "User-agent: Claude-Web",
        "Allow: /",
        "User-agent: anthropic-ai",
        "Allow: /",
        "User-agent: PerplexityBot",
        "Allow: /",
        "User-agent: Perplexity-User",
        "Allow: /",
        "User-agent: Google-Extended",
        "Allow: /",
        "User-agent: Bingbot",
        "Allow: /",
        "User-agent: CCBot",
        "Allow: /",
        "User-agent: Applebot",
        "Allow: /",
        "User-agent: Applebot-Extended",
        "Allow: /",
        "User-agent: DuckAssistBot",
        "Allow: /",
        "User-agent: Meta-ExternalAgent",
        "Allow: /",
        "User-agent: YouBot",
        "Allow: /",
        "User-agent: MistralAI-User",
        "Allow: /",
        "User-agent: Cohere-AI",
        "Allow: /",
        "",
        `Sitemap: https://${SITE_APEX}/sitemap.xml`,
        "",
        `# https://${SITE_APEX}/llms.txt`,
        `# https://${SITE_APEX}/llms-full.txt`,
        "",
      ].join("\n")
    );
  });

  // ── /sitemap.xml — published only. §16D.
  app.get("/sitemap.xml", async (_req, res) => {
    try {
      const rows = await listPublishedForSitemap();
      const xml = buildSitemapXml(rows, SITE_APEX);
      res.type("application/xml").set("Cache-Control", "public, max-age=3600").send(xml);
    } catch (e: any) {
      res.status(500).type("text/plain").send(`sitemap-unavailable: ${e?.message || "error"}`);
    }
  });

  // ── /llms.txt — markdown index. §16D.
  app.get("/llms.txt", async (_req, res) => {
    try {
      const rows = await listPublishedArticles({ limit: 500 });
      const md = buildLlmsTxt(rows, { siteApex: SITE_APEX, siteName: SITE_NAME });
      res.type("text/markdown").set("Cache-Control", "public, max-age=3600").send(md);
    } catch (e: any) {
      res.status(500).type("text/plain").send(`llms-unavailable: ${e?.message || "error"}`);
    }
  });

  // ── /llms-full.txt — full text dump. §16D.
  // We cap to top 50 by recency so the response stays under 5MB and the route
  // doesn't time out cold-hydrating 100 bodies from Bunny on first hit.
  app.get("/llms-full.txt", async (_req, res) => {
    try {
      const rows = await listPublishedArticles({ limit: 50, includeBody: true });
      const txt = buildLlmsFullTxt(rows, { siteApex: SITE_APEX, siteName: SITE_NAME });
      res.type("text/plain").set("Cache-Control", "public, max-age=3600").send(txt);
    } catch (e: any) {
      res.status(500).type("text/plain").send(`llms-full-unavailable: ${e?.message || "error"}`);
    }
  });

  // ── JSON API for client navigation.
  app.get("/api/articles", async (req, res) => {
    const q = String(req.query.q || "").trim();
    const category = String(req.query.category || "").trim();
    const limit = Math.min(parseInt(String(req.query.limit || "60"), 10) || 60, 200);
    try {
      const items = q
        ? await searchPublishedArticles(q, { limit })
        : await listPublishedArticles({ limit, category: category || undefined });
      res.json({ ok: true, items });
    } catch (e: any) {
      res.status(500).json({ ok: false, error: e?.message || "error" });
    }
  });

  app.get("/api/articles/:slug", async (req, res) => {
    try {
      const a = await getPublishedArticleBySlug(req.params.slug);
      if (!a) return res.status(404).json({ ok: false, error: "not-found" });
      res.json({ ok: true, article: a });
    } catch (e: any) {
      res.status(500).json({ ok: false, error: e?.message || "error" });
    }
  });

  app.get("/api/stats", async (_req, res) => {
    try {
      const published = await countPublished();
      res.json({ ok: true, published, site: SITE_APEX });
    } catch (e: any) {
      res.status(500).json({ ok: false, error: e?.message || "error" });
    }
  });

  // ── Contact form via Nodemailer (no third-party email service).
  app.post("/api/contact", async (req, res) => {
    try {
      const { name, email, message } = req.body || {};
      if (!name || !email || !message) {
        return res.status(400).json({ ok: false, error: "missing-fields" });
      }
      await sendContactEmail({ name, email, message, site: SITE_NAME });
      res.json({ ok: true });
    } catch (e: any) {
      res.status(500).json({ ok: false, error: e?.message || "error" });
    }
  });

  // ── Static — production assets.
  const staticPath =
    process.env.NODE_ENV === "production"
      ? path.resolve(__dirname, "public")
      : path.resolve(__dirname, "..", "dist", "public");
  if (fs.existsSync(staticPath)) {
    app.use(
      express.static(staticPath, {
        setHeaders: (res, p) => {
          if (p.endsWith(".html")) {
            res.setHeader("Cache-Control", "public, max-age=300");
          } else if (/\.(js|css|svg|woff2?)$/i.test(p)) {
            res.setHeader("Cache-Control", "public, max-age=31536000, immutable");
          }
        },
      })
    );
  }

  const indexHtmlPath = path.join(staticPath, "index.html");

  // ── HTML SSR head injection. §16G.
  function injectHead(rawHtml: string, ctx: any): string {
    const canonical = buildCanonical(ctx.req, SITE_APEX);
    const social = buildSocialMeta({
      title: ctx.title,
      description: ctx.description,
      url: canonical,
      image: ctx.image || `${BUNNY_PULL_ZONE}/og/default.webp`,
      author: SITE_AUTHOR,
      section: ctx.category || "Autoimmune",
      publishedTime: ctx.publishedAt,
      modifiedTime: ctx.modifiedAt,
    });

    const ld: any[] = [];
    ld.push(buildOrgJsonLd({ siteApex: SITE_APEX, siteName: SITE_NAME, sameAs: [SISTER_SITE_URL] }));

    if (ctx.kind === "home") {
      ld.push(buildWebsiteJsonLd({ siteApex: SITE_APEX, siteName: SITE_NAME }));
      ld.push(
        buildPersonJsonLd({
          name: SITE_AUTHOR,
          url: SISTER_SITE_URL,
          knowsAbout: /** @type {string[]} */ ([
            "autoimmune disease",
            "AIP protocol",
            "leaky gut",
            "functional medicine",
            "Hashimoto's",
            "lupus",
            "rheumatoid arthritis",
            "MS",
            "psoriasis",
            "emotional roots of illness",
          ]),
        })
      );
    } else if (ctx.kind === "article" && ctx.article) {
      ld.push(buildArticleJsonLd(ctx.article, { siteApex: SITE_APEX, siteName: SITE_NAME, author: SITE_AUTHOR, sisterSiteUrl: SISTER_SITE_URL, bunnyZone: BUNNY_PULL_ZONE }));
      ld.push(buildBreadcrumbJsonLd(ctx.article, { siteApex: SITE_APEX }));
      const faq = buildFaqJsonLd(ctx.article);
      if (faq) ld.push(faq);
      if (ctx.article.hero_url) ld.push(buildImageObjectJsonLd(ctx.article.hero_url, { siteApex: SITE_APEX, author: SITE_AUTHOR }));
    }

    const ldBlocks = ld
      .filter(Boolean)
      .map((o) => `<script type="application/ld+json">${JSON.stringify(o).replace(/</g, "\\u003c")}</script>`)
      .join("");

    const headInject = [
      `<title>${escapeHtml(ctx.title)}</title>`,
      `<meta name="description" content="${escapeHtml(ctx.description)}">`,
      `<link rel="canonical" href="${canonical}">`,
      `<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">`,
      `<meta name="theme-color" content="#FAFAF5">`,
      `<link rel="icon" type="image/svg+xml" href="/favicon.svg">`,
      social,
      ldBlocks,
    ].join("\n");

    return rawHtml
      .replace(/<title>[^<]*<\/title>/i, "")
      .replace(/<meta\s+name="description"[^>]*>/i, "")
      .replace("</head>", `${headInject}\n</head>`);
  }

  // ── SSR routes for crawlers (head). React shell renders the rest client-side.
  app.get(["/", "/articles", "/articles/:slug", "/about", "/disclosures", "/privacy", "/contact", "/assessments", "/assessments/:slug", "/apothecary"], async (req, res, next) => {
    if (!fs.existsSync(indexHtmlPath)) return next();
    const raw = fs.readFileSync(indexHtmlPath, "utf8");
    let ctx: any = {
      req,
      kind: "home" as string,
      title: `${SITE_NAME} - Reverse the Fire Within` as string,
      description: "Your immune system isn't attacking you. It's responding to something. Immune Rebuilt helps you find what." as string,
      image: undefined as string | undefined,
      category: undefined as string | undefined,
      publishedAt: undefined as string | undefined,
      modifiedAt: undefined as string | undefined,
      article: undefined as any,
    };

    if (req.path.startsWith("/articles/")) {
      const slug = req.params.slug;
      try {
        const article = await getPublishedArticleBySlug(slug);
        if (!article) {
          ctx = { req, kind: "notfound", title: `Not found , ${SITE_NAME}`, description: `That article was not found on ${SITE_NAME}.` };
        } else {
          ctx = {
            req,
            kind: "article",
            article,
            title: `${article.title} , ${SITE_NAME}`,
            description: (article.excerpt || article.title).slice(0, 160),
            image: article.hero_url,
            category: article.category,
            publishedAt: article.published_at,
            modifiedAt: article.last_modified_at || article.published_at,
          };
        }
      } catch {
        // DB unreachable — fall through to home shell so the site still renders.
      }
    } else if (req.path === "/articles") {
      ctx = { req, kind: "list", title: `Articles , ${SITE_NAME}`, description: "Every essay on autoimmune root causes, AIP, leaky gut, functional medicine, and the emotional roots underneath." };
    } else if (req.path === "/about") {
      ctx = { req, kind: "page", title: `About , ${SITE_NAME}`, description: `Why ${SITE_NAME} exists. Who writes here. What we believe about chronic illness.` };
    } else if (req.path === "/disclosures") {
      ctx = { req, kind: "page", title: `Disclosures , ${SITE_NAME}`, description: "Affiliate disclosure, medical disclaimer, and editorial standards for Immune Rebuilt." };
    } else if (req.path === "/privacy") {
      ctx = { req, kind: "page", title: `Privacy , ${SITE_NAME}`, description: "How Immune Rebuilt handles personal information." };
    } else if (req.path === "/contact") {
      ctx = { req, kind: "page", title: `Contact , ${SITE_NAME}`, description: `Reach Immune Rebuilt.` };
    } else if (req.path === "/assessments") {
      ctx = { req, kind: "page", title: `Self-screen assessments , ${SITE_NAME}`, description: `Eleven validated, free, browser-only screens for autoimmune-relevant patterns. Nothing leaves your device.` };
    } else if (req.path.startsWith("/assessments/")) {
      ctx = { req, kind: "page", title: `${SITE_NAME} self-screen`, description: `An interactive, browser-only screen with a TL;DR result and pointers to deeper essays.` };
    } else if (req.path === "/apothecary") {
      ctx = { req, kind: "page", title: `Apothecary , ${SITE_NAME}`, description: `Fifty considered supplements, herbs, and TCM items with one-line reasoning, cautions where they apply, and Amazon links.` };
    }

    res.set("Cache-Control", "public, max-age=3600");
    res.type("text/html").send(injectHead(raw, ctx));
  });

  // ── Catch-all (404) routed to React shell.
  app.get("*", (req, res) => {
    if (!fs.existsSync(indexHtmlPath)) {
      return res.status(404).type("text/plain").send("Not found");
    }
    const raw = fs.readFileSync(indexHtmlPath, "utf8");
    const ctx = {
      req,
      kind: "notfound",
      title: `Not found — ${SITE_NAME}`,
      description: `That page isn't on ${SITE_NAME}.`,
    };
    res.status(404).type("text/html").send(injectHead(raw, ctx));
  });

  function escapeHtml(s: string): string {
    return String(s || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  const port = parseInt(process.env.PORT || "8080", 10);
  const host = "0.0.0.0";
  server.on("error", (err: NodeJS.ErrnoException) => {
    // eslint-disable-next-line no-console
    console.error(`[server] listen error on ${host}:${port}:`, err?.code || "", err?.message || err);
    process.exit(1);
  });
  server.listen(port, host, () => {
    // eslint-disable-next-line no-console
    console.log(`[${SITE_NAME}] listening on ${host}:${port}  (apex=${SITE_APEX})`);
  });
}

startServer().catch((e) => {
  // eslint-disable-next-line no-console
  console.error("[server] fatal:", e);
  process.exit(1);
});
