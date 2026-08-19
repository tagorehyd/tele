# Telegram Media Cloud

Telegram Media Cloud is a self-hosted archival and streaming platform for storing Jellyfin media canonically in Telegram while exposing users only to Cloudflare Pages and Cloudflare Workers. The private server `i5serv` runs upload and gateway components only; it never handles search, browsing, playback UI, or direct user traffic.

## Production architecture

1. Users open the React web application on Cloudflare Pages.
2. The web application calls the Cloudflare Worker API.
3. The Worker authenticates users, searches D1 only, serves hot media from R2, records audit/cache metrics in D1, and contacts the private Telegram Gateway only on R2 cache misses.
4. The Telegram Gateway runs on `i5serv`, uses Telethon, requires replay-protected JWT requests, and retrieves manifests/chunks from Telegram.
5. The Upload Manager runs on `i5serv`, scans Jellyfin libraries, reads NFO metadata, enriches records, hashes files, chunks files, uploads chunks/manifests to Telegram, tracks upload-only quotas, and syncs searchable metadata to D1.
6. Telegram remains canonical storage. R2 is disposable hot cache.

## Configuration-first rule

The application is operable without editing code and without long-lived configuration files. Only these bootstrap environment variables are permitted:

- `DATABASE_URL`
- `ENCRYPTION_MASTER_KEY`
- `INITIAL_SETUP_TOKEN`

All Telegram, Jellyfin, TMDB, Cloudflare, JWT, upload, cache, channel mapping, and health settings are stored in database tables and managed from the web UI after initial setup. See `docs/bootstrap.md`.


## Complete setup guide

Follow `docs/setup-guide.md` for the end-to-end procedure to configure PostgreSQL, bootstrap the three allowed variables, start private services, create Cloudflare resources, complete the first-run Setup Wizard, validate health, run scans, test playback/downloads, enable monitoring, and operate backups.

## Fresh Ubuntu 24.04 installation with Docker already installed

1. Provision PostgreSQL and create an empty application database.
2. Generate the encryption key: `python - <<'PY'
from packages.auth.src.crypto import SecretBox
print(SecretBox.generate_key())
PY`.
3. Generate a one-time setup token with your password manager or `openssl rand -base64 48`.
4. Export only the three bootstrap variables in the shell or systemd secret manager: `DATABASE_URL`, `ENCRYPTION_MASTER_KEY`, and `INITIAL_SETUP_TOKEN`.
5. Run migrations: `psql "$DATABASE_URL" -f packages/database/d1/schema.sql` for SQLite-compatible Cloudflare D1 schema review, and apply PostgreSQL migrations through the deployment pipeline when targeting PostgreSQL.
6. Start private services: `docker compose -f infrastructure/docker/docker-compose.yml up -d --build`.
7. Deploy the Worker and Pages project with Cloudflare bindings for D1, KV, and R2. No application secrets are stored in Worker source.
8. Open the Cloudflare Pages URL. If `system.setup_completed` is absent or false, the UI redirects to the Setup Wizard.
9. Enter the setup token and complete all wizard sections: Admin User, Telegram, Jellyfin, TMDB, Cloudflare, Upload Rules, Cache Rules, and Security Settings.
10. Submit validation. The backend encrypts secrets, writes settings, audits changes, writes `system.setup_completed=true`, and switches the application into normal mode.
11. Use the Health Dashboard to verify Telegram, Telethon session, Jellyfin, TMDB, Worker, D1, KV, R2, Upload Manager, and Gateway status.

## Settings managed in UI

- Telegram: phone number, API ID, API hash, session name/status, login, reconnect, discovery, test upload/download, channel IDs, and channel mappings.
- Jellyfin: server URL, API key, username, optional password, library paths, validation, library refresh, rescan, and metadata pull.
- TMDB: API key, language, region, poster sync, and backdrop sync.
- Cloudflare: account ID, Worker URL, Worker secret, D1 database ID, KV namespace, R2 bucket, Pages project, domain, and validation.
- Upload: monthly upload limit, chunk size, upload windows, allowed days, scheduling, quotas, and SHA validation.
- Cache: R2 cache size, eviction policy, cache duration, popularity threshold, preload settings, purge action, and statistics.
- Security: JWT/refresh secrets, encrypted secret rotation, masked display, audit log review, and administrator reveal controls.

## Repository layout

- `apps/upload-manager` — private FastAPI upload orchestration service.
- `apps/telegram-gateway` — private FastAPI Telethon retrieval gateway.
- `apps/worker` — Cloudflare Worker API.
- `apps/web` — React/Vite/Tailwind Pages UI.
- `packages/database` — D1 schema and configuration migrations.
- `packages/configuration` — database-backed settings subsystem.
- `packages/auth` — AES-256-GCM secret utilities.
- `infrastructure` — Docker, Nginx, Cloudflare, monitoring, and scripts.
- `docs` — bootstrap, deployment, architecture, operations, API, and recovery runbooks.

## Operational guarantees

- Upload quotas apply only to upload jobs and never to playback, downloads, streaming, search, or browsing.
- Search uses D1 only and never contacts Telegram, Upload Manager, or Jellyfin.
- Secrets are encrypted with AES-256-GCM and masked unless an administrator explicitly reveals them.
- Gateway requests require JWT, nonce, timestamp, and audit logging.
- `i5serv` is not exposed to users.
