import importlib.util
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

module_path = Path(__file__).resolve().parents[2] / 'apps' / 'upload-manager' / 'src' / 'scheduler.py'
spec = importlib.util.spec_from_file_location('scheduler', module_path)
scheduler = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scheduler)  # type: ignore[union-attr]
UploadPolicy = scheduler.UploadPolicy

def test_upload_window_weekday():
    p = UploadPolicy('UTC', [0, 1, 2, 3, 4], [('01:00', '06:00')], 100)
    assert p.is_open(datetime(2026, 8, 19, 2, 0, tzinfo=ZoneInfo('UTC')))
    assert not p.is_open(datetime(2026, 8, 22, 2, 0, tzinfo=ZoneInfo('UTC')))

def test_upload_quota_applies_only_to_upload_bytes():
    p = UploadPolicy('UTC', [0], [('00:00', '23:59')], 100)
    assert p.quota_allows(90, 10)
    assert not p.quota_allows(90, 11)
