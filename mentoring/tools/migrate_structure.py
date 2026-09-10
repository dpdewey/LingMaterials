#!/usr/bin/env python3
"""
migrate_structure.py — one-time restructure of the LingMaterials repository.

BEFORE                          AFTER
------                          -----
index.html (mentoring)          index.html                  ← two-door hub
FacultyMentoring/               Mentoring/index.html        ← mentoring landing
MentoredStudent/                Mentoring/FacultyMentoring/
materials.html                  Mentoring/MentoredStudent/
IntermediateEnglish/            TeachingMaterials/index.html
AdvancedEnglish_for_Teachers/   TeachingMaterials/IntermediateEnglish/
TeachingLessons/                TeachingMaterials/AdvancedEnglish_for_Teachers/
FamilyLessonPossessivePronouns/ TeachingMaterials/TeachingLessons/
possessive_*.html (root)        TeachingMaterials/FamilyLessonPossessivePronouns/

embed/ does NOT move — its 8 internal script paths are rewritten instead, so
the Brightspot iframes on the department site keep working untouched.

Usage, from the repository root:

    python3 tools/migrate_structure.py --check    # preview, changes nothing
    python3 tools/migrate_structure.py            # do it

Refuses to run if the repo is already migrated, or if expected folders are
missing. Every action is printed. Nothing is deleted.
"""

import os
import re
import shutil
import sys

CHECK = "--check" in sys.argv

MENTORING_DIRS = ["FacultyMentoring", "MentoredStudent"]
TEACHING_DIRS = [
    "IntermediateEnglish",
    "AdvancedEnglish_for_Teachers",
    "TeachingLessons",
    "FamilyLessonPossessivePronouns",
]
POSSESSIVE_FILES = ["possessive_handout.html", "possessive_survey.html"]
DRAFTS = ["index-2.html", "index-3.html"]

FORM_FACULTY = ("https://docs.google.com/forms/d/e/"
                "1FAIpQLSd1W_Q90Q4yzKKRn0lQjG-Sm-dmK_NUo2xRBQOH9zmJE8hldw/viewform")
FORM_STUDENT = ("https://docs.google.com/forms/d/e/"
                "1FAIpQLSeywfK4kLT_hr1-ZMiMd0-GcE463EaFKrDcEiaOaeaqdlfjAQ/viewform")

log = []


def say(msg):
    log.append(msg)
    print(msg)


def act(msg):
    say(("  would " if CHECK else "  ") + msg)


# ------------------------------------------------------------------ preflight

def preflight():
    problems = []
    if os.path.isdir("Mentoring") or os.path.isdir("TeachingMaterials"):
        problems.append("Mentoring/ or TeachingMaterials/ already exists — "
                        "this repo looks already migrated.")
    for d in MENTORING_DIRS + TEACHING_DIRS:
        if not os.path.isdir(d):
            problems.append(f"expected folder missing: {d}/")
    for f in ("styles.css", "index.html"):
        if not os.path.isfile(f):
            problems.append(f"expected file missing: {f}")
    if not os.path.isdir("assets/logos"):
        problems.append("expected folder missing: assets/logos/")
    return problems


# ------------------------------------------------------------------ chrome

TOPBAR = """<div class="byu-topbar" role="banner">
  <div class="byu-topbar-inner">
    <a href="https://byu.edu" class="byu-mono">BYU</a>
    <span class="sep">|</span>
    <a href="https://hum.byu.edu/" class="topbar-link optional">College of Humanities</a>
    <span class="sep optional">|</span>
    <a href="https://ling.byu.edu/">Linguistics</a>
    <span class="spacer"></span>
    <a href="https://donate.churchofjesuschrist.org/donations/byu/humanities" class="topbar-link optional">Donate</a>
  </div>
</div>"""

UNI_FOOTER = """<div class="university-footer">
  <div class="university-footer-inner">
    <span class="byu-mark">BYU</span>
    <span>Provo, UT 84602, USA &middot; 801-422-4636</span>
    <span>&copy; 2026 Brigham Young University</span>
  </div>
</div>"""


