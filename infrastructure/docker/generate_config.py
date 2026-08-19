import base64
import json
import os
import secrets
from pathlib import Path

CONFIG_DIR = Path(os.environ.get("TELE_CONFIG_DIR", "/config"))
CONFIG_FILE = CONFIG_DIR / "config.json"
POSTGRES_PASSWORD_FILE = CONFIG_DIR / "postgres_password"

DB_USER = os.environ.get("POSTGRES_USER", "tmc")
DB_NAME = os.environ.get("POSTGRES_DB", "telegram_media_cloud")
DB_HOST = os.environ.get("POSTGRES_HOST", "127.0.0.1")
DB_PORT = os.environ.get("POSTGRES_PORT", "5432")

CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def write_secret(path: Path, value: str) -> None:
    path.write_text(value, encoding="utf-8")
    path.chmod(0o600)

if CONFIG_FILE.exists():
    config = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
else:
    postgres_password = secrets.token_urlsafe(32)
    config = {
        "database_url": f"postgresql+asyncpg://{DB_USER}:{postgres_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
        "encryption_master_key": base64.b64encode(secrets.token_bytes(32)).decode("ascii"),
        "initial_setup_token": secrets.token_urlsafe(48),
    }
    CONFIG_FILE.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    CONFIG_FILE.chmod(0o600)

password = config["database_url"].split(":", 2)[2].split("@", 1)[0]
write_secret(POSTGRES_PASSWORD_FILE, password)
print(f"Bootstrap configuration is available at {CONFIG_FILE}")
