LingJobs web pages — for hosting on GitHub Pages (or any web host)
====================================================================

WHAT'S HERE
  index.html          Jobs for Linguists (the main report)
  sample-jobs.html    Sample Jobs & top sites
  program-cards.html  Program cards
  img/                the charts and word clouds
  pdf/                PDF versions to link to
Upload everything in this folder, keeping the folder structure. Each new
report rebuilds this folder; upload it again to update the live pages.

PUT IT ON GITHUB PAGES (one time)
  1. On github.com, create a repository, e.g. "lingjobs" (Public).
  2. Add file → Upload files → drag in everything from this folder → Commit.
  3. Settings → Pages → Source: "Deploy from a branch", Branch: main, Folder: / (root) → Save.
  4. After a minute the pages are at  https://YOUR-GITHUB-NAME.github.io/lingjobs/
     (index.html is the main report; add sample-jobs.html or program-cards.html for the others).
  To update: Add file → Upload files → drag in the new folder contents → Commit.

SHOW IT IN BRIGHTSPOT
  Use an iframe (embed) module on each page with the page's GitHub address.
  If the module asks for HTML, use:

  <iframe src="https://YOUR-GITHUB-NAME.github.io/lingjobs/" title="Jobs for Linguists"
          style="width:100%;height:9500px;border:0" loading="lazy"></iframe>

  An iframe doesn't grow to fit its page, so set the height a little taller than
  the page. Heights measured for this build:
  index.html
    1200px wide → 7,793px tall
    900px wide → 7,925px tall
    600px wide → 9,035px tall
    380px wide → 12,469px tall
  sample-jobs.html
    1200px wide → 7,638px tall
    900px wide → 8,224px tall
    600px wide → 12,314px tall
    380px wide → 15,984px tall
  program-cards.html
    1200px wide → 5,436px tall
    900px wide → 5,436px tall
    600px wide → 5,436px tall
    380px wide → 5,436px tall

  The pages also announce their height to the host page (a postMessage named
  "lingjobsHeight"), so if Brightspot ever allows a small script, the frame can
  size itself:

  <script>addEventListener("message",function(e){if(e.data&&e.data.lingjobsHeight){
    document.querySelectorAll('iframe[src*="github.io/lingjobs"]').forEach(function(f){
      if(f.contentWindow===e.source)f.style.height=(e.data.lingjobsHeight+20)+"px";});}});</script>

THE PAGE LINKS
  The links at the top of each page (Jobs for Linguists · Sample Jobs · Program
  Cards) go to the other pages in this same folder. To send them somewhere else
  (e.g. ling.byu.edu pages), put full web addresses in PAGE_LINKS in
  build_report_v2.py; full addresses open in the whole window.

SEARCH ENGINES
  The pages carry a "noindex" tag so Google lists the ling.byu.edu pages, not
  this copy. Set WEB_NOINDEX = False in build_report_v2.py to change that.
