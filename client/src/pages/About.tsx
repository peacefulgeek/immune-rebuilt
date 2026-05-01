export default function About() {
  return (
    <div className="container py-14 md:py-20 grid md:grid-cols-12 gap-10">
      <div className="md:col-span-7">
        <p className="text-xs uppercase tracking-[.18em] text-[oklch(0.45_0.075_150)] mb-2">About this site</p>
        <h1 className="text-3xl md:text-5xl font-semibold tracking-tight">
          Why Immune Rebuilt exists.
        </h1>
        <div className="ar-prose mt-8">
          <p>
            Immune Rebuilt is a writing project. It is not a clinic. It is not a brand.
            It is a long, careful conversation about why the immune system flares, what it's
            actually responding to, and how people in remission got there.
          </p>
          <p>
            We pull from researchers who do this work seriously: Sarah Ballantyne, Amy Myers,
            Donna Jackson Nakazawa, Terry Wahls, Alessio Fasano, Datis Kharrazian, Susan Blum,
            Tom O'Bryan, Gabor Maté, Aristo Vojdani. Their books are linked throughout.
          </p>
          <h2>What you'll find here</h2>
          <p>
            Essays on autoimmune root causes ,  leaky gut, the HPA axis, molecular mimicry,
            childhood trauma, environmental toxins, infections like EBV. Practical guides to
            AIP, the Wahls Protocol, food sensitivity testing, supplements for recovery.
            Honest conversation about the emotional work nobody warns you about.
          </p>
          <h2>Editorial standards</h2>
          <p>
            Every essay is written from a research base, then reviewed for accuracy and tone.
            We update articles when the science changes. We disclose every affiliate link.
            We never promise cures.
          </p>
          <h2>Who writes this</h2>
          <p>
            The Oracle Lover writes here ,  a longtime student of contemplative practice, body
            wisdom, and the places medicine and meaning meet. Read more at{" "}
            <a href="https://theoraclelover.com" rel="noopener">theoraclelover.com</a>.
          </p>
        </div>
      </div>
      <aside className="md:col-span-5 space-y-5">
        <div className="ar-card p-6">
          <h3 className="text-base font-semibold mb-3">What this site believes</h3>
          <ul className="space-y-3 text-sm leading-relaxed text-[oklch(0.40_0.02_145)]">
            <li>Your immune system isn't broken. It's responding to something. Find what.</li>
            <li>Medication and root-cause work are not enemies. They co-exist.</li>
            <li>The gut, the stress response, and the emotional body are one system.</li>
            <li>Remission exists. So does relapse. We talk honestly about both.</li>
          </ul>
        </div>
        <div className="ar-card p-6 bg-[oklch(0.95_0.040_152/0.35)]">
          <h3 className="text-base font-semibold mb-2">Sister site</h3>
          <p className="text-sm leading-relaxed">
            <a href="https://theoraclelover.com" rel="noopener" className="underline">The Oracle Lover</a>{" "}
            is the larger writing project this site grows out of ,  body wisdom, contemplative practice,
            and the slower kinds of healing.
          </p>
        </div>
      </aside>
    </div>
  );
}
