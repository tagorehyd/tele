from dataclasses import dataclass
from datetime import datetime, time
from zoneinfo import ZoneInfo

@dataclass(frozen=True)
class UploadPolicy:
    timezone: str
    allowed_days: list[int]
    windows: list[tuple[str, str]]
    monthly_limit_bytes: int
    scheduling_enabled: bool = True
    quotas_enabled: bool = True
    sha_validation_enabled: bool = True

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            timezone=data['timezone'],
            allowed_days=[int(day) for day in data['allowed_days']],
            windows=[(w['start'], w['end']) for w in data['windows']],
            monthly_limit_bytes=int(data['monthly_upload_limit_bytes']),
            scheduling_enabled=bool(data.get('scheduling_enabled', True)),
            quotas_enabled=bool(data.get('quotas_enabled', True)),
            sha_validation_enabled=bool(data.get('sha_validation_enabled', True)),
        )

    def is_open(self, now: datetime | None = None) -> bool:
        if not self.scheduling_enabled:
            return True
        current = now.astimezone(ZoneInfo(self.timezone)) if now else datetime.now(ZoneInfo(self.timezone))
        if current.weekday() not in self.allowed_days:
            return False
        current_time = current.time()
        return any(time(*map(int, start.split(':'))) <= current_time <= time(*map(int, end.split(':'))) for start, end in self.windows)

    def quota_allows(self, uploaded_this_month: int, next_bytes: int) -> bool:
        return True if not self.quotas_enabled else uploaded_this_month + next_bytes <= self.monthly_limit_bytes
