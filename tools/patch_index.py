#!/usr/bin/env python3
"""
patch_index.py — adds Teaching Materials navigation to the mentoring home page.

Five surgical edits, each verified. Run from the repo root:
    python3 tools/patch_index.py index.html index-3.html

Idempotent: re-running on an already-patched file is a no-op.
"""

import sys

NEW_SECTION = """  <section class="section">
    <h2>Teaching Materials</h2>
    <p style="max-width: 760px;">
      Alongside the mentoring record, the department publishes the teaching
      materials that came out of this mentored work &mdash; lesson plans,
      handouts, interactive practice pages, and surveys developed for the EFL
      teacher internship programs in Ecuador and Peru and for professional
      development with practising teachers. They are free to use and adapt.
    </p>
    <div class="quick-links-grid" style="margin-top: 1.5rem; max-width: 900px;">
      <a href="materials.html">All Teaching Materials</a>
      <a href="IntermediateEnglish/">Intermediate English</a>
      <a href="AdvancedEnglish_for_Teachers/">Advanced English for Teachers</a>
      <a href="TeachingLessons/">Classroom Lessons</a>
    </div>
  </section>

"""

FOOTER_COL = """    <div>
      <h4>Teaching Materials</h4>
      <ul>
        <li><a href="materials.html">All Materials</a></li>
        <li><a href="IntermediateEnglish/">Intermediate English</a></li>
        <li><a href="AdvancedEnglish_for_Teachers/">Advanced English for Teachers</a></li>
        <li><a href="TeachingLessons/">Classroom Lessons</a></li>
      </ul>
    </div>
"""

EDITS = [
    # (label, find, replace)
    ("stylesheet link",
     '<link rel="stylesheet" href="styles.css">',
     '<link rel="stylesheet" href="styles.css">\n'
     '<link rel="stylesheet" href="styles-materials.css">'),

    ("navbar link",
     '<a href="MentoredStudent/student-view.html">Student Experiences</a>\n    </nav>',
     '<a href="MentoredStudent/student-view.html">Student Experiences</a>\n'
     '      <a href="materials.html">Teaching Materials</a>\n    </nav>'),

    ("quick link",
     '      <a href="https://ling.byu.edu/">Department Home</a>',
     '      <a href="materials.html">Teaching Materials</a>\n'
     '      <a href="https://ling.byu.edu/">Department Home</a>'),

    ("new section",
     '  <section class="section">\n    <h2>Note about Archive Purpose</h2>',
     NEW_SECTION + '  <section class="section">\n    <h2>Note about Archive Purpose</h2>'),

    ("footer grid width",
     '<div class="area-footer-inner">',
     '<div class="area-footer-inner cols-4">'),

    ("footer column",
     '  </div>\n</footer>',
     FOOTER_COL + '  </div>\n</footer>'),
]


def patch(path):
    with open(path, encoding="utf-8") as fh:
        src = fh.read()
    applied, skipped, failed = [], [], []
    for label, find, repl in EDITS:
        if repl in src:
            skipped.append(label)
        elif src.count(find) == 1:
            src = src.replace(find, repl)
            applied.append(label)
        else:
            failed.append(f"{label} (anchor found {src.count(find)}x, expected 1)")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(src)
    print(f"\n{path}")
    for a in applied:
        print(f"   applied  {a}")
    for s in skipped:
        print(f"   already  {s}")
    for f in failed:
        print(f"   FAILED   {f}")
    return not failed


if __name__ == "__main__":
    targets = sys.argv[1:] or ["index.html"]
    ok = all(patch(t) for t in targets)
    sys.exit(0 if ok else 1)
