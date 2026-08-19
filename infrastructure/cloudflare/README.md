# Cloudflare provisioning

Create D1, KV, R2, Worker, and Pages resources with Wrangler or the Cloudflare dashboard. Bind resource identifiers to the Worker in Cloudflare project settings or deployment automation. Do not store Telegram, Jellyfin, TMDB, JWT, gateway, or Cloudflare secrets in source files.

Required resource commands:

```bash
wrangler d1 create telegram-media-cloud
wrangler d1 execute telegram-media-cloud --remote --file packages/database/d1/schema.sql
wrangler kv namespace create TMC_KV
wrangler r2 bucket create telegram-media-cloud-cache
cd apps/worker && wrangler deploy
cd ../web && npm ci && npm run build && wrangler pages deploy dist --project-name telegram-media-cloud
```

After Pages is deployed, complete the Setup Wizard. The Cloudflare settings page stores account ID, Worker URL, Worker secret, D1 database ID, KV namespace, R2 bucket, Pages project, and domain in the database-backed settings subsystem.
