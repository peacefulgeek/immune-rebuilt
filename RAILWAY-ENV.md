# Railway environment variables for Immune Rebuilt

Copy these into Railway → Service → Variables. The Railway Postgres plugin auto-injects `DATABASE_URL`.

## Required

```
NODE_ENV="production"
AUTO_GEN_ENABLED="true"
AMAZON_TAG="spankyspinola-20"
JWT_SECRET="<paste the 96-hex JWT signing secret>"

# Final-Pass §1: writing engine = Claude (claude-sonnet-4-5)
CLAUDE_API_KEY="<paste your Anthropic API key, starts with sk-ant-...>"
CLAUDE_MODEL="claude-sonnet-4-5"

# Optional fallback engine — used ONLY if CLAUDE_API_KEY is missing.
OPENAI_API_KEY="<paste DeepSeek API key, starts with sk-...>"
OPENAI_BASE_URL="https://api.deepseek.com"
OPENAI_MODEL="deepseek-v4-pro"
FAL_KEY="<paste FAL key, format ID:secret>"
GH_PAT="<paste GitHub PAT, starts with ghp_>"
BUNNY_PULL_ZONE="https://conscious-elder.b-cdn.net"
PUBLISH_CAP="100"
PUBLISH_PER_TICK="1"
SITE_APEX="immunerebuilt.com"
SITE_NAME="Immune Rebuilt"
SITE_AUTHOR="The Immune Rebuilt Editorial Team"
```

The actual secret values were delivered out-of-band (chat / 1Password / Railway). Do not commit them.

## Optional (only if you want runtime uploads to Bunny Storage from the server itself)

```
BUNNY_STORAGE_ZONE="conscious-elder"
BUNNY_STORAGE_KEY="<storage-zone-password>"
BUNNY_STORAGE_HOST="ny.storage.bunnycdn.com"
```

## Notes

- The writing engine in `src/lib/engine.mjs` is Claude-first. When `CLAUDE_API_KEY` is set the engine ONLY hits `https://api.anthropic.com/v1/messages` with `anthropic-version: 2023-06-01`.
- If `CLAUDE_API_KEY` is unset, the engine falls back to the OpenAI-compatible client using `OPENAI_API_KEY` / `OPENAI_BASE_URL` / `OPENAI_MODEL` (DeepSeek by default). Every voice rule and quality gate still applies.
- `FAL_KEY` is present for the image-tooling pipeline (Bunny image-prep scripts). The engine never touches it.
- `BUNNY_PULL_ZONE` is the read-only public CDN host. Article bodies live at `BUNNY_PULL_ZONE/immune-rebuilt/articles/<slug>.json`; hero images at `BUNNY_PULL_ZONE/immune-rebuilt/article-heroes/<slug>.webp`.
- `GH_PAT` is for the deploy automation. The running web service does not need it; set it on the deployer/CI runner only if you wire one.
- Do **not** set `PORT` manually. Railway injects it; the boot script falls back to `8080`.
