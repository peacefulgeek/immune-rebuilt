// Writing engine — Final Pass §1: Claude is the primary writer.
// Anthropic Messages API (claude-sonnet-4-5 by default; CLAUDE_MODEL overrides).
// If CLAUDE_API_KEY is unset, falls back to the OpenAI-compatible engine
// (DeepSeek by default) so existing generator/refresh/rewrite paths still run.
// Master scope §0 hard rule: when CLAUDE_API_KEY is set we ONLY hit
// api.anthropic.com. fal.ai / manus.im / fal.run remain explicitly banned.
import OpenAI from "openai";

const CLAUDE_API_KEY = (process.env.CLAUDE_API_KEY || "").trim();
const CLAUDE_MODEL = (process.env.CLAUDE_MODEL || "claude-sonnet-4-5").trim();
const CLAUDE_BASE = "https://api.anthropic.com/v1/messages";
const CLAUDE_VERSION = "2023-06-01";

function _pickBaseURL() {
  const raw = (process.env.OPENAI_BASE_URL || "").trim();
  if (!raw) return "https://api.deepseek.com";
  const banned = /(manus\.im|fal\.ai|fal\.run)/i;
  if (banned.test(raw) && process.env.ENGINE_ALLOW_PROXY !== "true") {
    return "https://api.deepseek.com";
  }
  return raw;
}
const FALLBACK_KEY = process.env.OPENAI_API_KEY || "";
const FALLBACK_BASE = _pickBaseURL();
const FALLBACK_MODEL = process.env.OPENAI_MODEL || "deepseek-v4-pro";

let _fallback = null;
function fallback() {
  if (!FALLBACK_KEY) {
    throw new Error("Neither CLAUDE_API_KEY nor OPENAI_API_KEY is set; engine cannot run.");
  }
  if (_fallback) return _fallback;
  _fallback = new OpenAI({ apiKey: FALLBACK_KEY, baseURL: FALLBACK_BASE });
  return _fallback;
}

async function callClaude({ system, user, temperature, max_tokens }) {
  const body = {
    model: CLAUDE_MODEL,
    max_tokens: max_tokens || 6000,
    temperature: typeof temperature === "number" ? temperature : 0.55,
    system: system || "",
    messages: [{ role: "user", content: user || "" }],
  };
  const resp = await fetch(CLAUDE_BASE, {
    method: "POST",
    headers: {
      "x-api-key": CLAUDE_API_KEY,
      "anthropic-version": CLAUDE_VERSION,
      "content-type": "application/json",
    },
    body: JSON.stringify(body),
  });
  if (!resp.ok) {
    const t = await resp.text().catch(() => "");
    throw new Error(`Claude HTTP ${resp.status}: ${t.slice(0, 400)}`);
  }
  const j = await resp.json();
  // Anthropic response: { content: [{ type:"text", text:"..." }, ...] }
  const text = (j?.content || [])
    .filter((b) => b && b.type === "text" && typeof b.text === "string")
    .map((b) => b.text)
    .join("\n")
    .trim();
  if (!text || text.length < 200) {
    throw new Error("Claude returned empty or too-short response.");
  }
  return text;
}

async function callFallback({ system, user, temperature, max_tokens }) {
  const c = fallback();
  const resp = await c.chat.completions.create({
    model: FALLBACK_MODEL,
    temperature: typeof temperature === "number" ? temperature : 0.55,
    max_tokens: max_tokens || 6000,
    messages: [
      { role: "system", content: system || "" },
      { role: "user", content: user || "" },
    ],
  });
  const text = resp?.choices?.[0]?.message?.content || "";
  if (!text || text.length < 200) {
    throw new Error("Fallback engine returned empty or too-short response.");
  }
  return text;
}

export async function generate({ system, user, temperature = 0.55, max_tokens = 6000 } = {}) {
  if (CLAUDE_API_KEY) {
    return callClaude({ system, user, temperature, max_tokens });
  }
  return callFallback({ system, user, temperature, max_tokens });
}

export const EngineConfig = {
  primary: CLAUDE_API_KEY ? "claude" : "openai-compatible",
  claudeModel: CLAUDE_MODEL,
  fallbackModel: FALLBACK_MODEL,
  fallbackBaseURL: FALLBACK_BASE,
  hasClaude: !!CLAUDE_API_KEY,
  hasFallback: !!FALLBACK_KEY,
};
