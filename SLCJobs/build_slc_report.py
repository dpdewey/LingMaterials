#!/usr/bin/env python3
"""
build_slc_report.py — turn SLCJobs.csv into the full report set.

Reads the spreadsheet slcjobs.py produced and writes, into a `report/`
folder beside it:

  • three word clouds   (job titles, skills & tools asked for, employers)  [PNG]
  • four charts         (postings by track, pay by track, employer types,
                         physical fit)                                      [PNG]
  • an interactive page (slc_jobs_report.html): numbers, takeaways, charts,
                         track cards, and a searchable table of every
                         posting with links                                 [HTML]
  • track cards         (track_cards.html/.pdf): one card per career track  [HTML/PDF]
  • a one-page handout  (apply_this_week.html/.pdf): the best current
                         postings, with links and resume tips               [HTML/PDF]
  • a Word report       (SLC_jobs_report.docx)                              [DOCX]

WHAT YOU NEED
-------------
Required (pip):  matplotlib
Optional:        wordcloud    -> the three clouds
                 python-docx  -> the Word report
                 playwright   -> PDF versions (then: python -m playwright install chromium)
Anything whose tool is missing is SKIPPED with a note, never a crash.

USE
---
    python build_slc_report.py                    # reads ./SLCJobs.csv
    python build_slc_report.py path/to/SLCJobs.csv
    python build_slc_report.py --collected "November 2026"

The window app's "Build report" button calls this same file.
"""
from __future__ import annotations

import argparse
import base64
import csv
import html
import io
import json
import os
import re
import statistics
import sys
from collections import Counter, defaultdict
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import slcjobs as J   # track descriptions, physical ratings, hand-search list

# ===========================================================================
# EDITABLE BLOCK — wording that appears in the report
# ===========================================================================
REPORT_TITLE = "Step-Up Jobs in the Salt Lake Area"
PREPARED_FOR = ("An experienced, highly reliable custodian moving into seated, "
                "bench and desk work that uses crafts and tech")

RESUME_TIPS = [
    "Lead with reliability as a number: “99%+ attendance across X years, zero unexcused absences.”",
    "Translate custodial work into operations terms: supply ordering and inventory, SDS/OSHA chemical safety, key and alarm control, finishing routes on deadline without supervision.",
    "For craft and bench roles, attach a simple portfolio: 5–10 well-lit photos of finished pieces.",
    "Read each ad's Physical Requirements section. “Lift 50 lbs” is often copied boilerplate on desk jobs; ask HR, and ask large employers for an elevator-accessible workstation.",
    "Apply first to hospitals, universities, school districts and government: steady benefits, internal promotion, and often tuition help for design, CAD or IT classes.",
]

# Words left out of the clouds (in addition to common English words)
CLOUD_EXCLUDE = {
    "salt", "lake", "city", "utah", "ut", "job", "jobs", "position", "work",
    "team", "company", "role", "will", "including", "ability", "must", "may",
    "experience", "required", "preferred", "years", "year", "hour", "hours",
    "per", "pay", "full", "time", "part", "new", "opportunity", "candidate",
    "employees", "employee", "benefits", "apply", "equal", "employer", "us",
    "inc", "llc", "corp", "corporation", "i", "ii", "iii", "sr", "jr", "m", "f",
    "w", "d", "x", "day", "days", "week", "shift",
}
_STOP = set("""a an and are as at be been but by can for from has have if in into is it its
of on or our so such that the their them then there these they this to was we were
what when where which while who with you your all any also each more most other
some than up out about over under not no""".split())

NAVY, ROYAL, INK, GRAY = "#1F4E79", "#2E75B6", "#1b1f24", "#6b6e72"
PHYS_COLORS = {"good": "#2E7D32", "caution": "#D49A00", "avoid": "#9E9E9E"}

# ===========================================================================
# DATA
# ===========================================================================

