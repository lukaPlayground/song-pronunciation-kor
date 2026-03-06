# 자동완성 + 검색 결과 목록 구현 계획

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 타이핑 중 자동완성 드롭다운 + 검색 버튼 클릭 시 후보 목록 표시 후 선택하여 가사 이동

**Architecture:** 새 `POST /api/search` 엔드포인트(lrclib 기반)를 자동완성과 결과 목록이 공유. 마지막 쿼리 결과를 메모리 캐시하여 API 호출 최소화. 자동완성 선택 시 즉시 가사 검색, 검색 버튼 클릭 시 결과 패널 표시 후 항목 선택으로 가사 이동.

**Tech Stack:** Python Flask, vanilla JS (ES5), lrclib.net API, pytest

---

### Task 1: search.py 모듈 (TDD)

**Files:**
- Create: `search.py`
- Create: `tests/test_search.py`

**Step 1: 테스트 작성**

`tests/test_search.py` 생성:

```python
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
        result = search_candidates('Coldplay', '')
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
        result = search_candidates('Coldplay', 'Yellow')
    assert len(result) == 1


def test_search_candidates_max_10():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = [
        {'artistName': f'Artist{i}', 'trackName': f'Song{i}'} for i in range(20)
    ]
    with patch('search.requests.get', return_value=mock_resp):
        result = search_candidates('', 'Song')
    assert len(result) == 10


def test_search_candidates_empty_result():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = []
    with patch('search.requests.get', return_value=mock_resp):
        result = search_candidates('Unknown', '')
    assert result == []


def test_search_candidates_skips_missing_fields():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = [
        {'artistName': '', 'trackName': 'Yellow'},   # artist 빈값
        {'artistName': 'Coldplay', 'trackName': ''},  # title 빈값
        {'artistName': 'Coldplay', 'trackName': 'Yellow'},  # 정상
    ]
    with patch('search.requests.get', return_value=mock_resp):
        result = search_candidates('Coldplay', 'Yellow')
    assert result == [{'artist': 'Coldplay', 'title': 'Yellow'}]


def test_search_candidates_http_error():
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    with patch('search.requests.get', return_value=mock_resp):
        result = search_candidates('Coldplay', 'Yellow')
    assert result == []


def test_search_candidates_network_error():
    with patch('search.requests.get', side_effect=Exception('timeout')):
        result = search_candidates('Coldplay', 'Yellow')
    assert result == []
```

**Step 2: 실패 확인**

```bash
cd /Users/work6/Desktop/ai-code/song-pronunciation-kor
python3 -m pytest tests/test_search.py -v
```

예상: `ModuleNotFoundError: No module named 'search'`

**Step 3: search.py 구현**

`search.py` 생성:

```python
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
```

**Step 4: 통과 확인**

```bash
python3 -m pytest tests/test_search.py -v
```

예상: `7 passed`

**Step 5: 커밋**

```bash
git add search.py tests/test_search.py
git commit -m "feat: search.py - lrclib 후보 목록 검색 모듈"
```

---

### Task 2: /api/search 엔드포인트 (TDD)

**Files:**
- Modify: `app.py`
- Modify: `tests/test_app.py`

**Step 1: 테스트 작성**

`tests/test_app.py` 하단에 추가:

```python
# ── /api/search ─────────────────────────────────────────────

def test_search_returns_candidates(client):
    mock_results = [{'artist': 'Coldplay', 'title': 'Yellow'}]
    with patch('app.search_candidates', return_value=mock_results):
        resp = client.post('/api/search', json={'artist': 'Coldplay', 'title': ''})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['results'] == mock_results


def test_search_empty_results(client):
    with patch('app.search_candidates', return_value=[]):
        resp = client.post('/api/search', json={'title': 'Unknown'})
    assert resp.status_code == 200
    assert resp.get_json()['results'] == []


def test_search_missing_both(client):
    resp = client.post('/api/search', json={})
    assert resp.status_code == 400


def test_search_artist_only(client):
    with patch('app.search_candidates', return_value=[]):
        resp = client.post('/api/search', json={'artist': 'Coldplay'})
    assert resp.status_code == 200


def test_search_title_only(client):
    with patch('app.search_candidates', return_value=[]):
        resp = client.post('/api/search', json={'title': 'Yellow'})
    assert resp.status_code == 200
```

**Step 2: 실패 확인**

```bash
python3 -m pytest tests/test_app.py -v -k "search"
```

예상: `5 failed` (404 또는 ImportError)

**Step 3: app.py 수정**

`app.py` 상단 import에 추가:

```python
from search import search_candidates
```

`get_pronunciation` 함수 뒤에 새 라우트 추가:

