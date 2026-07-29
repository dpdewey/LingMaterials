#!/usr/bin/env python3
"""
build_materials.py — generates the Teaching Materials pages for
https://dpdewey.github.io/LingMaterials/

Emits:
    materials.html                              (hub)
    IntermediateEnglish/index.html              (catalogue)
    AdvancedEnglish_for_Teachers/index.html     (catalogue)
    TeachingLessons/index.html                  (catalogue)
    FamilyLessonPossessivePronouns/index.html   (catalogue)

To add a new material: add a dict to the right SETS list and re-run.
    python3 tools/build_materials.py

Everything is driven by the PROJECTS structure below. Markup uses the
existing BYU brand classes from styles.css plus the .mat-* classes in
styles-materials.css. No other file is touched.
"""

import html
import os
import urllib.parse

OUT = os.environ.get("LINGMATERIALS_ROOT", ".")

# ---------------------------------------------------------------- shared chrome

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


def navbar(page_title, subtitle, prefix, active):
    """active: 'home' | 'faculty' | 'student' | 'materials'"""
    def cls(key):
        return ' class="active"' if key == active else ""
    return f"""<header class="byu-navbar">
  <div class="byu-navbar-inner">
    <h1 class="page-title">
      <small>{subtitle}</small>
      {page_title}
    </h1>
    <nav>
      <a href="{prefix}index.html"{cls('home')}>Home</a>
      <a href="{prefix}FacultyMentoring/view.html"{cls('faculty')}>Faculty Mentoring</a>
      <a href="{prefix}MentoredStudent/student-view.html"{cls('student')}>Student Experiences</a>
      <a href="{prefix}materials.html"{cls('materials')}>Teaching Materials</a>
    </nav>
  </div>
</header>"""


def footers(prefix):
    return f"""<footer class="area-footer">
  <div class="area-footer-inner cols-4">
    <div>
      <div class="area-footer-logo">
        <img src="{prefix}assets/logos/ling_horiz_white.png" alt="BYU Linguistics">
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
    </div>
    <div>
      <h4>Mentoring Archive</h4>
      <ul>
        <li><a href="{prefix}index.html">Archive Home</a></li>
        <li><a href="{prefix}FacultyMentoring/view.html">Faculty Mentoring</a></li>
        <li><a href="{prefix}MentoredStudent/student-view.html">Student Experiences</a></li>
      </ul>
    </div>
    <div>
      <h4>Teaching Materials</h4>
      <ul>
        <li><a href="{prefix}materials.html">All Materials</a></li>
        <li><a href="{prefix}IntermediateEnglish/">Intermediate English</a></li>
        <li><a href="{prefix}AdvancedEnglish_for_Teachers/">Advanced English for Teachers</a></li>
        <li><a href="{prefix}TeachingLessons/">Classroom Lessons</a></li>
      </ul>
    </div>
  </div>
</footer>

<div class="university-footer">
  <div class="university-footer-inner">
    <span class="byu-mark">BYU</span>
    <span>Provo, UT 84602, USA &middot; 801-422-4636</span>
    <span>&copy; 2026 Brigham Young University</span>
  </div>
</div>"""


def page(title, description, prefix, body):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="stylesheet" href="{prefix}styles.css">
<link rel="stylesheet" href="{prefix}styles-materials.css">
</head>
<body>

{TOPBAR}

{body}

{footers(prefix)}

