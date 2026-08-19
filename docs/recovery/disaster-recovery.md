# Disaster recovery

Telegram session loss: stop services, restore encrypted Telethon session backup, validate login, run Gateway `/healthz`, and perform a test manifest download.

D1 loss: create a new D1 database, import the latest SQL export, reapply `packages/database/d1/schema.sql`, update Worker binding, and redeploy. If exports are unavailable, rebuild D1 by reading Telegram manifests from `Archive-Manifests`.

R2 loss: recreate bucket and binding. No canonical data is lost; the cache repopulates from Telegram through the Gateway.

KV loss: recreate namespace, rotate JWT/session secrets, force user logins, and restore settings from encrypted backups.

i5serv loss or entire server loss: provision Ubuntu 24.04, restore `.env`, Telethon session, PostgreSQL dump, Docker volumes where available, run Docker Compose, validate Telegram channel access, then resume upload queues.

Telegram channel recovery: use manifests in `Archive-Manifests` and channel/message identifiers in D1 to verify all chunks. If a channel is replaced, re-upload affected chunks from source media or reconstructed media and publish replacement manifests.
