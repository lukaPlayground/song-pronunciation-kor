# Song Pronunciation - 프로젝트 문서

## 프로젝트 개요

영어 노래 가사를 한글 발음 기호로 변환하여 한국 사용자들이 쉽게 따라 부를 수 있도록 돕는 웹 애플리케이션입니다.

### 핵심 목표
- 영어 노래 가사를 정확한 한글 발음으로 변환
- 빠르고 정확한 발음 제공을 위한 5단계 폴백 시스템
- 무료 API 활용으로 비용 최소화
- 향후 PWA로 확장 가능한 구조

## 기술 스택

### 프론트엔드
- **HTML5** - 시맨틱 마크업
- **CSS3** - 그라데이션 디자인 (보라색/파란색 테마)
- **Vanilla JavaScript (ES6+)** - 프레임워크 없이 순수 JS
- **Fetch API** - 비동기 통신
- **LocalStorage** - 클라이언트 사이드 캐싱

### 백엔드
- **Python 3.7+** - 발음 변환 서버
- **Flask** - 경량 웹 프레임워크
- **Flask-CORS** - CORS 지원

### 외부 API
- **Lyrics.ovh API** - 무료 가사 검색 API
- **Dictionary API** - 무료 IPA 발음 API (api.dictionaryapi.dev)
- **Python Transliteration Server** - 커스텀 발음 변환 (포트 5001)

## 5단계 하이브리드 발음 변환 시스템

정확도와 성능을 모두 고려한 폴백 시스템:

### 1단계: 단어 사전 (최우선)
- **파일**: `js/converter.js` - `commonWords` 객체
- **단어 수**: 1000개 이상
- **포함 내용**:
  - 대명사, 동사, 형용사, 명사, 부사, 전치사, 접속사
  - 노래에 자주 나오는 단어들 (baby, love, heart 등)
- **응답 속도**: ~1ms (즉시)
- **장점**: 가장 빠르고 정확

### 2단계: LocalStorage 캐시
- **저장 위치**: 브라우저 LocalStorage
- **키 형식**: `pronunciation_{단어}`
- **값**: 한글 발음 문자열
- **응답 속도**: ~1ms
- **장점**: 이전에 조회한 단어는 재요청 불필요

### 3단계: Python API (핵심)
- **파일**: `python/transliterate_server.py`
- **포트**: 5001
- **엔드포인트**:
  - POST `/transliterate` - 단일 텍스트 변환
  - POST `/batch` - 배치 변환
  - GET `/health` - 서버 상태 확인
- **변환 방식**:
  - 1000+ 단어 Python 사전
  - 규칙 기반 접미사 처리 (-tion, -able, -ful 등)
  - 이중 모음/자음 조합 패턴
  - 기본 자음/모음 매핑
- **응답 속도**: ~10-50ms
- **장점**: 높은 정확도, 로컬 서버라 빠름

### 4단계: Dictionary API + IPA 변환
- **API**: https://api.dictionaryapi.dev/api/v2/entries/en/{word}
- **변환 과정**:
  1. Dictionary API에서 IPA 발음 기호 조회
  2. IPA → 한글 변환 (60+ 매핑 규칙)
  3. LocalStorage에 캐싱
- **IPA 매핑 예시**:
  - `/iː/` → `이`
  - `/eɪ/` → `에이`
  - `/θ/` → `쓰`
  - `/ʃ/` → `쉬`
- **응답 속도**: ~100-500ms (외부 API)
- **장점**: 사전에 없는 단어도 처리 가능

### 5단계: JavaScript 규칙 기반 폴백
- **파일**: `js/converter.js` - `convertByRules()` 함수
- **처리 내용**:
  - 접미사 규칙 (정규표현식)
  - 이중 모음 패턴
  - 자음 조합 패턴
  - 기본 자음/모음 매핑
- **응답 속도**: ~5ms
- **장점**: 모든 상황에서 결과 보장 (최후의 수단)

## 프로젝트 구조

