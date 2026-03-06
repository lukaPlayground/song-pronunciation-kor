# Song Pronunciation - 자동완성 + 검색 결과 목록 설계서

**날짜**: 2026-03-06
**버전**: 1.0

---

## 목표

- 자동완성: 타이핑 중 곡 제안 드롭다운 (3글자+, 300ms debounce)
- 검색 결과 목록: 검색 버튼 클릭 시 항상 후보 목록 먼저 표시 후 선택
- API 호출 최소화: 자동완성과 결과 목록이 동일한 `/api/search` 공유 + 캐시

---

## 백엔드

### 새 엔드포인트

| 메서드 | 경로 | 입력 | 출력 |
|--------|------|------|------|
| POST | `/api/search` | `{artist, title}` | `{results: [{artist, title}]}` |

- `artist`, `title` 둘 중 하나만 있어도 동작 (둘 다 없으면 400)
- lrclib `/api/search?artist_name=&track_name=` 호출
- `artistName`, `trackName` 파싱하여 최대 10개 반환
- 결과 없으면 `{results: []}` 반환 (404 아님)

### 기존 엔드포인트 유지

- `POST /api/lyrics` — 그대로 유지 (artist + title 확정 후 가사 페치)
- `POST /api/pronunciation` — 그대로 유지

### 새 모듈: `search.py`

```python
def search_candidates(artist: str, title: str) -> list[dict]:
    """lrclib 검색으로 후보 목록 반환. [{artist, title}, ...]"""
```

---

## 프론트엔드

### 사용자 흐름

```
[아티스트 (선택)] [노래 제목 (선택)] [검색]

경로 A - 자동완성:
  타이핑 3글자+ (300ms debounce)
  → POST /api/search
  → 드롭다운: "Yellow — Coldplay"
  → 클릭 → 바로 POST /api/lyrics → 가사

경로 B - 검색 버튼:
  검색 버튼 클릭
  → POST /api/search (캐시 없으면 신규 호출, 있으면 재사용)
  → 결과 패널:
       1. Yellow — Coldplay
       2. Yellow — Chris Martin
  → 항목 클릭 → POST /api/lyrics → 가사
```

### API 호출 최소화

- 마지막 `/api/search` 결과를 `{ key: 'artist|title', results }` 형태로 메모리 캐시
- 검색 버튼 클릭 시 입력값이 자동완성 마지막 쿼리와 같으면 캐시 재사용

### 새 DOM 요소

```html
<!-- 자동완성 드롭다운 (각 입력 필드 아래) -->
<ul id="autocompleteList" class="autocomplete-list hidden"></ul>

<!-- 검색 결과 패널 (검색 버튼 클릭 후) -->
<section id="candidatePanel" class="candidate-panel hidden">
  <h3>검색 결과</h3>
  <ul id="candidateList"></ul>
</section>
```

### JS 모듈 구조

- `autocomplete.js` (신규): debounce, `/api/search` 호출, 드롭다운 렌더
- `app.js` (수정): form submit → `/api/search` → 결과 패널, 항목 클릭 → `search(artist, title)`

### CSS 추가

- `.autocomplete-list`: absolute position, input 아래 붙음, z-index 높게
- `.autocomplete-item`: hover 강조
- `.candidate-panel`: 검색폼 아래 카드 스타일
- `.candidate-item`: 클릭 가능한 리스트 항목, hover 강조

---

## 테스트 계획

### 백엔드 (tests/test_search.py 신규)
- `search_candidates` 성공 케이스 (결과 있음)
- `search_candidates` 빈 결과
- `search_candidates` 네트워크 오류 → `[]` 반환
- `POST /api/search` 200 응답
- `POST /api/search` 둘 다 없으면 400

### 프론트엔드 (수동)
- 3글자 미만 입력 시 드롭다운 미표시
- 3글자 이상 입력 후 300ms → 드롭다운 표시
- 드롭다운 항목 클릭 → 가사 바로 표시
- 검색 버튼 → 결과 패널 표시
- 결과 패널 항목 클릭 → 가사 표시
- 결과 없음 → "검색 결과 없음" 메시지
- 외부 클릭 시 드롭다운 닫힘

---

## 파일 변경 범위

| 파일 | 변경 |
|------|------|
| `search.py` | 신규 |
| `app.py` | `/api/search` 엔드포인트 추가 |
| `tests/test_search.py` | 신규 |
| `tests/test_app.py` | `/api/search` 테스트 추가 |
| `static/js/autocomplete.js` | 신규 |
| `static/js/app.js` | form submit 흐름 변경 |
| `static/index.html` | DOM 요소 추가, script 태그 추가 |
| `static/css/style.css` | autocomplete, candidate-panel 스타일 추가 |
