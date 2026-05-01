/* =========================================================
   Administrator page — Student experiences
   ---------------------------------------------------------
   - Soft password gate (client-side only; not real security)
   - Reads ALL student entries including private fields,
     real names of those who opted into anonymity
   - CSV export with full data, one aim response per row
   ========================================================= */

(function () {
  'use strict';

  const ADMIN_PASSWORD = 'ShaneReeseMentors';
  const SESSION_KEY    = 'admin-student-session';

  const AIM_LABELS = {
    spiritual:    'Spiritually Strengthening',
    intellectual: 'Intellectually Enlarging',
    character:    'Character Building',
    service:      'Lifelong Learning & Service'
  };

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
  const statAnon     = document.getElementById('stat-anon');
  const statAims     = document.getElementById('stat-aims');

  /* -------- Session -------- */
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

  /* -------- Show / load -------- */
  async function showReport() {
    gate.style.display    = 'none';
    report.style.display  = 'block';
    document.body.style.background = 'var(--paper)';
    await loadAndRender();
  }

  async function loadAndRender() {
    const entries = await loadAllEntries();
    renderStats(entries);
    renderEntries(entries);
    wireExport(entries);
  }

  async function loadAllEntries() {
    const entries = [];
    try {
      const res = await window.storage.list('student:', true);
      const keys = (res && res.keys) || [];
      for (const key of keys) {
        try {
          const got = await window.storage.get(key, true);
          if (got && got.value) entries.push(JSON.parse(got.value));
        } catch (e) { console.warn('Could not load', key, e); }
      }
    } catch (e) { console.warn('Could not list', e); }

    if (!entries.length && Array.isArray(window.STUDENT_SEED_ENTRIES)) {
      entries.push.apply(entries, window.STUDENT_SEED_ENTRIES);
    }

    entries.sort(function (a, b) {
      return new Date(b.createdAt) - new Date(a.createdAt);
    });
    return entries;
  }

  /* -------- Stats -------- */
  function renderStats(entries) {
    const total = entries.length;
    let allPriv = 0, partial = 0, fullyPublic = 0, anon = 0, aims = 0;
    entries.forEach(function (e) {
      if (e.allPrivate) { allPriv++; }
      else {
        const flags = e.privacyFlags || {};
        const hasFieldPrivate = !!flags.transformative;
        const hasAimPrivate = (e.aimsResponses || []).some(function (r) { return r.private; });
        if (hasFieldPrivate || hasAimPrivate) partial++;
        else fullyPublic++;
      }
      if (e.showAnonymous) anon++;
      aims += (e.aimsResponses || []).length;
    });
    statTotal.textContent   = total;
    statPublic.textContent  = fullyPublic;
    statMixed.textContent   = partial;
    statAllpriv.textContent = allPriv;
    statAnon.textContent    = anon;
    statAims.textContent    = aims;
  }

  /* -------- Render -------- */
  function renderEntries(entries) {
    if (!entries.length) {
      container.innerHTML =
        '<div style="text-align:center;padding:60px 20px;' +
        'font-family:var(--font-display);font-style:italic;color:var(--ink-mute);">' +
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
      const anonBadge = e.showAnonymous
        ? '<span class="anon-banner">DISPLAYED ANONYMOUSLY ON PUBLIC ARCHIVE</span>'
        : '';

      const fields = [];
      // Field: transformative
      fields.push(renderField(
        'Part A — Transformative experience',
        e.transformative || '—',
        flags.transformative,
        true
      ));
      // Aims responses (each may have its own privacy flag)
      (e.aimsResponses || []).forEach(function (r) {
        const aimLabel = AIM_LABELS[r.aim] || r.aim;
        fields.push(renderAimResponse(aimLabel, r));
      });
      // Image
      if (e.image) {
        fields.push(
          '<div class="admin-field">' +
          '<div class="admin-field-label">Image attached</div>' +
          '<img src="' + e.image + '" alt="" style="max-width:240px;border-radius:3px;border:1px solid var(--rule-soft);" onerror="this.style.display=\'none\'">' +
          '</div>'
        );
      }
      if (!fields.length) {
        fields.push('<div style="font-style:italic;color:var(--ink-mute);">No reflections recorded.</div>');
      }

      return '<div class="admin-entry">' +
        '<div class="admin-entry-header">' +
        '<div>' +
          '<div class="admin-entry-name">' + esc(e.studentName || '—') + '</div>' +
          '<div style="margin-top:4px;font-size:14px;color:var(--ink-soft);font-family:var(--font-display);">' +
            'mentored by ' + esc(e.mentorName || '—') +
            ' · ' + esc(e.program || '') +
            (e.venueType ? ' · ' + esc(e.venueType) : '') +
            (e.venueDesc ? ' — ' + esc(e.venueDesc) : '') +
          '</div>' +
        '</div>' +
        '<div class="admin-entry-meta">' + dateStr +
          (e.term ? ' · ' + esc(e.term) : '') +
          ' &nbsp; ' + anonBadge + ' ' + allPrivBadge +
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

  function renderAimResponse(aimLabel, r) {
    const labelHtml = '<div class="admin-field-label">' +
      'Aim · ' + esc(aimLabel) +
      (r.private ? '<span class="admin-field-private-tag">PRIVATE</span>' : '') +
      '</div>';
    return '<div class="admin-field">' +
      labelHtml +
      '<div style="margin-bottom:8px;">' +
        '<span class="chip ' + esc(r.aim) + '">' + esc(r.promptLabel || '') + '</span>' +
      '</div>' +
      '<div style="font-family:var(--font-display);font-style:italic;color:var(--ink-mute);font-size:13px;line-height:1.5;margin-bottom:10px;padding-bottom:8px;border-bottom:1px dotted var(--rule-soft);">' +
        esc(r.promptFull || '') +
      '</div>' +
      '<div class="admin-field-content serif-em">' +
        esc(r.response || '').replace(/\n/g, '<br>') +
      '</div>' +
      '</div>';
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
    // One row per entry, with aims responses flattened into a few columns.
    // Each aim is its own column for ease of analysis in Excel.
    const headers = [
      'id', 'createdAt', 'studentName', 'mentorName', 'program',
      'venueType', 'venueDesc', 'term',
      'transformative', 'transformative_private',
      'spiritual_prompt', 'spiritual_response', 'spiritual_private',
      'intellectual_prompt', 'intellectual_response', 'intellectual_private',
      'character_prompt', 'character_response', 'character_private',
      'service_prompt', 'service_response', 'service_private',
      'aimsCount', 'allPrivate', 'showAnonymous', 'hasImage'
    ];

    const rows = [headers.map(csvCell).join(',')];

    entries.forEach(function (e) {
      const flags = e.privacyFlags || {};
      // Index aims responses by aim
      const byAim = { spiritual: null, intellectual: null, character: null, service: null };
      (e.aimsResponses || []).forEach(function (r) {
        if (byAim.hasOwnProperty(r.aim)) byAim[r.aim] = r;
      });

      function aimCells(aim) {
        const r = byAim[aim];
        if (!r) return ['', '', 'false'];
        return [r.promptLabel || '', r.response || '', r.private ? 'true' : 'false'];
      }

      const row = [
        e.id || '',
        e.createdAt || '',
        e.studentName || '',
        e.mentorName || '',
        e.program || '',
        e.venueType || '',
        e.venueDesc || '',
        e.term || '',
        e.transformative || '',
        flags.transformative ? 'true' : 'false',
        ...aimCells('spiritual'),
        ...aimCells('intellectual'),
        ...aimCells('character'),
        ...aimCells('service'),
        (e.aimsResponses || []).length,
        e.allPrivate ? 'true' : 'false',
        e.showAnonymous ? 'true' : 'false',
        e.image ? 'true' : 'false'
      ];
      rows.push(row.map(csvCell).join(','));
    });

    const csv = rows.join('\r\n');
    const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' });
    const url  = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'student-experiences-' + new Date().toISOString().slice(0, 10) + '.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(function () { URL.revokeObjectURL(url); }, 200);
  }

  /* -------- Util -------- */
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
