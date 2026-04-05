/**
 * app.js — Reading Reviews frontend scripts
 *
 * Uses event delegation so it works for any delete form rendered
 * on the page, including those added dynamically in the future.
 */

document.addEventListener('DOMContentLoaded', function () {
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
});
