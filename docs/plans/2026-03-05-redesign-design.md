# Song Pronunciation - 리디자인 설계서

**날짜**: 2026-03-05
**버전**: 2.0

---

## 목표

- 발음 변환 품질 향상: 수작업 사전 → g2p-en (ML 기반)
- 가사 API 신뢰성 향상: lrclib + Genius 병행
- UI 개선: 2페이지 → 싱글페이지 통합
- 서버 실행 단순화: `python app.py` 하나로

---

## 파일 구조

```
song-pronunciation-kor/
├── app.py                  # Flask (API + 정적파일 서빙)
├── requirements.txt
├── .env                    # GENIUS_ACCESS_TOKEN (gitignore)
└── static/
    ├── index.html
    ├── css/style.css
    └── js/app.js
```

제거 대상: `python/`, `lyrics.html`, `test-5tier.html`, `test.html`, `js/`, `css/`

---

## 백엔드

### 실행
```bash
python app.py  # localhost:5001
```

### API 엔드포인트

| 메서드 | 경로 | 입력 | 출력 |
|--------|------|------|------|
| GET | `/` | - | static/index.html |
| POST | `/api/lyrics` | `{artist, title}` | `{lyrics, source}` |
| POST | `/api/pronunciation` | `{lyrics}` | `{lines: [{original, pronunciation}]}` |

### 가사 검색 로직
1. lrclib.net API 호출 (`https://lrclib.net/api/search?artist_name=&track_name=`)
2. 결과 없으면 Genius API 폴백 (`Authorization: Bearer <token>`)
3. 응답에 `source: "lrclib"` 또는 `source: "genius"` 포함

### 발음 변환 로직 (g2p-en)
```python
from g2p_en import G2p
g2p = G2p()

# ARPAbet → 한글 매핑 테이블
ARPABET_TO_KOR = {
    'AA': '아', 'AE': '애', 'AH': '어', 'AO': '오', 'AW': '아우',
    'AY': '아이', 'EH': '에', 'ER': '어', 'EY': '에이', 'IH': '이',
    'IY': '이', 'OW': '오', 'OY': '오이', 'UH': '우', 'UW': '우',
    'B': '브', 'CH': '치', 'D': '드', 'DH': '드', 'F': '프',
    'G': '그', 'HH': '흐', 'JH': '즈', 'K': '크', 'L': '르',
    'M': '므', 'N': '느', 'NG': '잉', 'P': '프', 'R': '르',
    'S': '스', 'SH': '쉬', 'T': '트', 'TH': '쓰', 'V': '브',
    'W': '우', 'Y': '이', 'Z': '즈', 'ZH': '즈',
}
```

---

## 프론트엔드

### 싱글페이지 구조
```
헤더 (앱 이름)
검색 영역 (아티스트 + 곡명 + 검색 버튼)
로딩 상태
가사 영역:
  원문:  I used to rule the world
  발음:  아이 유즈드 투 룰 더 월드
  (빈줄)
  원문:  Seas would rise when I gave the word
  발음:  씨즈 우드 라이즈 웬 아이 게이브 더 워드
```

### JS 흐름
1. 검색 → `POST /api/lyrics`
2. 가사 수신 → `POST /api/pronunciation`
3. 응답 파싱 → DOM 렌더링

---

## 자격증명

`.env`:
```
GENIUS_ACCESS_TOKEN=<GENIUS_ACCESS_TOKEN>
```

`.gitignore`에 `.env` 추가.

---

## 향후 계획 (모드 B)

한국어 가사 → 외국어 발음기호 변환 (로마자/카타카나 등) - 별도 업데이트에서 구현.
