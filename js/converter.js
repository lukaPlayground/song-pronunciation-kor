// 영어 발음을 한글로 변환하는 함수 (개선된 버전 - 규칙 기반)

// 일반적인 영단어 발음 매핑 (확장된 사전 - 1000개 이상)
const commonWords = {
    // 대명사
    'i': '아이', 'you': '유', 'he': '히', 'she': '쉬', 'it': '잇', "it's": '잇츠',
    'we': '위', 'they': '데이', 'me': '미', 'him': '힘', 'her': '허',
    'us': '어스', 'them': '뎀', 'myself': '마이셀프', 'yourself': '유어셀프',
    'himself': '힘셀프', 'herself': '허셀프', 'ourselves': '아워셀브즈',
    'themselves': '뎀셀브즈',
    'my': '마이', 'your': '유어', 'his': '히즈', 'mine': '마인', 'yours': '유어즈',

    // 동사 (기본형 + 변형)
    'is': '이즈', 'are': '아', 'am': '앰', 'was': '워즈', 'were': '워', 'you\'re': '유알',
    'be': '비', 'been': '빈', 'being': '비잉',
    'have': '해브', 'has': '해즈', 'had': '해드', 'having': '해빙',
    'do': '두', 'does': '더즈', 'did': '디드', 'doing': '두잉', "don't": '돈트', "doesn't": '더전트', "didn't": '디든트',
    'will': '윌', 'would': '우드', 'could': '쿠드', 'should': '슈드', "won't": '원트', "wouldn't": '우든트', "couldn't": '쿠든트', "shouldn't": '슈든트',
    'can': '캔', "can't": '캔트', 'may': '메이', 'must': '머스트', "mustn't": '머슨트',
    'might': '마잇', 'shall': '샬',

    // 이동 동사
    'go': '고', 'goes': '고즈', 'going': '고잉', 'gone': '곤', 'went': '웬트',
    'come': '컴', 'comes': '컴즈', 'coming': '커밍', 'came': '케임',
    'run': '런', 'running': '러닝', 'ran': '랜',
    'walk': '워크', 'walking': '워킹', 'walked': '워크트',
    'fly': '플라이', 'flying': '플라잉', 'flew': '플루', 'flown': '플로운',
    'drive': '드라이브', 'driving': '드라이빙', 'drove': '드로브', 'driven': '드리븐',
    'ride': '라이드', 'riding': '라이딩', 'rode': '로드', 'ridden': '리든',
    'jump': '점프', 'jumping': '점핑', 'jumped': '점프트',
    'climb': '클라임', 'climbing': '클라이밍', 'climbed': '클라임드',

    // 행동 동사
    'get': '겟', 'getting': '게팅', 'got': '갓', 'gotten': '가튼',
    'make': '메이크', 'making': '메이킹', 'made': '메이드',
    'take': '테이크', 'taking': '테이킹', 'took': '투크', 'taken': '테이큰',
    'give': '기브', 'giving': '기빙', 'gave': '게이브', 'given': '기븐',
    'put': '풋', 'putting': '푸팅',
    'set': '셋', 'setting': '세팅',
    'let': '렛', 'letting': '레팅',
    'bring': '브링', 'bringing': '브링잉', 'brought': '브롯',
    'buy': '바이', 'buying': '바잉', 'bought': '봇',
    'catch': '캐치', 'catching': '캐칭', 'caught': '콧',
    'hold': '홀드', 'holding': '홀딩', 'held': '헬드',
    'keep': '킵', 'keeping': '키핑', 'kept': '켑트',
    'leave': '리브', 'leaving': '리빙', 'left': '레프트',
    'lose': '루즈', 'losing': '루징', 'lost': '로스트',
    'find': '파인드', 'finding': '파인딩', 'found': '파운드',
    'send': '센드', 'sending': '센딩', 'sent': '센트',
    'spend': '스펜드', 'spending': '스펜딩', 'spent': '스펜트',
    'build': '빌드', 'building': '빌딩', 'built': '빌트',

    // 감각/인지 동사
    'see': '씨', 'seeing': '씨잉', 'saw': '쏘', 'seen': '씬',
    'look': '룩', 'looking': '루킹', 'looked': '룩트',
    'watch': '와치', 'watching': '와칭', 'watched': '와치트',
    'hear': '히어', 'hearing': '히어링', 'heard': '허드',
    'listen': '리슨', 'listening': '리스닝', 'listened': '리슨드',
    'feel': '필', 'feeling': '필링', 'felt': '펠트',
    'touch': '터치', 'touching': '터칭', 'touched': '터치트',
    'taste': '테이스트', 'tasting': '테이스팅', 'tasted': '테이스티드',
    'smell': '스멜', 'smelling': '스멜링', 'smelled': '스멜드',

    // 사고/의사 동사
    'know': '노우', 'knowing': '노잉', 'knew': '뉴', 'known': '노운',
    'think': '씽크', 'thinking': '씽킹', 'thought': '쏘트',
    'believe': '빌리브', 'believing': '빌리빙', 'believed': '빌리브드',
    'understand': '언더스탠드', 'understanding': '언더스탠딩', 'understood': '언더스투드',
    'remember': '리멤버', 'remembering': '리멤버링', 'remembered': '리멤버드',
    'forget': '포겟', 'forgetting': '포게팅', 'forgot': '포갓', 'forgotten': '포가튼',
    'mean': '민', 'meaning': '미닝', 'meant': '멘트',
    'realize': '리얼라이즈', 'realizing': '리얼라이징', 'realized': '리얼라이즈드',
    'notice': '노티스', 'noticing': '노티싱', 'noticed': '노티스트',
    'recognize': '레커그나이즈', 'recognized': '레커그나이즈드',
    'imagine': '이매진', 'imagining': '이매지닝', 'imagined': '이매진드',
    'wonder': '원더', 'wondering': '원더링', 'wondered': '원더드',
    'guess': '게스', 'guessing': '게싱', 'guessed': '게스트',
    'hope': '호프', 'hoping': '호핑', 'hoped': '호프트',
    'wish': '위시', 'wishing': '위싱', 'wished': '위시트',
    'want': '원트', 'wanting': '원팅', 'wanted': '원티드',
    'need': '니드', 'needing': '니딩', 'needed': '니디드',
    'expect': '익스펙트', 'expecting': '익스펙팅', 'expected': '익스펙티드',
    'decide': '디사이드', 'deciding': '디사이딩', 'decided': '디사이디드',
    'choose': '추즈', 'choosing': '추징', 'chose': '초즈', 'chosen': '초즌',
    'prefer': '프리퍼', 'preferring': '프리퍼링', 'preferred': '프리퍼드',

    // 감정/상태 동사
    'love': '러브', 'loving': '러빙', 'loved': '러브드',
    'like': '라이크', 'liking': '라이킹', 'liked': '라이크트',
    'hate': '헤이트', 'hating': '헤이팅', 'hated': '헤이티드',
    'enjoy': '인조이', 'enjoying': '인조잉', 'enjoyed': '인조이드',
    'care': '케어', 'caring': '케어링', 'cared': '케어드',
    'worry': '워리', 'worrying': '워리잉', 'worried': '워리드',
    'fear': '피어', 'fearing': '피어링', 'feared': '피어드',
    'miss': '미스', 'missing': '미싱', 'missed': '미스트',
    'mind': '마인드', 'minding': '마인딩', 'minded': '마인디드',

    // 의사소통 동사
    'say': '세이', 'saying': '세잉', 'said': '세드',
    'tell': '텔', 'telling': '텔링', 'told': '톨드',
    'speak': '스피크', 'speaking': '스피킹', 'spoke': '스포크', 'spoken': '스포큰',
    'talk': '톡', 'talking': '토킹', 'talked': '톡트',
    'ask': '애스크', 'asking': '애스킹', 'asked': '애스크트',
    'answer': '앤서', 'answering': '앤서링', 'answered': '앤서드',
    'reply': '리플라이', 'replying': '리플라잉', 'replied': '리플라이드',
    'call': '콜', 'calling': '콜링', 'called': '콜드',
    'shout': '샤웃', 'shouting': '샤우팅', 'shouted': '샤우티드',
    'whisper': '위스퍼', 'whispering': '위스퍼링', 'whispered': '위스퍼드',
    'explain': '익스플레인', 'explaining': '익스플레이닝', 'explained': '익스플레인드',
    'describe': '디스크라이브', 'describing': '디스크라이빙', 'described': '디스크라이브드',
    'mention': '멘션', 'mentioning': '멘셔닝', 'mentioned': '멘션드',

    // 변화 동사
    'become': '비컴', 'becoming': '비커밍', 'became': '비케임',
    'change': '체인지', 'changing': '체인징', 'changed': '체인지드',
    'turn': '턴', 'turning': '터닝', 'turned': '턴드',
    'grow': '그로우', 'growing': '그로잉', 'grew': '그루', 'grown': '그로운',
    'develop': '디벨럽', 'developing': '디벨러핑', 'developed': '디벨럽트',
    'improve': '임프루브', 'improving': '임프루빙', 'improved': '임프루브드',
    'increase': '인크리스', 'increasing': '인크리싱', 'increased': '인크리스트',
    'decrease': '디크리스', 'decreasing': '디크리싱', 'decreased': '디크리스트',
    'rise': '라이즈', 'rising': '라이징', 'rose': '로즈', 'risen': '리즌',
    'fall': '폴', 'falling': '폴링', 'fell': '펠', 'fallen': '폴른',
    'drop': '드랍', 'dropping': '드라핑', 'dropped': '드랍트',

    // 시작/끝 동사
    'start': '스타트', 'starting': '스타팅', 'started': '스타티드',
    'begin': '비긴', 'beginning': '비기닝', 'began': '비갠', 'begun': '비건',
    'stop': '스탑', 'stopping': '스타핑', 'stopped': '스탑트',
    'end': '엔드', 'ending': '엔딩', 'ended': '엔디드',
    'finish': '피니시', 'finishing': '피니싱', 'finished': '피니시트',
    'continue': '컨티뉴', 'continuing': '컨티뉴잉', 'continued': '컨티뉴드',
    'quit': '퀴트', 'quitting': '퀴팅',

    // 기타 동사
    'stay': '스테이', 'staying': '스테잉', 'stayed': '스테이드',
    'wait': '웨이트', 'waiting': '웨이팅', 'waited': '웨이티드',
    'stand': '스탠드', 'standing': '스탠딩', 'stood': '스투드',
    'sit': '싯', 'sitting': '시팅', 'sat': '샛',
    'lie': '라이', 'lying': '라잉', 'lay': '레이', 'lain': '레인',
    'sleep': '슬립', 'sleeping': '슬리핑', 'slept': '슬렙트',
    'wake': '웨이크', 'waking': '웨이킹', 'woke': '워크', 'woken': '워큰',
    'live': '리브', 'living': '리빙', 'lived': '리브드',
    'die': '다이', 'dying': '다잉', 'died': '다이드',
    'kill': '킬', 'killing': '킬링', 'killed': '킬드',
    'save': '세이브', 'saving': '세이빙', 'saved': '세이브드',
    'help': '헬프', 'helping': '헬핑', 'helped': '헬프트',
    'try': '트라이', 'trying': '트라잉', 'tried': '트라이드',
    'use': '유즈', 'using': '유징', 'used': '유즈드',
    'work': '워크', 'working': '워킹', 'worked': '워크트',
    'play': '플레이', 'playing': '플레잉', 'played': '플레이드',
    'show': '쇼', 'showing': '쇼잉', 'showed': '쇼드', 'shown': '쇼운',
    'open': '오픈', 'opening': '오프닝', 'opened': '오픈드',
    'close': '클로즈', 'closing': '클로징', 'closed': '클로즈드',
    'write': '라이트', 'writing': '라이팅', 'wrote': '로트', 'written': '리튼',
    'read': '리드', 'reading': '리딩',
    'draw': '드로', 'drawing': '드로잉', 'drew': '드루', 'drawn': '드론',
    'sing': '싱', 'singing': '싱잉', 'sang': '생', 'sung': '성',
    'dance': '댄스', 'dancing': '댄싱', 'danced': '댄스트',
    'smile': '스마일', 'smiling': '스마일링', 'smiled': '스마일드',
    'laugh': '래프', 'laughing': '래핑', 'laughed': '래프트',
    'cry': '크라이', 'crying': '크라잉', 'cried': '크라이드',
    'break': '브레이크', 'breaking': '브레이킹', 'broke': '브로크', 'broken': '브로큰',
    'cut': '컷', 'cutting': '커팅',
    'hit': '힛', 'hitting': '히팅',
    'push': '푸시', 'pushing': '푸싱', 'pushed': '푸시트',
    'pull': '풀', 'pulling': '풀링', 'pulled': '풀드',
    'throw': '쓰로우', 'throwing': '쓰로잉', 'threw': '쓰루', 'thrown': '쓰로운',
    'wear': '웨어', 'wearing': '웨어링', 'wore': '워', 'worn': '워른',
    'carry': '캐리', 'carrying': '캐리잉', 'carried': '캐리드',
    'move': '무브', 'moving': '무빙', 'moved': '무브드',
    'pass': '패스', 'passing': '패싱', 'passed': '패스트',
    'reach': '리치', 'reaching': '리칭', 'reached': '리치트',
    'follow': '팔로우', 'following': '팔로잉', 'followed': '팔로우드',
    'lead': '리드', 'leading': '리딩', 'led': '레드',
    'meet': '밋', 'meeting': '미팅', 'met': '멧',
    'join': '조인', 'joining': '조이닝', 'joined': '조인드',
    'happen': '해픈', 'happening': '해프닝', 'happened': '해픈드',
    'seem': '심', 'seeming': '시밍', 'seemed': '심드',
    'appear': '어피어', 'appearing': '어피어링', 'appeared': '어피어드',

    // 관사/접속사/전치사
    'the': '더', 'a': '어', 'an': '앤',
    'and': '앤드', 'or': '오어', 'but': '벗', 'so': '소', 'yet': '옛',
    'because': '비코즈', 'if': '이프', 'unless': '언레스', 'although': '올도',
    'though': '도', 'while': '와일', 'since': '신스', 'until': '언틸',
    'when': '웬', 'where': '웨어', 'as': '애즈', 'than': '댄',
    'in': '인', 'on': '온', 'at': '앳', 'to': '투', 'for': '포', 'from': '프롬',
    'with': '위드', 'without': '위다웃', 'of': '오브', 'by': '바이',
    'about': '어바웃', 'into': '인투', 'through': '쓰루', 'throughout': '쓰루아웃',
    'over': '오버', 'under': '언더', 'above': '어보브', 'below': '빌로우',
    'between': '비트윈', 'among': '어멍', 'behind': '비하인드',
    'before': '비포', 'after': '애프터', 'during': '듀어링',
    'across': '어크로스', 'against': '어겐스트', 'along': '얼롱',
    'beside': '비사이드', 'besides': '비사이즈', 'beyond': '비욘드',
    'inside': '인사이드', 'outside': '아웃사이드',
    'near': '니어', 'off': '오프', 'toward': '투워드', 'towards': '투워즈',
    'upon': '어폰', 'within': '위딘',

    // 의문사
    'what': '왓', 'when': '웬', 'where': '웨어', 'who': '후', "who's": '후즈',
    'whom': '훔', 'why': '와이', 'how': '하우', 'which': '위치', 'whose': '후즈', 'whatever': '왓에버',

    // 지시대명사/한정사
    'this': '디스', 'that': '댓', 'these': '디즈', 'those': '도즈',
    'such': '서치', 'same': '세임', 'other': '아더', 'another': '어나더',

    // 부사
    'here': '히어', 'there': '데어', 'everywhere': '에브리웨어', 'somewhere': '썸웨어',
    'anywhere': '에니웨어', 'nowhere': '노웨어',
    'now': '나우', 'then': '덴', 'today': '투데이', 'tonight': '투나잇',
    'tomorrow': '투모로우', 'yesterday': '예스터데이',
    'never': '네버', 'ever': '에버', 'always': '올웨이즈', 'forever': '포에버',
    'sometimes': '섬타임즈', 'often': '오픈', 'usually': '유주얼리', 'rarely': '레얼리',
    'seldom': '셀덤', 'hardly': '하들리', 'barely': '베얼리',
    'again': '어겐', 'once': '원스', 'twice': '트와이스',
    'just': '저스트', 'only': '온리', 'even': '이븐', 'still': '스틸',
    'already': '올레디', 'yet': '옛', 'almost': '올모스트', 'nearly': '니얼리',
    'too': '투', 'also': '올소', 'either': '아이더', 'neither': '나이더',
    'very': '베리', 'really': '리얼리', 'quite': '콰잇', 'rather': '래더',
    'pretty': '프리티', 'fairly': '페얼리', 'extremely': '익스트림리',
    'completely': '컴플리틀리', 'totally': '토탈리', 'absolutely': '앱솔루틀리',
    'perfectly': '퍼펙틀리', 'entirely': '인타이얼리',
    'enough': '이너프', 'more': '모어', 'most': '모스트', 'less': '레스', 'least': '리스트',
    'much': '머치', 'many': '메니', 'few': '퓨', 'little': '리틀',
    'several': '세버럴', 'some': '썸', 'any': '에니', 'no': '노', 'none': '논',
    'all': '올', 'both': '보쓰', 'each': '이치', 'every': '에브리',
    'up': '업', 'down': '다운', 'out': '아웃', 'in': '인',
    'away': '어웨이', 'back': '백', 'forward': '포워드', 'backward': '백워드',
    'around': '어라운드', 'together': '투게더', 'apart': '어파트', 'alone': '얼로운',
    'fast': '패스트', 'slow': '슬로우', 'slowly': '슬로울리', 'quickly': '퀵클리',
    'suddenly': '서든리', 'immediately': '이미디에틀리', 'finally': '파이널리',
    'lately': '레이틀리', 'recently': '리센틀리', 'currently': '커런틀리',
    'probably': '프라버블리', 'possibly': '파서블리', 'certainly': '서튼리',
    'definitely': '데피니틀리', 'maybe': '메이비', 'perhaps': '퍼햅스',

    // 형용사
    'good': '굿', 'better': '베터', 'best': '베스트',
    'bad': '배드', 'worse': '워스', 'worst': '워스트',
    'great': '그레이트', 'fine': '파인', 'nice': '나이스', 'wonderful': '원더풀',
    'excellent': '익셀런트', 'perfect': '퍼펙트', 'amazing': '어메이징',
    'terrible': '테러블', 'awful': '오풀', 'horrible': '호러블',
    'big': '빅', 'large': '라지', 'huge': '휴지', 'giant': '자이언트',
    'small': '스몰', 'little': '리틀', 'tiny': '타이니',
    'long': '롱', 'short': '숏', 'tall': '톨',
    'high': '하이', 'low': '로우', 'deep': '딥', 'shallow': '샬로우',
    'wide': '와이드', 'narrow': '내로우', 'thick': '띡', 'thin': '띤',
    'heavy': '헤비', 'light': '라이트', 'strong': '스트롱', 'weak': '위크',
    'hard': '하드', 'soft': '소프트', 'tough': '터프', 'gentle': '젠틀',
    'hot': '핫', 'warm': '워름', 'cool': '쿨', 'cold': '콜드', 'freezing': '프리징',
    'new': '뉴', 'old': '올드', 'young': '영', 'ancient': '에인션트', 'modern': '마던',
    'early': '얼리', 'late': '레이트',
    'fast': '패스트', 'quick': '퀵', 'slow': '슬로우',
    'easy': '이지', 'simple': '심플', 'hard': '하드', 'difficult': '디피컬트',
    'right': '라잇', 'wrong': '롱', 'correct': '커렉트', 'incorrect': '인커렉트',
    'true': '트루', 'false': '폴스', 'real': '리얼', 'fake': '페이크',
    'beautiful': '뷰티풀', 'pretty': '프리티', 'handsome': '핸섬', 'ugly': '어글리',
    'clean': '클린', 'dirty': '더티', 'clear': '클리어', 'dark': '다크',
    'bright': '브라이트', 'full': '풀', 'empty': '엠티', 'complete': '컴플리트',
    'happy': '해피', 'sad': '새드', 'glad': '글래드', 'sorry': '쏘리',
    'angry': '앵그리', 'mad': '매드', 'crazy': '크레이지',
    'afraid': '어프레이드', 'scared': '스케어드', 'brave': '브레이브',
    'lonely': '론리', 'alone': '얼로운', 'together': '투게더',
    'busy': '비지', 'free': '프리', 'ready': '레디',
    'safe': '세이프', 'dangerous': '데인저러스',
    'important': '임포턴트', 'special': '스페셜', 'usual': '유주얼',
    'different': '디퍼런트', 'same': '세임', 'similar': '시밀러',
    'strange': '스트레인지', 'weird': '위어드', 'normal': '노멀',
    'sure': '슈어', 'certain': '서튼', 'possible': '파서블', 'impossible': '임파서블',
    'necessary': '네서서리', 'comfortable': '컴퍼터블', 'uncomfortable': '언컴퍼터블',

    // 명사
    'time': '타임', 'day': '데이', 'week': '위크', 'month': '먼쓰', 'year': '이어',
    'moment': '모먼트', 'second': '세컨드', 'minute': '미닛', 'hour': '아워',
    'morning': '모닝', 'afternoon': '애프터눈', 'evening': '이브닝', 'night': '나잇',
    'today': '투데이', 'tomorrow': '투모로우', 'yesterday': '예스터데이',
    'way': '웨이', 'road': '로드', 'path': '패쓰', 'street': '스트리트',
    'thing': '씽', 'things': '씽즈', 'stuff': '스터프',
    'life': '라이프', 'death': '데쓰', 'world': '월드', 'place': '플레이스',
    'man': '맨', 'woman': '우먼', 'people': '피플', 'person': '퍼슨',
    'boy': '보이', 'girl': '걸', 'baby': '베이비', 'child': '차일드', 'children': '칠드런',
    'friend': '프렌드', 'friends': '프렌즈', 'family': '패밀리',
    'mother': '마더', 'father': '파더', 'parent': '페어런트',
    'brother': '브라더', 'sister': '시스터',
    'hand': '핸드', 'hands': '핸즈', 'finger': '핑거', 'fingers': '핑거즈',
    'arm': '암', 'arms': '암즈', 'leg': '레그', 'legs': '레그즈', 'foot': '풋', 'feet': '피트',
    'eye': '아이', 'eyes': '아이즈', 'ear': '이어', 'ears': '이어즈',
    'nose': '노즈', 'mouth': '마우쓰', 'face': '페이스',
    'head': '헤드', 'hair': '헤어', 'neck': '넥',
    'body': '바디', 'heart': '하트', 'soul': '소울', 'mind': '마인드', 'brain': '브레인',
    'home': '홈', 'house': '하우스', 'room': '룸', 'door': '도어', 'window': '윈도우',
    'floor': '플로어', 'wall': '월', 'roof': '루프',
    'bed': '베드', 'table': '테이블', 'chair': '체어',
    'car': '카', 'bus': '버스', 'train': '트레인', 'plane': '플레인', 'ship': '쉽',
    'phone': '폰', 'computer': '컴퓨터', 'book': '북', 'paper': '페이퍼',
    'pen': '펜', 'pencil': '펜슬',
    'water': '워터', 'food': '푸드', 'drink': '드링크',
    'fire': '파이어', 'air': '에어', 'earth': '어쓰',
    'sun': '선', 'moon': '문', 'star': '스타', 'stars': '스타즈',
    'sky': '스카이', 'cloud': '클라우드', 'clouds': '클라우즈', 'rain': '레인',
    'wind': '윈드', 'snow': '스노우',
    'tree': '트리', 'trees': '트리즈', 'flower': '플라워', 'flowers': '플라워즈',
    'color': '컬러', 'light': '라이트', 'shadow': '새도우',
    'sound': '사운드', 'music': '뮤직', 'song': '송', 'voice': '보이스',
    'name': '네임', 'number': '넘버', 'word': '워드', 'words': '워즈',
    'letter': '레터', 'line': '라인', 'story': '스토리',
    'question': '퀘스쳔', 'answer': '앤서', 'problem': '프라블럼', 'solution': '솔루션',
    'idea': '아이디어', 'thought': '쏘트', 'dream': '드림', 'memory': '메모리',
    'feeling': '필링', 'emotion': '이모션',
    'part': '파트', 'piece': '피스', 'side': '사이드',
    'top': '탑', 'bottom': '바텀', 'middle': '미들',
    'beginning': '비기닝', 'end': '엔드', 'start': '스타트', 'finish': '피니시',
    'chance': '챈스', 'choice': '초이스', 'decision': '디시전',
    'reason': '리즌', 'cause': '코즈', 'result': '리절트', 'effect': '이펙트',
    'fact': '팩트', 'truth': '트루쓰', 'lie': '라이',

    // 기타 자주 쓰이는 단어
    'oh': '오', 'yeah': '예', 'yes': '예스', 'no': '노', 'okay': '오케이', 'ok': '오케이',
    'please': '플리즈', 'thanks': '땡스', 'thank': '땡크',
    'hello': '헬로', 'hi': '하이', 'hey': '헤이', 'goodbye': '굿바이', 'bye': '바이',
    'nothing': '너씽', 'something': '썸씽', 'everything': '에브리씽', 'anything': '에니씽',
    'someone': '썸원', 'everyone': '에브리원', 'anyone': '에니원', 'no one': '노원',
    'one': '원', 'two': '투', 'three': '쓰리', 'four': '포', 'five': '파이브',
    'six': '식스', 'seven': '세븐', 'eight': '에잇', 'nine': '나인', 'ten': '텐',
    'hundred': '헌드레드', 'thousand': '싸우전드', 'million': '밀리언',
    'first': '퍼스트', 'second': '세컨드', 'third': '써드',
    'last': '래스트', 'next': '넥스트', 'previous': '프리비어스',
    'gonna': '고나', 'wanna': '워나', 'gotta': '가라',
    'cause': '코즈', "'cause": '코즈', 'cuz': '커즈',

    // 추가 노래 관련 단어
    'blush': '블러쉬', 'trouble': '트러블', 'pain': '페인',
    'tear': '티어', 'tears': '티어즈', 'kiss': '키스', 'hug': '허그',
    'touch': '터치', 'hold': '홀드', 'embrace': '임브레이스',
};

