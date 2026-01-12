#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
영어 → 한글 발음 변환 API 서버
Flask 기반의 간단한 REST API
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import json

app = Flask(__name__)
CORS(app)  # CORS 설정으로 브라우저에서 접근 가능

# 영어 → 한글 발음 사전 (JavaScript와 동일)
PRONUNCIATION_DICT = {
    # 대명사
    'i': '아이', 'you': '유', 'he': '히', 'she': '쉬', 'it': '잇', "it's": '잇츠',
    'we': '위', 'they': '데이', 'me': '미', 'him': '힘', 'her': '허',
    'us': '어스', 'them': '뎀', 'myself': '마이셀프', 'yourself': '유어셀프',
    'my': '마이', 'your': '유어', 'his': '히즈', 'mine': '마인',

    # 기본 동사
    'is': '이즈', 'are': '아', 'am': '앰', 'was': '워즈', 'were': '워',
    'be': '비', 'been': '빈', 'being': '비잉',
    'have': '해브', 'has': '해즈', 'had': '해드',
    'do': '두', 'does': '더즈', 'did': '디드',
    "don't": '돈트', "doesn't": '더전트', "didn't": '디든트',
    'will': '윌', 'would': '우드', 'could': '쿠드', 'should': '슈드',
    "won't": '원트', "wouldn't": '우든트', "couldn't": '쿠든트',
    'can': '캔', "can't": '캔트', 'may': '메이', 'must': '머스트',

    # 기본 동사들
    'go': '고', 'come': '컴', 'get': '겟', 'make': '메이크', 'take': '테이크',
    'give': '기브', 'know': '노', 'think': '씽크', 'see': '씨', 'want': '원트',
    'look': '룩', 'use': '유즈', 'find': '파인드', 'tell': '텔', 'ask': '애스크',
    'work': '워크', 'feel': '필', 'try': '트라이', 'leave': '리브', 'call': '콜',
    'need': '니드', 'say': '세이', 'help': '헬프', 'talk': '토크', 'turn': '턴',
    'start': '스타트', 'show': '쇼', 'hear': '히어', 'play': '플레이', 'run': '런',
    'move': '무브', 'live': '리브', 'believe': '빌리브', 'bring': '브링', 'happen': '해픈',
    'write': '라이트', 'sit': '싯', 'stand': '스탠드', 'lose': '루즈', 'pay': '페이',
    'meet': '미트', 'include': '인클루드', 'continue': '컨티뉴', 'set': '셋', 'learn': '런',
    'change': '체인지', 'lead': '리드', 'understand': '언더스탠드', 'watch': '와치',
    'follow': '팔로우', 'stop': '스탑', 'create': '크리에이트', 'speak': '스피크',
    'read': '리드', 'spend': '스펜드', 'grow': '그로우', 'open': '오픈', 'walk': '워크',
    'win': '윈', 'teach': '티치', 'offer': '오퍼', 'remember': '리멤버', 'love': '러브',
    'consider': '컨시더', 'appear': '어피어', 'buy': '바이', 'serve': '서브',
    'die': '다이', 'send': '센드', 'build': '빌드', 'stay': '스테이', 'fall': '폴',
    'cut': '컷', 'reach': '리치', 'kill': '킬', 'raise': '레이즈', 'pass': '패스',

    # 형용사
    'good': '굿', 'great': '그레이트', 'new': '뉴', 'old': '올드', 'big': '빅',
    'small': '스몰', 'long': '롱', 'short': '쇼트', 'high': '하이', 'low': '로우',
    'early': '얼리', 'late': '레이트', 'young': '영', 'important': '임포턴트',
    'few': '퓨', 'public': '퍼블릭', 'bad': '배드', 'same': '세임', 'able': '에이블',
    'easy': '이지', 'hard': '하드', 'happy': '해피', 'sad': '새드', 'hot': '핫',
    'cold': '콜드', 'beautiful': '뷰티풀', 'strong': '스트롱', 'weak': '위크',
    'right': '라이트', 'wrong': '롱', 'free': '프리', 'ready': '레디', 'simple': '심플',
    'different': '디퍼런트', 'true': '트루', 'false': '폴스', 'sure': '슈어',
    'clear': '클리어', 'possible': '파서블', 'real': '리얼', 'full': '풀', 'better': '베터',
    'best': '베스트', 'nice': '나이스', 'pretty': '프리티', 'comfortable': '컴퍼터블',
    'uncomfortable': '언컴퍼터블', 'perfect': '퍼펙트', 'special': '스페셜',

    # 명사
    'time': '타임', 'year': '이어', 'people': '피플', 'way': '웨이', 'day': '데이',
    'man': '맨', 'thing': '씽', 'woman': '우먼', 'life': '라이프', 'child': '차일드',
    'world': '월드', 'school': '스쿨', 'state': '스테이트', 'family': '패밀리',
    'student': '스튜던트', 'group': '그룹', 'country': '컨트리', 'problem': '프라블럼',
    'hand': '핸드', 'part': '파트', 'place': '플레이스', 'case': '케이스', 'week': '위크',
    'company': '컴퍼니', 'system': '시스템', 'program': '프로그램', 'question': '퀘스천',
    'work': '워크', 'government': '거번먼트', 'number': '넘버', 'night': '나이트',
    'point': '포인트', 'home': '홈', 'water': '워터', 'room': '룸', 'mother': '마더',
    'area': '에어리어', 'money': '머니', 'story': '스토리', 'fact': '팩트', 'month': '먼쓰',
    'lot': '랏', 'right': '라이트', 'study': '스터디', 'book': '북', 'eye': '아이',
    'job': '잡', 'word': '워드', 'business': '비즈니스', 'issue': '이슈', 'side': '사이드',
    'kind': '카인드', 'head': '헤드', 'house': '하우스', 'service': '서비스', 'friend': '프렌드',
    'father': '파더', 'power': '파워', 'hour': '아워', 'game': '게임', 'line': '라인',
    'end': '엔드', 'member': '멤버', 'law': '로', 'car': '카', 'city': '시티',
    'community': '커뮤니티', 'name': '네임', 'president': '프레지던트', 'team': '팀',
    'minute': '미닛', 'idea': '아이디어', 'kid': '키드', 'body': '바디', 'information': '인포메이션',
    'back': '백', 'parent': '페어런트', 'face': '페이스', 'others': '아더스', 'level': '레벨',
    'office': '오피스', 'door': '도어', 'health': '헬쓰', 'person': '퍼슨', 'art': '아트',
    'war': '워', 'history': '히스토리', 'party': '파티', 'result': '리절트', 'change': '체인지',
    'morning': '모닝', 'reason': '리즌', 'research': '리서치', 'girl': '걸', 'guy': '가이',
    'moment': '모먼트', 'air': '에어', 'teacher': '티처', 'force': '포스', 'education': '에듀케이션',
    'love': '러브', 'music': '뮤직', 'song': '송', 'voice': '보이스', 'heart': '하트',
    'dream': '드림', 'hope': '호프', 'sky': '스카이', 'star': '스타', 'light': '라이트',
    'dark': '다크', 'color': '컬러', 'sound': '사운드', 'feeling': '필링', 'smile': '스마일',
    'tear': '티어', 'pain': '페인', 'fear': '피어', 'wall': '월', 'window': '윈도우',

    # 부사
    'not': '낫', 'now': '나우', 'very': '베리', 'just': '저스트', 'so': '쏘',
    'too': '투', 'also': '올쏘', 'only': '온리', 'well': '웰', 'back': '백',
    'then': '덴', 'how': '하우', 'more': '모어', 'most': '모스트', 'even': '이븐',
    'much': '머치', 'really': '리얼리', 'here': '히어', 'there': '데어', 'where': '웨어',
    'when': '웬', 'why': '와이', 'always': '올웨이즈', 'never': '네버', 'sometimes': '썸타임즈',
    'maybe': '메이비', 'together': '투게더', 'around': '어라운드', 'again': '어겐',
    'away': '어웨이', 'tonight': '투나잇', 'today': '투데이', 'tomorrow': '투모로우',
    'yesterday': '예스터데이', 'forever': '포에버', 'already': '올레디',

    # 전치사
    'in': '인', 'on': '온', 'at': '앳', 'to': '투', 'for': '포', 'of': '오브',
    'with': '위드', 'by': '바이', 'from': '프롬', 'up': '업', 'about': '어바웃',
    'into': '인투', 'through': '쓰루', 'over': '오버', 'after': '애프터', 'between': '비트윈',
    'under': '언더', 'during': '듀링', 'without': '위다웃', 'before': '비포', 'around': '어라운드',
    'down': '다운', 'off': '오프', 'out': '아웃', 'near': '니어', 'above': '어보브',

    # 접속사
    'and': '앤드', 'or': '오어', 'but': '벗', 'because': '비코즈', 'if': '이프',
    'when': '웬', 'than': '댄', 'while': '와일', 'though': '도', 'although': '올도',
    'unless': '언레스', 'until': '언틸', 'since': '신스',

    # 의문사
    'what': '왓', 'which': '위치', 'who': '후', 'whom': '훔', 'whose': '후즈',

    # 기타 자주 쓰이는 단어
    'yes': '예스', 'no': '노', 'okay': '오케이', 'ok': '오케이', 'oh': '오',
    'all': '올', 'some': '썸', 'any': '에니', 'every': '에브리', 'each': '이치',
    'many': '메니', 'little': '리틀', 'both': '보쓰', 'either': '아이더', 'neither': '나이더',
    'such': '서치', 'another': '어나더', 'other': '아더', 'else': '엘스',
    'thing': '씽', 'things': '씽즈', 'something': '썸씽', 'nothing': '나씽', 'everything': '에브리씽',
    'someone': '썸원', 'anyone': '에니원', 'everyone': '에브리원', 'nobody': '노바디',
    'somebody': '썸바디', 'everybody': '에브리바디',
    'this': '디스', 'that': '댓', 'these': '디즈', 'those': '도즈',

    # 노래에 자주 나오는 단어들
    'baby': '베이비', 'girl': '걸', 'boy': '보이', 'lady': '레이디', 'darling': '달링',
    'crazy': '크레이지', 'lonely': '론리', 'break': '브레이크', 'broken': '브로큰',
    'hurts': '허츠', 'hurt': '허트', 'kiss': '키스', 'touch': '터치', 'hold': '홀드',
    'dance': '댄스', 'dancing': '댄싱', 'sing': '씽', 'singing': '씽잉',
    'cry': '크라이', 'crying': '크라잉', 'tears': '티어즈', 'lies': '라이즈',
    'lose': '루즈', 'lost': '로스트', 'found': '파운드', 'stay': '스테이',
    'leaving': '리빙', 'goodbye': '굿바이', 'hello': '헬로우', 'sorry': '쏘리',
    'please': '플리즈', 'thank': '땡크', 'thanks': '땡스',
    'rain': '레인', 'shine': '샤인', 'fire': '파이어', 'cold': '콜드',
    'wild': '와일드', 'free': '프리', 'alive': '얼라이브', 'dead': '데드',
    'heaven': '헤븐', 'hell': '헬', 'angel': '엔젤', 'devil': '데블',
    'beautiful': '뷰티풀', 'wonderful': '원더풀', 'amazing': '어메이징',
    'magic': '매직', 'miracle': '미러클', 'paradise': '패러다이스',
}

