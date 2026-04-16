/**
 * visualizer.js — Renovation Cost Estimator
 * Bat Iso-84, Vaucluse
 * Pure vanilla JS, no external dependencies.
 */

(function () {
  'use strict';

  /* ─────────────────────────────────────────────
     Constants
  ───────────────────────────────────────────── */

  const AID_RATES = {
    isolation: 0.40,
    toiture:   0.15,
    facade:    0.35,
    pac:       0.45,
    photo:     0.20,
    plomb:     0.10,
  };

  const SERVICE_ICONS = {
    isolation: '🏠',
    toiture:   '🔨',
    facade:    '🎨',
    pac:       '♨️',
    photo:     '☀️',
    plomb:     '🔧',
  };

  const EASING = (t) => 1 - Math.pow(1 - t, 3); // easeOutCubic
  const ANIM_DURATION = 600; // ms for count-up

  /* ─────────────────────────────────────────────
     DOM references (populated on DOMContentLoaded)
  ───────────────────────────────────────────── */

  let uploadZone, fileInput, placeholder, imgEl, badgesContainer;
  let checksContainer, resultPanel, vrTotal, vrAid, vrNet, vizCta;
  let imageLoaded = false;

  /* ─────────────────────────────────────────────
     Initialisation
  ───────────────────────────────────────────── */

  function init() {
    uploadZone      = document.getElementById('viz-upload');
    fileInput       = document.getElementById('viz-input');
    placeholder     = document.getElementById('viz-placeholder');
    imgEl           = document.getElementById('viz-img');
    badgesContainer = document.getElementById('viz-badges');
    checksContainer = document.getElementById('viz-checks');
    resultPanel     = document.getElementById('viz-result');
    vrTotal         = document.getElementById('vr-total');
    vrAid           = document.getElementById('vr-aid');
    vrNet           = document.getElementById('vr-net');
    vizCta          = document.getElementById('viz-cta');

    if (!uploadZone) return; // section not present on this page

    bindUploadEvents();
    bindCheckboxEvents();
    bindScrollReveal();
  }

  /* ─────────────────────────────────────────────
     1. Image upload
  ───────────────────────────────────────────── */

  function bindUploadEvents() {
    // Click anywhere in the zone (except directly on the hidden input)
    uploadZone.addEventListener('click', function (e) {
      if (e.target !== fileInput) {
        fileInput.click();
      }
    });

    fileInput.addEventListener('change', function () {
      if (this.files && this.files[0]) {
        loadFile(this.files[0]);
      }
    });

    // Drag-and-drop
    uploadZone.addEventListener('dragover', function (e) {
      e.preventDefault();
      uploadZone.classList.add('viz-upload--drag');
    });

    uploadZone.addEventListener('dragleave', function (e) {
      // Only remove if the pointer has truly left the zone
      if (!uploadZone.contains(e.relatedTarget)) {
        uploadZone.classList.remove('viz-upload--drag');
      }
    });

    uploadZone.addEventListener('drop', function (e) {
      e.preventDefault();
      uploadZone.classList.remove('viz-upload--drag');
      const file = e.dataTransfer.files && e.dataTransfer.files[0];
      if (file) loadFile(file);
    });
  }

  function loadFile(file) {
    if (!file.type.startsWith('image/')) return; // silently ignore non-images

    const reader = new FileReader();
    reader.onload = function (e) {
      imgEl.src = e.target.result;
    };

    imgEl.onload = function () {
      // Apply warm filter matching the brand's photography palette
      imgEl.style.filter = 'sepia(0.1) saturate(1.1) brightness(1.05)';
      imgEl.style.display = 'block';
      placeholder.style.display = 'none';
      imageLoaded = true;
      refreshBadges();
    };

    reader.readAsDataURL(file);
  }

  /* ─────────────────────────────────────────────
     2. Service checkboxes → cost calculation
  ───────────────────────────────────────────── */

  function bindCheckboxEvents() {
    checksContainer.addEventListener('change', function (e) {
      if (e.target.type !== 'checkbox') return;
      recalculate();
      refreshBadges();
    });
  }

  function getCheckedServices() {
    return Array.from(checksContainer.querySelectorAll('input[type="checkbox"]:checked'));
  }

  function recalculate() {
    const checked = getCheckedServices();

    if (checked.length === 0) {
      hideResult();
      return;
    }

    let totalMin = 0, totalMax = 0;
    let aidMin   = 0, aidMax   = 0;

    checked.forEach(function (cb) {
      const min  = parseInt(cb.dataset.min, 10);
      const max  = parseInt(cb.dataset.max, 10);
      const rate = AID_RATES[cb.value] || 0;

      totalMin += min;
      totalMax += max;
      aidMin   += Math.round(min * rate);
      aidMax   += Math.round(max * rate);
    });

    const netMin = totalMin - aidMax; // best case net (max aid on min cost)
    const netMax = totalMax - aidMin; // worst case net

    showResult(totalMin, totalMax, aidMin, aidMax, netMin, netMax);
  }

  /* ─────────────────────────────────────────────
     3. Result panel display / hide
  ───────────────────────────────────────────── */

  function showResult(totalMin, totalMax, aidMin, aidMax, netMin, netMax) {
    const wasHidden = resultPanel.style.display === 'none' || resultPanel.style.display === '';

    resultPanel.style.display = 'flex';

    if (wasHidden) {
      // Trigger reflow so the CSS transition fires from opacity:0
      resultPanel.classList.remove('viz-result--visible');
      void resultPanel.offsetWidth; // force reflow
      resultPanel.classList.add('viz-result--visible');

      // Animate numbers only on first reveal
      animateRange(vrTotal, 0, totalMin, totalMax, ANIM_DURATION);
      animateRange(vrAid,   0, aidMin,   aidMax,   ANIM_DURATION);
      animateRange(vrNet,   0, netMin,   netMax,   ANIM_DURATION);
    } else {
      // Already visible — just update without re-animating to avoid jank
      vrTotal.textContent = formatRange(totalMin, totalMax);
      vrAid.textContent   = formatRange(aidMin,   aidMax);
      vrNet.textContent   = formatRange(Math.max(0, netMin), Math.max(0, netMax));
    }
  }

  function hideResult() {
    resultPanel.classList.remove('viz-result--visible');
    // Wait for fade-out transition before hiding from layout
    resultPanel.addEventListener('transitionend', function handler() {
      resultPanel.style.display = 'none';
      resultPanel.removeEventListener('transitionend', handler);
    });
  }

  /* ─────────────────────────────────────────────
     4. Number formatting & count-up animation
  ───────────────────────────────────────────── */

  function fmt(n) {
    return Math.round(n).toLocaleString('fr-FR') + '\u00a0€'; // non-breaking space before €
  }

  function formatRange(min, max) {
    return fmt(min) + '\u00a0–\u00a0' + fmt(max);
  }

  function animateRange(el, fromMin, toMin, toMax, duration) {
    const start = performance.now();

    function tick(now) {
      const elapsed  = now - start;
      const progress = Math.min(elapsed / duration, 1);
      const eased    = EASING(progress);
      const current  = fromMin + (toMin - fromMin) * eased;

      el.textContent = fmt(current) + '\u00a0–\u00a0' + fmt(toMax);

      if (progress < 1) {
        requestAnimationFrame(tick);
      } else {
        el.textContent = formatRange(toMin, toMax);
      }
    }

    requestAnimationFrame(tick);
  }

  /* ─────────────────────────────────────────────
     5. Service badges overlay on image
  ───────────────────────────────────────────── */

  function refreshBadges() {
    const checked = getCheckedServices();

    // Remove badges for unchecked services
    Array.from(badgesContainer.children).forEach(function (badge) {
      const value = badge.dataset.service;
      const stillChecked = checked.some(function (cb) { return cb.value === value; });
      if (!stillChecked) {
        removeBadge(badge);
      }
    });

    // Add badges for newly checked services (avoid duplicates)
    checked.forEach(function (cb) {
      const existing = badgesContainer.querySelector('[data-service="' + cb.value + '"]');
      if (!existing) {
        addBadge(cb.value);
      }
    });
  }

  function addBadge(serviceValue) {
    const badge  = document.createElement('span');
    badge.className        = 'viz-badge';
    badge.dataset.service  = serviceValue;

    const icon = SERVICE_ICONS[serviceValue] || '✓';
    const label = getLabelForService(serviceValue);
    badge.textContent = icon + '\u00a0' + label;

    // Start transparent; CSS transition will animate to opacity:1
    badge.style.opacity   = '0';
    badge.style.transform = 'translateY(6px)';

    badgesContainer.appendChild(badge);

    // Force reflow, then trigger transition
    void badge.offsetWidth;
    badge.style.opacity   = '1';
    badge.style.transform = 'translateY(0)';
  }

  function removeBadge(badge) {
    badge.style.opacity   = '0';
    badge.style.transform = 'translateY(6px)';
    badge.addEventListener('transitionend', function () {
      if (badge.parentNode) badge.parentNode.removeChild(badge);
    }, { once: true });
  }

  function getLabelForService(value) {
    const el = checksContainer.querySelector('input[value="' + value + '"]');
    if (!el) return value;
    const nameEl = el.closest('.vcheck') && el.closest('.vcheck').querySelector('.vcheck__name');
    return nameEl ? nameEl.textContent.trim() : value;
  }

  /* ─────────────────────────────────────────────
     6. Scroll reveal (IntersectionObserver)
  ───────────────────────────────────────────── */

  function bindScrollReveal() {
    const section = document.getElementById('visualizer');
    if (!section || typeof IntersectionObserver === 'undefined') return;

    // Set initial invisible state via inline style; class will override it
    section.style.opacity  = '0';
    section.style.transform = 'translateY(40px)';
    section.style.transition = 'opacity 0.7s ease, transform 0.7s ease';

    const observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            section.style.opacity  = '1';
            section.style.transform = 'translateY(0)';
            observer.unobserve(section); // fire only once
          }
        });
      },
      { threshold: 0.12 }
    );

    observer.observe(section);
  }

  /* ─────────────────────────────────────────────
     Bootstrap
  ───────────────────────────────────────────── */

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init(); // DOM already ready (e.g. deferred script)
  }
})();
