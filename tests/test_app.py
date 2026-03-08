import pytest
from unittest.mock import patch


@pytest.fixture
def client():
    from app import app
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# ── static serving ─────────────────────────────────────────

def test_index_returns_html(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"<!DOCTYPE html>" in response.data


# ── /api/lyrics ────────────────────────────────────────────

def test_lyrics_success(client):
    with patch("app.search_lyrics", return_value=("Hello world", "lrclib")):
        resp = client.post("/api/lyrics",
                           json={"artist": "Coldplay", "title": "Yellow"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["lyrics"] == "Hello world"
    assert data["source"] == "lrclib"


def test_lyrics_title_only(client):
    """제목만 있어도 검색 성공"""
    with patch("app.search_lyrics", return_value=("Hello world", "lrclib")):
        resp = client.post("/api/lyrics", json={"title": "Yellow"})
    assert resp.status_code == 200


def test_lyrics_artist_only(client):
    """아티스트만 있어도 검색 성공"""
    with patch("app.search_lyrics", return_value=("Hello world", "lrclib")):
        resp = client.post("/api/lyrics", json={"artist": "Coldplay"})
    assert resp.status_code == 200


def test_lyrics_missing_both(client):
    """둘 다 없으면 400"""
    resp = client.post("/api/lyrics", json={})
    assert resp.status_code == 400


def test_lyrics_not_found(client):
    with patch("app.search_lyrics", return_value=(None, "none")):
        resp = client.post("/api/lyrics",
                           json={"artist": "Unknown", "title": "Unknown"})
    assert resp.status_code == 404


# ── /api/pronunciation ─────────────────────────────────────────

def test_pronunciation_success(client):
    mock_lines = [{"original": "hello", "pronunciation": "흐어르오"}]
    with patch("app.lyrics_to_korean", return_value=mock_lines):
        resp = client.post("/api/pronunciation", json={"lyrics": "hello"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["lines"] == mock_lines


def test_pronunciation_missing_lyrics(client):
    resp = client.post("/api/pronunciation", json={})
    assert resp.status_code == 400


# ── /api/search ─────────────────────────────────────────────

def test_search_returns_candidates(client):
    mock_results = [{'artist': 'Coldplay', 'title': 'Yellow'}]
    with patch('app.search_candidates', return_value=mock_results):
        resp = client.post('/api/search', json={'query': 'Coldplay Yellow'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['results'] == mock_results


def test_search_empty_results(client):
    with patch('app.search_candidates', return_value=[]):
        resp = client.post('/api/search', json={'query': 'Unknown'})
    assert resp.status_code == 200
    assert resp.get_json()['results'] == []


def test_search_missing_query(client):
    resp = client.post('/api/search', json={})
    assert resp.status_code == 400


def test_search_with_artist_name(client):
    with patch('app.search_candidates', return_value=[]):
        resp = client.post('/api/search', json={'query': 'Coldplay'})
    assert resp.status_code == 200


def test_search_with_song_title(client):
    with patch('app.search_candidates', return_value=[]):
        resp = client.post('/api/search', json={'query': 'Yellow'})
    assert resp.status_code == 200
