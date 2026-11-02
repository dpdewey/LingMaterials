#!/usr/bin/env python3
"""
slcjobs.py — SLC Step-Up Jobs: a Salt Lake–area job scanner for one profile
===========================================================================

Built on the joblens (LingJobs) architecture — polite fetching, sanctioned
channels only, word-boundary scoring with hard vetoes, smart import,
merge-dedup, per-employer cap — but aimed at a single kind of job seeker:

    Experienced custodian, extremely reliable, no degree assumed, who wants
    to move UP and OUT of manual cleaning into coordination, oversight,
    inventory, safety, security, scheduling, or property work.

It searches ONLY the Salt Lake region (Salt Lake County, plus Davis County
and north Utah County by default; edit REGION_TOWNS), keeps only postings
whose title matches one of the step-up CAREER TRACKS below, and drops:

  * hands-on cleaning jobs (custodian, janitor, housekeeper, EVS tech,
    porter ...) unless the title is a lead/supervisor/coordinator role
  * heavy manual labor (picker, loader, CDL driver, laborer ...)
  * roles out of reach without a degree or license (nurse, engineer ...)

Each kept posting is labeled with its track, employer type (hospital,
university/school, government, property management, facilities services),
an estimated hourly pay, the shift pattern, what it asks for (diploma,
degree, certificate), and a fit score.

QUICK START
-----------
    pip install requests beautifulsoup4 openpyxl
    python slcjobs.py --selftest       # offline check of the rules
    python slcjobs.py --audit          # which sources are alive?
    python slcjobs.py --all            # writes SLCJobs.csv + SLCJobs.xlsx
    python slcjobs.py --all --merge-into SLCJobs.csv
    python slcjobs.py --import indeed.csv --merge-into SLCJobs.csv
    python slcjobs.py --rescore SLCJobs.csv

KEYS
----
Adzuna and USAJobs keys are read from slcjobs_keys.json, or from
lingjobs_keys.json / gerrusjobs_keys.json / deruscan_keys.json if those are
in the same folder. Environment variables override files.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import os
import random
import re
import sqlite3
import sys
import time
import urllib.parse
import urllib.robotparser
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, fields
from datetime import datetime, timezone
from typing import Callable, Iterable, Iterator

import requests

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

VERSION = "1.0"
HERE = os.path.dirname(os.path.abspath(__file__))

# ============================================================================
# CONFIG
# ============================================================================

CONTACT_EMAIL = "ddewey@byu.edu"
PROJECT_URL = "https://dpdewey.github.io/"
USER_AGENT = (f"BYU-SLCStepUpJobs/{VERSION} (+{PROJECT_URL}; {CONTACT_EMAIL}) "
              "python-requests")

MIN_DELAY_SECONDS = 3.0
JITTER_SECONDS = 1.5
REQUEST_TIMEOUT = 25
MAX_REQUESTS_PER_HOST = 300
MAX_RETRIES = 3
CACHE_DB = os.path.join(HERE, "slcjobs_cache.sqlite")
CACHE_TTL_HOURS = 12

DEFAULT_CSV = "SLCJobs.csv"
DEFAULT_XLSX = "SLCJobs.xlsx"

MIN_SCORE = 5               # fit score needed to keep a posting
PER_EMPLOYER_CAP = 40       # local search: keep one hospital from flooding it
MIN_HOURLY = 0              # e.g. 18 to hide anything below $18/hr (0 = off)
INCLUDE_HANDS_ON_TRADES = False   # True = also keep maintenance-tech trainee roles
INCLUDE_CREATIVE = True           # creative & maker tracks (crafts + tech interest)
INCLUDE_STRETCH = True            # CAD / UI design: 6-12 months of skills first
PHYSICAL_LIMITS = True            # no heavy lifting, no stair climbing (see PHYSICAL below)
LIFT_LIMIT_LBS = 25               # an ad asking to lift more than this gets flagged

API_HOSTS = {"api.adzuna.com", "data.usajobs.gov"}

# ============================================================================
# REGION  (edit to widen or narrow)
# ============================================================================

SEARCH_CENTER = "Salt Lake City, Utah"
ADZUNA_DISTANCE_KM = 50          # ~31 miles from downtown SLC
USAJOBS_RADIUS_MILES = 35        # reaches Hill AFB, Tooele Army Depot, VA SLC

REGION_TOWNS = {
    "Salt Lake County": [
        "salt lake city", "slc", "west valley", "west valley city",
        "south salt lake", "murray", "sandy", "draper", "west jordan",
        "south jordan", "taylorsville", "midvale", "cottonwood heights",
        "holladay", "millcreek", "riverton", "herriman", "bluffdale",
        "magna", "kearns", "white city", "copperton", "emigration canyon",
        "brighton", "alta", "north salt lake", "salt lake county",
    ],
    "Davis County": [
        "bountiful", "woods cross", "centerville", "farmington", "kaysville",
        "layton", "clearfield", "syracuse", "clinton", "west bountiful",
        "fruit heights", "sunset", "hill afb", "hill air force base",
        "davis county",
    ],
    "North Utah County": ["lehi", "american fork", "pleasant grove",
                          "saratoga springs", "eagle mountain", "alpine",
                          "highland", "cedar hills", "lindon"],
    "Tooele County": ["tooele", "grantsville", "stansbury park",
                      "tooele army depot", "tooele county"],
}
REGIONS_ON = ["Salt Lake County", "Davis County", "North Utah County",
              "Tooele County"]

# ============================================================================
# POLITE FETCHER + TEXT HELPERS (from joblens)
# ============================================================================

class Blocked(Exception):
    """Raised when a host tells us to go away. We listen."""


class PoliteFetcher:
    def __init__(self, dry_run: bool = False, verbose: bool = True,
                 log: Callable[[str], None] | None = None):
        self.dry_run = dry_run
        self.verbose = verbose
        self.logf = log or (lambda m: print(m, file=sys.stderr))
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": USER_AGENT,
            "Accept-Language": "en-US,en;q=0.9,de;q=0.8,ru;q=0.7",
            "From": CONTACT_EMAIL,
        })
        self._last_hit: dict[str, float] = {}
        self._budget: dict[str, int] = {}
        self._robots: dict[str, urllib.robotparser.RobotFileParser | None] = {}
        self.db = sqlite3.connect(CACHE_DB)
        self.db.execute("CREATE TABLE IF NOT EXISTS cache (url TEXT PRIMARY KEY,"
                        " body TEXT, status INT, fetched_at REAL)")
        self.db.commit()

    def _log(self, msg: str) -> None:
        if self.verbose:
            self.logf(msg)

    # cache
    def _cache_get(self, k: str) -> str | None:
        row = self.db.execute("SELECT body, fetched_at FROM cache WHERE url=?",
                              (k,)).fetchone()
        if not row or time.time() - row[1] > CACHE_TTL_HOURS * 3600:
            return None
        return row[0]

    def _cache_put(self, k: str, body: str, status: int) -> None:
        self.db.execute("INSERT OR REPLACE INTO cache VALUES (?,?,?,?)",
                        (k, body, status, time.time()))
        self.db.commit()

    # robots
    def _robots_ok(self, url: str) -> bool:
        p = urllib.parse.urlsplit(url)
        if p.netloc in API_HOSTS:
            return True
        host = f"{p.scheme}://{p.netloc}"
        if host not in self._robots:
            rp = urllib.robotparser.RobotFileParser()
            try:
                r = self.session.get(f"{host}/robots.txt", timeout=REQUEST_TIMEOUT)
                if r.status_code == 200:
                    rp.parse(r.text.splitlines())
                else:
                    rp = None
            except requests.RequestException:
                rp = None
            self._robots[host] = rp
            self._sleep(p.netloc)
        rp = self._robots[host]
        return True if rp is None else rp.can_fetch(USER_AGENT, url)

    # pacing
    def _sleep(self, host: str) -> None:
        wait = MIN_DELAY_SECONDS - (time.time() - self._last_hit.get(host, 0.0))
        wait = max(wait, 0) + random.uniform(0, JITTER_SECONDS)
        time.sleep(wait)
        self._last_hit[host] = time.time()

    def _spend(self, host: str) -> None:
        self._budget[host] = self._budget.get(host, 0) + 1
        if self._budget[host] > MAX_REQUESTS_PER_HOST:
            raise Blocked(f"request budget of {MAX_REQUESTS_PER_HOST} used up for {host}")

    def _request(self, method: str, url: str, *, headers=None, data=None,
                 use_cache=True) -> str | None:
        ckey = url if method == "GET" else (
            url + "#POST#" + hashlib.sha1((data or "").encode()).hexdigest())
        if self.dry_run:
            self._log(f"  [dry-run] {method} {url}")
            return None
        if use_cache:
            c = self._cache_get(ckey)
            if c is not None:
                self._log(f"  [cache]   {url}")
                return c
        if not self._robots_ok(url):
            raise Blocked(f"robots.txt disallows {url}")
        host = urllib.parse.urlsplit(url).netloc
        delay = MIN_DELAY_SECONDS
        for attempt in range(1, MAX_RETRIES + 1):
            self._spend(host)
            self._sleep(host)
            try:
                r = self.session.request(method, url, headers=headers, data=data,
                                         timeout=REQUEST_TIMEOUT)
            except requests.RequestException as e:
                self._log(f"  [net err] {url}: {e}")
                if attempt == MAX_RETRIES:
                    return None
                time.sleep(delay); delay *= 2
                continue
            if r.status_code in (429, 503):
                ra = r.headers.get("Retry-After", "")
                wait = float(ra) if ra.isdigit() else delay
                self._log(f"  [throttled {r.status_code}] waiting {wait:.0f}s")
                time.sleep(wait); delay *= 2
                continue
            if r.status_code in (401, 403):
                raise Blocked(f"{url} -> {r.status_code} (access restricted)")
            if r.status_code != 200:
                self._log(f"  [http {r.status_code}] {url}")
                return None
            self._log(f"  [ok]      {url}")
            self._cache_put(ckey, r.text, r.status_code)
            return r.text
        return None

    def get(self, url: str, *, params: dict | None = None,
            headers: dict | None = None) -> str | None:
        if params:
            url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
        return self._request("GET", url, headers=headers)

    def get_json(self, url: str, **kw):
        body = self.get(url, **kw)
        if not body:
            return None
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            self._log(f"  [not json] {url}")
            return None

    def post_json(self, url: str, payload: dict, headers: dict | None = None):
        h = {"Content-Type": "application/json", "Accept": "application/json"}
        h.update(headers or {})
        body = self._request("POST", url, headers=h,
                             data=json.dumps(payload, sort_keys=True))
        try:
            return json.loads(body) if body else None
        except json.JSONDecodeError:
            return None


# ============================================================================
# TEXT HELPERS
# ============================================================================

def strip_html(s: str) -> str:
    if not s:
        return ""
    s = str(s)
    if "<" in s and BeautifulSoup is not None:
        s = BeautifulSoup(s, "html.parser").get_text(" ")
    else:
        s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def clip(s: str, n: int = 600) -> str:
    s = s or ""
    return s if len(s) <= n else s[:n].rsplit(" ", 1)[0] + " …"


def site_of(url: str) -> tuple[str, str]:
    try:
        p = urllib.parse.urlsplit(url)
        host = p.netloc.lower().removeprefix("www.")
        return host, f"{p.scheme}://{p.netloc}" if p.netloc else ""
    except ValueError:
        return "", ""


def fmt_salary(lo, hi, unit: str = "", cur: str = "") -> str:
    def f(x):
        try:
            x = float(x)
        except (TypeError, ValueError):
            return ""
        return f"{x:,.0f}" if x >= 1000 else f"{x:,.2f}"
    a, b = f(lo), f(hi)
    if not a and not b:
        return ""
    s = f"{cur}{a}" + (f" - {cur}{b}" if b and b != a else "")
    return s + (f" {unit}" if unit else "")


def _wre(term: str) -> re.Pattern:
    """Whole-word / phrase regex. Spaces in the term allow - or / too."""
    t = re.escape(term).replace(r"\ ", r"[\s\-/]+")
    return re.compile(rf"(?<![\w]){t}(?![\w])", re.I)


def _sre(stem: str) -> re.Pattern:
    """Word-start stem regex: 'translat' matches translator, translation."""
    return re.compile(rf"(?<![\w]){re.escape(stem)}\w*", re.I)


def _compile(terms):
    return [(t, w, _wre(t) if m == "w" else _sre(t)) for t, w, m in terms]




# ============================================================================
# CAREER TRACKS  — the profile lives here. Edit freely.
#
# Each track: (name, why it fits, entry note, [(title term, weight, mode)])
#   mode "w" = whole word/phrase, "s" = word-start stem
# A posting must match at least one track IN ITS TITLE to be kept.
# ============================================================================

TRACKS: list[tuple[str, str, str, list[tuple[str, int, str]]]] = [
    # ---------------- operations step-up ----------------
    ("Dispatch & Scheduling",
     "Seated desk work: calls, technician routing, appointment and work-order queues",
     "Diploma; 911 dispatch has a paid academy and strong benefits",
     [("dispatcher", 6, "w"), ("dispatch coordinator", 7, "w"),
      ("service coordinator", 6, "w"), ("service scheduler", 7, "w"),
      ("scheduling coordinator", 6, "w"), ("scheduling specialist", 6, "w"),
      ("scheduler", 5, "w"), ("patient scheduler", 7, "w"),
      ("appointment scheduler", 7, "w"), ("medical support assistant", 6, "w"),
      ("field service coordinator", 7, "w"), ("fleet coordinator", 5, "w"),
      ("public safety telecommunicator", 6, "w"),
      ("emergency communications", 6, "s"), ("911", 6, "w"),
      ("operations dispatcher", 7, "w"), ("transit dispatcher", 7, "w"),
      ("work order coordinator", 6, "w"), ("work control", 5, "w"),
      ("maintenance scheduler", 6, "w")]),
    ("Security Desk & Badging",
     "Front desk or monitor bank: IDs, badges, keycard access, cameras — no patrol",
     "Utah security licensing is handled through the employer",
     [("access control", 7, "w"), ("badging", 7, "s"), ("badge office", 7, "w"),
      ("security console", 7, "w"), ("console operator", 7, "w"),
      ("gsoc", 7, "w"), ("soc operator", 6, "w"), ("security operations center", 7, "w"),
      ("security dispatcher", 7, "w"), ("alarm monitoring", 7, "w"),
      ("alarm operator", 7, "w"), ("monitoring specialist", 6, "w"),
      ("central station operator", 7, "w"), ("lobby ambassador", 5, "w"),
      ("front desk security", 7, "w"), ("security receptionist", 7, "w"),
      ("visitor management", 6, "w"), ("security assistant", 6, "w"),
      ("id card", 5, "s"), ("credentialing", 4, "w")]),
    ("Purchasing & Inventory Data (desk)",
     "Orders and stock records at a computer, not in the stockroom",
     "Diploma + Excel; emphasize years of supply ordering",
     [("purchasing assistant", 7, "w"), ("purchasing coordinator", 7, "w"),
      ("purchasing clerk", 7, "w"), ("purchasing specialist", 6, "w"),
      ("procurement assistant", 7, "w"), ("procurement technician", 6, "w"),
      ("procurement specialist", 5, "w"), ("buyer assistant", 6, "w"),
      ("assistant buyer", 6, "w"), ("inventory data", 7, "s"),
      ("inventory analyst", 5, "w"), ("inventory planner", 5, "w"),
      ("supply chain analyst", 4, "w"), ("data entry clerk", 4, "w")]),
    ("Facilities Coordination",
     "Work orders, vendors and supplies — but often walks buildings and escorts vendors",
     "Ask whether the post is desk-based; IFMA FMA later",
     [("facilities coordinator", 7, "w"), ("facility coordinator", 7, "w"),
      ("facilities assistant", 6, "w"), ("facility assistant", 6, "w"),
      ("facilities administrator", 6, "w"), ("maintenance coordinator", 6, "w"),
      ("maintenance planner", 6, "w"), ("building operations coordinator", 6, "w"),
      ("workplace coordinator", 5, "w"), ("office services", 4, "s")]),
    ("Custodial / EVS Supervisor",
     "Leads cleaning teams; usually walks floors all shift",
     "Ask about walking and stairs; AHE CHEST/CHESP in hospitals",
     [("custodial supervisor", 7, "w"), ("custodial manager", 6, "w"),
      ("janitorial supervisor", 7, "w"), ("evs supervisor", 7, "w"),
      ("environmental services supervisor", 7, "w"),
      ("environmental services manager", 6, "w"),
      ("housekeeping supervisor", 7, "w"), ("housekeeping manager", 6, "w"),
      ("building services supervisor", 6, "w"), ("building services coordinator", 6, "w"),
      ("custodial coordinator", 6, "w"), ("custodial lead", 5, "w"),
      ("lead custodian", 4, "w"), ("evs lead", 5, "w")]),
    ("Sterile Processing",
     "Certified hospital role, but standing all shift and lifting instrument trays",
     "CRCST; ask about tray weights",
     [("sterile processing", 6, "s"), ("central sterile", 6, "s"),
      ("spd technician", 6, "w"), ("central service technician", 6, "w")]),
    ("Security Officer (check post)",
     "Some posts are a seated desk, many are patrol",
     "Ask for a fixed desk post",
     [("security officer", 5, "w"), ("security guard", 4, "w"),
      ("campus security", 4, "w"), ("security specialist", 4, "w"),
      ("public safety officer", 3, "w")]),
    ("Inventory & Supply Chain",
     "Stock counts and supply rooms — usually lifting boxes",
     "Avoid unless the ad says data entry or purchasing",
     [("inventory control", 6, "w"), ("inventory specialist", 6, "w"),
      ("inventory coordinator", 6, "w"), ("inventory clerk", 5, "w"),
      ("inventory technician", 5, "w"), ("supply chain technician", 6, "w"),
      ("supply technician", 5, "w"), ("materials management", 5, "s"),
      ("materials coordinator", 5, "w"), ("distribution technician", 5, "w"),
      ("stockroom", 5, "s"), ("storekeeper", 5, "w"), ("supply clerk", 5, "w")]),
    ("Shipping, Receiving & Logistics",
     "Dock work; clerks often move boxes and pallets",
     "Avoid with lifting limits",
     [("shipping and receiving", 6, "w"), ("shipping receiving", 6, "w"),
      ("receiving clerk", 6, "w"), ("shipping clerk", 6, "w"),
      ("logistics coordinator", 5, "w"), ("logistics clerk", 5, "w"),
      ("dock coordinator", 6, "w"), ("mailroom", 5, "s"), ("mail clerk", 5, "w")]),
    ("Property Management",
     "Walking properties and climbing stairs for showings and inspections",
     "Avoid with stair limits",
     [("leasing consultant", 6, "w"), ("leasing agent", 6, "w"),
      ("leasing specialist", 6, "w"), ("leasing professional", 6, "w"),
      ("assistant community manager", 6, "w"), ("assistant property manager", 6, "w"),
      ("make ready coordinator", 6, "w"), ("turnover coordinator", 6, "w"),
      ("property inspector", 6, "w")]),
    ("Inspection & Code Compliance",
     "Field inspections with stairs, bending and crawl spaces",
     "Avoid with stair limits",
     [("code enforcement", 6, "w"), ("code compliance", 6, "w"),
      ("housing inspector", 6, "w"), ("building inspector", 5, "w"),
      ("inspector trainee", 6, "w")]),
    ("Safety / EHS",
     "Walk-through audits across sites",
     "Avoid with stair limits",
     [("ehs technician", 6, "w"), ("ehs coordinator", 6, "w"),
      ("ehs assistant", 6, "w"), ("safety coordinator", 6, "w"),
      ("safety technician", 6, "w")]),
    ("Maintenance Trainee (hands-on)",
     "Repair work: ladders, lifting, crawling",
     "Off by default",
     [("maintenance technician", 4, "w"), ("maintenance tech", 4, "w"),
      ("maintenance apprentice", 6, "w"), ("maintenance trainee", 6, "w"),
      ("building maintenance", 3, "s")]),
]
HANDS_ON_TRACK = "Maintenance Trainee (hands-on)"

# --- Creative, maker and bench-precision tracks.
CREATIVE_TRACKS: list[tuple[str, str, str, list[tuple[str, int, str]]]] = [
    ("Pre-Press & File Prep",
     "Pure desk work: checking files, bleeds and color before printing",
     "InDesign, Illustrator, Acrobat Pro (target file prep, not press operator)",
     [("prepress", 7, "s"), ("pre-press", 7, "s"), ("production artist", 6, "w"),
      ("file prep", 7, "s"), ("file preparation", 7, "w"),
      ("preflight", 6, "s"), ("graphics coordinator", 5, "w"),
      ("print estimator", 4, "w"), ("customer service representative print", 5, "w")]),
    ("Bench Engraving & Small-Format Vinyl",
     "Seated laser engraving, awards, personalized gifts, small vinyl cutting",
     "LightBurn for lasers; Cricut/Silhouette practice for vinyl",
     [("engraver", 7, "w"), ("engraving", 7, "w"), ("laser engraver", 7, "w"),
      ("laser engraving", 7, "w"), ("trophy", 6, "s"), ("awards technician", 6, "w"),
      ("personalization", 6, "s"), ("personalized", 4, "s"),
      ("vinyl cutter", 6, "w"), ("small format", 6, "w"),
      ("decal", 5, "s"), ("sticker production", 6, "w"), ("jewelry engraving", 7, "w")]),
    ("Embroidery & Digitizing",
     "Light bench work running multi-needle machines, or seated stitch-file design",
     "Ink/Stitch (free, inside Inkscape); any sewing or textile work",
     [("embroidery", 7, "s"), ("embroiderer", 7, "w"), ("digitizer", 7, "w"),
      ("embroidery digitizer", 7, "w"), ("embroidery operator", 7, "w"),
      ("machine embroidery", 7, "w")]),
    ("Dental Lab Technician",
     "Seated 90%+ at a bench; pieces weigh ounces; CAD/CAM and 3D scanning",
     "Labs train reliable entry hires on model pouring, trimming and scanning",
     [("dental lab technician", 7, "w"), ("dental laboratory technician", 7, "w"),
      ("dental laboratory", 6, "w"), ("dental lab", 6, "w"),
      ("dental technician", 6, "w"), ("ceramist", 5, "w"),
      ("model room", 6, "w"), ("dental cad", 6, "s"), ("denture", 5, "s"),
      ("crown and bridge", 5, "w"), ("aligner", 4, "s")]),
    ("Optical Lab / Optician Assistant",
     "Bench lens edging and frame adjustments; flat clinic floor",
     "Apply directly to optometry offices and optical labs",
     [("optical lab technician", 7, "w"), ("optical technician", 7, "w"),
      ("lab optician", 7, "w"), ("lens technician", 7, "w"),
      ("edger", 6, "s"), ("optician assistant", 7, "w"), ("optical assistant", 7, "w"),
      ("optometric technician", 6, "w"), ("optometric assistant", 6, "w"),
      ("optometry technician", 6, "w"), ("frame stylist", 7, "w"),
      ("optician", 5, "w"), ("ophthalmic technician", 4, "w")]),
    ("Electronics Assembly & Device Repair",
     "Seated anti-static bench: small boards, soldering, phone and laptop repair",
     "A $20 soldering practice kit; iFixit repair guides",
     [("electronics assembler", 7, "w"), ("electronic assembler", 7, "w"),
      ("electronics assembly", 7, "w"), ("solder", 6, "s"), ("pcb assembl", 6, "s"),
      ("wire harness assembler", 5, "w"), ("cable assembler", 5, "w"),
      ("rework technician", 6, "w"), ("bench technician", 6, "w"),
      ("repair technician", 4, "w"), ("device repair", 7, "w"),
      ("phone repair", 7, "w"), ("cell phone repair", 7, "w"),
      ("computer repair", 6, "w"), ("electronics technician", 4, "w"),
      ("microelectronics", 4, "s")]),
    ("Library Technical Services",
     "Back-office mending, jacketing, labeling and catalog records — not shelving",
     "Bookbinding/paper-craft neatness; spreadsheet basics",
     [("library technician", 7, "w"), ("technical services", 6, "w"),
      ("technical services assistant", 7, "w"), ("cataloging", 6, "s"),
      ("catalog assistant", 7, "w"), ("acquisitions assistant", 6, "w"),
      ("processing assistant", 5, "w"), ("book repair", 7, "w"),
      ("book mending", 7, "w"), ("conservation technician", 6, "w"),
      ("bindery technician", 5, "w"), ("library assistant", 3, "w")]),
    ("Photo Digitization & Archival Scanning",
     "Seated at scanners, digitizing photos and documents; light editing and tagging",
     "File-naming discipline; Lightroom, Photoshop or GIMP dust removal",
     [("digitization", 7, "s"), ("digitizing technician", 7, "w"),
      ("scanning technician", 7, "w"), ("scanning specialist", 7, "w"),
      ("scanner operator", 7, "w"), ("document imaging", 7, "w"),
      ("imaging technician", 6, "w"), ("imaging specialist", 6, "w"),
      ("digital imaging", 6, "w"), ("archives technician", 6, "w"),
      ("archival technician", 6, "w"), ("records digitization", 7, "w"),
      ("metadata technician", 6, "w"), ("metadata specialist", 5, "w"),
      ("photo restoration", 6, "w"), ("records technician", 4, "w")]),
    ("Makerspace / FabLab Technician",
     "Desktop 3D printers, vinyl cutters, sewing machines; safety and inventory",
     "Check it is a single accessible floor without a heavy wood/metal shop",
     [("makerspace", 7, "s"), ("maker space", 7, "w"), ("fablab", 7, "s"),
      ("fab lab", 7, "w"), ("creative lab", 6, "w"), ("innovation lab", 5, "w"),
      ("digital fabrication", 6, "w"), ("studio technician", 4, "w")]),
    ("3D Printing Operator",
     "Queues and finishes desktop prints at a bench",
     "A small portfolio of prints; Tinkercad or Fusion 360",
     [("3d print", 7, "s"), ("additive manufacturing technician", 7, "w"),
      ("additive technician", 7, "w"), ("prototype technician", 6, "w"),
      ("model maker", 5, "w")]),
    ("CAD Drafting / UI Design (stretch)",
     "Desk-and-tech path: drafting floor plans or parts, or laying out web screens",
     "6-12 months: AutoCAD/Revit certificate, or Figma + HTML/CSS portfolio",
     [("cad drafter", 6, "w"), ("drafter", 5, "w"), ("drafting technician", 6, "w"),
      ("cad technician", 6, "w"), ("cad operator", 6, "w"), ("cad designer", 4, "w"),
      ("autocad", 4, "w"), ("revit technician", 5, "w"),
      ("junior ui", 4, "s"), ("ui designer", 3, "w"), ("web designer", 3, "w"),
      ("graphic design assistant", 4, "w")]),
    ("E-commerce Photo & Listing",
     "Mostly standing in a photo studio and moving products",
     "Ask how heavy the products are",
     [("product photographer", 7, "w"), ("ecommerce photographer", 7, "w"),
      ("e-commerce photographer", 7, "w"), ("listing specialist", 7, "w"),
      ("listings specialist", 7, "w"), ("ecommerce specialist", 6, "w"),
      ("e-commerce specialist", 6, "w"), ("ecommerce coordinator", 6, "w"),
      ("e-commerce coordinator", 6, "w"), ("catalog specialist", 5, "w"),
      ("photo editor", 5, "w")]),
    ("Custom Framing & Screen Print",
     "Standing at counters and presses; large frames can be heavy",
     "Ask about frame sizes and press work",
     [("custom framer", 7, "w"), ("custom framing", 7, "w"),
      ("picture framing", 7, "w"), ("frame shop", 6, "w"),
      ("screen printer", 6, "w"), ("screen printing", 6, "w"),
      ("heat press", 5, "w"), ("promotional products", 5, "w")]),
    ("Press & Bindery Operation",
     "Press operators lift 40-50 lb cases of paper",
     "Avoid with lifting limits; target pre-press instead",
     [("digital press", 6, "w"), ("press operator", 5, "w"),
      ("print operator", 6, "w"), ("bindery", 5, "s"), ("copy center", 5, "w"),
      ("print and mail", 5, "w"), ("reprographics", 5, "s")]),
    ("Sign & Large-Format Print",
     "Ladders and heavy vinyl rolls",
     "Avoid with lifting/stair limits; small-format vinyl is under Bench Engraving",
     [("sign production", 6, "w"), ("sign maker", 6, "w"), ("sign fabricat", 6, "s"),
      ("wide format", 6, "w"), ("large format", 6, "w"),
      ("graphics production", 6, "w"), ("print finisher", 5, "w")]),
    ("Visual Merchandising & Display",
     "Ladders, mannequins and heavy fixtures",
     "Avoid with lifting/stair limits",
     [("visual merchandiser", 7, "w"), ("visual merchandising", 7, "w"),
      ("display coordinator", 6, "w"), ("window display", 6, "w")]),
    ("Museum & Gallery Preparator",
     "Ladders, lighting and heavy framed art",
     "Avoid with lifting/stair limits; collections data work is under Digitization",
     [("preparator", 7, "w"), ("art handler", 7, "w"),
      ("exhibit technician", 7, "w"), ("exhibits technician", 7, "w"),
      ("collections assistant", 5, "w"), ("gallery assistant", 5, "w")]),
]
STRETCH_TRACKS = {"CAD Drafting / UI Design (stretch)"}
CREATIVE_NAMES = {t[0] for t in CREATIVE_TRACKS}
TRACKS = TRACKS + CREATIVE_TRACKS

# ---------------------------------------------------------------------------
# PHYSICAL FIT — this person: no heavy lifting, no stair climbing.
#   good    = seated / bench / single-floor work; kept
#   caution = kept only when the ad shows no lifting/stair/standing demands
#   avoid   = dropped
# Set PHYSICAL_LIMITS = False to ignore this and use every track.
# ---------------------------------------------------------------------------
PHYSICAL = {
    "Dispatch & Scheduling": "good",
    "Security Desk & Badging": "good",
    "Purchasing & Inventory Data (desk)": "good",
    "Pre-Press & File Prep": "good",
    "Bench Engraving & Small-Format Vinyl": "good",
    "Embroidery & Digitizing": "good",
    "Dental Lab Technician": "good",
    "Optical Lab / Optician Assistant": "good",
    "Electronics Assembly & Device Repair": "good",
    "Library Technical Services": "good",
    "Photo Digitization & Archival Scanning": "good",
    "Makerspace / FabLab Technician": "good",
    "3D Printing Operator": "good",
    "CAD Drafting / UI Design (stretch)": "good",
    "Facilities Coordination": "caution",
    "Custodial / EVS Supervisor": "caution",
    "Sterile Processing": "caution",
    "Security Officer (check post)": "caution",
    "E-commerce Photo & Listing": "caution",
    "Custom Framing & Screen Print": "caution",
    "Inventory & Supply Chain": "avoid",
    "Shipping, Receiving & Logistics": "avoid",
    "Property Management": "avoid",
    "Inspection & Code Compliance": "avoid",
    "Safety / EHS": "avoid",
    "Maintenance Trainee (hands-on)": "avoid",
    "Press & Bindery Operation": "avoid",
    "Sign & Large-Format Print": "avoid",
    "Visual Merchandising & Display": "avoid",
    "Museum & Gallery Preparator": "avoid",
}

# Titles that mean walking, climbing or carrying, whatever the track.
PHYSICAL_NEG_TITLES = [
    "patrol", "mobile patrol", "rover", "roving", "installer", "mover",
    "library page", "page", "shelver", "runner", "valet", "courier",
    "merchandiser", "stagehand", "rigger", "warehouse", "material handler",
    "materials handler", "transporter", "delivery",
]

# What the ad body says about physical demands.
_LIFT_RE = re.compile(
    r"lift(?:ing)?(?:,?\s*(?:and|/|or)\s*(?:carry|carrying|push|pull|move)\w*)*"
    r"[^.\d]{0,40}?(\d{2,3})\s*(?:\+\s*)?(?:lbs?|pounds|#)", re.I)
PHYS_FLAGS = [
    ("stairs/ladders", r"\bstairs?\b|\bstairwells?\b|\bclimb\w*|\bladders?\b|step stools?|scaffold\w*"),
    ("standing long periods", r"stand(?:ing)?\s+(?:for\s+)?(?:long|extended|prolonged)|"
                              r"on (?:your|their|one's) feet|stand(?:ing)? (?:up to |for up to )?\d+\s*(?:hours|%)|"
                              r"standing (?:and|/) walking (?:for|throughout)"),
    ("walking/multi-floor", r"walk\w* (?:long distances|throughout|between buildings|the (?:property|campus|grounds))|"
                            r"multi-?stor(?:y|ey)|multiple floors|several floors"),
    ("carts/pallets", r"push(?:ing)?\s*(?:/|and|or)\s*pull\w*|pallet\w*|carts? (?:weighing|of up to)|heavy carts?"),
    ("bending/kneeling", r"\bstoop\w*|\bkneel\w*|\bcrawl\w*|\bcrouch\w*"),
]
PHYS_GOOD = re.compile(
    r"\bseated\b|\bsitting\b|\bsit for\b|sedentary|desk[- ]based|at a desk|\bworkbench\b|"
    r"bench work|bench-top|benchtop|light duty|light physical|\belevator\b|ada[- ]accessible|"
    r"wheelchair accessible|sit[/-]stand", re.I)

# Words in the body that show the job uses this person's strengths.
SKILL_TERMS = [
    ("work order", 1, "s"), ("cmms", 1, "w"), ("inventory", 1, "s"),
    ("scheduling", 1, "w"), ("schedule", 1, "w"), ("vendor", 1, "s"),
    ("contractor", 1, "s"), ("inspection", 1, "s"), ("osha", 1, "w"),
    ("sds", 1, "w"), ("safety data sheet", 1, "s"), ("key control", 1, "w"),
    ("access control", 1, "w"), ("dispatch", 1, "s"), ("customer service", 1, "w"),
    ("data entry", 1, "w"), ("excel", 1, "w"), ("ordering", 1, "w"),
    ("purchase order", 1, "s"), ("supplies", 1, "w"), ("training", 1, "w"),
    ("reliab", 1, "s"), ("attendance", 1, "w"), ("punctual", 1, "s"),
    ("custodial", 2, "s"), ("janitorial", 2, "s"), ("housekeeping", 2, "w"),
    ("environmental services", 2, "w"), ("facilities", 1, "w"),
    # creative / maker tools
    ("illustrator", 1, "w"), ("inkscape", 1, "w"), ("coreldraw", 1, "w"),
    ("lightburn", 1, "w"), ("cura", 1, "w"), ("prusaslicer", 1, "w"),
    ("fusion 360", 1, "w"), ("tinkercad", 1, "w"), ("canva", 1, "w"),
    ("figma", 1, "w"), ("photoshop", 1, "w"), ("lightroom", 1, "w"),
    ("indesign", 1, "w"), ("acrobat", 1, "w"), ("shopify", 1, "w"),
    ("cricut", 1, "w"), ("silhouette", 1, "w"), ("vinyl", 1, "s"),
    ("laser", 1, "s"), ("3d print", 1, "s"), ("sewing", 1, "s"),
    ("embroidery", 1, "s"), ("craft", 1, "s"), ("woodworking", 1, "w"),
    ("safety", 1, "w"), ("organized", 1, "s"),
    # desk-security strengths
    ("front desk", 1, "w"), ("visitor", 1, "s"), ("badge", 1, "s"),
    ("camera", 1, "s"), ("monitor", 1, "s"), ("phone", 1, "s")
]
SKILL_CAP = 4

FRIENDLY_TERMS = [
    ("high school diploma", 2, "w"), ("ged", 2, "w"), ("no experience", 2, "s"),
    ("will train", 2, "w"), ("on-the-job training", 2, "w"),
    ("on the job training", 2, "w"), ("paid training", 2, "w"),
    ("entry level", 1, "w"), ("entry-level", 1, "w"), ("tuition", 1, "s"),
    ("career growth", 1, "w"), ("promote from within", 1, "w"),
    ("full-time", 1, "w"), ("benefits", 1, "w"),
]

# Hands-on cleaning titles. Dropped UNLESS the title also has a step-up word.
CLEANING_TITLES = [
    "custodian", "custodial", "janitor", "janitorial", "housekeeper",
    "housekeeping", "cleaner", "cleaning", "porter", "day porter", "evs tech",
    "evs technician", "evs aide", "environmental services tech",
    "environmental services aide", "environmental services worker",
    "environmental services associate", "environmental services attendant",
    "floor tech", "floor technician", "sanitation", "sanitor", "room attendant",
    "laundry", "dishwasher", "steward",
]
STEP_UP_WORDS = ["supervisor", "lead", "manager", "coordinator", "trainer",
                 "foreman", "inspector", "scheduler", "director", "specialist",
                 "administrator", "planner"]

# Hard vetoes: heavy labor, or out of reach without a degree/license.
NEG_TITLE_TERMS = [
    "picker", "packer", "loader", "unloader", "order selector", "laborer",
    "general labor", "cdl", "truck driver", "delivery driver", "driver",
    "landscap", "groundskeeper", "lawn", "line cook", "cook", "server",
    "registered nurse", "rn", "lpn", "nurse", "physician", "pharmacist",
    "therapist", "attorney", "accountant", "software", "developer",
    "engineer", "architect", "electrician", "plumber", "hvac technician",
    "director", "vice president", "senior manager", "physical therapy",
    "medical assistant", "phlebotom", "caregiver", "cna", "teacher",
    "instructor", "sales representative", "commission", "flooring",
    "carpenter", "framing carpenter", "welder", "stocker", "route merchandiser",
]

# Things in the body that count against fit.
PENALTY_TERMS = [
    ("bachelor's degree required", -3, "s"), ("bachelor's degree is required", -3, "s"),
    ("degree required", -2, "s"), ("master's degree", -3, "s"),
    ("5+ years", -1, "s"), ("7+ years", -2, "s"), ("10+ years", -2, "s"),
    ("lift 75", -1, "s"), ("lift up to 75", -1, "s"), ("lift 100", -2, "s"),
    ("lift up to 100", -2, "s"), ("commission only", -3, "s"),
]

EMPLOYER_TYPES = [
    ("Hospital / health system", [
        "intermountain", "university of utah health", "u of u health",
        "huntsman", "primary children", "hca", "mountainstar", "st. mark",
        "st mark", "lakeview hospital", "jordan valley", "ogden regional",
        "timpanogos", "steward", "salt lake regional", "va medical",
        "veterans affairs", "veterans health", "shriners", "crothall",
        "healthcare services group", "hospital", "medical center", "health"]),
    ("University / school", [
        "university", "college", "slcc", "westminster", "school district",
        "granite school", "canyons school", "jordan school", "davis school",
        "salt lake city school", "academy", "schools"]),
    ("Government", [
        "salt lake county", "salt lake city corporation", "city of", "state of utah",
        "utah department", "department of", "county", "uta", "utah transit",
        "airport", "army", "air force", "navy", "federal", "u.s.", "usajobs",
        "housing authority", "municipal"]),
    ("Facilities services firm", [
        "jll", "jones lang", "cbre", "cushman", "abm", "aramark", "sodexo",
        "compass group", "c&w services", "harvard maintenance", "eurest",
        "iss facility", "newmark", "allied universal", "securitas", "g4s",
        "gardaworld", "paladin"]),
    ("Property management", [
        "greystar", "cottonwood residential", "bridge investment", "apartments",
        "property management", "properties", "residential", "living",
        "communities", "asset living", "alliance residential", "wasatch property"]),
    ("Library / museum / arts", [
        "library", "museum", "gallery", "umfa", "arts council", "art center",
        "arts center", "makerspace", "theatre", "theater", "symphony", "ballet"]),
    ("Print / sign / fabrication", [
        "sign", "signs", "graphics", "printing", "print", "wraps", "imaging",
        "engraving", "awards", "embroidery", "screen print", "fabrication",
        "dental lab", "prototype", "frame", "framing"]),
    ("Retail / e-commerce", [
        "michaels", "hobby lobby", "target", "nordstrom", "anthropologie",
        "pottery barn", "west elm", "crate", "rh ", "ikea", "boutique",
        "shopify", "store", "retail"]),
    ("Church / nonprofit", ["church of jesus christ", "latter-day saints",
                            "deseret", "catholic", "nonprofit", "foundation"]),
]

# Libraries and museums are often run by a county or university; label them
# by what they are, so check that type first.
EMPLOYER_TYPES.sort(key=lambda t: 0 if t[0].startswith("Library") else 1)


def _rx_list(terms):
    out = []
    for t in terms:
        if isinstance(t, tuple):
            term, w, mode = t
            out.append((term, w, _wre(term) if mode == "w" else _sre(term)))
        else:
            out.append((t, 0, _wre(t) if not t.endswith(("landscap", "phlebotom"))
                        else _sre(t)))
    return out


_TRACK_RES = [(n, why, entry, _rx_list(terms)) for n, why, entry, terms in TRACKS]
_SKILL = _rx_list(SKILL_TERMS)
_FRIENDLY = _rx_list(FRIENDLY_TERMS)
_PENALTY = _rx_list(PENALTY_TERMS)
_CLEAN = [_wre(t) for t in CLEANING_TITLES]
_STEPUP = [_wre(t) for t in STEP_UP_WORDS]
_NEG = [_sre(t) if t in ("landscap", "phlebotom") else _wre(t) for t in NEG_TITLE_TERMS]
TRACK_INFO = {n: (why, entry) for n, why, entry, _ in TRACKS}
_PHYS_NEG = [_wre(t) for t in PHYSICAL_NEG_TITLES]
_PHYS_FLAG_RES = [(n, re.compile(p, re.I)) for n, p in PHYS_FLAGS]


def physical_scan(text: str) -> tuple[int, list[str], bool]:
    """(heaviest lift asked, list of demand flags, says seated/bench)."""
    lifts = [int(m.group(1)) for m in _LIFT_RE.finditer(text or "")]
    lift = max([x for x in lifts if x <= 200], default=0)
    flags = [n for n, rx in _PHYS_FLAG_RES if rx.search(text or "")]
    if lift > LIFT_LIMIT_LBS:
        flags.insert(0, f"lift {lift} lbs")
    return lift, flags, bool(PHYS_GOOD.search(text or ""))


# ============================================================================
# DATA MODEL
# ============================================================================

# Same core columns, in the same order, as joblens (LingJobs); the
# person-specific columns follow. "field" is the career track.
COLUMNS = [
    "field", "job_title", "organization", "location", "salary", "min_degree",
    "url", "site", "site_url", "source", "date_posted", "employment_type",
    "score", "physical_fit", "physical_flags", "pay_hourly_est", "shift",
    "asks_for", "employer_type", "area", "track_group", "why_it_fits",
    "certificate_hint", "matched_terms", "degree_context", "summary",
]
EXCLUDED_COLUMNS = ["reason", "job_title", "organization", "location", "salary",
                    "url", "source", "date_posted", "score", "summary"]


@dataclass
class Job:
    job_title: str = ""
    organization: str = ""
    location: str = ""
    salary: str = ""
    url: str = ""
    source: str = ""
    date_posted: str = ""
    employment_type: str = ""
    summary: str = ""
    # filled by scoring
    track: str = ""
    track_group: str = ""
    min_degree: str = ""
    degree_context: str = ""
    physical_fit: str = ""
    physical_flags: str = ""
    employer_type: str = ""
    area: str = ""
    pay: str = ""
    pay_hourly_est: str = ""
    shift: str = ""
    asks_for: str = ""
    certificate_hint: str = ""
    why_it_fits: str = ""
    site: str = ""
    site_url: str = ""
    matched_terms: str = ""
    score: int = 0
    region_known: bool = True      # False = source gave no usable location

    def key(self) -> str:
        norm = lambda s: re.sub(r"[^a-z0-9]+", "", (s or "").lower())
        base = norm(self.job_title) + "|" + norm(self.organization) + "|" + norm(self.location)[:20]
        return hashlib.sha1(base.encode()).hexdigest()

    def row(self) -> dict:
        d = asdict(self)
        d["field"] = self.track
        d["salary"] = self.salary or self.pay
        d["summary"] = clip(self.summary, 1500)
        return {c: d.get(c, "") for c in COLUMNS}


# ============================================================================
# REGION, PAY, SHIFT, REQUIREMENTS
# ============================================================================

_TOWN_RES = [(county, t, re.compile(rf"(?<![a-z]){re.escape(t)}(?![a-z])", re.I))
             for county in REGIONS_ON for t in REGION_TOWNS[county]]
_UTAH = re.compile(r"\b(utah|ut)\b", re.I)


def set_regions(regions: list[str]) -> None:
    """Change which counties count as 'in the region' (used by the window app)."""
    global REGIONS_ON, _TOWN_RES
    REGIONS_ON = [r for r in regions if r in REGION_TOWNS]
    _TOWN_RES = [(county, t, re.compile(rf"(?<![a-z]){re.escape(t)}(?![a-z])", re.I))
                 for county in REGIONS_ON for t in REGION_TOWNS[county]]


def region_of(location: str) -> str:
    """County name if the location is in the search region, else ''."""
    loc = location or ""
    for county, town, rx in _TOWN_RES:
        if rx.search(loc):
            # "Sandy" or "Murray" alone could be elsewhere; trust it when
            # Utah is named or the source was already geo-filtered.
            return county
    return ""


def hourly_estimate(text: str) -> float | None:
    """Best-effort hourly figure from a pay string or body text."""
    if not text:
        return None
    t = text.replace(",", "")
    m = re.search(r"\$?\s*(\d{2,3}(?:\.\d{1,2})?)\s*(?:-|to|–)\s*\$?\s*(\d{2,3}(?:\.\d{1,2})?)\s*"
                  r"(?:/|per|an|a)?\s*(?:hr|hour|hourly)", t, re.I)
    if m:
        return round((float(m.group(1)) + float(m.group(2))) / 2, 2)
    m = re.search(r"\$\s*(\d{2,3}(?:\.\d{1,2})?)\s*(?:/|per|an|a)?\s*(?:hr|hour)", t, re.I)
    if m:
        return float(m.group(1))
    nums = [float(x) for x in re.findall(r"\$?\s*(\d{4,6}(?:\.\d+)?)", t)]
    nums = [n for n in nums if 15000 <= n <= 250000]
    if nums:
        return round(sum(nums[:2]) / len(nums[:2]) / 2080, 2)
    m = re.search(r"(?<!\d)(\d{2}(?:\.\d{1,2})?)\s*(?:-|to)\s*(\d{2}(?:\.\d{1,2})?)(?!\d)", t)
    if m and 10 <= float(m.group(1)) <= 80 and re.search(r"hour|hr|hourly", t, re.I):
        return round((float(m.group(1)) + float(m.group(2))) / 2, 2)
    return None


_SHIFTS = [
    ("Day shift", r"\bday shift|days\b|\bdaytime\b|7\s*a\.?m|8\s*a\.?m"),
    ("Mon–Fri", r"monday\s*(?:-|through|to|–)\s*friday|\bm\s*-\s*f\b|mon\s*-\s*fri"),
    ("Evenings / swing", r"\bswing\b|evening shift|second shift|2nd shift"),
    ("Nights", r"\bnight shift|\bnights\b|graveyard|third shift|3rd shift|overnight"),
    ("Weekends", r"\bweekends?\b"),
    ("Rotating", r"\brotating\b"),
    ("Part-time", r"\bpart[\s-]?time\b|\bprn\b"),
]
_SHIFT_RES = [(n, re.compile(p, re.I)) for n, p in _SHIFTS]


def shift_of(text: str) -> str:
    return ", ".join(n for n, rx in _SHIFT_RES if rx.search(text or ""))


_ASKS = [
    ("Bachelor's", r"bachelor'?s?|four-year degree|4-year degree|\bb\.?a\.?\b|\bb\.?s\.?\b"),
    ("Associate's", r"associate'?s? degree"),
    ("High school / GED", r"high school|\bged\b|diploma"),
    ("Driver's license", r"driver'?s licen[cs]e|valid license"),
    ("Background check", r"background check|background screen"),
    ("Certification", r"\bcrcst\b|\bcbspd\b|\bosha\s*(?:10|30)\b|\bicc\b|"
                      r"certification required|certified|\bchest\b|\bchesp\b|\bcamt\b|epa 608|forklift cert"),
    ("Security license", r"security (?:officer |guard )?licen[cs]e|armed"),
]
_ASK_RES = [(n, re.compile(p, re.I)) for n, p in _ASKS]


def asks_for(text: str) -> str:
    return ", ".join(n for n, rx in _ASK_RES if rx.search(text or ""))


def employer_type(org: str, source: str = "") -> str:
    s = f"{org} {source}".lower()
    for name, keys in EMPLOYER_TYPES:
        if any(k in s for k in keys):
            return name
    return "Private employer"


# ============================================================================
# SCORING
# ============================================================================

_SAL_RE = re.compile(
    r"\$\s?\d[\d,]*(?:\.\d{1,2})?(?:\s*(?:k|K))?"
    r"(?:\s*(?:-|–|to)\s*\$?\s?\d[\d,]*(?:\.\d{1,2})?(?:\s*(?:k|K))?)?"
    r"(?:\s*(?:/|per|an|a)\s*(?:hour|hr|year|yr|annually|month))?", re.I)


def extract_salary(text: str) -> str:
    """First pay figure stated in the ad text, as written ('$18 - $21 per hour')."""
    for m in _SAL_RE.finditer(text or ""):
        s = m.group(0).strip()
        if re.search(r"\d{2}", s):
            return s
    return ""


_DEG = [
    ("Bachelor's", re.compile(r"bachelor'?s?|four-year degree|4-year degree|\bB\.?[AS]\.?\b", re.I)),
    ("Associate's", re.compile(r"associate'?s? degree|two-year degree|2-year degree", re.I)),
    ("Certificate", re.compile(r"certificat(?:e|ion) (?:required|program)|\bcrcst\b|\bcbspd\b", re.I)),
    ("High school", re.compile(r"high school|\bged\b|diploma", re.I)),
]


def extract_min_degree(text: str) -> tuple[str, str]:
    """Lowest credential the ad mentions, with the sentence around it."""
    found = []
    for name, rx in _DEG:
        m = rx.search(text or "")
        if m:
            found.append((name, re.sub(r"\s+", " ", text[max(0, m.start() - 70): m.end() + 70]).strip()))
    return found[-1] if found else ("", "")


def match_track(title: str) -> tuple[str, int, list[str]]:
    best, best_w, hits = "", 0, []
    for name, _, _, terms in _TRACK_RES:
        for t, w, rx in terms:
            if rx.search(title):
                hits.append(t)
                if w > best_w:
                    best, best_w = name, w
    return best, best_w, hits


def score_job(job: Job) -> Job:
    title = job.job_title or ""
    body = job.summary or ""
    blob = f"{title} {body}"

    # 1. hands-on cleaning title with no step-up word -> out
    if any(rx.search(title) for rx in _CLEAN) and not any(rx.search(title) for rx in _STEPUP):
        job.score, job.matched_terms = -1, "VETO: hands-on cleaning role"
        return job
    # 2. heavy labor / out of reach
    for rx in _NEG:
        if rx.search(title):
            job.score, job.matched_terms = -1, "VETO: " + rx.pattern
            return job

    track, tw, thits = match_track(title)
    if not track:
        job.score, job.matched_terms = 0, "no track in title"
        return job
    if track == HANDS_ON_TRACK and not INCLUDE_HANDS_ON_TRADES:
        job.score, job.matched_terms = -1, "VETO: hands-on trade (INCLUDE_HANDS_ON_TRADES is off)"
        return job

    skill = min(sum(w for _, w, rx in _SKILL if rx.search(body)), SKILL_CAP)
    friendly = min(sum(w for _, w, rx in _FRIENDLY if rx.search(blob)), 4)
    penalty = sum(w for _, w, rx in _PENALTY if rx.search(blob))
    job.score = tw + skill + friendly + penalty
    if PHYSICAL_LIMITS:
        lift_, pf_, seated_ = physical_scan(blob)
        job.score += {"good": 2, "caution": -1}.get(PHYSICAL.get(track, "good"), 0)
        job.score -= min(len(pf_), 3)
        job.score += 1 if seated_ else 0

    job.track = track
    if track in CREATIVE_NAMES and not INCLUDE_CREATIVE:
        job.score, job.matched_terms = -1, "VETO: creative tracks are off"
        return job
    if track in STRETCH_TRACKS and not INCLUDE_STRETCH:
        job.score, job.matched_terms = -1, "VETO: stretch tracks are off"
        return job
    phys = PHYSICAL.get(track, "good")
    lift, pflags, says_seated = physical_scan(blob)
    if PHYSICAL_LIMITS:
        for rx in _PHYS_NEG:
            if rx.search(title):
                job.score, job.matched_terms = -1, "VETO: physical (" + rx.pattern + ")"
                return job
        if phys == "avoid":
            job.score, job.matched_terms = -1, f"VETO: physical — {track} is on the avoid list"
            return job
        if phys == "caution" and pflags:
            job.score, job.matched_terms = -1, ("VETO: caution role and the ad lists "
                                                + ", ".join(pflags))
            return job
    job.physical_flags = ", ".join(pflags)
    if phys == "good":
        job.physical_fit = ("Good fit" if not pflags else
                            "Good fit — check physical section (often boilerplate)")
    else:
        job.physical_fit = "Caution — ask about walking, standing and lifting"
    if says_seated:
        job.physical_fit += " · ad says seated/bench"
    job.track_group = ("Stretch (6-12 months of skills)" if track in STRETCH_TRACKS else
                       "Creative & maker" if track in CREATIVE_NAMES else
                       "Operations step-up")
    job.why_it_fits, job.certificate_hint = TRACK_INFO[track]
    job.employer_type = employer_type(job.organization, job.source)
    if job.employer_type in ("Hospital / health system", "University / school", "Government",
                             "Library / museum / arts"):
        job.score += 1            # stable benefits, internal promotion ladders
    job.area = region_of(job.location) or ("check location" if not job.region_known else "")
    hr = hourly_estimate(job.salary) or hourly_estimate(body)
    job.pay_hourly_est = f"{hr:.2f}" if hr else ""
    if not job.salary:
        job.salary = extract_salary(body)
    job.pay = job.salary
    job.min_degree, job.degree_context = extract_min_degree(body)
    job.shift = shift_of(blob)
    job.asks_for = asks_for(body)
    if not job.site:
        job.site, job.site_url = site_of(job.url)
    job.matched_terms = "; ".join(
        [f"title[{', '.join(thits[:4])}]"] +
        ([f"skills[{', '.join(t for t, _, rx in _SKILL if rx.search(body))[:120]}]"] if skill else []) +
        ([f"friendly+{friendly}"] if friendly else []) +
        ([f"penalty{penalty}"] if penalty else []))
    return job


def keep(job: Job, min_score: int = MIN_SCORE) -> bool:
    if job.score < min_score or not job.track:
        return False
    if job.region_known and not job.area:
        return False                      # outside the SLC region
    if MIN_HOURLY and job.pay_hourly_est and float(job.pay_hourly_est) < MIN_HOURLY:
        return False
    return True


# ============================================================================
# SOURCES
# ============================================================================

def _json_path(d, *path, default=None):
    for p in path:
        if isinstance(d, dict):
            d = d.get(p)
        elif isinstance(d, list) and isinstance(p, int) and len(d) > p:
            d = d[p]
        else:
            return default
    return d if d is not None else default


# Adzuna queries per track. Queries for tracks on the "avoid" list are
# skipped automatically while PHYSICAL_LIMITS is on (fewer API calls).
ADZUNA_QUERIES_BY_TRACK = {
    "Dispatch & Scheduling": ["dispatcher", "service coordinator", "scheduling coordinator",
                              "patient scheduler", "911 dispatcher", "work order coordinator"],
    "Security Desk & Badging": ["access control", "badging", "security console operator",
                                "alarm monitoring", "security receptionist"],
    "Purchasing & Inventory Data (desk)": ["purchasing assistant", "purchasing coordinator",
                                           "procurement assistant", "inventory data entry"],
    "Pre-Press & File Prep": ["prepress", "production artist"],
    "Bench Engraving & Small-Format Vinyl": ["laser engraver", "engraving", "personalization"],
    "Embroidery & Digitizing": ["embroidery", "embroidery digitizer"],
    "Dental Lab Technician": ["dental lab technician", "dental laboratory"],
    "Optical Lab / Optician Assistant": ["optical lab technician", "optician assistant",
                                         "optometric technician"],
    "Electronics Assembly & Device Repair": ["electronics assembler", "soldering",
                                             "phone repair technician", "bench technician"],
    "Library Technical Services": ["library technician", "library technical services"],
    "Photo Digitization & Archival Scanning": ["digitization technician", "scanning technician",
                                               "document imaging"],
    "Makerspace / FabLab Technician": ["makerspace"],
    "3D Printing Operator": ["3d printing technician"],
    "CAD Drafting / UI Design (stretch)": ["cad drafter", "drafting technician"],
    "Facilities Coordination": ["facilities coordinator", "facilities assistant"],
    "Custodial / EVS Supervisor": ["custodial supervisor", "environmental services supervisor"],
    "Sterile Processing": ["sterile processing"],
    "Security Officer (check post)": ["security officer"],
    "E-commerce Photo & Listing": ["product photographer", "ecommerce specialist"],
    "Custom Framing & Screen Print": ["custom framing"],
    "Inventory & Supply Chain": ["inventory control", "supply chain technician"],
    "Shipping, Receiving & Logistics": ["shipping receiving clerk"],
    "Property Management": ["leasing consultant"],
    "Inspection & Code Compliance": ["code enforcement"],
    "Safety / EHS": ["ehs technician"],
    "Sign & Large-Format Print": ["sign production"],
    "Visual Merchandising & Display": ["visual merchandiser"],
    "Museum & Gallery Preparator": ["preparator"],
}
ADZUNA_PAGES = 1        # local results rarely fill more than one page of 50


def adzuna_queries() -> list[str]:
    out = []
    for track, qs in ADZUNA_QUERIES_BY_TRACK.items():
        if PHYSICAL_LIMITS and PHYSICAL.get(track) == "avoid":
            continue
        if track in CREATIVE_NAMES and not INCLUDE_CREATIVE:
            continue
        if track in STRETCH_TRACKS and not INCLUDE_STRETCH:
            continue
        out += qs
    return list(dict.fromkeys(out))


def src_adzuna(f, keys) -> Iterator[Job]:
    app_id, app_key = keys.get("adzuna_app_id"), keys.get("adzuna_app_key")
    if not (app_id and app_key):
        raise Blocked("no Adzuna keys (add them to slcjobs_keys.json)")
    for q in adzuna_queries():
        for page in range(1, ADZUNA_PAGES + 1):
            data = f.get_json(
                f"https://api.adzuna.com/v1/api/jobs/us/search/{page}",
                params={"app_id": app_id, "app_key": app_key, "what": q,
                        "where": SEARCH_CENTER, "distance": ADZUNA_DISTANCE_KM,
                        "max_days_old": 45, "results_per_page": 50,
                        "content-type": "application/json"})
            results = (data or {}).get("results") or []
            for r in results:
                lo, hi = r.get("salary_min"), r.get("salary_max")
                pred = " (estimated)" if str(r.get("salary_is_predicted")) == "1" else ""
                areas = _json_path(r, "location", "area", default=[]) or []
                yield Job(
                    job_title=r.get("title", ""),
                    organization=_json_path(r, "company", "display_name", default=""),
                    location=", ".join([_json_path(r, "location", "display_name", default="")] +
                                       [a for a in areas[-2:] if isinstance(a, str)]),
                    salary=(fmt_salary(lo, hi, "per year", "$") + pred) if lo else "",
                    url=r.get("redirect_url", ""), source="Adzuna",
                    date_posted=(r.get("created") or "")[:10],
                    employment_type=r.get("contract_time") or "",
                    summary=strip_html(r.get("description", "")))
            if len(results) < 50:
                break


USAJOBS_KEYWORDS = [
    "dispatcher", "medical support assistant", "scheduler", "security assistant",
    "alarm", "purchasing", "procurement technician", "dental laboratory",
    "library technician", "archives technician", "digitization", "electronics",
    "facility", "custodial supervisor", "sterile processing",
]


def src_usajobs(f, keys) -> Iterator[Job]:
    key, email = keys.get("usajobs_api_key"), keys.get("usajobs_email")
    if not (key and email):
        raise Blocked("no USAJobs key/email (add them to slcjobs_keys.json)")
    hdr = {"Host": "data.usajobs.gov", "User-Agent": email, "Authorization-Key": key}
    for kw in USAJOBS_KEYWORDS:
        data = f.get_json("https://data.usajobs.gov/api/search",
                          params={"Keyword": kw, "LocationName": SEARCH_CENTER,
                                  "Radius": USAJOBS_RADIUS_MILES,
                                  "ResultsPerPage": 250}, headers=hdr)
        for it in _json_path(data, "SearchResult", "SearchResultItems", default=[]):
            d = it.get("MatchedObjectDescriptor", {})
            rem = (d.get("PositionRemuneration") or [{}])[0]
            ua = _json_path(d, "UserArea", "Details", default={}) or {}
            # multi-location postings: keep only the in-region locations
            locs = [l.get("LocationName", "") for l in d.get("PositionLocation") or []]
            local = [l for l in locs if region_of(l)] or [d.get("PositionLocationDisplay", "")]
            unit = rem.get("Description", "")
            yield Job(
                job_title=d.get("PositionTitle", ""),
                organization=" – ".join(filter(None, [d.get("DepartmentName", ""),
                                                       d.get("OrganizationName", "")])),
                location="; ".join(local),
                salary=fmt_salary(rem.get("MinimumRange"), rem.get("MaximumRange"),
                                  unit, "$"),
                url=d.get("PositionURI", ""), source="USAJobs",
                date_posted=(d.get("PublicationStartDate") or "")[:10],
                employment_type=_json_path(d, "PositionSchedule", 0, "Name", default=""),
                summary=strip_html(" ".join(filter(None, [
                    ua.get("JobSummary", ""), d.get("QualificationSummary", ""),
                    ua.get("Education", "")]))))


# --- Workday career sites (many big Utah employers). Paste the address you
# see in your browser on the employer's job list; the adapter works out the
# rest. Run --audit: a wrong address simply reports "no board".
WORKDAY_SITES = [
    ("JLL", "https://jll.wd1.myworkdayjobs.com/jllcareers"),      # unverified
    # ("Employer name", "https://<tenant>.wdN.myworkdayjobs.com/<site>"),
]
WORKDAY_SEARCH = ["Salt Lake", "Utah"]


def _workday_parts(url: str):
    p = urllib.parse.urlsplit(url)
    tenant = p.netloc.split(".")[0]
    segs = [s for s in p.path.split("/") if s and not re.fullmatch(r"[a-z]{2}-[A-Z]{2}", s)]
    site = segs[0] if segs else ""
    return p.netloc, tenant, site


def src_workday(f, keys, notes=None) -> Iterator[Job]:
    for name, url in WORKDAY_SITES:
        try:
            yield from _workday_one(f, name, url, notes)
        except Blocked as e:
            f._log(f"  [workday skip] {name}: {e}")
            if notes is not None:
                notes.append(f"Workday/{name}: {e}")


def _workday_one(f, name, url, notes):
    if True:
        host, tenant, site = _workday_parts(url)
        api = f"https://{host}/wday/cxs/{tenant}/{site}/jobs"
        n = 0
        seen = set()
        for q in WORKDAY_SEARCH:
            for offset in range(0, 200, 20):
                data = f.post_json(api, {"appliedFacets": {}, "limit": 20,
                                         "offset": offset, "searchText": q})
                posts = (data or {}).get("jobPostings") or []
                for p in posts:
                    path = p.get("externalPath", "")
                    if path in seen:
                        continue
                    seen.add(path)
                    job = Job(job_title=p.get("title", ""), organization=name,
                              location=p.get("locationsText", ""),
                              url=f"https://{host}/en-US/{site}{path}",
                              source=f"Workday/{name}",
                              date_posted=p.get("postedOn", ""))
                    if "location" in job.location.lower():     # "3 Locations"
                        job.region_known = False
                    # Only fetch the full description for titles on a track
                    if match_track(job.job_title)[0]:
                        det = f.get_json(f"https://{host}/wday/cxs/{tenant}/{site}{path}")
                        info = (det or {}).get("jobPostingInfo") or {}
                        job.summary = strip_html(info.get("jobDescription", ""))
                        job.location = info.get("location", job.location) or job.location
                        job.region_known = True
                    n += 1
                    yield job
                if len(posts) < 20:
                    break
        f._log(f"  [workday] {name}: {n} postings")
        if n == 0 and notes is not None:
            notes.append(f"Workday/{name}: no postings — check the address in WORKDAY_SITES")


# --- iCIMS career sites (University of Utah Health uses one).
ICIMS_SITES = [
    ("University of Utah Health", "https://careers-uuhc.icims.com"),
]
ICIMS_QUERIES = ["supervisor", "coordinator", "supply chain", "sterile processing",
                 "security", "environmental services", "inventory", "facilities"]


def src_icims(f, keys, notes=None) -> Iterator[Job]:
    if BeautifulSoup is None:
        raise Blocked("beautifulsoup4 not installed")
    for name, base in ICIMS_SITES:
        try:
            yield from _icims_one(f, name, base, notes)
        except Blocked as e:
            f._log(f"  [icims skip] {name}: {e}")
            if notes is not None:
                notes.append(f"iCIMS/{name}: {e} — search this site by hand")


def _icims_one(f, name, base, notes):
    if True:
        n = 0
        for q in ICIMS_QUERIES:
            body = f.get(f"{base}/jobs/search", params={"ss": "1", "searchKeyword": q,
                                                        "in_iframe": "1"})
            if not body:
                continue
            soup = BeautifulSoup(body, "html.parser")
            for a in soup.select("a[href*='/jobs/']"):
                href = a.get("href", "")
                if not re.search(r"/jobs/\d+/", href):
                    continue
                title = a.get("title") or a.get_text(" ", strip=True)
                title = re.sub(r"^\s*job title\s*", "", title, flags=re.I).strip()
                row = a.find_parent(["li", "div", "tr"])
                text = row.get_text(" ", strip=True) if row else ""
                loc = ""
                m = re.search(r"(US-UT-[A-Za-z .-]+|[A-Z][a-z]+(?: [A-Z][a-z]+)*, UT)", text)
                if m:
                    loc = m.group(1).replace("US-UT-", "") + ", UT"
                n += 1
                yield Job(job_title=title, organization=name,
                          location=loc or "Salt Lake City, UT",
                          url=urllib.parse.urljoin(base, href.split("?")[0]),
                          source=f"iCIMS/{name}", summary=text[:600])
        f._log(f"  [icims] {name}: {n} postings")
        if n == 0 and notes is not None:
            notes.append(f"iCIMS/{name}: nothing parsed — search this site by hand")


SOURCES: dict[str, tuple[str, Callable]] = {
    "adzuna":  ("Adzuna (keyed; aggregates most local job boards)", src_adzuna),
    "usajobs": ("USAJobs (keyed; VA SLC, Hill AFB, Tooele Army Depot ...)", src_usajobs),
    "workday": ("Employer Workday sites (edit WORKDAY_SITES)", src_workday),
    "icims":   ("Employer iCIMS sites (University of Utah Health)", src_icims),
}
NEEDS_NOTES = {"workday", "icims"}

# Written to the XLSX "Search by hand" tab.
MANUAL_SITES = [
    ("Utah DWS Job Board", "https://jobs.utah.gov/", "State workforce board; many local employers post only here"),
    ("State of Utah jobs", "https://statejobs.utah.gov/", "Facilities, inventory, security and safety roles with state benefits"),
    ("Salt Lake County", "https://slco.org/", "Careers page: facilities, parks/rec ops, code enforcement"),
    ("Salt Lake City Corporation", "https://www.slc.gov/", "Careers page: also hires for the SLC International Airport"),
    ("Utah Transit Authority", "https://www.rideuta.com/", "Dispatch, facilities and inventory roles"),
    ("University of Utah (campus)", "https://www.utah.edu/", "Facilities Management, Housing & Residential Ed, Campus Security"),
    ("University of Utah Health", "https://careers-uuhc.icims.com/", "EVS supervisor, supply chain, sterile processing"),
    ("Intermountain Health", "https://intermountainhealth.org/careers", "Largest Utah employer: EVS leads, supply chain, sterile processing, security"),
    ("HCA MountainStar (St. Mark's, Lakeview, Jordan Valley)", "https://careers.hcahealthcare.com/", "EVS and sterile processing"),
    ("Salt Lake Community College", "https://www.slcc.edu/", "Facilities and custodial supervisor roles"),
    ("Granite / Canyons / Jordan / Salt Lake City / Davis school districts", "https://www.graniteschools.org/", "District custodial supervisor and warehouse/inventory roles; check each district's HR page"),
    ("Church of Jesus Christ employment", "https://careers.churchofjesuschrist.org/", "Facilities management for meetinghouses and Temple Square; large SLC employer"),
    ("JLL / CBRE / Cushman & Wakefield", "https://www.jll.com/", "Facilities coordinator roles on corporate campuses (Draper, Lehi, downtown)"),
    ("ABM / Aramark / Sodexo / Crothall", "https://www.abm.com/", "Custodial and EVS supervisor roles at hospitals, campuses, airports"),
    ("Allied Universal / Securitas", "https://www.aus.com/", "Security officer and access-control posts"),
    ("Salt Lake County Library", "https://www.slcolibrary.org/", "Creative/maker spaces at several branches; library assistant and lab jobs post through the county"),
    ("The City Library (Salt Lake City)", "https://www.slcpl.org/", "Creative Lab at the Main Library; jobs post through Salt Lake City"),
    ("University of Utah Marriott Library", "https://lib.utah.edu/", "Makerspace and digital-fabrication staff; campus jobs include tuition benefits"),
    ("Utah Museum of Fine Arts", "https://umfa.utah.edu/", "Collections-database and digitization roles (University of Utah jobs); skip preparator posts"),
    ("Natural History Museum of Utah", "https://nhmu.utah.edu/", "Collections and imaging roles (University of Utah jobs); skip exhibit installation"),
    ("FamilySearch (Church of Jesus Christ)", "https://careers.churchofjesuschrist.org/", "Record digitization and imaging roles in Salt Lake; search 'FamilySearch'"),
    ("Utah State Archives / State History", "https://archives.utah.gov/", "Archives and digitization technicians (State of Utah jobs)"),
    ("University of Utah Marriott Library (Digital Library)", "https://lib.utah.edu/", "Digitization, cataloging and technical services; seated work"),
    ("Dental labs, optical labs, device-repair shops", "https://www.indeed.com/", "Mostly small shops: search 'dental lab', 'optical lab', 'phone repair' near Salt Lake City and read the Physical Requirements section"),
    ("Indeed", "https://www.indeed.com/", "Search each track with location 'Salt Lake City, UT'; export and use --import. Sign, print and engraving shops mostly post here"),
    ("LinkedIn Jobs", "https://www.linkedin.com/jobs/", "Same; good for facilities coordinator roles at tech campuses"),
]


# ============================================================================
# KEYS
# ============================================================================

KEY_FILES = ["slcjobs_keys.json", "lingjobs_keys.json", "gerrusjobs_keys.json", "deruscan_keys.json"]
_KEY_ALIASES = {
    "adzuna_app_id": ["adzunaappid", "adzunaid", "appid"],
    "adzuna_app_key": ["adzunaappkey", "adzunakey", "appkey"],
    "usajobs_api_key": ["usajobsapikey", "usajobskey", "usajobsauthorizationkey"],
    "usajobs_email": ["usajobsemail", "usajobsuseragent", "usajobsuser"],
    "reliefweb_appname": ["reliefwebappname", "reliefweb"],
}


def load_keys(log=print) -> dict:
    # Merge every key file present; earlier files win, but a blank value never
    # hides a filled one in a later file (so an empty template is harmless).
    flat, read = {}, []
    for name in KEY_FILES:
        p = os.path.join(HERE, name)
        if not os.path.exists(p):
            continue
        try:
            raw = json.load(open(p, encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            log(f"[keys] could not read {name}: {e}")
            continue
        read.append(name)
        for k, v in _flatten(raw).items():
            k2 = re.sub(r"[^a-z]", "", k.lower())
            if v and not flat.get(k2):
                flat[k2] = v
    used = ", ".join(read)
    keys = {}
    for canon, aliases in _KEY_ALIASES.items():
        env = os.environ.get(canon.upper())
        val = env or next((flat[a] for a in aliases if flat.get(a)), "")
        if val:
            keys[canon] = str(val).strip()
    if used:
        log(f"[keys] read {used}: " + (", ".join(sorted(keys)) or "no usable keys"))
    return keys


def _flatten(d, prefix=""):
    out = {}
    if isinstance(d, dict):
        for k, v in d.items():
            if isinstance(v, dict):
                out.update(_flatten(v, prefix + k))
            else:
                out[prefix + k] = v
    return out


# ============================================================================
# SMART IMPORT (hand-downloaded CSV / XLSX from LinkedIn, Indeed, etc.)
# ============================================================================

_IMPORT_MAP = {
    "job_title": ["job_title", "title", "jobtitle", "position", "role", "job", "stellentitel"],
    "organization": ["organization", "company", "companyname", "employer", "org", "arbeitgeber"],
    "location": ["location", "city", "joblocation", "place", "ort"],
    "url": ["url", "link", "joburl", "applyurl", "href", "joblink"],
    "salary": ["salary", "pay", "compensation", "salaryrange"],
    "date_posted": ["dateposted", "date", "posted", "postedat", "listed"],
    "summary": ["summary", "description", "jobdescription", "details", "snippet", "beschreibung"],
    "employment_type": ["employmenttype", "jobtype", "type", "schedule"],
    "site": ["site", "listedon", "jobboard", "board", "foundon"],
    "site_url": ["siteurl", "boardurl", "searchurl"],
    "_physical": ["physicalrequirements", "physicaldemands", "physical", "workingconditions"],
}


def src_smart_import(path: str) -> Iterator[Job]:
    ext = os.path.splitext(path)[1].lower()
    if ext in (".xlsx", ".xlsm"):
        from openpyxl import load_workbook
        ws = load_workbook(path, read_only=True, data_only=True).active
        it = ws.iter_rows(values_only=True)
        header = [str(h or "") for h in next(it)]
        rows = [dict(zip(header, r)) for r in it]
    else:
        with open(path, newline="", encoding="utf-8-sig") as fh:
            rows = list(csv.DictReader(fh))
        header = list(rows[0].keys()) if rows else []
    norm = {re.sub(r"[^a-z]", "", h.lower()): h for h in header}
    col = {k: next((norm[a] for a in al if a in norm), None) for k, al in _IMPORT_MAP.items()}
    label = os.path.basename(path)
    for r in rows:
        kw = {k: str(r.get(c) or "").strip() for k, c in col.items() if c}
        if not kw.get("job_title"):
            continue
        kw["summary"] = strip_html(kw.get("summary", ""))
        phys = kw.pop("_physical", "")
        if phys:   # keep the ad's physical-requirements text where the rules can see it
            kw["summary"] = (kw.get("summary", "") + " Physical requirements: " + phys).strip()
        site = kw.get("site", "")
        # files made by the Claude-in-Chrome guide name the site they came from
        yield Job(source=(f"{site} (searched by hand)" if site else f"import:{label}"), **kw)




# ============================================================================
# PIPELINE
# ============================================================================

LAST_EXCLUDED: list[dict] = []     # filled by finalize(); written to *_excluded.csv


def finalize(jobs: Iterable[Job], min_score: int = MIN_SCORE, log=print
             ) -> tuple[list[Job], dict]:
    LAST_EXCLUDED.clear()
    best: dict[str, Job] = {}
    stats = defaultdict(Counter)
    for j in jobs:
        score_job(j)
        src = j.source.split("/")[0]
        stats[src]["seen"] += 1
        if j.score < 0:
            stats[src]["vetoed"] += 1
            _exclude(j, j.matched_terms.replace("VETO: ", ""))
            continue
        if not keep(j, min_score):
            _exclude(j, "outside the Salt Lake region" if (j.track and j.region_known and not j.area)
                     else "no matching career track in title" if not j.track
                     else f"fit score {j.score} below {min_score}")
            stats[src]["out of region" if (j.track and j.region_known and not j.area
                                            and j.score >= min_score) else "dropped"] += 1
            continue
        stats[src]["kept"] += 1
        k = j.key()
        if k in best:
            old = best[k]
            if j.score > old.score:
                j.source = ", ".join(dict.fromkeys([j.source] + old.source.split(", ")))
                best[k] = j
            elif j.source not in old.source:
                old.source += ", " + j.source
        else:
            best[k] = j
    per_org: Counter = Counter()
    out = []
    for j in sorted(best.values(), key=lambda x: (-x.score, x.track, x.job_title)):
        per_org[(j.organization or "?").lower()] += 1
        if per_org[(j.organization or "?").lower()] <= PER_EMPLOYER_CAP:
            out.append(j)
    if len(best) > len(out):
        log(f"[cap] dropped {len(best) - len(out)} postings beyond {PER_EMPLOYER_CAP} per employer")
    return out, stats


def _exclude(j: Job, reason: str) -> None:
    LAST_EXCLUDED.append({"reason": reason, "job_title": j.job_title,
                          "organization": j.organization, "location": j.location,
                          "salary": j.salary, "url": j.url, "source": j.source,
                          "date_posted": j.date_posted, "score": j.score,
                          "summary": clip(j.summary, 400)})


def write_excluded(path: str) -> int:
    with open(path, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=EXCLUDED_COLUMNS)
        w.writeheader()
        for r in sorted(LAST_EXCLUDED, key=lambda r: (r["reason"], r["job_title"])):
            w.writerow(r)
    return len(LAST_EXCLUDED)


def run(sources: list[str], *, dry_run=False, verbose=True, log=None,
        min_score=MIN_SCORE, imports: list[str] | None = None):
    log = log or (lambda m: print(m, file=sys.stderr))
    keys = load_keys(log)
    f = PoliteFetcher(dry_run=dry_run, verbose=verbose, log=log)
    f.session.headers["Accept-Language"] = "en-US,en;q=0.9"
    raw: list[Job] = []
    yields: dict[str, int] = {}
    notes: list[str] = []
    for name in sources:
        label, fn = SOURCES[name]
        log(f"\n== {label} ==")
        n0 = len(raw)
        try:
            gen = fn(f, keys, notes) if name in NEEDS_NOTES else fn(f, keys)
            raw.extend(gen)
        except Blocked as e:
            notes.append(f"{name}: {e}")
            log(f"  [skipped] {e}")
        except Exception as e:
            notes.append(f"{name}: ERROR {type(e).__name__}: {e}")
            log(f"  [error] {type(e).__name__}: {e}")
        yields[name] = len(raw) - n0
    for p in imports or []:
        n0 = len(raw)
        try:
            for j in src_smart_import(p):
                j.region_known = bool(j.location)
                raw.append(j)
        except Exception as e:
            notes.append(f"import {p}: {e}")
        yields[f"import:{os.path.basename(p)}"] = len(raw) - n0
    kept, stats = finalize(raw, min_score, log)
    return kept, stats, notes, yields


# ============================================================================
# OUTPUT
# ============================================================================

def write_csv(jobs: list[Job], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS)
        w.writeheader()
        for j in jobs:
            w.writerow(j.row())


def read_csv_jobs(path: str) -> list[Job]:
    names = {f.name for f in fields(Job)}
    out = []
    with open(path, newline="", encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            kw = {k: v for k, v in r.items() if k in names and k not in ("score", "region_known")}
            kw["salary"] = kw.get("salary") or r.get("pay", "")
            out.append(Job(**kw))
    return out


def _median(xs):
    xs = sorted(xs)
    if not xs:
        return None
    m = len(xs) // 2
    return xs[m] if len(xs) % 2 else (xs[m - 1] + xs[m]) / 2


def track_summary(jobs: list[Job]) -> list[list]:
    rows = []
    for name, why, entry, _ in TRACKS:
        js = [j for j in jobs if j.track == name]
        if not js and name == HANDS_ON_TRACK and not INCLUDE_HANDS_ON_TRADES:
            continue
        pays = [float(j.pay_hourly_est) for j in js if j.pay_hourly_est]
        med = _median(pays)
        orgs = Counter(j.organization for j in js if j.organization).most_common(4)
        if PHYSICAL_LIMITS and PHYSICAL.get(name) == "avoid" and not js:
            continue
        grp = ("Stretch" if name in STRETCH_TRACKS else
               "Creative & maker" if name in CREATIVE_NAMES else "Operations")
        grp = f"{grp} · {PHYSICAL.get(name, 'good')}" if PHYSICAL_LIMITS else grp
        rows.append([grp, name, len(js), f"${med:.2f}" if med else "", len(pays),
                     sum(1 for j in js if "Day shift" in j.shift or "Mon–Fri" in j.shift),
                     "; ".join(f"{o} ({n})" for o, n in orgs), why, entry])
    return rows


def write_xlsx(jobs: list[Job], path: str, stats: dict | None = None,
               notes: list[str] | None = None) -> None:
    """joblens layout: 'All Postings' first, then one tab per field (career
    track), then the run's Sources and the Search-by-hand list."""
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    HEAD = "1F4E79"
    widths = {"field": 30, "job_title": 46, "organization": 30, "location": 26,
              "salary": 24, "min_degree": 13, "url": 46, "site": 22, "site_url": 26,
              "source": 18, "date_posted": 12, "employment_type": 14, "score": 7,
              "physical_fit": 34, "physical_flags": 28, "pay_hourly_est": 10,
              "shift": 20, "asks_for": 26, "employer_type": 22, "area": 16,
              "track_group": 20, "why_it_fits": 46, "certificate_hint": 46,
              "matched_terms": 46, "degree_context": 46, "summary": 80}

    def header(ws, cols):
        ws.append(cols)
        for c in ws[1]:
            c.font = Font(bold=True, color="FFFFFF")
            c.fill = PatternFill("solid", fgColor=HEAD)

    def sheet(name, rows, first=False):
        ws = wb.active if first else wb.create_sheet()
        ws.title = re.sub(r"[\[\]:*?/\\]", "-", name)[:31]
        header(ws, COLUMNS)
        for j in rows:
            ws.append([j.row()[c] for c in COLUMNS])
        uc = COLUMNS.index("url") + 1
        for r in range(2, ws.max_row + 1):
            cell = ws.cell(r, uc)
            if cell.value and str(cell.value).startswith("http"):
                cell.hyperlink = cell.value
                cell.font = Font(color="0563C1", underline="single")
        for i, c in enumerate(COLUMNS, 1):
            ws.column_dimensions[get_column_letter(i)].width = widths.get(c, 14)
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions

    wb = Workbook()
    sheet("All Postings", jobs, first=True)
    for fld in sorted({j.track for j in jobs}):
        sheet(fld.replace("&", "and"), [j for j in jobs if j.track == fld])

    s = wb.create_sheet("Sources")
    header(s, ["source", "fetched", "kept", "no fit", "out of region", "vetoed"])
    for k, c in sorted((stats or {}).items()):
        s.append([k, c["seen"], c["kept"], c["dropped"], c["out of region"], c["vetoed"]])
    if notes:
        s.append([]); s.append(["Run notes"])
        for n in notes:
            s.append([n])
    s.column_dimensions["A"].width = 70

    s = wb.create_sheet("Search by hand")
    header(s, ["site", "url", "what to look for"])
    for n, u, why in MANUAL_SITES:
        s.append([n, u, why])
        s.cell(s.max_row, 2).hyperlink = u
    for col, w in zip("ABC", (44, 46, 90)):
        s.column_dimensions[col].width = w
    wb.save(path)


