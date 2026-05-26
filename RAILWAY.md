# Railway deployment guide — Immune Rebuilt

## One-time setup

### 1. Create the Railway project from this repo
- Go to https://railway.com/new and select **Deploy from GitHub repo**.
- Pick `peacefulgeek/immune-rebuilt`. Railway auto-detects `railway.json` and `nixpacks.toml`.
- Build command: `pnpm install --frozen-lockfile && pnpm build`
- Start command: `node scripts/start-with-cron.mjs`
- Health check path: `/healthz`

### 2. Add a Postgres database
- In the project, click **+ New** → **Database** → **PostgreSQL**.
- Railway auto-injects `DATABASE_URL` into the web service. No further action.

### 3. Set the secrets / envs
Use Railway's **Variables** tab on the web service. Paste each:

| Variable | Value |
|---|---|
| `OPENAI_API_KEY` | `sk-82bdad0a1fd34987b73030504ae67080` |
| `OPENAI_BASE_URL` | `https://api.deepseek.com` |
| `OPENAI_MODEL` | `deepseek-v4-pro` |
| `AUTO_GEN_ENABLED` | `true` |
| `PUBLISH_CAP` | `100` |
| `PUBLISH_PER_TICK` | `1` |
| `SITE_APEX` | `immunerebuilt.com` |
| `SITE_NAME` | `Immune Rebuilt` |
| `SITE_AUTHOR` | `The Oracle Lover` |
| `SITE_NICHE` | `autoimmune root causes, AIP, leaky gut, functional medicine` |
| `SISTER_SITE_URL` | `https://theoraclelover.com` |
| `AMAZON_AFFILIATE_TAG` | `spankyspinola-20` |
| `BUNNY_PULL_ZONE` | `https://conscious-elder.b-cdn.net/immune-rebuilt` |
| `CONTACT_TO` | `hello@immunerebuilt.com` |
| `NODE_ENV` | `production` |
| `PORT` | `3000` |

Optional (only if you want the contact form to email immediately):

| Variable | Value |
|---|---|
| `SMTP_HOST` | `smtp.zoho.com` |
| `SMTP_PORT` | `587` |
| `SMTP_USER` | (your SMTP user) |
| `SMTP_PASS` | (your SMTP password) |

### 4. Custom domain
- In the web service, **Settings** → **Networking** → **Custom Domain**.
- Add `immunerebuilt.com` and `www.immunerebuilt.com`.
- Railway gives you a CNAME target like `xxx.up.railway.app`. Add it at your DNS provider:
  - **apex (immunerebuilt.com)** → ALIAS / ANAME to that target (or use Railway's A records if your DNS doesn't support ANAME)
  - **www.immunerebuilt.com** → CNAME to that target
- Railway provisions TLS automatically. Express's WWW→apex 301 (first middleware in `server/index.ts`) handles the redirect.

### 5. First deploy
- Push to `main` triggers an auto-build (already enabled via `railway.json`).
- Boot sequence inside `scripts/start-with-cron.mjs`:
  1. `node scripts/migrate.mjs` — creates / alters tables
  2. `node scripts/bulk-seed.mjs` — seeds **up to PUBLISH_CAP=100** articles as `published`
  3. `node scripts/seed-queue.mjs` — seeds the rest (430) as `queued`
  4. Schedules four in-process node-cron jobs (daily publish, monthly refresh, quarterly refresh, weekly product spotlight)
  5. Starts Express on `PORT`

### 6. Verify after deploy
- `GET /healthz` → `200 OK`
- `GET /robots.txt`, `/sitemap.xml`, `/llms.txt`, `/llms-full.txt` → expected XML/text
- `GET /api/articles` → 100 articles (status=published)
- `GET https://www.immunerebuilt.com` → 301 redirect to `https://immunerebuilt.com`
- Check Railway logs for `[publish] PUBLISH_CAP=100 reached`. The cron will refuse to exceed 100 — to drip more, raise `PUBLISH_CAP`.

## Notes
- The site is a single Node process: web + cron in the same dyno (Railway's recommended pattern for low-traffic sites). No separate worker required.
- All images live on Bunny CDN (`https://conscious-elder.b-cdn.net/immune-rebuilt/...`). Zero raster images in the repo — only `client/public/favicon.svg`.
- The writing engine calls DeepSeek V4-Pro via the OpenAI client at `https://api.deepseek.com`. The banned-proxy guard in `src/lib/engine.mjs` rejects any inherited URL pointing at Manus / Anthropic / fal.ai.
- Crons are in-code only (`node-cron`). Nothing is scheduled externally.
