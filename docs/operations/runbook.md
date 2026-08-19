# Operations runbook

Use the Health Dashboard for Telegram status, Telethon session status, Jellyfin status, TMDB status, Cloudflare Worker status, D1 status, KV status, R2 status, Upload Manager status, Gateway status, last check time, latency, and errors.

Settings changes must be made in the web UI. Secret changes are encrypted, masked in normal responses, and written to audit logs. Rotate the encryption master key by re-encrypting `secret_store` values with the new key version during a maintenance window.

Upload quota applies only to Upload Manager jobs. Playback, downloads, search, and browsing remain unthrottled by monthly upload quotas.
