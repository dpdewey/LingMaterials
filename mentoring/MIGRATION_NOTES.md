# Restructure — Mentoring/ and TeachingMaterials/

This package restructures the repository so the mentoring archive and the
teaching materials are two separate branches behind a small front door.
Nothing about the mentoring content changes; it just stops sharing a page
with handouts.

## Before you run it

**Get your pushes working first.** If `.nojekyll` isn't live yet and
GitHub Pages is still serving a stale build, don't restructure on top of
that — you won't be able to tell a real problem from a stale deploy. Push
`.nojekyll`, confirm a change appears on the live site, then come back.
(The migration writes `.nojekyll` for you if it's still missing.)

**Commit whatever you have now.** The script moves about twenty folders
and files. A clean commit beforehand means `git reset --hard HEAD` is a
complete undo.

## How to run it

Copy this package's contents over your repository root, then:

```bash
cd ~/path/to/LingMaterials
python3 tools/migrate_structure.py --check     # preview, changes nothing
python3 tools/migrate_structure.py             # do it
```

The `--check` pass prints every move and rewrite without touching a file.
Read it, then run for real. The script refuses to run if `Mentoring/` or
`TeachingMaterials/` already exists, so you can't half-apply it twice.

Afterwards, open `index.html` in your browser and click through both
doors before you commit.

## What changes

```
BEFORE                            AFTER
index.html    (mentoring page)    index.html                    ← two doors
FacultyMentoring/                 Mentoring/index.html          ← mentoring page
MentoredStudent/                  Mentoring/FacultyMentoring/
materials.html                    Mentoring/MentoredStudent/
IntermediateEnglish/              TeachingMaterials/index.html
AdvancedEnglish_for_Teachers/     TeachingMaterials/IntermediateEnglish/
TeachingLessons/                  TeachingMaterials/AdvancedEnglish_for_Teachers/
FamilyLessonPossessivePronouns/   TeachingMaterials/TeachingLessons/
possessive_*.html   (in root)     TeachingMaterials/FamilyLessonPossessivePronouns/
```

Seven steps, all printed as they happen:

1. **Moves** the six folders and the two stranded `possessive_*.html` files.
2. **Fixes 26 paths** inside the moved mentoring pages — `../assets/logos/`
   becomes `../../assets/logos/`, the nav gains a real link to the site root,
   and any teaching-materials references from the earlier integration are
   removed.
3. **Rewrites 10 script paths** in `embed/`.
4. **Writes** the new root hub and `Mentoring/index.html`.
5. **Writes 7 redirect stubs** at the old URLs.
6. **Writes `.nojekyll`** if missing.
7. **Regenerates** the five teaching-materials pages with corrected paths
   and scoped navigation.

## The two things I was careful about

**Your Brightspot embeds keep working.** `embed/` does not move. Its pages
load their JavaScript from `../../FacultyMentoring/view.js` and similar, so
those 10 `src` paths are rewritten to `../../Mentoring/FacultyMentoring/...`.
The iframe URLs you pasted into Brightspot — `embed/FacultyMentoring/view.html`
— are unchanged, so nothing needs editing on the department site.

One subtlety worth knowing, because it would have been an easy mistake:
`embed/index.html` links to `FacultyMentoring/view.html`, which means the
chrome-free copy *inside* `embed/`. Those links are deliberately left alone.
Rewriting them would have quietly sent Brightspot visitors to the
full-chrome pages, header and footer and all — the exact problem the embed
folder exists to solve.

**Old URLs still work.** Your README tells you to bookmark
`<base>/FacultyMentoring/admin.html`, and you may have shared links to the
faculty archive. Seven meta-refresh stubs sit at the old paths and bounce
visitors to the new ones. They carry `noindex` so search engines don't hold
onto them. Delete them in a year when nothing points there anymore.

## Navigation is now scoped

Each branch only shows its own links:

| Page | Nav |
|---|---|
| Root hub | Home · Mentoring · Teaching Materials |
| Mentoring pages | Home · Mentoring · Faculty Mentoring · Student Experiences |
| Teaching pages | Home · Teaching Materials · Department |

Your mentoring pages no longer mention handouts, and a cooperating teacher
opening a collection never sees departmental record-keeping links.

## What I verified

Against a copy of your repo, with the earlier integration package already
applied:

- **92 HTML pages, 290 internal links, 0 broken**
- The moved faculty archive is functionally identical: same 8 entries, 8
  mentors, 46 students, 4 programs, 8 rows, 42 word-cloud terms
- Redirect stubs resolve — `/FacultyMentoring/view.html` lands on
  `/Mentoring/FacultyMentoring/view.html`, and `/materials.html` lands on
  `/TeachingMaterials/index.html`
- The footer logo loads from the new two-level-deep path
- No cross-leaks in any nav bar

The script also works if you never applied the earlier integration package —
it just has fewer teaching-materials references to clean up.

## Files in this package

| File | Notes |
|---|---|
| `tools/migrate_structure.py` | The one-time migration. Run with `--check` first. |
| `tools/build_materials.py` | **Replaces v1.** Knows the new structure and scoped nav. |
| `styles-materials.css` | Include in case you never applied the earlier package — the new hub needs it. |
| `MIGRATION_NOTES.md` | This file. |

`tools/patch_index.py` and `tools/patch_subpages.py` from the earlier
package are obsolete after this runs. Delete them.

## If you want to back out

If you committed before running: `git reset --hard HEAD`.

If you already committed the migration: `git revert HEAD`. The moves are
recorded as renames, so the revert restores the old layout cleanly.

## Afterwards — optional cleanup

1. `Mentoring/drafts/` holds `index-2.html.bak` and `index-3.html.bak`, your
   two superseded home-page drafts. The `.bak` suffix stops GitHub Pages
   serving them as broken pages. `Mentoring/index.html` was built from the
   `index-3` version, with the Google Forms links — so if you preferred the
   `index-2` editorial direction (About / Two Views / Contribute / Privacy),
   that draft is still there to work from.
2. `student-styles.css` in the root is referenced by zero pages. Safe to delete.
3. The 0-byte `teach_lesson_handout.html` and the duplicate
   `teacher_beliefs_survey.html` in the root are still there. Safe to delete.
4. **Do not delete** root `storage.js`, `seed-data.js`, or `student-seed.js`.
   The `embed/` pages load all three from the root. I got this wrong in the
   earlier notes; this corrects it.