</body>
</html>
"""


# ---------------------------------------------------------------- data model
#
# Each project = folder name + presentation metadata + list of "sets".
# A set is one topic; its files are the roles that topic comes in
# (lesson plan / handout / survey / etc). That grouping is real — these
# materials were authored as triads — so it drives the layout.

PROJECTS = [
    {
        "folder": "IntermediateEnglish",
        "name": "Intermediate English",
        "audience": "A2–B2 learners",
        "blurb": (
            "Topic units for intermediate English learners, each built as a lesson "
            "plan, a student handout, and a short survey. Most units come in two "
            "parallel levels so the same topic can run in a mixed-proficiency class."
        ),
        "hero": (
            "Topic units for intermediate learners — football, food, and travel — "
            "each written at two proficiency levels so the same lesson can run "
            "across a mixed-ability class."
        ),
        "note": (
            "<p>Units marked <strong>A2–B1</strong> and <strong>B1–B2</strong> cover the same "
            "topic at different levels. Pair them when you are teaching a mixed-proficiency "
            "group: the tasks align, so both halves of the class can share a final activity.</p>"
        ),
        "sets": [
            {
                "id": "football",
                "title": "Football",
                "note": "Sport as a way into opinion language, comparatives, and structured disagreement.",
                "chips": ["A2–B1", "B1–B2", "Speaking", "Debate"],
                "files": [
                    ("football_lesson_plan_A2B1.html", "Lesson plan", "I Love Football", "A2–B1"),
                    ("football_handout_A2B1.html", "Handout", "I Love Football", "A2–B1"),
                    ("football_survey_A2B1.html", "Survey", "I Love Football", "A2–B1"),
                    ("football_debate_A2B1.html", "Debate", "Structured debate activity", "A2–B1"),
                    ("football_lesson_plan_B1B2.html", "Lesson plan", "Football &amp; Us", "B1–B2"),
                    ("football_handout_B1B2.html", "Handout", "Football &amp; Us", "B1–B2"),
                    ("football_survey_B1B2.html", "Survey", "Football &amp; Us", "B1–B2"),
                ],
            },
            {
                "id": "food",
                "title": "Food, Cooking &amp; Culture",
                "note": "Preferences, food vocabulary, and cultural comparison, with a pair role-play and printable fill-in practice.",
                "chips": ["A2", "A2–B1", "B1–B2", "Role-play"],
                "files": [
                    ("gastronomy_lesson_plan_A2B1.html", "Lesson plan", "Food I Like", "A2–B1"),
                    ("gastronomy_handout_A2B1.html", "Handout", "Food I Like", "A2–B1"),
                    ("gastronomy_survey_A2B1.html", "Survey", "Food I Like", "A2–B1"),
                    ("gastronomy_lesson_plan_B1B2.html", "Lesson plan", "Food, Cooking &amp; Culture", "B1–B2"),
                    ("gastronomy_handout_B1B2.html", "Handout", "Food, Cooking &amp; Culture", "B1–B2"),
                    ("gastronomy_survey_B1B2.html", "Survey", "Food, Cooking &amp; Culture", "B1–B2"),
                    ("food_roleplay_A2.html", "Role-play", "Talk About Food — pair task", "A2"),
                    ("Fill_In_Foods1.pdf", "Print practice", "Food vocabulary fill-in", ""),
                ],
            },
            {
                "id": "travel",
                "title": "Travel &amp; Places",
                "note": "Describing places, expressing wishes and plans, and talking about famous destinations.",
                "chips": ["A2–B1", "B1–B2", "Speaking"],
                "files": [
                    ("tourism_lesson_plan_A2B1.html", "Lesson plan", "Places I Want To See", "A2–B1"),
                    ("tourism_handout_A2B1.html", "Handout", "Places I Want To See", "A2–B1"),
                    ("tourism_survey_A2B1.html", "Survey", "Places I Want To See", "A2–B1"),
                    ("tourism_lesson_plan_B1B2.html", "Lesson plan", "Travel &amp; Famous Places", "B1–B2"),
                    ("tourism_handout_B1B2.html", "Handout", "Travel &amp; Famous Places", "B1–B2"),
                    ("tourism_survey_B1B2.html", "Survey", "Travel &amp; Famous Places", "B1–B2"),
                ],
            },
            {
                "id": "sports-chunks",
                "title": "Sports Language Chunks",
                "note": "Formulaic sequences for talking about sport, with a printable fill-in and Spanish glosses for L1 support.",
                "chips": ["A2–B1", "Vocabulary", "Spanish glosses"],
                "files": [
                    ("talk-sports.html", "Interactive", "Talk Sports — chunk practice", "A2–B1"),
                    ("SportsPhrasesFill_In.pdf", "Print practice", "Sports phrases fill-in", ""),
                    ("SportsPhrasesSpanishTranslations.pdf", "Reference", "Sports phrases with Spanish translations", ""),
                ],
            },
        ],
    },
    {
        "folder": "AdvancedEnglish_for_Teachers",
        "name": "Advanced English for Teachers",
        "audience": "B2–C1 practising EFL teachers",
        "blurb": (
            "The <em>Teach for Success!</em> professional development suite. Each unit "
            "pairs advanced content-based language work with a reflective survey on "
            "teaching beliefs and practice."
        ),
        "hero": (
            "The <em>Teach for Success!</em> suite — advanced content-based units for "
            "practising EFL teachers, each with a lesson plan, a discussion handout, "
            "and a survey that turns the topic back on the teacher's own practice."
        ),
        "note": (
            "<p>These units are written for <strong>teachers as learners</strong>: the language "
            "work is B2–C1, and the surveys collect beliefs and self-reported practice "
            "rather than testing comprehension. Surveys post to Google Forms, so responses "
            "arrive in a sheet you control.</p>"
        ),
        "sets": [
            {
                "id": "core",
                "title": "Teach for Success! — Core Session",
                "note": "The anchor 55-minute session, with an annotated plan showing the SLA rationale behind each stage.",
                "chips": ["B2–C1", "Annotated plan", "Teacher beliefs"],
                "files": [
                    ("teach_lesson_plan.html", "Lesson plan", "Annotated 55-minute session plan", "B2–C1"),
                    ("teach_lesson_handout.html", "Handout", "Participant handout", "B2–C1"),
                    ("teacher_beliefs_survey.html", "Survey", "Teacher beliefs &amp; practices", ""),
                ],
            },
            {
                "id": "braindrain",
                "title": "Brain Drain &amp; Migration",
                "note": "Academic migration and its effects on home institutions. Two versions of the plan and handout; the revised pair is the later draft.",
                "chips": ["B2–C1", "Discussion", "Two drafts"],
                "files": [
                    ("braindrain_lesson_plan2.html", "Lesson plan", "Revised version — recommended", "B2–C1"),
                    ("braindrain_handout2.html", "Handout", "Revised version — recommended", "B2–C1"),
                    ("braindrain_survey.html", "Survey", "Brain drain survey", ""),
                    ("braindrain_lesson_plan.html", "Lesson plan", "Earlier draft", "B2–C1"),
                    ("braindrain_handout.html", "Handout", "Earlier draft", "B2–C1"),
                ],
            },
            {
                "id": "democracy",
                "title": "Democracy &amp; Voting",
                "note": "Civic participation as a content vehicle for hedging, conditionals, and argument structure.",
                "chips": ["B2–C1", "Discussion"],
                "files": [
                    ("democracy_lesson_plan.html", "Lesson plan", "Democracy &amp; Voting", "B2–C1"),
                    ("democracy_handout.html", "Handout", "Democracy &amp; Voting", "B2–C1"),
                    ("democracy_survey.html", "Survey", "Democracy &amp; Voting", ""),
                ],
            },
            {
                "id": "heritage",
                "title": "Heritage, Mass Tourism &amp; Cultural Preservation",
                "note": "How places get labelled and sold — reading tourism language critically. Includes a B1–B2 adaptation of the handout.",
                "chips": ["B2–C1", "B1–B2 adaptation", "Critical reading"],
                "files": [
                    ("tourism_labels_lesson_plan.html", "Lesson plan", "The Words We Travel Under", "B2–C1"),
                    ("tourism_labels_handout.html", "Handout", "The Words We Travel Under", "B2–C1"),
                    ("tourism_labels_survey.html", "Survey", "Heritage &amp; mass tourism", ""),
                    ("tourism_handout_b1b2.html", "Handout", "Adapted for B1–B2", "B1–B2"),
                ],
            },
        ],
    },
    {
        "folder": "TeachingLessons",
        "name": "Classroom Lessons",
        "audience": "Young learners &amp; teacher training",
        "blurb": (
            "Interactive lessons for young EFL learners in Ecuador and Peru, memory "
            "and retrieval demonstrations for teacher training, and standalone "
            "professional development handouts."
        ),
        "hero": (
            "Day-by-day interactive lessons for young learners, live memory "
            "demonstrations for teacher training sessions, and standalone "
            "professional development handouts."
        ),
        "note": (
            "<p>The <strong>memory demonstrations</strong> are designed to be run live: split the "
            "room, send Group A and Group B to different pages, then bring everyone to the "
            "shared test page. Don't preview the test page on the projector first.</p>"
        ),
        "sets": [
            {
                "id": "days",
                "title": "Young Learner Day Sets",
                "note": "Four consecutive days, each with an interactive practice page, a quiz, and printable cards for TPR-style games.",
                "chips": ["Young learners", "Interactive", "Printables"],
                "files": [
                    ("day1_get_to_know.html", "Practice", "Day 1 — Get to Know", ""),
                    ("day1_quiz.html", "Quiz", "Day 1 — Get to Know", ""),
                    ("day1_printable_cards.pdf", "Cards", "Day 1 — printable set", ""),
                    ("day2_get_to_know.html", "Practice", "Day 2 — Likes &amp; Dislikes", ""),
                    ("day2_quiz.html", "Quiz", "Day 2 — Likes &amp; Dislikes", ""),
                    ("day2_printable_cards.pdf", "Cards", "Day 2 — printable set", ""),
                    ("day3_get_to_know.html", "Practice", "Day 3 — Family", ""),
                    ("day3_quiz.html", "Quiz", "Day 3 — Family", ""),
                    ("day3_printable_cards.pdf", "Cards", "Day 3 — printable set", ""),
                    ("day4_get_to_know.html", "Practice", "Day 4 — Directions &amp; Locations", ""),
                    ("day4_quiz.html", "Quiz", "Day 4 — Directions &amp; Locations", ""),
                    ("day4_printable_cards.pdf", "Cards", "Day 4 — printable set", ""),
                    ("family_tree_practice.html", "Practice", "Family tree — extra practice for Day 3", ""),
                ],
            },
            {
                "id": "listening",
                "title": "Listening Exercises",
                "note": "Bundled listening sets used alongside the day lessons.",
                "chips": ["Young learners", "Listening"],
                "files": [
                    ("ListeningExercisesDay3_1.html", "Listening", "Day 3 listening set", ""),
                    ("Listening Exercises - Day 4.html", "Listening", "Day 4 listening set", ""),
                    ("Likes_Dislikes_Teach.html", "Listening", "Likes &amp; dislikes — teaching version", ""),
                ],
            },
            {
                "id": "birdguide",
                "title": "Bird Guide English",
                "note": "English for reserve workers and guides: species names, visitor questions, and field small talk.",
                "chips": ["ESP", "Interactive", "Printables"],
                "files": [
                    ("birdguide_get_to_know.html", "Practice", "Bird Guide English — practice", ""),
                    ("birdguide_quiz.html", "Quiz", "Bird Guide English — quiz", ""),
                    ("birdguide_printable_cards.pdf", "Cards", "Bird guide printable set", ""),
                ],
            },
            {
                "id": "memory",
                "title": "Memory &amp; Retrieval Demonstrations",
                "note": "Two live split-group demonstrations for teacher training. Group A and Group B get different instructions, then both take the same test.",
                "chips": ["Teacher training", "Run live", "Split groups"],
                "files": [
                    ("Memory/demo1-reread.html", "Group A", "Demo 1 — read &amp; re-read", ""),
                    ("Memory/demo1-recall.html", "Group B", "Demo 1 — read &amp; recall", ""),
                    ("Memory/demo1-test.html", "Shared test", "Demo 1 — both groups", ""),
                    ("Memory/demo2-memorize.html", "Group A", "Demo 2 — memorise the statements", ""),
                    ("Memory/demo2-person.html", "Group B", "Demo 2 — get to know this person", ""),
                    ("Memory/demo2-test.html", "Shared test", "Demo 2 — both groups", ""),
                ],
            },
            {
                "id": "pd",
                "title": "Professional Development Handouts",
                "note": "Standalone review-and-self-check handouts on three evidence-based classroom practices.",
                "chips": ["Teacher training", "Self-check"],
                "files": [
                    ("translanguaging-handout.html", "Handout", "Translanguaging", ""),
                    ("translanguaging_survey.html", "Survey", "Translanguaging — teacher survey", ""),
                    ("retrieval-handout.html", "Handout", "Retrieval practice", ""),
                    ("output-handout.html", "Handout", "Pushed output", ""),
                ],
            },
        ],
    },
    {
        "folder": "FamilyLessonPossessivePronouns",
        "name": "Possessive Pronouns &amp; Family",
        "audience": "Intermediate ESL grammar",
        "blurb": (
            "A single grammar-focused unit on possessive pronouns in the context of "
            "family vocabulary, with slides, a student handout, and a survey."
        ),
        "hero": (
            "One grammar unit, fully built out: possessive pronouns taught through "
            "family vocabulary, with slides for the front of the room and a handout "
            "for the desk."
        ),
        "note": (
            "<p>The handout and survey currently sit in the <strong>repository root</strong> rather "
            "than in this folder, so the links below point one level up. Moving them into "
            "this folder is listed as optional cleanup in <code>INTEGRATION_NOTES.md</code>; "
            "if you do move them, drop the <code>../</code> from the two links.</p>"
        ),
        "sets": [
            {
                "id": "possessives",
                "title": "Possessive Pronouns &amp; Family",
                "note": "Slides, handout, and survey for the possessive pronoun unit.",
                "chips": ["Intermediate", "Grammar", "Slides"],
                "files": [
                    ("Possessive Pronoun Family Activities.pptx", "Slides", "Classroom activity deck", ""),
                    ("../possessive_handout.html", "Handout", "Student handout", ""),
                    ("../possessive_survey.html", "Survey", "Possessive pronouns survey", ""),
                ],
            },
        ],
    },
]


# ---------------------------------------------------------------- rendering

def filetype(path):
    ext = os.path.splitext(path)[1].lower().lstrip(".")
    return {"html": "HTML", "pdf": "PDF", "pptx": "PPTX", "jpg": "IMG"}.get(ext, ext.upper())


def render_item(path, role, label, level):
    href = urllib.parse.quote(path)
    ft = filetype(path)
    target = ' target="_blank" rel="noopener"' if ft in ("PDF", "PPTX") else ""
    lvl = f' <span class="mat-item-desc">{level}</span>' if level else ""
    return f"""      <li class="mat-item">
        <span class="mat-item-role">{role}</span>
        <span class="mat-item-name"><a href="{href}"{target}>{label}</a>{lvl}</span>
        <span class="mat-item-type" data-type="{ft}">{ft}</span>
      </li>"""


def render_set(s):
    chips = ""
    if s.get("chips"):
        chips = '\n      <div class="mat-chips">' + "".join(
            f'<span class="mat-chip">{c}</span>' for c in s["chips"]
        ) + "</div>"
    items = "\n".join(render_item(*f) for f in s["files"])
    return f"""  <section class="mat-set" id="{s['id']}">
    <div class="mat-set-head">
      <h3>{s['title']}</h3>
      <p class="mat-set-note">{s['note']}</p>{chips}
    </div>
    <ul class="mat-list">
{items}
    </ul>
  </section>"""


def count_files(project):
    return sum(len(s["files"]) for s in project["sets"])


def build_project(project):
    toc = "\n".join(
        f'        <li><a href="#{s["id"]}">{s["title"]}</a></li>' for s in project["sets"]
    )
    sets = "\n\n".join(render_set(s) for s in project["sets"])
    plain = html.unescape(project["name"])
    body = f"""{navbar(project['name'], 'Teaching Materials', '../', 'materials')}

