# Deploying Immune Rebuilt to Railway

This site ships on **Railway** with the **Railpack** builder (not Nixpacks, not Docker). All nine known Railway failure modes have been pre-resolved in the repo. Do not "improve" them.

---

## Quick connect

1. New Project → Deploy from GitHub repo → `peacefulgeek/immune-rebuilt` → branch `main`.
2. Add the **Postgres** plugin to the same project. Railway auto-injects `DATABASE_URL`.
3. Paste the env vars from the table below into the web service's Variables tab.
4. Deploy. The builder is configured in `railpack.json`; the start command is `node scripts/start-with-cron.mjs` (declared in `railway.json`, `railpack.json`, and `Procfile`). No Dockerfile, no `nixpacks.toml`, no `Caddyfile`.
5. After the first green deploy, add the custom domain in Railway → Settings → Domains: `immunerebuilt.com` and `www.immunerebuilt.com`. Point DNS:
   - **apex** `immunerebuilt.com` → ALIAS / ANAME / flattened CNAME to the Railway target hostname.
   - **www** `www.immunerebuilt.com` → CNAME to the Railway target hostname.
   Express already 301s `www.` → apex as the first middleware in `server/index.ts`.

---

## Environment variables

| Key | Value |
|---|---|
| `OPENAI_API_KEY` | `sk-82bdad0a1fd34987b73030504ae67080` |
| `OPENAI_BASE_URL` | `https://api.deepseek.com` |
| `OPENAI_MODEL` | `deepseek-v4-pro` |
| `AUTO_GEN_ENABLED` | `true` |
| `DATABASE_URL` | (auto from Postgres plugin) |
| `BUNNY_PULL_ZONE` | `https://conscious-elder.b-cdn.net/immune-rebuilt` |
| `PUBLISH_CAP` | `100` |
| `PUBLISH_PER_TICK` | `1` |
| `SITE_APEX` | `immunerebuilt.com` |
| `SITE_NAME` | `Immune Rebuilt` |
| `SITE_AUTHOR` | `The Immune Rebuilt Editorial Team` |
| `AMAZON_AFFILIATE_TAG` | `spankyspinola-20` |
| `NODE_ENV` | `production` |

Optional (contact-form delivery): `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `CONTACT_TO`.

The writing engine in `src/lib/engine.mjs` rejects any `OPENAI_BASE_URL` pointing at `manus.im`, `api.anthropic.com`, or `fal.ai`. Do not paste those.

Do not set `PORT` manually. Railway injects it; the boot script defaults to `8080` only as a fallback.

---

## The 9 Railway failure modes — already fixed in this repo

### 1. Builder conflict (Nixpacks injecting Caddy)
Nixpacks auto-detected `dist/public/` as a static site and inserted Caddy as a reverse proxy in front of Express. Caddy grabbed `PORT`, so Express could not bind. **Fix:** `railway.json` sets `"builder": "RAILPACK"`, and there is no `nixpacks.toml`, no `Dockerfile`, no `Caddyfile` in the repo. Railpack does not inject a reverse proxy.

### 2. Missing `patches/` during install
`pnpm-lock.yaml` references `patches/wouter@3.7.1.patch`. If `patches/` is missing from the build context before `pnpm install`, the lockfile integrity check fails silently. **Fix:** `.gitignore` does not exclude `patches/`, `patches/wouter@3.7.1.patch` is committed to the repo, and Railpack copies the full repo before the install step (no `.dockerignore` to mis-configure).

### 3. pnpm version mismatch
`package.json` pins `"packageManager": "pnpm@10.4.1+sha512..."`. If the builder activates `pnpm@latest`, corepack's strict check rejects it. **Fix:** `railpack.json` declares `"pnpm": "10.4.1"` under `packages` and runs `corepack prepare pnpm@10.4.1 --activate` before `pnpm install --frozen-lockfile`.

### 4. No error handling — silent crashes
A bad import or a failed `listen()` used to kill the process with zero log output. **Fix:** `scripts/start-with-cron.mjs` registers `uncaughtException` and `unhandledRejection` handlers as the very first executable lines, logs every spawn, and `server/index.ts` registers `server.on("error", …)` before `server.listen()`.

### 5. Wrong default port
The boot script used to default `PORT=10000`; Railway routes to `8080`. **Fix:** both `scripts/start-with-cron.mjs` and `server/index.ts` default to `8080`. Railway-injected `PORT` always wins when set; `8080` is only the fallback.

### 6. Healthcheck timing out during cold boot
The first boot reads hundreds of JSON files and seeds the queue. A 30-second healthcheck expired before `listen()` was called, so Railway killed the container. **Fix:** there is **no** `healthcheckPath` in `railway.json`. Railway falls back to TCP readiness on the bound port, which only checks after `listen()` succeeds.

### 7. `startCommand` vs Dockerfile `CMD` ambiguity
No Dockerfile exists. The start command is declared identically in `railway.json` (`deploy.startCommand`), `railpack.json` (`deploy.startCommand`), and `Procfile`. All three say `node scripts/start-with-cron.mjs`.

### 8. Stale build cache from prior Dockerfile attempts
**Fix:** the repo no longer carries a Dockerfile. If you previously deployed a Dockerfile build for this service, do one redeploy with **Clear build cache** checked in the Railway UI. Subsequent deploys are clean.

### 9. Stale DNS records
After the deploy is green, `immunerebuilt.com` must point at the Railway target hostname. If you previously had it pointing elsewhere, **delete the old A/CNAME records first**, then add the Railway ones. Propagation can take up to an hour. Express already 301s `www.` → apex.

---

## Verifying a green deploy

```
curl -I https://<railway-host>.up.railway.app/                  # → 200 (apex), 301 if hit via www
curl    https://<railway-host>.up.railway.app/healthz           # → "ok"
curl    https://<railway-host>.up.railway.app/robots.txt | head -3
curl    https://<railway-host>.up.railway.app/sitemap.xml | head -5
```

After custom domain is live:

```
curl -I https://www.immunerebuilt.com/      # → 301 to https://immunerebuilt.com/
curl -I https://immunerebuilt.com/          # → 200
```

---

## Cron sanity (UTC)

| Job | Schedule | Behavior |
|---|---|---|
| Daily publish | `17 13 * * *` | Promotes 1 queue article, refuses past `PUBLISH_CAP=100` |
| Monthly refresh | `11 4 1 * *` | Re-passes gate, rewrites soft-banned phrasing |
| Quarterly refresh | `23 5 1 1,4,7,10 *` | Deep rewrites on oldest essays |
| Product spotlight | `9 12 * * 1` | Weekly affiliate refresh |

All crons run **inside the same Node process** as the Express server. No external scheduler, no Manus runtime, no Cloudflare worker.
