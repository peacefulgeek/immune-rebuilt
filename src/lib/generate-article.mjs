// Generate one article end-to-end: prompt → engine → gate → repair-if-needed.
// Master scope §15: regenerate-on-fail up to N attempts, then escalate. Never publish a failure.

import { generate } from "./engine.mjs";
import { gateOrThrow, checkText } from "./gate.mjs";
import { SYSTEM_PROMPT, buildUserPrompt } from "./voice.mjs";

const MAX_ATTEMPTS = 4;

function stripEmDashes(text) {
  // Em-dash and en-dash are zero-tolerance. Replace with a comma + space.
  return text
    .replace(/\s*—\s*/g, ", ")
    .replace(/\s*–\s*/g, ", ")
    .replace(/, , /g, ", ");
}

export async function generateArticle({ title, slug, category, angle, must_cover, asins, related_slugs }) {
  const sys = SYSTEM_PROMPT;
  const usr = buildUserPrompt({ title, slug, category, angle, must_cover, asins, related_slugs });

  let last_err = null;
  let last_text = "";
  let last_gate = null;

  for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt++) {
    let text;
    try {
      text = await generate({ system: sys, user: usr, temperature: 0.55 });
    } catch (e) {
      last_err = e;
      continue;
    }

    // Pre-clean obvious AI tells before testing the gate
    text = stripEmDashes(text);

    const gate = checkText(text);
    last_text = text;
    last_gate = gate;

    if (gate.ok) {
      return { html: text, attempts: attempt, gate };
    }

    // Build a corrective second pass that names exactly what failed
    const corrective = [
      "Your previous draft failed the editorial gate. Fix all of these without rewriting your voice:",
      ...gate.reasons.map(r => "- " + r),
      "Do not introduce em-dashes (—) or en-dashes (–) at all.",
      "Keep the same essay; produce a corrected full HTML body.",
    ].join("\n");

    try {
      text = await generate({
        system: sys,
        user: usr + "\n\n" + corrective + "\n\nPrevious draft:\n" + text.slice(0, 6000),
        temperature: 0.4,
      });
      text = stripEmDashes(text);
      const g2 = checkText(text);
      last_text = text;
      last_gate = g2;
      if (g2.ok) return { html: text, attempts: attempt + 1, gate: g2 };
    } catch (e) {
      last_err = e;
    }
  }

  const err = new Error(`Article failed quality gate after ${MAX_ATTEMPTS} attempts.`);
  err.last_text = last_text;
  err.last_gate = last_gate;
  err.last_err = last_err;
  throw err;
}

export { gateOrThrow };
