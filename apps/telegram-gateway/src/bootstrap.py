from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

class BootstrapSettings(BaseSettings):
    database_url: str
    encryption_master_key: str
    initial_setup_token: str
    class Config:
        extra = 'forbid'

def sessionmaker_from_bootstrap(cfg: BootstrapSettings):
    engine = create_async_engine(cfg.database_url, pool_pre_ping=True, pool_size=10, max_overflow=20)
    return async_sessionmaker(engine, expire_on_commit=False)
