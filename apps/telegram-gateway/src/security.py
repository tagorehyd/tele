import time
import jwt
from fastapi import HTTPException
from packages.auth.src.crypto import SecretBox
from packages.configuration.src.settings_service import SettingsService

_seen: dict[str, float] = {}

def _prune(now: float) -> None:
    for nonce, expires in list(_seen.items()):
        if expires < now:
            _seen.pop(nonce, None)

async def verify_gateway_token(token: str, nonce: str | None, timestamp: str | None, settings: SettingsService) -> bool:
    now = time.time(); _prune(now)
    if not nonce or not timestamp or abs(now - int(timestamp)) > 300 or nonce in _seen:
        return False
    jwt_secret = await settings.get('security.jwt_secret', reveal_secret=True)
    if not jwt_secret:
        raise HTTPException(409, 'gateway jwt secret is not configured')
    payload = jwt.decode(token, jwt_secret.value, algorithms=['HS256'], audience='telegram-gateway')
    _seen[nonce] = now + 300
    return payload.get('scope') in {'gateway:read', 'admin'}
