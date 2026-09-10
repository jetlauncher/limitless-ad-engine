(() => {
  'use strict';

  // ── State ──────────────────────────────────────────────────
  let ads = [];
  let filtered = [];
  let currentIndex = 0;
  let activeFamily = 'all';
  let activeAngle = 'all';

  // ── DOM refs ───────────────────────────────────────────────
  const grid = document.getElementById('ad-grid');
  const emptyState = document.getElementById('empty-state');
  const statTotal = document.getElementById('stat-total');
  const statVisible = document.getElementById('stat-visible');
  const angleFilters = document.getElementById('angle-filters');
  const modal = document.getElementById('modal');
  const modalBackdrop = document.getElementById('modal-backdrop');
  const modalClose = document.getElementById('modal-close');
  const modalPrev = document.getElementById('modal-prev');
  const modalNext = document.getElementById('modal-next');
  const modalImage = document.getElementById('modal-image');
  const modalFamily = document.getElementById('modal-family');
  const modalCounter = document.getElementById('modal-counter');
  const modalTitle = document.getElementById('modal-title');
  const modalFields = document.getElementById('modal-fields');

  // ── Load data ──────────────────────────────────────────────
  fetch('manifest.json')
    .then(r => r.json())
    .then(data => {
      ads = data;
      statTotal.textContent = ads.length;
      const statAlt = document.getElementById('stat-alt');
      if (statAlt) statAlt.textContent = ads.filter(a => a.family === 'Alternatives').length;
      buildAngleChips();
      applyFilters();
    })
    .catch(() => {
      grid.innerHTML = '<p style="color:var(--text-muted);padding:40px">Failed to load manifest.json</p>';
    });

  // ── Build angle chips dynamically ─────────────────────────
  function buildAngleChips() {
    const angles = [...new Set(ads.map(a => a.angle))];
    angles.forEach(angle => {
      const btn = document.createElement('button');
      btn.className = 'angle-chip';
      btn.dataset.angle = angle;
      btn.textContent = angle;
      btn.addEventListener('click', () => selectAngle(angle, btn));
      angleFilters.appendChild(btn);
    });
  }

  // ── Family toggle ──────────────────────────────────────────
  document.querySelectorAll('.family-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.family-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeFamily = btn.dataset.family;
      activeAngle = 'all';
      document.querySelectorAll('.angle-chip').forEach(c => c.classList.remove('active'));
      document.querySelector('.angle-chip[data-angle="all"]').classList.add('active');
      applyFilters();
    });
  });

  // ── Angle filter ───────────────────────────────────────────
  document.querySelector('.angle-chip[data-angle="all"]').addEventListener('click', e => {
    selectAngle('all', e.currentTarget);
  });

  function selectAngle(angle, btn) {
    document.querySelectorAll('.angle-chip').forEach(c => c.classList.remove('active'));
    btn.classList.add('active');
    activeAngle = angle;
    applyFilters();
  }

  // ── Filter logic ───────────────────────────────────────────
  function applyFilters() {
    filtered = ads.filter(ad => {
      const familyMatch = activeFamily === 'all' || ad.family === activeFamily;
      const angleMatch = activeAngle === 'all' || ad.angle === activeAngle;
      return familyMatch && angleMatch;
    });
    statVisible.textContent = filtered.length;
    renderGrid();
  }

  // ── Render grid ────────────────────────────────────────────
  function renderGrid() {
    grid.innerHTML = '';

    if (filtered.length === 0) {
      emptyState.hidden = false;
      return;
    }
    emptyState.hidden = true;

    filtered.forEach((ad, i) => {
      const card = document.createElement('div');
      card.className = 'ad-card';
      card.setAttribute('tabindex', '0');
      card.setAttribute('role', 'button');
      card.setAttribute('aria-label', ad.title);
      card.style.animationDelay = `${Math.min(i * 30, 300)}ms`;

      const isOriginal = ad.family === 'Originals';
      const dotClass = isOriginal ? 'original' : 'alternative';
      const indexLabel = isOriginal ? `OG ${i + 1}` : `v${ad.slug.match(/\d+/)?.[0] ?? i + 1}`;

      card.innerHTML = `
        <div class="card-img-wrap">
          <img src="${escHtml(ad.file)}" alt="${escHtml(ad.title)}" loading="lazy" />
          <span class="card-family-dot ${dotClass}"></span>
        </div>
        <div class="card-body">
          <div class="card-angle"><span class="card-index">${escHtml(indexLabel)}</span>${escHtml(ad.angle)}</div>
          <div class="card-title">${escHtml(ad.title)}</div>
          ${ad.notes ? `<div class="card-notes">${escHtml(ad.notes)}</div>` : ''}
        </div>
      `;

      card.addEventListener('click', () => openModal(i));
      card.addEventListener('keydown', e => {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); openModal(i); }
      });

      grid.appendChild(card);
    });
  }

  // ── Modal ──────────────────────────────────────────────────
  function openModal(index) {
    currentIndex = index;
    renderModal();
    modal.hidden = false;
    document.body.style.overflow = 'hidden';
    modalClose.focus();
  }

  function closeModal() {
    modal.hidden = true;
    document.body.style.overflow = '';
  }

  function renderModal() {
    const ad = filtered[currentIndex];
    if (!ad) return;

    const isOriginal = ad.family === 'Originals';

    modalImage.src = ad.file;
    modalImage.alt = ad.title;
    modalFamily.textContent = ad.family;
    modalFamily.className = 'modal-family-badge ' + (isOriginal ? 'original' : 'alternative');
    modalCounter.textContent = `${currentIndex + 1} / ${filtered.length}`;
    modalTitle.textContent = ad.title;

    // Build metadata fields
    const fields = [
      { label: 'Angle', value: ad.angle, cls: 'angle-val' },
      ad.notes   && { label: 'Notes', value: ad.notes },
      ad.proof   && { label: 'Proof', value: ad.proof },
      ad.cta     && { label: 'CTA', value: ad.cta },
      ad.template && { label: 'Template', value: ad.template, cls: 'template-val' },
    ].filter(Boolean);

    modalFields.innerHTML = fields.map((f, i) => `
      ${i > 0 ? '<div class="modal-divider"></div>' : ''}
      <div class="modal-field">
        <span class="field-label">${escHtml(f.label)}</span>
        <span class="field-value ${f.cls || ''}">${escHtml(f.value)}</span>
      </div>
    `).join('');

    if (ad.caption) {
      modalFields.innerHTML += `
        <div class="modal-caption">
          <div class="caption-head">
            <span class="field-label">Caption สำหรับยิงแอด</span>
            <button class="copy-caption-btn" id="copy-caption">คัดลอก</button>
          </div>
          <pre class="caption-text" id="caption-text">${escHtml(ad.caption)}</pre>
        </div>
      `;
      const btn = document.getElementById('copy-caption');
      btn.addEventListener('click', () => {
        const text = ad.caption;
        const done = () => {
          btn.textContent = 'คัดลอกแล้ว ✓';
          btn.classList.add('copied');
          setTimeout(() => { btn.textContent = 'คัดลอก'; btn.classList.remove('copied'); }, 1600);
        };
        const fallback = () => {
          const ta = document.createElement('textarea');
          ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0';
          document.body.appendChild(ta);
          ta.focus(); ta.select();
          try { document.execCommand('copy'); } catch (e) {}
          ta.remove(); done();
        };
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(text).then(done).catch(fallback);
        } else {
          fallback();
        }
      });
    }

    modalPrev.disabled = currentIndex === 0;
    modalNext.disabled = currentIndex === filtered.length - 1;
  }

  function goNext() {
    if (currentIndex < filtered.length - 1) { currentIndex++; renderModal(); }
  }

  function goPrev() {
    if (currentIndex > 0) { currentIndex--; renderModal(); }
  }

  // ── Modal events ───────────────────────────────────────────
  modalClose.addEventListener('click', closeModal);
  modalBackdrop.addEventListener('click', closeModal);
  modalPrev.addEventListener('click', goPrev);
  modalNext.addEventListener('click', goNext);

  document.addEventListener('keydown', e => {
    if (modal.hidden) return;
    if (e.key === 'Escape')      closeModal();
    if (e.key === 'ArrowRight')  goNext();
    if (e.key === 'ArrowLeft')   goPrev();
  });

  // ── Util ───────────────────────────────────────────────────
  function escHtml(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

})();