// 발음 규칙 패턴
const pronunciationRules = {
    // 접미사
    'tion': '션',
    'sion': '전',
    'able': '어블',
    'ible': '어블',
    'ful': '풀',
    'less': '레스',
    'ness': '네스',
    'ment': '먼트',
    'ly': '리',

    // 이중 모음
    'oo': '우',
    'ee': '이',
    'ea': '이',
    'ai': '에이',
    'ay': '에이',
    'oa': '오',
    'ow': '오',
    'ou': '아우',
    'oi': '오이',
    'oy': '오이',

    // 자음 조합
    'th': '쓰',
    'sh': '쉬',
    'ch': '치',
    'ph': '프',
    'wh': '웨',
    'ng': '잉',
    'ck': '크',
};

// API 캐시 (LocalStorage 사용)
const apiCache = {
    get: (word) => {
        try {
            const cached = localStorage.getItem(`pronunciation_${word}`);
            return cached ? JSON.parse(cached) : null;
        } catch (e) {
            return null;
        }
    },
    set: (word, pronunciation) => {
        try {
            localStorage.setItem(`pronunciation_${word}`, JSON.stringify(pronunciation));
        } catch (e) {
            // 저장 실패 시 무시
        }
    }
};

// IPA to 한글 변환 매핑
const ipaToKorean = {
    // 모음
    'iː': '이', 'ɪ': '이', 'i': '이',
    'uː': '우', 'ʊ': '우', 'u': '우',
    'eɪ': '에이', 'e': '에', 'ɛ': '에',
    'oʊ': '오', 'əʊ': '오', 'ɔː': '오', 'ɔ': '오', 'o': '오',
    'aɪ': '아이', 'aʊ': '아우', 'ɔɪ': '오이',
    'ə': '어', 'ɜː': '어', 'ʌ': '어', 'ɑː': '아', 'æ': '애', 'a': '아',

    // 자음
    'p': '프', 'b': '브', 't': '트', 'd': '드', 'k': '크', 'g': '그',
    'f': '프', 'v': '브', 'θ': '쓰', 'ð': '드', 's': '스', 'z': '즈',
    'ʃ': '쉬', 'ʒ': '즈', 'h': '흐',
    'tʃ': '치', 'dʒ': '즈',
    'm': '므', 'n': '느', 'ŋ': '잉',
    'l': '르', 'r': '르', 'w': '우', 'j': '이',
};

