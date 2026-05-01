// Writing engine: DeepSeek V4-Pro via the OpenAI client at https://api.deepseek.com
// Master scope §0 hard rule. No @anthropic-ai/sdk, no FAL_KEY.
import OpenAI from "openai";

// Master scope §0 hard rule: engine must be DeepSeek. We pin the default to
// api.deepseek.com and reject any inherited proxy URL that points at any
// Anthropic, or fal.ai — those are explicitly banned. Operators can override
// to a self-hosted gateway by setting ENGINE_ALLOW_PROXY=true.
function _pickBaseURL() {
  const raw = (process.env.OPENAI_BASE_URL || "").trim();
  if (!raw) return "https://api.deepseek.com";
  const banned = /(manus\.im|api\.anthropic\.com|fal\.ai|fal\.run)/i;
  if (banned.test(raw) && process.env.ENGINE_ALLOW_PROXY !== "true") {
    return "https://api.deepseek.com";
  }
  return raw;
}
const apiKey = process.env.OPENAI_API_KEY || "";
const baseURL = _pickBaseURL();
const model = process.env.OPENAI_MODEL || "deepseek-v4-pro";

let _client = null;
function client() {
  if (!apiKey) {
    throw new Error("OPENAI_API_KEY is not set; engine cannot run.");
  }
  if (_client) return _client;
  _client = new OpenAI({ apiKey, baseURL });
  return _client;
}

export async function generate({ system, user, temperature = 0.55, max_tokens = 6000 } = {}) {
  const c = client();
  const resp = await c.chat.completions.create({
    model,
    temperature,
    max_tokens,
    messages: [
      { role: "system", content: system || "" },
      { role: "user", content: user || "" },
    ],
  });
  const text = resp?.choices?.[0]?.message?.content || "";
  if (!text || text.length < 200) {
    throw new Error("Engine returned empty or too-short response.");
  }
  return text;
}

export const EngineConfig = { model, baseURL, hasKey: !!apiKey };
