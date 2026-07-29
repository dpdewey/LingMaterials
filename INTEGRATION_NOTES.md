# Integration Notes — Teaching Materials into LingMaterials

Everything in this folder is either **new** or a **modified copy** of a file
already in your repo. Nothing is deleted, and no teaching material file was
edited. The mentoring archive keeps top billing on the home page.

---

## How to install

Copy the contents of this folder over the root of your local
`LingMaterials` checkout, keeping the folder structure. On a Mac:

```bash
cd ~/path/to/LingMaterials
cp -R ~/Downloads/LingMaterials_integration/. .
python3 tools/patch_subpages.py          # adds the nav item to the archive pages
git add -A
git commit -m "Add Teaching Materials hub and collection catalogues"
git push
```

That one script call is the only step you have to run yourself. It adds
"Teaching Materials" to the nav bar and footer of the four public
mentoring archive pages, which are not shipped in this package because
they contain live seed data and JS wiring I didn't want to overwrite
blind. The script makes four small edits per file and prints exactly
what it changed. It is safe to run twice — the second run reports
`already` for everything and changes nothing.

GitHub Pages redeploys in a minute or two. Then check:

- <https://dpdewey.github.io/LingMaterials/> — new "Teaching Materials" nav item
- <https://dpdewey.github.io/LingMaterials/materials.html> — the hub
- <https://dpdewey.github.io/LingMaterials/IntermediateEnglish/> — a catalogue

If anything looks wrong, `git revert HEAD` puts you straight back.

---

## Files in this package

### New

| File | What it is |
|---|---|
| `materials.html` | Teaching Materials hub — four collection cards, usage guidance |
| `styles-materials.css` | Additive stylesheet. Loads **after** `styles.css`. Every selector is prefixed `.mat-` or is an explicit modifier, so it cannot collide with existing mentoring styles. |
| `IntermediateEnglish/index.html` | Catalogue: 24 files in 4 topic sets |
| `AdvancedEnglish_for_Teachers/index.html` | Catalogue: 15 files in 4 topic sets |
| `TeachingLessons/index.html` | Catalogue: 29 files in 5 topic sets |
| `FamilyLessonPossessivePronouns/index.html` | Catalogue: 3 files |
| `tools/build_materials.py` | Generator for all five pages above |
| `tools/patch_index.py` | The script that made the `index.html` edits, kept so the edits are reproducible |
| `tools/patch_subpages.py` | **Run this once.** Adds the nav item + footer column to the four public archive pages |
| `.gitignore` | Stops `.DS_Store` and `Archive.zip` being committed |

### Modified

| File | Change |
|---|---|
| `index.html` | Six additions, listed below |
| `index-3.html` | Same six additions |
| `README.md` | Rewritten to describe both halves of the repo |

The six edits to the home page(s):

1. `styles-materials.css` added after the `styles.css` link
2. "Teaching Materials" added to the nav bar
3. "Teaching Materials" added to the Quick Links strip
4. A new "Teaching Materials" section added above "Note about Archive Purpose"
5. `class="area-footer-inner"` → `class="area-footer-inner cols-4"`
6. A fourth footer column, "Teaching Materials"

Nothing else in either file was touched. Every existing mentoring link,
form URL, and stylesheet reference is unchanged.

---

## Why the catalogues look different from the materials

The catalogue pages follow the BYU brand system already in `styles.css` —
IBM Plex Sans, navy and royal, official sub-brand logos. Your teaching
materials use a completely different visual language.

Restyling 70-odd material files to match BYU brand would be a large,
risky edit for little gain, and would make them worse at the job they
actually do. So the integration is at the **navigation** layer: the
catalogue pages are consistently BYU-branded, and materials open in
their own design. The hub page says this out loud so nobody thinks it's
a bug.

---

## Both index files, one decision to make

Your repo currently has three home pages:

- `index.html` — live. Its two "Add Entry" buttons point at the local
  forms, `FacultyMentoring/entry.html` and
  `MentoredStudent/student-entry.html`.
- `index-3.html` — same page, but those buttons point at your two live
  **Google Forms**. Untracked.
- `index-2.html` — a different, longer draft (About / Two Views /
  Contribute / Privacy sections). Untracked.

Since the submission pipeline moved to Google Forms, `index-3.html` is
probably the one you actually want live. I patched both `index.html` and
`index-3.html` identically so you can promote either without redoing
work:

```bash
# to make the Google Forms version the live home page
git mv index.html index-local-forms.html   # keep a copy, or just delete
mv index-3.html index.html
```

I left `index-2.html` alone — it's a different editorial direction, not a
variant, so it's your call.

---

## Optional cleanup (not done — your call)

None of these are required. Listed roughly best-value-first.

1. **`teach_lesson_handout.html` in the root is 0 bytes.** An empty file.
   `git rm teach_lesson_handout.html`. The real one is
   `AdvancedEnglish_for_Teachers/teach_lesson_handout.html`.

2. **`teacher_beliefs_survey.html` in the root is a byte-for-byte
   duplicate** of `AdvancedEnglish_for_Teachers/teacher_beliefs_survey.html`.
   Delete the root copy.

3. **`TeachingLessons/ListeningExercisesDay3_2.html` is a byte-for-byte
   duplicate** of `ListeningExercisesDay3_1.html`. The catalogue lists
   only `_1`. Delete `_2`.

4. **`Listening Exercises - Day 4.html` has spaces in the filename.** It
   works (the catalogue links to it URL-encoded) but it's fragile. To
   rename:

   ```bash
   git mv "TeachingLessons/Listening Exercises - Day 4.html" \
          TeachingLessons/ListeningExercisesDay4.html
   ```

   Then update that one filename in `tools/build_materials.py` and re-run it.

5. **`possessive_handout.html` and `possessive_survey.html` sit in the
   root** but belong to `FamilyLessonPossessivePronouns/`. They are also
   large (1.7 MB and 3.4 MB — inlined images). To move them:

   ```bash
   git mv possessive_handout.html possessive_survey.html FamilyLessonPossessivePronouns/
   ```

   Then in `tools/build_materials.py`, drop the `../` from those two
   paths and re-run. The catalogue's callout note about this can come out
   too.

6. **`Archive.zip` (96 KB) is untracked in the root.** The new
   `.gitignore` keeps it out of commits; delete the file itself when you
   don't need it.

7. **Unused duplicate JS/CSS in the root:** `storage.js`, `seed-data.js`,
   `student-seed.js`, `student-styles.css` are each duplicated inside
   `FacultyMentoring/` or `MentoredStudent/`, which is where the pages
   actually load them from. The root copies appear unused. **Leave
   `styles.css` alone** — `index.html` and `materials.html` both need it.
   Verify with a search for each filename before removing anything.

---

## Adding a new material later

Drop the file into the right collection folder, then add one line to the
matching `sets` entry in `tools/build_materials.py`:

```python
("my_new_handout.html", "Handout", "What it is", "B1–B2"),
#  filename,             role,      label,       level (optional)
```

Then:

```bash
python3 tools/build_materials.py
```

Roles are free text — `Lesson plan`, `Handout`, `Survey`, `Quiz`,
`Cards`, `Practice`, `Debate`, `Role-play`, `Slides`, `Reference`,
`Group A`, `Shared test`. The file-type badge (HTML / PDF / PPTX) is
derived from the extension automatically, and PDFs and PowerPoint files
get `target="_blank"` so they don't navigate away from the catalogue.

To add a whole new collection, copy one of the dicts in `PROJECTS`, point
`folder` at the new directory, and re-run. The hub page, footers, and
counts all pick it up.