```
song-pronunciation-kor/
├── index.html              # 검색 페이지 (아티스트/제목 입력)
├── lyrics.html             # 가사 표시 페이지 (원문 + 발음)
├── test-5tier.html         # 5단계 시스템 테스트 페이지
│
├── css/
│   └── style.css           # 통합 스타일시트 (그라데이션 디자인)
│
├── js/
│   ├── search.js           # Lyrics.ovh API 호출 및 검색 로직
│   ├── converter.js        # 5단계 발음 변환 엔진 (핵심)
│   └── app.js              # 가사 페이지 로직 (비동기 처리)
│
├── python/
│   ├── transliterate_server.py   # Flask API 서버
│   ├── requirements.txt          # Python 의존성
│   └── transliteration/          # muik/transliteration (참고용)
│
├── .gitignore              # Git 제외 파일
├── README.md               # 사용자용 가이드
├── CLAUDE.MD               # 이 파일 (개발자용 프로젝트 문서)
└── IMPLEMENTATION.md       # 구현 상세 내역
```

## 핵심 구현 사항

### 1. 가사 검색 (index.html + search.js)

**UI 구성:**
- 아티스트 입력 필드
- 제목 입력 필드
- 검색 버튼
- 검색 결과 목록 (동적 생성)

**검색 흐름:**
```javascript
사용자 입력
→ Lyrics.ovh API 호출 (/v1/{artist}/{title})
→ 가사 데이터 수신
→ lyrics.html로 이동 (URLSearchParams로 데이터 전달)
```

**API 형식:**
```
GET https://api.lyrics.ovh/v1/{artist}/{title}

응답:
{
  "lyrics": "가사 텍스트...",
  "error": "에러 메시지" (실패 시)
}
```

### 2. 가사 표시 (lyrics.html + app.js)

**표시 방식:**
```
원문 라인
발음 라인
(빈 줄)
원문 라인
발음 라인
...
```

**토글 버튼:**
- "한글 발음 보기" → 원문 + 발음 번갈아 표시
- "원문만 보기" → 원문만 표시

**비동기 처리:**
```javascript
async function displayLyricsWithPronunciation(lyrics) {
    const lines = lyrics.split('\n');

    // 모든 라인을 병렬로 변환 (성능 최적화)
    const pronunciations = await Promise.all(
        lines.map(line => line.trim() ? convertLineAsync(line) : Promise.resolve(''))
    );

    // HTML 생성 및 렌더링
    lines.forEach((line, index) => {
        // 원문 + 발음 교대로 표시
    });
}
```

### 3. 발음 변환 엔진 (converter.js)

**주요 함수:**

```javascript
// 비동기 단어 변환 (5단계 폴백)
async function convertWordAsync(word) {
    // 1. 사전 조회
    if (commonWords[lowerWord]) return commonWords[lowerWord];

    // 2. 캐시 조회
    const cached = apiCache.get(lowerWord);
    if (cached) return cached;

    // 3. Python API
    const pythonResult = await fetchPronunciationFromPython(lowerWord);
    if (pythonResult) {
        apiCache.set(lowerWord, pythonResult);
        return pythonResult;
    }

    // 4. Dictionary API
    const apiResult = await fetchPronunciationFromAPI(lowerWord);
    if (apiResult) {
        apiCache.set(lowerWord, apiResult);
        return apiResult;
    }

    // 5. 규칙 기반 폴백
    return convertByRules(lowerWord);
}

// 라인 변환 (단어별로 처리)
async function convertLineAsync(line) {
    const words = line.split(' ');
    const convertedWords = await Promise.all(
        words.map(word => convertWordAsync(word))
    );
    return convertedWords.join(' ');
}
```

**캐싱 시스템:**
```javascript
const apiCache = {
    get: (word) => {
        const cached = localStorage.getItem(`pronunciation_${word}`);
        return cached ? JSON.parse(cached) : null;
    },
    set: (word, pronunciation) => {
        localStorage.setItem(`pronunciation_${word}`, JSON.stringify(pronunciation));
    }
};
```

### 4. Python 발음 변환 서버 (transliterate_server.py)

