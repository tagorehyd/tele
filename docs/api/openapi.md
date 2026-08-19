# Public Worker API

The Cloudflare Worker exposes these authenticated routes: `POST /api/login`, `POST /api/logout`, `POST /api/refresh`, `GET /api/search`, `GET /api/movie/{id}`, `GET /api/show/{id}`, `GET /api/play/{id}`, `GET /api/download/{id}`, `GET /api/stats`, `GET /api/settings`, and `POST /api/settings`. FastAPI services expose private OpenAPI JSON at `/openapi.json` on localhost-bound ports for internal automation only.
