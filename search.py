import requests
from typing import List, Dict


def search_candidates(artist: str, title: str) -> List[Dict[str, str]]:
    """lrclib 검색으로 후보 목록 반환. [{artist, title}, ...] 최대 10개.

    lrclib는 artist_name 단독 전달 시 결과 0개를 반환하므로 파라미터를 분기한다:
    - 둘 다: artist_name + track_name
    - 아티스트만: q=artist  (general search)
    - 곡명만: track_name=title
    """
    try:
        if artist and title:
            params = {'artist_name': artist, 'track_name': title}
        elif artist:
            params = {'q': artist}
        else:
            params = {'track_name': title}

        response = requests.get(
            'https://lrclib.net/api/search',
            params=params,
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
