# Telegram Media Cloud

Production-oriented self-hosted archival and streaming platform that stores canonical media chunks and manifests in Telegram while serving users exclusively through Cloudflare Pages, Workers, D1, KV, and R2. The private i5serv host runs only the Upload Manager and Telegram Gateway.

## Components

- `apps/upload-manager`: FastAPI service and workers for Jellyfin scanning, NFO/TMDB metadata, SHA256 hashing, chunking, Telegram uploads, quotas, scheduling, manifest generation, and D1 sync.
- `apps/telegram-gateway`: private FastAPI/Telethon gateway for authenticated manifest/chunk/range retrieval.
- `apps/worker`: Cloudflare Worker API for auth, D1-only search, R2 hot-cache streaming/downloads, settings, stats, and audit logging.
- `apps/web`: React/Vite/Tailwind Cloudflare Pages UI.
- `packages/database`: PostgreSQL and D1 schemas/migrations.
- `packages/auth`, `packages/logging`, `packages/shared-types`, `packages/shared-utils`: shared production primitives.
- `infrastructure`: Docker Compose, Nginx, Cloudflare, monitoring, and operations scripts.
- `docs`: architecture, deployment, operations, and disaster recovery runbooks.

## Quick start

```bash
cp .env.example .env
docker compose -f infrastructure/docker/docker-compose.yml up --build
```

The Upload Manager binds to localhost only and must be firewalled on i5serv. Users access only Cloudflare Pages and Worker routes.
