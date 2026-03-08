# 음절 합성 방식 발음 변환 설계서

**Date:** 2026-03-09
**Status:** Approved
**Scope:** `pronunciation.py` 단일 파일 교체 (API/테스트 구조 유지)

---

## 문제

현재 `phonemes_to_korean()`은 ARPAbet 음소 하나를 독립 음절 하나로 단순 치환한다.
자음이 항상 `으` 모음을 달고 독립 음절을 형성하므로 받침이 전혀 없고, 읽기 어렵다.

```
"Danger with your love"
현재: 드에이느즈어 우이드 이오르 르어브
목표: 데인져 위드 유어 러브
```

---

## 설계 방향: 음절 합성 (Syllabify)

ARPAbet 음소 배열을 CV 패턴으로 묶어서 초성·중성·종성을 조합한 완전한 한글 음절을 생성한다.

```
(D, EY, N, JH, ER)
  └─ D+EY → 초성ㄷ+중성ㅔ = 데
  └─ EY trailing ㅣ + N(받침) → 중성ㅣ+종성ㄴ = 인
  └─ JH+ER → 초성ㅈ+중성ㅓ = 져
  → 데인져
```

---

## 데이터 테이블 (4개)

### VOWEL_JAMO — 단순 모음

| ARPAbet | 자모 | 예시 |
|---------|------|------|
| AA | ㅏ | father |
| AE | ㅐ | cat |
| AH | ㅓ | but |
| AO | ㅗ | thought |
| EH | ㅔ | bed |
| ER | ㅓ | her |
| EY | ㅔ | day (main vowel, trailing=ㅣ) |
| IH | ㅣ | bit |
| IY | ㅣ | beat |
| OW | ㅗ | go (main vowel, trailing=ㅜ) |
| UH | ㅓ | book |
| UW | ㅜ | food |
| AY | ㅏ | buy (main vowel, trailing=ㅣ) |
| AW | ㅏ | how (main vowel, trailing=ㅜ) |
| OY | ㅗ | boy (main vowel, trailing=ㅣ) |

### CONS_JAMO — 자음 자모

| ARPAbet | 자모 | 비고 |
|---------|------|------|
| B | ㅂ | |
| CH | ㅊ | |
| D | ㄷ | |
| DH | ㄷ | the |
| F | ㅍ | |
| G | ㄱ | |
| HH | ㅎ | |
| JH | ㅈ | |
| K | ㄱ | |
| L | ㄹ | |
| M | ㅁ | |
| N | ㄴ | |
| NG | ㅇ | |
| P | ㅍ | |
| R | ㄹ | |
| S | ㅅ | |
| SH | ㅅ | |
| T | ㅌ | |
| TH | ㅅ | think |
| V | ㅂ | |
| W | ㅜ | 복합모음 처리 별도 |
| Y | ㅣ | 복합모음 처리 별도 |
| Z | ㅈ | |
| ZH | ㅈ | |

### DIPHTHONG_TRAIL — 이중모음 trailing glide

| ARPAbet | trailing 자모 |
|---------|--------------|
| EY | ㅣ |
| AY | ㅣ |
| OY | ㅣ |
| AW | ㅜ |
| OW | ㅜ |

### CODA_SET — 받침 허용 자음

`{ㄴ, ㄹ, ㅁ, ㅂ, ㄱ, ㅇ, ㅅ}`

단어 끝 또는 자음 앞에서 이 자모들만 받침(종성)으로 사용된다.
그 외 자음은 `으` 버퍼 음절로 처리한다.

---

## W/Y 복합모음 처리 (GLIDE_COMBO)

W 또는 Y가 모음 앞에서 복합 모음을 형성한다.

| 패턴 | 결과 모음 | 예시 |
|------|----------|------|
| Y + AH | ㅕ | year |
| Y + UW | ㅠ | you |
| Y + AO | ㅛ | yore |
| Y + IH/IY | ㅣ | (Y 흡수) |
| Y + other | ㅣ + 해당모음 (분리) | |
| W + AH | ㅘ | water |
| W + IH/IY | ㅚ/ㅜ+ㅣ | with |
| W + UH/UW | ㅜ | wood |
| W + other | ㅜ + 해당모음 (분리) | |