def print_summary(jobs, stats, notes, yields) -> None:
    p = lambda *a: print(*a, file=sys.stderr)
    p("\n================ SUMMARY ================")
    p(f"{'source':<14}{'fetched':>8}{'kept':>7}{'no fit':>8}{'out of area':>12}{'vetoed':>8}")
    for s, c in sorted(stats.items()):
        p(f"{s[:13]:<14}{c['seen']:>8}{c['kept']:>7}{c['dropped']:>8}"
          f"{c['out of region']:>12}{c['vetoed']:>8}")
    zero = [k for k, v in yields.items() if v == 0]
    if zero:
        p(f"\nSources that returned nothing: {', '.join(zero)}")
    p(f"\nKept {len(jobs)} postings in the Salt Lake region "
      f"({len(LAST_EXCLUDED)} excluded; see the _excluded.csv file for why).")
    p(f"Salary present on {sum(1 for j in jobs if j.salary)}/{len(jobs)} postings; "
      f"URL on {sum(1 for j in jobs if j.url)}/{len(jobs)}.\n")
    p(f"{'group · physical':<26}{'track':<38}{'jobs':>5}{'median $/hr':>13}")
    for r in track_summary(jobs):
        p(f"{r[0][:25]:<26}{r[1][:37]:<38}{r[2]:>5}{r[3]:>13}")
    if notes:
        p("\nNotes:")
        for n in notes:
            p("  - " + n)