<section class="hero">
  <div class="hero-inner">
    <div class="mat-crumb"><a href="../materials.html">&larr; All teaching materials</a></div>
    <div class="hero-subtitle">{project['audience']}</div>
    <h1>{project['name']}</h1>
    <p class="hero-statement">{project['hero']}</p>
  </div>
</section>

<main class="main">

  <div class="mat-note">
{project['note']}
  </div>

  <nav class="mat-toc" aria-label="Contents">
    <h2>On this page</h2>
    <ul>
{toc}
    </ul>
  </nav>

{sets}

</main>"""
    out = os.path.join(OUT, project["folder"], "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(page(
            f"{plain} | BYU Linguistics Teaching Materials",
            f"{plain} — open teaching materials from the BYU Department of Linguistics: "
            f"lesson plans, handouts, and surveys for {html.unescape(project['audience'])}.",
            "../",
            body,
        ))
    return out


def build_hub():
    cards = []
    for p in PROJECTS:
        n = count_files(p)
        cards.append(f"""      <article class="mat-project">
        <h3>{p['name']}</h3>
        <p class="mat-project-audience">{p['audience']}</p>
        <p>{p['blurb']}</p>
        <div class="mat-project-foot">
          <span class="mat-project-count">{n} files</span>
          <a href="{p['folder']}/" class="btn btn-primary">Open</a>
        </div>
      </article>""")
    total = sum(count_files(p) for p in PROJECTS)
    body = f"""{navbar('Teaching Materials', 'Department of Linguistics', '', 'materials')}

