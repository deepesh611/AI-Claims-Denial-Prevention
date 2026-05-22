# ── Stage 1: Install dependencies ────────────────────────────────────────────
FROM node:22-alpine AS deps
WORKDIR /app

COPY package*.json ./
# --legacy-peer-deps is required: project uses React 19 but next@14 declares
# a peer dep on React 18. The app works fine at runtime; this flag just
# suppresses the resolver error during install.
RUN npm install --legacy-peer-deps

# ── Stage 2: Build the Next.js app ───────────────────────────────────────────
FROM node:22-alpine AS builder
WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Ensure env vars are available to Next.js at build time
# (NEXT_PUBLIC_* vars get inlined into JS bundles during `next build`)
COPY .env.production .env.production

RUN npm run build

# ── Stage 3: Minimal production image ────────────────────────────────────────
FROM node:22-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production

# Copy only what Next.js standalone output needs
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
# Runtime env vars (NEXTAUTH_URL, etc.)
COPY --from=builder /app/.env.production .env.production

EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# next start is replaced by the standalone server.js (smaller, faster boot)
CMD ["node", "server.js"]