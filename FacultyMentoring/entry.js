/* =========================================================
   Faculty entry page — handles form submission for the BYU
   brand-compliant form layout. Reads inputs by id (since
   the form fields use id rather than name), handles privacy
   toggles via data-private attributes, and writes a
   backward-compatible entry shape so view.js and the seed
   data both keep working.
   ========================================================= */

(function () {
  'use strict';

  const form = document.getElementById('mentoring-form');
  if (!form) return;

  const fileInput = document.getElementById('image');

  const $ = function (id) { return document.getElementById(id); };
  const val = function (id) {
    const el = $(id);
    return el ? (el.value || '').trim() : '';
  };

  function generateId() {
    return 'entry_' + Date.now().toString(36) + '_' + Math.random().toString(36).slice(2, 8);
  }

  // Inline status message (added above the form)
  function showStatus(msg, kind) {
    let el = document.getElementById('entry-status');
    if (!el) {
      el = document.createElement('div');
      el.id = 'entry-status';
      el.style.cssText =
        'margin: 1rem 0; padding: 0.875rem 1rem; border-radius: 4px; ' +
        'font-size: 0.9375rem; font-weight: 500; line-height: 1.4;';
      form.parentNode.insertBefore(el, form);
    }
    if (kind === 'success') {
      el.style.background = '#E6F4EA';
      el.style.color = '#006141';
      el.style.border = '1px solid #B7E1C7';
    } else if (kind === 'error') {
      el.style.background = '#FCE8E8';
      el.style.color = '#A3082A';
      el.style.border = '1px solid #F4B7B7';
    } else {
      el.style.background = '#F0F4FA';
      el.style.color = '#002E5D';
      el.style.border = '1px solid #C9D7E8';
    }
    el.textContent = msg;
    try { el.scrollIntoView({ behavior: 'smooth', block: 'center' }); } catch (e) {}
  }

  function getDisciplines() {
    const out = [];
    form.querySelectorAll('input[name="discipline"]:checked').forEach(function (cb) {
      out.push(cb.value);
    });
    return out;
  }

  function getMentees() {
    const raw = val('mentees');
    if (!raw) return [];
    return raw.split(/[,;\n]+/).map(function (s) { return s.trim(); }).filter(Boolean);
  }

  function getPrivacyFlags() {
    const masterEl = $('all-private');
    const isAll = !!(masterEl && masterEl.checked);
    const flags = {};
    form.querySelectorAll('input[type="checkbox"][data-private]').forEach(function (cb) {
      const key = cb.getAttribute('data-private');
      flags[key] = isAll || cb.checked;
    });
    return { allPrivate: isAll, privacyFlags: flags };
  }

  // Image: resize + compress to JPEG
  const MAX_DIMENSION = 1200;
  const COMPRESS_QUALITY = 0.78;
  function compressImage(file) {
    return new Promise(function (resolve, reject) {
      const reader = new FileReader();
      reader.onload = function (e) {
        const img = new Image();
        img.onload = function () {
          let w = img.width, h = img.height;
          if (w > MAX_DIMENSION || h > MAX_DIMENSION) {
            if (w > h) { h = Math.round(h * MAX_DIMENSION / w); w = MAX_DIMENSION; }
            else       { w = Math.round(w * MAX_DIMENSION / h); h = MAX_DIMENSION; }
          }
          const canvas = document.createElement('canvas');
          canvas.width = w; canvas.height = h;
          canvas.getContext('2d').drawImage(img, 0, 0, w, h);
          resolve(canvas.toDataURL('image/jpeg', COMPRESS_QUALITY));
        };
        img.onerror = function () { reject(new Error('Could not read image')); };
        img.src = e.target.result;
      };
      reader.onerror = function () { reject(new Error('Could not load file')); };
      reader.readAsDataURL(file);
    });
  }

  form.addEventListener('submit', async function (ev) {
    ev.preventDefault();

    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.dataset.originalText = submitBtn.textContent;
      submitBtn.textContent = 'Saving…';
    }

    showStatus('Saving entry…', 'info');

    try {
      // Optional image
      let imageDataUrl = null;
      let imageFileName = '';
      if (fileInput && fileInput.files && fileInput.files[0]) {
        try {
          imageDataUrl = await compressImage(fileInput.files[0]);
          imageFileName = fileInput.files[0].name;
        } catch (e) {
          console.warn('Image compression failed — saving without image.', e);
        }
      }

      const mentor = val('mentor-name');
      const title  = val('title');
      if (!mentor) {
        showStatus('Please enter the mentor name before saving.', 'error');
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.textContent = submitBtn.dataset.originalText || 'Save Entry';
        }
        return;
      }

      const disciplines    = getDisciplines();
      const mentees        = getMentees();
      const privacy        = getPrivacyFlags();
      const impactFaculty  = val('impact-faculty');
      const impactStudent  = val('impact-student');

      // Build a date/term string for back-compat with seed entries that use 'term'
      const dateStr = val('date');
      let term = '';
      if (dateStr) {
        try {
          const d = new Date(dateStr);
          term = d.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
        } catch (e) { term = dateStr; }
      }

      // Combined impact for the modal that expects a single field
      const impactCombined = [
        impactFaculty ? 'Faculty: ' + impactFaculty : '',
        impactStudent ? 'Student: ' + impactStudent : ''
      ].filter(Boolean).join('\n\n');

      const entry = {
        id:              generateId(),
        createdAt:       new Date().toISOString(),

        mentor:          mentor,
        mentorRole:      val('mentor-role'),

        // Keep BOTH the array and a joined string so view.js (which uses
        // a single 'discipline' string) keeps working.
        disciplines:     disciplines,
        discipline:      disciplines.join(', '),

        title:           title,
        venueType:       val('activity-type'),
        venue:           val('venue') || title,
        date:            dateStr,
        term:            term,
        location:        val('location'),

        students:        mentees,
        mentees:         mentees,
        menteeLevel:     val('mentee-level'),
        menteeCount:     val('mentee-count'),

        accomplishments: val('accomplishments'),
        notes:           val('notes'),
        impactFaculty:   impactFaculty,
        impactStudent:   impactStudent,
        impact:          impactCombined,

        privacyFlags:    privacy.privacyFlags,
        allPrivate:      privacy.allPrivate,

        image:           imageDataUrl,
        imageName:       imageFileName
      };

      if (!window.storage) {
        throw new Error('Storage backend is not available. Please reload the page.');
      }
      const key = 'mentoring:' + entry.id;
      const result = await window.storage.set(key, JSON.stringify(entry), true);
      if (!result) throw new Error('Storage write returned no confirmation.');

      try {
        await window.storage.delete('mentoring-summary:cache', true);
      } catch (e) { /* fine if there is no cache yet */ }

      showStatus('Entry saved. Redirecting to the archive…', 'success');
      form.reset();
      setTimeout(function () { window.location.href = 'view.html'; }, 1200);

    } catch (err) {
      console.error('Save failed:', err);
      showStatus('Could not save entry: ' + err.message, 'error');
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = submitBtn.dataset.originalText || 'Save Entry';
      }
    }
  });

})();