# ============================================================================
# SELF-TEST (offline)
# ============================================================================

SELFTEST = [
    # (title, location, body, expect_keep, expect_track)   — PHYSICAL_LIMITS on
    ("HVAC Service Dispatcher", "Bountiful, UT", "Route technicians and answer calls. Seated at a desk.", True, "Dispatch & Scheduling"),
    ("Patient Scheduler", "Murray, UT", "Schedule appointments. High school diploma.", True, "Dispatch & Scheduling"),
    ("Access Control Specialist", "Salt Lake City, UT", "Issue badges, manage keycard access. Monday-Friday.", True, "Security Desk & Badging"),
    ("Security Officer - Mobile Patrol", "Sandy, UT", "Patrol multiple sites.", False, ""),
    ("Security Officer", "Salt Lake City, UT", "Lobby post; must climb stairs during rounds.", False, ""),
    ("Security Officer", "Salt Lake City, UT", "Staff the front desk and check visitor IDs.", True, "Security Officer (check post)"),
    ("Purchasing Coordinator", "Salt Lake City, UT", "Enter purchase orders in Excel.", True, "Purchasing & Inventory Data (desk)"),
    ("Inventory Control Specialist", "Salt Lake City, UT", "Cycle counts.", False, ""),
    ("Shipping and Receiving Clerk", "West Valley City, UT", "Check in drivers.", False, ""),
    ("Leasing Consultant", "Millcreek, UT", "Show units.", False, ""),
    ("EHS Technician", "Lehi, UT", "Safety audits.", False, ""),
    ("Prepress Technician", "Salt Lake City, UT", "Preflight PDFs in Acrobat and InDesign.", True, "Pre-Press & File Prep"),
    ("Digital Press Operator", "Salt Lake City, UT", "Run presses, load paper.", False, ""),
    ("Laser Engraver", "Murray, UT", "Operate laser engravers using LightBurn at a workbench.", True, "Bench Engraving & Small-Format Vinyl"),
    ("Embroidery Digitizer", "Draper, UT", "Convert logos to stitch files.", True, "Embroidery & Digitizing"),
    ("Dental Lab Technician - Model Room", "Salt Lake City, UT", "Pour and trim models; will train.", True, "Dental Lab Technician"),
    ("Optical Lab Technician", "Sandy, UT", "Edge lenses and adjust frames.", True, "Optical Lab / Optician Assistant"),
    ("Electronics Assembler", "Salt Lake City, UT", "Solder small boards at an anti-static bench. Must lift 50 lbs.", True, "Electronics Assembly & Device Repair"),
    ("Library Technician - Technical Services", "Salt Lake City, UT", "Mend books, apply labels, catalog records.", True, "Library Technical Services"),
    ("Library Page", "Salt Lake City, UT", "Shelve books, push carts.", False, ""),
    ("Digitization Technician", "Salt Lake City, UT", "Scan photographs and documents; add metadata.", True, "Photo Digitization & Archival Scanning"),
    ("Makerspace Technician", "Salt Lake City, UT", "Maintain desktop 3D printers and vinyl cutters.", True, "Makerspace / FabLab Technician"),
    ("CAD Drafter", "Salt Lake City, UT", "Draft floor plans in AutoCAD.", True, "CAD Drafting / UI Design (stretch)"),
    ("Facilities Coordinator", "Draper, UT", "Manage work orders in CMMS from the front office.", True, "Facilities Coordination"),
    ("Facilities Coordinator", "Draper, UT", "Walk throughout the campus; lift up to 50 lbs.", False, ""),
    ("EVS Supervisor", "Salt Lake City, UT", "Must be able to stand for long periods and walk throughout the hospital.", False, ""),
    ("Visual Merchandiser", "Salt Lake City, UT", "Build displays.", False, ""),
    ("Preparator", "Salt Lake City, UT", "Install exhibitions.", False, ""),
    ("Sign Production Specialist", "West Valley City, UT", "Wide-format printing.", False, ""),
    ("Custodian", "Sandy, UT", "Clean classrooms.", False, ""),
    ("Dispatcher", "Denver, CO", "Route technicians.", False, "Dispatch & Scheduling"),
    ("Warehouse Inventory Clerk", "Salt Lake City, UT", "Count stock.", False, ""),
]