def load(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        try:
            r["_hr"] = float(r.get("pay_hourly_est") or "")
        except ValueError:
            r["_hr"] = None
        try:
            r["_score"] = int(float(r.get("score") or 0))
        except ValueError:
            r["_score"] = 0
        r["_phys"] = J.PHYSICAL.get(r.get("field", ""), "good")
    return rows


def med(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else None


def money(x):
    return f"${x:,.2f}/hr" if x else "—"


def analyze(rows: list[dict]) -> dict:
    by_track = defaultdict(list)
    for r in rows:
        by_track[r["field"]].append(r)
    tracks = []
    for name, js in by_track.items():
        why, entry = J.TRACK_INFO.get(name, ("", ""))
        pays = [r["_hr"] for r in js if r["_hr"]]
        tracks.append({
            "name": name, "n": len(js), "median": med(pays), "n_pay": len(pays),
            "phys": J.PHYSICAL.get(name, "good"),
            "group": ("Stretch" if name in J.STRETCH_TRACKS else
                      "Creative & maker" if name in J.CREATIVE_NAMES else "Operations"),
            "why": why, "entry": entry,
            "day": sum(1 for r in js if "Day shift" in r.get("shift", "") or "Mon" in r.get("shift", "")),
            "employers": Counter(r["organization"] for r in js if r.get("organization")).most_common(5),
            "examples": sorted(js, key=lambda r: (-r["_score"], r["job_title"]))[:4],
        })
    phys_order = {"good": 0, "caution": 1, "avoid": 2}
    tracks.sort(key=lambda t: (phys_order[t["phys"]], -t["n"]))
    all_pay = [r["_hr"] for r in rows if r["_hr"]]
    good = [r for r in rows if r.get("physical_fit", "").startswith("Good fit") and not r.get("physical_flags")]
    top = sorted(good or rows, key=lambda r: (-r["_score"], r["job_title"]))[:18]
    return {
        "n": len(rows), "tracks": tracks, "median": med(all_pay), "n_pay": len(all_pay),
        "n_good": len(good),
        "n_check": sum(1 for r in rows if r.get("physical_flags") or r.get("physical_fit", "").startswith("Caution")),
        "employer_types": Counter(r.get("employer_type") or "Private employer" for r in rows),
        "employers": Counter(r["organization"] for r in rows if r.get("organization")),
        "areas": Counter(r.get("area") or "check location" for r in rows),
        "no_degree": sum(1 for r in rows if r.get("min_degree") in ("", "High school", "Certificate")),
        "top": top,
    }


def takeaways(a: dict) -> list[str]:
    out = []
    if not a["n"]:
        return ["No postings were kept in this run. Check the API keys and run the collector again."]
    biggest = max(a["tracks"], key=lambda t: t["n"])
    out.append(f"{a['n']} current postings in the Salt Lake region fit this profile; "
               f"{a['n_good']} are seated or bench work with no physical demands listed in the ad.")
    out.append(f"The largest track is {biggest['name']} ({biggest['n']} postings).")
    paid = [t for t in a["tracks"] if t["median"] and t["n_pay"] >= 3]
    if paid:
        hi = max(paid, key=lambda t: t["median"])
        out.append(f"Where pay is listed, the median is {money(a['median'])}; "
                   f"{hi['name']} pays best (median {money(hi['median'])}, {hi['n_pay']} postings with pay).")
    out.append(f"{a['no_degree']} of {a['n']} postings do not mention a college degree.")
    stable = sum(v for k, v in a["employer_types"].items()
                 if k in ("Hospital / health system", "University / school", "Government",
                          "Library / museum / arts"))
    if stable:
        out.append(f"{stable} postings are with hospitals, schools, universities, libraries or "
                   f"government, where benefits and tuition help are most common.")
    if a["n_check"]:
        out.append(f"{a['n_check']} postings need a question to HR about lifting, stairs or standing "
                   f"before applying (see the physical-fit column).")
    return out

# ===========================================================================
# CHARTS & CLOUDS
# ===========================================================================

def _plt():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "axes.edgecolor": "#c9ccd1", "axes.labelcolor": INK,
                         "xtick.color": GRAY, "ytick.color": INK})
    return plt