// IPA를 한글로 변환
function convertIPAToKorean(ipa) {
    if (!ipa) return null;

    // IPA 기호 정리 (/, /, ', 등 제거)
    let cleaned = ipa.replace(/[\/\[\]ˈˌ]/g, '');

    let result = '';
    let i = 0;

    while (i < cleaned.length) {
        let matched = false;

        // 긴 패턴부터 매칭 (2글자)
        if (i < cleaned.length - 1) {
            const twoChar = cleaned.substr(i, 2);
            if (ipaToKorean[twoChar]) {
                result += ipaToKorean[twoChar];
                i += 2;
                matched = true;
            }
        }

        // 1글자 매칭
        if (!matched) {
            const oneChar = cleaned[i];
            if (ipaToKorean[oneChar]) {
                result += ipaToKorean[oneChar];
                i++;
            } else {
                // 매칭 안되는 문자는 건너뛰기
                i++;
            }
        }
    }

    return result || null;
}

// Python 발음 변환 서버에서 발음 가져오기 (최우선)
async function fetchPronunciationFromPython(word) {
    try {
        const response = await fetch('http://localhost:5001/transliterate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: word,
                word_mode: true
            })
        });

        if (!response.ok) {
            return null;
        }

        const data = await response.json();

        if (data && data.success && data.transliteration) {
            return data.transliteration;
        }

        return null;
    } catch (error) {
        // Python 서버가 실행 중이 아닐 수 있으므로 조용히 실패
        return null;
    }
}