```python
@app.route('/api/search', methods=['POST'])
def get_search_candidates():
    data = request.get_json() or {}
    artist = data.get('artist', '').strip()
    title = data.get('title', '').strip()

    if not artist and not title:
        return jsonify({'error': 'artist or title is required'}), 400

    results = search_candidates(artist, title)
    return jsonify({'results': results})
```

**Step 4: 통과 확인**

```bash
python3 -m pytest tests/ -v
```

예상: 모든 테스트 통과 (기존 35 + 신규 5 = 40 passed)

**Step 5: 커밋**

```bash
git add app.py tests/test_app.py
git commit -m "feat: /api/search 엔드포인트 추가"
```

---

### Task 3: CSS 추가 (자동완성 + 후보 패널)

**Files:**
- Modify: `static/css/style.css`

**Step 1: style.css 하단에 추가**

`.lyric-break` 블록 이후, `@media` 이전에 삽입:

```css
/* Input Wrapper (autocomplete positioning) */
.input-wrapper {
    position: relative;
}

/* Autocomplete Dropdown */
.autocomplete-list {
    position: absolute;
    top: calc(100% + 4px);
    left: 0;
    right: 0;
    background: white;
    border: 1.5px solid #d2d2d7;
    border-radius: 12px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    list-style: none;
    z-index: 100;
    overflow: hidden;
    max-height: 220px;
    overflow-y: auto;
}

.autocomplete-item {
    padding: 12px 18px;
    font-size: 0.95rem;
    cursor: pointer;
    border-bottom: 1px solid #f0f0f5;
    transition: background 0.15s;
}

.autocomplete-item:last-child {
    border-bottom: none;
}

.autocomplete-item:hover {
    background: #f5f5ff;
    color: #667eea;
}

/* Candidate Panel */
.candidate-panel {
    background: white;
    border-radius: 16px;
    border: 1.5px solid #e5e5ea;
    margin-bottom: 24px;
    overflow: hidden;
}

.candidate-heading {
    font-size: 0.85rem;
    font-weight: 600;
    color: #6e6e73;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding: 14px 18px 10px;
    border-bottom: 1px solid #f0f0f5;
}

.candidate-list {
    list-style: none;
}

.candidate-item {
    padding: 14px 18px;
    cursor: pointer;
    border-bottom: 1px solid #f5f5f7;
    transition: background 0.15s;
    display: flex;
    align-items: baseline;
    gap: 8px;
}

.candidate-item:last-child {
    border-bottom: none;
}

.candidate-item:hover {
    background: #f5f5ff;
}

.candidate-title {
    font-size: 1rem;
    font-weight: 600;
    color: #1d1d1f;
}

.candidate-artist {
    font-size: 0.88rem;
    color: #6e6e73;
}
```

**Step 2: 서버 실행 후 시각 확인 (선택)**

```bash
python3 app.py
# http://localhost:5001 접속하여 입력창 레이아웃 확인
```

**Step 3: 커밋**

```bash
git add static/css/style.css
git commit -m "style: 자동완성 드롭다운 + 후보 패널 CSS 추가"
```

---

### Task 4: autocomplete.js 신규 생성

**Files:**
- Create: `static/js/autocomplete.js`

**Step 1: autocomplete.js 생성**

`static/js/autocomplete.js`:

```javascript
// Shared cache: last /api/search result
var _acCache = { key: null, results: [] };

async function apiFetchCandidates(artist, title) {
    var key = artist + '||' + title;
    if (_acCache.key === key) return _acCache.results;
    try {
        var resp = await fetch('/api/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ artist: artist, title: title })
        });
        if (!resp.ok) { _acCache = { key: key, results: [] }; return []; }
        var data = await resp.json();
        _acCache = { key: key, results: data.results || [] };
        return _acCache.results;
    } catch (e) {
        return [];
    }
}

function getAutocompleteCache() { return _acCache; }

function setupAutocomplete(config) {
    // config: { inputEl, listEl, getArtist, getTitle, onSelect }
    var timer = null;

    config.inputEl.addEventListener('input', function () {
        clearTimeout(timer);
        var val = config.inputEl.value.trim();
        if (val.length < 3) {
            config.listEl.classList.add('hidden');
            return;
        }
        timer = setTimeout(async function () {
            var candidates = await apiFetchCandidates(
                config.getArtist(),
                config.getTitle()
            );
            renderAutocompleteItems(config.listEl, candidates, config.onSelect);
        }, 300);
    });

    config.inputEl.addEventListener('blur', function () {
        setTimeout(function () { config.listEl.classList.add('hidden'); }, 150);
    });
}

function renderAutocompleteItems(listEl, candidates, onSelect) {
    listEl.innerHTML = '';
    if (!candidates.length) {
        listEl.classList.add('hidden');
        return;
    }
    candidates.slice(0, 5).forEach(function (item) {
        var li = document.createElement('li');
        li.className = 'autocomplete-item';
        li.textContent = item.title + ' \u2014 ' + item.artist;
        li.addEventListener('mousedown', function (e) {
            e.preventDefault();
            listEl.classList.add('hidden');
            onSelect(item.artist, item.title);
        });
        listEl.appendChild(li);
    });
    listEl.classList.remove('hidden');
}
```

