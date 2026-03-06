import requests
from typing import List, Dict


def search_candidates(artist: str, title: str) -> List[Dict[str, str]]:
    """lrclib 검색으로 후보 목록 반환. [{artist, title}, ...] 최대 10개."""
    try:
        response = requests.get(
            'https://lrclib.net/api/search',
            params={'artist_name': artist, 'track_name': title},
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
            key = f"{artist_name}|{track_name}".lower()
            if key in seen:
                continue
            seen.add(key)
            candidates.append({'artist': artist_name, 'title': track_name})
            if len(candidates) >= 10:
                break
        return candidates
    except Exception:
        return []
