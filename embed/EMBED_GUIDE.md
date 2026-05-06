============================================================
  BRIGHTSPOT EMBED GUIDE
  How to put the Mentoring Archive into your university site
============================================================

This package adds an `embed/` folder to your site with versions
of each public page that have NO BYU header, navigation, or
footer chrome. They're meant to live INSIDE another page that
already provides those elements (your Brightspot site).

After you re-deploy to GitHub Pages, you'll have these new URLs:

  https://dpdewey.github.io/LingMaterials/embed/index.html
  https://dpdewey.github.io/LingMaterials/embed/FacultyMentoring/view.html
  https://dpdewey.github.io/LingMaterials/embed/FacultyMentoring/entry.html
  https://dpdewey.github.io/LingMaterials/embed/MentoredStudent/student-view.html
  https://dpdewey.github.io/LingMaterials/embed/MentoredStudent/student-entry.html

These work side-by-side with your existing standalone pages —
the original URLs (without /embed/) still work and still show
the full BYU chrome for direct visitors.

============================================================
  EMBED OPTION 1 — IFRAME (recommended)
============================================================

This is the option Claude in Chrome already recommended, but
now you point it at the /embed/ URLs instead of the originals.
That way you get NO redundant BYU chrome.

In Brightspot, on the page where you want the archive:
  1. Click "Add Module"
  2. Choose "HTML Embed"
  3. Paste this code:

  <iframe
    src="https://dpdewey.github.io/LingMaterials/embed/FacultyMentoring/view.html"
    width="100%"
    height="2400"
    style="border: 0; display: block;"
    loading="lazy"
    title="Faculty Mentoring Archive">
  </iframe>

For the Student Experiences page:

  <iframe
    src="https://dpdewey.github.io/LingMaterials/embed/MentoredStudent/student-view.html"
    width="100%"
    height="2600"
    style="border: 0; display: block;"
    loading="lazy"
    title="Student Experiences">
  </iframe>

NOTE ON HEIGHT: iframes don't auto-size to their content. You
need to set a height that's tall enough. The numbers above are
about right for the current data — if the entries list grows
substantially, increase the height. Alternatively, use the
"auto-resize iframe" snippet at the end of this document.

WHY THIS WORKS WELL:
  - Zero rework. Brightspot sees a single HTML element.
  - Updates to GitHub Pages automatically appear in Brightspot.
  - The form submission, modal, search, and filters all work
    exactly as they do on the standalone site.
  - localStorage is shared with the standalone site (same
    origin), so an entry submitted in the iframe shows up on
    the standalone view too.

ONE LIMITATION: iframes are sandboxed. The fonts, colors, and
styles inside the iframe are isolated from the parent page —
which is GOOD for keeping the BYU brand styling intact, but
means deep linking between BrightSpot pages and embed content
won't work seamlessly.

============================================================
  EMBED OPTION 2 — DIRECT HTML EMBED (no iframe)
============================================================

Brightspot's "HTML Embed" module also accepts raw HTML+CSS+JS,
not just iframes. With this approach you can paste the actual
content of the embed pages directly into Brightspot, and the
page becomes truly part of the Brightspot DOM rather than a
nested document.

THE STRENGTH: No iframe height issues, native scrolling, the
content shares the parent page's font sizing context, links
inside the embed can navigate to other Brightspot pages.

THE WEAKNESS: Brightspot's editor may strip or modify <script>
tags, complex CSS, or attributes it doesn't like — depending
on how your installation is configured. You may also see your
content's CSS conflict with Brightspot's own styles.

If you want to try this approach, here's how:

  1. View the embed page at the GitHub Pages URL above
  2. Right-click → "View Page Source" (or use Developer Tools)
  3. Copy everything from <body> through </body>
  4. Also copy the <link rel="stylesheet"...> tag in the <head>
  5. In Brightspot's HTML Embed module, paste:
     - The stylesheet <link> tag
     - The body content
     - The <script> tags from the bottom of the page

