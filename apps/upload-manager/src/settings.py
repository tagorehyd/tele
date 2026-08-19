from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    database_url: str = Field("postgresql+asyncpg://tmc:${POSTGRES_PASSWORD}@postgres:5432/tmc", alias="DATABASE_URL")
    redis_url: str = Field("redis://redis:6379/0", alias="REDIS_URL")
    library_paths: list[str] = ["/media/Movies", "/media/TV Shows", "/media/Anime"]
    upload_timezone: str = Field("America/New_York", alias="UPLOAD_TIMEZONE")
    monthly_upload_limit_bytes: int = 2 * 1024**4
    chunk_size_bytes: int = 1900 * 1000 * 1000
    allowed_days: list[int] = [0,1,2,3,4]
    upload_windows: list[tuple[str,str]] = [("01:00","06:00"),("10:00","16:00")]
