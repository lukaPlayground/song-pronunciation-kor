import pytest
from pronunciation import phonemes_to_korean, word_to_korean, line_to_korean, lyrics_to_korean


def test_phonemes_to_korean_vowels():
    # AA→아, AH0→어 (stress digit stripped), OW1→오우 (OW는 이중모음)
    assert phonemes_to_korean(['AA', 'AH0', 'OW1']) == '아어오우'


def test_phonemes_to_korean_consonants():
    assert phonemes_to_korean(['HH', 'L', 'M']) == '흐르므'


def test_phonemes_to_korean_space():
    # 공백만 있으면 빈 문자열 반환 (단어 없음)
    assert phonemes_to_korean([' ']) == ''


def test_phonemes_to_korean_empty():
    assert phonemes_to_korean([]) == ''


def test_word_to_korean_returns_string():
    result = word_to_korean('hello')
    assert isinstance(result, str)
    assert len(result) > 0


def test_word_to_korean_empty():
    assert word_to_korean('') == ''


def test_word_to_korean_nonalpha():
    # Numbers/punctuation only → return as-is
    assert word_to_korean('123') == '123'


def test_line_to_korean_words_separated():
    result = line_to_korean('hello world')
    assert ' ' in result


def test_line_to_korean_empty():
    assert line_to_korean('') == ''


def test_line_to_korean_whitespace_only():
    assert line_to_korean('   ') == ''


def test_lyrics_to_korean_structure():
    lyrics = "hello world\n\ngoodbye"
    result = lyrics_to_korean(lyrics)
    assert len(result) == 3
    assert result[0]['original'] == 'hello world'
    assert 'pronunciation' in result[0]
    assert result[1]['original'] == ''
    assert result[1]['pronunciation'] == ''
    assert result[2]['original'] == 'goodbye'


def test_word_to_korean_with_trailing_punctuation():
    # "hello," should produce same result as "hello"
    assert word_to_korean("hello,") == word_to_korean("hello")


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


# ── 한글 처리 ────────────────────────────────────────────────

def test_word_to_korean_korean_word():
    assert word_to_korean("사랑해") == "사랑해"


def test_word_to_korean_korean_with_punctuation():
    assert word_to_korean("너를,") == "너를,"


def test_line_to_korean_full_korean():
    result = line_to_korean("사랑해 너를")
    assert result == "사랑해 너를"


def test_line_to_korean_mixed():
    result = line_to_korean("I love 너를")
    parts = result.split()
    assert parts[2] == "너를"
    assert parts[0] != "I"


def test_lyrics_to_korean_korean_song():
    lyrics = "사랑해\n너를 원해\n"
    result = lyrics_to_korean(lyrics)
    assert result[0]['pronunciation'] == "사랑해"
    assert result[1]['pronunciation'] == "너를 원해"
