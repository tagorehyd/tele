import hashlib
from pathlib import Path
from typing import Iterator

def sha256_file(path: Path, block_size: int = 8*1024*1024) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(block_size), b''):
            h.update(block)
    return h.hexdigest()

def iter_chunks(path: Path, chunk_size: int) -> Iterator[tuple[int, bytes, str]]:
    part=1
    with path.open('rb') as f:
        while True:
            data=f.read(chunk_size)
            if not data: break
            yield part, data, hashlib.sha256(data).hexdigest()
            part += 1
