import json
import os
from pathlib import Path
from typing import Any

from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


def _config_file_values() -> dict[str, Any]:
    config_file = Path(os.environ.get("CONFIG_FILE", "/run/tele-config/config.json"))
    if not config_file.exists():
        return {}
    with config_file.open(encoding="utf-8") as fh:
        return json.load(fh)


class BootstrapSettings(BaseSettings):
    database_url: str
    encryption_master_key: str
    initial_setup_token: str

    def __init__(self, **data: Any):
        file_values = _config_file_values()
        for field_name in type(self).model_fields:
            env_name = field_name.upper()
            if field_name not in data and env_name not in os.environ and field_name in file_values:
                data[field_name] = file_values[field_name]
        super().__init__(**data)

    class Config:
        extra = 'forbid'

def sessionmaker_from_bootstrap(cfg: BootstrapSettings):
    engine = create_async_engine(cfg.database_url, pool_pre_ping=True, pool_size=10, max_overflow=20)
    return async_sessionmaker(engine, expire_on_commit=False)
