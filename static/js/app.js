// DOM references
const searchForm = document.getElementById('searchForm');
const artistInput = document.getElementById('artistInput');
const titleInput = document.getElementById('titleInput');
const statusEl = document.getElementById('status');
const resultsEl = document.getElementById('results');
const songTitleEl = document.getElementById('songTitle');
const songArtistEl = document.getElementById('songArtist');
const lyricsContainer = document.getElementById('lyricsContainer');

// Status helpers
function showStatus(msg, type = 'loading') {
    statusEl.textContent = msg;
    statusEl.className = `status ${type}`;
    statusEl.classList.remove('hidden');
    resultsEl.classList.add('hidden');
}

function hideStatus() {
    statusEl.classList.add('hidden');
}

// Render lyrics lines into DOM
function renderLyrics(lines) {
    lyricsContainer.innerHTML = '';

    lines.forEach(({ original, pronunciation }) => {
        if (!original.trim()) {
            const br = document.createElement('div');
            br.className = 'lyric-break';
            lyricsContainer.appendChild(br);
            return;
        }

        const pair = document.createElement('div');
        pair.className = 'lyric-pair';

        const orig = document.createElement('p');
        orig.className = 'original';
        orig.textContent = original;

        const pron = document.createElement('p');
        pron.className = 'pronunciation';
        pron.textContent = pronunciation;

        pair.appendChild(orig);
        pair.appendChild(pron);
        lyricsContainer.appendChild(pair);
    });
}

// Main search flow
async function search(artist, title) {
    showStatus('가사를 검색하는 중...', 'loading');

    // Step 1: fetch lyrics
    let lyricsResp;
    try {
        lyricsResp = await fetch('/api/lyrics', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ artist, title })
        });
    } catch {
        showStatus('네트워크 오류가 발생했습니다.', 'error');
        return;
    }

    if (lyricsResp.status === 404) {
        showStatus('가사를 찾을 수 없습니다. 아티스트명과 제목을 확인해주세요.', 'error');
        return;
    }
    if (!lyricsResp.ok) {
        showStatus('가사 검색 중 오류가 발생했습니다.', 'error');
        return;
    }

    const { lyrics } = await lyricsResp.json();

    // Step 2: get pronunciation
    showStatus('발음을 변환하는 중...', 'loading');

    let pronResp;
    try {
        pronResp = await fetch('/api/pronunciation', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ lyrics })
        });
    } catch {
        showStatus('발음 변환 중 오류가 발생했습니다.', 'error');
        return;
    }

    if (!pronResp.ok) {
        showStatus('발음 변환 중 오류가 발생했습니다.', 'error');
        return;
    }

    const { lines } = await pronResp.json();

    // Step 3: render results
    hideStatus();
    songTitleEl.textContent = title || artist;
    songArtistEl.textContent = title ? artist : '';
    renderLyrics(lines);
    resultsEl.classList.remove('hidden');
    resultsEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Form submit handler
searchForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const artist = artistInput.value.trim();
    const title = titleInput.value.trim();
    if (!artist && !title) {
        showStatus('아티스트 또는 곡명을 입력해주세요.', 'error');
        return;
    }
    search(artist, title);
});
