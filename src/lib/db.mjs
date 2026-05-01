/**
 * Postgres connection pool. Master scope §15B. SSL on for managed DBs.
 * Safe-fails when DATABASE_URL is missing (dev preview, image-only Manus run).
 */
import pg from "pg";
const { Pool } = pg;

let pool = null;

export function getPool() {
  if (pool) return pool;
  const url = process.env.DATABASE_URL;
  if (!url) {
    return null;
  }
  // Master scope: only Postgres. If a non-postgres URL is injected by the platform
  // (e.g. mysql://) we treat it as 'no DB configured' rather than crashing the boot.
  if (!/^postgres(ql)?:\/\//i.test(url)) {
    console.warn("[db] DATABASE_URL is not postgres — ignoring (" + url.split("://")[0] + ")");
    return null;
  }
  pool = new Pool({
    connectionString: url,
    ssl: /sslmode=disable/.test(url) ? false : { rejectUnauthorized: false },
    max: 5,
    idleTimeoutMillis: 30_000,
  });
  pool.on("error", (e) => {
    console.error("[db] pool error:", e?.message || e);
  });
  return pool;
}

export async function query(sql, params = []) {
  const p = getPool();
  if (!p) {
    throw new Error("DATABASE_URL is not configured");
  }
  return p.query(sql, params);
}

export async function close() {
  if (pool) {
    await pool.end();
    pool = null;
  }
}
