from pathlib import Path
import xml.etree.ElementTree as ET

def read_nfo(media_path: Path) -> dict:
    candidates=[media_path.with_name('movie.nfo'), media_path.with_name('tvshow.nfo'), media_path.with_suffix('.nfo')]
    nfo=next((p for p in candidates if p.exists()), None)
    if not nfo: return {}
    root=ET.fromstring(nfo.read_text(encoding='utf-8', errors='ignore'))
    def text(name):
        node=root.find(name); return node.text.strip() if node is not None and node.text else None
    return {
      'imdb_id': text('imdbid') or text('imdb_id'), 'tmdb_id': text('tmdbid') or text('tmdb_id'),
      'title': text('title'), 'original_title': text('originaltitle'), 'sort_title': text('sorttitle'),
      'year': int(text('year')) if text('year') and text('year').isdigit() else None,
      'genres': [g.text for g in root.findall('genre') if g.text], 'studios': [s.text for s in root.findall('studio') if s.text],
      'actors': [a.findtext('name') for a in root.findall('actor') if a.findtext('name')],
      'runtime': int(text('runtime')) if text('runtime') and text('runtime').isdigit() else None, 'plot': text('plot')
    }
