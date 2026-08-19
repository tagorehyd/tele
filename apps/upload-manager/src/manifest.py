import json
def build_manifest(media: dict, chunks: list[dict]) -> dict:
    return {k: media.get(k) for k in ['imdb_id','tmdb_id','title','year','sha256','size']} | {'chunks': chunks}
def manifest_bytes(manifest: dict) -> bytes:
    return json.dumps(manifest, sort_keys=True, separators=(',',':')).encode()