def contact_block(root):
    return f"""    <div>
      <div class="area-footer-logo">
        <img src="{root}assets/logos/ling_horiz_white.png" alt="BYU Linguistics">
      </div>
      <p>
        4064 JFSB<br>
        Brigham Young University<br>
        Provo, UT 84602
      </p>
      <p>
        Office: 801-422-2937<br>
        Email: <a href="mailto:lingoffice@byu.edu">lingoffice@byu.edu</a>
      </p>
    </div>
    <div>
      <h4>Department</h4>
      <ul>
        <li><a href="https://ling.byu.edu/">Department Home</a></li>
        <li><a href="https://ling.byu.edu/faculty-staff-directory">Faculty &amp; Staff</a></li>
        <li><a href="https://ling.byu.edu/about">About</a></li>
        <li><a href="https://ling.byu.edu/news">News</a></li>
      </ul>
    </div>"""


# ------------------------------------------------------------------ new pages

ROOT_HUB = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Linguistics Materials | BYU Department of Linguistics</title>
<meta name="description" content="Two collections from the BYU Department of Linguistics: the Mentoring Archive, and open teaching materials for EFL and ESL classrooms.">
<link rel="stylesheet" href="styles.css">
<link rel="stylesheet" href="styles-materials.css">
</head>
<body>

{TOPBAR}

<header class="byu-navbar">
  <div class="byu-navbar-inner">
    <h1 class="page-title">
      <small>Department of Linguistics</small>
      Linguistics Materials
    </h1>
    <nav>
      <a href="index.html" class="active">Home</a>
      <a href="Mentoring/index.html">Mentoring</a>
      <a href="TeachingMaterials/index.html">Teaching Materials</a>
    </nav>
  </div>
</header>

<section class="hero">
  <div class="hero-inner">
    <div class="hero-subtitle">Department of Linguistics</div>
    <h1>Linguistics Materials</h1>
    <p class="hero-statement">
      Two collections from the BYU Department of Linguistics: a record of
      faculty mentoring and transformative student experiences, and the open
      teaching materials that came out of that mentored work.
    </p>
  </div>
</section>

<main class="main">

  <section class="section">
    <div class="portal-grid">
      <article class="portal-card">
        <div class="portal-card-header">
          <h2>Mentoring Archive</h2>
          <p>Faculty mentoring and student experiences</p>
        </div>
        <div class="portal-card-body">
          <p>
            A dynamic record of how faculty-student out-of-class interactions
            &mdash; office hours, research, lab work, study abroad, and other
            experiential learning &mdash; shape the growth, character, and
            professional trajectories of our students. Faculty document their
            mentoring activities; students reflect on transformative
            experiences in light of the Aims of a BYU Education.
          </p>
          <div class="portal-card-actions">
            <a href="Mentoring/index.html" class="btn btn-primary">Enter the archive</a>
          </div>
        </div>
      </article>

      <article class="portal-card">
        <div class="portal-card-header">
          <h2>Teaching Materials</h2>
          <p>Open lesson plans, handouts, and surveys</p>
        </div>
        <div class="portal-card-body">
          <p>
            Lesson plans, student handouts, interactive practice pages, and
            surveys developed for the department's EFL teacher internship
            programs in Ecuador and Peru, and for professional development with
            practising teachers. Organised by audience and topic, free to use
            and adapt.
          </p>
          <div class="portal-card-actions">
            <a href="TeachingMaterials/index.html" class="btn btn-primary">Browse materials</a>
          </div>
        </div>
      </article>
    </div>
  </section>

</main>

<footer class="area-footer">
  <div class="area-footer-inner">
{contact_block("")}
    <div>
      <h4>This Site</h4>
      <ul>
        <li><a href="Mentoring/index.html">Mentoring Archive</a></li>
        <li><a href="Mentoring/FacultyMentoring/view.html">Faculty Mentoring</a></li>
        <li><a href="Mentoring/MentoredStudent/student-view.html">Student Experiences</a></li>
        <li><a href="TeachingMaterials/index.html">Teaching Materials</a></li>
      </ul>
    </div>
  </div>
</footer>

{UNI_FOOTER}

