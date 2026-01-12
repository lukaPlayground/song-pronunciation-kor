# Song Pronunciation - 영어 노래 발음 학습 앱

영어 노래 가사를 한글 발음 기호로 변환하여 쉽게 따라 부를 수 있도록 도와주는 웹 애플리케이션입니다.

## 🎯 주요 기능

- **노래 검색**: 아티스트명과 제목으로 노래 가사 검색
- **한글 발음 변환**: 5단계 폴백 시스템으로 정확한 발음 제공
- **가사 표시**: 원문과 발음을 번갈아 표시하여 가독성 향상
- **오프라인 캐싱**: 한 번 조회한 발음은 캐시에 저장

## 🚀 5단계 폴백 시스템

정확도와 속도를 모두 잡은 하이브리드 발음 변환 시스템:

1. **1단계: 단어 사전** (1000+ 단어)
   - 즉시 응답 (0-1ms)
   - 일반적인 영어 단어 커버

2. **2단계: LocalStorage 캐시**
   - 이전에 조회한 단어는 캐시에서 즉시 반환
   - 속도: ~1ms

3. **3단계: Python API** ⭐ **NEW**
   - Flask 기반 발음 변환 서버
   - 규칙 기반 고급 변환
   - 속도: ~10-50ms

4. **4단계: Dictionary API + IPA**
   - 외부 무료 API 활용
   - IPA(국제음성기호) → 한글 자동 변환
   - 속도: ~100-500ms

5. **5단계: JavaScript 규칙 기반**
   - 최후의 폴백
   - 기본 발음 규칙 적용

## 📦 설치 및 실행

### 필수 요구사항

- Python 3.7 이상
- 웹 브라우저 (Chrome, Firefox, Safari 등)

### 1. Python 서버 실행

```bash
# 의존성 설치
cd python
pip install -r requirements.txt

# 서버 시작 (포트 5001)
python3 transliterate_server.py
```

### 2. 웹 서버 실행

```bash
# 프로젝트 루트에서
python3 -m http.server 8000
```

### 3. 브라우저에서 접속

- **메인 앱**: http://localhost:8000/index.html
- **5단계 시스템 테스트**: http://localhost:8000/test-5tier.html

## 🛠 기술 스택

### 프론트엔드
- HTML5 / CSS3
- Vanilla JavaScript (ES6+)
- Fetch API (비동기 통신)

### 백엔드
- Python 3 + Flask
- Flask-CORS (CORS 지원)

### API
- Lyrics.ovh API (가사 검색)
- Dictionary API (IPA 발음)
- Python Transliteration Server (커스텀)

## 📁 프로젝트 구조

```
song-pronunciation-kor/
├── index.html              # 메인 검색 페이지
├── lyrics.html             # 가사 표시 페이지
├── test-5tier.html         # 5단계 시스템 테스트 페이지
├── css/
│   └── style.css           # 스타일시트
├── js/
│   ├── search.js           # 가사 검색 로직
│   ├── converter.js        # 발음 변환 엔진 (5단계 폴백)
│   └── app.js              # 가사 페이지 로직
├── python/
│   ├── transliterate_server.py   # Flask API 서버
│   ├── requirements.txt          # Python 의존성
│   └── transliteration/          # muik/transliteration (참고)
├── CLAUDE.MD               # 프로젝트 문서
├── IMPLEMENTATION.md       # 구현 상세 내역
└── README.md               # 이 파일
```

## 🎨 사용 예시

### 노래 검색

```
아티스트: Coldplay
제목: Viva La Vida
```

### 발음 변환 결과

```
원문:  I used to rule the world
발음:  아이 유즈드 투 룰 더 월드

원문:  Seas would rise when I gave the word
발음:  씨즈 우드 라이즈 웬 아이 게이브 더 워드
```

## ⚙️ Python API 엔드포인트

### POST /transliterate
단일 텍스트 변환

```bash
curl -X POST http://localhost:5001/transliterate \
  -H "Content-Type: application/json" \
  -d '{"text": "hello world", "word_mode": true}'
```

**응답:**
```json
{
  "original": "hello world",
  "transliteration": "헬로 월드",
  "success": true
}
```

### POST /batch
여러 단어 일괄 변환

```bash
curl -X POST http://localhost:5001/batch \
  -H "Content-Type: application/json" \
  -d '{"words": ["hello", "world", "beautiful"]}'
```

### GET /health
서버 상태 확인

```bash
curl http://localhost:5001/health
```

## 🔧 성능 최적화

### 캐싱 전략
- LocalStorage 활용
- 단어별 개별 캐싱
- 영구 저장 (브라우저 캐시 삭제 전까지)

### 병렬 처리
```javascript
const pronunciations = await Promise.all(
    lines.map(line => convertLineAsync(line))
);
```

### 속도 비교

| 방법 | 첫 번째 조회 | 캐시 조회 | 배속 |
|------|-------------|-----------|------|
| Python API | ~30ms | ~1ms | 30배 |
| Dictionary API | ~200ms | ~1ms | 200배 |
| 규칙 기반 | ~5ms | ~1ms | 5배 |

## 🐛 문제 해결

### Python 서버가 시작되지 않을 때

```bash
# 포트 5000이 사용 중인 경우 (macOS AirPlay)
# transliterate_server.py의 포트를 5001로 변경 (이미 적용됨)

# 의존성 재설치
pip install --upgrade -r python/requirements.txt
```

### CORS 오류가 발생할 때

```python
# Flask-CORS가 설치되어 있는지 확인
pip install flask-cors

# 서버 재시작
```

### 가사를 찾을 수 없을 때

- 아티스트명과 제목을 정확히 입력
- 영어로 검색 (Lyrics.ovh API는 영어 기준)
- 특수문자나 부제는 제외

## 📝 TODO

- [ ] PWA 변환 (오프라인 지원)
- [ ] 사용자 피드백 기능 (발음 수정)
- [ ] 발음 듣기 기능 (TTS)
- [ ] 즐겨찾기 기능
- [ ] 다국어 지원 (일본어, 중국어)

## 📄 라이선스

MIT License - 자유롭게 사용 가능

## 🙏 감사의 말

- [Lyrics.ovh](https://lyrics.ovh) - 무료 가사 API
- [Dictionary API](https://dictionaryapi.dev) - 무료 IPA 발음 API
- [muik/transliteration](https://github.com/muik/transliteration) - 영한 음역 참고

## 📧 문의

프로젝트에 대한 질문이나 제안사항이 있으시면 이슈를 등록해주세요.

---

**Made with ❤️ for English learners**
