// Process entry point.
// Boots the built Express server AND in-process cron schedules. Master scope §15A:
// crons run inside the same Node process, no separate worker, no third-party scheduler.
//
// Railway-hardened: top-level crash diagnostics so deploy logs never go silent,
// migrations/seeds run with their own try/catch, and the web process inherits
// the PORT Railway injects (default 8080, NOT 10000).

// ---------- crash diagnostics (must be the very first thing) ----------
process.on("uncaughtException", (err) => {
  console.error("[boot:uncaughtException]", err && err.stack ? err.stack : err);
  process.exit(1);
});
process.on("unhandledRejection", (reason) => {
  console.error("[boot:unhandledRejection]", reason && reason.stack ? reason.stack : reason);
  process.exit(1);
});
console.log("[boot] start-with-cron.mjs booting; node=" + process.version + " pid=" + process.pid);
// ---------- end crash diagnostics ----------

import cron from "node-cron";
import { spawn } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");

function run(label, cmd, args) {
  return new Promise((resolve) => {
    console.log(`[boot] ${label}: ${cmd} ${args.join(" ")}`);
    const p = spawn(cmd, args, { cwd: ROOT, stdio: "inherit", env: process.env });
    p.on("exit", (code) => {
      console.log(`[boot] ${label}: exited ${code}`);
      resolve(code);
    });
    p.on("error", (err) => {
      console.error(`[boot] ${label}: spawn error`, err);
      resolve(1);
    });
  });
}

function script(file) { return ["node", [path.join("scripts", file)]]; }

async function bootCrons() {
  if (String(process.env.AUTO_GEN_ENABLED || "true").toLowerCase() !== "true") {
    console.log("[boot] AUTO_GEN_ENABLED=false — crons not scheduled");
    return;
  }
  cron.schedule("17 13 * * *", () => { run("publish", ...script("cron-publish.mjs")); }, { timezone: "UTC" });
  cron.schedule("11 4 1 * *", () => { run("refresh-monthly", ...script("refresh-monthly.mjs")); }, { timezone: "UTC" });
  cron.schedule("23 5 1 1,4,7,10 *", () => { run("refresh-quarterly", ...script("refresh-quarterly.mjs")); }, { timezone: "UTC" });
  cron.schedule("9 12 * * 1", () => { run("spotlight", ...script("product-spotlight.mjs")); }, { timezone: "UTC" });
  console.log("[boot] crons scheduled: daily 13:17 UTC publish, monthly refresh, quarterly refresh, weekly spotlight");
}

async function main() {
  console.log("[boot] step 1/4: migrate");
  await run("migrate", ...script("migrate.mjs"));

  console.log("[boot] step 2/4: bulk-seed (cap=" + (process.env.PUBLISH_CAP || "100") + ")");
  await run("seed", ...script("bulk-seed.mjs"));

  console.log("[boot] step 3/4: queue-seed (430 queued)");
  await run("queue-seed", ...script("seed-queue.mjs"));

  console.log("[boot] step 4/4: schedule crons + start web");
  await bootCrons();

  // Default to 8080, not 10000. Railway-injected PORT always wins, but the
  // fallback must match what Railway expects when env is empty.
  const port = process.env.PORT || "8080";
  console.log("[boot] launching dist/index.js on PORT=" + port);
  const p = spawn("node", ["dist/index.js"], {
    cwd: ROOT,
    stdio: "inherit",
    env: { ...process.env, PORT: port },
  });
  p.on("exit", (code) => { console.log(`[boot] web exited ${code}`); process.exit(code || 0); });
  p.on("error", (err) => { console.error("[boot] web spawn error", err); process.exit(1); });
}

main().catch((e) => {
  console.error("[boot] fatal", e && e.stack ? e.stack : e);
  process.exit(1);
});