**Step 2: 커밋**

```bash
git add static/js/autocomplete.js
git commit -m "feat: autocomplete.js - 드롭다운 자동완성 모듈"
```

---

### Task 5: index.html + app.js 수정

**Files:**
- Modify: `static/index.html`
- Modify: `static/js/app.js`

**Step 1: index.html 수정**

기존 `<form>` 내용 교체:

```html
<form id="searchForm" class="search-form">
    <div class="input-wrapper">
        <input
            type="text"
            id="artistInput"
            class="input"
            placeholder="아티스트 (선택)"
            autocomplete="off"
        >
        <ul id="artistAutocomplete" class="autocomplete-list hidden"></ul>
    </div>
    <div class="input-wrapper">
        <input
            type="text"
            id="titleInput"
            class="input"
            placeholder="노래 제목 (선택)"
            autocomplete="off"
        >
        <ul id="titleAutocomplete" class="autocomplete-list hidden"></ul>
    </div>
    <button type="submit" class="btn-search">검색</button>
</form>
```

`<div id="status" ...>` 앞에 후보 패널 추가:

```html
<section id="candidatePanel" class="candidate-panel hidden">
    <h3 class="candidate-heading">검색 결과를 선택해주세요</h3>
    <ul id="candidateList" class="candidate-list"></ul>
</section>
```

`</body>` 직전 스크립트 태그:

```html
<script src="/static/js/autocomplete.js"></script>
<script src="/static/js/app.js"></script>
```

**Step 2: app.js 전체 교체**

