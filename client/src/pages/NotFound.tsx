import { Link } from "wouter";

export default function NotFound() {
  return (
    <div className="container py-24 md:py-32 text-center max-w-2xl">
      <p className="text-xs uppercase tracking-[.18em] text-[oklch(0.45_0.075_150)]">404</p>
      <h1 className="mt-3 text-4xl md:text-5xl font-semibold tracking-tight">That essay isn't here.</h1>
      <p className="mt-4 text-[oklch(0.45_0.02_145)] text-lg">
        The library reorganises itself sometimes. Try the index.
      </p>
      <Link href="/articles" className="mt-8 inline-flex ar-pill" data-active="true">Browse the library</Link>
    </div>
  );
}
