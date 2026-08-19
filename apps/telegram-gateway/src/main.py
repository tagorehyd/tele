from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import StreamingResponse
from prometheus_client import make_asgi_app
from .security import verify_gateway_token
from .telegram_client import TelegramStorage

app=FastAPI(title='Telegram Media Cloud Gateway', version='1.0.0')
app.mount('/metrics', make_asgi_app())
storage=TelegramStorage()

@app.middleware('http')
async def auth(request: Request, call_next):
    if request.url.path in {'/healthz','/metrics'} or request.url.path.startswith('/metrics/'):
        return await call_next(request)
    token=request.headers.get('authorization','').removeprefix('Bearer ')
    if not verify_gateway_token(token, request.headers.get('x-request-nonce'), request.headers.get('x-request-timestamp')):
        raise HTTPException(401,'invalid gateway token')
    return await call_next(request)

@app.get('/healthz')
async def healthz(): return {'status':'ok','service':'telegram-gateway'}

@app.get('/manifest/{channel}/{message_id}')
async def manifest(channel: str, message_id: int): return await storage.get_json(channel, message_id)

@app.get('/chunk/{channel}/{message_id}')
async def chunk(channel: str, message_id: int, range: str | None = Header(default=None)):
    start,end=storage.parse_range(range)
    stream,size=await storage.stream_message(channel, message_id, start, end)
    headers={'Accept-Ranges':'bytes','Content-Length':str(size)}
    if range: headers['Content-Range']=f'bytes {start}-{start+size-1}/*'
    return StreamingResponse(stream, status_code=206 if range else 200, headers=headers, media_type='application/octet-stream')
