import requests
from typing import List, Dict

# iTunes RSS Feed (무료, 인증 불필요)
_ITUNES_URL = 'https://rss.applemarketingtools.com/api/v2/{country}/music/most-played/25/songs.json'

SUPPORTED_COUNTRIES = {
    'kr': '한국',
    'us': 'US',
    'gb': 'UK',
    'jp': '일본',
    'au': 'AU',
}


def get_chart(country: str) -> List[Dict[str, str]]:
    """iTunes RSS에서 국가별 인기 차트 반환. [{rank, title, artist}, ...]"""
    country = country.lower()
    if country not in SUPPORTED_COUNTRIES:
        return []
    try:
        response = requests.get(
            _ITUNES_URL.format(country=country),
            timeout=8
        )
        if response.status_code != 200:
            return []
        items = response.json().get('feed', {}).get('results', [])
        return [
            {
                'rank': str(i + 1),
                'title': item.get('name', '').strip(),
                'artist': item.get('artistName', '').strip(),
            }
            for i, item in enumerate(items)
            if item.get('name') and item.get('artistName')
        ]
    except Exception:
        return []
