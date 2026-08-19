# Operations runbook

Daily: review Grafana cache hit ratio, upload queue depth, Telegram gateway health, and recent audit errors. Weekly: run restore drills for manifests and D1 exports. Monthly: verify upload quota reset and rotate Cloudflare/API credentials where policy requires.

Cache cleanup: Worker records cache objects in D1. Evict least-recently-used objects when configured bytes exceed the `cache.max_bytes` setting, default 6 GiB. Upload quota applies only to upload jobs; playback, downloads, browsing, and search are never quota-limited.
