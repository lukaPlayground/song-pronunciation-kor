import pytest
from unittest.mock import patch, MagicMock
from charts import get_chart, SUPPORTED_COUNTRIES


def _mock_resp(results):
    m = MagicMock()
    m.status_code = 200
    m.json.return_value = {'feed': {'results': results}}
    return m


def test_get_chart_returns_list():
    mock = _mock_resp([
        {'name': 'APT.', 'artistName': 'ROSÉ & Bruno Mars'},
        {'name': 'Magnetic', 'artistName': 'ILLIT'},
    ])
    with patch('charts.requests.get', return_value=mock):
        result = get_chart('kr')
    assert len(result) == 2
    assert result[0] == {'rank': '1', 'title': 'APT.', 'artist': 'ROSÉ & Bruno Mars'}
    assert result[1]['rank'] == '2'


def test_get_chart_rank_sequence():
    mock = _mock_resp([
        {'name': f'Song{i}', 'artistName': f'Artist{i}'} for i in range(5)
    ])
    with patch('charts.requests.get', return_value=mock):
        result = get_chart('us')
    assert [r['rank'] for r in result] == ['1', '2', '3', '4', '5']


def test_get_chart_skips_missing_fields():
    mock = _mock_resp([
        {'name': '', 'artistName': 'Artist'},          # name 빈값
        {'name': 'Song', 'artistName': ''},             # artist 빈값
        {'name': 'Valid Song', 'artistName': 'Valid'},  # 정상
    ])
    with patch('charts.requests.get', return_value=mock):
        result = get_chart('gb')
    assert len(result) == 1
    assert result[0]['title'] == 'Valid Song'


def test_get_chart_unsupported_country():
    result = get_chart('zz')
    assert result == []


def test_get_chart_http_error():
    mock = MagicMock()
    mock.status_code = 500
    with patch('charts.requests.get', return_value=mock):
        result = get_chart('kr')
    assert result == []


def test_get_chart_network_error():
    with patch('charts.requests.get', side_effect=Exception('timeout')):
        result = get_chart('us')
    assert result == []


def test_supported_countries_keys():
    assert 'kr' in SUPPORTED_COUNTRIES
    assert 'us' in SUPPORTED_COUNTRIES
    assert 'gb' in SUPPORTED_COUNTRIES
    assert 'jp' in SUPPORTED_COUNTRIES
    assert 'au' in SUPPORTED_COUNTRIES