```javascript
// DOM references
var searchForm = document.getElementById('searchForm');
var artistInput = document.getElementById('artistInput');
var titleInput = document.getElementById('titleInput');
var artistAutocomplete = document.getElementById('artistAutocomplete');
var titleAutocomplete = document.getElementById('titleAutocomplete');
var candidatePanel = document.getElementById('candidatePanel');
var candidateList = document.getElementById('candidateList');
var statusEl = document.getElementById('status');
var resultsEl = document.getElementById('results');
var songTitleEl = document.getElementById('songTitle');
var songArtistEl = document.getElementById('songArtist');
var lyricsContainer = document.getElementById('lyricsContainer');

// Status helpers
function showStatus(msg, type) {
    statusEl.textContent = msg;
    statusEl.className = 'status ' + (type || 'loading');
    statusEl.classList.remove('hidden');
    resultsEl.classList.add('hidden');
    candidatePanel.classList.add('hidden');
}

function hideStatus() {
    statusEl.classList.add('hidden');
}

// Render lyrics lines into DOM
function renderLyrics(lines) {
    lyricsContainer.innerHTML = '';
    lines.forEach(function (line) {
        var original = line.original;
        var pronunciation = line.pronunciation;
        if (!original.trim()) {
            var br = document.createElement('div');
            br.className = 'lyric-break';
            lyricsContainer.appendChild(br);
            return;
        }
        var pair = document.createElement('div');
        pair.className = 'lyric-pair';

        var orig = document.createElement('p');
        orig.className = 'original';
        orig.textContent = original;

        var pron = document.createElement('p');
        pron.className = 'pronunciation';
        pron.textContent = pronunciation;

        pair.appendChild(orig);
        pair.appendChild(pron);
        lyricsContainer.appendChild(pair);
    });
}

// Render candidate selection panel
function renderCandidatePanel(candidates) {
    candidateList.innerHTML = '';
    candidates.forEach(function (item) {
        var li = document.createElement('li');
        li.className = 'candidate-item';

        var titleSpan = document.createElement('span');
        titleSpan.className = 'candidate-title';
        titleSpan.textContent = item.title;

        var artistSpan = document.createElement('span');
        artistSpan.className = 'candidate-artist';
        artistSpan.textContent = '\u2014 ' + item.artist;

        li.appendChild(titleSpan);
        li.appendChild(artistSpan);
        li.addEventListener('click', function () {
            candidatePanel.classList.add('hidden');
            artistInput.value = item.artist;
            titleInput.value = item.title;
            searchLyrics(item.artist, item.title);
        });
        candidateList.appendChild(li);
    });
    hideStatus();
    candidatePanel.classList.remove('hidden');
    candidatePanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Fetch lyrics + pronunciation and render
async function searchLyrics(artist, title) {
    showStatus('가사를 검색하는 중...', 'loading');

    var lyricsResp;
    try {
        lyricsResp = await fetch('/api/lyrics', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ artist: artist, title: title })
        });
    } catch (e) {
        showStatus('네트워크 오류가 발생했습니다.', 'error');
        return;
    }

    if (lyricsResp.status === 404) {
        showStatus('가사를 찾을 수 없습니다. 다른 곡을 선택해주세요.', 'error');
        return;
    }
    if (!lyricsResp.ok) {
        showStatus('가사 검색 중 오류가 발생했습니다.', 'error');
        return;
    }

    var lyricsData = await lyricsResp.json();

    showStatus('발음을 변환하는 중...', 'loading');

    var pronResp;
    try {
        pronResp = await fetch('/api/pronunciation', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ lyrics: lyricsData.lyrics })
        });
    } catch (e) {
        showStatus('발음 변환 중 오류가 발생했습니다.', 'error');
        return;
    }

    if (!pronResp.ok) {
        showStatus('발음 변환 중 오류가 발생했습니다.', 'error');
        return;
    }

    var pronData = await pronResp.json();

    hideStatus();
    songTitleEl.textContent = title || artist;
    songArtistEl.textContent = title ? artist : '';
    renderLyrics(pronData.lines);
    resultsEl.classList.remove('hidden');
    resultsEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Autocomplete setup
setupAutocomplete({
    inputEl: artistInput,
    listEl: artistAutocomplete,
    getArtist: function () { return artistInput.value.trim(); },
    getTitle: function () { return titleInput.value.trim(); },
    onSelect: function (artist, title) {
        artistInput.value = artist;
        titleInput.value = title;
        artistAutocomplete.classList.add('hidden');
        titleAutocomplete.classList.add('hidden');
        searchLyrics(artist, title);
    }
});

setupAutocomplete({
    inputEl: titleInput,
    listEl: titleAutocomplete,
    getArtist: function () { return artistInput.value.trim(); },
    getTitle: function () { return titleInput.value.trim(); },
    onSelect: function (artist, title) {
        artistInput.value = artist;
        titleInput.value = title;
        artistAutocomplete.classList.add('hidden');
        titleAutocomplete.classList.add('hidden');
        searchLyrics(artist, title);
    }
});

// Form submit: always show candidate list first
searchForm.addEventListener('submit', async function (e) {
    e.preventDefault();
    var artist = artistInput.value.trim();
    var title = titleInput.value.trim();

    if (!artist && !title) {
        showStatus('아티스트 또는 곡명을 입력해주세요.', 'error');
        return;
    }

    // Reuse autocomplete cache if same query
    var cache = getAutocompleteCache();
    var cacheKey = artist + '||' + title;
    var candidates;

    if (cache.key === cacheKey && cache.results.length > 0) {
        candidates = cache.results;
    } else {
        showStatus('검색 중...', 'loading');
        candidates = await apiFetchCandidates(artist, title);
        hideStatus();
    }

    if (!candidates.length) {
        showStatus('검색 결과가 없습니다. 아티스트명 또는 제목을 확인해주세요.', 'error');
        return;
    }

    renderCandidatePanel(candidates);
});
```

**Step 3: 수동 동작 확인**

```bash
python3 app.py
# http://localhost:5001 접속
```

체크리스트:
- [ ] 아티스트 입력란에 3글자 입력 → 300ms 후 드롭다운 표시
- [ ] 드롭다운 항목 클릭 → 두 필드 채워지고 바로 가사 표시
- [ ] 검색 버튼 → 후보 패널 표시
- [ ] 후보 패널 항목 클릭 → 가사 표시
- [ ] 빈 입력 → "아티스트 또는 곡명을 입력해주세요." 표시
- [ ] 입력 필드 외 클릭 → 드롭다운 닫힘

**Step 4: 커밋**

```bash
git add static/index.html static/js/app.js
git commit -m "feat: 자동완성 드롭다운 + 검색 결과 후보 패널 UI 완성"
```

---

### Task 6: 전체 테스트 최종 확인

**Step 1: 전체 테스트 실행**

```bash
cd /Users/work6/Desktop/ai-code/song-pronunciation-kor
python3 -m pytest tests/ -v
```

예상: 40 passed (기존 35 + 신규 5)

**Step 2: 실패 시 개별 확인**

```bash
python3 -m pytest tests/test_search.py -v    # 신규 모듈
python3 -m pytest tests/test_app.py -v       # /api/search 엔드포인트
```

**Step 3: 최종 커밋 (필요 시)**

```bash
git add -A
git commit -m "test: 전체 테스트 40 passed 확인"
```
