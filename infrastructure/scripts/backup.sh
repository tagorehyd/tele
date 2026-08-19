#!/usr/bin/env bash
set -euo pipefail
stamp=$(date -u +%Y%m%dT%H%M%SZ)
mkdir -p backups/$stamp
docker exec docker-postgres-1 pg_dump -U tmc tmc | gzip > backups/$stamp/postgres.sql.gz
wrangler d1 export telegram-media-cloud --remote --output backups/$stamp/d1.sql
wrangler kv:key list --namespace-id "$KV_NAMESPACE_ID" > backups/$stamp/kv-keys.json