<section class="hero">
  <div class="hero-inner">
    <div class="hero-subtitle">Department of Linguistics</div>
    <h1>Teaching Materials</h1>
    <p class="hero-statement">
      Open lesson plans, handouts, interactive practice pages, and surveys
      developed for the department's EFL teacher internship programs in
      Ecuador and Peru, and for professional development with practising
      teachers. {total} files across {len(PROJECTS)} collections, free to
      use and adapt.
    </p>
  </div>
</section>

<main class="main">

  <section class="section">
    <h2>Collections</h2>
    <p style="max-width: 760px;">
      Materials are grouped by the audience they were written for. Within each
      collection, files are organised by topic: most topics come as a matched
      set of a lesson plan, a student handout, and a survey, so you can pick up
      a whole unit at once rather than assembling it from parts.
    </p>
    <div class="mat-projects">
{chr(10).join(cards)}
    </div>
  </section>

  <section class="section">
    <h2>Using these materials</h2>
    <div class="panels">
      <div class="panel">
        <h3>What to expect</h3>
        <p>
          Most files are single self-contained HTML pages. Open one in a browser
          and it works — no install, no login, nothing to configure. Interactive
          pages run entirely in the browser, so they also work offline once the
          page has loaded, which matters in classrooms with unreliable
          connections.
        </p>
        <p>
          The teaching materials use their own visual design, distinct from the
          department pages you are on now. That is deliberate: they were built to
          hold a young learner's attention on a projector.
        </p>
      </div>
      <div class="panel">
        <h3>Printing and adapting</h3>
        <p>
          Handouts are laid out to print from the browser at A4 or Letter. Card
          sets and fill-in practice are supplied as PDFs so page breaks hold.
          Slides are PowerPoint files and will download rather than open in the
          browser.
        </p>
        <p>
          Everything here may be reused and adapted for teaching. If you adapt a
          unit substantially and would like it added back to the collection,
          contact the department office.
        </p>
      </div>
    </div>
  </section>

  <section class="section">
    <h2>Related</h2>
    <p style="max-width: 760px;">
      These materials came out of mentored work with students and partner
      institutions. The
      <a href="index.html">Mentoring Archive</a> documents that side of the
      department's work — faculty mentoring activities and student reflections
      on transformative mentored experiences.
    </p>
  </section>

</main>"""
    out = os.path.join(OUT, "materials.html")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(page(
            "Teaching Materials | BYU Department of Linguistics",
            "Open EFL and ESL teaching materials from the BYU Department of Linguistics — "
            "lesson plans, handouts, interactive practice pages, and surveys for learners "
            "and for practising teachers.",
            "",
            body,
        ))
    return out


if __name__ == "__main__":
    written = [build_hub()] + [build_project(p) for p in PROJECTS]
    for w in written:
        print("wrote", w)
