import re
from g2p_en import G2p

# G2p instance created once at module load (expensive to create repeatedly)
g2p = G2p()

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
    ('W', 'AH'): 'ㅘ', ('W', 'AO'): 'ㅗ', ('W', 'IH'): 'ㅟ',
    ('W', 'IY'): 'ㅟ', ('W', 'UH'): 'ㅜ', ('W', 'UW'): 'ㅜ',
    ('W', 'EH'): 'ㅞ', ('W', 'ER'): 'ㅝ',
}

VOWELS = set(VOWEL_JAMO.keys())
CONSONANTS = set(CONS_JAMO.keys())
GLIDES = {'W', 'Y'}


def _strip_stress(phone: str) -> str:
    return phone.rstrip('012')


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
            onset = 'ㅇ'
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
                i += 1
                vow = phones[i]
                onset = cons_jamo
                jung = VOWEL_JAMO[vow]
                trail = DIPHTHONG_TRAIL.get(vow)
                coda, skip = _find_coda(phones, i + 1)
                result.append(compose_hangul(onset, jung, coda if not trail else ''))
                if trail:
                    # trailing glide → 별도 음절 (받침 붙일 수 있음)
                    # trail의 coda는 i+1 위치에서 탐색 (main vowel coda와 같은 위치)
                    t_coda, t_skip = _find_coda(phones, i + 1)
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
                t_coda, t_skip = _find_coda(phones, i + 1)
                result.append(compose_hangul('ㅇ', trail, t_coda))
                if t_skip:
                    i += 1
            elif skip:
                i += 1
            i += 1
            continue

        i += 1

    return result


ARPABET_TO_KOR = {
    # Vowels (stress digits 0,1,2 stripped before lookup)
    'AA': '아', 'AE': '애', 'AH': '어', 'AO': '오',
    'AW': '아우', 'AY': '아이', 'EH': '에', 'ER': '어',
    'EY': '에이', 'IH': '이', 'IY': '이', 'OW': '오',
    'OY': '오이', 'UH': '우', 'UW': '우',
    # Consonants
    'B': '브', 'CH': '치', 'D': '드', 'DH': '드',
    'F': '프', 'G': '그', 'HH': '흐', 'JH': '즈',
    'K': '크', 'L': '르', 'M': '므', 'N': '느',
    'NG': '잉', 'P': '프', 'R': '르', 'S': '스',
    'SH': '쉬', 'T': '트', 'TH': '쓰', 'V': '브',
    'W': '우', 'Y': '이', 'Z': '즈', 'ZH': '즈',
}


def phonemes_to_korean(phonemes: list) -> str:
    """Convert ARPAbet phoneme list to Korean string."""
    parts = []
    for phone in phonemes:
        if phone == ' ':
            parts.append(' ')
            continue
        stripped = phone.rstrip('012')  # strip stress digit
        if stripped in ARPABET_TO_KOR:
            parts.append(ARPABET_TO_KOR[stripped])
    return ''.join(parts)


def word_to_korean(word: str) -> str:
    """Convert single English word to Korean pronunciation."""
    if not word:
        return word
    clean = re.sub(r"[^a-zA-Z']", '', word)
    if not clean:
        return word  # numbers/punctuation only → return as-is
    phonemes = g2p(clean.lower())
    result = phonemes_to_korean(phonemes)
    return result if result else word


def line_to_korean(line: str) -> str:
    """Convert one line of English to Korean pronunciation."""
    if not line.strip():
        return ''
    words = line.split()
    return ' '.join(word_to_korean(w) for w in words)


def lyrics_to_korean(lyrics: str) -> list:
    """Convert full lyrics text to list of {original, pronunciation} dicts."""
    result = []
    for line in lyrics.split('\n'):
        result.append({
            'original': line,
            'pronunciation': line_to_korean(line)
        })
    return result
