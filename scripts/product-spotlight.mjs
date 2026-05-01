// Weekly product spotlight: queue one essay around an ASIN that hasn't been featured recently.
// Master scope §15F. Affiliate tag: spankyspinola-20.
import { getPool, query } from "../src/lib/db.mjs";

const ASIN_LIBRARY = [
  { asin: "0358108411", title: "Gut: The Inside Story of Our Body's Most Underrated Organ" },
  { asin: "1476755183", title: "Childhood Disrupted (ACE study, autoimmunity)" },
  { asin: "0143127748", title: "The Body Keeps the Score" },
  { asin: "0393706095", title: "The Pocket Guide to Polyvagal Theory" },
  { asin: "1583335544", title: "The Wahls Protocol" },
  { asin: "0985690402", title: "Why Do I Still Have Thyroid Symptoms?" },
  { asin: "0985690437", title: "Hashimoto's Protocol" },
  { asin: "1623172241", title: "The Autoimmune Fix" },
  { asin: "1628600381", title: "The Paleo Approach" },
  { asin: "1628602473", title: "The Healing Kitchen" },
  { asin: "1623368669", title: "The Immune System Recovery Plan" },
  { asin: "1465482067", title: "Heal Your Gut by Cooking with Bone Broth" },
];

async function main() {
  const pool = getPool();
  if (!pool) { console.log("[spotlight] no DB"); return; }
  // Find the ASIN least used in the last 30 days
  const { rows: usage } = await query(
    `SELECT a, count(*)::int AS c
       FROM articles, unnest(asins_used) AS a
      WHERE published_at > NOW() - INTERVAL '30 days'
      GROUP BY a`
  );
  const used = new Map(usage.map(r => [r.a, r.c]));
  const sorted = ASIN_LIBRARY.slice().sort((x, y) => (used.get(x.asin) || 0) - (used.get(y.asin) || 0));
  const pick = sorted[0];
  const slug = `spotlight-${pick.asin}-${new Date().toISOString().slice(0,10)}`;
  await query(
    `INSERT INTO article_queue (slug, title, category, angle, asins, status, priority)
     VALUES ($1,$2,'Library Spotlight',$3,$4,'queued',75)
     ON CONFLICT (slug) DO NOTHING`,
    [slug, `Why "${pick.title}" still matters`, "weekly product spotlight", [pick.asin]]
  );
  console.log(`[spotlight] queued ${slug}`);
}
main().catch(e => { console.error(e); process.exit(1); });
