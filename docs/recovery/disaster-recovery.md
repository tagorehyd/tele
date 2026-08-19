# Disaster recovery

Telegram session loss: use the Telegram settings page to reconnect, validate session status, run test download, and audit the session secret rotation.

D1 loss: recreate D1, apply `packages/database/d1/schema.sql`, import the most recent export, and redeploy Worker bindings. If no export exists, rebuild searchable metadata from Telegram manifests in `Archive-Manifests`.

R2 loss: recreate the bucket and binding. No canonical media is lost because Telegram stores manifests and chunks.

KV loss: recreate namespace, force sign-out, rotate JWT/refresh secrets through Security Settings, and validate Worker health.

i5serv or full server loss: provision Ubuntu 24.04, restore the database, provide only `DATABASE_URL`, `ENCRYPTION_MASTER_KEY`, and `INITIAL_SETUP_TOKEN` through the host secret manager, start Docker Compose, reconnect Telegram if needed, validate health checks, and resume upload queues.

Database corruption: restore PostgreSQL and D1 from backups, verify settings versions, decrypt representative secrets with the active master key, and reconcile manifests against Telegram.

Telegram channel recovery: rebuild channel mappings in the UI, validate channel IDs, verify every manifest chunk reference, and re-upload only missing or corrupted chunks.
