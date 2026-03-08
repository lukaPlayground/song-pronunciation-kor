import pytest
from unittest.mock import patch, MagicMock
from search import search_candidates


def test_search_candidates_returns_list():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = [
        {'artistName': 'Coldplay', 'trackName': 'Yellow'},
        {'artistName': 'Coldplay', 'trackName': 'The Scientist'},
    ]
    with patch('search.requests.get', return_value=mock_resp):
        result = search_candidates('Coldplay')
    assert result == [
        {'artist': 'Coldplay', 'title': 'Yellow'},
        {'artist': 'Coldplay', 'title': 'The Scientist'},
    ]


def test_search_candidates_deduplicates():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = [
        {'artistName': 'Coldplay', 'trackName': 'Yellow'},
        {'artistName': 'Coldplay', 'trackName': 'Yellow'},  # 중복
    ]
    with patch('search.requests.get', return_value=mock_resp):
        result = search_candidates('Coldplay Yellow')
    assert len(result) == 1


def test_search_candidates_max_10():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = [
        {'artistName': f'Artist{i}', 'trackName': f'Song{i}'} for i in range(20)
    ]
    with patch('search.requests.get', return_value=mock_resp):
        result = search_candidates('Song')
    assert len(result) == 10


def test_search_candidates_empty_result():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = []
    with patch('search.requests.get', return_value=mock_resp):
        result = search_candidates('Unknown')
    assert result == []


def test_search_candidates_skips_missing_fields():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = [
        {'artistName': '', 'trackName': 'Yellow'},    # artist 빈값
        {'artistName': 'Coldplay', 'trackName': ''},  # title 빈값
        {'artistName': 'Coldplay', 'trackName': 'Yellow'},  # 정상
    ]
    with patch('search.requests.get', return_value=mock_resp):
        result = search_candidates('Coldplay Yellow')
    assert result == [{'artist': 'Coldplay', 'title': 'Yellow'}]


def test_search_candidates_http_error():
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    with patch('search.requests.get', return_value=mock_resp):
        result = search_candidates('Coldplay Yellow')
    assert result == []


def test_search_candidates_network_error():
    with patch('search.requests.get', side_effect=Exception('timeout')):
        result = search_candidates('Coldplay Yellow')
    assert result == []


# ── 파라미터 확인 ──────────────────────────────────────────

def test_always_uses_q_param():
    """항상 q= 파라미터 사용"""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = []
    with patch('search.requests.get', return_value=mock_resp) as mock_get:
        search_candidates('Olivia Dean Danger')
    params = mock_get.call_args.kwargs['params']
    assert params == {'q': 'Olivia Dean Danger'}
