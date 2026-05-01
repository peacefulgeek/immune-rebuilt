import { useEffect, useState } from "react";
import { Link, useSearch } from "wouter";
import { fetchList, type ArticleCard, CATEGORIES } from "@/lib/articles";
import { Search } from "lucide-react";

export default function Articles() {
  const search = useSearch();
  const initialQ = new URLSearchParams(search).get("q") || "";
  const initialCat = new URLSearchParams(search).get("category") || "";
  const [q, setQ] = useState(initialQ);
  const [cat, setCat] = useState(initialCat);
  const [items, setItems] = useState<ArticleCard[] | null>(null);

  useEffect(() => {
    let alive = true;
    (async () => {
      setItems(null);
      const list = await fetchList({ q, category: cat, limit: 200 });
      if (alive) setItems(list);
    })();
    return () => { alive = false; };
  }, [q, cat]);

  return (
    <div className="container py-12 md:py-16">
      <header className="max-w-2xl mb-10">
        <p className="text-xs uppercase tracking-[.18em] text-[oklch(0.45_0.075_150)] mb-2">All essays</p>
        <h1 className="text-3xl md:text-4xl font-semibold tracking-tight">The Reset Library</h1>
        <p className="mt-3 text-[oklch(0.40_0.02_145)] text-lg">
          Every essay on autoimmune root causes, the AIP protocol, leaky gut,
          functional medicine, and the emotional roots underneath.
        </p>
      </header>

      <div className="grid md:grid-cols-12 gap-6 mb-8">
        <label className="md:col-span-7 ar-card flex items-center gap-3 px-4 py-3">
          <Search className="h-4 w-4 text-[oklch(0.45_0.02_145)]" />
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search Hashimoto's, AIP, leaky gut, MS, lupus, EBV…"
            className="bg-transparent flex-1 outline-none text-sm"
          />
        </label>
        <div className="md:col-span-5 flex flex-wrap items-center gap-2">
          <button onClick={() => setCat("")} className="ar-pill" data-active={!cat ? "true" : "false"}>All</button>
          {CATEGORIES.map((c) => (
            <button key={c} onClick={() => setCat(c)} className="ar-pill" data-active={cat === c ? "true" : "false"}>
              {c}
            </button>
          ))}
        </div>
      </div>

      {items === null && <p className="text-sm text-[oklch(0.45_0.02_145)]">Loading essays…</p>}
      {items && items.length === 0 && (
        <div className="ar-card p-8 text-center">
          <p className="text-base font-medium">No essays match that search yet.</p>
          <p className="mt-1 text-sm text-[oklch(0.45_0.02_145)]">
            New writing publishes throughout the week. Try a broader keyword or clear the filter.
          </p>
        </div>
      )}

      <div className="grid gap-5" style={{ gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))" }}>
        {(items || []).map((a, i) => (
          <Link key={a.slug} href={`/articles/${a.slug}`} className="ar-card block group">
            <div className={`relative ${i % 5 === 0 ? "aspect-[3/4]" : "aspect-[4/3]"}`}>
              <img src={a.hero_url} alt={a.title} loading="lazy" className="absolute inset-0 h-full w-full object-cover group-hover:scale-[1.02] transition-transform duration-500" />
              <div className="absolute inset-0 bg-gradient-to-t from-[oklch(0.20_0.02_145/0.55)] via-transparent to-transparent" />
              <span className="absolute top-3 left-3 ar-pill bg-white/85 text-xs">{a.category}</span>
              <div className="absolute inset-x-0 bottom-0 p-4">
                <h3 className="text-lg font-semibold leading-snug text-white drop-shadow-md">{a.title}</h3>
              </div>
            </div>
            <div className="p-4">
              <p className="text-sm text-[oklch(0.40_0.02_145)] line-clamp-3">{a.excerpt}</p>
              <div className="mt-3 text-[11px] uppercase tracking-[.16em] text-[oklch(0.45_0.075_150)]">
                {new Date(a.published_at).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" })}
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
