// Process entry point.
// Boots the built Express server AND in-process cron schedules. Master scope §15A:
// crons run inside the same Node process, no separate worker, no third-party scheduler.

import cron from "node-cron";
import { spawn } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");

function run(label, cmd, args) {
  return new Promise((resolve) => {
    const p = spawn(cmd, args, { cwd: ROOT, stdio: "inherit", env: process.env });
    p.on("exit", (code) => {
      console.log(`[cron:${label}] exit ${code}`);
      resolve(code);
    });
  });
}

function script(file) { return ["node", [path.join("scripts", file)]]; }

async function bootCrons() {
  if (String(process.env.AUTO_GEN_ENABLED || "true").toLowerCase() !== "true") {
    console.log("[boot] AUTO_GEN_ENABLED=false — crons not scheduled");
    return;
  }

  // Daily publish tick. Master scope §15: 1 article per day default.
  cron.schedule("17 13 * * *", () => { run("publish", ...script("cron-publish.mjs")); }, { timezone: "UTC" });
  // Monthly freshness pass. First of the month.
  cron.schedule("11 4 1 * *", () => { run("refresh-monthly", ...script("refresh-monthly.mjs")); }, { timezone: "UTC" });
  // Quarterly refresh. First of Jan/Apr/Jul/Oct.
  cron.schedule("23 5 1 1,4,7,10 *", () => { run("refresh-quarterly", ...script("refresh-quarterly.mjs")); }, { timezone: "UTC" });
  // Weekly product spotlight. Mondays.
  cron.schedule("9 12 * * 1", () => { run("spotlight", ...script("product-spotlight.mjs")); }, { timezone: "UTC" });

  console.log("[boot] crons scheduled: daily 13:17 UTC publish, monthly refresh, quarterly refresh, weekly spotlight");
}

async function main() {
  // Run migrate once on boot (idempotent).
  await run("migrate", ...script("migrate.mjs"));
  // Run seed once on boot (idempotent — ON CONFLICT updates).
  await run("seed", ...script("bulk-seed.mjs"));
  // One-time pre-seed of 500 queued articles. Idempotent — ON CONFLICT DO NOTHING.
  await run("queue-seed", ...script("seed-queue.mjs"));
  // Schedule crons.
  await bootCrons();
  // Start the Express server.
  const p = spawn("node", ["dist/index.js"], { cwd: ROOT, stdio: "inherit", env: process.env });
  p.on("exit", (code) => { console.log(`[boot] web exited ${code}`); process.exit(code || 0); });
}

main().catch((e) => { console.error("[boot] fatal", e); process.exit(1); });
