/**
 * Apothecary: 50 vetted ASINs across supplements, herbs, TCM. Filterable by
 * family and category. Every Amazon link carries tag=spankyspinola-20 via
 * the helper in lib/apothecary. The disclosure banner runs on every view.
 */
import { useMemo, useState } from "react";
import { Link } from "wouter";
import { APOTHECARY, FAMILIES, CATEGORIES, amazonUrl, type Item } from "@/lib/apothecary";

export default function Apothecary() {
  const [family, setFamily] = useState<string>("All");
  const [category, setCategory] = useState<string>("All");
  const [q, setQ] = useState<string>("");

  const items = useMemo(() => {
    return APOTHECARY.filter((i) => {
      if (family !== "All" && i.family !== family) return false;
      if (category !== "All" && i.category !== category) return false;
      if (q && !(i.title + " " + i.brand + " " + i.whyHere).toLowerCase().includes(q.toLowerCase())) return false;
      return true;
    });
  }, [family, category, q]);

  return (
    <>
      <header className="container max-w-6xl pt-12 pb-6">
        <div className="text-xs uppercase tracking-widest text-emerald-800 font-semibold">Apothecary</div>
        <h1 className="font-serif text-4xl md:text-5xl text-stone-800 mt-3 leading-tight">
          Fifty things, considered, not pushed
        </h1>
        <p className="mt-4 text-stone-700 max-w-2xl text-lg leading-relaxed">
          Supplements, herbs, and traditional Chinese medicine items we have actually thought about, with a one-line reason for each. None of these replace clinical care. Where there is a real risk, it is named.
        </p>
        <p className="mt-3 text-sm text-stone-500 max-w-2xl">
          Affiliate disclosure: Immune Rebuilt participates in the Amazon Services LLC Associates Program. As an Amazon Associate we earn from qualifying purchases. Your price does not change.
        </p>
      </header>

      <div className="container max-w-6xl pb-4 flex flex-wrap gap-3 items-center">
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search..."
          className="rounded-xl border border-stone-200 bg-white px-3 py-2 text-sm w-full md:w-64"
        />
        <select value={family} onChange={(e) => setFamily(e.target.value)} className="rounded-xl border border-stone-200 bg-white px-3 py-2 text-sm">
          <option value="All">All families</option>
          {FAMILIES.map((f) => <option key={f} value={f}>{f}</option>)}
        </select>
        <select value={category} onChange={(e) => setCategory(e.target.value)} className="rounded-xl border border-stone-200 bg-white px-3 py-2 text-sm">
          <option value="All">All categories</option>
          {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
        </select>
        <div className="text-sm text-stone-500">{items.length} of {APOTHECARY.length}</div>
      </div>

      <main className="container max-w-6xl pb-24 grid md:grid-cols-2 lg:grid-cols-3 gap-5">
        {items.map((i) => <Card key={i.asin} i={i} />)}
      </main>
    </>
  );
}

function Card({ i }: { i: Item }) {
  return (
    <article className="rounded-3xl border border-stone-200/80 bg-white/80 backdrop-blur p-5 flex flex-col gap-3">
      <div className="flex items-center gap-2 text-xs">
        <span className="px-2 py-0.5 rounded-full bg-emerald-700/10 text-emerald-800 font-semibold uppercase tracking-widest">{i.family}</span>
        <span className="px-2 py-0.5 rounded-full bg-amber-700/10 text-amber-800 font-semibold uppercase tracking-widest">{i.category}</span>
      </div>
      <div>
        <div className="font-serif text-lg text-stone-800 leading-snug">{i.title}</div>
        <div className="text-sm text-stone-500 mt-0.5">{i.brand}</div>
      </div>
      <p className="text-sm text-stone-700 leading-relaxed">{i.whyHere}</p>
      <p className="text-sm text-stone-600"><span className="text-stone-500 uppercase tracking-widest text-xs">Best for: </span>{i.bestFor}</p>
      {i.warning && (
        <p className="text-sm text-amber-900 bg-amber-50 border border-amber-200 rounded-xl px-3 py-2">
          <span className="text-xs uppercase tracking-widest font-semibold">Caution: </span>{i.warning}
        </p>
      )}
      <div className="mt-auto flex items-center gap-3 pt-2">
        <a
          href={amazonUrl(i.asin)}
          target="_blank"
          rel="sponsored noopener noreferrer"
          className="inline-flex items-center gap-2 rounded-xl bg-emerald-700 hover:bg-emerald-800 text-amber-50 px-4 py-2 text-sm font-semibold transition"
        >
          View on Amazon ,
        </a>
        {i.internalSlug && (
          <Link href={`/articles/${i.internalSlug}`}>
            <a className="text-sm text-emerald-800 hover:underline">read the deep-write</a>
          </Link>
        )}
      </div>
    </article>
  );
}