**실행:**
```bash
cd python
python3 transliterate_server.py
# 포트 5001에서 실행됨
```

**주요 엔드포인트:**

```python
@app.route('/health', methods=['GET'])
def health():
    # 서버 상태 확인
    return jsonify({'status': 'ok'})

@app.route('/transliterate', methods=['POST'])
def transliterate():
    # 입력: {"text": "hello", "word_mode": true}
    # 출력: {"transliteration": "헬로", "success": true}
    text = request.json['text']
    result = transliterate_text(text)
    return jsonify({'transliteration': result, 'success': True})

@app.route('/batch', methods=['POST'])
def batch_transliterate():
    # 입력: {"words": ["hello", "world"]}
    # 출력: {"results": {"hello": "헬로", "world": "월드"}}
    words = request.json['words']
    results = {word: transliterate_word(word) for word in words}
    return jsonify({'results': results, 'success': True})
```

**변환 로직:**
```python
def transliterate_word(word):
    lower_word = word.lower()

    # 1. 사전 조회
    if lower_word in PRONUNCIATION_DICT:
        return PRONUNCIATION_DICT[lower_word]

    # 2. 규칙 기반 변환
    return convert_by_rules(lower_word)

def convert_by_rules(word):
    # 접미사 규칙 적용
    for pattern, replacement in PRONUNCIATION_RULES.items():
        word = re.sub(pattern, replacement, word)

    # 자음/모음 매핑
    # ...

    return korean_result
```

## 개발 가이드라인

### 코드 스타일

**JavaScript:**
- ES6+ 문법 사용 (async/await, const/let)
- 함수명: camelCase
- 명확한 함수 이름 (convertWordAsync, fetchPronunciationFromPython 등)

**Python:**
- PEP 8 준수
- 함수명: snake_case
- Type hints 선택적 사용

**CSS:**
- BEM 방식 클래스명 지양 (간단한 프로젝트)
- 명확한 클래스명 (.lyrics-line, .pronunciation-line 등)

### 에러 처리

**JavaScript:**
```javascript
try {
    const response = await fetch(url);
    if (!response.ok) return null;
    // ...
} catch (error) {
    console.warn('API 호출 실패:', error);
    return null; // 조용히 실패 (폴백 시스템으로 처리)
}
```

**Python:**
```python
try:
    # API 호출 또는 변환
    result = process()
    return jsonify({'success': True, 'data': result})
except Exception as e:
    return jsonify({'success': False, 'error': str(e)}), 500
```

### 성능 최적화

1. **병렬 처리**
```javascript
// 좋음: 모든 라인을 동시에 변환
const results = await Promise.all(lines.map(convertLineAsync));

// 나쁨: 순차 처리
for (const line of lines) {
    const result = await convertLineAsync(line);
}
```

2. **캐싱**
- 모든 API 결과는 LocalStorage에 캐싱
- 캐시 키: `pronunciation_{단어}`
- 만료 시간 없음 (영구 저장)

3. **사전 우선**
- 가능한 많은 단어를 사전에 추가
- API 호출 최소화

## 디버깅 및 테스트

### 로컬 테스트

```bash
# 터미널 1: Python 서버
cd python
python3 transliterate_server.py

# 터미널 2: 웹 서버
python3 -m http.server 8000

# 브라우저
http://localhost:8000/test-5tier.html
```

### 테스트 시나리오

