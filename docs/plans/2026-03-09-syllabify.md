# 음절 합성 발음 변환 구현 계획

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** ARPAbet 음소를 음절 단위로 합성해 받침 있는 자연스러운 한글 발음 표기 생성

**Architecture:** `pronunciation.py`의 `phonemes_to_korean()`만 교체. 자음·모음 자모 테이블 4개 + 유니코드 음절 조합 함수 + 음절화 로직으로 구성. 외부 API, app.py, 프론트엔드 변경 없음.

**Tech Stack:** Python, g2p_en (ARPAbet 변환), 한글 유니코드 (0xAC00), pytest

---

### Task 1: 유니코드 음절 조합 함수 + 자모 테이블 (TDD)

**Files:**
- Modify: `pronunciation.py`
- Modify: `tests/test_pronunciation.py`

**Step 1: 실패할 테스트 작성**

`tests/test_pronunciation.py` 하단에 추가:

```python
# ── 음절 합성 ────────────────────────────────────────────────

from pronunciation import compose_hangul, JUNG

def test_compose_basic_syllable():
    # ㄷ + ㅓ + 종성없음 = 더
    assert compose_hangul('ㄷ', 'ㅓ') == '더'

def test_compose_with_coda():
    # ㄷ + ㅔ + ㄴ = 덴
    assert compose_hangul('ㄷ', 'ㅔ', 'ㄴ') == '덴'

def test_compose_no_onset():
    # 초성없음(ㅇ) + ㅓ = 어
    assert compose_hangul('ㅇ', 'ㅓ') == '어'

def test_compose_no_onset_with_coda():
    # ㅇ + ㅣ + ㄴ = 인
    assert compose_hangul('ㅇ', 'ㅣ', 'ㄴ') == '인'

def test_jung_table_contains_compound():
    # 복합모음이 JUNG 테이블에 있어야 함
    assert 'ㅕ' in JUNG
    assert 'ㅠ' in JUNG
    assert 'ㅛ' in JUNG
```

**Step 2: 실패 확인**

```bash
cd /Users/work6/Desktop/ai-code/song-pronunciation-kor
python3 -m pytest tests/test_pronunciation.py -v -k "compose or jung_table"
```

예상: `ImportError: cannot import name 'compose_hangul'`

**Step 3: 자모 테이블 + compose_hangul 구현**

`pronunciation.py` 상단의 `import re` 아래에 삽입 (기존 `ARPABET_TO_KOR` dict 위):

```python
# ── 한글 자모 테이블 ────────────────────────────────────────
CHO = ['ㄱ','ㄲ','ㄴ','ㄷ','ㄸ','ㄹ','ㅁ','ㅂ','ㅃ','ㅅ','ㅆ',
       'ㅇ','ㅈ','ㅉ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ']

JUNG = ['ㅏ','ㅐ','ㅑ','ㅒ','ㅓ','ㅔ','ㅕ','ㅖ','ㅗ','ㅘ','ㅙ',
        'ㅚ','ㅛ','ㅜ','ㅝ','ㅞ','ㅟ','ㅠ','ㅡ','ㅢ','ㅣ']

JONG = ['','ㄱ','ㄲ','ㄳ','ㄴ','ㄵ','ㄶ','ㄷ','ㄹ','ㄺ','ㄻ',
        'ㄼ','ㄽ','ㄾ','ㄿ','ㅀ','ㅁ','ㅂ','ㅄ','ㅅ','ㅆ',
        'ㅇ','ㅈ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ']


def compose_hangul(cho: str, jung: str, jong: str = '') -> str:
    """초성 + 중성 + 종성(선택) → 완성형 한글 음절"""
    c = CHO.index(cho)
    v = JUNG.index(jung)
    j = JONG.index(jong) if jong else 0
    return chr(0xAC00 + c * 21 * 28 + v * 28 + j)
```

**Step 4: 통과 확인**

```bash
python3 -m pytest tests/test_pronunciation.py -v -k "compose or jung_table"
```

예상: `5 passed`

**Step 5: 커밋**