def selftest() -> int:
    bad = 0
    for title, loc, body, exp, exp_track in SELFTEST:
        j = score_job(Job(job_title=title, location=loc, summary=body))
        got = keep(j)
        ok = got == exp and (not exp or j.track == exp_track)
        bad += not ok
        print(f"{'ok ' if ok else 'XX '} keep={got!s:5} score={j.score:>3} "
              f"{(j.track or j.matched_terms)[:34]:<34} {j.area or '-':<17} {title}")
    print(f"\n{len(SELFTEST) - bad}/{len(SELFTEST)} as expected")
    return bad


# ============================================================================
# CLI
# ============================================================================

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Salt Lake–area step-up job scanner")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--sources", help="comma list: " + ",".join(SOURCES))
    ap.add_argument("--list-sources", action="store_true")
    ap.add_argument("--audit", action="store_true", help="run all sources, report yield, write nothing")
    ap.add_argument("--check", action="store_true", help="dry run: list requests only")
    ap.add_argument("--import", dest="imports", nargs="+", default=[])
    ap.add_argument("--merge-into")
    ap.add_argument("--rescore")
    ap.add_argument("--min-score", type=int, default=MIN_SCORE)
    ap.add_argument("--out", default=DEFAULT_CSV)
    ap.add_argument("--xlsx", default=DEFAULT_XLSX)
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)

    if a.selftest:
        return 1 if selftest() else 0
    if a.list_sources:
        for k, (label, _) in SOURCES.items():
            print(f"  {k:<9} {label}")
        return 0
    if a.rescore:
        jobs, stats = finalize(read_csv_jobs(a.rescore), a.min_score)
        out = a.out if a.out != DEFAULT_CSV else a.rescore.replace(".csv", "_rescored.csv")
        write_csv(jobs, out)
        write_xlsx(jobs, os.path.splitext(out)[0] + ".xlsx", stats)
        write_excluded(os.path.splitext(out)[0] + "_excluded.csv")
        print_summary(jobs, stats, [], {})
        print(f"\nWrote {out}", file=sys.stderr)
        return 0

    names = list(SOURCES) if (a.all or a.audit) else (
        [s.strip() for s in a.sources.split(",")] if a.sources else [])
    bad = [n for n in names if n not in SOURCES]
    if bad:
        ap.error(f"unknown source(s): {bad}")
    if not names and not a.imports:
        ap.error("choose --all, --sources, --import, --rescore or --selftest")

    jobs, stats, notes, yields = run(names, dry_run=a.check, verbose=not a.quiet,
                                     min_score=a.min_score, imports=a.imports)
    if a.check or a.audit:
        print_summary(jobs, stats, notes, yields)
        return 0
    if a.merge_into and os.path.exists(a.merge_into):
        existing = read_csv_jobs(a.merge_into)
        excluded_this_run = list(LAST_EXCLUDED)
        jobs, _ = finalize(existing + jobs, a.min_score)
        LAST_EXCLUDED[:] = excluded_this_run + LAST_EXCLUDED
        print(f"\nMerged with {len(existing)} existing -> {len(jobs)} total", file=sys.stderr)
        a.out, a.xlsx = a.merge_into, os.path.splitext(a.merge_into)[0] + ".xlsx"
    write_csv(jobs, a.out)
    write_xlsx(jobs, a.xlsx, stats, notes)
    write_excluded(os.path.splitext(a.out)[0] + "_excluded.csv")
    print_summary(jobs, stats, notes, yields)
    print(f"\nWrote {len(jobs)} postings -> {a.out}\nWrote workbook          -> {a.xlsx}"
          f"\nWrote excluded list     -> {os.path.splitext(a.out)[0]}_excluded.csv"
          f"\n\nNext: python build_slc_report.py {a.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
