#!/usr/bin/env python3
"""
slcjobs_gui.py — window app for SLC Step-Up Jobs.

A point-and-click front end for slcjobs.py and build_slc_report.py, laid out
like the LingJobs window. It does not reimplement any searching or report
logic: it imports those two files and calls the same functions the command
line uses, so the three always stay in sync. Tkinter ships with Python
(including Anaconda), so there is nothing extra to install for the window.

HOW TO LAUNCH
-------------
Keep this file in the SAME FOLDER as slcjobs.py and build_slc_report.py, then
  * double-click run_slcjobs_mac.command (Mac) or run_slcjobs_windows.bat, or
  * from a terminal:  python slcjobs_gui.py

TABS
----
  1  Collect jobs        tick sources and settings, press Start; the results
                         and (optionally) the full report are written to the
                         folder you choose
  2  Add downloaded files  Indeed / LinkedIn / job-board exports, merged into
                         the same results file
  3  Build report        rebuild the report from any SLCJobs.csv
  4  API keys            paste Adzuna and USAJobs keys, or copy them from
                         another tool's keys file
  5  Instructions        what each step does, and what to do by hand
"""
from __future__ import annotations

import contextlib
import json
import os
import queue
import subprocess
import sys
import threading
import traceback

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, scrolledtext, ttk
except Exception:
    sys.stderr.write("\nThis program needs Tkinter, which normally ships with Python.\n"
                     "On Anaconda run:  conda install tk\n\n")
    raise

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
try:
    import slcjobs as J
except Exception:
    root = tk.Tk(); root.withdraw()
    messagebox.showerror("SLC Step-Up Jobs",
                         "Could not load slcjobs.py. Keep slcjobs_gui.py in the same folder "
                         "as slcjobs.py.\n\n" + traceback.format_exc(limit=2))
    raise SystemExit(1)

APP_TITLE = "SLC Step-Up Jobs"
KEYS_FILE = os.path.join(HERE, "slcjobs_keys.json")

INSTRUCTIONS = """\
WHAT THIS DOES
Searches job boards for openings in the Salt Lake area that fit one person:
an experienced, very reliable custodian moving into seated, bench and desk
work (dispatch, security desk, purchasing, pre-press, engraving, embroidery,
dental and optical labs, electronics repair, library technical services,
digitization, makerspaces, CAD). Hands-on cleaning, heavy lifting and stair-
climbing jobs are left out.

FIRST TIME
1. API keys tab: paste the Adzuna and USAJobs keys (or "Copy keys from another
   file" and pick lingjobs_keys.json or gerrusjobs_keys.json). Save.
   Free keys: developer.adzuna.com and developer.usajobs.gov.
2. Collect jobs tab: leave the settings as they are and press "Check sources".
   This shows which sources work without saving anything. Adzuna and USAJobs
   should each fetch a few hundred postings.
3. Press "Start". It takes 5-10 minutes because it waits politely between
   requests. When it finishes, the results folder holds:
     SLCJobs.csv            every kept posting, one per row, with the ad's link
     SLCJobs.xlsx           the same, plus one tab per career track
     SLCJobs_excluded.csv   every posting left out, and why
     report/                the full report (if "Build the report" is ticked)

THE REPORT (report folder)
  slc_jobs_report.html   interactive page: numbers, takeaways, charts, track
                         cards, and a searchable list of every posting
  track_cards.html/.pdf  one card per career track
  apply_this_week.html/.pdf  one-page handout of the best current postings
  SLC_jobs_report.docx   Word version
  chart_*.png, cloud_*.png  the charts and word clouds on their own
Word clouds need "pip install wordcloud"; the Word file needs "pip install
python-docx"; PDFs need "pip install playwright" then
"python -m playwright install chromium". Anything missing is skipped.

EVERY WEEK
Tick "Add to existing results" and press Start. New postings are added to
SLCJobs.csv without duplicates.

SEARCHING WITH CLAUDE IN CHROME
SLCJobs_browser_search.md (in this folder) tells Claude in Chrome how to search the sites this
program can't read and save a CSV. Attach it in the Claude side panel in
Chrome and say "Run the browser search". Then add the CSV on the
"Add downloaded files" tab.

SEARCHING BY HAND
Some of the best sources have no feed the program can read: Utah's state job
board (jobs.utah.gov), Intermountain Health, the school districts, FamilySearch,
Indeed and LinkedIn. The "Search by hand" tab in SLCJobs.xlsx lists them with
what to look for. On Indeed or LinkedIn, export or copy results into a
spreadsheet (title, company, location, link, description) and add the file on
the "Add downloaded files" tab; it is scored and merged like everything else.

READING THE RESULTS
  field           the career track
  physical_fit    "Good fit"; "Good fit — check physical section" (the ad lists
                  lifting or stairs, often copied boilerplate: ask HR); or
                  "Caution" (ask about walking, standing and lifting)
  pay_hourly_est  pay converted to dollars per hour, where the ad lists pay
  score           how well the posting fits; higher is better
"""


