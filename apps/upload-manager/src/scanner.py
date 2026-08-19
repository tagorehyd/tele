from pathlib import Path
from .chunking import sha256_file
from .metadata import read_nfo

VIDEO_EXT={'.mkv','.mp4','.m4v','.avi','.mov','.webm'}
async def scan_libraries(paths: list[str]) -> dict:
    media=[]
    for root in paths:
        base=Path(root)
        if not base.exists(): continue
        for p in base.rglob('*'):
            if p.is_file() and p.suffix.lower() in VIDEO_EXT:
                st=p.stat(); meta=read_nfo(p)
                media.append({'path':str(p),'size':st.st_size,'mtime':int(st.st_mtime),'sha256':sha256_file(p),'metadata':meta})
    return {'count':len(media),'media':media}
