from fastapi import FastAPI, Header, HTTPException, Request, Depends
from fastapi.responses import StreamingResponse
from prometheus_client import make_asgi_app
from packages.auth.src.crypto import SecretBox
from packages.configuration.src.settings_service import SettingsService
from .bootstrap import BootstrapSettings, sessionmaker_from_bootstrap
from .security import verify_gateway_token
from .telegram_client import TelegramStorage

app = FastAPI(title='Telegram Media Cloud Gateway', version='1.1.0')
app.mount('/metrics', make_asgi_app())

def bootstrap(): return BootstrapSettings()
async def settings_service(cfg: BootstrapSettings = Depends(bootstrap)):
    maker = sessionmaker_from_bootstrap(cfg)
    async with maker() as session:
        yield SettingsService(session, SecretBox(cfg.encryption_master_key))

@app.middleware('http')
async def auth(request: Request, call_next):
    if request.url.path in {'/healthz', '/metrics'} or request.url.path.startswith('/metrics/'):
        return await call_next(request)
    return await call_next(request)

@app.get('/healthz')
async def healthz(): return {'status': 'ok', 'service': 'telegram-gateway'}

@app.get('/manifest/{channel}/{message_id}')
async def manifest(channel: str, message_id: int, request: Request, settings: SettingsService = Depends(settings_service)):
    token = request.headers.get('authorization', '').removeprefix('Bearer ')
    if not await verify_gateway_token(token, request.headers.get('x-request-nonce'), request.headers.get('x-request-timestamp'), settings):
        raise HTTPException(401, 'invalid gateway token')
    return await TelegramStorage(settings).get_json(channel, message_id)

@app.get('/chunk/{channel}/{message_id}')
async def chunk(channel: str, message_id: int, request: Request, range: str | None = Header(default=None), settings: SettingsService = Depends(settings_service)):
    token = request.headers.get('authorization', '').removeprefix('Bearer ')
    if not await verify_gateway_token(token, request.headers.get('x-request-nonce'), request.headers.get('x-request-timestamp'), settings):
        raise HTTPException(401, 'invalid gateway token')
    storage = TelegramStorage(settings)
    start, end = storage.parse_range(range)
    stream, size = await storage.stream_message(channel, message_id, start, end)
    headers = {'Accept-Ranges': 'bytes', 'Content-Length': str(size)}
    if range:
        headers['Content-Range'] = f'bytes {start}-{start + size - 1}/*'
    return StreamingResponse(stream, status_code=206 if range else 200, headers=headers, media_type='application/octet-stream')
