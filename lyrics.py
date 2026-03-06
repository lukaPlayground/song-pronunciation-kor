import os
import requests
import lyricsgenius
from typing import Optional, Tuple


def search_lrclib(artist: str, title: str) -> Optional[str]:
    """Search lrclib.net for plain lyrics. Returns None if not found."""
    try:
        response = requests.get(
            'https://lrclib.net/api/search',
            params={'artist_name': artist, 'track_name': title},
            timeout=10
        )
        if response.status_code != 200:
            return None
        results = response.json()
        for item in results:
            if item.get('plainLyrics'):
                return item['plainLyrics']
        return None
    except Exception:
        return None


def search_genius(artist: str, title: str) -> Optional[str]:
    """Search Genius for lyrics (fallback). Returns None if not found."""
    token = os.getenv('GENIUS_ACCESS_TOKEN')
    if not token:
        return None
    try:
        genius = lyricsgenius.Genius(
            token,
            verbose=False,
            remove_section_headers=True,
            timeout=15
        )
        song = genius.search_song(title, artist)
        if song and song.lyrics:
            return song.lyrics
        return None
    except Exception:
        return None


def search_lyrics(artist: str, title: str) -> Tuple[Optional[str], str]:
    """Search with lrclib first, Genius fallback.

    Returns:
        (lyrics_text, source) where source is 'lrclib' | 'genius' | 'none'
    """
    lyrics = search_lrclib(artist, title)
    if lyrics:
        return lyrics, 'lrclib'

    lyrics = search_genius(artist, title)
    if lyrics:
        return lyrics, 'genius'

    return None, 'none'