```bash
git add pronunciation.py tests/test_pronunciation.py
git commit -m "feat: 한글 자모 테이블 + compose_hangul 음절 조합 함수"
```

---

### Task 2: 자음·모음 ARPAbet 매핑 테이블 (TDD)

**Files:**
- Modify: `pronunciation.py`
- Modify: `tests/test_pronunciation.py`

**Step 1: 실패할 테스트 작성**

`tests/test_pronunciation.py` 하단에 추가:

```python
from pronunciation import VOWEL_JAMO, CONS_JAMO, DIPHTHONG_TRAIL, CODA_SET

def test_vowel_jamo_basic():
    assert VOWEL_JAMO['AH'] == 'ㅓ'
    assert VOWEL_JAMO['IY'] == 'ㅣ'
    assert VOWEL_JAMO['UW'] == 'ㅜ'
    assert VOWEL_JAMO['AO'] == 'ㅗ'

def test_vowel_jamo_diphthong_main():
    # 이중모음의 메인 모음
    assert VOWEL_JAMO['EY'] == 'ㅔ'
    assert VOWEL_JAMO['AY'] == 'ㅏ'
    assert VOWEL_JAMO['OW'] == 'ㅗ'

def test_cons_jamo_basic():
    assert CONS_JAMO['D'] == 'ㄷ'
    assert CONS_JAMO['N'] == 'ㄴ'
    assert CONS_JAMO['L'] == 'ㄹ'
    assert CONS_JAMO['M'] == 'ㅁ'
    assert CONS_JAMO['JH'] == 'ㅈ'
    assert CONS_JAMO['V'] == 'ㅂ'

def test_diphthong_trail():
    assert DIPHTHONG_TRAIL['EY'] == 'ㅣ'
    assert DIPHTHONG_TRAIL['AY'] == 'ㅣ'
    assert DIPHTHONG_TRAIL['AW'] == 'ㅜ'
    assert DIPHTHONG_TRAIL['OW'] == 'ㅜ'
    assert DIPHTHONG_TRAIL['OY'] == 'ㅣ'

def test_coda_set_contains_sonorants():
    assert 'ㄴ' in CODA_SET
    assert 'ㄹ' in CODA_SET
    assert 'ㅁ' in CODA_SET
    assert 'ㅇ' in CODA_SET
    assert 'ㅂ' in CODA_SET
    assert 'ㄱ' in CODA_SET
```

**Step 2: 실패 확인**

```bash
python3 -m pytest tests/test_pronunciation.py -v -k "vowel_jamo or cons_jamo or diphthong or coda_set"
```

예상: `ImportError: cannot import name 'VOWEL_JAMO'`

**Step 3: 4개 테이블 구현**

`pronunciation.py`의 `compose_hangul` 함수 바로 아래에 추가:

