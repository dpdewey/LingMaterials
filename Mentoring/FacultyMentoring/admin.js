/* =========================================================
   Administrator page — Faculty mentoring
   ---------------------------------------------------------
   - Soft password gate (client-side only; not real security)
   - Reads ALL entries from storage including private fields
   - Renders each entry with private-field markers
   - CSV export with full data
   ========================================================= */

(function () {
  'use strict';

  const ADMIN_PASSWORD = 'ShaneReeseMentors';
  const SESSION_KEY    = 'admin-faculty-session';

  /* -------- DOM -------- */
  const gate         = document.getElementById('gate');
  const report       = document.getElementById('report');
  const gateForm     = document.getElementById('gate-form');
  const gatePw       = document.getElementById('gate-pw');
  const gateErr      = document.getElementById('gate-err');
  const exportBtn    = document.getElementById('export-csv');
  const logoutBtn    = document.getElementById('logout');
  const container    = document.getElementById('entries-container');
  const statTotal    = document.getElementById('stat-total');
  const statPublic   = document.getElementById('stat-public');
  const statMixed    = document.getElementById('stat-mixed');
  const statAllpriv  = document.getElementById('stat-allpriv');

  /* -------- Session: keep unlocked through page navigation only --------
     Uses sessionStorage so closing the tab clears it. Not in localStorage
     deliberately — we don't want indefinite admin sessions. */
  function isUnlocked() {
    try { return sessionStorage.getItem(SESSION_KEY) === '1'; }
    catch (e) { return false; }
  }
  function unlock() {
    try { sessionStorage.setItem(SESSION_KEY, '1'); } catch (e) {}
  }
  function lock() {
    try { sessionStorage.removeItem(SESSION_KEY); } catch (e) {}
  }

  /* -------- Gate -------- */
  gateForm.addEventListener('submit', function (e) {
    e.preventDefault();
    if (gatePw.value === ADMIN_PASSWORD) {
      unlock();
      showReport();
    } else {
      gateErr.classList.add('show');
      gatePw.value = '';
      gatePw.focus();
    }
  });

  logoutBtn.addEventListener('click', function () {
    lock();
    window.location.reload();
  });

  /* -------- Show / load report -------- */
  async function showReport() {
    gate.style.display    = 'none';
    report.style.display  = 'block';
    document.body.style.background = 'var(--bg-soft)';
    await loadAndRender();
  }

  async function loadAndRender() {
    const entries = await loadAllEntries();
    renderStats(entries);
    renderEntries(entries);
    wireExport(entries);
  }

  /* -------- Load every entry, including private ones -------- */
  async function loadAllEntries() {
    const entries = [];
    try {
      const res = await window.storage.list('mentoring:', true);
      const keys = (res && res.keys) || [];
      for (const key of keys) {
        try {
          const got = await window.storage.get(key, true);
          if (got && got.value) entries.push(JSON.parse(got.value));
        } catch (e) { console.warn('Could not load', key, e); }
      }
    } catch (e) { console.warn('Could not list', e); }

    // Seed if empty (so admin sees at least the demo data on first visit)
    if (!entries.length && Array.isArray(window.SEED_ENTRIES)) {
      entries.push.apply(entries, window.SEED_ENTRIES);
    }

    entries.sort(function (a, b) {
      return new Date(b.createdAt) - new Date(a.createdAt);
    });
    return entries;
  }

  /* -------- Stats -------- */
  function renderStats(entries) {
    const total = entries.length;
    let allPriv = 0, partial = 0, fullyPublic = 0;
    entries.forEach(function (e) {
      if (e.allPrivate) { allPriv++; return; }
      const flags = e.privacyFlags || {};
      const hasAny = !!(flags.accomplishments || flags.notes || flags.impact);
      if (hasAny) partial++;
      else fullyPublic++;
    });
    statTotal.textContent   = total;
    statPublic.textContent  = fullyPublic;
    statMixed.textContent   = partial;
    statAllpriv.textContent = allPriv;
  }

  /* -------- Render each entry -------- */
  function renderEntries(entries) {
    if (!entries.length) {
      container.innerHTML =
        '<div style="text-align:center;padding:60px 20px;' +
        'font-family:var(--font-sans);font-style:italic;color:var(--text-medium);">' +
        'No entries yet.</div>';
      return;
    }

    container.innerHTML = entries.map(function (e) {
      const flags = e.privacyFlags || {};
      const date = e.createdAt ? new Date(e.createdAt) : null;
      const dateStr = date ? date.toLocaleDateString('en-US', {
        year: 'numeric', month: 'short', day: 'numeric',
        hour: '2-digit', minute: '2-digit'
      }) : '';

      const allPrivBadge = e.allPrivate
        ? '<span class="anon-banner" style="background:var(--error);">FULLY PRIVATE ENTRY</span>'
        : '';

      const fields = [];
      // Header (mentor + date + venue)
      // Field: students
      fields.push(renderField(
        'Students mentored (' + (e.students || []).length + ')',
        (e.students || []).join(', ') || '—',
        false, false
      ));
      // Field: accomplishments
      fields.push(renderField(
        'Accomplishments',
        e.accomplishments || '—',
        flags.accomplishments,
        false
      ));
      // Field: notes
      fields.push(renderField(
        'Mentor reflection',
        e.notes || '—',
        flags.notes,
        true
      ));
      // Field: impact (new)
      if (e.impact || flags.impact) {
        fields.push(renderField(
          'Personal impact',
          e.impact || '—',
          flags.impact,
          true
        ));
      }
      // Field: image
      if (e.image) {
        fields.push(
          '<div class="admin-field">' +
          '<div class="admin-field-label">Image attached</div>' +
          '<img src="' + e.image + '" alt="" style="max-width:240px;border-radius:3px;border:1px solid var(--border);" onerror="this.style.display=\'none\'">' +
          '</div>'
        );
      }

      return '<div class="admin-entry">' +
        '<div class="admin-entry-header">' +
        '<div>' +
          '<div class="admin-entry-name">' + esc(e.mentor || '—') + '</div>' +
          '<div style="margin-top:4px;font-size:14px;color:var(--text-medium);font-family:var(--font-sans);">' +
            esc(e.venueType || '') +
            (e.venue ? ' · ' + esc(e.venue) : '') +
            (e.discipline ? ' · ' + esc(e.discipline) : '') +
          '</div>' +
        '</div>' +
        '<div class="admin-entry-meta">' + dateStr +
          (e.term ? ' · ' + esc(e.term) : '') +
          ' &nbsp; ' + allPrivBadge +
        '</div>' +
        '</div>' +
        '<div class="admin-entry-body">' + fields.join('') + '</div>' +
        '</div>';
    }).join('');
  }

  function renderField(label, content, isPrivate, italic) {
    const labelHtml = '<div class="admin-field-label">' +
      esc(label) +
      (isPrivate ? '<span class="admin-field-private-tag">PRIVATE</span>' : '') +
      '</div>';
    const contentClass = 'admin-field-content' + (italic ? ' serif-em' : '');
    const contentHtml = '<div class="' + contentClass + '">' +
      esc(content || '').replace(/\n/g, '<br>') + '</div>';
    return '<div class="admin-field">' + labelHtml + contentHtml + '</div>';
  }

  /* -------- CSV export -------- */
  function wireExport(entries) {
    exportBtn.onclick = function () { downloadCsv(entries); };
  }

  function csvCell(v) {
    if (v == null) return '';
    const s = String(v).replace(/"/g, '""');
    return '"' + s + '"';
  }

  function downloadCsv(entries) {
    const headers = [
      'id', 'createdAt', 'mentor', 'venueType', 'venue', 'discipline', 'term',
      'students', 'studentCount',
      'accomplishments', 'accomplishments_private',
      'notes', 'notes_private',
      'impact', 'impact_private',
      'allPrivate', 'hasImage'
    ];

    const rows = [headers.map(csvCell).join(',')];
    entries.forEach(function (e) {
      const flags = e.privacyFlags || {};
      const students = (e.students || []).join('; ');
      const row = [
        e.id || '',
        e.createdAt || '',
        e.mentor || '',
        e.venueType || '',
        e.venue || '',
        e.discipline || '',
        e.term || '',
        students,
        (e.students || []).length,
        e.accomplishments || '',
        flags.accomplishments ? 'true' : 'false',
        e.notes || '',
        flags.notes ? 'true' : 'false',
        e.impact || '',
        flags.impact ? 'true' : 'false',
        e.allPrivate ? 'true' : 'false',
        e.image ? 'true' : 'false'
      ];
      rows.push(row.map(csvCell).join(','));
    });

    const csv = rows.join('\r\n');
    // Add UTF-8 BOM so Excel reads non-ASCII characters correctly
    const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' });
    const url  = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'faculty-mentoring-' + new Date().toISOString().slice(0, 10) + '.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(function () { URL.revokeObjectURL(url); }, 200);
  }

  /* -------- HTML escape -------- */
  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  /* -------- Init -------- */
  if (isUnlocked()) {
    showReport();
  } else {
    setTimeout(function () { gatePw.focus(); }, 100);
  }

})();
