# Cloudflare provisioning

Run these commands from the repository root after `wrangler login`:

```bash
wrangler d1 create telegram-media-cloud
wrangler d1 execute telegram-media-cloud --remote --file packages/database/d1/schema.sql
wrangler kv namespace create TMC_KV
wrangler r2 bucket create telegram-media-cloud-cache
cd apps/worker && wrangler deploy
cd ../web && npm ci && npm run build && wrangler pages deploy dist --project-name telegram-media-cloud
```

Keep Worker secrets out of source control with `wrangler secret put JWT_SECRET`, `wrangler secret put WORKER_SECRET`, and environment-specific Cloudflare dashboard bindings.