```python
# ── ARPAbet → 자모 매핑 ─────────────────────────────────────
VOWEL_JAMO = {
    'AA': 'ㅏ', 'AE': 'ㅐ', 'AH': 'ㅓ', 'AO': 'ㅗ',
    'EH': 'ㅔ', 'ER': 'ㅓ', 'IH': 'ㅣ', 'IY': 'ㅣ',
    'UH': 'ㅓ', 'UW': 'ㅜ',
    # 이중모음 — 메인 모음만 (trailing은 DIPHTHONG_TRAIL)
    'EY': 'ㅔ', 'AY': 'ㅏ', 'AW': 'ㅏ', 'OW': 'ㅗ', 'OY': 'ㅗ',
}

CONS_JAMO = {
    'B': 'ㅂ', 'CH': 'ㅊ', 'D': 'ㄷ', 'DH': 'ㄷ',
    'F': 'ㅍ', 'G': 'ㄱ', 'HH': 'ㅎ', 'JH': 'ㅈ',
    'K': 'ㄱ', 'L': 'ㄹ', 'M': 'ㅁ', 'N': 'ㄴ',
    'NG': 'ㅇ', 'P': 'ㅍ', 'R': 'ㄹ', 'S': 'ㅅ',
    'SH': 'ㅅ', 'T': 'ㅌ', 'TH': 'ㅅ', 'V': 'ㅂ',
    'W': 'ㅜ', 'Y': 'ㅣ', 'Z': 'ㅈ', 'ZH': 'ㅈ',
}

# 이중모음 trailing glide (EY → 에이에서 ㅣ 부분)
DIPHTHONG_TRAIL = {
    'EY': 'ㅣ', 'AY': 'ㅣ', 'OY': 'ㅣ',
    'AW': 'ㅜ', 'OW': 'ㅜ',
}

# 받침으로 허용되는 자모
CODA_SET = {'ㄴ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㄱ', 'ㅇ', 'ㅅ'}

# W/Y + 모음 → 복합 모음 (예: Y+AH → ㅕ)
GLIDE_COMBO = {
    ('Y', 'AH'): 'ㅕ', ('Y', 'UW'): 'ㅠ', ('Y', 'AO'): 'ㅛ',
    ('Y', 'AE'): 'ㅖ', ('Y', 'EH'): 'ㅖ', ('Y', 'UH'): 'ㅕ',
    ('W', 'AH'): 'ㅘ', ('W', 'AO'): 'ㅗ', ('W', 'IH'): 'ㅜ',
    ('W', 'IY'): 'ㅜ', ('W', 'UH'): 'ㅜ', ('W', 'UW'): 'ㅜ',
    ('W', 'EH'): 'ㅞ', ('W', 'ER'): 'ㅝ',
}

VOWELS = set(VOWEL_JAMO.keys())
CONSONANTS = set(CONS_JAMO.keys())
GLIDES = {'W', 'Y'}
```

**Step 4: 통과 확인**

```bash
python3 -m pytest tests/test_pronunciation.py -v -k "vowel_jamo or cons_jamo or diphthong or coda_set"
```

예상: `6 passed`

**Step 5: 커밋**

```bash
git add pronunciation.py tests/test_pronunciation.py
git commit -m "feat: ARPAbet→자모 매핑 테이블 4종 (VOWEL_JAMO, CONS_JAMO, DIPHTHONG_TRAIL, CODA_SET)"
```

---

### Task 3: 음절화 함수 syllabify() (TDD)

**Files:**
- Modify: `pronunciation.py`
- Modify: `tests/test_pronunciation.py`

**Step 1: 실패할 테스트 작성**

`tests/test_pronunciation.py` 하단에 추가:

```python
from pronunciation import syllabify

def test_syllabify_simple_cv():
    # L + AH = 러
    assert syllabify(['L', 'AH0']) == ['러']

def test_syllabify_cvc_with_sonorant_coda():
    # T + EH + N = 텐 (N → 받침)
    assert syllabify(['T', 'EH1', 'N']) == ['텐']

def test_syllabify_consonant_cluster_buffer():
    # N + IH + T → N 앞에 자음 없으므로 으 버퍼: 니+트
    assert syllabify(['N', 'IH1', 'T']) == ['니', '트']

def test_syllabify_diphthong_with_coda():
    # D + EY + N → 데 + 인 (EY trailing ㅣ + N받침)
    assert syllabify(['D', 'EY1', 'N']) == ['데', '인']

def test_syllabify_glide_combo():
    # W + IH + DH → 위 + 드 (W+IH→ㅜ, DH→ㄷ으 버퍼)
    result = syllabify(['W', 'IH1', 'DH'])
    assert result == ['위', '드']

def test_syllabify_ng_coda():
    # R + IH + NG → 링 (NG → 받침 ㅇ)
    assert syllabify(['R', 'IH1', 'NG']) == ['링']

def test_syllabify_no_onset():
    # AH alone → 어
    assert syllabify(['AH0']) == ['어']
```

**Step 2: 실패 확인**

```bash
python3 -m pytest tests/test_pronunciation.py -v -k "syllabify"
```

예상: `ImportError: cannot import name 'syllabify'`

**Step 3: syllabify() 구현**

`pronunciation.py`의 `GLIDES = ...` 라인 아래에 추가:

