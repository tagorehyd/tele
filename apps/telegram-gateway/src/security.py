import os, time, jwt
SECRET=os.getenv('TMC_JWT_SECRET','dev-secret-change')
_seen=set()
def verify_gateway_token(token: str, nonce: str | None, ts: str | None) -> bool:
    try:
        if not nonce or not ts or abs(time.time()-int(ts))>300 or nonce in _seen: return False
        payload=jwt.decode(token, SECRET, algorithms=['HS256'], audience='telegram-gateway')
        _seen.add(nonce)
        return payload.get('scope') in {'gateway:read','admin'}
    except Exception: return False
