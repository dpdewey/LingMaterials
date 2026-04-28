/* =========================================================
   Student entry page JS
   - Accordion aim cards with animated expand/collapse
   - Prompt tile selection (one active per aim)
   - Image compression and preview
   - Form validation and submission to shared storage
   ========================================================= */

(function () {
  'use strict';

  /* -------- Prompt metadata -------- */
  const PROMPTS = {
    spiritual: {
      'shared-prayer': {
        label: 'The Shared Prayer',
        full: 'Has there been a specific instance where a mentor invited spiritual reflection, shared a personal testimony, or prayed with you during a time of academic or personal struggle? What impact did that have on your perspective?'
      },
      'gospel-lens': {
        label: 'The Gospel Lens',
        full: 'Can you identify a specific conversation where a mentor helped you see a connection between your academic field and a gospel principle that you hadn\'t considered before?'
      },
      'spiritual-model': {
        label: 'The Spiritual Model',
        full: 'Describe a specific time you saw this faculty member handle a professional challenge or disagreement. How did their behavior model Christlike character or spiritual maturity in that moment?'
      }
    },
    intellectual: {
      'rigorous-standard': {
        label: 'The Rigorous Standard',
        full: 'Describe a moment when a mentor refused to let you settle for a "good enough" answer. How did they challenge you to think more deeply or more critically while still making you feel capable of reaching that higher level?'
      },
      'breakthrough': {
        label: 'The Breakthrough',
        full: 'Recall a moment when you felt a sudden "click" in your understanding or confidence. How did this faculty member facilitate that specific breakthrough?'
      },
      'deep-dive': {
        label: 'The Deep Dive',
        full: 'Think of a time when a faculty member\'s enthusiasm for a topic made you want to learn more on your own. What exactly did they do to spark that curiosity?'
      }
    },
    character: {
      'acts-kindness': {
        label: 'Acts of Kindness',
        full: 'Describe a specific small act of kindness or service this mentor performed for you or a peer that had nothing to do with your coursework, but everything to do with your well-being.'
      },
      'hidden-lesson': {
        label: 'The Hidden Lesson',
        full: 'What is one specific habit or professional "trick of the trade" you have adopted solely because you saw this faculty member doing it?'
      },
      'vulnerable-expert': {
        label: 'The Vulnerable Expert',
        full: 'Describe an instance where your mentor admitted a mistake or shared a personal setback. How did their honesty influence your own view of integrity and growth?'
      }
    },
    service: {
      'pivot': {
        label: 'The Pivot',
        full: 'Describe a specific conversation or meeting with this faculty member that fundamentally changed how you approached a project or your career goals. What exactly did they say or do?'
      },
      'rescue': {
        label: 'The Rescue',
        full: 'Tell me about a time you were struggling with a difficult concept, a failed study, or a setback. What specific steps did the faculty member take to help you navigate that situation and keep moving forward?'
      },
      'open-door': {
        label: 'The Open Door',
        full: 'Describe a specific instance where you needed guidance outside of a scheduled meeting. How did the faculty member\'s response influence your desire to support others in the same way?'
      },
      'service-bridge': {
        label: 'The Service Bridge',
        full: 'Can you share an instance where your mentor helped you see how your specific academic skills could be used to serve your community or the Church?'
      }
    }
  };

  /* -------- Accordion behavior -------- */
  document.querySelectorAll('.aim-card').forEach(function (card) {
    const header = card.querySelector('.aim-header');
    const body   = card.querySelector('.aim-body');
    const chevron = card.querySelector('.aim-chevron');

    header.addEventListener('click', function () {
      const isOpen = !body.hidden;
      if (isOpen) {
        body.hidden = true;
        header.setAttribute('aria-expanded', 'false');
        card.classList.remove('open');
      } else {
        body.hidden = false;
        header.setAttribute('aria-expanded', 'true');
        card.classList.add('open');
      }
    });
  });

  /* -------- Prompt tile selection -------- */
  document.querySelectorAll('.prompt-tile').forEach(function (tile) {
    tile.addEventListener('click', function () {
      const aim    = tile.getAttribute('data-aim');
      const prompt = tile.getAttribute('data-prompt');

      // Deselect siblings in this aim
      document.querySelectorAll('.prompt-tile[data-aim="' + aim + '"]').forEach(function (t) {
        t.classList.remove('selected');
      });

      tile.classList.add('selected');

      // Show the response area
      const responseArea = document.getElementById('response-' + aim);
      const selectedLabel = document.getElementById('selected-' + aim);
      const fullPromptEl  = document.getElementById('fullprompt-' + aim);

      if (responseArea) {
        const meta = PROMPTS[aim] && PROMPTS[aim][prompt];
        if (meta) {
          selectedLabel.textContent = meta.label;
          fullPromptEl.textContent  = meta.full;
        }
        responseArea.hidden = false;
        // Scroll the textarea into comfortable view
        setTimeout(function () {
          responseArea.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }, 80);
      }

      // Store which prompt is selected on the tile's parent aim card
      const card = tile.closest('.aim-card');
      card.setAttribute('data-selected-prompt', prompt);
      card.setAttribute('data-selected-prompt-label', PROMPTS[aim][prompt].label);
    });
  });

  /* -------- Image handling -------- */
  const dropzone    = document.getElementById('dropzone');
  const fileInput   = document.getElementById('image');
  const previewWrap = document.getElementById('preview-wrap');
  const previewImg  = document.getElementById('preview-img');
  const previewName = document.getElementById('preview-name');
  const previewSize = document.getElementById('preview-size');
  const removeBtn   = document.getElementById('remove-img');

  const MAX_BYTES = 4 * 1024 * 1024;
  const MAX_DIM   = 1200;
  const QUALITY   = 0.78;

  let imageDataUrl  = null;
  let imageFileName = '';

  function fmtSize(b) {
    if (b < 1024) return b + ' B';
    if (b < 1048576) return (b / 1024).toFixed(1) + ' KB';
    return (b / 1048576).toFixed(1) + ' MB';
  }

  function compressImage(file) {
    return new Promise(function (res, rej) {
      const reader = new FileReader();
      reader.onload = function (e) {
        const img = new Image();
        img.onload = function () {
          let w = img.width, h = img.height;
          if (w > MAX_DIM || h > MAX_DIM) {
            if (w > h) { h = Math.round(h * MAX_DIM / w); w = MAX_DIM; }
            else       { w = Math.round(w * MAX_DIM / h); h = MAX_DIM; }
          }
          const c = document.createElement('canvas');
          c.width = w; c.height = h;
          c.getContext('2d').drawImage(img, 0, 0, w, h);
          res(c.toDataURL('image/jpeg', QUALITY));
        };
        img.onerror = function () { rej(new Error('Could not read image')); };
        img.src = e.target.result;
      };
      reader.onerror = function () { rej(new Error('File read failed')); };
      reader.readAsDataURL(file);
    });
  }

  function handleFile(file) {
    if (!file) return;
    if (!/^image\/(jpeg|png|webp)$/.test(file.type)) {
      showToast('Please choose a JPG, PNG, or WEBP image.', 'error'); return;
    }
    if (file.size > MAX_BYTES) {
      showToast('Image is larger than 4 MB.', 'error'); return;
    }
    imageFileName = file.name;
    compressImage(file).then(function (dataUrl) {
      imageDataUrl = dataUrl;
      previewImg.src = dataUrl;
      previewName.textContent = file.name;
      const approx = Math.round((dataUrl.length - 22) * 3 / 4);
      previewSize.textContent = fmtSize(file.size) + ' → ' + fmtSize(approx) + ' (compressed)';
      previewWrap.style.display = 'flex';
    }).catch(function (err) {
      showToast('Image processing failed: ' + err.message, 'error');
    });
  }

  fileInput.addEventListener('change', function (e) { handleFile(e.target.files[0]); });
  ['dragenter', 'dragover'].forEach(function (ev) {
    dropzone.addEventListener(ev, function (e) { e.preventDefault(); dropzone.classList.add('drag'); });
  });
  ['dragleave', 'drop'].forEach(function (ev) {
    dropzone.addEventListener(ev, function (e) { e.preventDefault(); dropzone.classList.remove('drag'); });
  });
  dropzone.addEventListener('drop', function (e) {
    if (e.dataTransfer.files && e.dataTransfer.files[0]) handleFile(e.dataTransfer.files[0]);
  });
  removeBtn.addEventListener('click', function () {
    imageDataUrl = null; imageFileName = ''; fileInput.value = '';
    previewWrap.style.display = 'none';
  });

  /* -------- Toast -------- */
  const toastEl = document.getElementById('toast');
  function showToast(msg, kind) {
    toastEl.textContent = msg;
    toastEl.className = 'toast show' + (kind ? ' ' + kind : '');
    clearTimeout(showToast._t);
    showToast._t = setTimeout(function () { toastEl.className = 'toast'; }, 3800);
  }

  /* -------- Collect Aims responses -------- */
  function collectAimsResponses() {
    const responses = [];
    document.querySelectorAll('.aim-card').forEach(function (card) {
      const aim    = card.getAttribute('data-aim');
      const prompt = card.getAttribute('data-selected-prompt');
      const label  = card.getAttribute('data-selected-prompt-label');
      if (!prompt) return;
      const ta = card.querySelector('.prompt-textarea');
      const text = ta ? ta.value.trim() : '';
      if (!text) return;
      const fullPromptMeta = PROMPTS[aim] && PROMPTS[aim][prompt];
      responses.push({
        aim:        aim,
        promptKey:  prompt,
        promptLabel: label || '',
        promptFull: fullPromptMeta ? fullPromptMeta.full : '',
        response:   text
      });
    });
    return responses;
  }

  /* -------- ID -------- */
  function generateId() {
    return 'student_' + Date.now().toString(36) + '_' + Math.random().toString(36).slice(2, 8);
  }

  /* -------- Submit -------- */
  const form      = document.getElementById('student-form');
  const submitBtn = document.getElementById('submit-btn');

  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    submitBtn.disabled = true;
    submitBtn.textContent = 'Submitting…';

    const fd = new FormData(form);
    const aimsResponses = collectAimsResponses();

    const entry = {
      id:              generateId(),
      type:            'student',
      studentName:     (fd.get('studentName') || '').toString().trim(),
      mentorName:      (fd.get('mentorName') || '').toString().trim(),
      program:         (fd.get('program') || '').toString().trim(),
      term:            (fd.get('term') || '').toString().trim(),
      venueType:       (fd.get('venueType') || '').toString().trim(),
      venueDesc:       (fd.get('venueDesc') || '').toString().trim(),
      transformative:  (fd.get('transformative') || '').toString().trim(),
      aimsResponses:   aimsResponses,
      image:           imageDataUrl,
      imageName:       imageFileName,
      createdAt:       new Date().toISOString()
    };

    // Basic validation
    if (!entry.studentName || !entry.mentorName || !entry.program ||
        !entry.venueType || !entry.venueDesc || !entry.transformative) {
      showToast('Please fill in all required fields.', 'error');
      submitBtn.disabled = false;
      submitBtn.innerHTML = 'Submit My Experience <span class="arrow">→</span>';
      return;
    }

    try {
      const key    = 'student:' + entry.id;
      const result = await window.storage.set(key, JSON.stringify(entry), true);
      if (!result) throw new Error('Storage returned no confirmation.');

      // Invalidate student summary cache
      try { await window.storage.delete('student-summary:cache', true); } catch (e) { /* fine */ }

      showToast('Thank you — your experience has been added to the archive.', 'success');
      form.reset();
      removeBtn.click();
      // Reset aims UI
      document.querySelectorAll('.aim-card').forEach(function (card) {
        card.removeAttribute('data-selected-prompt');
        card.removeAttribute('data-selected-prompt-label');
        card.classList.remove('open');
        const body = card.querySelector('.aim-body');
        if (body) body.hidden = true;
        card.querySelector('.aim-header').setAttribute('aria-expanded', 'false');
        card.querySelectorAll('.prompt-tile').forEach(function (t) { t.classList.remove('selected'); });
        const ra = card.querySelector('.prompt-response-area');
        if (ra) ra.hidden = true;
        const ta = card.querySelector('.prompt-textarea');
        if (ta) ta.value = '';
      });

      submitBtn.innerHTML = 'Submit My Experience <span class="arrow">→</span>';
      submitBtn.disabled  = false;
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      console.error(err);
      showToast('Could not submit: ' + err.message, 'error');
      submitBtn.disabled = false;
      submitBtn.innerHTML = 'Submit My Experience <span class="arrow">→</span>';
    }
  });

})();