**test-5tier.html에서:**
1. 사전 기반 테스트 (Tell me why it's so uncomfortable)
2. Python API 테스트 (serendipity magnificent)
3. 전체 가사 테스트 (실제 노래 가사)
4. 캐싱 성능 테스트 (속도 비교)

### 디버깅 팁

**Python 서버 확인:**
```bash
curl http://localhost:5001/health
# {"status": "ok", "message": "..."}

curl -X POST http://localhost:5001/transliterate \
  -H "Content-Type: application/json" \
  -d '{"text": "hello", "word_mode": true}'
```

**JavaScript 콘솔:**
```javascript
// 캐시 확인
localStorage.getItem('pronunciation_hello')

// 함수 직접 호출
await convertWordAsync('hello')

// 캐시 초기화
localStorage.clear()
```

## 향후 개발 계획

### Phase 1: 기능 개선
- [ ] 발음 정확도 향상 (사전 단어 추가)
- [ ] 사용자 피드백 기능 (발음 수정 제안)
- [ ] 북마크/즐겨찾기 기능
- [ ] 최근 검색 기록

### Phase 2: PWA 변환
- [ ] Service Worker 추가
- [ ] 오프라인 지원
- [ ] 앱 설치 기능
- [ ] 푸시 알림

### Phase 3: 고급 기능
- [ ] TTS (발음 듣기)
- [ ] 발음 연습 모드
- [ ] 난이도별 가사 추천
- [ ] 다국어 지원 (일본어, 중국어)

### Phase 4: 백엔드 확장
- [ ] 사용자 계정 시스템
- [ ] 데이터베이스 (발음 캐시 공유)
- [ ] 관리자 페이지 (사전 관리)
- [ ] 통계 대시보드

## 배포

### 프론트엔드 (GitHub Pages)
```bash
# Settings → Pages → Source: main branch
# 정적 사이트로 자동 배포
# URL: https://gaengdoo.github.io/song-pronunciation-kor/
```

**제한사항:** Python 서버는 GitHub Pages에서 실행 불가 (정적 호스팅)

### Python 서버 (별도 호스팅 필요)
**옵션:**
- Heroku (무료 티어)
- PythonAnywhere
- AWS EC2 (프리티어)
- Google Cloud Run
- Vercel (serverless functions)

**배포 시 수정 사항:**
```javascript
// js/converter.js
// localhost를 실제 서버 URL로 변경
const PYTHON_API_URL = 'https://your-server.com';

async function fetchPronunciationFromPython(word) {
    const response = await fetch(`${PYTHON_API_URL}/transliterate`, {
        // ...
    });
}
```

## 문제 해결

### 자주 발생하는 문제

**1. Python 서버가 시작되지 않음**
```bash
# 포트 5000/5001 충돌 확인
lsof -i :5001

# 의존성 재설치
pip install --upgrade -r python/requirements.txt
```

**2. CORS 오류**
```python
# transliterate_server.py에 CORS 설정 확인
from flask_cors import CORS
CORS(app)
```

**3. 가사를 찾을 수 없음**
- Lyrics.ovh API는 모든 노래를 커버하지 않음
- 아티스트명/제목을 정확히 입력 (영어)
- 대안: Genius API, Musixmatch API 고려

**4. 발음이 부정확함**
- Python 사전에 단어 추가
- IPA 매핑 규칙 개선
- 사용자 피드백 시스템 구축 고려

## 기여 가이드

### 새 단어 추가

**JavaScript 사전:**
```javascript
// js/converter.js - commonWords 객체에 추가
const commonWords = {
    // ...
    'newword': '뉴워드',
};
```

**Python 사전:**
```python
# python/transliterate_server.py - PRONUNCIATION_DICT에 추가
PRONUNCIATION_DICT = {
    # ...
    'newword': '뉴워드',
}
```

### IPA 매핑 추가

```javascript
// js/converter.js - ipaToKorean 객체
const ipaToKorean = {
    // ...
    'ɹ': '르',  // 새 IPA 심볼
};
```

## 라이선스

MIT License - 자유롭게 사용, 수정, 배포 가능

## 참고 자료

- [Lyrics.ovh API 문서](https://lyricsovh.docs.apiary.io/)
- [Dictionary API 문서](https://dictionaryapi.dev/)
- [IPA 표기법](https://en.wikipedia.org/wiki/International_Phonetic_Alphabet)
- [Flask 문서](https://flask.palletsprojects.com/)
- [muik/transliteration](https://github.com/muik/transliteration)

---

**프로젝트 시작일:** 2026-01-15
**마지막 업데이트:** 2026-01-15
**버전:** 1.0.0
**개발자:** Gaengdoo
**저장소:** https://github.com/Gaengdoo/song-pronunciation-kor
