// Writing quality gate.
// Union of all banned word/phrase lists across master scope §12 + WRITINGQUALITYGATEADDENDUM 1..73.
// No item dropped. Em-dash count must be zero. Token-style "AI tells" suppressed.
//
// Returns { ok, reasons[], em_dashes, banned_hits[], soft_signals[] }.

const HARD_BANNED = [
  // Tone, hedging, AI-tells (master scope §12A + addendum)
  "delve", "delves", "delving",
  "navigate", "navigates", "navigating", "navigation",
  "leverage", "leverages", "leveraging",
  "harness", "harnesses", "harnessing",
  "unleash", "unleashes", "unleashing",
  "unlock", "unlocks", "unlocking",
  "unveil", "unveils", "unveiling",
  "embark", "embarks", "embarking",
  "journey", "journeys",
  "tapestry", "tapestries",
  "realm", "realms",
  "myriad",
  "multifaceted",
  "holistic approach",
  "in today's fast-paced world",
  "in today's world",
  "in the realm of",
  "in the world of",
  "world of",
  "game-changer", "game changer",
  "game-changing",
  "cutting-edge",
  "state-of-the-art",
  "next-level",
  "level up",
  "ground-breaking", "groundbreaking",
  "robust",
  "seamless", "seamlessly",
  "synergy", "synergies", "synergistic",
  "paradigm",
  "paradigm shift",
  "ecosystem",
  "vibrant",
  "bustling",
  "navigating the complex",
  "the world of wellness",
  "imagine a world",
  "picture this",
  "let's dive in",
  "dive in", "dive into",
  "deep dive",
  "let's explore",
  "let me",
  "i'll",
  "i will",
  "first off",
  "in conclusion",
  "to sum up",
  "in summary",
  "in essence",
  "essentially,",
  "ultimately,",
  "moreover,",
  "furthermore,",
  "additionally,",
  "however, it's important to",
  "it's important to note",
  "it is important to note",
  "it's worth noting",
  "it is worth noting",
  "as we have seen",
  "as mentioned",
  "as discussed",
  "as previously",
  "without further ado",
  "rest assured",
  "fear not",
  "the truth is",
  "the reality is",
  "the fact of the matter",
  "at the end of the day",
  "when push comes to shove",
  "navigating the challenges",
  "in the grand scheme",
  "in this digital age",
  "the modern era",
  "the digital era",
  "this comprehensive guide",
  "comprehensive guide",
  "a deep understanding",
  "a deep dive into",
  "stay tuned",
  "buckle up",
  "let that sink in",
  "wrap your head around",
  "the takeaway",
  "key takeaways",
  "key takeaway",
  // Wellness-specific
  "skinny", "skinnier",
  "detox", "detoxify",
  "shred",
  "miracle cure",
  "miracle",
  "biohack", "biohacker", "biohacking",
  "optimize", "optimization", "optimizing", "optimized",
  "cure for cancer",
  "snake oil",
  "guaranteed",
  "instant results",
  "overnight",
  "secret weapon",
  "magic bullet",
  // Em-dash standins / overuse signals
  "—",
  "–",
];

const SOFT_FLAGS = [
  // Heuristic patterns we down-weight rather than hard-fail
  / very [a-z]+ very /i,
  / really really /i,
  / kind of, sort of /i,
];

export const HARD_BANNED_LOWER = HARD_BANNED.map((s) => s.toLowerCase());

export function checkText(input) {
  const text = String(input || "");
  const lower = text.toLowerCase();
  const reasons = [];
  const banned_hits = [];

  // Em-dash count must be exactly zero
  const emCount = (text.match(/—/g) || []).length;
  const enDashCount = (text.match(/–/g) || []).length;
  if (emCount > 0) {
    reasons.push(`em_dash_count=${emCount} (must be 0)`);
    banned_hits.push("em_dash");
  }
  if (enDashCount > 0) {
    reasons.push(`en_dash_count=${enDashCount} (must be 0)`);
    banned_hits.push("en_dash");
  }

  for (const term of HARD_BANNED_LOWER) {
    if (term === "—" || term === "–") continue; // already counted
    if (lower.includes(term)) {
      banned_hits.push(term);
    }
  }

  if (banned_hits.length) {
    reasons.push(`banned_hits=${banned_hits.length}: ${banned_hits.slice(0, 8).join(", ")}${banned_hits.length > 8 ? "…" : ""}`);
  }

  const soft_signals = [];
  for (const re of SOFT_FLAGS) {
    if (re.test(text)) soft_signals.push(re.source);
  }

  // Structural floors per master scope §10/§13
  const tldr_present = /TL;?DR/i.test(text);
  const has_h2 = /<h2[\s>]/i.test(text);
  const internal_links = (text.match(/href="\/articles\//g) || []).length;
  const external_links = (text.match(/href="https?:\/\/(?!(?:[a-z0-9-]+\.)?theautoimmunereset\.com|theautoimmunereset\.com)/g) || []).length;
  const self_ref = /(Immune Rebuilt|this site|this library)/i.test(text);

  if (!tldr_present) reasons.push("missing_tldr");
  if (!has_h2) reasons.push("missing_h2_structure");
  if (internal_links < 3) reasons.push(`internal_links=${internal_links} (need ≥3)`);
  if (external_links < 1) reasons.push(`external_authoritative_links=${external_links} (need ≥1)`);
  if (!self_ref) reasons.push("missing_self_reference");

  return {
    ok: reasons.length === 0,
    em_dashes: emCount,
    en_dashes: enDashCount,
    banned_hits,
    soft_signals,
    structural: { tldr_present, has_h2, internal_links, external_links, self_ref },
    reasons,
  };
}

export function gateOrThrow(text, label = "article") {
  const r = checkText(text);
  if (!r.ok) {
    const err = new Error(`Quality gate failed for ${label}: ${r.reasons.join("; ")}`);
    err.gate = r;
    throw err;
  }
  return r;
}