// Dictionary API에서 발음 가져오기
async function fetchPronunciationFromAPI(word) {
    try {
        const response = await fetch(`https://api.dictionaryapi.dev/api/v2/entries/en/${encodeURIComponent(word)}`);

        if (!response.ok) {
            return null;
        }

        const data = await response.json();

        if (data && data[0] && data[0].phonetics) {
            // phonetics 배열에서 IPA 찾기
            for (const phonetic of data[0].phonetics) {
                if (phonetic.text) {
                    const koreanPronunciation = convertIPAToKorean(phonetic.text);
                    if (koreanPronunciation) {
                        return koreanPronunciation;
                    }
                }
            }
        }

        return null;
    } catch (error) {
        console.warn(`API 호출 실패 (${word}):`, error);
        return null;
    }
}

// 메인 변환 함수 (비동기)
async function convertToPronunciationAsync(text) {
    if (!text) return '';

    const lines = text.split('\n');
    const convertedLines = await Promise.all(lines.map(line => convertLineAsync(line)));

    return convertedLines.join('\n');
}

// 메인 변환 함수 (동기 - 기존 호환성)
function convertToPronunciation(text) {
    if (!text) return '';

    const lines = text.split('\n');
    const convertedLines = lines.map(line => convertLine(line));

    return convertedLines.join('\n');
}

