from dataclasses import dataclass
from datetime import datetime, time
from zoneinfo import ZoneInfo

@dataclass(frozen=True)
class UploadPolicy:
    timezone: str
    allowed_days: list[int]
    windows: list[tuple[str,str]]
    monthly_limit_bytes: int
    @classmethod
    def from_settings(cls, s): return cls(s.upload_timezone, s.allowed_days, s.upload_windows, s.monthly_upload_limit_bytes)
    def is_open(self, now: datetime | None = None) -> bool:
        current = now.astimezone(ZoneInfo(self.timezone)) if now else datetime.now(ZoneInfo(self.timezone))
        if current.weekday() not in self.allowed_days: return False
        t=current.time()
        for start,end in self.windows:
            sh,sm=map(int,start.split(':')); eh,em=map(int,end.split(':'))
            if time(sh,sm) <= t <= time(eh,em): return True
        return False
    def quota_allows(self, uploaded_this_month: int, next_bytes: int) -> bool:
        return uploaded_this_month + next_bytes <= self.monthly_limit_bytes
