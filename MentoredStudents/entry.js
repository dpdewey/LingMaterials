/* =========================================================
   Entry page — handles form submission and image preview
   ========================================================= */

(function () {
  'use strict';

  const form          = document.getElementById('mentoring-form');
  const dropzone      = document.getElementById('dropzone');
  const fileInput     = document.getElementById('image');
  const previewWrap   = document.getElementById('preview-wrap');
  const previewImg    = document.getElementById('preview-img');
  const previewName   = document.getElementById('preview-name');
  const previewSize   = document.getElementById('preview-size');
  const removeImgBtn  = document.getElementById('remove-img');
  const submitBtn     = document.getElementById('submit-btn');
  const toast         = document.getElementById('toast');

  const MAX_BYTES   = 4 * 1024 * 1024;        // 4MB raw
  const MAX_DIMENSION = 1200;                  // resize to this max side after compression
  const COMPRESS_QUALITY = 0.78;

  let imageDataUrl = null;
  let imageFileName = '';

  /* -------- Toast -------- */
  function showToast(msg, kind) {
    toast.textContent = msg;
    toast.className = 'toast show' + (kind ? ' ' + kind : '');
    clearTimeout(showToast._t);
    showToast._t = setTimeout(function () { toast.className = 'toast'; }, 3500);
  }

  /* -------- File handling -------- */
  function fmtSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  }

  function compressImage(file) {
    return new Promise(function (resolve, reject) {
      const reader = new FileReader();
      reader.onload = function (e) {
        const img = new Image();
        img.onload = function () {
          // Resize to fit within MAX_DIMENSION on the longer edge
          let w = img.width, h = img.height;
          if (w > MAX_DIMENSION || h > MAX_DIMENSION) {
            if (w > h) { h = Math.round(h * MAX_DIMENSION / w); w = MAX_DIMENSION; }
            else      { w = Math.round(w * MAX_DIMENSION / h); h = MAX_DIMENSION; }
          }
          const canvas = document.createElement('canvas');
          canvas.width = w; canvas.height = h;
          const ctx = canvas.getContext('2d');
          ctx.drawImage(img, 0, 0, w, h);
          const dataUrl = canvas.toDataURL('image/jpeg', COMPRESS_QUALITY);
          resolve(dataUrl);
        };
        img.onerror = function () { reject(new Error('Could not read image')); };
        img.src = e.target.result;
      };
      reader.onerror = function () { reject(new Error('Could not load file')); };
      reader.readAsDataURL(file);
    });
  }

  function handleFile(file) {
    if (!file) return;
    if (!/^image\/(jpeg|png|webp)$/.test(file.type)) {
      showToast('Please choose a JPG, PNG, or WEBP image.', 'error');
      return;
    }
    if (file.size > MAX_BYTES) {
      showToast('Image is larger than 4 MB. Please choose a smaller file.', 'error');
      return;
    }
    imageFileName = file.name;
    compressImage(file)
      .then(function (dataUrl) {
        imageDataUrl = dataUrl;
        previewImg.src = dataUrl;
        previewName.textContent = file.name;
        // Approximate compressed size from base64 length
        const approxBytes = Math.round((dataUrl.length - 22) * 3 / 4);
        previewSize.textContent = fmtSize(file.size) + ' → ' + fmtSize(approxBytes) + ' (compressed)';
        previewWrap.style.display = 'flex';
      })
      .catch(function (err) {
        showToast('Image processing failed: ' + err.message, 'error');
      });
  }

  fileInput.addEventListener('change', function (e) {
    handleFile(e.target.files[0]);
  });

  // Drag and drop
  ['dragenter', 'dragover'].forEach(function (ev) {
    dropzone.addEventListener(ev, function (e) {
      e.preventDefault(); e.stopPropagation();
      dropzone.classList.add('drag');
    });
  });
  ['dragleave', 'drop'].forEach(function (ev) {
    dropzone.addEventListener(ev, function (e) {
      e.preventDefault(); e.stopPropagation();
      dropzone.classList.remove('drag');
    });
  });
  dropzone.addEventListener('drop', function (e) {
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  });

  removeImgBtn.addEventListener('click', function () {
    imageDataUrl = null;
    imageFileName = '';
    fileInput.value = '';
    previewWrap.style.display = 'none';
  });

  /* -------- ID generation -------- */
  function generateId() {
    return 'entry_' + Date.now().toString(36) + '_' + Math.random().toString(36).slice(2, 8);
  }

  /* -------- Submit -------- */
  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    submitBtn.disabled = true;
    submitBtn.textContent = 'Submitting…';

    const fd = new FormData(form);
    // Normalize student list
    const studentRaw = (fd.get('students') || '').toString().trim();
    const students = studentRaw
      .split(/[,;\n]+/)
      .map(function (s) { return s.trim(); })
      .filter(Boolean);

    const id = generateId();
    const entry = {
      id:              id,
      mentor:          (fd.get('mentor') || '').toString().trim(),
      venueType:       (fd.get('venueType') || '').toString().trim(),
      venue:           (fd.get('venue') || '').toString().trim(),
      discipline:      (fd.get('discipline') || '').toString().trim(),
      term:            (fd.get('term') || '').toString().trim(),
      students:        students,
      accomplishments: (fd.get('accomplishments') || '').toString().trim(),
      notes:           (fd.get('notes') || '').toString().trim(),
      image:           imageDataUrl,
      imageName:       imageFileName,
      createdAt:       new Date().toISOString()
    };

    try {
      // Save under shared key so the public view can read it
      const key = 'mentoring:' + id;
      const result = await window.storage.set(key, JSON.stringify(entry), true);
      if (!result) throw new Error('Storage returned no confirmation.');

      // Invalidate any cached AI summary on the view side
      try {
        await window.storage.delete('mentoring-summary:cache', true);
      } catch (e) { /* nothing cached yet — fine */ }

      showToast('Entry submitted. Thank you for documenting this work.', 'success');
      form.reset();
      removeImgBtn.click();
      submitBtn.textContent = 'Submit Entry';
      submitBtn.disabled = false;
      // Scroll to top so user sees confirmation
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      console.error(err);
      showToast('Could not submit: ' + err.message, 'error');
      submitBtn.disabled = false;
      submitBtn.textContent = 'Submit Entry';
    }
  });

})();
