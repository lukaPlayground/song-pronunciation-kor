// DOM references
var searchForm = document.getElementById('searchForm');
var searchInput = document.getElementById('searchInput');
var searchAutocomplete = document.getElementById('searchAutocomplete');
var candidatePanel = document.getElementById('candidatePanel');
var candidateList = document.getElementById('candidateList');
var statusEl = document.getElementById('status');
var resultsEl = document.getElementById('results');
var songTitleEl = document.getElementById('songTitle');
var songArtistEl = document.getElementById('songArtist');
var lyricsContainer = document.getElementById('lyricsContainer');

// Status helpers
function showStatus(msg, type) {
    statusEl.textContent = msg;
    statusEl.className = 'status ' + (type || 'loading');
    statusEl.classList.remove('hidden');
    resultsEl.classList.add('hidden');
    candidatePanel.classList.add('hidden');
}

function hideStatus() {
    statusEl.classList.add('hidden');
}

// Render lyrics lines into DOM
function renderLyrics(lines) {
    lyricsContainer.innerHTML = '';
    lines.forEach(function (line) {
        var original = line.original;
        var pronunciation = line.pronunciation;
        if (!original.trim()) {
            var br = document.createElement('div');
            br.className = 'lyric-break';
            lyricsContainer.appendChild(br);
            return;
        }
        var pair = document.createElement('div');
        pair.className = 'lyric-pair';

        var orig = document.createElement('p');
        orig.className = 'original';
        orig.textContent = original;

        var pron = document.createElement('p');
        pron.className = 'pronunciation';
        pron.textContent = pronunciation;

        pair.appendChild(orig);
        pair.appendChild(pron);
        lyricsContainer.appendChild(pair);
    });
}

// Render candidate selection panel
function renderCandidatePanel(candidates) {
    candidateList.innerHTML = '';
    candidates.forEach(function (item) {
        var li = document.createElement('li');
        li.className = 'candidate-item';

        var titleSpan = document.createElement('span');
        titleSpan.className = 'candidate-title';
        titleSpan.textContent = item.title;

        var artistSpan = document.createElement('span');
        artistSpan.className = 'candidate-artist';
        artistSpan.textContent = '\u2014 ' + item.artist;

        li.appendChild(titleSpan);
        li.appendChild(artistSpan);
        li.addEventListener('click', function () {
            candidatePanel.classList.add('hidden');
            searchLyrics(item.artist, item.title);
        });
        candidateList.appendChild(li);
    });
    hideStatus();
    candidatePanel.classList.remove('hidden');
    candidatePanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Fetch lyrics + pronunciation and render
async function searchLyrics(artist, title) {
    showStatus('가사를 검색하는 중...', 'loading');

    var lyricsResp;
    try {
        lyricsResp = await fetch('/api/lyrics', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ artist: artist, title: title })
        });
    } catch (e) {
        showStatus('네트워크 오류가 발생했습니다.', 'error');
        return;
    }

    if (lyricsResp.status === 404) {
        showStatus('가사를 찾을 수 없습니다. 다른 곡을 선택해주세요.', 'error');
        return;
    }
    if (!lyricsResp.ok) {
        showStatus('가사 검색 중 오류가 발생했습니다.', 'error');
        return;
    }

    var lyricsData = await lyricsResp.json();

    showStatus('발음을 변환하는 중...', 'loading');

    var pronResp;
    try {
        pronResp = await fetch('/api/pronunciation', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ lyrics: lyricsData.lyrics })
        });
    } catch (e) {
        showStatus('발음 변환 중 오류가 발생했습니다.', 'error');
        return;
    }

    if (!pronResp.ok) {
        showStatus('발음 변환 중 오류가 발생했습니다.', 'error');
        return;
    }

    var pronData = await pronResp.json();

    hideStatus();
    songTitleEl.textContent = title || artist;
    songArtistEl.textContent = title ? artist : '';
    renderLyrics(pronData.lines);
    resultsEl.classList.remove('hidden');
    resultsEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Autocomplete setup
setupAutocomplete({
    inputEl: searchInput,
    listEl: searchAutocomplete,
    onSelect: function (artist, title) {
        searchAutocomplete.classList.add('hidden');
        searchLyrics(artist, title);
    }
});

// Form submit: always show candidate list first
searchForm.addEventListener('submit', async function (e) {
    e.preventDefault();
    var query = searchInput.value.trim();

    if (!query) {
        showStatus('아티스트 또는 곡명을 입력해주세요.', 'error');
        return;
    }

    // Reuse autocomplete cache if same query
    var cache = getAutocompleteCache();
    var candidates;

    if (cache.key === query && cache.results.length > 0) {
        candidates = cache.results;
    } else {
        showStatus('검색 중...', 'loading');
        candidates = await apiFetchCandidates(query);
        hideStatus();
    }

    if (!candidates.length) {
        showStatus('검색 결과가 없습니다. 다른 검색어를 입력해주세요.', 'error');
        return;
    }

    renderCandidatePanel(candidates);
});