</body>
</html>
"""

MENTORING_INDEX = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Mentoring Archive | BYU Department of Linguistics</title>
<meta name="description" content="Faculty and student mentoring stories from the BYU Department of Linguistics — capturing transformative learning experiences and faculty-mentored research.">
<link rel="stylesheet" href="../styles.css">
</head>
<body>

{TOPBAR}

<header class="byu-navbar">
  <div class="byu-navbar-inner">
    <h1 class="page-title">
      <small>Department of Linguistics</small>
      Mentoring Archive
    </h1>
    <nav>
      <a href="../index.html">Home</a>
      <a href="index.html" class="active">Mentoring</a>
      <a href="FacultyMentoring/view.html">Faculty Mentoring</a>
      <a href="MentoredStudent/student-view.html">Student Experiences</a>
    </nav>
  </div>
</header>

<section class="hero">
  <div class="hero-inner">
    <div class="hero-subtitle">Department of Linguistics</div>
    <h1>Mentoring Archive</h1>
    <p class="hero-statement">
      A dynamic record of faculty mentoring and transformative student
      experiences in the BYU Department of Linguistics &mdash; capturing how
      faculty-student out-of-class interactions through office hours, research,
      lab work, study abroad, or other experiential learning shape the growth,
      character, and professional trajectories of our students.
    </p>
  </div>
</section>

<section class="quick-links">
  <div class="quick-links-inner">
    <h2>Quick Links</h2>
    <div class="quick-links-grid">
      <a href="FacultyMentoring/view.html">Browse Faculty Stories</a>
      <a href="MentoredStudent/student-view.html">Browse Student Stories</a>
      <a href="{FORM_FACULTY}" target="_blank" rel="noopener">Submit Faculty Entry</a>
      <a href="{FORM_STUDENT}" target="_blank" rel="noopener">Submit Student Entry</a>
      <a href="https://ling.byu.edu/">Department Home</a>
    </div>
  </div>
</section>

<main class="main">

  <section class="section">
    <h2>Two Archives, One Story</h2>
    <p style="font-size: 1.0625rem; max-width: 760px; color: var(--text-dark);">
      The mentoring archive is organized into two collections. Faculty
      members document their mentoring activities &mdash; experiential learning
      opportunities that have a lasting impact on student and faculty
      development. Students reflect on transformative experiences with
      faculty in light of the
      <a href="https://aims.byu.edu/aims-of-a-byu-education" target="_blank" rel="noopener">Aims of a BYU Education</a>.
    </p>

    <div class="portal-grid">
      <article class="portal-card">
        <div class="portal-card-header">
          <h2>Faculty Mentoring</h2>
          <p>Transformative mentoring outcomes</p>
        </div>
        <div class="portal-card-body">
          <p>
            Document mentoring activities such as coauthored papers,
            presentations at venues like ACES, AAAL or LSA, or undergraduate
            or graduate research projects. This archive tracks student-faculty
            out-of-class interactions and their impact on student growth and
            trajectories and on faculty motivation and development. Entries
            can be public or marked private for departmental records only.
          </p>
          <div class="portal-card-actions">
            <a href="FacultyMentoring/view.html" class="btn btn-primary">View Archive</a>
            <a href="{FORM_FACULTY}" target="_blank" rel="noopener" class="btn btn-secondary">Add Entry</a>
          </div>
        </div>
      </article>

      <article class="portal-card">
        <div class="portal-card-header">
          <h2>Student Experiences</h2>
          <p>Transformative experiences with faculty</p>
        </div>
        <div class="portal-card-body">
          <p>
            Students share how out-of-class mentored experiences &mdash; research,
            internships, study abroad, conference presentations, office hour
            conversations &mdash; shaped their development across the four BYU Aims:
            spiritually strengthening, intellectually enlarging,
            character-building, and lifelong learning &amp; service.
          </p>
          <div class="portal-card-actions">
            <a href="MentoredStudent/student-view.html" class="btn btn-primary">View Archive</a>
            <a href="{FORM_STUDENT}" target="_blank" rel="noopener" class="btn btn-secondary">Add Entry</a>
          </div>
        </div>
      </article>
    </div>
  </section>

  <section class="section">
    <h2>Note about Archive Purpose</h2>
    <p style="max-width: 760px;">
      This archive was created to help the BYU Department of Linguistics
      document and preserve memory of the work of faculty mentors and the
      resulting transformative experiences of students. It serves the
      department's reporting needs, aids in faculty reflection for the
      purposes of their own professional development, and allows students
      to tell others about transformative experiences they have had with
      Department faculty members.
    </p>
    <p style="max-width: 760px;">
      Entries can be public or private at the contributor's discretion.
      Public entries appear in the open archive; private content is
      reserved for departmental review.
    </p>
  </section>

</main>

<footer class="area-footer">
  <div class="area-footer-inner">
{contact_block("../")}
    <div>
      <h4>Mentoring Archive</h4>
      <ul>
        <li><a href="index.html">Archive Home</a></li>
        <li><a href="FacultyMentoring/view.html">Faculty Mentoring</a></li>
        <li><a href="MentoredStudent/student-view.html">Student Experiences</a></li>
        <li><a href="{FORM_FACULTY}" target="_blank" rel="noopener">Submit Faculty Entry</a></li>
        <li><a href="{FORM_STUDENT}" target="_blank" rel="noopener">Submit Student Entry</a></li>
      </ul>
    </div>
  </div>
</footer>

{UNI_FOOTER}

</body>
</html>
"""

