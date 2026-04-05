/**
 * app.js — Reading Reviews frontend scripts
 *
 * Uses event delegation so it works for any delete form rendered
 * on the page, including those added dynamically in the future.
 */

document.addEventListener('DOMContentLoaded', function () {
    // ----------------------------------------------------------------
    // Delete confirmation: any form with data-confirm="..." will prompt
    // the user before submitting.
    // ----------------------------------------------------------------
    document.addEventListener('submit', function (event) {
        var form = event.target;
        if (!form.matches('form[data-confirm]')) {
            return;
        }
        var message = form.getAttribute('data-confirm');
        if (!confirm(message)) {
            event.preventDefault();
        }
    });

    // ----------------------------------------------------------------
    // OpenLibrary search on the Add Book page.
    // Fetches /books/search-ol?q=... and renders result cards.
    // Clicking "Use this book" pre-fills the form fields below.
    // ----------------------------------------------------------------
    var searchBtn = document.getElementById('ol-search-btn');
    if (!searchBtn) return;  // only runs on the Add Book page

    var searchInput  = document.getElementById('ol-search-query');
    var resultsBox   = document.getElementById('ol-results');

    function renderResults(results) {
        resultsBox.innerHTML = '';

        if (results.length === 0) {
            resultsBox.innerHTML = '<p class="text-muted mb-0">No results found.</p>';
            resultsBox.style.display = 'block';
            return;
        }

        var cards = results.map(function (book, i) {
            var coverHtml = book.cover_url
                ? '<img src="' + book.cover_url + '" alt="Cover" class="rounded" style="width:60px;height:90px;object-fit:cover;">'
                : '<div class="rounded bg-light d-flex align-items-center justify-content-center text-muted" style="width:60px;height:90px;font-size:0.7rem;">No cover</div>';

            return '<div class="d-flex align-items-start gap-3 p-2 border rounded mb-2">'
                + coverHtml
                + '<div class="flex-grow-1">'
                + '<div class="fw-semibold">' + escapeHtml(book.title) + '</div>'
                + '<div class="text-muted small">' + escapeHtml(book.author) + '</div>'
                + (book.isbn ? '<div class="text-muted small">ISBN: ' + escapeHtml(book.isbn) + '</div>' : '')
                + (book.total_pages ? '<div class="text-muted small">' + book.total_pages + ' pages</div>' : '')
                + '</div>'
                + '<button type="button" class="btn btn-sm btn-outline-success flex-shrink-0 ol-use-btn"'
                + ' data-index="' + i + '">Use</button>'
                + '</div>';
        });

        resultsBox.innerHTML = cards.join('');
        resultsBox.style.display = 'block';

        // Attach click handlers to all "Use" buttons.
        resultsBox.querySelectorAll('.ol-use-btn').forEach(function (btn) {
            btn.addEventListener('click', function () {
                var book = results[parseInt(btn.dataset.index, 10)];
                document.getElementById('title').value       = book.title  || '';
                document.getElementById('author').value      = book.author || '';
                document.getElementById('isbn').value        = book.isbn   || '';
                document.getElementById('total_pages').value = book.total_pages || '';
                document.getElementById('genre').value       = book.genre  || '';
                document.getElementById('cover_url').value   = book.cover_url  || '';
                // Scroll down to the form so the user can see the pre-filled fields.
                document.getElementById('title').scrollIntoView({ behavior: 'smooth', block: 'center' });
            });
        });
    }

    function escapeHtml(str) {
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    function doSearch() {
        var q = searchInput.value.trim();
        if (q.length < 3) {
            resultsBox.innerHTML = '<p class="text-muted mb-0">Please enter at least 3 characters.</p>';
            resultsBox.style.display = 'block';
            return;
        }

        searchBtn.disabled = true;
        searchBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Searching…';

        fetch('/books/search-ol?q=' + encodeURIComponent(q))
            .then(function (resp) { return resp.json(); })
            .then(function (data) { renderResults(data); })
            .catch(function () {
                resultsBox.innerHTML = '<p class="text-danger mb-0">Search failed. Please try again.</p>';
                resultsBox.style.display = 'block';
            })
            .finally(function () {
                searchBtn.disabled = false;
                searchBtn.innerHTML = '<i class="bi bi-search me-1"></i>Search';
            });
    }

    searchBtn.addEventListener('click', doSearch);

    // Allow pressing Enter in the search input to trigger the search.
    searchInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            doSearch();
        }
    });
});
