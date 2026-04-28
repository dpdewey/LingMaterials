# BYU Linguistics — Mentoring Documentation Site

A two-page editorial site for documenting and showcasing student
mentoring across the Department of Linguistics, TESOL, and Editing &
Publishing.

---

## 1. Quick local preview (no setup beyond Python)

```bash
cd path/to/this/folder
python3 -m http.server 8000
```

Then open `http://localhost:8000/view.html`. The page seeds itself with
8 sample entries on first load and persists them in your browser via
`localStorage`, so a refresh keeps them. Submit new entries from
`http://localhost:8000/entry.html` and they appear immediately on
`view.html`.

The AI summary block on the view page will show a locally-composed
fallback paragraph — the actual AI summary requires the serverless
function (see §3) or being deployed somewhere with API access.

To **clear the seeded data and start fresh**, run this in the browser
console while on the view page:

```js
Object.keys(localStorage).filter(k => k.startsWith('byuling_')).forEach(k => localStorage.removeItem(k)); location.reload();
```

If you don't have Python:

```bash
npx serve .          # Node, no install
```

Or use VS Code's **Live Server** extension (right-click `view.html` →
"Open with Live Server").

---

## 2. Files

| File                          | Purpose                                                                |
| ----------------------------- | ---------------------------------------------------------------------- |
| `entry.html`                  | Private submission form. Tagged `noindex, nofollow`.                   |
| `view.html`                   | Public archive page.                                                   |
| `styles.css`                  | Shared editorial stylesheet.                                           |
| `entry.js`                    | Form submission, image compression, drag-and-drop upload.              |
| `view.js`                     | Loads entries, builds visualizations, generates AI summary.            |
| `seed-data.js`                | 8 sample entries with inline SVG illustrations. Loaded once, then      |
|                               | persisted to storage.                                                  |
| `storage.js`                  | Storage shim. Auto-detects backend: Claude artifact API → localStorage.|
| `netlify/functions/summary.js`| Serverless function (Netlify) for the AI summary call.                 |
| `netlify.toml`                | Netlify config — wires `/api/summary` and sets noindex headers.        |
| `api/summary.js`              | Same serverless function in Vercel format.                             |

---

## 3. Deployment paths

### Quickest: Netlify Drop (5 minutes, free)

1. Go to [app.netlify.com/drop](https://app.netlify.com/drop) and drag
   the entire folder onto the page.
2. You get a public URL immediately (e.g., `random-name.netlify.app`).
3. To enable AI summaries: in the Netlify dashboard for your new site,
   go to **Site settings → Environment variables** and add
   `ANTHROPIC_API_KEY` = your API key from
   [console.anthropic.com](https://console.anthropic.com).
4. Trigger a redeploy. The function at `/api/summary` becomes live and
   `view.html` will start using real AI summaries automatically.

### Vercel (similar flow)

1. Push the folder to a GitHub repo, or use `vercel deploy` from the
   CLI.
2. In project settings, set `ANTHROPIC_API_KEY` in **Environment
   Variables**.
3. Vercel auto-routes `/api/summary` to `api/summary.js`.

### Cloudflare Workers / Pages

The function code in `netlify/functions/summary.js` is portable —
the body uses standard `fetch`, so wrapping it in a Worker is a
small adaptation. Mount the Pages site to serve the static files
and add a Worker bound to `/api/summary`.

### Integrating with `ling.byu.edu`

For a real BYU deployment, you'll likely want to talk to whoever runs
the department's Brightspot CMS. Options:

- Embed the static page as an iframe in a Brightspot page.
- Self-host the static files on BYU infrastructure and link from
  the department site.
- Re-implement the entry form against BYU's existing data layer
  (preferred long-term; protects against vendor lock-in).

---

## 4. Storage architecture

`storage.js` provides a single interface (`get`, `set`, `list`,
`delete`) and probes for backends in order:

1. **`window.storage`** — Claude's artifact storage API, present only
   when running inside a Claude artifact preview.
2. **`localStorage`** — universal browser fallback. Each user sees their
   own submissions. Good for demos and local preview.
3. **Memory dummy** — last resort if both above are unavailable.

**For a real multi-user deployment** you'll want a proper backend so
all visitors see the same entries. Add a fourth branch in
`storage.js`'s `chooseBackend()` for Firebase, Supabase, a BYU API,
or whatever you settle on. Keep the same `get / set / list / delete`
contract and nothing else changes.

---

## 5. Sample data

When the archive first loads with no entries in storage, it seeds
itself from `seed-data.js`:

- Corpus research (Mark Davies, Linguistics)
- Mexico City study abroad (Lynn Henrichsen, TESOL)
- Schreiner Press editing internship (Daniel Adams, Editing & Pub.)
- ELC advanced speaking practicum (Norman Evans, TESOL)
- LSA poster session (Earl K. Brown, Linguistics)
- Honors thesis on lexicography (Cynthia Hallen, Applied English Ling.)
- Schwa journal Volume XIV (Wendy Baker Smemoe, Linguistics)
- Ling 377 methods course (K. James Hartshorn, TESOL)

Each entry has an inline SVG illustration as its image — no external
asset dependencies.

To deploy without sample data, delete `seed-data.js` and remove the
matching `<script>` tag from `view.html`. The archive will start empty
and populate as mentors submit.

---

## 6. Privacy of the entry page

`entry.html` carries:

```html
<meta name="robots" content="noindex, nofollow, noarchive, nosnippet">
```

The Netlify config also sends an `X-Robots-Tag` header for the same
URL. Together these keep the page out of Google, Bing, and most AI
crawlers.

For real privacy you'll also want **access control** on the entry
URL — basic auth at the host level, BYU NetID/SSO, or a simple shared
secret. The `noindex` tags only prevent search engines from listing
the page; anyone with the URL can still reach it.
