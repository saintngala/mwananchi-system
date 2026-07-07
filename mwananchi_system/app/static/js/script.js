/**
 * Mwananchi System — front-end behaviour
 * ---------------------------------------------------------------------------
 * Vanilla JS, no build step. Split into small, independently-initialised
 * pieces so any one of them failing (e.g. no matching elements on a given
 * page) never breaks the others.
 */
document.addEventListener('DOMContentLoaded', function () {
  initDarkMode();
  initAnimatedCounters();
  initFormLoadingStates();
  initAutoDismissAlerts();
});

/* ---------------------------------------------------------------------------
   Dark mode toggle
   Preference is remembered in localStorage so it persists across visits.
   ------------------------------------------------------------------------ */
function initDarkMode() {
  var root = document.documentElement;
  var toggleBtn = document.getElementById('darkModeToggle');
  var stored = localStorage.getItem('mwn-theme');

  if (stored === 'dark' || stored === 'light') {
    root.setAttribute('data-bs-theme', stored);
  }
  updateToggleIcon();

  if (toggleBtn) {
    toggleBtn.addEventListener('click', function () {
      var current = root.getAttribute('data-bs-theme') === 'dark' ? 'dark' : 'light';
      var next = current === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-bs-theme', next);
      localStorage.setItem('mwn-theme', next);
      updateToggleIcon();
    });
  }

  function updateToggleIcon() {
    if (!toggleBtn) return;
    var icon = toggleBtn.querySelector('i');
    if (!icon) return;
    var isDark = root.getAttribute('data-bs-theme') === 'dark';
    icon.className = isDark ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
  }
}

/* ---------------------------------------------------------------------------
   Animated stat counters (home page quick-stats row)
   ------------------------------------------------------------------------ */
function initAnimatedCounters() {
  var counters = document.querySelectorAll('[data-count]');
  if (!counters.length) return;

  if (typeof IntersectionObserver === 'undefined') {
    counters.forEach(function (el) { renderFinalValue(el); });
    return;
  }

  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        animateCounter(entry.target);
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.4 });

  counters.forEach(function (el) { observer.observe(el); });

  function renderFinalValue(el) {
    var target = parseInt(el.getAttribute('data-count'), 10) || 0;
    var prefix = el.getAttribute('data-prefix') || '';
    el.textContent = prefix + target.toLocaleString();
  }

  function animateCounter(el) {
    var target = parseInt(el.getAttribute('data-count'), 10) || 0;
    var prefix = el.getAttribute('data-prefix') || '';
    var duration = 1200;
    var start = null;

    function step(timestamp) {
      if (start === null) start = timestamp;
      var progress = Math.min((timestamp - start) / duration, 1);
      var value = Math.floor(progress * target);
      el.textContent = prefix + value.toLocaleString();
      if (progress < 1) {
        window.requestAnimationFrame(step);
      } else {
        el.textContent = prefix + target.toLocaleString();
      }
    }
    window.requestAnimationFrame(step);
  }
}

/* ---------------------------------------------------------------------------
   Confirm destructive actions, then show a loading state on submit buttons.

   These two concerns live in ONE handler deliberately: they used to be two
   separate submit listeners on the same form, and event.preventDefault()
   from one listener does not stop a sibling listener from also running.
   That meant cancelling the confirm() dialog still left the submit button
   permanently disabled with a stuck spinner, because the loading-state
   listener had already fired first. Handling both in a single listener
   guarantees the loading state only ever activates once the form is
   actually going to submit.

   The data-confirm="..." attribute (rather than an inline onsubmit="")
   also keeps the page free of inline JavaScript, so it stays compatible
   with a strict Content-Security-Policy (script-src without
   'unsafe-inline') if one is added in front of it later.
   ------------------------------------------------------------------------ */
function initFormLoadingStates() {
  document.querySelectorAll('form').forEach(function (form) {
    form.addEventListener('submit', function (event) {
      var confirmMessage = form.getAttribute('data-confirm');
      if (confirmMessage && !window.confirm(confirmMessage)) {
        event.preventDefault();
        return;
      }

      if (form.checkValidity && !form.checkValidity()) return;

      var submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
      if (submitBtn && !submitBtn.disabled) {
        submitBtn.dataset.originalText = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Please wait...';
      }
    });
  });
}

/* ---------------------------------------------------------------------------
   Auto-dismiss flash messages after a few seconds
   ------------------------------------------------------------------------ */
function initAutoDismissAlerts() {
  document.querySelectorAll('.flash-container .alert').forEach(function (alert) {
    setTimeout(function () {
      if (typeof bootstrap === 'undefined') return;
      var bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      bsAlert.close();
    }, 6000);
  });
}