class QueueWriter:
    """File-like object that sends text to the log window."""
    def __init__(self, q):
        self.q = q

    def write(self, s):
        if s:
            self.q.put(s)

    def flush(self):
        pass


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("980x720")
        self.minsize(820, 560)
        self.q: queue.Queue = queue.Queue()
        self.calls: queue.Queue = queue.Queue()   # UI updates from the worker thread
        self.busy = False
        self.import_files: list[str] = []

        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Head.TLabel", font=("Helvetica", 16, "bold"), foreground="#1F4E79")
        style.configure("Accent.TButton", font=("Helvetica", 11, "bold"))

        ttk.Label(self, text=APP_TITLE, style="Head.TLabel").pack(anchor="w", padx=14, pady=(12, 0))
        ttk.Label(self, text="Salt Lake–area openings for seated, bench and desk work",
                  foreground="#5d636b").pack(anchor="w", padx=14, pady=(0, 6))

        paned = ttk.PanedWindow(self, orient="vertical")
        paned.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.nb = ttk.Notebook(paned)
        paned.add(self.nb, weight=3)

        logf = ttk.LabelFrame(paned, text="Progress")
        paned.add(logf, weight=2)
        self.log_box = scrolledtext.ScrolledText(logf, height=12, font=("Menlo", 11), wrap="word")
        self.log_box.pack(fill="both", expand=True, padx=4, pady=4)
        self.log_box.configure(state="disabled")

        self._tab_collect()
        self._tab_import()
        self._tab_report()
        self._tab_keys()
        self._tab_help()
        self.after(100, self._drain)

    # ------------------------------------------------------------------ log
    def log(self, msg: str) -> None:
        self.q.put(msg if msg.endswith("\n") else msg + "\n")

    def _drain(self):
        try:
            while True:
                s = self.q.get_nowait()
                self.log_box.configure(state="normal")
                self.log_box.insert("end", s)
                self.log_box.see("end")
                self.log_box.configure(state="disabled")
        except queue.Empty:
            pass
        try:
            while True:
                self.calls.get_nowait()()
        except queue.Empty:
            pass
        self.after(100, self._drain)

    def _worker(self, fn, done_msg=None, on_done=None):
        if self.busy:
            messagebox.showinfo(APP_TITLE, "Please wait for the current task to finish.")
            return
        self.busy = True
        self._set_buttons("disabled")

        def target():
            w = QueueWriter(self.q)
            result = None
            try:
                with contextlib.redirect_stderr(w), contextlib.redirect_stdout(w):
                    result = fn()
                if done_msg:
                    self.log("\n" + done_msg)
            except Exception:
                self.log("\nSomething went wrong:\n" + traceback.format_exc())
            finally:
                self.busy = False
                # Tk must only be touched from the main thread: queue the updates
                self.calls.put(lambda: self._set_buttons("normal"))
                if on_done:
                    self.calls.put(lambda: on_done(result))
        threading.Thread(target=target, daemon=True).start()

    def _set_buttons(self, state):
        for b in (self.btn_start, self.btn_audit, self.btn_merge_files, self.btn_build):
            b.configure(state=state)

    # ------------------------------------------------------------ tab 1
    def _tab_collect(self):
        f = ttk.Frame(self.nb, padding=10)
        self.nb.add(f, text="1  Collect jobs")
        top = ttk.Frame(f); top.pack(fill="x")

        src = ttk.LabelFrame(top, text="Where to search", padding=8)
        src.pack(side="left", fill="both", expand=True, padx=(0, 8))
        self.src_vars = {}
        for k, (label, _) in J.SOURCES.items():
            v = tk.BooleanVar(value=True)
            ttk.Checkbutton(src, text=label, variable=v).pack(anchor="w")
            self.src_vars[k] = v

        who = ttk.LabelFrame(top, text="What kinds of jobs", padding=8)
        who.pack(side="left", fill="both", expand=True, padx=(0, 8))
        self.v_phys = tk.BooleanVar(value=J.PHYSICAL_LIMITS)
        self.v_creative = tk.BooleanVar(value=J.INCLUDE_CREATIVE)
        self.v_stretch = tk.BooleanVar(value=J.INCLUDE_STRETCH)
        self.v_trades = tk.BooleanVar(value=J.INCLUDE_HANDS_ON_TRADES)
        ttk.Checkbutton(who, text="No heavy lifting or stairs", variable=self.v_phys).pack(anchor="w")
        ttk.Checkbutton(who, text="Creative, maker and bench jobs", variable=self.v_creative).pack(anchor="w")
        ttk.Checkbutton(who, text="CAD / UI design (6–12 months of skills first)",
                        variable=self.v_stretch).pack(anchor="w")
        ttk.Checkbutton(who, text="Hands-on maintenance trainee jobs", variable=self.v_trades).pack(anchor="w")
        row = ttk.Frame(who); row.pack(anchor="w", pady=(6, 0))
        ttk.Label(row, text="Flag lifting over").pack(side="left")
        self.v_lift = tk.StringVar(value=str(J.LIFT_LIMIT_LBS))
        ttk.Entry(row, textvariable=self.v_lift, width=5).pack(side="left", padx=4)
        ttk.Label(row, text="lbs").pack(side="left")
        row = ttk.Frame(who); row.pack(anchor="w", pady=(4, 0))
        ttk.Label(row, text="Hide jobs paying under $").pack(side="left")
        self.v_minhr = tk.StringVar(value=str(J.MIN_HOURLY or ""))
        ttk.Entry(row, textvariable=self.v_minhr, width=5).pack(side="left", padx=4)
        ttk.Label(row, text="/hr (blank = show all)").pack(side="left")

        area = ttk.LabelFrame(top, text="Area", padding=8)
        area.pack(side="left", fill="both", expand=True)
        self.area_vars = {}
        for county in J.REGION_TOWNS:
            v = tk.BooleanVar(value=county in J.REGIONS_ON)
            ttk.Checkbutton(area, text=county, variable=v).pack(anchor="w")
            self.area_vars[county] = v

        out = ttk.LabelFrame(f, text="Save results to", padding=8)
        out.pack(fill="x", pady=(10, 0))
        self.v_folder = tk.StringVar(value=HERE)
        ttk.Entry(out, textvariable=self.v_folder).pack(side="left", fill="x", expand=True)
        ttk.Button(out, text="Choose…", command=self._choose_folder).pack(side="left", padx=6)

        opts = ttk.Frame(f); opts.pack(fill="x", pady=(8, 0))
        self.v_merge = tk.BooleanVar(value=True)
        self.v_autoreport = tk.BooleanVar(value=True)
        ttk.Checkbutton(opts, text="Add to existing results (no duplicates)",
                        variable=self.v_merge).pack(side="left")
        ttk.Checkbutton(opts, text="Build the report when done",
                        variable=self.v_autoreport).pack(side="left", padx=16)

        btns = ttk.Frame(f); btns.pack(fill="x", pady=(10, 0))
        self.btn_start = ttk.Button(btns, text="Start", style="Accent.TButton", command=self.start)
        self.btn_start.pack(side="left")
        self.btn_audit = ttk.Button(btns, text="Check sources (saves nothing)", command=self.audit)
        self.btn_audit.pack(side="left", padx=8)
        ttk.Button(btns, text="Open results folder",
                   command=lambda: open_path(self.v_folder.get())).pack(side="left")

    def _choose_folder(self):
        d = filedialog.askdirectory(initialdir=self.v_folder.get() or HERE)
        if d:
            self.v_folder.set(d)

    def _apply_settings(self) -> bool:
        J.PHYSICAL_LIMITS = self.v_phys.get()
        J.INCLUDE_CREATIVE = self.v_creative.get()
        J.INCLUDE_STRETCH = self.v_stretch.get()
        J.INCLUDE_HANDS_ON_TRADES = self.v_trades.get()
        try:
            J.LIFT_LIMIT_LBS = int(self.v_lift.get() or 25)
            J.MIN_HOURLY = float(self.v_minhr.get()) if self.v_minhr.get().strip() else 0
        except ValueError:
            messagebox.showerror(APP_TITLE, "Lift limit and minimum pay must be numbers.")
            return False
        regions = [c for c, v in self.area_vars.items() if v.get()]
        if not regions:
            messagebox.showerror(APP_TITLE, "Tick at least one area.")
            return False
        J.set_regions(regions)
        return True

    def _paths(self):
        folder = self.v_folder.get() or HERE
        os.makedirs(folder, exist_ok=True)
        csv_path = os.path.join(folder, J.DEFAULT_CSV)
        return folder, csv_path, os.path.join(folder, J.DEFAULT_XLSX)

    def _selected_sources(self):
        names = [k for k, v in self.src_vars.items() if v.get()]
        if not names:
            messagebox.showerror(APP_TITLE, "Tick at least one source.")
        return names

    def audit(self):
        names = self._selected_sources()
        if not names or not self._apply_settings():
            return

        def job():
            jobs, stats, notes, yields = J.run(names, log=self.log)
            J.print_summary(jobs, stats, notes, yields)
        self._worker(job, "Check finished. Nothing was saved.")

    def start(self):
        names = self._selected_sources()
        if not names or not self._apply_settings():
            return
        folder, csv_path, xlsx_path = self._paths()
        merge, auto = self.v_merge.get(), self.v_autoreport.get()
        collected = self.v_collected.get().strip()

        def job():
            jobs, stats, notes, yields = J.run(names, log=self.log)
            jobs = self._save(jobs, stats, notes, csv_path, xlsx_path, merge)
            J.print_summary(jobs, stats, notes, yields)
            if auto:
                self._build(csv_path, collected)
            return csv_path
        self._worker(job, f"Done. Results are in {folder}",
                     on_done=lambda p: self.v_csv.set(p) if p else None)

    def _save(self, jobs, stats, notes, csv_path, xlsx_path, merge):
        if merge and os.path.exists(csv_path):
            existing = J.read_csv_jobs(csv_path)
            excluded = list(J.LAST_EXCLUDED)
            jobs, _ = J.finalize(existing + jobs, log=self.log)
            J.LAST_EXCLUDED[:] = excluded + J.LAST_EXCLUDED
            self.log(f"Merged with {len(existing)} earlier postings -> {len(jobs)} total")
        J.write_csv(jobs, csv_path)
        J.write_xlsx(jobs, xlsx_path, stats, notes)
        n_ex = J.write_excluded(os.path.splitext(csv_path)[0] + "_excluded.csv")
        self.log(f"Wrote {len(jobs)} postings -> {os.path.basename(csv_path)} and "
                 f"{os.path.basename(xlsx_path)}; {n_ex} excluded postings listed in "
                 f"{os.path.basename(os.path.splitext(csv_path)[0])}_excluded.csv")
        return jobs

    # ------------------------------------------------------------ tab 2
    def _tab_import(self):
        f = ttk.Frame(self.nb, padding=10)
        self.nb.add(f, text="2  Add downloaded files")
        ttk.Label(f, wraplength=880, justify="left", text=(
            "For sites the program can't search (Indeed, LinkedIn, jobs.utah.gov, employer sites): "
            "save the results as a CSV or Excel file with columns such as title, company, location, "
            "link and description. Add the files here; they are scored with the same rules and "
            "merged into the results file chosen on the Collect tab.")).pack(anchor="w")
        self.file_list = tk.Listbox(f, height=10)
        self.file_list.pack(fill="both", expand=True, pady=8)
        b = ttk.Frame(f); b.pack(fill="x")
        ttk.Button(b, text="Add files…", command=self._add_files).pack(side="left")
        ttk.Button(b, text="Remove selected", command=self._remove_file).pack(side="left", padx=6)
        self.btn_merge_files = ttk.Button(b, text="Score and merge into results",
                                          style="Accent.TButton", command=self.merge_files)
        self.btn_merge_files.pack(side="left", padx=6)

    def _add_files(self):
        for p in filedialog.askopenfilenames(filetypes=[("Spreadsheets", "*.csv *.xlsx *.xlsm"),
                                                        ("All files", "*.*")]):
            if p not in self.import_files:
                self.import_files.append(p)
                self.file_list.insert("end", p)

    def _remove_file(self):
        for i in reversed(self.file_list.curselection()):
            self.file_list.delete(i)
            del self.import_files[i]

    def merge_files(self):
        if not self.import_files:
            messagebox.showinfo(APP_TITLE, "Add at least one file first.")
            return
        if not self._apply_settings():
            return
        folder, csv_path, xlsx_path = self._paths()
        files = list(self.import_files)
        auto = self.v_autoreport.get()
        collected = self.v_collected.get().strip()

        def job():
            jobs, stats, notes, yields = J.run([], imports=files, log=self.log)
            jobs = self._save(jobs, stats, notes, csv_path, xlsx_path, merge=True)
            J.print_summary(jobs, stats, notes, yields)
            if auto:
                self._build(csv_path, collected)
            return csv_path
        self._worker(job, "Files merged.", on_done=lambda p: self.v_csv.set(p) if p else None)

    # ------------------------------------------------------------ tab 3
    def _tab_report(self):
        f = ttk.Frame(self.nb, padding=10)
        self.nb.add(f, text="3  Build report")
        ttk.Label(f, wraplength=880, justify="left", text=(
            "Builds the full report from a results file into a 'report' folder beside it: an "
            "interactive web page with a searchable list of every posting, track cards, a one-page "
            "'Apply this week' handout, a Word report, charts and word clouds.")).pack(anchor="w")
        row = ttk.Frame(f); row.pack(fill="x", pady=8)
        ttk.Label(row, text="Results file:").pack(side="left")
        self.v_csv = tk.StringVar(value=os.path.join(HERE, J.DEFAULT_CSV))
        ttk.Entry(row, textvariable=self.v_csv).pack(side="left", fill="x", expand=True, padx=6)
        ttk.Button(row, text="Choose…", command=self._choose_csv).pack(side="left")
        row = ttk.Frame(f); row.pack(fill="x")
        ttk.Label(row, text="Date label (optional):").pack(side="left")
        self.v_collected = tk.StringVar()
        ttk.Entry(row, textvariable=self.v_collected, width=24).pack(side="left", padx=6)
        b = ttk.Frame(f); b.pack(fill="x", pady=10)
        self.btn_build = ttk.Button(b, text="Build report", style="Accent.TButton", command=self.build)
        self.btn_build.pack(side="left")
        ttk.Button(b, text="Open report page", command=self._open_report).pack(side="left", padx=6)
        ttk.Button(b, text="Open report folder", command=lambda: open_path(
            os.path.join(os.path.dirname(self.v_csv.get()), "report"))).pack(side="left")

    def _choose_csv(self):
        p = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")],
                                       initialdir=os.path.dirname(self.v_csv.get()) or HERE)
        if p:
            self.v_csv.set(p)

    def _build(self, csv_path, collected=""):
        import build_slc_report as R
        self.log("\nBuilding the report…")
        out, files, notes = R.build(csv_path, collected, log=self.log)
        self.log(f"Report folder: {out}")
        return out

    def build(self):
        p = self.v_csv.get()
        if not os.path.exists(p):
            messagebox.showerror(APP_TITLE, f"Can't find {p}.\nCollect jobs first.")
            return
        collected = self.v_collected.get().strip()
        self._worker(lambda: self._build(p, collected), "Report built.")

    def _open_report(self):
        p = os.path.join(os.path.dirname(self.v_csv.get()), "report", "slc_jobs_report.html")
        if os.path.exists(p):
            open_path(p)
        else:
            messagebox.showinfo(APP_TITLE, "Build the report first.")

    # ------------------------------------------------------------ tab 4
    def _tab_keys(self):
        f = ttk.Frame(self.nb, padding=10)
        self.nb.add(f, text="4  API keys")
        ttk.Label(f, wraplength=880, justify="left", text=(
            "Adzuna and USAJobs do most of the searching and need free keys. Paste them here and "
            "press Save, or copy them from LingJobs or GerRusJobs (lingjobs_keys.json / "
            "gerrusjobs_keys.json). Get keys at developer.adzuna.com and developer.usajobs.gov.")
                  ).pack(anchor="w")
        keys = J.load_keys(log=lambda m: None)
        grid = ttk.Frame(f); grid.pack(anchor="w", pady=10)
        self.key_vars = {}
        for i, (k, label) in enumerate((("adzuna_app_id", "Adzuna Application ID"),
                                        ("adzuna_app_key", "Adzuna Application Key"),
                                        ("usajobs_api_key", "USAJobs API key"),
                                        ("usajobs_email", "USAJobs email (the one you registered)"))):
            ttk.Label(grid, text=label).grid(row=i, column=0, sticky="w", pady=3)
            v = tk.StringVar(value=keys.get(k, ""))
            ttk.Entry(grid, textvariable=v, width=52,
                      show="•" if "key" in k else "").grid(row=i, column=1, padx=8)
            self.key_vars[k] = v
        b = ttk.Frame(f); b.pack(anchor="w")
        ttk.Button(b, text="Save", style="Accent.TButton", command=self._save_keys).pack(side="left")
        ttk.Button(b, text="Copy keys from another file…", command=self._copy_keys).pack(side="left", padx=8)
        self.keys_status = ttk.Label(f, text="", foreground="#2E7D32")
        self.keys_status.pack(anchor="w", pady=6)

    def _save_keys(self):
        data = {"ADZUNA_APP_ID": self.key_vars["adzuna_app_id"].get().strip(),
                "ADZUNA_APP_KEY": self.key_vars["adzuna_app_key"].get().strip(),
                "USAJOBS_API_KEY": self.key_vars["usajobs_api_key"].get().strip(),
                "USAJOBS_EMAIL": self.key_vars["usajobs_email"].get().strip()}
        with open(KEYS_FILE, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
        self.keys_status.configure(text=f"Saved to {os.path.basename(KEYS_FILE)}.")

    def _copy_keys(self):
        p = filedialog.askopenfilename(filetypes=[("Keys file", "*.json")], initialdir=os.path.expanduser("~"))
        if not p:
            return
        try:
            raw = json.load(open(p, encoding="utf-8"))
        except (OSError, ValueError) as e:
            messagebox.showerror(APP_TITLE, f"Couldn't read that file:\n{e}")
            return
        import re
        flat = {re.sub(r"[^a-z]", "", k.lower()): v for k, v in J._flatten(raw).items() if v}
        found = 0
        for canon, aliases in J._KEY_ALIASES.items():
            if canon in self.key_vars:
                val = next((flat[a] for a in aliases if flat.get(a)), "")
                if val:
                    self.key_vars[canon].set(str(val)); found += 1
        self.keys_status.configure(text=f"Found {found} of 4 keys in {os.path.basename(p)}. "
                                        "Press Save to keep them.")

    # ------------------------------------------------------------ tab 5
    def _tab_help(self):
        f = ttk.Frame(self.nb, padding=10)
        self.nb.add(f, text="5  Instructions")
        t = scrolledtext.ScrolledText(f, wrap="word", font=("Helvetica", 12))
        t.pack(fill="both", expand=True)
        t.insert("1.0", INSTRUCTIONS)
        t.configure(state="disabled")


def open_path(p: str) -> None:
    if not os.path.exists(p):
        messagebox.showinfo(APP_TITLE, f"{p} doesn't exist yet.")
        return
    if sys.platform == "darwin":
        subprocess.Popen(["open", p])
    elif os.name == "nt":
        os.startfile(p)  # type: ignore[attr-defined]
    else:
        subprocess.Popen(["xdg-open", p])


if __name__ == "__main__":
    App().mainloop()
