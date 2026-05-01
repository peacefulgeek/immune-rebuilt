// Schema migration. Idempotent. Safe to run on every deploy.
// Master scope §7 + §10 (ASIN attribution) + §15 (queue).
import { getPool } from "../src/lib/db.mjs";

const SQL = `
CREATE TABLE IF NOT EXISTS articles (
  id BIGSERIAL PRIMARY KEY,
  slug TEXT UNIQUE NOT NULL,
  title TEXT NOT NULL,
  category TEXT NOT NULL,
  tags TEXT[] DEFAULT '{}',
  excerpt TEXT NOT NULL,
  body TEXT NOT NULL,
  hero_url TEXT,
  word_count INTEGER NOT NULL DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'draft',
  published_at TIMESTAMPTZ,
  queued_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  last_modified_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  asins_used TEXT[] DEFAULT '{}',
  gate_meta JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_articles_status_pub ON articles(status, published_at DESC);
CREATE INDEX IF NOT EXISTS idx_articles_category ON articles(category);

CREATE TABLE IF NOT EXISTS article_queue (
  id BIGSERIAL PRIMARY KEY,
  slug TEXT UNIQUE NOT NULL,
  title TEXT NOT NULL,
  category TEXT NOT NULL,
  angle TEXT,
  must_cover TEXT[] DEFAULT '{}',
  asins TEXT[] DEFAULT '{}',
  related_slugs TEXT[] DEFAULT '{}',
  status TEXT NOT NULL DEFAULT 'queued',
  priority INTEGER NOT NULL DEFAULT 100,
  attempts INTEGER NOT NULL DEFAULT 0,
  last_error TEXT,
  scheduled_for TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_queue_status_priority ON article_queue(status, priority, scheduled_for);

-- Pre-seed columns: hold pre-vetted body so cron can publish without round-tripping DeepSeek
ALTER TABLE article_queue ADD COLUMN IF NOT EXISTS excerpt TEXT;
ALTER TABLE article_queue ADD COLUMN IF NOT EXISTS body TEXT;
ALTER TABLE article_queue ADD COLUMN IF NOT EXISTS hero_url TEXT;
ALTER TABLE article_queue ADD COLUMN IF NOT EXISTS hero_alt TEXT;
ALTER TABLE article_queue ADD COLUMN IF NOT EXISTS word_count INTEGER;

CREATE TABLE IF NOT EXISTS publish_log (
  id BIGSERIAL PRIMARY KEY,
  slug TEXT NOT NULL,
  action TEXT NOT NULL,
  detail JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_publish_log_created ON publish_log(created_at DESC);

CREATE TABLE IF NOT EXISTS contact_messages (
  id BIGSERIAL PRIMARY KEY,
  name TEXT,
  email TEXT,
  body TEXT NOT NULL,
  source TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
`;

async function run() {
  const pool = getPool();
  if (!pool) {
    console.log("[migrate] DATABASE_URL not set — skipping (preview/dev mode).");
    return;
  }
  await pool.query(SQL);
  console.log("[migrate] OK");
}
run().catch((e) => { console.error("[migrate] FAIL", e); process.exit(1); });