```python
def _strip_stress(phone: str) -> str:
    return phone.rstrip('012')


def syllabify(phonemes: list) -> list:
    """ARPAbet 음소 리스트 → 한글 음절 리스트"""
    phones = [_strip_stress(p) for p in phonemes if p != ' ']
    result = []
    i = 0

    while i < len(phones):
        p = phones[i]

        # ── Glide (W/Y) + 다음 모음 → 복합모음 처리 ──────────
        if p in GLIDES and i + 1 < len(phones) and phones[i + 1] in VOWELS:
            nxt = phones[i + 1]
            combo = GLIDE_COMBO.get((p, nxt))
            if combo:
                jung = combo
            else:
                # 복합모음 없으면: glide 자모 → 단독 음절, 다음 모음 별도
                result.append(compose_hangul('ㅇ', CONS_JAMO[p] if CONS_JAMO[p] in JUNG else 'ㅜ'))
                i += 1
                continue
            i += 1  # nxt 소비
            # onset: 이전 pending 자음 (result에서 꺼내기 불가 → 직접 추적)
            # 이 케이스는 glide가 단어 시작이거나 자음 뒤에 올 때 처리 필요
            # 단순화: glide combo는 항상 ㅇ onset으로 시작
            onset = 'ㅇ'
            # coda 결정
            coda, skip = _find_coda(phones, i + 1)
            result.append(compose_hangul(onset, jung, coda))
            if skip:
                i += 1
            i += 1
            continue

        # ── 자음 처리 ────────────────────────────────────────
        if p in CONSONANTS:
            cons_jamo = CONS_JAMO[p]
            # 다음이 모음이면 onset으로 보류 (다음 iteration에서 처리)
            if i + 1 < len(phones) and phones[i + 1] in VOWELS:
                # 다음 iteration으로 pass — onset은 아래 모음 처리에서 담당
                i += 1
                vow = phones[i]
                onset = cons_jamo
                jung = VOWEL_JAMO[vow]
                trail = DIPHTHONG_TRAIL.get(vow)
                coda, skip = _find_coda(phones, i + 1)
                result.append(compose_hangul(onset, jung, coda if not trail else ''))
                if trail:
                    # trailing glide → 별도 음절 (받침 붙일 수 있음)
                    t_coda, t_skip = _find_coda(phones, i + (2 if skip else 1))
                    result.append(compose_hangul('ㅇ', trail, t_coda))
                    if t_skip:
                        i += 1
                elif skip:
                    i += 1
            else:
                # 다음이 자음이거나 단어 끝 → 으 버퍼 음절
                result.append(compose_hangul(cons_jamo, 'ㅡ'))
            i += 1
            continue

        # ── 모음 처리 (앞에 처리된 자음 onset 없이 단독) ──────
        if p in VOWELS:
            jung = VOWEL_JAMO[p]
            trail = DIPHTHONG_TRAIL.get(p)
            coda, skip = _find_coda(phones, i + 1)
            result.append(compose_hangul('ㅇ', jung, coda if not trail else ''))
            if trail:
                t_coda, t_skip = _find_coda(phones, i + (2 if skip else 1))
                result.append(compose_hangul('ㅇ', trail, t_coda))
                if t_skip:
                    i += 1
            elif skip:
                i += 1
            i += 1
            continue

        i += 1

    return result


def _find_coda(phones: list, idx: int):
    """phones[idx]가 자음이고 그 다음이 자음이거나 끝이면 받침 반환.
    Returns: (coda_jamo or '', consumed_bool)
    """
    if idx >= len(phones):
        return '', False
    p = phones[idx]
    if p not in CONSONANTS or p in GLIDES:
        return '', False
    after = phones[idx + 1] if idx + 1 < len(phones) else None
    if after is None or after in CONSONANTS:
        jamo = CONS_JAMO[p]
        if jamo in CODA_SET:
            return jamo, True
    return '', False
```

**Step 4: 통과 확인**

```bash
python3 -m pytest tests/test_pronunciation.py -v -k "syllabify"
```

예상: `7 passed`

**Step 5: 전체 기존 테스트도 확인**

```bash
python3 -m pytest tests/ -v
```

예상: 기존 50개 + 신규 테스트 모두 통과

**Step 6: 커밋**

