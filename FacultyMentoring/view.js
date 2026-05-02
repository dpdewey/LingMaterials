/* =========================================================
   View page logic
   ========================================================= */

(function () {
  'use strict';

  /* -------- Stopwords -------- */
  // Comprehensive stopword list — covers articles, pronouns, modals,
  // common verbs (all tenses & forms), contractions, vague nouns,
  // and high-frequency words that don't carry topical meaning in
  // narrative/reflective writing about mentoring.
  const STOPWORDS = new Set((
    // Articles, conjunctions, prepositions
    'a an the and but or nor so yet for of in on at by to from with into onto upon ' +
    'about above across after against along among around before behind below beneath ' +
    'beside between beyond despite during except inside outside over through throughout ' +
    'under underneath until via within without near off down up out ' +
    // Pronouns & possessives (all forms)
    'i me my mine myself we us our ours ourselves you your yours yourself yourselves ' +
    'he him his himself she her hers herself it its itself they them their theirs themselves ' +
    'who whom whose which what whatever whoever whomever ' +
    // Demonstratives & determiners
    'this that these those some any all both each every either neither none many much ' +
    'few several other another such same different various certain own ' +
    // Be / have / do verbs (all tenses & forms)
    'is am are was were be been being isn aren wasn weren ' +
    'has have had having hasn haven hadn ' +
    'do does did doing done don doesn didn ' +
    // Modal verbs & contractions
    'will would shall should can could may might must ought ' +
    'won wouldn shan shouldn cannot couldn mustn mightn ' +
    // Common contractions (with apostrophes stripped by the regex)
    'im youre hes shes its were theyre ive youve weve theyve ill youll hell shell theyll ' +
    'id youd hed shed wed theyd wont didnt doesnt dont isnt arent wasnt werent ' +
    'hasnt havent hadnt cant couldnt wouldnt shouldnt mustnt mightnt shant ' +
    'thats whats whos heres theres lets ' +
    // High-frequency narrative verbs (all common forms)
    'go goes going gone went ' +
    'come comes coming came ' +
    'get gets getting got gotten ' +
    'give gives giving gave given ' +
    'take takes taking took taken ' +
    'make makes making made ' +
    'put puts putting ' +
    'see sees seeing saw seen ' +
    'know knows knowing knew known ' +
    'think thinks thinking thought ' +
    'say says saying said ' +
    'tell tells telling told ' +
    'ask asks asking asked ' +
    'find finds finding found ' +
    'feel feels feeling felt ' +
    'want wants wanting wanted ' +
    'need needs needing needed ' +
    'try tries trying tried ' +
    'use uses using used ' +
    'work works working worked ' +
    'help helps helping helped ' +
    'keep keeps keeping kept ' +
    'let lets letting ' +
    'start starts starting started ' +
    'turn turns turning turned ' +
    'leave leaves leaving left ' +
    'mean means meaning meant ' +
    'show shows showing showed shown ' +
    'hear hears hearing heard ' +
    'play plays playing played ' +
    'run runs running ran ' +
    'move moves moving moved ' +
    'live lives living lived ' +
    'believe believes believing believed ' +
    'hold holds holding held ' +
    'bring brings bringing brought ' +
    'happen happens happening happened ' +
    'write writes writing wrote written ' +
    'sit sits sitting sat ' +
    'stand stands standing stood ' +
    'lose loses losing lost ' +
    'pay pays paying paid ' +
    'meet meets meeting met ' +
    'set sets setting ' +
    'send sends sending sent ' +
    'expect expects expecting expected ' +
    'remember remembers remembering remembered ' +
    'consider considers considering considered ' +
    'become becomes becoming became ' +
    'seem seems seeming seemed ' +
    'look looks looking looked ' +
    'call calls calling called ' +
    'follow follows following followed ' +
    // Vague nouns
    'thing things something anything nothing everything someone anyone everyone noone ' +
    'somewhere anywhere everywhere nowhere ' +
    'way ways stuff bit lot lots part parts side sides kind kinds sort sorts type types ' +
    'point points piece pieces issue issues matter matters case cases reason reasons ' +
    // Time & quantity
    'time times year years month months week weeks day days hour hours minute minutes ' +
    'today tomorrow yesterday morning afternoon evening night midnight noon ' +
    'often sometimes always never usually frequently rarely occasionally already ' +
    'now then later soon early late ' +
    'ago since while during ' +
    'one two three four five six seven eight nine ten eleven twelve ' +
    'first second third fourth fifth sixth seventh ' +
    'once twice ' +
    // Quantifiers & intensifiers
    'very really quite rather pretty fairly somewhat extremely incredibly absolutely ' +
    'only just even still also too more most less least much many enough ' +
    'almost nearly approximately roughly exactly precisely ' +
    'big small large little tiny huge enormous massive ' +
    'good bad better worse best worst nice fine okay ' +
    'old new young high low long short wide narrow deep shallow ' +
    'great greater greatest ' +
    'whole entire complete full empty ' +
    // Conjunctions & discourse markers
    'because although though however therefore thus hence moreover furthermore nevertheless ' +
    'whereas whether unless until than as if when where why how ' +
    'yet still even though although while whereas given since because ' +
    'also additionally further additionally besides ' +
    'actually basically essentially generally normally typically usually ' +
    'maybe perhaps possibly probably likely surely certainly definitely obviously ' +
    'indeed truly really actually literally ' +
    // Common adverbs
    'here there everywhere anywhere somewhere ' +
    'forward backward upward downward inward outward ' +
    'together alone apart aside away back ' +
    'well however away around inside outside ' +
    // Additional narrative verbs (final pass)
    'spend spends spending spent ' +
    'read reads reading ' +
    'eat eats eating ate eaten ' +
    'watch watches watching watched ' +
    'add adds adding added ' +
    'change changes changing changed ' +
    'open opens opening opened ' +
    'close closes closing closed ' +
    'wait waits waiting waited ' +
    'walk walks walking walked ' +
    'talk talks talking talked ' +
    'speak speaks speaking spoke spoken ' +
    'answer answers answering answered ' +
    'wonder wonders wondering wondered ' +
    'realize realizes realizing realized ' +
    'understand understands understanding understood ' +
    'continue continues continuing continued ' +
    'happen happens happening happened ' +
    'allow allows allowing allowed ' +
    'agree agrees agreeing agreed ' +
    'decide decides deciding decided ' +
    'hope hopes hoping hoped ' +
    'love loves loving loved ' +
    'like likes liking liked ' +
    'mention mentions mentioning mentioned ' +
    'notice notices noticing noticed ' +
    'happen happens happened ' +
    // More quantifiers / vague descriptors
    'next previous current former latter prior recent subsequent ' +
    'else such above below behind ahead ' +
    'ever never always forever often often ' +
    'wise foolish smart stupid clever simple complex easy hard difficult ' +
    'true false correct wrong right wrong real fake ' +
    // Filler/transition that often shows up in narratives
    'instance example case scenario situation context circumstance ' +
    'particularly especially specifically generally usually probably likely ' +
    'literally truly genuinely honestly frankly basically simply easily ' +
    'mostly partly fully entirely completely totally absolutely ' +
    'either neither both together apart alone single double ' +
    // Polite/conversational filler
    'please thanks thank okay ok yes yeah yep nope alright '
  ).split(/\s+/).filter(Boolean));

  /* -------- DOM -------- */
  const $ = function (id) { return document.getElementById(id); };
  const summaryText  = $('summary-text');
  const summaryMeta  = $('summary-meta');
  const wordCloudEl  = $('word-cloud');
  const galleryEl    = $('gallery');
  const disciplineSvg = $('discipline-svg');
  const disciplineLegend = $('discipline-legend');
  const entriesListEl = $('entries-list');
  const entriesCountEl = $('entries-count');
  const searchEl     = $('search');
  const filterDiscEl = $('filter-discipline');
  const filterTypeEl = $('filter-type');
  const sortEl       = $('sort');
  const modalBackdrop = $('modal-backdrop');
  const modalInner   = $('modal-inner');
  const modalClose   = $('modal-close');
  const heroUpdated  = $('hero-updated');
  const pullQuote    = $('pull-quote');
  const pullQuoteText = $('pull-quote-text');
  const pullQuoteAttr = $('pull-quote-attr');

  // BYU palette for the radial chart
  const DISCIPLINE_COLORS = [
    '#002E5D', // navy
    '#0062B8', // blue accent
    '#A89968', // tan deep
    '#1B4079', // navy light
    '#C5B783', // tan
    '#8B6914'  // warning gold
  ];

  let allEntries = [];

  /* =========================================================
     LOAD ENTRIES (with seed-data fallback)
     ========================================================= */
  async function loadEntries() {
    let entries = [];
    try {
      const res = await window.storage.list('mentoring:', true);
      const keys = (res && res.keys) || [];
      for (const key of keys) {
        try {
          const got = await window.storage.get(key, true);
          if (got && got.value) {
            entries.push(JSON.parse(got.value));
          }
        } catch (e) {
          console.warn('Could not load entry', key, e);
        }
      }
    } catch (e) {
      console.warn('Could not list entries', e);
    }

    // If empty, seed with sample data so the archive is never blank
    if (entries.length === 0 && Array.isArray(window.SEED_ENTRIES)) {
      entries = window.SEED_ENTRIES.slice();
      // Persist seeds so the page is consistent on refresh
      // (and so anyone visiting sees the populated archive)
      seedEntries(entries);
    }

    // PRIVACY FILTERING: drop entries marked allPrivate, then redact per-field privates.
    // The original raw data stays in storage — admin page reads it untouched.
    entries = entries
      .filter(function (e) { return !e.allPrivate; })
      .map(function (e) {
        const flags = e.privacyFlags || {};
        const redacted = Object.assign({}, e);
        if (flags.accomplishments) redacted.accomplishments = '';
        if (flags.notes)           redacted.notes = '';
        if (flags.impact)          redacted.impact = '';
        return redacted;
      });

    entries.sort(function (a, b) {
      return new Date(b.createdAt) - new Date(a.createdAt);
    });
    return entries;
  }

  async function seedEntries(entries) {
    // Run in background; don't block UI
    for (const entry of entries) {
      try {
        await window.storage.set('mentoring:' + entry.id, JSON.stringify(entry), true);
      } catch (e) {
        // Storage may not be available — that's fine, we still have the data in memory
        console.warn('Could not seed', entry.id, e);
      }
    }
  }

  /* =========================================================
     STATS
     ========================================================= */
  function computeStats(entries) {
    const mentors = new Set();
    const students = new Set();
    const projects = new Set();
    const disciplines = new Set();
    entries.forEach(function (e) {
      if (e.mentor) mentors.add(e.mentor.toLowerCase().trim());
      if (e.venue) projects.add((e.mentor || '') + '|' + e.venue);
      if (e.discipline) disciplines.add(e.discipline);
      (e.students || []).forEach(function (s) {
        if (s) students.add(s.toLowerCase().trim());
      });
    });
    return {
      mentors: mentors.size,
      students: students.size,
      projects: projects.size,
      disciplines: disciplines.size
    };
  }

  function renderStats(s) {
    animateCount($('stat-mentors'), s.mentors);
    animateCount($('stat-students'), s.students);
    animateCount($('stat-projects'), s.projects);
    animateCount($('stat-disciplines'), s.disciplines);
  }

  function animateCount(el, target) {
    const duration = 900;
    const start = performance.now();
    function tick(now) {
      const t = Math.min(1, (now - start) / duration);
      const eased = 1 - Math.pow(1 - t, 3);
      el.textContent = Math.floor(eased * target);
      if (t < 1) requestAnimationFrame(tick);
      else el.textContent = target;
    }
    requestAnimationFrame(tick);
  }

  /* =========================================================
     HERO META
     ========================================================= */
  function updateHero(entries) {
    if (!entries.length) { heroUpdated.textContent = '—'; return; }
    const latest = entries.reduce(function (a, b) {
      return new Date(a.createdAt) > new Date(b.createdAt) ? a : b;
    });
    heroUpdated.textContent = new Date(latest.createdAt)
      .toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
  }

  /* =========================================================
     PULL QUOTE — extract a striking sentence
     ========================================================= */
  function findPullQuote(entries) {
    if (!entries.length) return null;

    // Prefer sentences from notes that contain certain emotional/scholarly markers
    const candidates = [];
    entries.forEach(function (e) {
      if (!e.notes) return;
      // Split into sentences
      const sentences = e.notes.split(/(?<=[.!?])\s+/);
      sentences.forEach(function (s) {
        const text = s.trim();
        // Looking for the sweet spot: long enough to be meaningful, short enough to display
        if (text.length < 60 || text.length > 220) return;
        let score = 0;
        // Emotional/reflective markers boost the score
        const markers = [
          /\b(proud|love|moment|remember|never|always|truly|finally|gift|honored|grateful|miracle|wonderful|extraordinary)\b/i,
          /\b(walked in|walked out|came back|went home)\b/i,
          /\b(I will|I am|I have|I keep)\b/,
          /\bkind of\b/i
        ];
        markers.forEach(function (m) { if (m.test(text)) score += 1; });
        // Sentences mentioning a student by name are golden
        (e.students || []).forEach(function (name) {
          const first = (name.split(/\s+/)[0] || '').trim();
          if (first.length > 2 && new RegExp('\\b' + first + '\\b').test(text)) score += 2;
        });
        if (score > 0) candidates.push({ text: text, mentor: e.mentor, venue: e.venue, score: score });
      });
    });

    if (!candidates.length) return null;
    candidates.sort(function (a, b) { return b.score - a.score; });
    // Add a tiny bit of variety — pick from the top 3
    const top = candidates.slice(0, 3);
    return top[Math.floor(Math.random() * top.length)];
  }

  function renderPullQuote(entries) {
    const q = findPullQuote(entries);
    if (!q) { pullQuote.style.display = 'none'; return; }
    pullQuoteText.textContent = '\u201C' + q.text + '\u201D';
    pullQuoteAttr.textContent = q.mentor + ' \u00B7 ' + q.venue;
    pullQuote.style.display = 'block';
  }

  /* =========================================================
     WORD CLOUD
     ========================================================= */
  function buildWordCloud(entries) {
    const counts = {};
    entries.forEach(function (e) {
      const text = [e.venue, e.accomplishments, e.notes].filter(Boolean).join(' ');
      const words = text
        .toLowerCase()
        .replace(/[^a-záéíóúñü'\-\s]/g, ' ')
        .split(/\s+/);
      words.forEach(function (w) {
        if (!w) return;
        // Strip ALL apostrophes (so didn't → didnt, students' → students)
        // and trim leading/trailing hyphens
        w = w.replace(/'/g, '').replace(/^-+|-+$/g, '');
        if (w.length < 4) return;
        if (STOPWORDS.has(w)) return;
        if (/\d/.test(w)) return;
        counts[w] = (counts[w] || 0) + 1;
      });
    });

    const top = Object.entries(counts)
      .sort(function (a, b) { return b[1] - a[1]; })
      .slice(0, 42);

    if (!top.length) {
      wordCloudEl.innerHTML = '<span class="empty">Themes will appear as entries are added.</span>';
      return;
    }

    const maxCount = top[0][1];
    const minCount = top[top.length - 1][1];
    const range = Math.max(1, maxCount - minCount);
    const shuffled = top.slice().sort(function () { return Math.random() - 0.5; });

    wordCloudEl.innerHTML = shuffled.map(function (pair) {
      const word = pair[0];
      const count = pair[1];
      const t = (count - minCount) / range;
      const fontSize = (15 + t * 38).toFixed(1);
      const color = t > 0.66 ? 'var(--byu-navy)' :
                    t > 0.33 ? 'var(--byu-royal)' :
                               'var(--byu-navy-soft)';
      const opacity = (0.55 + t * 0.45).toFixed(2);
      const cap = word.charAt(0).toUpperCase() + word.slice(1);
      return '<span title="' + count + ' mention' + (count === 1 ? '' : 's') +
             '" style="font-size:' + fontSize + 'px; color:' + color + '; opacity:' + opacity + ';">' +
             cap + '</span>';
    }).join('');
  }

  /* =========================================================
     RADIAL DISCIPLINE CHART (donut)
     ========================================================= */
  function buildDisciplineChart(entries) {
    const counts = {};
    entries.forEach(function (e) {
      if (!e.discipline) return;
      counts[e.discipline] = (counts[e.discipline] || 0) + 1;
    });
    const sorted = Object.entries(counts).sort(function (a, b) { return b[1] - a[1]; });

    if (!sorted.length) {
      disciplineSvg.innerHTML = '<text x="100" y="105" text-anchor="middle" font-family="Crimson Pro, serif" font-style="italic" fill="#6B7385" font-size="13">no data yet</text>';
      disciplineLegend.innerHTML = '';
      return;
    }

    const total = sorted.reduce(function (s, p) { return s + p[1]; }, 0);
    const cx = 100, cy = 100, r = 80, ir = 50;

    let angleStart = -Math.PI / 2; // start at top
    const arcs = [];
    sorted.forEach(function (pair, i) {
      const value = pair[1];
      const sweep = (value / total) * 2 * Math.PI;
      const angleEnd = angleStart + sweep;
      arcs.push({
        name: pair[0],
        count: value,
        color: DISCIPLINE_COLORS[i % DISCIPLINE_COLORS.length],
        start: angleStart,
        end: angleEnd
      });
      angleStart = angleEnd;
    });

    // Build SVG paths for each arc
    function arcPath(start, end) {
      const sx1 = cx + r * Math.cos(start);
      const sy1 = cy + r * Math.sin(start);
      const sx2 = cx + r * Math.cos(end);
      const sy2 = cy + r * Math.sin(end);
      const ix1 = cx + ir * Math.cos(end);
      const iy1 = cy + ir * Math.sin(end);
      const ix2 = cx + ir * Math.cos(start);
      const iy2 = cy + ir * Math.sin(start);
      const largeArc = (end - start) > Math.PI ? 1 : 0;
      return [
        'M', sx1, sy1,
        'A', r, r, 0, largeArc, 1, sx2, sy2,
        'L', ix1, iy1,
        'A', ir, ir, 0, largeArc, 0, ix2, iy2,
        'Z'
      ].join(' ');
    }

    let svg = '';
    arcs.forEach(function (a) {
      svg += '<path d="' + arcPath(a.start, a.end) + '" fill="' + a.color + '" stroke="#FAF6EC" stroke-width="2"/>';
    });
    // Center number
    svg += '<text x="' + cx + '" y="' + (cy - 4) + '" text-anchor="middle" font-family="Crimson Pro, serif" font-weight="600" fill="#002E5D" font-size="34" letter-spacing="-1">' + total + '</text>';
    svg += '<text x="' + cx + '" y="' + (cy + 16) + '" text-anchor="middle" font-family="Crimson Pro, serif" font-style="italic" fill="#6B7385" font-size="11">entries</text>';
    disciplineSvg.innerHTML = svg;

    disciplineLegend.innerHTML = arcs.map(function (a) {
      const pct = Math.round((a.count / total) * 100);
      return '<div class="discipline-row">' +
             '<div class="swatch" style="background: ' + a.color + ';"></div>' +
             '<div class="name">' + escapeHtml(a.name) + '</div>' +
             '<div class="count">' + a.count + ' &middot; ' + pct + '%</div>' +
             '</div>';
    }).join('');
  }

  /* =========================================================
     GALLERY
     ========================================================= */
  function buildGallery(entries) {
    // Only include entries with a non-empty image string. We also test-load each
    // image to drop any whose src is broken/unrenderable so we don't show the
    // broken-image icon + alt text in the grid.
    const withImages = entries.filter(function (e) {
      return e.image && typeof e.image === 'string' && e.image.length > 100;
    });
    if (!withImages.length) {
      galleryEl.innerHTML = '<div class="gallery-empty">Photos shared by mentors will appear here.</div>';
      return;
    }

    const items = withImages.slice(0, 9);
    // Render with empty alt so a broken image shows nothing rather than alt text
    galleryEl.innerHTML = items.map(function (e) {
      return '<div class="gallery-item" data-entry-id="' + e.id + '">' +
             '<img src="' + e.image + '" alt="" loading="lazy" onerror="this.parentElement.style.display=\'none\'">' +
             '<div class="caption">' + escapeHtml(e.venue || '') + ' &middot; ' + escapeHtml(e.mentor || '') + '</div>' +
             '</div>';
    }).join('');
    // After image load attempts settle, if every tile got hidden, show empty state
    setTimeout(function () {
      const visible = Array.from(galleryEl.querySelectorAll('.gallery-item'))
        .filter(function (el) { return el.style.display !== 'none'; });
      if (!visible.length) {
        galleryEl.innerHTML = '<div class="gallery-empty">Photos shared by mentors will appear here.</div>';
      }
    }, 600);
    galleryEl.querySelectorAll('.gallery-item').forEach(function (el) {
      el.addEventListener('click', function () {
        const id = el.getAttribute('data-entry-id');
        const entry = allEntries.find(function (x) { return x.id === id; });
        if (entry) openModal(entry);
      });
    });
  }

  /* =========================================================
     ENTRIES LIST
     ========================================================= */
  function populateFilters(entries) {
    const disciplines = new Set();
    const types = new Set();
    entries.forEach(function (e) {
      if (e.discipline) disciplines.add(e.discipline);
      if (e.venueType)  types.add(e.venueType);
    });
    function fill(sel, set, defaultLabel) {
      const current = sel.value;
      sel.innerHTML = '<option value="">' + defaultLabel + '</option>';
      Array.from(set).sort().forEach(function (v) {
        const opt = document.createElement('option');
        opt.value = v;
        opt.textContent = v;
        sel.appendChild(opt);
      });
      sel.value = current;
    }
    fill(filterDiscEl, disciplines, 'All disciplines');
    fill(filterTypeEl, types, 'All types');
  }

  function getFilteredSorted() {
    const q = (searchEl.value || '').trim().toLowerCase();
    const disc = filterDiscEl.value;
    const type = filterTypeEl.value;
    let list = allEntries.filter(function (e) {
      if (disc && e.discipline !== disc) return false;
      if (type && e.venueType !== type) return false;
      if (q) {
        const blob = [
          e.mentor, e.venue, e.venueType, e.discipline, e.term,
          (e.students || []).join(' '),
          e.accomplishments, e.notes
        ].join(' ').toLowerCase();
        if (blob.indexOf(q) === -1) return false;
      }
      return true;
    });

    const sort = sortEl.value;
    list.sort(function (a, b) {
      switch (sort) {
        case 'date-asc':       return new Date(a.createdAt) - new Date(b.createdAt);
        case 'date-desc':      return new Date(b.createdAt) - new Date(a.createdAt);
        case 'mentor-asc':     return (a.mentor || '').localeCompare(b.mentor || '');
        case 'mentor-desc':    return (b.mentor || '').localeCompare(a.mentor || '');
        case 'venue-asc':      return (a.venue || '').localeCompare(b.venue || '');
        case 'students-desc':  return (b.students || []).length - (a.students || []).length;
        case 'discipline-asc': return (a.discipline || '').localeCompare(b.discipline || '');
        default:               return 0;
      }
    });
    return list;
  }

  function renderEntries() {
    const list = getFilteredSorted();
    entriesCountEl.textContent = list.length + ' of ' + allEntries.length + ' entries shown';

    if (!list.length) {
      entriesListEl.innerHTML = '<div class="entry-empty"><span class="symbol">¶</span>No entries match those filters.</div>';
      return;
    }

    entriesListEl.innerHTML = list.map(function (e, i) {
      const studentCount = (e.students || []).length;
      const date = e.createdAt ? new Date(e.createdAt) : null;
      const dateStr = date ? date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' }) : '';
      const studentsPreview = (e.students || []).slice(0, 4).join(', ') +
                              (studentCount > 4 ? ', +' + (studentCount - 4) + ' more' : '');
      const term = e.term ? ' &middot; ' + escapeHtml(e.term) : '';
      const num = romanize(i + 1);
      return '<div class="entry-row" data-entry-id="' + e.id + '">' +
             '<div class="row-num">' + num + '</div>' +
             '<div class="meta">' +
               '<div class="mentor-line">' +
                 '<span class="mentor-name">' + escapeHtml(e.mentor || 'Anonymous mentor') + '</span>' +
                 '<span class="date">' + dateStr + term + '</span>' +
               '</div>' +
               '<div class="project">' +
                 (e.venueType ? '<span class="type">' + escapeHtml(e.venueType) + '</span>' : '') +
                 escapeHtml(e.venue || '') +
               '</div>' +
               '<div class="students">With ' + escapeHtml(studentsPreview || '—') + '</div>' +
             '</div>' +
             '<div class="right-meta">' +
               '<span class="student-count">' + studentCount + '</span>' +
               '<span>' + (studentCount === 1 ? 'student' : 'students') + '</span>' +
               '<span class="discipline-tag">' + escapeHtml(e.discipline || '') + '</span>' +
             '</div>' +
             '</div>';
    }).join('');

    entriesListEl.querySelectorAll('.entry-row').forEach(function (row) {
      row.addEventListener('click', function () {
        const id = row.getAttribute('data-entry-id');
        const entry = allEntries.find(function (x) { return x.id === id; });
        if (entry) openModal(entry);
      });
    });
  }

  function romanize(num) {
    const map = [
      ['M', 1000], ['CM', 900], ['D', 500], ['CD', 400], ['C', 100],
      ['XC', 90], ['L', 50], ['XL', 40], ['X', 10], ['IX', 9],
      ['V', 5], ['IV', 4], ['I', 1]
    ];
    let result = '';
    for (const [letter, value] of map) {
      while (num >= value) { result += letter; num -= value; }
    }
    return result.toLowerCase();
  }

  /* =========================================================
     MODAL
     ========================================================= */
  function openModal(e) {
    const date = e.createdAt ? new Date(e.createdAt) : null;
    const dateStr = date ? date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' }) : '';
    const term = e.term ? ' &middot; ' + escapeHtml(e.term) : '';
    const fields = [];
    fields.push(
      '<h2>' + escapeHtml(e.venue || 'Untitled') + '</h2>',
      '<div class="modal-sub">' +
        escapeHtml(e.venueType || '') +
        (e.discipline ? ' &middot; ' + escapeHtml(e.discipline) : '') +
        ' &middot; mentored by ' + escapeHtml(e.mentor || '—') +
        ' &middot; ' + dateStr + term +
      '</div>'
    );
    if (e.image) fields.push('<img class="modal-img" src="' + e.image + '" alt="">');
    fields.push(
      '<div class="field"><div class="field-label">Students mentored (' + (e.students || []).length + ')</div>' +
        '<div class="field-content">' + escapeHtml((e.students || []).join(', ') || '—') + '</div></div>'
    );
    if (e.accomplishments) {
      fields.push(
        '<div class="field"><div class="field-label">Accomplishments</div>' +
          '<div class="field-content">' + escapeHtml(e.accomplishments).replace(/\n/g, '<br>') + '</div></div>'
      );
    }
    if (e.notes) {
      fields.push(
        '<div class="field"><div class="field-label">Mentor reflection</div>' +
          '<div class="field-content serif">' + escapeHtml(e.notes).replace(/\n/g, '<br>') + '</div></div>'
      );
    }
    if (e.impact) {
      fields.push(
        '<div class="field"><div class="field-label">Personal impact</div>' +
          '<div class="field-content serif">' + escapeHtml(e.impact).replace(/\n/g, '<br>') + '</div></div>'
      );
    }
    modalInner.innerHTML = fields.join('');
    modalBackdrop.classList.add('active');
  }

  function closeModal() {
    modalBackdrop.classList.remove('active');
  }
  modalClose.addEventListener('click', closeModal);
  modalBackdrop.addEventListener('click', function (e) {
    if (e.target === modalBackdrop) closeModal();
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeModal();
  });

  /* =========================================================
     AI SUMMARY
     ========================================================= */
  function hashEntries(entries) {
    const ids = entries.map(function (e) { return e.id; }).sort().join('|');
    let h = 0;
    for (let i = 0; i < ids.length; i++) {
      h = ((h << 5) - h + ids.charCodeAt(i)) | 0;
    }
    return entries.length + ':' + h;
  }

  async function loadOrGenerateSummary(entries) {
    if (!entries.length) {
      summaryText.classList.remove('has-content');
      summaryText.innerHTML = '<span class="empty">As mentors document their work, a synthesis of the archive will appear here.</span>';
      summaryMeta.textContent = '';
      return;
    }

    const sig = hashEntries(entries);

    // Try cache
    try {
      const cached = await window.storage.get('mentoring-summary:cache', true);
      if (cached && cached.value) {
        const parsed = JSON.parse(cached.value);
        if (parsed.sig === sig && parsed.text) {
          renderSummary(parsed.text, parsed.generatedAt, parsed.fallback);
          return;
        }
      }
    } catch (e) { /* no cache yet */ }

    // Show local fallback IMMEDIATELY so the page is alive
    const fallbackText = buildLocalSummary(entries);
    renderSummary(fallbackText, new Date().toISOString(), true);

    // Then try to upgrade to AI summary in the background
    try {
      const text = await callClaudeForSummary(entries);
      const generatedAt = new Date().toISOString();
      try {
        await window.storage.set('mentoring-summary:cache', JSON.stringify({
          sig: sig, text: text, generatedAt: generatedAt, fallback: false
        }), true);
      } catch (e) { /* cache write failed — fine */ }
      renderSummary(text, generatedAt, false);
    } catch (err) {
      console.warn('AI summary failed, keeping local fallback', err);
      // Cache the local fallback so we don't keep retrying
      try {
        await window.storage.set('mentoring-summary:cache', JSON.stringify({
          sig: sig, text: fallbackText, generatedAt: new Date().toISOString(), fallback: true
        }), true);
      } catch (e) { /* fine */ }
    }
  }

  function renderSummary(text, generatedAt, isFallback) {
    summaryText.classList.add('has-content');
    summaryText.textContent = text;
    const date = generatedAt ? new Date(generatedAt) : null;
    const dateStr = date ? date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' }) : '';
    summaryMeta.textContent = (isFallback ? 'Composed locally' : 'AI-generated') +
                              (dateStr ? ' \u00B7 ' + dateStr : '') +
                              ' \u00B7 refreshes when new entries are added';
  }

  async function callClaudeForSummary(entries) {
    const compact = entries.map(function (e) {
      return {
        mentor: e.mentor,
        venue: e.venue,
        venueType: e.venueType,
        discipline: e.discipline,
        term: e.term,
        studentCount: (e.students || []).length,
        accomplishments: (e.accomplishments || '').slice(0, 600),
        notes: (e.notes || '').slice(0, 600)
      };
    });

    // Try the serverless function endpoint first.
    // Works on Netlify (/.netlify/functions/summary), Vercel (/api/summary),
    // Cloudflare (/api/summary). We try /api/summary first because most hosts
    // can rewrite to it; Netlify users can add a redirect.
    try {
      const response = await fetch('/api/summary', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ entries: compact })
      });
      if (response.ok) {
        const data = await response.json();
        if (data && data.text) return data.text;
      }
      // 404 / 5xx — fall through to direct call
    } catch (e) {
      // Network error or no function deployed — fall through
    }

    // Fallback: direct call to Anthropic API.
    // This only works in environments that have an authenticated client
    // (e.g., Claude artifacts) — won't work on a plain static host.
    const prompt =
      'You are writing a short editorial synthesis for the BYU Department of Linguistics ' +
      'mentoring archive — a public page documenting how faculty have mentored students across ' +
      'Linguistics, TESOL, and Editing & Publishing.\n\n' +
      'Below are ' + entries.length + ' mentor-submitted entries. Write a single paragraph of ' +
      '3–5 sentences (around 75–115 words) that captures the texture of this body of work: ' +
      'what mentors and students are doing together, what kinds of accomplishments recur, and ' +
      'what feels distinctive. Be specific where you can — name a few projects, themes, or ' +
      'kinds of work. Avoid clichés ("dedicated faculty", "exciting opportunities"). Keep an ' +
      'editorial, slightly literary register that fits a department of linguists, TESOL teachers, ' +
      'and editors. Do not begin with "This archive" or "The archive". Do not use a bulleted list. ' +
      'Write in plain prose only. No quotation marks around your output.\n\n' +
      'ENTRIES (JSON):\n' + JSON.stringify(compact, null, 0);

    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 400,
        messages: [{ role: 'user', content: prompt }]
      })
    });

    if (!response.ok) {
      throw new Error('API returned ' + response.status);
    }
    const data = await response.json();
    const text = (data.content || [])
      .filter(function (b) { return b.type === 'text'; })
      .map(function (b) { return b.text; })
      .join('')
      .trim();
    if (!text) throw new Error('No text in response');
    return text;
  }

  function buildLocalSummary(entries) {
    const stats = computeStats(entries);
    const disciplineCounts = {};
    entries.forEach(function (e) {
      if (e.discipline) disciplineCounts[e.discipline] = (disciplineCounts[e.discipline] || 0) + 1;
    });
    const topDisciplines = Object.entries(disciplineCounts)
      .sort(function (a, b) { return b[1] - a[1]; })
      .slice(0, 3)
      .map(function (p) { return p[0]; });
    const venueTypes = {};
    entries.forEach(function (e) {
      if (e.venueType) venueTypes[e.venueType] = (venueTypes[e.venueType] || 0) + 1;
    });
    const topVenues = Object.entries(venueTypes)
      .sort(function (a, b) { return b[1] - a[1]; })
      .slice(0, 3)
      .map(function (p) { return p[0].toLowerCase(); });

    return 'Across ' + stats.projects + ' venues, ' + stats.mentors +
      ' mentors have worked alongside ' + stats.students + ' students' +
      (topDisciplines.length ? ' in ' + topDisciplines.join(', ') : '') + '. ' +
      (topVenues.length ? 'Their work spans ' + topVenues.join(', ') + '. ' : '') +
      'Each entry below records the project, the people, and what mentors most want remembered.';
  }

  /* =========================================================
     UTIL
     ========================================================= */
  function escapeHtml(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }
  function escapeAttr(s) { return escapeHtml(s); }

  /* =========================================================
     INIT
     ========================================================= */
  async function init() {
    allEntries = await loadEntries();

    if (!allEntries.length) {
      renderStats({ mentors: 0, students: 0, projects: 0, disciplines: 0 });
      buildWordCloud([]);
      buildDisciplineChart([]);
      buildGallery([]);
      entriesListEl.innerHTML = '<div class="entry-empty"><span class="symbol">¶</span>No entries yet. As mentors submit, this archive will populate.</div>';
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
    buildDisciplineChart(allEntries);
    buildGallery(allEntries);
    renderEntries();
    await loadOrGenerateSummary(allEntries);
  }

  [searchEl, filterDiscEl, filterTypeEl, sortEl].forEach(function (el) {
    el.addEventListener('input', renderEntries);
    el.addEventListener('change', renderEntries);
  });

  init();

})();
