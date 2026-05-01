import { useEffect, useMemo, useState } from "react";
import { Link, useRoute } from "wouter";
import { fetchOne, fetchList, type ArticleCard } from "@/lib/articles";
import { Share2, ChevronLeft, AlertTriangle } from "lucide-react";
import { toast } from "sonner";

export default function Article() {
  const [, params] = useRoute<{ slug: string }>("/articles/:slug");
  const slug = params?.slug || "";
  const [article, setArticle] = useState<ArticleCard | null | undefined>(undefined);
  const [related, setRelated] = useState<ArticleCard[]>([]);

  useEffect(() => {
    let alive = true;
    (async () => {
      setArticle(undefined);
      const a = await fetchOne(slug);
      if (!alive) return;
      setArticle(a || null);
      if (a) {
        const list = await fetchList({ category: a.category, limit: 8 });
        if (alive) setRelated(list.filter((x) => x.slug !== a.slug).slice(0, 5));
      }
    })();
    return () => { alive = false; };
  }, [slug]);

  const sections = useMemo(() => extractToc(article?.body || ""), [article?.body]);

  if (article === undefined) {
    return <div className="container py-24 text-center text-sm text-[oklch(0.45_0.02_145)]">Loading…</div>;
  }
  if (article === null) {
    return (
      <div className="container py-24 text-center">
        <h1 className="text-3xl font-semibold">Essay not found</h1>
        <p className="mt-3 text-[oklch(0.45_0.02_145)]">It might still be in the queue. Try the library.</p>
        <Link href="/articles" className="mt-6 inline-flex ar-pill" data-active="true">Back to library</Link>
      </div>
    );
  }

  const published = new Date(article.published_at);
  const modified = article.last_modified_at ? new Date(article.last_modified_at) : null;

  function onShare() {
    const url = `${location.origin}/articles/${article!.slug}`;
    if (navigator.share) {
      navigator.share({ title: article!.title, url }).catch(() => {});
    } else {
      navigator.clipboard.writeText(url).then(() => toast.success("Link copied"));
    }
  }

  return (
    <article className="pb-16">
      {/* ── Hero ─────────────────────────────────────────────── */}
      <div className="relative">
        <div className="container pt-8 md:pt-12">
          <Link href="/articles" className="inline-flex items-center gap-1.5 text-sm text-[oklch(0.45_0.02_145)] hover:text-[oklch(0.30_0.02_145)]">
            <ChevronLeft className="h-4 w-4" /> Back to library
          </Link>
        </div>
        <div className="container mt-5 grid md:grid-cols-12 gap-6 items-end">
          <div className="md:col-span-7">
            <span className="ar-pill mb-4">{article.category}</span>
            <h1 className="text-3xl md:text-5xl font-semibold leading-[1.1] tracking-tight">
              {article.title}
            </h1>
            {article.excerpt && (
              <p className="mt-4 text-lg md:text-xl text-[oklch(0.40_0.02_145)] max-w-2xl leading-relaxed">
                {article.excerpt}
              </p>
            )}
            <div className="mt-5 flex flex-wrap items-center gap-3 text-sm text-[oklch(0.45_0.02_145)]">
              <span>By <a href="https://theoraclelover.com" rel="author noopener" className="font-medium text-[oklch(0.30_0.02_145)] hover:underline">The Oracle Lover</a></span>
              <span className="text-[oklch(0.78_0.06_152)]">·</span>
              <time dateTime={published.toISOString()}>
                {published.toLocaleDateString(undefined, { month: "long", day: "numeric", year: "numeric" })}
              </time>
              {modified && modified.getTime() > published.getTime() + 86400000 && (
                <>
                  <span className="text-[oklch(0.78_0.06_152)]">·</span>
                  <span>Updated {modified.toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" })}</span>
                </>
              )}
              {article.word_count ? (
                <>
                  <span className="text-[oklch(0.78_0.06_152)]">·</span>
                  <span>{Math.round(article.word_count / 220)} min read</span>
                </>
              ) : null}
              <button onClick={onShare} className="ml-auto ar-pill"><Share2 className="h-3.5 w-3.5" /> Share</button>
            </div>
          </div>
          <div className="md:col-span-5">
            <div className="ar-card relative aspect-[4/3] md:aspect-[5/6]">
              <img src={article.hero_url} alt={article.title} className="absolute inset-0 h-full w-full object-cover" />
            </div>
          </div>
        </div>
      </div>

      {/* ── Pill TOC (horizontal) ───────────────────────────── */}
      {sections.length > 1 && (
        <div className="container mt-10">
          <div className="ar-card px-4 py-3 overflow-x-auto">
            <div className="flex items-center gap-2 whitespace-nowrap">
              <span className="text-xs uppercase tracking-[.18em] text-[oklch(0.45_0.075_150)] mr-2">In this essay</span>
              {sections.map((s) => (
                <a key={s.id} href={`#${s.id}`} className="ar-pill">{s.title}</a>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ── 60/40 Body + Right column ──────────────────────── */}
      <div className="container mt-10 grid md:grid-cols-12 gap-10">
        <div className="md:col-span-7">
          {article.body && firstParagraph(article.body) && (
            <div className="ar-tldr" data-tldr="ai-overview">
              <p className="text-xs uppercase tracking-[.16em] text-[oklch(0.45_0.075_150)] mb-1">TL;DR</p>
              <p className="text-[15.5px] leading-relaxed">{firstParagraph(article.body)}</p>
            </div>
          )}
          <div className="ar-prose" dangerouslySetInnerHTML={{ __html: article.body || "" }} />
          <div className="mt-12 ar-card p-5 flex items-start gap-3 border-l-4 border-[oklch(0.72_0.115_80)]">
            <AlertTriangle className="h-5 w-5 mt-0.5 text-[oklch(0.55_0.10_80)]" />
            <p className="text-sm text-[oklch(0.40_0.02_145)] leading-relaxed">
              This article is for educational purposes only and is not medical advice.
              Autoimmune conditions require medical supervision. Always work with your
              healthcare team before changing medications or starting new supplements.
            </p>
          </div>
        </div>

        {/* ── Right rail (40%): image gallery + related ────── */}
        <aside className="md:col-span-5 space-y-6">
          <div className="ar-card overflow-hidden">
            <div className="relative aspect-[4/5]">
              <img src={article.hero_url} alt="" aria-hidden className="absolute inset-0 h-full w-full object-cover" />
            </div>
            <div className="p-5">
              <p className="text-xs uppercase tracking-[.18em] text-[oklch(0.45_0.075_150)] mb-2">Original illustration</p>
              <p className="text-sm text-[oklch(0.40_0.02_145)] leading-relaxed">
                Painted for {article.title} — soft watercolor on warm cream paper.
              </p>
            </div>
          </div>

          {related.length > 0 && (
            <div className="ar-card p-5">
              <h2 className="text-base font-semibold mb-3">More on {article.category}</h2>
              <ul className="divide-y divide-[oklch(0.90_0.012_95)]">
                {related.map((r) => (
                  <li key={r.slug} className="py-3">
                    <Link href={`/articles/${r.slug}`} className="flex gap-3 group">
                      <div className="relative h-16 w-20 flex-shrink-0 rounded-lg overflow-hidden">
                        <img src={r.hero_url} alt="" aria-hidden className="absolute inset-0 h-full w-full object-cover" />
                      </div>
                      <div>
                        <p className="text-sm font-medium leading-snug group-hover:underline">{r.title}</p>
                        <p className="mt-1 text-xs text-[oklch(0.45_0.02_145)]">
                          {new Date(r.published_at).toLocaleDateString(undefined, { month: "short", day: "numeric" })}
                        </p>
                      </div>
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="ar-card p-5 bg-[oklch(0.95_0.040_152/0.4)]">
            <p className="text-xs uppercase tracking-[.18em] text-[oklch(0.45_0.075_150)] mb-2">From The Oracle Lover</p>
            <p className="text-sm leading-relaxed">
              The body keeps a record. When the immune system flares, it's writing one of the chapters.
              <a href="https://theoraclelover.com" rel="noopener" className="ml-1 underline">Read the body wisdom essays →</a>
            </p>
          </div>
        </aside>
      </div>
    </article>
  );
}

function extractToc(html: string): { id: string; title: string }[] {
  const re = /<h2[^>]*(?:\sid="([^"]+)")?[^>]*>([^<]+)<\/h2>/gi;
  const out: { id: string; title: string }[] = [];
  let m;
  while ((m = re.exec(html)) !== null) {
    const title = m[2].trim();
    const id = m[1] || title.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
    out.push({ id, title });
  }
  return out;
}

function firstParagraph(html: string): string | null {
  const m = /<p[^>]*>([^<]+)<\/p>/.exec(html);
  if (!m) return null;
  const text = m[1].trim();
  if (text.length < 60) return null;
  return text.length > 360 ? text.slice(0, 357) + "…" : text;
}
