// 가사 페이지 메인 로직

// DOM 요소
const songTitle = document.getElementById('songTitle');
const artistName = document.getElementById('artistName');
const albumName = document.getElementById('albumName');
const loadingIndicator = document.getElementById('loadingIndicator');
const errorMessage = document.getElementById('errorMessage');
const lyricsSection = document.getElementById('lyricsSection');
const lyricsContainer = document.getElementById('lyricsContainer');
const togglePronunciationBtn = document.getElementById('togglePronunciation');

let showingPronunciation = false;

// 페이지 로드 시 실행
document.addEventListener('DOMContentLoaded', () => {
    loadLyrics();
});

// URL 파라미터에서 가사 정보 가져오기
function loadLyrics() {
    const params = new URLSearchParams(window.location.search);

    const artist = params.get('artist');
    const title = params.get('title');
    const lyrics = params.get('lyrics');

    if (!artist || !title || !lyrics) {
        showError('가사 정보를 불러올 수 없습니다.');
        return;
    }

    // 노래 정보 표시
    songTitle.textContent = title;
    artistName.textContent = artist;
    albumName.textContent = '-'; // Lyrics.ovh API는 앨범 정보를 제공하지 않음

    // 가사 표시
    displayLyrics(lyrics);
}

// 가사 표시 (원문만)
function displayLyrics(lyrics) {
    // 원문만 표시
    const lines = lyrics.split('\n');
    let html = '';

    lines.forEach((line, index) => {
        if (line.trim()) {
            html += `<div class="lyrics-line">
                <div class="original-line">${escapeHtml(line)}</div>
            </div>`;
        } else {
            html += '<div class="lyrics-line-break"></div>';
        }
    });

    lyricsContainer.innerHTML = html;

    // 가사 섹션 표시
    lyricsSection.classList.remove('hidden');
}

// 가사 표시 (원문 + 발음) - 비동기 버전
async function displayLyricsWithPronunciation(lyrics) {
    const lines = lyrics.split('\n');
    let html = '';

    // 모든 라인을 병렬로 변환
    const pronunciations = await Promise.all(
        lines.map(line => {
            if (line.trim()) {
                return convertLineAsync(line);
            }
            return Promise.resolve('');
        })
    );

    lines.forEach((line, index) => {
        if (line.trim()) {
            html += `<div class="lyrics-line">
                <div class="original-line">${escapeHtml(line)}</div>
                <div class="pronunciation-line">${escapeHtml(pronunciations[index])}</div>
            </div>`;
        } else {
            html += '<div class="lyrics-line-break"></div>';
        }
    });

    lyricsContainer.innerHTML = html;
}

// HTML 이스케이프 처리
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 발음 토글 버튼 이벤트
togglePronunciationBtn.addEventListener('click', async () => {
    showingPronunciation = !showingPronunciation;

    const params = new URLSearchParams(window.location.search);
    const lyrics = params.get('lyrics');

    if (showingPronunciation) {
        // 로딩 표시 추가
        togglePronunciationBtn.disabled = true;
        togglePronunciationBtn.textContent = '변환 중...';

        await displayLyricsWithPronunciation(lyrics);

        togglePronunciationBtn.disabled = false;
        togglePronunciationBtn.textContent = '원문만 보기';
    } else {
        displayLyrics(lyrics);
        togglePronunciationBtn.textContent = '한글 발음 보기';
    }
});

// 에러 메시지 표시
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.remove('hidden');
    loadingIndicator.classList.add('hidden');
}

// converter.js의 convertLine 함수 사용
// (converter.js가 먼저 로드되어야 함)
