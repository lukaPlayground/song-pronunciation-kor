(function () {
    'use strict';

    var currentCountry = 'kr';

    function initCharts(onSelect) {
        var tabs = document.querySelectorAll('.chart-tab');
        tabs.forEach(function (tab) {
            tab.addEventListener('click', function () {
                tabs.forEach(function (t) { t.classList.remove('active'); });
                tab.classList.add('active');
                currentCountry = tab.dataset.country;
                loadChart(currentCountry, onSelect);
            });
        });
        loadChart(currentCountry, onSelect);
    }

    function loadChart(country, onSelect) {
        var statusEl = document.getElementById('chartStatus');
        var listEl = document.getElementById('chartList');

        statusEl.textContent = '불러오는 중...';
        statusEl.classList.remove('hidden');
        listEl.classList.add('hidden');
        listEl.innerHTML = '';

        fetch('/api/charts?country=' + country)
            .then(function (res) { return res.json(); })
            .then(function (data) {
                var tracks = data.tracks || [];
                if (tracks.length === 0) {
                    statusEl.textContent = '차트 정보를 불러올 수 없습니다.';
                    return;
                }
                statusEl.classList.add('hidden');
                tracks.forEach(function (track) {
                    var li = document.createElement('li');
                    li.className = 'chart-item';
                    li.innerHTML =
                        '<span class="chart-rank">' + track.rank + '</span>' +
                        '<span class="chart-info">' +
                        '<span class="chart-track">' + escapeHtml(track.title) + '</span>' +
                        '<span class="chart-artist">' + escapeHtml(track.artist) + '</span>' +
                        '</span>';
                    li.addEventListener('click', function () {
                        onSelect(track.artist, track.title);
                    });
                    listEl.appendChild(li);
                });
                listEl.classList.remove('hidden');
            })
            .catch(function () {
                statusEl.textContent = '차트 정보를 불러올 수 없습니다.';
            });
    }

    function escapeHtml(str) {
        return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }

    window.initCharts = initCharts;
})();
