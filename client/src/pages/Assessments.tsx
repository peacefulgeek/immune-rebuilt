/**
 * Assessments hub. Lists all 11 self-screen instruments. Each card opens a
 * single-page interactive form whose score is computed in the browser.
 * Result panel includes a TL;DR sentence, a band label, a readable explanation,
 * and 2-3 internal article links. No data leaves the browser.
 */
import { Link, useParams } from "wouter";
import { useState, useMemo } from "react";
import { ASSESSMENTS, scoreAssessment, type Assessment } from "@/lib/assessments";

function Card({ a }: { a: Assessment }) {
  return (
    <Link href={`/assessments/${a.slug}`}>
      <a className="group block rounded-3xl border border-stone-200/80 bg-white/80 backdrop-blur p-6 hover:border-emerald-700/40 hover:shadow-lg hover:-translate-y-0.5 transition-all">
        <div className="text-xs uppercase tracking-widest text-emerald-800/80 font-semibold">
          {a.questions.length} questions , {Math.ceil(a.questions.length / 2)} min
        </div>
        <h3 className="mt-2 font-serif text-2xl text-stone-800 leading-tight group-hover:text-emerald-900">
          {a.title}
        </h3>
        <p className="mt-3 text-stone-600 text-sm leading-relaxed">{a.short}</p>
        <div className="mt-5 text-emerald-800 text-sm font-medium">Take the screen ,</div>
      </a>
    </Link>
  );
}

export function AssessmentsIndex() {
  return (
    <>
      <header className="container max-w-6xl pt-12 pb-8">
        <div className="text-xs uppercase tracking-widest text-emerald-800 font-semibold">Self-screens</div>
        <h1 className="font-serif text-4xl md:text-5xl text-stone-800 mt-3 leading-tight">
          Quiet, validated, free assessments
        </h1>
        <p className="mt-4 text-stone-700 max-w-2xl text-lg leading-relaxed">
          Eleven instruments that autoimmune patients tend to want, drawn from the public literature. Each one returns a number, a band, and a short paragraph that points you to what to read next on this site. Nothing you type leaves your browser.
        </p>
      </header>
      <main className="container max-w-6xl pb-24 grid md:grid-cols-2 lg:grid-cols-3 gap-5">
        {ASSESSMENTS.map((a) => <Card key={a.slug} a={a} />)}
      </main>
    </>
  );
}

function Detail({ a }: { a: Assessment }) {
  const [answers, setAnswers] = useState<Record<string, number>>({});
  const allAnswered = a.questions.every((q) => answers[q.id] !== undefined);
  const result = useMemo(() => (allAnswered ? scoreAssessment(a, answers) : null), [a, answers, allAnswered]);

  return (
    <>
      <article className="container max-w-3xl pt-10 pb-24">
        <Link href="/assessments"><a className="text-sm text-emerald-800 hover:underline">, All assessments</a></Link>
        <h1 className="font-serif text-3xl md:text-4xl text-stone-800 mt-3 leading-tight">{a.title}</h1>
        <p className="mt-3 text-stone-600">{a.short}</p>
        <div className="mt-2 text-xs text-stone-500">
          Source: {a.authorAttribution} , <a className="underline" href={a.source} rel="noopener noreferrer" target="_blank">reference</a>
        </div>
        <div className="mt-6 rounded-2xl border border-stone-200 bg-amber-50/40 p-5 text-sm text-stone-700">
          {a.about}
        </div>

        <ol className="mt-8 space-y-6">
          {a.questions.map((q, i) => (
            <li key={q.id} className="rounded-2xl border border-stone-200 bg-white p-5">
              <div className="flex gap-3">
                <span className="text-emerald-800 font-serif text-xl leading-none">{i+1}.</span>
                <div className="flex-1">
                  <div className="text-stone-800 leading-relaxed">{q.text}</div>
                  <div className="mt-3 grid grid-cols-2 sm:grid-cols-4 gap-2">
                    {q.choices.map((c) => {
                      const selected = answers[q.id] === c.value;
                      return (
                        <button
                          key={c.label}
                          type="button"
                          onClick={() => setAnswers((s) => ({ ...s, [q.id]: c.value }))}
                          className={`text-sm rounded-xl border px-3 py-2 text-left transition ${selected ? "bg-emerald-700 text-amber-50 border-emerald-700" : "bg-white text-stone-700 border-stone-200 hover:border-emerald-700/50"}`}
                        >
                          {c.label}
                        </button>
                      );
                    })}
                  </div>
                </div>
              </div>
            </li>
          ))}
        </ol>

        {result?.band && (
          <section className="mt-10 rounded-3xl border-2 border-emerald-700/30 bg-emerald-50/40 p-6">
            <div className="text-xs uppercase tracking-widest text-emerald-800 font-semibold">Your result</div>
            <div className="mt-2 font-serif text-3xl text-stone-800">Score {result.score} , {result.band.label}</div>
            <p className="mt-3 text-stone-700 leading-relaxed">{result.band.copy}</p>
            <div className="mt-5">
              <div className="text-xs uppercase tracking-widest text-emerald-800 font-semibold mb-2">What to read next</div>
              <ul className="space-y-2">
                {result.band.readNext.map((slug) => (
                  <li key={slug}>
                    <Link href={`/articles/${slug}`}><a className="text-emerald-800 hover:underline">, /articles/{slug}</a></Link>
                  </li>
                ))}
              </ul>
            </div>
          </section>
        )}
      </article>
    </>
  );
}

export function AssessmentDetail() {
  const params = useParams<{ slug: string }>();
  const a = ASSESSMENTS.find((x) => x.slug === params.slug);
  if (!a) {
    return (
      <>
        <div className="container max-w-2xl py-20 text-center">
          <h1 className="font-serif text-3xl">Not found</h1>
          <p className="mt-3 text-stone-600">That assessment is not in our library.</p>
          <Link href="/assessments"><a className="mt-6 inline-block text-emerald-800 hover:underline">, Back to all assessments</a></Link>
        </div>
      </>
    );
  }
  return <Detail a={a} />;
}
