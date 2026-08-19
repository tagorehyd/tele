# Telegram Media Cloud Setup Guide

This guide describes how to configure and run Telegram Media Cloud from a fresh Ubuntu 24.04 host with Docker already installed. The system is configuration-first: after bootstrap, administrators manage settings from the web UI and database-backed settings subsystem instead of editing source code or long-lived configuration files.

## 1. Required architecture and network boundaries

Telegram Media Cloud has two trust zones:

1. **Cloudflare zone**
   - Cloudflare Pages serves the React web application.
   - Cloudflare Worker handles all public API requests.
   - Cloudflare D1 stores searchable metadata, users, roles, audit logs, cache metrics, health checks, and UI-managed settings needed by the Worker.
   - Cloudflare R2 stores disposable hot-cache media objects.
   - Cloudflare KV stores ephemeral Worker state when needed.
2. **Private i5serv zone**
   - Upload Manager scans Jellyfin libraries, extracts metadata, hashes files, chunks media, uploads chunks and manifests to Telegram, and syncs metadata to Cloudflare.
   - Telegram Gateway retrieves Telegram manifests/chunks for the Worker on R2 cache misses.
   - Neither private service should be exposed directly to users.

Firewall policy for `i5serv` must block direct public user access to Upload Manager and Telegram Gateway. If a Cloudflare Tunnel or reverse proxy is used for the Gateway, restrict it to the Worker path and require Gateway JWT replay protection.

## 2. Bootstrap inputs

Only three environment variables are used to start private services:

- `DATABASE_URL`: PostgreSQL connection URL for the private application database.
- `ENCRYPTION_MASTER_KEY`: base64-encoded 32-byte AES-256-GCM master key.
- `INITIAL_SETUP_TOKEN`: high-entropy one-time token used to submit the first-run setup wizard.

Do not create environment files for Telegram, Jellyfin, TMDB, Cloudflare, JWT, Worker, Redis, cache, or channel values. Those settings are entered in the web UI and stored in database tables.

## 3. Prepare PostgreSQL

Create a private PostgreSQL database reachable from `i5serv` only.

```bash
sudo -u postgres createuser --pwprompt tmc
sudo -u postgres createdb --owner=tmc telegram_media_cloud
```

Build the bootstrap URL in your shell or host secret manager:

```bash
export DATABASE_URL='postgresql+asyncpg://tmc:REDACTED_PASSWORD@127.0.0.1:5432/telegram_media_cloud'
```

Keep this value outside the repository. If you use a containerized PostgreSQL instance, bind it to a private interface and use the same `DATABASE_URL` pattern.

## 4. Generate bootstrap secrets

Generate the encryption master key with the repository utility:

```bash
python - <<'PY'
from packages.auth.src.crypto import SecretBox
print(SecretBox.generate_key())
PY
```

Export it through your host secret manager or current shell:

```bash
export ENCRYPTION_MASTER_KEY='REDACTED_BASE64_32_BYTE_KEY'
```

Generate a one-time setup token:

```bash
export INITIAL_SETUP_TOKEN="$(openssl rand -base64 48)"
```

Record the setup token in your password manager until setup is complete. Rotate or remove it from service runtime after `system.setup_completed=true` has been written and audited.

## 5. Apply database schema

Apply the application schema to the private database using the migration process used by your deployment pipeline. The repository contains D1-compatible schema and configuration migrations under `packages/database/d1/`; keep the private PostgreSQL schema aligned with these structures.

For Cloudflare D1, create and initialize the database:

```bash
wrangler d1 create telegram-media-cloud
wrangler d1 execute telegram-media-cloud --remote --file packages/database/d1/schema.sql
```

The schema includes users, roles, media records, metadata relations, channels, chunks, manifests, upload jobs, audit logs, settings, secret store, upload/cache rules, component configuration tables, and health checks.

## 6. Start private services on i5serv

From the repository root, start the Upload Manager, Telegram Gateway, Prometheus, and Grafana containers:

```bash
docker compose -f infrastructure/docker/docker-compose.yml up -d --build
```

Verify service health locally on `i5serv`:

```bash
curl -fsS http://127.0.0.1:8081/healthz
curl -fsS http://127.0.0.1:8082/healthz
```

The compose file passes only the three bootstrap variables into private services and mounts `/media` read-only for Jellyfin library scanning.

## 7. Create Cloudflare resources

Authenticate Wrangler from your workstation or deployment runner:

```bash
wrangler login
```

Create required resources:

```bash
wrangler d1 create telegram-media-cloud
wrangler kv namespace create TMC_KV
wrangler r2 bucket create telegram-media-cloud-cache
```

Bind D1, KV, and R2 to the Worker in Cloudflare project settings or your deployment automation. Application secrets still belong in the database-backed settings subsystem and should not be placed in source-controlled Worker configuration.

Deploy the Worker:

```bash
cd apps/worker
npm install --no-audit --no-fund
npm run build
wrangler deploy
```