STUB = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>This page has moved</title>
<link rel="canonical" href="{target}">
<meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0; url={target}">
<script>location.replace("{target}");</script>
<style>body{{font-family:-apple-system,"IBM Plex Sans",Helvetica,Arial,sans-serif;
max-width:34rem;margin:5rem auto;padding:0 1.5rem;color:#141414;line-height:1.6}}
a{{color:#0047BA}}</style>
</head>
<body>
<h1 style="font-size:1.375rem;color:#002E5D">This page has moved</h1>
<p>You should be redirected automatically. If not,
<a href="{target}">continue to the new location</a>.</p>
</body>
</html>
"""

STUBS = {
    "FacultyMentoring/view.html": "../Mentoring/FacultyMentoring/view.html",
    "FacultyMentoring/entry.html": "../Mentoring/FacultyMentoring/entry.html",
    "FacultyMentoring/admin.html": "../Mentoring/FacultyMentoring/admin.html",
    "MentoredStudent/student-view.html": "../Mentoring/MentoredStudent/student-view.html",
    "MentoredStudent/student-entry.html": "../Mentoring/MentoredStudent/student-entry.html",
    "MentoredStudent/admin.html": "../Mentoring/MentoredStudent/admin.html",
    "materials.html": "TeachingMaterials/index.html",
}


# ------------------------------------------------------------------ steps

def move(src, dst):
    act(f"move  {src}  ->  {dst}")
    if not CHECK:
        os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
        shutil.move(src, dst)


def rewrite(path, pairs, label):
    """Apply (find, replace) pairs to a file. Returns number of edits."""
    if not os.path.isfile(path):
        return 0
    with open(path, encoding="utf-8", errors="ignore") as fh:
        src = fh.read()
    orig, n = src, 0
    for find, repl in pairs:
        c = src.count(find)
        if c:
            src = src.replace(find, repl)
            n += c
    if src != orig:
        act(f"rewrite {path}  ({n} {label})")
        if not CHECK:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(src)
    return n


def step_move_folders():
    say("\n[1] Moving folders")
    for d in MENTORING_DIRS:
        move(d, os.path.join("Mentoring", d))
    for d in TEACHING_DIRS:
        move(d, os.path.join("TeachingMaterials", d))
    for f in POSSESSIVE_FILES:
        if os.path.isfile(f):
            move(f, os.path.join("TeachingMaterials",
                                 "FamilyLessonPossessivePronouns", f))
        else:
            say(f"  note: {f} not in root — skipping (already moved?)")
    # Superseded drafts: parked with a .bak suffix so GitHub Pages does not
    # serve them as live (and now broken) pages. Content is preserved; git
    # history has them too. Delete the folder whenever you like.
    for f in DRAFTS:
        if os.path.isfile(f):
            move(f, os.path.join("Mentoring", "drafts", f + ".bak"))


def step_fix_mentoring_pages():
    say("\n[2] Fixing paths inside the moved mentoring pages")
    if CHECK:
        say("  (not previewable — depends on step 1 having run)")
    pairs = [
        # one level deeper now
        ('"../assets/logos/', '"../../assets/logos/'),
        # nav: '../index.html' now means Mentoring/index.html, which is right,
        # but it should be labelled as such, with a separate link to the root.
        # footer FIRST — its <li> contains the nav pattern as a substring
        ('<li><a href="../index.html">Home</a></li>',
         '<li><a href="../index.html">Archive Home</a></li>'),
        # nav: exact 6-space indent + trailing newline so it matches only the
        # nav bar, never the footer list
        ('      <a href="../index.html">Home</a>\n',
         '      <a href="../../index.html">Home</a>\n'
         '      <a href="../index.html">Mentoring</a>\n'),
        # undo the earlier teaching-materials integration, if it was applied
        ('<link rel="stylesheet" href="../styles-materials.css">\n', ''),
        ('      <a href="../materials.html">Teaching Materials</a>\n', ''),
        ('<div class="area-footer-inner cols-4">', '<div class="area-footer-inner">'),
    ]
    total = 0
    for d in MENTORING_DIRS:
        folder = os.path.join("Mentoring", d)
        if not os.path.isdir(folder):
            continue
        for f in sorted(os.listdir(folder)):
            if f.endswith(".html"):
                total += rewrite(os.path.join(folder, f), pairs, "path edits")
    # drop the teaching-materials footer column if the earlier patch added it
    for d in MENTORING_DIRS:
        folder = os.path.join("Mentoring", d)
        if not os.path.isdir(folder):
            continue
        for f in sorted(os.listdir(folder)):
            if not f.endswith(".html"):
                continue
            p = os.path.join(folder, f)
            with open(p, encoding="utf-8", errors="ignore") as fh:
                s = fh.read()
            new = re.sub(
                r'\s*<div>\s*<h4>Teaching Materials</h4>.*?</ul>\s*</div>\n',
                '\n', s, flags=re.S)
            if new != s:
                act(f"rewrite {p}  (removed Teaching Materials footer column)")
                if not CHECK:
                    with open(p, "w", encoding="utf-8") as fh:
                        fh.write(new)
    say(f"  total path edits: {total}")


def step_fix_embed():
    say("\n[3] Rewriting embed/ script paths (keeps Brightspot iframes working)")
    pairs = [
        ('src="../../FacultyMentoring/', 'src="../../Mentoring/FacultyMentoring/'),
        ('src="../../MentoredStudent/', 'src="../../Mentoring/MentoredStudent/'),
        # NOTE: embed/index.html's href="FacultyMentoring/..." links point at
        # the chrome-free copies inside embed/, which do NOT move. They are
        # deliberately left alone.
    ]
    total = 0
    for root, _, files in os.walk("embed"):
        for f in sorted(files):
            if f.endswith(".html"):
                total += rewrite(os.path.join(root, f), pairs, "script/link edits")
    say(f"  total embed edits: {total}")
    say("  note: ../../storage.js, ../../seed-data.js and ../../student-seed.js")
    say("        stay at the repo root and were deliberately NOT changed.")


def step_new_pages():
    say("\n[4] Writing the new hub and mentoring landing pages")
    for path, content in (("index.html", ROOT_HUB),
                          ("Mentoring/index.html", MENTORING_INDEX)):
        act(f"write {path}")
        if not CHECK:
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(content)


def step_stubs():
    say("\n[5] Writing redirect stubs at the old URLs")
    for old, target in STUBS.items():
        act(f"stub  {old}  ->  {target}")
        if not CHECK:
            os.makedirs(os.path.dirname(old) or ".", exist_ok=True)
            with open(old, "w", encoding="utf-8") as fh:
                fh.write(STUB.format(target=target))


def step_nojekyll():
    say("\n[6] Ensuring .nojekyll exists")
    if os.path.exists(".nojekyll"):
        say("  already present")
    else:
        act("write .nojekyll")
        if not CHECK:
            open(".nojekyll", "w").close()


def step_build_materials():
    say("\n[7] Generating the teaching-materials pages")
    if CHECK:
        say("  would run tools/build_materials.py")
        return
    sys.path.insert(0, os.path.join(os.getcwd(), "tools"))
    import build_materials
    for w in build_materials.build_all():
        say(f"  wrote {w}")


# ------------------------------------------------------------------ main

def main():
    problems = preflight()
    if problems:
        print("Cannot migrate:\n")
        for p in problems:
            print("  -", p)
        print("\nRun this from the repository root. If the repo is already")
        print("migrated, there is nothing to do.")
        return 1

    say("=" * 62)
    say("  LingMaterials restructure" + ("  [--check: PREVIEW ONLY]" if CHECK else ""))
    say("=" * 62)

    step_move_folders()
    step_fix_mentoring_pages()
    step_fix_embed()
    step_new_pages()
    step_stubs()
    step_nojekyll()
    step_build_materials()

    say("\n" + "=" * 62)
    if CHECK:
        say("  Preview complete. Nothing was changed.")
        say("  Re-run without --check to apply.")
    else:
        say("  Done. Next steps:")
        say("    1. Open index.html in a browser and click through both doors.")
        say("    2. Commit and push in GitHub Desktop.")
        say("    3. Check the Brightspot embeds on the department site still load.")
        say("    4. Once satisfied, consider deleting Mentoring/drafts/ and")
        say("       the orphaned root file student-styles.css.")
    say("=" * 62)
    return 0


if __name__ == "__main__":
    sys.exit(main())
