# Song Pronunciation KOR

영어 노래 가사를 한글 발음으로 변환해 따라 부를 수 있도록 도와주는 웹 앱.

## 주요 기능

- **통합 검색**: 아티스트명 또는 노래 제목 하나로 자동완성 검색
- **발음 변환**: ARPAbet 기반 음절 합성으로 자연스러운 한글 발음 생성
- **한글 가사 지원**: 한글이 포함된 가사는 변환 없이 원문 그대로 표시
- **국가별 차트**: iTunes RSS 기반 핫 차트에서 바로 선택 검색

## 기술 스택

| 영역 | 기술 |
|------|------|
| 백엔드 | Python 3, Flask, Flask-CORS |
| 발음 엔진 | g2p_en (ARPAbet), 한글 음절 합성 |
| 가사 소스 | lrclib.net API |
| 차트 소스 | iTunes RSS Feed |
| 프론트엔드 | Vanilla JS, HTML5, CSS3 |
| 테스트 | pytest |

## 프로젝트 구조

```
song-pronunciation-kor/
├── app.py                  # Flask 앱 (API 라우팅)
├── lyrics.py               # 가사 검색 (lrclib)
├── pronunciation.py        # ARPAbet → 한글 발음 변환
├── search.py               # 검색 후보 조회 + 중복 제거
├── requirements.txt
├── static/
│   ├── index.html
│   ├── css/style.css
│   └── js/
│       ├── app.js          # 메인 앱 로직
│       └── autocomplete.js # 자동완성
└── tests/
    ├── test_app.py
    ├── test_lyrics.py
    ├── test_pronunciation.py
    └── test_search.py
```

## 설치 및 실행

```bash
pip install -r requirements.txt
python3 app.py
# → http://localhost:5001
```

## API

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | `/api/search` | 검색 후보 반환 `{query}` |
| POST | `/api/lyrics` | 가사 조회 `{artist, title}` |
| POST | `/api/pronunciation` | 발음 변환 `{lyrics}` |
| GET  | `/api/charts?country=kr` | 국가별 차트 조회 |

## 발음 변환 원리

g2p_en으로 영어 단어를 ARPAbet 음소로 변환한 뒤, 자체 음절 합성 알고리즘으로 한글 음절을 조합한다.

```
"love"  → ['L', 'AH1', 'V'] → 러브
"night" → ['N', 'AY1', 'T'] → 나이트
"ring"  → ['R', 'IH1', 'NG'] → 링
```

한글이 포함된 단어/라인은 g2p를 거치지 않고 원문을 그대로 반환한다.

## 라이선스

MIT
