import fs from "node:fs";
import { checkText } from "../src/lib/gate.mjs";
import { fetchArticleJson } from "../src/lib/bunny.mjs";

const m = JSON.parse(fs.readFileSync("client/public/content/preview-manifest.json", "utf8"));
let bad = 0;
const wcStats = [];
for (const a of m.articles) {
  let body = a.body;
  if (!body && a.body_url) {
    const j = await fetchArticleJson(a.body_url);
    body = (j && j.body) || "";
  }
  const r = checkText(body);
  wcStats.push(a.word_count);
  if (r.ok === false) {
    bad++;
    console.log("FAIL", a.slug, r.reasons.join(" | "));
  }
}
console.log(`articles=${m.articles.length} bad=${bad}`);
console.log(`word_counts min=${Math.min(...wcStats)} max=${Math.max(...wcStats)} avg=${Math.round(wcStats.reduce((a,b)=>a+b,0)/wcStats.length)}`);
const days = new Set(m.articles.map(a => (a.publish_at || a.published_at || "").slice(0,10)));
console.log(`distinct_days=${days.size}`);
process.exit(bad === 0 ? 0 : 1);
