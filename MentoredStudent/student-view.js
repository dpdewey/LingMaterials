/* =========================================================
   Student view page JS
   ========================================================= */

(function () {
  'use strict';

  const STOPWORDS = new Set((
    'a about above after again against all am an and any are as at be because been before being below between both but by could did do does doing down during each few for from further had has have having he her here his how into is it its itself just let me more most my nor not now of off on once only or other our out over own same she should so some such than that the their them then there these they this those through too under until up very was we were what when where which while who whom why will with would you your get got also one two three time times day days year years way back even much many how what just still more most well only also like just even some any way can may might will would could should must shall let get set go come came say said made make take took put keep kept give gave show use used really very quite big little small great good bad old new high long last next such rather rather much very quite'
  ).split(/\s+/).filter(Boolean));

  const AIM_LABELS = {
    spiritual:    'Spiritually Strengthening',
    intellectual: 'Intellectually Enlarging',
    character:    'Character Building',
    service:      'Lifelong Learning & Service'
  };

  /* -------- DOM -------- */
  const $ = id => document.getElementById(id);
  const summaryText    = $('summary-text');
  const summaryMeta    = $('summary-meta');
  const wordCloudEl    = $('word-cloud');
  const galleryEl      = $('gallery');
  const aimsBreakdown  = $('aims-breakdown');
  const entriesListEl  = $('entries-list');
  const entriesCountEl = $('entries-count');
  const searchEl       = $('search');
  const filterAimEl    = $('filter-aim');
  const filterVenueEl  = $('filter-venue');
  const sortEl         = $('sort');
  const modalBackdrop  = $('modal-backdrop');
  const modalInner     = $('modal-inner');
  const modalClose     = $('modal-close');
  const heroUpdated    = $('hero-updated');
  const pullQuote      = $('pull-quote');
  const pullQuoteText  = $('pull-quote-text');
  const pullQuoteAttr  = $('pull-quote-attr');

  let allEntries = [];

  /* =========================================================
     LOAD
     ========================================================= */
  async function loadEntries() {
    let entries = [];
    try {
      const res  = await window.storage.list('student:', true);
      const keys = (res && res.keys) || [];
      for (const key of keys) {
        try {
          const got = await window.storage.get(key, true);
          if (got && got.value) entries.push(JSON.parse(got.value));
        } catch (e) { console.warn('Could not load', key, e); }
      }
    } catch (e) { console.warn('Could not list student entries', e); }

    if (!entries.length && Array.isArray(window.STUDENT_SEED_ENTRIES)) {
      entries = window.STUDENT_SEED_ENTRIES.slice();
      seedEntries(entries);
    }

    // PRIVACY FILTERING — drop fully-private entries, redact per-field privates,
    // apply anonymous-display to those who opted in.
    entries = entries
      .filter(e => !e.allPrivate)
      .map(e => {
        const flags = e.privacyFlags || {};
        const redacted = Object.assign({}, e);
        if (flags.transformative) redacted.transformative = '';
        // Filter aim responses individually
        redacted.aimsResponses = (e.aimsResponses || [])
          .filter(r => !r.private);
        // Anonymous-display: replace name on public view but keep id intact
        if (e.showAnonymous) {
          redacted.studentName = 'Anonymous student';
          redacted._anonymous = true;
        }
        return redacted;
      });

    entries.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
    return entries;
  }

  async function seedEntries(entries) {
    for (const e of entries) {
      try { await window.storage.set('student:' + e.id, JSON.stringify(e), true); }
      catch (err) { console.warn('Seed write failed', e.id, err); }
    }
  }

  /* =========================================================
     STATS
     ========================================================= */
  function computeStats(entries) {
    const students  = new Set();
    const mentors   = new Set();
    const programs  = new Set();
    let   aimsCount = 0;
    const aimCounts = { spiritual: 0, intellectual: 0, character: 0, service: 0 };

    entries.forEach(e => {
      if (e.studentName) students.add(e.studentName.toLowerCase().trim());
      if (e.mentorName)  mentors.add(e.mentorName.toLowerCase().trim());
      if (e.program)     programs.add(e.program);
      (e.aimsResponses || []).forEach(r => {
        aimsCount++;
        if (aimCounts[r.aim] !== undefined) aimCounts[r.aim]++;
      });
    });
    return { students: students.size, mentors: mentors.size,
             programs: programs.size, aimsCount, aimCounts };
  }

  function renderStats(s) {
    animateCount($('stat-students'),  s.students);
    animateCount($('stat-mentors'),   s.mentors);
    animateCount($('stat-aims'),      s.aimsCount);
    animateCount($('stat-programs'),  s.programs);

    // Aims banner counts
    ['spiritual', 'intellectual', 'character', 'service'].forEach(aim => {
      const el = $('aim-count-' + aim);
      if (el) animateCount(el, s.aimCounts[aim]);
    });
  }

  function animateCount(el, target) {
    if (!el) return;
    const dur = 900, start = performance.now();
    const tick = now => {
      const t = Math.min(1, (now - start) / dur);
      const eased = 1 - Math.pow(1 - t, 3);
      el.textContent = Math.floor(eased * target);
      if (t < 1) requestAnimationFrame(tick); else el.textContent = target;
    };
    requestAnimationFrame(tick);
  }

  /* =========================================================
     HERO META
     ========================================================= */
  function updateHero(entries) {
    if (!entries.length) { heroUpdated.textContent = '—'; return; }
    const latest = entries.reduce((a, b) =>
      new Date(a.createdAt) > new Date(b.createdAt) ? a : b);
    heroUpdated.textContent = new Date(latest.createdAt)
      .toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
  }

  /* =========================================================
     PULL QUOTE — from transformative narratives
     ========================================================= */
  function renderPullQuote(entries) {
    const candidates = [];
    entries.forEach(e => {
      if (!e.transformative) return;
      const sents = e.transformative.split(/(?<=[.!?])\s+/);
      sents.forEach(s => {
        const text = s.trim();
        if (text.length < 60 || text.length > 240) return;
        let score = 0;
        const markers = [
          /\b(changed|realized|understood|knew|moment|first time|never|always)\b/i,
          /\b(I thought|I knew|I felt|I learned|I had|I was)\b/,
          /\b(that day|that night|that moment|that afternoon|that hour)\b/i,
          /\b(he said|she said|they said)\b/i
        ];
        markers.forEach(m => { if (m.test(text)) score++; });
        if (score > 0) candidates.push({ text, name: e.studentName, venue: e.venueDesc, score });
      });
    });
    if (!candidates.length) { pullQuote.style.display = 'none'; return; }
    candidates.sort((a, b) => b.score - a.score);
    const top = candidates.slice(0, 3);
    const q = top[Math.floor(Math.random() * top.length)];
    pullQuoteText.textContent = '\u201C' + q.text + '\u201D';
    pullQuoteAttr.textContent = q.name + ' \u00B7 ' + q.venue;
    pullQuote.style.display = 'block';
  }

  /* =========================================================
     WORD CLOUD
     ========================================================= */
  function buildWordCloud(entries) {
    const counts = {};
    entries.forEach(e => {
      const texts = [e.venueDesc, e.transformative,
        ...(e.aimsResponses || []).map(r => r.response)].filter(Boolean).join(' ');
      texts.toLowerCase()
        .replace(/[^a-záéíóúñü'\-\s]/g, ' ')
        .split(/\s+/)
        .forEach(w => {
          w = w.replace(/^['\-]+|['\-]+$/g, '');
          if (w.length < 4 || STOPWORDS.has(w) || /\d/.test(w)) return;
          counts[w] = (counts[w] || 0) + 1;
        });
    });
    const top = Object.entries(counts).sort((a, b) => b[1] - a[1]).slice(0, 44);
    if (!top.length) {
      wordCloudEl.innerHTML = '<span class="empty">Themes will appear as entries are added.</span>';
      return;
    }
    const max = top[0][1], min = top[top.length - 1][1], range = Math.max(1, max - min);
    const shuffled = top.slice().sort(() => Math.random() - 0.5);
    wordCloudEl.innerHTML = shuffled.map(([word, count]) => {
      const t = (count - min) / range;
      const size = (15 + t * 38).toFixed(1);
      const color = t > 0.66 ? 'var(--byu-navy)' : t > 0.33 ? 'var(--byu-royal)' : 'var(--byu-navy-soft)';
      const opacity = (0.55 + t * 0.45).toFixed(2);
      const cap = word.charAt(0).toUpperCase() + word.slice(1);
      return `<span title="${count} mention${count === 1 ? '' : 's'}" style="font-size:${size}px; color:${color}; opacity:${opacity};">${cap}</span>`;
    }).join('');
  }

  /* =========================================================
     AIMS BREAKDOWN
     ========================================================= */
  function buildAimsBreakdown(entries) {
    // Count by aim × prompt
    const promptCounts = {};
    entries.forEach(e => {
      (e.aimsResponses || []).forEach(r => {
        const key = r.aim + ':' + r.promptKey;
        promptCounts[key] = (promptCounts[key] || { aim: r.aim, label: r.promptLabel, count: 0 });
        promptCounts[key].count++;
      });
    });

    const aimOrder = ['spiritual', 'intellectual', 'character', 'service'];
    const aimTotals = {};
    Object.values(promptCounts).forEach(p => {
      aimTotals[p.aim] = (aimTotals[p.aim] || 0) + p.count;
    });
    const maxTotal = Math.max(1, ...Object.values(aimTotals));

    if (!Object.keys(aimTotals).length) {
      aimsBreakdown.innerHTML = '<div style="font-family: var(--font-sans); font-style: italic; color: var(--text-medium); font-size: 14px;">No reflections yet.</div>';
      return;
    }

    aimsBreakdown.innerHTML = aimOrder
      .filter(aim => aimTotals[aim] > 0)
      .map(aim => {
        const pct = Math.round((aimTotals[aim] / maxTotal) * 100);
        return `<div class="aims-bar-row">
          <div class="aims-bar-label">
            <span class="aims-bar-name">${AIM_LABELS[aim]}</span>
            <span class="aims-bar-count">${aimTotals[aim]}</span>
          </div>
          <div class="aims-bar-track">
            <div class="aims-bar-fill ${aim}" style="width: ${pct}%"></div>
          </div>
        </div>`;
      }).join('');
  }

  /* =========================================================
     GALLERY
     ========================================================= */
  function buildGallery(entries) {
    const withImages = entries.filter(e => e.image && typeof e.image === 'string' && e.image.length > 100);
    if (!withImages.length) {
      galleryEl.innerHTML = '<div class="gallery-empty">Photos shared by students will appear here.</div>';
      return;
    }
    galleryEl.innerHTML = withImages.slice(0, 9).map(e =>
      `<div class="gallery-item" data-entry-id="${e.id}">
        <img src="${e.image}" alt="" loading="lazy" onerror="this.parentElement.style.display='none'">
        <div class="caption">${escH(e.studentName || '')} &middot; ${escH(e.venueDesc || '')}</div>
      </div>`
    ).join('');
    galleryEl.querySelectorAll('.gallery-item').forEach(el =>
      el.addEventListener('click', () => {
        const entry = allEntries.find(x => x.id === el.getAttribute('data-entry-id'));
        if (entry) openModal(entry);
      })
    );
    // After image loads settle, fall back to empty state if all hidden
    setTimeout(function () {
      const visible = Array.from(galleryEl.querySelectorAll('.gallery-item'))
        .filter(el => el.style.display !== 'none');
      if (!visible.length) {
        galleryEl.innerHTML = '<div class="gallery-empty">Photos shared by students will appear here.</div>';
      }
    }, 600);
  }

  /* =========================================================
     ENTRIES LIST
     ========================================================= */
  function populateFilters(entries) {
    const venues = new Set();
    entries.forEach(e => { if (e.venueType) venues.add(e.venueType); });
    filterVenueEl.innerHTML = '<option value="">All venues</option>';
    Array.from(venues).sort().forEach(v => {
      const opt = document.createElement('option');
      opt.value = v; opt.textContent = v;
      filterVenueEl.appendChild(opt);
    });
  }

  function getFilteredSorted() {
    const q     = (searchEl.value || '').trim().toLowerCase();
    const aim   = filterAimEl.value;
    const venue = filterVenueEl.value;

    let list = allEntries.filter(e => {
      if (venue && e.venueType !== venue) return false;
      if (aim && !(e.aimsResponses || []).some(r => r.aim === aim)) return false;
      if (q) {
        const blob = [e.studentName, e.mentorName, e.program, e.venueType,
          e.venueDesc, e.term, e.transformative,
          ...(e.aimsResponses || []).map(r => r.response + ' ' + r.promptLabel)
        ].join(' ').toLowerCase();
        if (!blob.includes(q)) return false;
      }
      return true;
    });

    list.sort((a, b) => {
      switch (sortEl.value) {
        case 'date-asc':     return new Date(a.createdAt) - new Date(b.createdAt);
        case 'date-desc':    return new Date(b.createdAt) - new Date(a.createdAt);
        case 'student-asc':  return (a.studentName || '').localeCompare(b.studentName || '');
        case 'mentor-asc':   return (a.mentorName || '').localeCompare(b.mentorName || '');
        case 'aims-desc':    return (b.aimsResponses || []).length - (a.aimsResponses || []).length;
        default:             return 0;
      }
    });
    return list;
  }

  function renderEntries() {
    const list = getFilteredSorted();
    entriesCountEl.textContent = `${list.length} of ${allEntries.length} entries shown`;

    if (!list.length) {
      entriesListEl.innerHTML = '<div class="entry-empty"><span class="symbol">¶</span>No entries match those filters.</div>';
      return;
    }

    entriesListEl.innerHTML = list.map((e, i) => {
      const aimsCount  = (e.aimsResponses || []).length;
      const date       = e.createdAt ? new Date(e.createdAt) : null;
      const dateStr    = date ? date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' }) : '';
      const term       = e.term ? ` &middot; ${escH(e.term)}` : '';
      const num        = romanize(i + 1);
      const chips      = [...new Set((e.aimsResponses || []).map(r => r.aim))]
        .map(aim => `<span class="aim-chip ${aim}">${AIM_LABELS[aim] ? AIM_LABELS[aim].split(' ')[0] : aim}</span>`)
        .join('');

      return `<div class="student-entry-row" data-entry-id="${e.id}">
        <div class="row-num">${num}</div>
        <div class="meta">
          <div class="name-line">
            <span class="student-name">${escH(e.studentName || '—')}</span>
            <span class="mentor-line-small">with ${escH(e.mentorName || '—')}</span>
            <span class="date-mono">${dateStr}${term}</span>
          </div>
          <div class="venue-line">
            ${e.venueType ? `<span class="type">${escH(e.venueType)}</span>` : ''}
            ${escH(e.venueDesc || '')}
          </div>
          <div class="aims-chips">${chips}</div>
        </div>
        <div class="right-meta">
          <span class="aims-count">${aimsCount}</span>
          <span>aim${aimsCount === 1 ? '' : 's'} reflection${aimsCount === 1 ? '' : 's'}</span>
          <span class="program-tag">${escH(e.program || '')}</span>
        </div>
      </div>`;
    }).join('');

    entriesListEl.querySelectorAll('.student-entry-row').forEach(row =>
      row.addEventListener('click', () => {
        const entry = allEntries.find(x => x.id === row.getAttribute('data-entry-id'));
        if (entry) openModal(entry);
      })
    );
  }

  /* =========================================================
     MODAL
     ========================================================= */
  const AIM_NICE = {
    spiritual:    'Spiritually Strengthening',
    intellectual: 'Intellectually Enlarging',
    character:    'Character Building',
    service:      'Lifelong Learning &amp; Service'
  };

  function openModal(e) {
    const date    = e.createdAt ? new Date(e.createdAt) : null;
    const dateStr = date ? date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' }) : '';
    const term    = e.term ? ` &middot; ${escH(e.term)}` : '';

    const aimsHtml = (e.aimsResponses || []).map(r =>
      `<div class="aims-response-block ${r.aim}">
        <div class="aims-response-aim">${AIM_NICE[r.aim] || r.aim}</div>
        <div class="aims-response-prompt-label">${escH(r.promptLabel)}</div>
        <div class="aims-response-prompt-full">${escH(r.promptFull)}</div>
        <div class="aims-response-text">${escH(r.response).replace(/\n/g, '<br>')}</div>
      </div>`
    ).join('');

    modalInner.innerHTML = `
      <h2>${escH(e.venueDesc || 'Untitled')}</h2>
      <div class="modal-sub">
        ${escH(e.venueType || '')}
        &middot; ${escH(e.program || '')}
        &middot; ${escH(e.studentName || '—')} with ${escH(e.mentorName || '—')}
        &middot; ${dateStr}${term}
      </div>
      ${e.image ? `<img class="modal-img" src="${e.image}" alt="">` : ''}
      ${e.transformative ? `<div class="field">
        <div class="field-label">Transformative experience</div>
        <div class="field-content serif">${escH(e.transformative).replace(/\n/g, '<br>')}</div>
      </div>` : ''}
      ${aimsHtml ? `<div class="field"><div class="field-label">BYU Aims reflections</div>${aimsHtml}</div>` : ''}
    `;
    modalBackdrop.classList.add('show');
  }

  modalClose.addEventListener('click', () => modalBackdrop.classList.remove('show'));
  modalBackdrop.addEventListener('click', e => { if (e.target === modalBackdrop) modalBackdrop.classList.remove('show'); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') modalBackdrop.classList.remove('show'); });

  /* =========================================================
     AI SUMMARY
     ========================================================= */
  function hashEntries(entries) {
    const ids = entries.map(e => e.id).sort().join('|');
    let h = 0;
    for (let i = 0; i < ids.length; i++) h = ((h << 5) - h + ids.charCodeAt(i)) | 0;
    return entries.length + ':' + h;
  }

  async function loadOrGenerateSummary(entries) {
    if (!entries.length) {
      summaryText.classList.remove('has-content');
      summaryText.innerHTML = '<span class="empty">As students share their experiences, a synthesis will appear here.</span>';
      summaryMeta.textContent = '';
      return;
    }
    const sig = hashEntries(entries);
    try {
      const cached = await window.storage.get('student-summary:cache', true);
      if (cached && cached.value) {
        const p = JSON.parse(cached.value);
        if (p.sig === sig && p.text) { renderSummary(p.text, p.generatedAt, p.fallback); return; }
      }
    } catch (e) { /* no cache */ }

    const fallback = buildLocalSummary(entries);
    renderSummary(fallback, new Date().toISOString(), true);

    try {
      const text = await callClaudeForSummary(entries);
      const generatedAt = new Date().toISOString();
      try {
        await window.storage.set('student-summary:cache', JSON.stringify({ sig, text, generatedAt, fallback: false }), true);
      } catch (e) { /* fine */ }
      renderSummary(text, generatedAt, false);
    } catch (err) {
      console.warn('AI summary failed', err);
      try {
        await window.storage.set('student-summary:cache', JSON.stringify({ sig, text: fallback, generatedAt: new Date().toISOString(), fallback: true }), true);
      } catch (e) { /* fine */ }
    }
  }

  function renderSummary(text, generatedAt, isFallback) {
    summaryText.classList.add('has-content');
    summaryText.textContent = text;
    const date = generatedAt ? new Date(generatedAt) : null;
    const dateStr = date ? date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' }) : '';
    summaryMeta.textContent = (isFallback ? 'Composed locally' : 'AI-generated') +
      (dateStr ? ' · ' + dateStr : '') + ' · refreshes when new entries are added';
  }

  async function callClaudeForSummary(entries) {
    const compact = entries.map(e => ({
      student: e.studentName, mentor: e.mentorName, program: e.program,
      venue: e.venueDesc, venueType: e.venueType,
      transformative: (e.transformative || '').slice(0, 400),
      aims: (e.aimsResponses || []).map(r => ({ aim: r.aim, prompt: r.promptLabel, response: r.response.slice(0, 300) }))
    }));

    const prompt = `You are writing a short editorial synthesis for the BYU Department of Linguistics student mentoring archive — a public page documenting how students experienced being mentored across Linguistics, TESOL, and Editing & Publishing, organized around BYU's four institutional aims (Spiritually Strengthening, Intellectually Enlarging, Character Building, Lifelong Learning & Service).\n\nBelow are ${entries.length} student-submitted entries. Write a single paragraph of 3–5 sentences (around 75–115 words) that captures what it felt like to be mentored here: the specific kinds of moments students describe, which aims recur most, and what feels distinctive about the mentoring culture these accounts reveal. Be specific and grounded — name a theme, a type of moment, a pattern. Avoid clichés. Keep an editorial, slightly literary register. Do not begin with "This archive" or "The archive". Plain prose only, no quotation marks around your output.\n\nENTRIES:\n${JSON.stringify(compact)}`;

    // Try serverless function first
    try {
      const r = await fetch('/api/summary', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ entries: compact }) });
      if (r.ok) { const d = await r.json(); if (d && d.text) return d.text; }
    } catch (e) { /* fall through */ }

    // Direct API call
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model: 'claude-sonnet-4-20250514', max_tokens: 400, messages: [{ role: 'user', content: prompt }] })
    });
    if (!response.ok) throw new Error('API ' + response.status);
    const data = await response.json();
    const text = (data.content || []).filter(b => b.type === 'text').map(b => b.text).join('').trim();
    if (!text) throw new Error('Empty response');
    return text;
  }

  function buildLocalSummary(entries) {
    const stats = computeStats(entries);
    const topAim = Object.entries(stats.aimCounts)
      .sort((a, b) => b[1] - a[1])[0];
    const topAimName = topAim ? AIM_LABELS[topAim[0]] : '';
    return `Across ${entries.length} student accounts, ${stats.students} students describe the mentoring they received from ${stats.mentors} faculty members in ${stats.programs} programs. ` +
      (topAimName ? `The most frequently reflected aim is ${topAimName}. ` : '') +
      `Each entry below records a transformative moment, a specific conversation, and what students carry forward.`;
  }

  /* =========================================================
     UTIL
     ========================================================= */
  function escH(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  function romanize(n) {
    const map = [['m',1000],['cm',900],['d',500],['cd',400],['c',100],['xc',90],
                 ['l',50],['xl',40],['x',10],['ix',9],['v',5],['iv',4],['i',1]];
    let r = '';
    for (const [l, v] of map) { while (n >= v) { r += l; n -= v; } }
    return r;
  }

  /* =========================================================
     INIT
     ========================================================= */
  async function init() {
    allEntries = await loadEntries();

    if (!allEntries.length) {
      renderStats(computeStats([]));
      buildWordCloud([]); buildAimsBreakdown([]); buildGallery([]);
      entriesListEl.innerHTML = '<div class="entry-empty"><span class="symbol">¶</span>No entries yet.</div>';
      entriesCountEl.textContent = '0 entries';
      heroUpdated.textContent = '—';
      await loadOrGenerateSummary([]);
      return;
    }

    populateFilters(allEntries);
    renderStats(computeStats(allEntries));
    updateHero(allEntries);
    renderPullQuote(allEntries);
    buildWordCloud(allEntries);
    buildAimsBreakdown(allEntries);
    buildGallery(allEntries);
    renderEntries();
    await loadOrGenerateSummary(allEntries);
  }

  [searchEl, filterAimEl, filterVenueEl, sortEl].forEach(el => {
    el.addEventListener('input', renderEntries);
    el.addEventListener('change', renderEntries);
  });

  init();
})();