def chart_hbar(path, labels, values, colors, title, xlabel, fmt="{:.0f}", note=""):
    plt = _plt()
    h = max(2.4, 0.38 * len(labels) + 1.1)
    fig, ax = plt.subplots(figsize=(8, h), dpi=150)
    y = range(len(labels))[::-1]
    ax.barh(list(y), values, color=colors, height=0.62)
    ax.set_yticks(list(y)); ax.set_yticklabels(labels)
    ax.set_xlabel(xlabel)
    fig.suptitle(title, x=0.01, ha="left", fontsize=12, color=INK)
    if note:
        fig.text(0.01, 0.005, note, ha="left", va="bottom", fontsize=8.5, color=GRAY)
    for yi, v in zip(y, values):
        ax.text(v, yi, " " + fmt.format(v), va="center", fontsize=9, color=INK)
    ax.margins(x=0.12)
    fig.tight_layout(rect=(0, 0.03 if note else 0, 1, 0.97)); fig.savefig(path); plt.close(fig)


def make_charts(a: dict, out: str) -> dict:
    files = {}
    tr = [t for t in a["tracks"] if t["n"]]
    if tr:
        p = os.path.join(out, "chart_postings_by_track.png")
        chart_hbar(p, [t["name"] for t in tr], [t["n"] for t in tr],
                   [PHYS_COLORS[t["phys"]] for t in tr],
                   "Postings by career track", "postings",
                   note="Green = good physical fit (seated/bench). Gold = caution role.")
        files["tracks"] = p
    paid = [t for t in tr if t["median"] and t["n_pay"] >= 2]
    if paid:
        paid.sort(key=lambda t: -t["median"])
        p = os.path.join(out, "chart_pay_by_track.png")
        chart_hbar(p, [f"{t['name']} (n={t['n_pay']})" for t in paid], [t["median"] for t in paid],
                   [PHYS_COLORS[t["phys"]] for t in paid],
                   "Median pay by track (estimated $/hour)", "$ per hour", "${:.2f}",
                   note="Only ads that list pay; n = number of those ads.")
        files["pay"] = p
    et = a["employer_types"].most_common()
    if et:
        p = os.path.join(out, "chart_employer_types.png")
        chart_hbar(p, [k for k, _ in et], [v for _, v in et], [NAVY] * len(et),
                   "Who is hiring", "postings")
        files["employers"] = p
    return files


def make_physical_chart(rows: list[dict], out: str) -> str | None:
    c = Counter()
    for r in rows:
        pf = r.get("physical_fit", "")
        c["Good fit, nothing listed" if pf.startswith("Good fit") and not r.get("physical_flags")
          else "Good fit, ad lists demands" if pf.startswith("Good fit")
          else "Caution role"] += 1
    if not c:
        return None
    order = ["Good fit, nothing listed", "Good fit, ad lists demands", "Caution role"]
    labels = [k for k in order if c[k]]
    p = os.path.join(out, "chart_physical_fit.png")
    chart_hbar(p, labels, [c[k] for k in labels],
               ["#2E7D32", "#7CB342", "#D49A00"][:len(labels)],
               "Physical fit of the postings", "postings")
    return p


def _words(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-z][a-z0-9+&'-]{1,}", text.lower())
            if w not in _STOP and w not in CLOUD_EXCLUDE and not w.isdigit()]


