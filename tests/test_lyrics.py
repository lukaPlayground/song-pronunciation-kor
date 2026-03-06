import pytest
from unittest.mock import patch, MagicMock
from lyrics import search_lrclib, search_genius, search_lyrics, search_lyricsovh


# -- lrclib tests -------------------------------------------

def test_search_lrclib_success():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = [
        {'plainLyrics': 'Hello world\nGoodbye', 'trackName': 'Test'}
    ]
    with patch('lyrics.requests.get', return_value=mock_resp):
        result = search_lrclib('Artist', 'Song')
    assert result == 'Hello world\nGoodbye'


def test_search_lrclib_empty_results():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = []
    with patch('lyrics.requests.get', return_value=mock_resp):
        result = search_lrclib('Unknown', 'Unknown')
    assert result is None


def test_search_lrclib_no_plain_lyrics():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = [{'syncedLyrics': '[00:01.00] hi', 'plainLyrics': None}]
    with patch('lyrics.requests.get', return_value=mock_resp):
        result = search_lrclib('Artist', 'Song')
    assert result is None


def test_search_lrclib_network_error():
    with patch('lyrics.requests.get', side_effect=Exception('timeout')):
        result = search_lrclib('Artist', 'Song')
    assert result is None


def test_search_lrclib_http_error():
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    with patch('lyrics.requests.get', return_value=mock_resp):
        result = search_lrclib('Artist', 'Song')
    assert result is None


# -- lyricsovh tests ----------------------------------------

def test_search_lyricsovh_success():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {'lyrics': 'OVH Lyrics'}
    with patch('lyrics.requests.get', return_value=mock_resp):
        result = search_lyricsovh('Artist', 'Song')
    assert result == 'OVH Lyrics'


def test_search_lyricsovh_not_found():
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    with patch('lyrics.requests.get', return_value=mock_resp):
        result = search_lyricsovh('Artist', 'Song')
    assert result is None


def test_search_lyricsovh_network_error():
    with patch('lyrics.requests.get', side_effect=Exception('timeout')):
        result = search_lyricsovh('Artist', 'Song')
    assert result is None


def test_search_lyricsovh_no_lyrics_key():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {'error': 'No lyrics found'}
    with patch('lyrics.requests.get', return_value=mock_resp):
        result = search_lyricsovh('Artist', 'Song')
    assert result is None


# -- search_lyrics fallback tests ---------------------------

def test_search_lyrics_lrclib_first():
    with patch('lyrics.search_lrclib', return_value='Lyrics') as mock_lrc:
        with patch('lyrics.search_genius') as mock_genius:
            with patch('lyrics.search_lyricsovh') as mock_ovh:
                text, source = search_lyrics('Artist', 'Song')
    assert text == 'Lyrics'
    assert source == 'lrclib'
    mock_genius.assert_not_called()
    mock_ovh.assert_not_called()


def test_search_lyrics_genius_fallback():
    with patch('lyrics.search_lrclib', return_value=None):
        with patch('lyrics.search_genius', return_value='Genius Lyrics'):
            with patch('lyrics.search_lyricsovh') as mock_ovh:
                text, source = search_lyrics('Artist', 'Song')
    assert text == 'Genius Lyrics'
    assert source == 'genius'
    mock_ovh.assert_not_called()


def test_search_lyrics_lyricsovh_fallback():
    with patch('lyrics.search_lrclib', return_value=None):
        with patch('lyrics.search_genius', return_value=None):
            with patch('lyrics.search_lyricsovh', return_value='OVH Lyrics'):
                text, source = search_lyrics('Artist', 'Song')
    assert text == 'OVH Lyrics'
    assert source == 'lyricsovh'


def test_search_lyrics_not_found():
    with patch('lyrics.search_lrclib', return_value=None):
        with patch('lyrics.search_genius', return_value=None):
            with patch('lyrics.search_lyricsovh', return_value=None):
                text, source = search_lyrics('Artist', 'Song')
    assert text is None
    assert source == 'none'


def test_search_lyrics_not_found_all_fail():
    with patch('lyrics.search_lrclib', return_value=None):
        with patch('lyrics.search_genius', return_value=None):
            with patch('lyrics.search_lyricsovh', return_value=None):
                text, source = search_lyrics('Artist', 'Song')
    assert text is None
    assert source == 'none'


def test_search_lyrics_lyricsovh_not_called_when_genius_found():
    with patch('lyrics.search_lrclib', return_value=None):
        with patch('lyrics.search_genius', return_value='Genius Lyrics'):
            with patch('lyrics.search_lyricsovh') as mock_ovh:
                text, source = search_lyrics('Artist', 'Song')
    assert text == 'Genius Lyrics'
    assert source == 'genius'
    mock_ovh.assert_not_called()
