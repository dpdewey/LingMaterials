# SLC Step-Up Jobs

Three files that work together, like the LingJobs set:

| File | Job |
|---|---|
| `slcjobs_gui.py` | The window: collect jobs, add downloaded files, build the report, manage keys. Double-click `run_slcjobs_mac.command` (Mac) or `run_slcjobs_windows.bat` |
| `slcjobs.py` | The collector (also runs from the terminal) |
| `build_slc_report.py` | Turns `SLCJobs.csv` into the full report |

A Salt Lake–area job scanner for one person: an experienced, highly reliable custodian who wants out of hands-on cleaning, enjoys crafts and tech, and **cannot do heavy lifting or stair climbing**. Built on the joblens (LingJobs) architecture.

## What it keeps

Only postings in the region (Salt Lake, Davis, north Utah and Tooele counties; edit `REGIONS_ON`) whose **title** matches a track below. With `PHYSICAL_LIMITS = True` (the default), each track has a physical rating:

| Rating | Tracks | Rule |
|---|---|---|
| **Good** (seated, bench, single floor) | Dispatch & Scheduling · Security Desk & Badging · Purchasing & Inventory Data (desk) · Pre-Press & File Prep · Bench Engraving & Small-Format Vinyl · Embroidery & Digitizing · Dental Lab Technician · Optical Lab / Optician Assistant · Electronics Assembly & Device Repair · Library Technical Services · Photo Digitization & Archival Scanning · Makerspace / FabLab · 3D Printing Operator · CAD Drafting / UI Design (stretch) | Kept. If the ad lists lifting or stairs, it is still kept but marked "check physical section", because that section is often copied boilerplate |
| **Caution** | Facilities Coordination · Custodial / EVS Supervisor · Sterile Processing · Security Officer (check post) · E-commerce Photo · Custom Framing & Screen Print | Kept only if the ad lists **no** lifting over 25 lbs, stairs, ladders, long standing, walking between buildings, carts, or kneeling |
| **Avoid** | Inventory & Supply Chain · Shipping & Receiving · Property Management · Inspection · Safety/EHS · Maintenance · Press & Bindery · Sign & Large-Format · Visual Merchandising · Museum Preparator | Dropped, and their searches are skipped |

Titles such as patrol, installer, library page, shelver, runner, courier, warehouse and material handler are dropped under any track. Hands-on cleaning titles are dropped unless they are lead or supervisor roles; heavy labor and degree- or license-only jobs are always dropped.

Each posting gets `physical_fit` ("Good fit", "Good fit — check physical section", or "Caution — ask about walking, standing and lifting") and `physical_flags` (for example "lift 50 lbs, stairs/ladders").

## Running

**Window:** open `slcjobs_gui.py`. Tabs: Collect jobs · Add downloaded files · Build report · API keys · Instructions. With "Build the report when done" ticked, one press of **Start** produces everything below.

**Terminal:**
```
pip install -r requirements.txt
python slcjobs.py --selftest      # should end 32/32 as expected
python slcjobs.py --audit         # which sources work (writes nothing)
python slcjobs.py --all           # SLCJobs.csv, SLCJobs.xlsx, SLCJobs_excluded.csv
python slcjobs.py --all --merge-into SLCJobs.csv   # weekly re-runs
python slcjobs.py --import indeed.csv --merge-into SLCJobs.csv
python slcjobs.py --rescore SLCJobs.csv            # after changing settings
python build_slc_report.py SLCJobs.csv             # the full report
```

Keys: put `lingjobs_keys.json` or `gerrusjobs_keys.json` in this folder (find them with `mdfind -name "_keys.json"`), or fill in `slcjobs_keys.json`. Free keys: developer.adzuna.com and developer.usajobs.gov.

## Settings (top of `slcjobs.py`)

| Setting | Default | Meaning |
|---|---|---|
| `PHYSICAL_LIMITS` | True | Apply the ratings above. False = use every track |
| `LIFT_LIMIT_LBS` | 25 | Lifting above this is flagged |
| `INCLUDE_CREATIVE` | True | Creative, maker and bench tracks |
| `INCLUDE_STRETCH` | True | CAD / UI design (6–12 months of skills first) |
| `MIN_HOURLY` | 0 | Hide jobs paying less than this per hour (jobs without pay are kept) |
| `REGIONS_ON` | 4 areas | Counties to include |
| `PHYSICAL` | — | Change any track's rating to good / caution / avoid |

## Output

**Job list (same layout as LingJobs `jobs.csv` / `jobs.xlsx`):**

- `SLCJobs.csv`: one row per posting. Columns start with the joblens set (`field, job_title, organization, location, salary, min_degree, url, site, site_url, source, date_posted, employment_type, score`), then this profile's columns (`physical_fit, physical_flags, pay_hourly_est, shift, asks_for, employer_type, area, track_group, why_it_fits, certificate_hint, matched_terms, degree_context, summary`). `field` is the career track; `url` is the link to the ad. Salary is taken from the ad text when the source doesn't supply it.
- `SLCJobs.xlsx`: **All Postings**, then one tab per career track, then Sources and Search by hand. Clickable links, filters on every column.
- `SLCJobs_excluded.csv`: every posting left out, with the reason (outside the area, hands-on cleaning, physical demands, no matching track), so nothing disappears silently.

**Report (`report/` folder, from `build_slc_report.py`):**

| File | What it is |
|---|---|
| `slc_jobs_report.html` | Interactive page: headline numbers, takeaways, charts, track cards with example jobs, a searchable and filterable list of every posting with links, word clouds, resume tips, search-by-hand sites |
| `track_cards.html` / `.pdf` | One printable card per career track: why it fits, how to qualify, pay, top employers, example jobs |
| `apply_this_week.html` / `.pdf` | One-page handout of the best current postings for seated/bench work, with links and resume tips |
| `SLC_jobs_report.docx` | Word version of the report, with linked job titles |
| `chart_*.png` | Postings by track (colored by physical fit), pay by track, who is hiring, physical fit |
| `cloud_*.png` | Word clouds of job titles, skills and tools, and employers |

Word clouds need `wordcloud`, the Word file `python-docx`, and PDFs `playwright` (then `python -m playwright install chromium`). Anything missing is skipped with a note. The wording at the top of `build_slc_report.py` (title, resume tips, words left out of clouds) is meant to be edited.

## Browser search with Claude in Chrome

`SLCJobs_browser_search.md` tells Claude in Chrome how to search the sites this program can't collect by itself and write a CSV that the **2 · Add downloaded files** tab imports. Open the Claude side panel in Chrome, attach or paste the file, and say, for example, "Run the SLC Step-Up Jobs browser search." LinkedIn, Indeed, Glassdoor and similar sites are skipped unless you say "include Tier B", because their terms restrict automated access. Imported rows keep the site they came from (shown as "UN Careers (searched by hand)", for example), and the program applies its own rules to them like everything else.
