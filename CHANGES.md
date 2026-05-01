# Update Notes — What Changed

This update adds:

1. **Faculty "Personal Impact" field** — section vi on the entry form
2. **Per-field privacy toggles** under each open-text response
3. **Master "make entire entry private" toggle** before submit
4. **"Show as Anonymous student" option** under student name field
5. **Linguistic Computing / Computational Linguistics** added as a program option
6. **Empty image tiles fixed** — broken thumbnails no longer appear
7. **Admin pages with CSV export** — at private URLs

## Admin pages

Two new pages have been added, each gated behind a soft password
(`ShaneReeseMentors`):

- `FacultyMentoring/admin.html`
- `MentoredStudent/admin.html`

These pages:
- Are tagged `noindex, nofollow, noarchive, nosnippet` so search
  engines and AI crawlers will skip them
- Are NOT linked from any public page — only accessible by typing the
  URL directly
- Show every entry including responses marked private and the real
  names of students who chose anonymous public display
- Include a "Download CSV" button that exports complete data
  (including private fields) for analysis in Excel
- Use sessionStorage for the unlock state, so closing the tab locks
  them again

### Important caveat about the admin password

This is a **client-side** password. Because GitHub Pages serves only
static files, the password lives in `admin.js` and can be discovered
by anyone who looks at the page source. It is a soft barrier — fine
for keeping casual visitors out of the admin views, but **not real
security**.

For genuinely sensitive admin data, you would want one of:
- BYU NetID / SSO authentication
- HTTP basic auth at the web server level
- A backend API that authenticates before returning data

The current setup is appropriate for a low-stakes departmental
mentoring archive but should not be treated as protecting confidential
information.

## Privacy behavior

When a faculty member or student checks a per-field privacy toggle:
- The whole entry still appears on the public archive
- That specific field is hidden (not shown at all) on the public view
- The admin page sees the full text with a `[PRIVATE]` tag

When they check the master "make entire entry private" toggle:
- The entry does not appear on the public archive at all
- The admin page sees the full entry with a `FULLY PRIVATE` banner

When a student checks "Show as Anonymous student":
- The public archive shows their name as "Anonymous student"
- The admin page sees their real name with an "ANONYMOUS ON PUBLIC"
  banner

## Folder structure for deployment

```
/                              ← root
├── index.html                 ← landing page
├── FacultyMentoring/
│   ├── entry.html             ← faculty submission form (private)
│   ├── view.html              ← faculty public archive
│   ├── admin.html             ← faculty admin (password-gated)
│   ├── admin.js
│   ├── entry.js, view.js
│   ├── styles.css, storage.js, seed-data.js
├── MentoredStudent/
│   ├── student-entry.html     ← student submission form
│   ├── student-view.html      ← student public archive
│   ├── admin.html             ← student admin (password-gated)
│   ├── admin.js
│   ├── student-entry.js, student-view.js
│   ├── styles.css, student-styles.css
│   ├── storage.js, student-seed.js
├── api/, netlify/             ← serverless functions for AI summary
└── netlify.toml
```

Each subfolder is self-contained (shared CSS and JS files are duplicated
into both folders) so the pages render correctly regardless of whether
they are loaded via the root index or directly by URL.

## Deployment

Replace your existing GitHub repository contents with this folder.
Commit and push. GitHub Pages will redeploy automatically.

The admin pages will be at:
- `https://dpdewey.github.io/LingMaterials/FacultyMentoring/admin.html`
- `https://dpdewey.github.io/LingMaterials/MentoredStudent/admin.html`

Bookmark these. The CSVs download with the date in the filename so
you can keep a running record of administrator exports.
