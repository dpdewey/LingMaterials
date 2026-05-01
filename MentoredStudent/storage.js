/* =========================================================
   Storage shim
   ---------------------------------------------------------
   Provides the same get/set/list/delete interface regardless
   of where the page is running. Probes for backends in order:

     1. window.storage  — Claude artifact persistent storage
     2. localStorage    — universal browser fallback

   To add a real backend later (Firebase, Supabase, BYU API),
   add a new branch in chooseBackend() and keep the same
   get/set/list/delete contract. Nothing else changes.

   All methods return the same shape as Claude's storage API
   so view.js and entry.js are agnostic about the backend.
   ========================================================= */

(function () {
  'use strict';

  const LS_PREFIX = 'byuling_'; // namespace localStorage to avoid collisions

  // ---- Backend: Claude artifact storage ----
  const claudeBackend = {
    name: 'claude',
    async get(key, shared) {
      return await window._claudeStorage.get(key, shared);
    },
    async set(key, value, shared) {
      return await window._claudeStorage.set(key, value, shared);
    },
    async delete(key, shared) {
      return await window._claudeStorage.delete(key, shared);
    },
    async list(prefix, shared) {
      return await window._claudeStorage.list(prefix, shared);
    }
  };

  // ---- Backend: localStorage ----
  const localBackend = {
    name: 'local',
    async get(key /*, shared */) {
      try {
        const raw = window.localStorage.getItem(LS_PREFIX + key);
        if (raw === null) return null;
        return { key: key, value: raw, shared: true };
      } catch (e) {
        return null;
      }
    },
    async set(key, value /*, shared */) {
      try {
        window.localStorage.setItem(LS_PREFIX + key, value);
        return { key: key, value: value, shared: true };
      } catch (e) {
        // Quota exceeded or storage disabled — return null so caller can detect failure
        console.warn('localStorage write failed:', e);
        return null;
      }
    },
    async delete(key /*, shared */) {
      try {
        window.localStorage.removeItem(LS_PREFIX + key);
        return { key: key, deleted: true, shared: true };
      } catch (e) {
        return null;
      }
    },
    async list(prefix /*, shared */) {
      try {
        const fullPrefix = LS_PREFIX + (prefix || '');
        const keys = [];
        for (let i = 0; i < window.localStorage.length; i++) {
          const k = window.localStorage.key(i);
          if (k && k.indexOf(fullPrefix) === 0) {
            keys.push(k.substring(LS_PREFIX.length));
          }
        }
        return { keys: keys, prefix: prefix, shared: true };
      } catch (e) {
        return { keys: [], prefix: prefix, shared: true };
      }
    }
  };

  // ---- Pick a backend ----
  function chooseBackend() {
    // Save a reference to Claude's storage if present, before we shadow it
    if (typeof window.storage !== 'undefined' &&
        window.storage &&
        typeof window.storage.get === 'function') {
      window._claudeStorage = window.storage;
      return claudeBackend;
    }
    // Fall back to localStorage
    if (typeof window.localStorage !== 'undefined') {
      return localBackend;
    }
    // Last resort: in-memory dummy that always returns null
    return {
      name: 'memory',
      async get() { return null; },
      async set() { return null; },
      async delete() { return null; },
      async list() { return { keys: [], shared: true }; }
    };
  }

  const backend = chooseBackend();

  // Expose unified interface on window.storage,
  // overriding the Claude-only interface if present.
  window.storage = {
    backend: backend.name,
    get: backend.get.bind(backend),
    set: backend.set.bind(backend),
    delete: backend.delete.bind(backend),
    list: backend.list.bind(backend)
  };

  // Make backend name visible for debugging
  console.info('[mentoring archive] storage backend:', backend.name);

})();
