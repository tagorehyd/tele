# Architecture

Telegram is canonical storage. i5serv runs the Upload Manager for scanning, hashing, chunking, manifesting and uploading, plus a private Telegram Gateway for controlled retrieval. Cloudflare Pages hosts the React UI. The Worker handles every user request, reads search metadata only from D1, caches hot media in R2, stores sessions and operational state in KV/D1, and contacts the Gateway only on cache misses.

Security boundaries: Upload Manager is bound to localhost/private networks; Gateway requires JWT, API keys, replay nonces, timestamps, CIDR filtering at Nginx/firewall, and Telethon session recovery. Secrets are AES-256-GCM encrypted with a rotatable master key.
