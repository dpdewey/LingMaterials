# BYU Linguistics — Mentoring Archive & Teaching Materials

This repository hosts two related bodies of work for the BYU Department
of Linguistics, published together at
<https://dpdewey.github.io/LingMaterials/>.

## 1. Mentoring Archive

- **Faculty Mentoring** — mentor-submitted records of research projects,
  conference presentations, and student-development outcomes.
- **Student Experiences** — student reflections on transformative
  mentored experiences, organized by the four BYU Aims.

Entry point: `index.html`

## 2. Teaching Materials

Open EFL/ESL materials produced through the department's teacher
internship programs in Ecuador and Peru and through professional
development work with practising teachers.

Entry point: `materials.html`

| Collection | Folder | Audience |
|---|---|---|
| Intermediate English | `IntermediateEnglish/` | A2–B2 learners |
| Advanced English for Teachers | `AdvancedEnglish_for_Teachers/` | B2–C1 practising teachers |
| Classroom Lessons | `TeachingLessons/` | Young learners & teacher training |
| Possessive Pronouns & Family | `FamilyLessonPossessivePronouns/` | Intermediate ESL grammar |

Each collection folder has its own `index.html` catalogue, so
`https://dpdewey.github.io/LingMaterials/IntermediateEnglish/` is a
usable link on its own — handy for sending a single collection to a
cooperating teacher without the rest of the site.

## Live URLs

- Public home: <https://dpdewey.github.io/LingMaterials/>
- Teaching materials: `<base>/materials.html`
- Faculty admin: `<base>/FacultyMentoring/admin.html`
- Student admin: `<base>/MentoredStudent/admin.html`

## Structure

```
/
├── index.html                  ← Mentoring Archive home
├── materials.html              ← Teaching Materials hub
├── styles.css                  ← BYU brand stylesheet (mentoring)
├── styles-materials.css        ← additive layer for materials catalogues
├── FacultyMentoring/           ← faculty archive + admin
├── MentoredStudent/            ← student archive + admin
├── IntermediateEnglish/        ← teaching materials + catalogue
├── AdvancedEnglish_for_Teachers/
├── TeachingLessons/            ← includes Memory/ demo pages
├── FamilyLessonPossessivePronouns/
├── assets/logos/               ← official BYU Linguistics sub-brand logos
├── embed/                      ← chrome-free versions for Brightspot embedding
├── api/, netlify/              ← serverless function for AI summary
└── tools/                      ← page generators (see below)
```

## Regenerating the catalogue pages

The teaching-materials catalogues are generated from a single data
model rather than hand-edited. To add or retitle a material:

1. Open `tools/build_materials.py` and edit the `PROJECTS` list.
2. Run it from the repository root:

   ```bash
   python3 tools/build_materials.py
   ```

This rewrites `materials.html` and the four collection `index.html`
files. It touches nothing else — no mentoring file, and none of the
teaching material files themselves.

## Design notes

The mentoring pages and the catalogue pages follow the BYU brand
standards described in `CHANGES.md` (IBM Plex Sans; navy `#002E5D`,
white, royal `#0047BA`; official sub-brand logos). The individual
teaching materials use their own separate visual design, which is
intentional — they were built for projectors and young learners. The
catalogue pages are the seam between the two.

## Privacy notes

Each mentoring entry can be marked private at the field level or at the
entry level. Private entries do not appear in the public archive but are
visible in the admin view. Anonymous students appear as "Anonymous
student" publicly; their real names are visible to admins.

The admin password is a client-side soft barrier — fine for casual
privacy, NOT real security. For sensitive personal data you would need
NetID/SSO.
