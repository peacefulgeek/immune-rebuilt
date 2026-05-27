# syntax=docker/dockerfile:1.7
# Immune Rebuilt — Railway deploy.
# Why a Dockerfile and not Railpack alone:
#   The previous Railpack build hit ERR_PNPM_NO_PKG_MANIFEST because /app was
#   empty when `pnpm install` ran. With a Dockerfile we own WORKDIR + COPY
#   explicitly, so the build context is guaranteed to contain package.json,
#   pnpm-lock.yaml, patches/, and the rest of the repo.

FROM node:22-bookworm-slim AS builder
WORKDIR /app

# Enable Corepack and pin pnpm to the exact version package.json declares.
# We do NOT use `--latest` to avoid the version-mismatch silent-fail seen on
# the Shattered Armor deploy.
RUN corepack enable && corepack prepare pnpm@10.4.1 --activate

# Copy the dependency-graph files first so Docker can cache the install layer.
# patches/ MUST come before `pnpm install` because pnpm-lock.yaml references
# patches/wouter@3.7.1.patch and the integrity check will fail otherwise.
COPY package.json pnpm-lock.yaml ./
COPY patches/ ./patches/

# Frozen lockfile, no scripts during install (we run the build step explicitly).
RUN pnpm install --frozen-lockfile

# Bring in the rest of the repo and build.
COPY . .
RUN pnpm build

# ---------- runtime image ----------
FROM node:22-bookworm-slim AS runtime
WORKDIR /app
ENV NODE_ENV=production

RUN corepack enable && corepack prepare pnpm@10.4.1 --activate

# Production-only install (smaller image, faster cold start).
COPY package.json pnpm-lock.yaml ./
COPY patches/ ./patches/
RUN pnpm install --frozen-lockfile --prod

# Copy build output, scripts, and source needed at runtime (cron + seeds read JSON
# manifests from client/public/content/ and src/lib/*.mjs).
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/scripts ./scripts
COPY --from=builder /app/src ./src
COPY --from=builder /app/server ./server
COPY --from=builder /app/shared ./shared
COPY --from=builder /app/client ./client

# Railway injects PORT; fallback 8080 lives in the boot script.
EXPOSE 8080

# Identical start command to railway.json so behaviour is consistent regardless
# of which entry point Railway picks (CMD vs startCommand).
CMD ["node", "scripts/start-with-cron.mjs"]
