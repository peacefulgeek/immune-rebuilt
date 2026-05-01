import { useEffect, useState } from "react";
import { Link } from "wouter";
import { fetchList, type ArticleCard, CATEGORIES } from "@/lib/articles";
import { Sparkles, ArrowRight, Leaf, HeartPulse, Brain, Soup, Sun } from "lucide-react";

const HERO_BG = "/manus-storage/ar-hero-meadow_7c7e75c3.webp";

const COLLAGE = [
  { src: "/manus-storage/ar-hero-pantry_b84fb324.webp",     label: "AIP-friendly pantry, painted in the morning light." },
  { src: "/manus-storage/ar-hero-breath_ada4791b.webp",     label: "Vagal tone, hand on chest, the longer exhale." },
  { src: "/manus-storage/ar-hero-microbiome_b2c03180.webp", label: "What the gut whispers to the immune system." },
  { src: "/manus-storage/ar-hero-journal_dca16fec.webp",    label: "Slow journal pages, stress as data." },
];

const CATEGORY_DECOR: Record<string, { icon: any; tint: string }> = {
  "AIP & Diet":               { icon: Soup,       tint: "oklch(0.95 0.030 100)" },
  "Stress & Nervous System":  { icon: HeartPulse, tint: "oklch(0.95 0.040 80)"  },
  "Emotional Roots":          { icon: Brain,      tint: "oklch(0.93 0.045 152)" },
  "Gut Healing":              { icon: Leaf,       tint: "oklch(0.93 0.040 130)" },
  "Functional Medicine":      { icon: Sun,        tint: "oklch(0.95 0.030 90)"  },
};

