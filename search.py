import re
import requests
from typing import List, Dict


def _normalize_artist(name: str) -> str:
    """Normalize artist name for dedup comparison only (not display)."""
    name = name.lower()
    name = re.sub(r'\s*&\s*', ' and ', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name


def search_candidates(query: str) -> List[Dict[str, str]]:
    """lrclib q= 통합 검색으로 후보 목록 반환. [{artist, title}, ...] 최대 10개."""
    try:
        response = requests.get(
            'https://lrclib.net/api/search',
            params={'q': query},
            timeout=10
        )
        if response.status_code != 200:
            return []
        seen = set()
        candidates = []
        for item in response.json():
            artist_name = (item.get('artistName') or '').strip()
            track_name = (item.get('trackName') or '').strip()
            if not artist_name or not track_name:
                continue
            key = f"{_normalize_artist(artist_name)}|{track_name.lower()}"
            if key in seen:
                continue
            seen.add(key)
            candidates.append({'artist': artist_name, 'title': track_name})
            if len(candidates) >= 10:
                break
        return candidates
    except Exception:
        return []
