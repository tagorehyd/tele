import json
from telethon import TelegramClient
from packages.configuration.src.settings_service import SettingsService

class TelegramStorage:
    def __init__(self, settings: SettingsService):
        self.settings = settings
        self.client: TelegramClient | None = None

    async def _ensure(self):
        if self.client and self.client.is_connected():
            return
        api_id = await self.settings.get('telegram.api_id', reveal_secret=True)
        api_hash = await self.settings.get('telegram.api_hash', reveal_secret=True)
        session = await self.settings.get('telegram.session_name', reveal_secret=True)
        if not api_id or not api_hash or not session:
            raise RuntimeError('telegram configuration is incomplete')
        self.client = TelegramClient(str(session.value), int(api_id.value), str(api_hash.value))
        await self.client.connect()

    def parse_range(self, header):
        if not header or not header.startswith('bytes='):
            return 0, None
        start, end = header[6:].split('-', 1)
        return int(start or 0), int(end) if end else None

    async def get_json(self, channel, message_id):
        await self._ensure(); assert self.client is not None
        msg = await self.client.get_messages(channel, ids=message_id)
        data = await self.client.download_media(msg, bytes)
        return json.loads(data.decode())

    async def stream_message(self, channel, message_id, start=0, end=None):
        await self._ensure(); assert self.client is not None
        msg = await self.client.get_messages(channel, ids=message_id)
        limit = None if end is None else end - start + 1
        async def gen():
            sent = 0
            async for chunk in self.client.iter_download(msg.media, offset=start, request_size=1024 * 1024):
                if limit is not None and sent + len(chunk) > limit:
                    chunk = chunk[:limit - sent]
                if not chunk:
                    break
                sent += len(chunk)
                yield chunk
                if limit is not None and sent >= limit:
                    break
        return gen(), (limit if limit is not None else getattr(msg.file, 'size', 0) - start)
