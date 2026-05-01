import { Link, useLocation } from "wouter";
import { Home as HomeIcon, Search, Sparkles, FlaskConical, Info } from "lucide-react";

export default function SiteShell({ children }: { children: React.ReactNode }) {
  const [location] = useLocation();
  const isActive = (p: string) => (p === "/" ? location === "/" : location.startsWith(p));

  return (
    <div className="min-h-screen flex flex-col">
      {/* ── Top brand bar ───────────────────────────────────────────── */}
      <header className="sticky top-0 z-40 backdrop-blur-md bg-[oklch(0.974_0.012_95/0.85)] border-b border-[oklch(0.88_0.015_95)]">
        <div className="container flex items-center justify-between py-3">
          <Link href="/" className="flex items-center gap-3">
            <span className="inline-flex h-9 w-9 items-center justify-center rounded-full bg-[oklch(0.93_0.045_152/0.55)] border border-[oklch(0.78_0.06_152)]">
              <svg viewBox="0 0 64 64" className="h-5 w-5">
                <path d="M32 50 C32 38 28 32 22 28" stroke="#C4943A" strokeWidth="2.5" strokeLinecap="round" fill="none"/>
                <ellipse cx="22" cy="20" rx="9" ry="12" transform="rotate(-25 22 20)" fill="#5A8F6A"/>
                <ellipse cx="42" cy="20" rx="9" ry="12" transform="rotate(25 42 20)" fill="#5A8F6A"/>
              </svg>
            </span>
            <span className="leading-tight">
              <span className="block font-[var(--font-display)] text-[1.05rem] font-semibold tracking-tight">
                Immune Rebuilt
              </span>
              <span className="block text-[11px] uppercase tracking-[.18em] text-[oklch(0.45_0.02_145)]">
                Reverse the fire within
              </span>
            </span>
          </Link>
          <nav className="hidden md:flex items-center gap-1">
            <NavPill href="/" active={isActive("/")}>Home</NavPill>
            <NavPill href="/articles" active={isActive("/articles")}>Articles</NavPill>
            <NavPill href="/assessments" active={isActive("/assessments")}>Assessments</NavPill>
            <NavPill href="/apothecary" active={isActive("/apothecary")}>Apothecary</NavPill>
            <NavPill href="/about" active={isActive("/about")}>About</NavPill>
            <NavPill href="/contact" active={isActive("/contact")}>Contact</NavPill>
          </nav>
        </div>
      </header>

      <main className="flex-1 pb-24 md:pb-0">{children}</main>

      {/* ── Footer ─────────────────────────────────────────────────── */}
      <footer className="mt-24 border-t border-[oklch(0.88_0.015_95)] bg-[oklch(0.97_0.010_95/0.6)]">
        <div className="container py-12 grid gap-8 md:grid-cols-3">
          <div>
            <h3 className="text-lg font-semibold mb-2">Reset Library</h3>
            <p className="text-sm text-[oklch(0.45_0.02_145)] max-w-sm">
              Independent essays on autoimmune root causes, the AIP protocol, leaky gut,
              functional medicine, and the emotional roots of chronic illness. No sponsors. No fluff.
            </p>
          </div>
          <div>
            <h4 className="text-sm font-semibold tracking-wide uppercase mb-3 text-[oklch(0.40_0.04_152)]">Read</h4>
            <ul className="space-y-1.5 text-sm">
              <li><Link href="/articles" className="hover:underline">All articles</Link></li>
              <li><Link href="/assessments" className="hover:underline">Self-screen assessments</Link></li>
              <li><Link href="/apothecary" className="hover:underline">Apothecary</Link></li>
              <li><Link href="/about" className="hover:underline">About this site</Link></li>
              <li><Link href="/contact" className="hover:underline">Contact</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="text-sm font-semibold tracking-wide uppercase mb-3 text-[oklch(0.40_0.04_152)]">Fine print</h4>
            <ul className="space-y-1.5 text-sm">
              <li><Link href="/disclosures" className="hover:underline">Disclosures &amp; medical disclaimer</Link></li>
              <li><Link href="/privacy" className="hover:underline">Privacy</Link></li>
              <li>
                <a href="https://theoraclelover.com" rel="noopener" className="hover:underline">
                  The Oracle Lover →
                </a>
              </li>
            </ul>
          </div>
        </div>
        <div className="border-t border-[oklch(0.88_0.015_95)]">
          <div className="container py-5 text-xs text-[oklch(0.45_0.02_145)] flex flex-wrap items-center justify-between gap-3">
            <span>© {new Date().getFullYear()} Immune Rebuilt. Educational; not medical advice.</span>
            <span>Hand-built. Reader supported.</span>
          </div>
        </div>
      </footer>

      {/* ── Mobile bottom tab bar ─────────────────────────────────── */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 z-40 border-t border-[oklch(0.88_0.015_95)] bg-[oklch(0.974_0.012_95/0.94)] backdrop-blur-md">
        <ul className="grid grid-cols-5">
          <BottomTab href="/" icon={<HomeIcon className="h-5 w-5" />} label="Home" active={isActive("/")} />
          <BottomTab href="/articles" icon={<Search className="h-5 w-5" />} label="Read" active={isActive("/articles")} />
          <BottomTab href="/assessments" icon={<Sparkles className="h-5 w-5" />} label="Screen" active={isActive("/assessments")} />
          <BottomTab href="/apothecary" icon={<FlaskConical className="h-5 w-5" />} label="Apothecary" active={isActive("/apothecary")} />
          <BottomTab href="/about" icon={<Info className="h-5 w-5" />} label="About" active={isActive("/about")} />
        </ul>
      </nav>
    </div>
  );
}

function NavPill({ href, active, children }: { href: string; active: boolean; children: React.ReactNode }) {
  return (
    <Link href={href} className="ar-pill" data-active={active ? "true" : "false"}>
      {children}
    </Link>
  );
}

function BottomTab({ href, icon, label, active }: { href: string; icon: React.ReactNode; label: string; active: boolean }) {
  return (
    <li>
      <Link
        href={href}
        className={`flex flex-col items-center justify-center py-2.5 text-[11px] ${active ? "text-[oklch(0.45_0.075_150)]" : "text-[oklch(0.45_0.02_145)]"}`}
      >
        {icon}
        <span className="mt-1">{label}</span>
      </Link>
    </li>
  );
}
