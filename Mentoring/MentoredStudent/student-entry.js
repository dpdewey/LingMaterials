/* =========================================================
   Student entry page — handles form submission for the BYU
   brand-compliant form layout. Reads inputs by id, gathers
   aim reflections from textareas with data-aim attrs, and
   writes a backward-compatible entry shape so student-view.js
   keeps working.
   ========================================================= */

(function () {
  'use strict';

  const form = document.getElementById('student-form');
  if (!form) return;

  const fileInput = document.getElementById('image');

  const $ = function (id) { return document.getElementById(id); };
  const val = function (id) {
    const el = $(id);
    return el ? (el.value || '').trim() : '';
  };

  function generateId() {
    return 'student_' + Date.now().toString(36) + '_' + Math.random().toString(36).slice(2, 8);
  }

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

  // Privacy flags: read all data-private toggles + master "all-private"
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

  // Aim responses: pick up every textarea[data-aim]
  // Returns: [{aim, response, private}]
  function collectAimsResponses() {
    const out = [];
    form.querySelectorAll('textarea[data-aim]').forEach(function (ta) {
      const aim = ta.getAttribute('data-aim');
      const response = (ta.value || '').trim();
      if (!aim || !response) return;
      out.push({ aim: aim, response: response });
    });
    return out;
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

    showStatus('Saving reflection…', 'info');

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

      const studentName = val('student-name');
      if (!studentName) {
        showStatus('Please enter your name before saving.', 'error');
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.textContent = submitBtn.dataset.originalText || 'Submit Reflection';
        }
        return;
      }

      const anonymous = !!($('anonymous') && $('anonymous').checked);
      const privacy   = getPrivacyFlags();
      const aimsList  = collectAimsResponses();

      // Apply per-aim privacy flags
      aimsList.forEach(function (r) {
        const cb = form.querySelector('input[data-private="aim-' + r.aim + '"]');
        r.private = privacy.allPrivate || (cb && cb.checked) || false;
      });

      const venue = val('venue');
      const date  = val('date');
      const title = val('title');

      const entry = {
        id:              generateId(),
        type:            'student',
        createdAt:       new Date().toISOString(),

        studentName:     studentName,
        anonymous:       anonymous,
        showAnonymous:   anonymous,           // back-compat alias
        program:         val('program'),
        gradYear:        val('grad-year'),

        mentorName:      val('mentor-name'),

        title:           title,
        venueType:       venue,                // venue used as "type" by student-view filters
        venueDesc:       venue || title,       // venueDesc used in modal
        venue:           venue,
        date:            date,
        term:            date,                 // back-compat for view.js stats

        transformative:  val('narrative'),     // narrative → transformative for back-compat

        aimsResponses:   aimsList,

        privacyFlags:    privacy.privacyFlags,
        allPrivate:      privacy.allPrivate,

        image:           imageDataUrl,
        imageName:       imageFileName
      };

      if (!window.storage) {
        throw new Error('Storage backend is not available. Please reload the page.');
      }
      const key = 'student:' + entry.id;
      const result = await window.storage.set(key, JSON.stringify(entry), true);
      if (!result) throw new Error('Storage write returned no confirmation.');

      try {
        await window.storage.delete('student-summary:cache', true);
      } catch (e) { /* fine if there is no cache yet */ }

      showStatus('Reflection saved. Redirecting to the archive…', 'success');
      form.reset();
      setTimeout(function () { window.location.href = 'student-view.html'; }, 1200);

    } catch (err) {
      console.error('Save failed:', err);
      showStatus('Could not save reflection: ' + err.message, 'error');
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = submitBtn.dataset.originalText || 'Submit Reflection';
      }
    }
  });

})();
