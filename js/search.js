// DOM 요소
const artistInput = document.getElementById('artistInput');
const titleInput = document.getElementById('titleInput');
const searchBtn = document.getElementById('searchBtn');
const loadingIndicator = document.getElementById('loadingIndicator');
const errorMessage = document.getElementById('errorMessage');
const resultsSection = document.getElementById('resultsSection');
const resultsList = document.getElementById('resultsList');

// 검색 버튼 클릭 이벤트
searchBtn.addEventListener('click', performSearch);

// 엔터키로 검색
artistInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        performSearch();
    }
});

titleInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        performSearch();
    }
});

// 검색 실행
async function performSearch() {
    const artist = artistInput.value.trim();
    const title = titleInput.value.trim();

    if (!artist || !title) {
        showError('아티스트명과 노래 제목을 모두 입력해주세요.');
        return;
    }

    clearResults();
    showLoading(true);
    hideError();

    try {
        // 가사 가져오기
        const lyrics = await fetchLyrics(artist, title);

        if (lyrics) {
            // 검색 성공 - 바로 가사 페이지로 이동
            navigateToLyrics(artist, title, lyrics);
        }

    } catch (error) {
        showError(error.message || '검색 중 오류가 발생했습니다.');
    } finally {
        showLoading(false);
    }
}

// Lyrics.ovh API로 가사 가져오기
async function fetchLyrics(artist, title) {
    const url = `https://api.lyrics.ovh/v1/${encodeURIComponent(artist)}/${encodeURIComponent(title)}`;

    try {
        const response = await fetch(url);

        if (!response.ok) {
            if (response.status === 404) {
                throw new Error('가사를 찾을 수 없습니다. 아티스트명과 제목을 확인해주세요.');
            }
            throw new Error('가사를 불러오는데 실패했습니다.');
        }

        const data = await response.json();

        if (!data.lyrics) {
            throw new Error('가사 데이터가 없습니다.');
        }

        return data.lyrics;

    } catch (error) {
        if (error.message.includes('Failed to fetch')) {
            throw new Error('네트워크 오류가 발생했습니다. 인터넷 연결을 확인해주세요.');
        }
        throw error;
    }
}

// 가사 페이지로 이동
function navigateToLyrics(artist, title, lyrics) {
    // URL 파라미터로 정보 전달
    const params = new URLSearchParams({
        artist: artist,
        title: title,
        lyrics: lyrics
    });

    window.location.href = `lyrics.html?${params.toString()}`;
}

// 로딩 표시
function showLoading(show) {
    if (show) {
        loadingIndicator.classList.remove('hidden');
    } else {
        loadingIndicator.classList.add('hidden');
    }
}

// 에러 메시지 표시
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.remove('hidden');
}

// 에러 메시지 숨기기
function hideError() {
    errorMessage.classList.add('hidden');
}

// 검색 결과 초기화
function clearResults() {
    resultsSection.classList.add('hidden');
    resultsList.innerHTML = '';
    hideError();
}
