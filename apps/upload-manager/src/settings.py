from pydantic_settings import BaseSettings

class BootstrapSettings(BaseSettings):
    database_url: str
    encryption_master_key: str
    initial_setup_token: str

    class Config:
        extra = 'forbid'