Deploy the Pages web application:

```bash
cd ../web
npm install --no-audit --no-fund
npm run build
wrangler pages deploy dist --project-name telegram-media-cloud
```

## 8. Complete the first-run Setup Wizard

Open the Cloudflare Pages URL. The web app checks `/api/setup/status`. If `system.setup_completed` is absent or false, it displays the Setup Wizard.

Complete these sections:

1. **Admin User**
   - Email address.
   - Strong password.
   - Admin role assignment.
2. **Telegram**
   - Phone number.
   - API ID.
   - API hash.
   - Session name.
   - Login flow.
   - Channel discovery.
   - Channel ID refresh.
   - Test upload.
   - Test download.
   - Channel mapping management for movie, TV, anime, manifest, index, and control channels.
3. **Jellyfin**
   - Server URL.
   - API key.
   - Username.
   - Optional password.
   - Library paths for Movies, TV Shows, and Anime.
   - Validate connection.
   - Refresh libraries.
   - Rescan libraries.
   - Pull metadata.
4. **TMDB**
   - API key.
   - Language.
   - Region.
   - Poster sync.
   - Backdrop sync.
5. **Cloudflare**
   - Account ID.
   - Worker URL.
   - Worker secret.
   - D1 database ID.
   - KV namespace.
   - R2 bucket.
   - Pages project.
   - Domain.
   - Validate connection.
6. **Upload Rules**
   - Monthly upload limit.
   - Chunk size.
   - Upload windows.
   - Allowed days.
   - Enable scheduling.
   - Enable quotas.
   - Enable SHA validation.
7. **Cache Rules**
   - R2 cache size.
   - Eviction policy.
   - Cache duration.
   - Popularity threshold.
   - Preload settings.
   - Purge cache action.
   - Cache statistics view.
8. **Security Settings**
   - JWT secret generation or rotation.
   - Refresh-token secret generation or rotation.
   - Secret reveal policy.
   - Master-key rotation plan.
   - Audit log review.

When validation succeeds, the setup endpoint writes the encrypted settings, records audit events, and sets `system.setup_completed=true`.

## 9. Validate operational health

Open the Health Dashboard and verify these components show `connected` or expected healthy status:

- Telegram status.
- Telethon session status.
- Jellyfin status.
- TMDB status.
- Cloudflare Worker status.
- D1 status.
- KV status.
- R2 status.
- Upload Manager status.
- Telegram Gateway status.

Each check should include last check time, latency, and latest error if one exists.

## 10. Run the first library scan

From an administrative workstation or private `i5serv` session, trigger the Upload Manager scan after Jellyfin settings are configured:

```bash
curl -fsS -X POST http://127.0.0.1:8081/internal/scan
```

The Upload Manager recursively scans configured library paths, calculates SHA256 hashes, reads NFO metadata, creates manifests, routes chunks to Telegram channels, and queues uploads according to upload windows and monthly upload quota rules.

## 11. Verify playback and downloads

In the web application:

1. Search for a known indexed title.
2. Open the media details page.
3. Click **Play** and confirm HTML5 playback begins.
4. Seek forward and backward to validate range requests.
5. Click **Download** and confirm the original filename is used.
6. Reopen the title and confirm R2 cache hit counters increase.

Playback, downloads, search, and browsing must not be limited by the monthly upload quota. The quota applies only to upload jobs.

## 12. Monitoring

Prometheus and Grafana are bound to localhost by default in Docker Compose.

```bash
curl -fsS http://127.0.0.1:9090/-/healthy
curl -fsS http://127.0.0.1:3000/api/health
```

Track upload throughput, playback throughput, download throughput, cache hit ratio, cache miss ratio, Worker performance, Gateway health, D1 health, upload queue depth, and monthly upload usage.

## 13. Backups

Back up these assets:

- Private PostgreSQL database.
- Cloudflare D1 exports.
- KV metadata exports if used.
- Encrypted Telethon session backup.
- Encrypted settings and secret store.
- Infrastructure deployment manifests.

Run the repository backup script from an authenticated operations shell:

```bash
infrastructure/scripts/backup.sh
```

R2 does not need canonical backup for media because it is a disposable hot cache. Telegram manifests and chunks are canonical.

## 14. Routine operations

- Review audit logs for settings changes and secret reveal operations.
- Verify upload windows and monthly quota reset at month boundaries.
- Rotate JWT and refresh secrets from the Security Settings page.
- Validate Telegram session health before large upload windows.
- Keep Cloudflare resource IDs current through the Cloudflare Settings page.
- Re-run health checks after any settings change.

## 15. Shutdown and restart

Stop services:

```bash
docker compose -f infrastructure/docker/docker-compose.yml down
```

Restart services:

```bash
docker compose -f infrastructure/docker/docker-compose.yml up -d --build
```

Private services reload runtime settings from the database, so changing Telegram, Jellyfin, TMDB, Cloudflare, upload, cache, or security settings does not require editing files or rebuilding images.
