import json, os
from telethon import TelegramClient

class TelegramStorage:
    def __init__(self):
        self.client=TelegramClient(os.getenv('TELEGRAM_SESSION','tmc'), int(os.getenv('TELEGRAM_API_ID','0')), os.getenv('TELEGRAM_API_HASH',''))
    def parse_range(self, header):
        if not header or not header.startswith('bytes='): return 0, None
        s,e=header[6:].split('-',1); return int(s or 0), int(e) if e else None
    async def _ensure(self):
        if not self.client.is_connected(): await self.client.connect()
    async def get_json(self, channel, message_id):
        await self._ensure(); msg=await self.client.get_messages(channel, ids=message_id)
        data=await self.client.download_media(msg, bytes)
        return json.loads(data.decode())
    async def stream_message(self, channel, message_id, start=0, end=None):
        await self._ensure(); msg=await self.client.get_messages(channel, ids=message_id)
        limit=None if end is None else end-start+1
        async def gen():
            sent=0
            async for chunk in self.client.iter_download(msg.media, offset=start, request_size=1024*1024):
                if limit is not None and sent+len(chunk)>limit: chunk=chunk[:limit-sent]
                if not chunk: break
                sent += len(chunk); yield chunk
                if limit is not None and sent>=limit: break
        return gen(), (limit if limit is not None else getattr(msg.file,'size',0)-start)