export default function Home() {
  const [items, setItems] = useState<ArticleCard[] | null>(null);
  const [activeCat, setActiveCat] = useState<string>("");

  useEffect(() => {
    let alive = true;
    (async () => {
      const list = await fetchList({ limit: 60 });
      if (alive) setItems(list);
    })();
    return () => { alive = false; };
  }, []);

  const filtered = activeCat ? (items || []).filter((a) => a.category === activeCat) : items || [];
  const featured = filtered[0];
  const rest = filtered.slice(1);

  return (
    <div>
      <section className="relative overflow-hidden">
        <div
          className="absolute inset-0 -z-10"
          style={{
            backgroundImage: `linear-gradient(180deg, oklch(0.974 0.012 95 / 0.40) 0%, oklch(0.974 0.012 95 / 0.92) 75%), url(${HERO_BG})`,
            backgroundSize: "cover",
            backgroundPosition: "center 30%",
          }}
        />
        <div className="container pt-14 md:pt-24 pb-10 md:pb-20 relative">
          <div className="grid md:grid-cols-12 gap-10 items-end">
            <div className="md:col-span-7">
              <span className="ar-pill mb-5">
                <Sparkles className="h-3.5 w-3.5" />
                The Oracle Lover network
              </span>
              <h1 className="text-[2.4rem] md:text-[3.6rem] leading-[1.05] font-semibold tracking-tight">
                Your immune system <em className="not-italic text-[oklch(0.45_0.075_150)]">isn't</em> attacking you.
                <br className="hidden md:block" />
                <span className="font-normal text-[oklch(0.40_0.04_152)]">It's responding to something.</span>
              </h1>
              <p className="mt-5 text-lg md:text-xl max-w-xl text-[oklch(0.40_0.02_145)] leading-relaxed">
                Honest writing about autoimmune root causes — AIP, leaky gut,
                the HPA axis, the things doctors don't have time to explain. Quietly, and without panic.
              </p>
              <div className="mt-7 flex flex-wrap gap-3">
                <Link href="/articles" className="inline-flex items-center gap-2 rounded-full bg-[oklch(0.45_0.075_150)] text-white px-5 py-2.5 text-sm font-medium shadow-md hover:translate-y-[-1px] transition">
                  Read the articles <ArrowRight className="h-4 w-4" />
                </Link>
                <Link href="/about" className="inline-flex items-center gap-2 rounded-full border border-[oklch(0.78_0.06_152)] bg-white/60 px-5 py-2.5 text-sm font-medium hover:bg-white">
                  What this site believes
                </Link>
              </div>
            </div>

            <div className="md:col-span-5">
              <div className="grid grid-cols-2 gap-3">
                {COLLAGE.map((c) => (
                  <figure key={c.src} className="ar-card p-0 relative aspect-[4/5]">
                    <img
                      src={c.src}
                      alt={c.label}
                      loading="lazy"
                      decoding="async"
                      className="absolute inset-0 h-full w-full object-cover"
                    />
                    <figcaption className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-[oklch(0.974_0.012_95/0.92)] via-[oklch(0.974_0.012_95/0.45)] to-transparent p-3">
                      <span className="text-xs font-medium leading-snug text-[oklch(0.30_0.02_145)]">
                        {c.label}
                      </span>
                    </figcaption>
                  </figure>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="container">
        <div className="flex flex-wrap items-center gap-2 py-6 border-y border-[oklch(0.88_0.015_95)]">
          <button onClick={() => setActiveCat("")} className="ar-pill" data-active={!activeCat ? "true" : "false"}>
            All essays
          </button>
          {CATEGORIES.map((c) => (
            <button key={c} onClick={() => setActiveCat(c)} className="ar-pill" data-active={activeCat === c ? "true" : "false"}>
              {c}
            </button>
          ))}
        </div>
      </section>

      {featured && (
        <section className="container py-10 md:py-14">
          <FeaturedCard card={featured} />
        </section>
      )}

      <section className="container pb-20 md:pb-24">
        <h2 className="text-2xl md:text-3xl font-semibold mb-6">More from the Reset Library</h2>
        {items === null && <p className="text-sm text-[oklch(0.45_0.02_145)]">Loading the library…</p>}
        {items && rest.length === 0 && (
          <p className="text-sm text-[oklch(0.45_0.02_145)]">
            New essays land here every few days. The first set is being prepared.
          </p>
        )}
        <div className="grid gap-5" style={{ gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))" }}>
          {rest.map((a, i) => <ArticleCardGrid key={a.slug} card={a} idx={i} />)}
        </div>
      </section>
    </div>
  );
}

function FeaturedCard({ card }: { card: ArticleCard }) {
  return (
    <Link href={`/articles/${card.slug}`} className="ar-card grid md:grid-cols-12 overflow-hidden">
      <div className="relative md:col-span-7 aspect-[16/10] md:aspect-auto md:min-h-[420px]">
        <img src={card.hero_url} alt={card.title} className="absolute inset-0 h-full w-full object-cover" />
        <div className="absolute inset-0 bg-gradient-to-t from-[oklch(0.20_0.02_145/0.45)] via-transparent to-transparent" />
        <span className="absolute top-4 left-4 ar-pill bg-white/90">{card.category}</span>
      </div>
      <div className="md:col-span-5 p-7 md:p-10 flex flex-col justify-between">
        <div>
          <p className="text-xs uppercase tracking-[.18em] text-[oklch(0.45_0.075_150)] mb-3">Featured essay</p>
          <h3 className="text-2xl md:text-3xl font-semibold leading-tight">{card.title}</h3>
          <p className="mt-4 text-[oklch(0.40_0.02_145)] leading-relaxed">{card.excerpt}</p>
        </div>
        <div className="mt-6 flex items-center gap-3 text-sm">
          <span className="text-[oklch(0.45_0.02_145)]">By The Oracle Lover</span>
          <span className="text-[oklch(0.78_0.06_152)]">·</span>
          <time className="text-[oklch(0.45_0.02_145)]">
            {new Date(card.published_at).toLocaleDateString(undefined, { month: "long", day: "numeric", year: "numeric" })}
          </time>
        </div>
      </div>
    </Link>
  );
}

function ArticleCardGrid({ card, idx }: { card: ArticleCard; idx: number }) {
  const decor = CATEGORY_DECOR[card.category];
  const tall = idx % 5 === 0 || idx % 7 === 3;
  return (
    <Link href={`/articles/${card.slug}`} className="ar-card block group">
      <div className={`relative ${tall ? "aspect-[3/4]" : "aspect-[4/3]"}`}>
        <img
          src={card.hero_url}
          alt={card.title}
          loading="lazy"
          decoding="async"
          className="absolute inset-0 h-full w-full object-cover group-hover:scale-[1.02] transition-transform duration-500"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-[oklch(0.20_0.02_145/0.55)] via-[oklch(0.20_0.02_145/0.05)] to-transparent" />
        <span className="absolute top-3 left-3 ar-pill bg-white/85 text-xs">
          {decor?.icon ? <decor.icon className="h-3.5 w-3.5" /> : null}
          {card.category}
        </span>
        <div className="absolute inset-x-0 bottom-0 p-4">
          <h3 className="text-lg font-semibold leading-snug text-white drop-shadow-md">
            {card.title}
          </h3>
        </div>
      </div>
      <div className="p-4">
        <p className="text-sm text-[oklch(0.40_0.02_145)] line-clamp-3">{card.excerpt}</p>
        <div className="mt-3 text-[11px] uppercase tracking-[.16em] text-[oklch(0.45_0.075_150)]">
          {new Date(card.published_at).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" })}
        </div>
      </div>
    </Link>
  );
}
