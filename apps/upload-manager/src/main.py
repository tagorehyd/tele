from fastapi import FastAPI, Depends
from prometheus_client import make_asgi_app
from .scanner import scan_libraries
from .scheduler import UploadPolicy
from .settings import Settings

app = FastAPI(title="Telegram Media Cloud Upload Manager", version="1.0.0")
app.mount("/metrics", make_asgi_app())

def settings(): return Settings()

@app.get("/healthz")
async def healthz():
    return {"status":"ok","service":"upload-manager","public":False}

@app.post("/internal/scan")
async def scan(cfg: Settings = Depends(settings)):
    return await scan_libraries(cfg.library_paths)

@app.get("/internal/upload-window")
async def upload_window(cfg: Settings = Depends(settings)):
    policy = UploadPolicy.from_settings(cfg)
    return {"allowed": policy.is_open(), "timezone": cfg.upload_timezone}