# 발음 규칙 패턴
PRONUNCIATION_RULES = {
    # 접미사 규칙
    r'tion$': '션',
    r'sion$': '션',
    r'ture$': '처',
    r'able$': '어블',
    r'ible$': '어블',
    r'ful$': '풀',
    r'less$': '레스',
    r'ness$': '네스',
    r'ment$': '먼트',
    r'ing$': '잉',
    r'ed$': '드',
    r'ly$': '리',
    r'ity$': '이티',
    r'ous$': '어스',
    r'ive$': '이브',

    # 이중 모음
    r'ee': '이',
    r'ea': '이',
    r'oo': '우',
    r'ai': '에이',
    r'ay': '에이',
    r'oy': '오이',
    r'ou': '아우',
    r'ow': '아우',
    r'igh': '아이',

    # 자음 조합
    r'th': '쓰',
    r'sh': '쉬',
    r'ch': '치',
    r'ph': '프',
    r'wh': '웨',
    r'ng': '잉',
    r'ck': '크',
}

def convert_by_rules(word):
    """규칙 기반으로 영어 단어를 한글 발음으로 변환"""
    result = word.lower()

    # 접미사 규칙 먼저 적용
    for pattern, replacement in PRONUNCIATION_RULES.items():
        if pattern.endswith('$'):
            result = re.sub(pattern, replacement, result)

    # 기본 자음/모음 매핑
    vowel_map = {
        'a': '아', 'e': '에', 'i': '이', 'o': '오', 'u': '유'
    }
    consonant_map = {
        'b': '브', 'c': '크', 'd': '드', 'f': '프', 'g': '그',
        'h': '흐', 'j': '즈', 'k': '크', 'l': '르', 'm': '므',
        'n': '느', 'p': '프', 'q': '크', 'r': '르', 's': '스',
        't': '트', 'v': '브', 'w': '우', 'x': '크스', 'y': '이', 'z': '즈'
    }

    # 자음 조합 패턴 적용
    for pattern, replacement in PRONUNCIATION_RULES.items():
        if not pattern.endswith('$'):
            result = result.replace(pattern.replace('r\'', '').replace('\'', ''), replacement)

    # 나머지 글자를 기본 매핑으로 변환
    korean = ''
    i = 0
    while i < len(result):
        char = result[i]
        if char in vowel_map:
            korean += vowel_map[char]
        elif char in consonant_map:
            korean += consonant_map[char]
        else:
            korean += char
        i += 1

    return korean if korean else word

