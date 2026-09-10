# BYU Brand-Compliance Update

This update brings the mentoring archive into alignment with the
official BYU brand standards published at brand.byu.edu, modeled
on the BYU Department of Linguistics homepage at ling.byu.edu.

## Source Documents Consulted

- https://brand.byu.edu/web-theme — typography & layout structure
- https://brand.byu.edu/colors — color palette & accent rules
- https://brand.byu.edu/type — typography spec (IBM Plex Sans)
- https://brand.byu.edu/unit-logos/academics-support — sub-brand rules
- https://ling.byu.edu/ — reference Brightspot implementation
- "Official College and Unit Logo Guidelines" PDF (provided)
- "2022 Logos PNG (raster)" zip (provided)

## What Changed

### Typography

**Was:** Crimson Pro serif headings + Inter body text. The serif
treatment gave the site a "literary magazine" feel that competed
with BYU's actual identity.

**Now:** IBM Plex Sans throughout, weights 300–700, loaded from
Google Fonts per BYU's official spec. This matches every BYU
Brightspot site including ling.byu.edu.

### Color Palette

**Was:** A custom palette including tan #C5B783, deep tan #A89968,
and paper #F7F2E8 backgrounds. None of these colors are in BYU's
brand palette.

**Now:** Strict BYU palette only:
  - Navy   #002E5D (dominant)
  - White  #FFFFFF (surfaces)
  - Royal  #0047BA (interactive accent)
  - Text colors per BYU spec: #141414, #002E5D, #666666

The brand guide explicitly warns against "using an accent color
as a close companion to navy in a way that gives it equal status,"
so royal is used sparingly for buttons, links, and hover states.

### Logo Treatment

**Was:** A custom typeset masthead reading "Department of
Linguistics" in Crimson Pro italics. This is exactly what the
unit-logo PDF prohibits: "Never create your own version of your
unit logo. Any deviations from the provided logo or usage
guidelines are considered incorrect."

**Now:** The official BYU Linguistics horizontal logo
(ling_horiz_white.png) appears in the navy footer, sized to BYU's
spec. The header bar follows BYU's text-link breadcrumb pattern
(BYU | College of Humanities | Linguistics) used throughout the
Brightspot template.

### Decorative Glyphs Removed

**Was:** Large IPA characters (ʃ, ə) and typographic symbols (¶, §)
splashed across the hero and section dividers as decorative flourishes.

**Why removed:** Page 10 of the unit-logo PDF says non-official
visual treatments "should not be used for over two years, though
ideally should be used for less so as to not inadvertently create
a new brand identity, logo, or icon that becomes recognizable to
identify the unit." Recurring IPA glyphs risked reading as a
custom sub-brand for the department.

**Now:** No decorative glyphs. Hierarchy is established through
typography weight, navy bands, and whitespace alone — exactly as
the Brightspot template does.

### Layout Structure

**Was:** Editorial masthead with custom department wordmark,
followed by content blocks.

**Now:** Brightspot-replica four-region layout per brand spec:

  1. HEADER: navy top bar with BYU monogram + breadcrumb links
  2. NAVIGATION: white sticky bar with page title + nav links
  3. MAIN CONTENT: hero, quick-links strip, content sections
  4. AREA FOOTER: contact info, supplementary links, social
  5. UNIVERSITY FOOTER: BYU mark + copyright

This mirrors ling.byu.edu's actual structure exactly.

### Accent Color Compliance

The BYU spec forbids using accent colors:
  - "as a dominant color for your website"
  - "as a close companion to navy in a way that gives it equal
    or near-equal status"
  - "for large amounts of text"

Royal #0047BA is now used only for:
  - Hyperlink color (interactive)
  - Button hover states
  - Focus rings (accessibility)
  - Aim chips (intellectual aim only)
  - Donut chart middle ring

Navy #002E5D dominates: hero accents, stats strips, pull quotes,
aims banner, footer, headings.

## Functionality

No JavaScript logic was changed. All previous functionality works
identically:
  - Per-field privacy toggles + master "all-private" toggle
  - Anonymous student submissions (admin sees real name)
  - 5-section faculty entry form (mentor, activity, mentees, accomplishments, notes, impact, image)
  - 4-aim student reflection accordion
  - Word cloud, donut chart, gallery, sortable entries list, modal
  - Password-gated admin pages with CSV export
  - AI summary via /api/summary serverless function
  - All seed data (8 faculty entries, 6 student reflections)

## Files Changed

  - styles.css (full rewrite — ~1100 lines)
  - index.html (full rewrite)
  - FacultyMentoring/entry.html (full rewrite)
  - FacultyMentoring/view.html (full rewrite)
  - FacultyMentoring/admin.html (full rewrite)
  - MentoredStudent/student-entry.html (full rewrite)
  - MentoredStudent/student-view.html (full rewrite)
  - MentoredStudent/admin.html (full rewrite)
  - assets/logos/*.png (added — official sub-brand logos)
  - FacultyMentoring/admin.js (CSS variable references updated)
  - FacultyMentoring/view.js (CSS variable references updated)
  - MentoredStudent/admin.js (CSS variable references updated)
  - MentoredStudent/student-view.js (CSS variable references updated)
  - All other JS files unchanged

## Files Unchanged

  - storage.js
  - seed-data.js
  - student-seed.js
  - api/summary.js
  - netlify/functions/summary.js
  - netlify.toml
