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