def make_clouds(rows: list[dict], out: str, notes: list[str]) -> dict:
    try:
        from wordcloud import WordCloud
    except ImportError:
        notes.append("Word clouds skipped: pip install wordcloud")
        return {}
    files = {}

    def cloud(name, freqs, color):
        if not freqs:
            return
        wc = WordCloud(width=1400, height=700, background_color="white", prefer_horizontal=0.95,
                       max_words=80, color_func=lambda *a, **k: color, collocations=False,
                       margin=6).generate_from_frequencies(dict(freqs))
        p = os.path.join(out, f"cloud_{name}.png")
        wc.to_file(p)
        files[name] = p

    titles = Counter()
    for r in rows:
        t = re.sub(r"\(.*?\)|[-–|,/].*$", "", r["job_title"]).strip()
        titles.update(w for w in _words(t))
    cloud("titles", titles.most_common(80), NAVY)

    skills = Counter()
    for r in rows:
        body = r.get("summary", "")
        for term, _, rx in J._SKILL:
            if rx.search(body):
                skills[term] += 1
    cloud("skills", skills.most_common(60), "#2E7D32")

    emp = Counter(r["organization"] for r in rows if r.get("organization"))
    cloud("employers", emp.most_common(60), ROYAL)
    return files

# ===========================================================================
# HTML
# ===========================================================================

def _b64(path: str | None) -> str:
    if not path or not os.path.exists(path):
        return ""
    return "data:image/png;base64," + base64.b64encode(open(path, "rb").read()).decode()


CSS = """
:root{--ink:#1b1f24;--muted:#5d636b;--line:#dde1e6;--bg:#ffffff;--soft:#f4f6f9;
--navy:#1F4E79;--royal:#2E75B6;--good:#2E7D32;--caution:#B8860B;--avoid:#8a8f96;}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--ink:#e8eaed;--muted:#a6adb5;
--line:#353b43;--bg:#16191d;--soft:#1f2329;--navy:#8fb8e3;--royal:#7fb0e6;}}
*{box-sizing:border-box} body{margin:0;background:var(--bg);color:var(--ink);
font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}
main{max-width:1100px;margin:0 auto;padding:28px 16px 60px}
h1{font-size:28px;margin:0 0 4px;color:var(--navy)} h2{font-size:20px;margin:36px 0 12px;color:var(--navy)}
.sub{color:var(--muted);margin:0 0 20px}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:18px 0}
.stat{background:var(--soft);border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.stat b{display:block;font-size:24px;color:var(--navy)} .stat span{color:var(--muted);font-size:13px}
ul.take li{margin:6px 0}
img.chart{display:block;width:100%;max-width:820px;height:auto;border:1px solid var(--line);border-radius:8px;background:#fff;margin:8px 0}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:14px}
.card{border:1px solid var(--line);border-radius:12px;padding:14px 16px;background:var(--bg);break-inside:avoid}
.card h3{margin:0 0 4px;font-size:16px} .pill{display:inline-block;font-size:12px;padding:1px 8px;border-radius:99px;
color:#fff;margin-right:6px} .good{background:var(--good)} .caution{background:var(--caution)} .avoid{background:var(--avoid)}
.card p{margin:6px 0;font-size:14px} .card .meta{color:var(--muted);font-size:13px}
.card ol{padding-left:18px;margin:6px 0;font-size:13.5px}
a{color:var(--royal)}
.filters{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0}
.filters input,.filters select{font:inherit;padding:7px 9px;border:1px solid var(--line);border-radius:8px;
background:var(--bg);color:var(--ink);min-width:0;flex:1 1 180px}
.tablewrap{overflow-x:auto;border:1px solid var(--line);border-radius:10px}
table{border-collapse:collapse;width:100%;font-size:13.5px} th,td{padding:7px 9px;border-bottom:1px solid var(--line);
text-align:left;vertical-align:top} th{background:var(--soft);position:sticky;top:0}
td.t a{font-weight:600} .count{color:var(--muted);font-size:13px}
@media print{.filters,.noprint{display:none} body{font-size:12px}}
"""


def esc(s) -> str:
    return html.escape(str(s or ""))