def transliterate_word(word):
    """단어 하나를 변환"""
    # 구두점 분리
    match = re.match(r'^([^a-zA-Z\']*)([a-zA-Z\']+)([^a-zA-Z\']*)$', word)

    if not match:
        return word

    prefix, main_word, suffix = match.groups()
    lower_word = main_word.lower()

    # 1. 사전에서 찾기
    if lower_word in PRONUNCIATION_DICT:
        return prefix + PRONUNCIATION_DICT[lower_word] + suffix

    # 2. 규칙 기반 변환
    result = convert_by_rules(lower_word)
    return prefix + result + suffix

def transliterate_text(text):
    """전체 텍스트를 변환"""
    lines = text.split('\n')
    converted_lines = []

    for line in lines:
        if not line.strip():
            converted_lines.append('')
            continue

        words = line.split()
        converted_words = [transliterate_word(word) for word in words]
        converted_lines.append(' '.join(converted_words))

    return '\n'.join(converted_lines)

@app.route('/health', methods=['GET'])
def health():
    """헬스 체크 엔드포인트"""
    return jsonify({'status': 'ok', 'message': 'Transliteration server is running'})

@app.route('/transliterate', methods=['POST'])
def transliterate():
    """발음 변환 API 엔드포인트"""
    try:
        data = request.get_json()

        if not data or 'text' not in data:
            return jsonify({
                'error': 'Missing required field: text'
            }), 400

        text = data['text']

        # 단어 또는 전체 텍스트 변환
        if 'word_mode' in data and data['word_mode']:
            result = transliterate_word(text)
        else:
            result = transliterate_text(text)

        return jsonify({
            'original': text,
            'transliteration': result,
            'success': True
        })

    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/batch', methods=['POST'])
def batch_transliterate():
    """배치 변환 API (여러 단어를 한번에)"""
    try:
        data = request.get_json()

        if not data or 'words' not in data:
            return jsonify({
                'error': 'Missing required field: words'
            }), 400

        words = data['words']

        if not isinstance(words, list):
            return jsonify({
                'error': 'words must be an array'
            }), 400

        results = {}
        for word in words:
            results[word] = transliterate_word(word)

        return jsonify({
            'results': results,
            'success': True
        })

    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

if __name__ == '__main__':
    print("=" * 50)
    print("영어 → 한글 발음 변환 서버 시작")
    print("포트: 5001")
    print("엔드포인트:")
    print("  - POST /transliterate - 텍스트 변환")
    print("  - POST /batch - 배치 변환")
    print("  - GET /health - 헬스 체크")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5001, debug=True)
