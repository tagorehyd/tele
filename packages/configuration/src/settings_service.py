import json
from dataclasses import dataclass
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from packages.auth.src.crypto import SecretBox

SECRET_KEYS = {
    'telegram.api_id', 'telegram.api_hash', 'telegram.phone_number', 'telegram.session',
    'jellyfin.api_key', 'jellyfin.password', 'tmdb.api_key', 'cloudflare.worker_secret',
    'cloudflare.api_token', 'security.jwt_secret', 'security.refresh_secret'
}

@dataclass(frozen=True)
class SettingValue:
    key: str
    value: Any
    encrypted: bool
    version: int

class SettingsService:
    def __init__(self, session: AsyncSession, secret_box: SecretBox):
        self.session = session
        self.secret_box = secret_box

    async def get(self, key: str, *, reveal_secret: bool = False) -> SettingValue | None:
        row = (await self.session.execute(text('select key,value,encrypted,version from settings where key=:key'), {'key': key})).mappings().first()
        if not row:
            return None
        value = row['value']
        encrypted = bool(row['encrypted'])
        if encrypted:
            value = self.secret_box.decrypt(value) if reveal_secret else self.secret_box.mask(self.secret_box.decrypt(value))
        else:
            try:
                value = json.loads(value)
            except Exception:
                pass
        return SettingValue(row['key'], value, encrypted, row['version'])

    async def set(self, key: str, value: Any, actor_id: str, *, force_secret: bool = False) -> None:
        encrypted = force_secret or key in SECRET_KEYS
        stored = self.secret_box.encrypt(str(value)) if encrypted else json.dumps(value)
        await self.session.execute(text('''
            insert into settings(key,value,encrypted,version,updated_by,updated_at)
            values(:key,:value,:encrypted,1,:actor,now())
            on conflict(key) do update set value=excluded.value, encrypted=excluded.encrypted,
              version=settings.version+1, updated_by=excluded.updated_by, updated_at=now()
        '''), {'key': key, 'value': stored, 'encrypted': encrypted, 'actor': actor_id})
        await self.session.execute(text('insert into audit_logs(actor_id,action,resource,metadata) values(:actor,:action,:resource,:metadata)'), {'actor': actor_id, 'action': 'settings.updated', 'resource': key, 'metadata': json.dumps({'encrypted': encrypted})})

    async def setup_completed(self) -> bool:
        v = await self.get('system.setup_completed')
        return bool(v and v.value is True)
