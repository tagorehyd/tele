from fastapi import FastAPI, Depends, Header, HTTPException
from prometheus_client import make_asgi_app
from packages.auth.src.crypto import SecretBox
from packages.configuration.src.settings_service import SettingsService
from .db import sessionmaker_from_bootstrap
from .scanner import scan_libraries
from .scheduler import UploadPolicy
from .settings import BootstrapSettings

app = FastAPI(title="Telegram Media Cloud Upload Manager", version="1.1.0")
app.mount("/metrics", make_asgi_app())

def bootstrap(): return BootstrapSettings()

def require_setup_token(x_setup_token: str | None = Header(default=None), cfg: BootstrapSettings = Depends(bootstrap)):
    if x_setup_token != cfg.initial_setup_token:
        raise HTTPException(401, 'invalid setup token')

@app.get('/healthz')
async def healthz(): return {'status':'ok','service':'upload-manager','public':False}

@app.post('/internal/setup/complete', dependencies=[Depends(require_setup_token)])
async def complete_setup(payload: dict, cfg: BootstrapSettings = Depends(bootstrap)):
    maker = sessionmaker_from_bootstrap(cfg)
    async with maker() as session:
        svc = SettingsService(session, SecretBox(cfg.encryption_master_key))
        for key, value in payload.items():
            await svc.set(key, value, 'setup-wizard')
        await svc.set('system.setup_completed', True, 'setup-wizard')
        await session.commit()
    return {'setup_completed': True}

@app.post('/internal/scan')
async def scan(cfg: BootstrapSettings = Depends(bootstrap)):
    maker = sessionmaker_from_bootstrap(cfg)
    async with maker() as session:
        svc = SettingsService(session, SecretBox(cfg.encryption_master_key))
        paths = await svc.get('jellyfin.library_paths', reveal_secret=True)
        if not paths: raise HTTPException(409, 'jellyfin library paths are not configured')
        return await scan_libraries(paths.value)

@app.get('/internal/upload-window')
async def upload_window(cfg: BootstrapSettings = Depends(bootstrap)):
    maker = sessionmaker_from_bootstrap(cfg)
    async with maker() as session:
        svc = SettingsService(session, SecretBox(cfg.encryption_master_key))
        rules = await svc.get('upload.rules', reveal_secret=True)
        if not rules: raise HTTPException(409, 'upload rules are not configured')
        policy = UploadPolicy.from_dict(rules.value)
        return {'allowed': policy.is_open(), 'timezone': policy.timezone}
