#!/usr/bin/env python3
"""
patch_subpages.py — extends the nav bar and footer of the public mentoring
archive pages so "Teaching Materials" appears everywhere, not just on the
home page.

Run from the repo root:

    python3 tools/patch_subpages.py

Touches only the four public archive pages. The password-gated admin pages
are deliberately left alone — they're internal tools and don't need a link
out to teaching materials.

Idempotent: re-running on an already-patched file is a no-op.
"""

import os
import sys

TARGETS = [
    "FacultyMentoring/view.html",
    "FacultyMentoring/entry.html",
    "MentoredStudent/student-view.html",
    "MentoredStudent/student-entry.html",
]

FOOTER_COL = """    <div>
      <h4>Teaching Materials</h4>
      <ul>
        <li><a href="../materials.html">All Materials</a></li>
        <li><a href="../IntermediateEnglish/">Intermediate English</a></li>
        <li><a href="../AdvancedEnglish_for_Teachers/">Advanced English for Teachers</a></li>
        <li><a href="../TeachingLessons/">Classroom Lessons</a></li>
      </ul>
    </div>
"""

EDITS = [
    ("stylesheet link",
     '<link rel="stylesheet" href="styles.css">',
     '<link rel="stylesheet" href="styles.css">\n'
     '<link rel="stylesheet" href="../styles-materials.css">'),

    ("navbar link",
     '    </nav>\n  </div>\n</header>',
     '      <a href="../materials.html">Teaching Materials</a>\n'
     '    </nav>\n  </div>\n</header>'),

    ("footer grid width",
     '<div class="area-footer-inner">',
     '<div class="area-footer-inner cols-4">'),

    ("footer column",
     '  </div>\n</footer>',
     FOOTER_COL + '  </div>\n</footer>'),
]


def patch(path):
    if not os.path.exists(path):
        print(f"\n{path}\n   SKIPPED  file not found")
        return True
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
    targets = sys.argv[1:] or TARGETS
    sys.exit(0 if all(patch(t) for t in targets) else 1)