def card_html(t: dict) -> str:
    emps = ", ".join(f"{esc(o)} ({n})" for o, n in t["employers"][:4]) or "—"
    ex = "".join(
        f'<li><a href="{esc(r["url"])}" target="_blank" rel="noopener">{esc(r["job_title"])}</a>'
        f' — {esc(r["organization"])}{" · " + esc(r["salary"]) if r.get("salary") else ""}</li>'
        if r.get("url") else f'<li>{esc(r["job_title"])} — {esc(r["organization"])}</li>'
        for r in t["examples"])
    return f"""<div class="card"><h3>{esc(t['name'])}</h3>
<span class="pill {t['phys']}">{t['phys']} physical fit</span><span class="meta">{esc(t['group'])}</span>
<p>{esc(t['why'])}</p><p><b>How to qualify:</b> {esc(t['entry'])}</p>
<p class="meta">{t['n']} postings · median {money(t['median'])} · {t['day']} day/Mon–Fri · top employers: {emps}</p>
<ol>{ex}</ol></div>"""


def build_page(rows, a, charts, clouds, phys_chart, collected, out) -> str:
    data = [{k: r.get(k, "") for k in ("field", "job_title", "organization", "location",
                                       "salary", "pay_hourly_est", "physical_fit",
                                       "physical_flags", "shift", "employer_type", "min_degree",
                                       "url", "source", "date_posted")} | {"score": r["_score"]}
            for r in sorted(rows, key=lambda r: (-r["_score"], r["job_title"]))]
    tracks = sorted({r["field"] for r in rows})
    etypes = sorted({r.get("employer_type") or "" for r in rows} - {""})
    imgs = "".join(f'<img class="chart" src="{_b64(p)}" alt="">' for p in
                   [charts.get("tracks"), phys_chart, charts.get("pay"), charts.get("employers")] if p)
    cimgs = "".join(f'<h3>{label}</h3><img class="chart" src="{_b64(clouds[k])}" alt="">'
                    for k, label in (("titles", "Job titles"), ("skills", "Skills and tools the ads ask for"),
                                     ("employers", "Employers")) if k in clouds)
    manual = "".join(f'<li><a href="{esc(u)}" target="_blank" rel="noopener">{esc(n)}</a> — {esc(w)}</li>'
                     for n, u, w in J.MANUAL_SITES)
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>SLC Step-Up Jobs</title>
<style>{CSS}</style></head><body><main>
<h1>{esc(REPORT_TITLE)}</h1>
<p class="sub">{esc(PREPARED_FOR)}. Collected {esc(collected)}. Salt Lake, Davis, north Utah and Tooele counties.</p>
<div class="stats">
<div class="stat"><b>{a['n']}</b><span>postings that fit</span></div>
<div class="stat"><b>{a['n_good']}</b><span>seated / bench, nothing physical listed</span></div>
<div class="stat"><b>{money(a['median'])}</b><span>median pay ({a['n_pay']} ads list pay)</span></div>
<div class="stat"><b>{a['no_degree']}</b><span>don't mention a college degree</span></div>
<div class="stat"><b>{len([t for t in a['tracks'] if t['n']])}</b><span>career tracks with openings</span></div>
</div>
<h2>Takeaways</h2><ul class="take">{''.join(f'<li>{esc(t)}</li>' for t in takeaways(a))}</ul>
<h2>Where the openings are</h2>{imgs}
<h2>Career tracks</h2><div class="grid">{''.join(card_html(t) for t in a['tracks'] if t['n'])}</div>
<h2>Every posting</h2>
<div class="filters noprint">
<input id="q" type="search" placeholder="Search titles, employers, places…">
<select id="ft"><option value="">All tracks</option>{''.join(f'<option>{esc(t)}</option>' for t in tracks)}</select>
<select id="fp"><option value="">Any physical fit</option><option value="clean">Good fit, nothing listed</option>
<option value="Good fit">Good fit (any)</option><option value="Caution">Caution</option></select>
<select id="fe"><option value="">All employer types</option>{''.join(f'<option>{esc(t)}</option>' for t in etypes)}</select>
<select id="fpay"><option value="">Pay listed or not</option><option value="1">Pay listed</option></select>
</div><p class="count" id="count"></p>
<div class="tablewrap"><table><thead><tr><th>Job</th><th>Employer</th><th>Where</th><th>Pay</th>
<th>Track</th><th>Physical</th><th>Posted</th></tr></thead><tbody id="rows"></tbody></table></div>
<h2>Word clouds</h2>{cimgs or '<p class="sub">Install wordcloud to add these.</p>'}
<h2>Resume tips</h2><ul>{''.join(f'<li>{esc(t)}</li>' for t in RESUME_TIPS)}</ul>
<h2>Search these by hand</h2><ul>{manual}</ul>
</main>
<script>
const DATA={json.dumps(data)};
const $=id=>document.getElementById(id);
function esc(s){{return String(s??"").replace(/[&<>"]/g,c=>({{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}})[c]);}}
function draw(){{
 const q=$("q").value.toLowerCase(),ft=$("ft").value,fp=$("fp").value,fe=$("fe").value,fpay=$("fpay").value;
 const out=DATA.filter(r=>(!q||(r.job_title+" "+r.organization+" "+r.location).toLowerCase().includes(q))
  &&(!ft||r.field===ft)&&(!fe||r.employer_type===fe)&&(!fpay||r.salary)
  &&(!fp||(fp==="clean"?(r.physical_fit.startsWith("Good fit")&&!r.physical_flags):r.physical_fit.startsWith(fp))));
 $("count").textContent=out.length+" of "+DATA.length+" postings";
 $("rows").innerHTML=out.map(r=>`<tr><td class="t">${{r.url?`<a href="${{esc(r.url)}}" target="_blank" rel="noopener">${{esc(r.job_title)}}</a>`:esc(r.job_title)}}</td>
 <td>${{esc(r.organization)}}<br><span class="count">${{esc(r.employer_type)}}</span></td><td>${{esc(r.location)}}</td>
 <td>${{esc(r.salary)}}</td><td>${{esc(r.field)}}</td><td>${{esc(r.physical_fit)}}${{r.physical_flags?`<br><span class="count">${{esc(r.physical_flags)}}</span>`:""}}</td>
 <td>${{esc(r.date_posted)}}</td></tr>`).join("");
}}
["q","ft","fp","fe","fpay"].forEach(id=>$(id).addEventListener("input",draw));draw();
</script></body></html>"""
    p = os.path.join(out, "slc_jobs_report.html")
    open(p, "w", encoding="utf-8").write(page)
    return p


def build_cards(a, collected, out) -> str:
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Career Track Cards</title>
<style>{CSS} .grid{{grid-template-columns:repeat(auto-fit,minmax(320px,1fr))}}
@page{{size:letter;margin:0.5in}}</style></head><body><main>
<h1>Career Track Cards</h1><p class="sub">Salt Lake area · collected {esc(collected)} · {esc(PREPARED_FOR)}</p>
<div class="grid">{''.join(card_html(t) for t in a['tracks'] if t['n'])}</div></main></body></html>"""
    p = os.path.join(out, "track_cards.html")
    open(p, "w", encoding="utf-8").write(page)
    return p


def build_handout(a, collected, out) -> str:
    def link(r):
        if not r.get("url"):
            return ""
        return '<a href="%s">%s</a>' % (esc(r["url"]), esc(J.site_of(r["url"])[0] or "link"))
    rows = "".join(
        f"<tr><td><b>{esc(r['job_title'])}</b><br><span class='count'>{esc(r['field'])}</span></td>"
        f"<td>{esc(r['organization'])}<br><span class='count'>{esc(r['location'])}</span></td>"
        f"<td>{esc(r.get('salary')) or '—'}</td><td class='u'>{link(r)}</td></tr>"
        for r in a["top"][:14])
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Apply This Week</title>
<style>{CSS} main{{max-width:8in}} table{{font-size:12.5px}} td.u{{word-break:break-all}}
@page{{size:letter;margin:0.45in}}</style></head><body><main>
<h1>Apply This Week</h1>
<p class="sub">The best-matching Salt Lake–area openings for seated, bench and desk work · {esc(collected)}</p>
<div class="stats"><div class="stat"><b>{a['n']}</b><span>fitting postings</span></div>
<div class="stat"><b>{a['n_good']}</b><span>no physical demands listed</span></div>
<div class="stat"><b>{money(a['median'])}</b><span>median listed pay</span></div></div>
<div class="tablewrap"><table><thead><tr><th>Job</th><th>Employer</th><th>Pay</th><th>Link</th></tr></thead>
<tbody>{rows}</tbody></table></div>
<h2>Before you apply</h2><ul>{''.join(f'<li>{esc(t)}</li>' for t in RESUME_TIPS)}</ul>
</main></body></html>"""
    p = os.path.join(out, "apply_this_week.html")
    open(p, "w", encoding="utf-8").write(page)
    return p

# ===========================================================================
# WORD & PDF (optional)
# ===========================================================================

def _add_hyperlink(par, url, text):
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    r_id = par.part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
                              is_external=True)
    h = OxmlElement("w:hyperlink"); h.set(qn("r:id"), r_id)
    run = OxmlElement("w:r"); rpr = OxmlElement("w:rPr")
    c = OxmlElement("w:color"); c.set(qn("w:val"), "2E75B6"); rpr.append(c)
    u = OxmlElement("w:u"); u.set(qn("w:val"), "single"); rpr.append(u)
    run.append(rpr); t = OxmlElement("w:t"); t.text = text; run.append(t); h.append(run)
    par._p.append(h)


def build_docx(rows, a, charts, phys_chart, collected, out, notes) -> str | None:
    try:
        from docx import Document
        from docx.shared import Inches, Pt, RGBColor
    except ImportError:
        notes.append("Word report skipped: pip install python-docx")
        return None
    d = Document()
    st = d.styles["Normal"]; st.font.name = "Calibri"; st.font.size = Pt(11)
    d.add_heading(REPORT_TITLE, 0)
    p = d.add_paragraph(f"{PREPARED_FOR}. Collected {collected}. Salt Lake, Davis, north Utah and Tooele counties.")
    p.runs[0].font.color.rgb = RGBColor(0x5d, 0x63, 0x6b)
    d.add_heading("Takeaways", 1)
    for t in takeaways(a):
        d.add_paragraph(t, style="List Bullet")
    d.add_heading("Where the openings are", 1)
    for k in ("tracks", "pay", "employers"):
        if charts.get(k):
            d.add_picture(charts[k], width=Inches(6.3))
    if phys_chart:
        d.add_picture(phys_chart, width=Inches(6.3))
    d.add_heading("Career tracks", 1)
    for t in a["tracks"]:
        if not t["n"]:
            continue
        d.add_heading(t["name"], 2)
        d.add_paragraph(f"Physical fit: {t['phys']} · {t['group']} · {t['n']} postings · "
                        f"median {money(t['median'])}")
        d.add_paragraph(t["why"])
        d.add_paragraph(f"How to qualify: {t['entry']}")
        if t["employers"]:
            d.add_paragraph("Top employers: " + ", ".join(f"{o} ({n})" for o, n in t["employers"][:5]))
        for r in t["examples"]:
            par = d.add_paragraph(style="List Bullet")
            if r.get("url"):
                _add_hyperlink(par, r["url"], r["job_title"])
            else:
                par.add_run(r["job_title"])
            par.add_run(f" — {r['organization']}" + (f" · {r['salary']}" if r.get("salary") else ""))
    d.add_heading("Apply this week", 1)
    tbl = d.add_table(rows=1, cols=4); tbl.style = "Light Grid Accent 1"
    for i, h in enumerate(("Job", "Employer", "Pay", "Physical fit")):
        tbl.rows[0].cells[i].text = h
    for r in a["top"][:20]:
        c = tbl.add_row().cells
        if r.get("url"):
            _add_hyperlink(c[0].paragraphs[0], r["url"], r["job_title"])
        else:
            c[0].text = r["job_title"]
        c[1].text = r["organization"]; c[2].text = r.get("salary") or "—"
        c[3].text = (r.get("physical_fit") or "") + (f" ({r['physical_flags']})" if r.get("physical_flags") else "")
    d.add_heading("Resume tips", 1)
    for t in RESUME_TIPS:
        d.add_paragraph(t, style="List Bullet")
    d.add_heading("Search these by hand", 1)
    for n, u, w in J.MANUAL_SITES:
        par = d.add_paragraph(style="List Bullet")
        _add_hyperlink(par, u, n); par.add_run(f" — {w}")
    p = os.path.join(out, "SLC_jobs_report.docx")
    d.save(p)
    return p


def build_pdfs(paths: list[str], notes: list[str]) -> list[str]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        notes.append("PDFs skipped: pip install playwright, then python -m playwright install chromium")
        return []
    done = []
    try:
        with sync_playwright() as pw:
            br = pw.chromium.launch()
            pg = br.new_page()
            for h in paths:
                pg.goto("file://" + os.path.abspath(h))
                pg.emulate_media(media="print")
                pdf = os.path.splitext(h)[0] + ".pdf"
                pg.pdf(path=pdf, format="Letter", print_background=True,
                       margin={"top": "0.45in", "bottom": "0.45in", "left": "0.45in", "right": "0.45in"})
                done.append(pdf)
            br.close()
    except Exception as e:
        notes.append(f"PDFs skipped ({type(e).__name__}): run  python -m playwright install chromium")
    return done

# ===========================================================================
# MAIN
# ===========================================================================

def build(csv_path: str, collected: str = "", log=print) -> tuple[str, list[str], list[str]]:
    """Build everything. Returns (report folder, files written, notes)."""
    rows = load(csv_path)
    collected = collected or date.today().strftime("%B %d, %Y")
    out = os.path.join(os.path.dirname(os.path.abspath(csv_path)), "report")
    os.makedirs(out, exist_ok=True)
    notes: list[str] = []
    files: list[str] = []
    a = analyze(rows)
    log(f"Read {len(rows)} postings from {os.path.basename(csv_path)}")
    try:
        charts = make_charts(a, out); files += charts.values()
        phys = make_physical_chart(rows, out); files += [phys] if phys else []
    except ImportError:
        notes.append("Charts skipped: pip install matplotlib")
        charts, phys = {}, None
    clouds = make_clouds(rows, out, notes); files += clouds.values()
    page = build_page(rows, a, charts, clouds, phys, collected, out); files.append(page)
    cards = build_cards(a, collected, out); files.append(cards)
    hand = build_handout(a, collected, out); files.append(hand)
    docx = build_docx(rows, a, charts, phys, collected, out, notes)
    if docx:
        files.append(docx)
    files += build_pdfs([cards, hand], notes)
    for f in files:
        log("  wrote " + os.path.relpath(f, os.path.dirname(out)))
    for n in notes:
        log("  note: " + n)
    return out, files, notes


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Build the SLC Step-Up Jobs report")
    ap.add_argument("csv", nargs="?", default=os.path.join(os.getcwd(), J.DEFAULT_CSV))
    ap.add_argument("--collected", default="", help='date label, e.g. "November 2026"')
    a = ap.parse_args(argv)
    if not os.path.exists(a.csv):
        print(f"Can't find {a.csv}. Run  python slcjobs.py --all  first.", file=sys.stderr)
        return 1
    out, files, notes = build(a.csv, a.collected)
    print(f"\nReport folder: {out}  ({len(files)} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