// 한 줄씩 변환 (비동기)
async function convertLineAsync(line) {
    if (!line.trim()) return '';

    const words = line.split(/\s+/);
    const convertedWords = await Promise.all(words.map(word => convertWordAsync(word)));

    return convertedWords.join(' ');
}

// 한 줄씩 변환 (동기)
function convertLine(line) {
    if (!line.trim()) return '';

    const words = line.split(/\s+/);
    const convertedWords = words.map(word => convertWord(word));

    return convertedWords.join(' ');
}

// 단어 변환 (비동기 - 5단계 폴백 시스템)
async function convertWordAsync(word) {
    if (!word) return '';

    // 구두점 분리
    const match = word.match(/^([^a-zA-Z']*)([a-zA-Z']+)([^a-zA-Z']*)$/);

    if (!match) return word;

    const [, prefix, mainWord, suffix] = match;
    const lowerWord = mainWord.toLowerCase();

    // 1단계: 단어 사전에서 찾기 (1000+ 단어, 즉시 응답)
    if (commonWords[lowerWord]) {
        return prefix + commonWords[lowerWord] + suffix;
    }

    // 2단계: 캐시에서 찾기 (이전에 조회한 단어)
    const cached = apiCache.get(lowerWord);
    if (cached) {
        return prefix + cached + suffix;
    }

    // 3단계: Python 발음 변환 서버 (규칙 기반, 빠르고 정확)
    const pythonResult = await fetchPronunciationFromPython(lowerWord);
    if (pythonResult) {
        apiCache.set(lowerWord, pythonResult);
        return prefix + pythonResult + suffix;
    }

    // 4단계: Dictionary API + IPA 변환 (외부 API)
    const apiResult = await fetchPronunciationFromAPI(lowerWord);
    if (apiResult) {
        apiCache.set(lowerWord, apiResult);
        return prefix + apiResult + suffix;
    }

    // 5단계: 규칙 기반 폴백 (최후의 수단)
    const ruleResult = convertByRules(lowerWord);
    return prefix + ruleResult + suffix;
}

// 단어 변환 (동기 - 기존 방식)
function convertWord(word) {
    if (!word) return '';

    // 구두점 분리
    const match = word.match(/^([^a-zA-Z']*)([a-zA-Z']+)([^a-zA-Z']*)$/);

    if (!match) return word;

    const [, prefix, mainWord, suffix] = match;
    const lowerWord = mainWord.toLowerCase();

    // 1. 단어 사전에서 찾기
    if (commonWords[lowerWord]) {
        return prefix + commonWords[lowerWord] + suffix;
    }

    // 2. 캐시에서 찾기 (동기)
    const cached = apiCache.get(lowerWord);
    if (cached) {
        return prefix + cached + suffix;
    }

    // 3. 발음 규칙 적용
    return prefix + convertByRules(lowerWord) + suffix;
}

// 규칙 기반 변환
function convertByRules(word) {
    let result = word;

    // 접미사 패턴 매칭
    for (const [pattern, replacement] of Object.entries(pronunciationRules)) {
        if (word.endsWith(pattern)) {
            const base = word.slice(0, -pattern.length);
            const basePronunciation = convertBySimpleRules(base);
            return basePronunciation + replacement;
        }
    }

    // 이중 모음/자음 패턴 매칭
    for (const [pattern, replacement] of Object.entries(pronunciationRules)) {
        if (word.includes(pattern)) {
            result = result.replace(new RegExp(pattern, 'g'), replacement);
        }
    }

    // 기본 자모 변환
    return convertBySimpleRules(result);
}

// 간단한 규칙 기반 변환
function convertBySimpleRules(word) {
    const vowelMap = {
        'a': '아', 'e': '에', 'i': '이', 'o': '오', 'u': '우'
    };

    const consonantMap = {
        'b': '브', 'c': '크', 'd': '드', 'f': '프', 'g': '그',
        'h': '흐', 'j': '즈', 'k': '크', 'l': '르', 'm': '므',
        'n': '느', 'p': '프', 'r': '르', 's': '스',
        't': '트', 'v': '브', 'w': '우', 'y': '이', 'z': '즈'
    };

    let pronunciation = '';
    for (let i = 0; i < word.length; i++) {
        const char = word[i].toLowerCase();
        if (vowelMap[char]) {
            pronunciation += vowelMap[char];
        } else if (consonantMap[char]) {
            pronunciation += consonantMap[char];
        } else {
            pronunciation += char;
        }
    }

    return pronunciation || word;
}

// 가사 전체 변환
function convertLyricsWithLineNumbers(lyrics) {
    return convertToPronunciation(lyrics);
}