The scripts reference other JS files (storage.js, view.js, etc.)
via relative paths. You'll need to change these to absolute URLs:

  <script src="https://dpdewey.github.io/LingMaterials/storage.js"></script>
  <script src="https://dpdewey.github.io/LingMaterials/seed-data.js"></script>
  <script src="https://dpdewey.github.io/LingMaterials/FacultyMentoring/view.js"></script>

And the stylesheet:
  <link rel="stylesheet"
        href="https://dpdewey.github.io/LingMaterials/embed/styles.css">

CAUTION: This requires testing in your specific Brightspot
installation. Some BrightSpot configurations sanitize <script>
tags by default. Check with your Brightspot administrator
before relying on this approach.

============================================================
  EMBED OPTION 3 — REBUILD WITH NATIVE BRIGHTSPOT MODULES
============================================================

This is the option Claude in Chrome called "most integrated,
most work." Instead of embedding HTML at all, you'd recreate
the same content using Brightspot's own module system:

  - Rich Text module for descriptions and intros
  - Pull Quote module for the featured mentor quote
  - List module for each entry (one list per archive)
  - Tabs module for filter views by discipline / aim
  - Image module for any photos

The advantages: it integrates with Brightspot's search, its
content editor, its publishing workflow, its access controls.
Faculty members can edit entries directly in Brightspot
without GitHub knowledge.

The disadvantages: you lose the AI summary feature, the
dynamic word cloud, the donut chart, the modal entry detail
view, the per-field privacy toggles, the sortable/filterable
entry list. Recreating these as Brightspot widgets would
require custom Brightspot module development. Also, you'd
need to manually move all 8 faculty + 6 student seed entries
into Brightspot, and add new ones in two places.

WHEN THIS MAKES SENSE: Once the project has stabilized AND
you have IT/web-team buy-in for ongoing Brightspot module
maintenance. For now, the iframe approach is much simpler.

============================================================
  RECOMMENDED PATH
============================================================

  Phase 1 (right now): Use Option 1 (iframe) pointing at the
  new /embed/ URLs. This eliminates the redundant chrome with
  zero rework.

  Phase 2 (if you outgrow iframes): Investigate Option 2
  (direct HTML embed) with your Brightspot administrator.

  Phase 3 (long term, if appropriate): Consider Option 3
  (native modules) once you know which features actually
  get used.

============================================================
  AUTO-RESIZING IFRAME (advanced, optional)
============================================================

If you want the iframe to size itself to its content
automatically — so you don't have to guess at heights — paste
this script after the iframe in the BrightSpot HTML Embed.
It only works if the iframe and parent are on the SAME origin.
Since BrightSpot is on a different domain than your GitHub
Pages site, this won't work without a change of strategy
(e.g., hosting the embed pages directly on the BrightSpot site).

  <script>
    // For SAME-ORIGIN embeds only
    window.addEventListener('message', function (ev) {
      if (ev.data && ev.data.iframeHeight) {
        var iframe = document.querySelector('iframe[title="Faculty Mentoring Archive"]');
        if (iframe) iframe.style.height = ev.data.iframeHeight + 'px';
      }
    });
  </script>

For cross-origin embeds (your case), the simplest workaround
is to set a generous fixed height (3000px or so) that fits all
the entries, and accept that there may be empty space at the
bottom on shorter content states.

============================================================
  WHAT IF I DON'T WANT TO USE iframe AT ALL?
============================================================

The cleanest non-iframe approach is to host the embed/ files
directly on the BrightSpot server (or wherever your university's
web team manages static assets). Then you can include them with
a simple <link> + <script> in any page template.

If your web team controls the BrightSpot deployment, ask them:

  "Can we host these static HTML/CSS/JS files at a path like
  /linguistics-mentoring/ on our domain, and include them via
  a server-side include or a simple template fragment?"

This eliminates the iframe entirely and gives you full
integration with the BrightSpot site, while preserving the
custom styling and dynamic features.