```bash
git add pronunciation.py tests/test_pronunciation.py
git commit -m "feat: syllabify() - ARPAbet 음소 배열을 한글 음절 리스트로 변환"
```

---

### Task 4: phonemes_to_korean() 교체 + 단어 단위 검증 (TDD)

**Files:**
- Modify: `pronunciation.py`
- Modify: `tests/test_pronunciation.py`

**Step 1: 실패할 테스트 작성**

`tests/test_pronunciation.py` 하단에 추가:

```python
def test_word_danger():
    result = word_to_korean("danger")
    # 데인져 또는 데인저 (JH+ER 처리에 따라)
    assert result in ("데인져", "데인저")

def test_word_love():
    assert word_to_korean("love") == "러브"

def test_word_with():
    assert word_to_korean("with") == "위드"

def test_word_ring():
    assert word_to_korean("ring") == "링"

def test_word_room():
    assert word_to_korean("room") == "룸"

def test_word_feel():
    assert word_to_korean("feel") == "필"

def test_word_ten():
    assert word_to_korean("ten") == "텐"

def test_word_baby():
    assert word_to_korean("baby") == "베이비"

def test_word_night():
    assert word_to_korean("night") == "나이트"
```

**Step 2: 실패 확인**

```bash
python3 -m pytest tests/test_pronunciation.py -v -k "word_danger or word_love or word_with or word_ring or word_room or word_feel or word_ten or word_baby or word_night"
```

예상: 일부 또는 전부 FAIL

**Step 3: phonemes_to_korean() 교체**

`pronunciation.py`에서 기존 `phonemes_to_korean` 함수를 찾아 아래로 교체:

```python
def phonemes_to_korean(phonemes: list) -> str:
    """Convert ARPAbet phoneme list to Korean string using syllabification."""
    # 단어 경계(' ')로 분리해 각 단어 음절화 후 합침
    words_phones = []
    current = []
    for p in phonemes:
        if p == ' ':
            if current:
                words_phones.append(current)
                current = []
        else:
            current.append(p)
    if current:
        words_phones.append(current)

    parts = []
    for wp in words_phones:
        parts.append(''.join(syllabify(wp)))
    return ' '.join(parts)
```

기존 `ARPABET_TO_KOR` dict은 삭제한다 (더 이상 사용하지 않음).

**Step 4: 통과 확인**

```bash
python3 -m pytest tests/test_pronunciation.py -v -k "word_danger or word_love or word_with or word_ring or word_room or word_feel or word_ten or word_baby or word_night"
```

테스트가 실패하는 항목이 있으면 `syllabify()` 또는 테이블을 조정하여 통과시킨다.

**Step 5: 전체 테스트 확인**

```bash
python3 -m pytest tests/ -v
```

예상: 기존 50개 + 신규 테스트 전부 통과

**Step 6: 커밋**

```bash
git add pronunciation.py tests/test_pronunciation.py
git commit -m "feat: phonemes_to_korean() 음절 합성 방식으로 교체 (받침 있는 한글 발음 생성)"
```

---

### Task 5: 최종 검증 + 푸시

**Step 1: 전체 테스트 실행**

```bash
cd /Users/work6/Desktop/ai-code/song-pronunciation-kor
python3 -m pytest tests/ -v
```

예상: 전체 passed (숫자 확인)

**Step 2: 실제 동작 확인**

```bash
python3 -c "
from pronunciation import word_to_korean
tests = [('danger','데인져/데인저'), ('love','러브'), ('with','위드'),
         ('your','유어'), ('ring','링'), ('room','룸'), ('feel','필')]
for word, expected in tests:
    result = word_to_korean(word)
    status = '✅' if result in expected else '❌'
    print(f'{status} {word} → {result}  (기대: {expected})')
"
```

**Step 3: 서버 실행 후 Olivia Dean - Danger 검색 확인**

```bash
python3 app.py
# 브라우저에서 http://localhost:5001 접속
# Olivia Dean / Danger 검색 → "Danger with your love" 발음 확인
```

**Step 4: 커밋 + 푸시**

```bash
git add -A
git commit -m "test: 음절 합성 발음 변환 최종 검증 완료"
git push origin main
```
