# Bootstrap configuration

Telegram Media Cloud is configuration-first. After installation, administrators manage all settings from the web UI and the database-backed settings subsystem. Do not create environment files containing Telegram, Jellyfin, TMDB, Cloudflare, JWT, Redis, or cache values.

Only three bootstrap environment variables are accepted:

1. `DATABASE_URL` — SQLAlchemy-compatible PostgreSQL URL used by the private services to reach the settings database.
2. `ENCRYPTION_MASTER_KEY` — base64-encoded 32-byte AES-256-GCM key used to decrypt the database secret store. Generate it once and store it in your host secret manager.
3. `INITIAL_SETUP_TOKEN` — one-time high-entropy token required to submit the first-run setup wizard before `system.setup_completed=true` is written.

Every other value is collected by the Setup Wizard and stored in database tables. Secret values are encrypted before persistence, masked by default in API responses, audited on change, and retrievable only by administrators using explicit reveal actions.
