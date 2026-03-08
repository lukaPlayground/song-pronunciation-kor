// Shared cache: last /api/search result
var _acCache = { key: null, results: [] };

async function apiFetchCandidates(query) {
    if (_acCache.key === query) return _acCache.results;
    try {
        var resp = await fetch('/api/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: query })
        });
        if (!resp.ok) { _acCache = { key: query, results: [] }; return []; }
        var data = await resp.json();
        _acCache = { key: query, results: data.results || [] };
        return _acCache.results;
    } catch (e) {
        return [];
    }
}

function getAutocompleteCache() { return _acCache; }

function setupAutocomplete(config) {
    // config: { inputEl, listEl, onSelect }
    var timer = null;

    config.inputEl.addEventListener('input', function () {
        clearTimeout(timer);
        var val = config.inputEl.value.trim();
        if (val.length < 2) {
            config.listEl.classList.add('hidden');
            return;
        }
        timer = setTimeout(async function () {
            var candidates = await apiFetchCandidates(val);
            renderAutocompleteItems(config.listEl, candidates, config.onSelect);
        }, 300);
    });

    config.inputEl.addEventListener('blur', function () {
        setTimeout(function () { config.listEl.classList.add('hidden'); }, 150);
    });
}

function renderAutocompleteItems(listEl, candidates, onSelect) {
    listEl.innerHTML = '';
    if (!candidates.length) {
        listEl.classList.add('hidden');
        return;
    }
    candidates.slice(0, 5).forEach(function (item) {
        var li = document.createElement('li');
        li.className = 'autocomplete-item';
        li.textContent = item.title + ' \u2014 ' + item.artist;
        li.addEventListener('mousedown', function (e) {
            e.preventDefault();
            listEl.classList.add('hidden');
            onSelect(item.artist, item.title);
        });
        listEl.appendChild(li);
    });
    listEl.classList.remove('hidden');
}
