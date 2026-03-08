import pytest
from pronunciation import phonemes_to_korean, word_to_korean, line_to_korean, lyrics_to_korean


def test_phonemes_to_korean_vowels():
    # AA→아, AH0→어 (stress digit stripped), OW1→오
    assert phonemes_to_korean(['AA', 'AH0', 'OW1']) == '아어오'


def test_phonemes_to_korean_consonants():
    assert phonemes_to_korean(['HH', 'L', 'M']) == '흐르므'


def test_phonemes_to_korean_space():
    assert phonemes_to_korean([' ']) == ' '


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
