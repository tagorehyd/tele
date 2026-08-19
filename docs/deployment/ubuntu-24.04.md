# Fresh Ubuntu 24.04 deployment

1. Create DNS in Cloudflare for the Pages app and Worker route.
2. Install Docker: `sudo apt update && sudo apt install -y ca-certificates curl gnupg ufw nginx` then install Docker Engine from Docker's Ubuntu repository.
3. Install Wrangler: `npm i -g wrangler`. Authenticate with `wrangler login`.
4. Create Cloudflare resources: `wrangler d1 create telegram-media-cloud`, `wrangler kv namespace create TMC_KV`, `wrangler r2 bucket create telegram-media-cloud-cache`, and update `apps/worker/wrangler.toml`.
5. Apply D1 schema: `wrangler d1 execute telegram-media-cloud --remote --file packages/database/d1/schema.sql`.
6. Configure `.env` from `.env.example`; generate keys with `openssl rand -base64 32` and `openssl rand -hex 64`.
7. Start private services: `docker compose -f infrastructure/docker/docker-compose.yml up -d --build`.
8. Deploy Worker: `cd apps/worker && wrangler deploy`.
9. Deploy Pages: `cd apps/web && npm ci && npm run build && wrangler pages deploy dist --project-name telegram-media-cloud`.
10. Configure UFW so only SSH, Nginx loopback, and Cloudflare-originated tunnel/proxy traffic are permitted. Users must never receive direct routes to i5serv.

Screenshot references: Cloudflare dashboard resource IDs are found on D1, KV, R2, Workers, and Pages resource settings screens after creation.
