# Fresh Ubuntu 24.04 deployment

Assumption: Docker is already installed and no application configuration exists.

1. Create a PostgreSQL database reachable only by `i5serv` and administrative hosts.
2. Export only `DATABASE_URL`, `ENCRYPTION_MASTER_KEY`, and `INITIAL_SETUP_TOKEN`; do not create application environment files.
3. Start services with `docker compose -f infrastructure/docker/docker-compose.yml up -d --build`.
4. Create Cloudflare D1, KV, R2, Worker, and Pages resources with Wrangler.
5. Apply `packages/database/d1/schema.sql` to D1 and the equivalent PostgreSQL migrations to the private database.
6. Deploy the Worker and Pages assets.
7. Visit the Pages URL and complete the Setup Wizard.
8. Configure Telegram, Jellyfin, TMDB, Cloudflare, upload, cache, and security settings in the UI.
9. Validate all connections in the Health Dashboard.
10. Remove or rotate `INITIAL_SETUP_TOKEN` after `system.setup_completed=true` is audited.