---

## 음절화 알고리즘

```
phonemes = strip_stress(raw_phonemes)   # EY1 → EY

syllables = []
i = 0
while i < len(phonemes):
    p = phonemes[i]

    if is_vowel(p):
        onset  = syllables[-1].pop_pending_consonant() if pending else ㅇ
        nucleus = VOWEL_JAMO[p]
        trail   = DIPHTHONG_TRAIL.get(p)          # None or ㅣ/ㅜ

        # coda 결정: 다음이 자음이고 그 뒤가 자음이거나 끝이면 받침
        next_c = phonemes[i+1] if is_consonant(i+1) else None
        after_next = phonemes[i+2] if exists(i+2) else None
        coda = None
        if next_c and (after_next is None or is_consonant(after_next)):
            jamo = CONS_JAMO[next_c]
            if jamo in CODA_SET:
                coda = jamo
                i += 1   # next_c 소비

        syllables.append(compose(onset, nucleus, coda))

        if trail:
            # trailing glide는 다음 자음을 받침으로 가질 수 있음
            syllables.append(compose(ㅇ, trail, ...))

    elif is_consonant(p):
        # 다음이 모음이면 → onset으로 보류 (다음 iteration에서 처리)
        # 다음이 자음이거나 끝이면 → 으 버퍼 음절
        if next_is_vowel:
            pending_onset = CONS_JAMO[p]
        else:
            syllables.append(compose(CONS_JAMO[p], ㅡ, None))

    i += 1

return ''.join(syllables)
```

---

## 유니코드 음절 조합 공식

```python
CHO  = ['ㄱ','ㄲ','ㄴ','ㄷ','ㄸ','ㄹ','ㅁ','ㅂ','ㅃ','ㅅ','ㅆ','ㅇ','ㅈ','ㅉ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ']
JUNG = ['ㅏ','ㅐ','ㅑ','ㅒ','ㅓ','ㅔ','ㅕ','ㅖ','ㅗ','ㅘ','ㅙ','ㅚ','ㅛ','ㅜ','ㅝ','ㅞ','ㅟ','ㅠ','ㅡ','ㅢ','ㅣ']
JONG = ['','ㄱ','ㄲ','ㄳ','ㄴ','ㄵ','ㄶ','ㄷ','ㄹ','ㄺ','ㄻ','ㄼ','ㄽ','ㄾ','ㄿ','ㅀ','ㅁ','ㅂ','ㅄ','ㅅ','ㅆ','ㅇ','ㅈ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ']

def compose(cho, jung, jong=''):
    c = CHO.index(cho)
    v = JUNG.index(jung)
    j = JONG.index(jong) if jong else 0
    return chr(0xAC00 + c * 21 * 28 + v * 28 + j)
```

---

## 테스트 케이스

기존 50개 테스트 전부 통과 유지.
`test_pronunciation.py`에 음절 변환 케이스 추가:

```python
# 기본 단어
assert word_to_korean("danger") == "데인져"
assert word_to_korean("love")   == "러브"
assert word_to_korean("with")   == "위드"
assert word_to_korean("your")   == "유어"

# 받침 케이스
assert word_to_korean("ring")   == "링"
assert word_to_korean("room")   == "룸"
assert word_to_korean("feel")   == "필"
assert word_to_korean("ten")    == "텐"

# 이중모음
assert word_to_korean("baby")   == "베이비"
assert word_to_korean("night")  == "나이트"
```

---

## 변경 파일

| 파일 | 변경 내용 |
|------|----------|
| `pronunciation.py` | `phonemes_to_korean()` 전면 교체, 테이블 4개 추가 |
| `tests/test_pronunciation.py` | 음절 변환 테스트 케이스 추가 |

API(`/api/pronunciation`), `app.py`, 프론트엔드 — **변경 없음**
