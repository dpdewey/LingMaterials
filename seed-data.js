/* =========================================================
   Seed data — realistic sample entries that populate
   the archive on first load.
   ========================================================= */

(function () {
  'use strict';

  function svgImage(content) {
    return 'data:image/svg+xml;utf8,' + encodeURIComponent(content);
  }

  // 1. Corpus / data viz
  const IMG_CORPUS = svgImage(`
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="400" height="400">
  <defs>
    <linearGradient id="g1" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#002E5D"/>
      <stop offset="1" stop-color="#0062B8"/>
    </linearGradient>
  </defs>
  <rect width="400" height="400" fill="#001E3F"/>
  <g opacity="0.18" fill="#C5B783" font-family="Georgia" font-size="11" font-style="italic">
    <text x="20" y="30">the</text><text x="60" y="30">a</text><text x="80" y="30">of</text><text x="105" y="30">to</text>
    <text x="130" y="30">in</text><text x="155" y="30">that</text><text x="195" y="30">is</text>
    <text x="20" y="55">and</text><text x="55" y="55">for</text><text x="90" y="55">it</text><text x="115" y="55">with</text>
    <text x="160" y="55">as</text><text x="185" y="55">be</text>
    <text x="20" y="80">collocate</text><text x="90" y="80">concordance</text><text x="180" y="80">token</text>
  </g>
  <g fill="url(#g1)">
    <rect x="45" y="200" width="10" height="120"/>
    <rect x="75" y="160" width="10" height="160"/>
    <rect x="105" y="120" width="10" height="200"/>
    <rect x="135" y="100" width="10" height="220"/>
    <rect x="165" y="140" width="10" height="180"/>
    <rect x="195" y="180" width="10" height="140"/>
    <rect x="225" y="220" width="10" height="100"/>
    <rect x="255" y="170" width="10" height="150"/>
    <rect x="285" y="130" width="10" height="190"/>
    <rect x="315" y="190" width="10" height="130"/>
    <rect x="345" y="240" width="10" height="80"/>
  </g>
  <line x1="40" y1="320" x2="365" y2="320" stroke="#C5B783" stroke-width="1.5"/>
  <text x="200" y="365" text-anchor="middle" fill="#C5B783" font-family="Georgia" font-style="italic" font-size="14" opacity="0.9">frequency distribution</text>
</svg>`);

  // 2. Editing / manuscript
  const IMG_EDITING = svgImage(`
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="400" height="400">
  <rect width="400" height="400" fill="#FAF6EC"/>
  <rect x="80" y="40" width="240" height="320" fill="#fff" stroke="#C9C0A8"/>
  <g font-family="Georgia" font-size="9" fill="#3A4150">
    <text x="100" y="70">A monograph on the syntactic patterns of</text>
    <text x="100" y="84">academic English. <tspan fill="#8B2920" text-decoration="line-through">presents</tspan> <tspan fill="#2D5F3F">examines</tspan></text>
    <text x="100" y="98">the way scholarly writers construct argument</text>
    <text x="100" y="112">across disciplines. Drawing on <tspan fill="#8B2920" text-decoration="line-through">a large</tspan></text>
    <text x="100" y="126"><tspan fill="#2D5F3F">a multi-million-word</tspan> corpus, the study</text>
    <text x="100" y="140">tracks shifts in nominal density, modal verbs</text>
    <text x="100" y="154">and stance markers. It will appeal to</text>
    <text x="100" y="168">applied linguists, editors<tspan fill="#2D5F3F">,</tspan> and writing</text>
    <text x="100" y="182">teachers alike.</text>
    <text x="100" y="216" font-style="italic" fill="#0062B8">¶ Add a sentence on methodology here.</text>
    <text x="100" y="240" fill="#3A4150">Across thirty-two journals in the humanities</text>
    <text x="100" y="254">and social sciences, the authors find a</text>
    <text x="100" y="268">consistent <tspan fill="#8B2920" text-decoration="line-through">grow</tspan> <tspan fill="#2D5F3F">growth</tspan> in nominalization</text>
    <text x="100" y="282">over the past five decades. Particularly</text>
    <text x="100" y="296">notable is the rise of complex noun</text>
    <text x="100" y="310">phrases as subjects.</text>
  </g>
  <g stroke="#0062B8" stroke-width="1.5" fill="none">
    <path d="M 90 80 Q 75 88 90 100" />
    <path d="M 90 240 L 80 240"/>
    <circle cx="76" cy="240" r="2.5" fill="#0062B8"/>
  </g>
  <text x="200" y="385" text-anchor="middle" fill="#A89968" font-family="Georgia" font-style="italic" font-size="13">manuscript &mdash; second pass</text>
</svg>`);

  // 3. Study abroad / Mexico City
  const IMG_TRAVEL = svgImage(`
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="400" height="400">
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#1B4079"/>
      <stop offset="0.6" stop-color="#0062B8"/>
      <stop offset="1" stop-color="#C5B783"/>
    </linearGradient>
  </defs>
  <rect width="400" height="400" fill="url(#sky)"/>
  <path d="M 0 280 L 60 220 L 120 260 L 180 200 L 240 250 L 300 210 L 360 240 L 400 220 L 400 400 L 0 400 Z" fill="#001E3F" opacity="0.6"/>
  <path d="M 0 320 L 50 280 L 130 310 L 200 270 L 280 300 L 360 280 L 400 290 L 400 400 L 0 400 Z" fill="#001E3F" opacity="0.85"/>
  <g fill="#001E3F">
    <rect x="40" y="290" width="22" height="60"/>
    <rect x="68" y="270" width="18" height="80"/>
    <rect x="92" y="295" width="16" height="55"/>
    <polygon points="115,260 130,290 100,290"/>
    <rect x="118" y="290" width="18" height="60"/>
    <rect x="142" y="280" width="20" height="70"/>
    <rect x="168" y="295" width="14" height="55"/>
    <rect x="190" y="275" width="20" height="75"/>
    <polygon points="220,250 240,285 200,285"/>
    <rect x="218" y="285" width="20" height="65"/>
    <rect x="244" y="290" width="18" height="60"/>
    <rect x="268" y="280" width="16" height="70"/>
    <rect x="290" y="295" width="20" height="55"/>
    <rect x="316" y="285" width="14" height="65"/>
    <rect x="334" y="295" width="22" height="55"/>
  </g>
  <circle cx="320" cy="120" r="38" fill="#FAF6EC" opacity="0.85"/>
  <circle cx="320" cy="120" r="38" fill="none" stroke="#C5B783" stroke-width="1" opacity="0.5"/>
  <g stroke="#001E3F" stroke-width="1.5" fill="none" opacity="0.7">
    <path d="M 80 150 q 5 -5 10 0 q 5 -5 10 0"/>
    <path d="M 130 130 q 4 -4 8 0 q 4 -4 8 0"/>
    <path d="M 100 175 q 3 -3 6 0 q 3 -3 6 0"/>
  </g>
  <text x="200" y="385" text-anchor="middle" fill="#FAF6EC" font-family="Georgia" font-style="italic" font-size="14" opacity="0.9">study abroad &mdash; ciudad de méxico</text>
</svg>`);

  // 4. Classroom / TESOL
  const IMG_CLASSROOM = svgImage(`
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="400" height="400">
  <rect width="400" height="400" fill="#002E5D"/>
  <rect x="40" y="50" width="320" height="200" fill="#1B4079" stroke="#C5B783" stroke-width="3"/>
  <g fill="#FAF6EC" font-family="Georgia" font-style="italic">
    <text x="60" y="90" font-size="20">Today: pronunciation</text>
    <text x="60" y="125" font-size="14">/ʃ/  vs  /tʃ/  vs  /s/</text>
    <text x="60" y="155" font-size="14">she &nbsp;|&nbsp; cheese &nbsp;|&nbsp; sea</text>
    <text x="60" y="185" font-size="13" opacity="0.85">listen → repeat → record</text>
    <text x="60" y="215" font-size="13" opacity="0.85">practice with partner</text>
  </g>
  <g fill="#C5B783" opacity="0.9">
    <circle cx="80" cy="320" r="14"/>
    <circle cx="130" cy="305" r="14"/>
    <circle cx="180" cy="295" r="14"/>
    <circle cx="230" cy="295" r="14"/>
    <circle cx="280" cy="305" r="14"/>
    <circle cx="320" cy="320" r="14"/>
  </g>
  <g fill="#A89968">
    <rect x="74" y="332" width="12" height="18"/>
    <rect x="124" y="319" width="12" height="20"/>
    <rect x="174" y="309" width="12" height="22"/>
    <rect x="224" y="309" width="12" height="22"/>
    <rect x="274" y="319" width="12" height="20"/>
    <rect x="314" y="332" width="12" height="18"/>
  </g>
  <text x="200" y="385" text-anchor="middle" fill="#C5B783" font-family="Georgia" font-style="italic" font-size="13" opacity="0.9">elc &mdash; advanced speaking</text>
</svg>`);

  // 5. Conference poster
  const IMG_CONFERENCE = svgImage(`
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="400" height="400">
  <rect width="400" height="400" fill="#EFE8D7"/>
  <rect x="80" y="40" width="240" height="280" fill="#fff" stroke="#A89968" stroke-width="2"/>
  <rect x="195" y="320" width="10" height="50" fill="#A89968"/>
  <rect x="170" y="368" width="60" height="6" fill="#A89968"/>
  <rect x="100" y="60" width="200" height="22" fill="#002E5D"/>
  <text x="200" y="76" text-anchor="middle" fill="#fff" font-family="Georgia" font-size="12" font-weight="700">L2 PROSODY ACQUISITION</text>
  <g fill="#3A4150" font-family="Georgia" font-size="7">
    <text x="105" y="100">Sarah Johnson, Miguel Reyes</text>
    <text x="105" y="110">Brigham Young University · Department of Linguistics</text>
  </g>
  <rect x="100" y="125" width="90" height="50" fill="#FAF6EC" stroke="#C9C0A8"/>
  <g fill="#1A1D24" font-family="Georgia" font-size="6">
    <text x="105" y="138" font-weight="700">Background</text>
    <line x1="105" y1="142" x2="180" y2="142" stroke="#C9C0A8"/>
    <text x="105" y="152" opacity="0.7">Stress patterns in</text>
    <text x="105" y="160" opacity="0.7">advanced learners</text>
    <text x="105" y="168" opacity="0.7">of English (n=42)</text>
  </g>
  <rect x="200" y="125" width="100" height="50" fill="#FAF6EC" stroke="#C9C0A8"/>
  <g>
    <line x1="208" y1="170" x2="208" y2="135" stroke="#002E5D" stroke-width="2"/>
    <line x1="220" y1="170" x2="220" y2="148" stroke="#002E5D" stroke-width="2"/>
    <line x1="232" y1="170" x2="232" y2="142" stroke="#002E5D" stroke-width="2"/>
    <line x1="244" y1="170" x2="244" y2="155" stroke="#0062B8" stroke-width="2"/>
    <line x1="256" y1="170" x2="256" y2="138" stroke="#0062B8" stroke-width="2"/>
    <line x1="268" y1="170" x2="268" y2="160" stroke="#0062B8" stroke-width="2"/>
    <line x1="280" y1="170" x2="280" y2="145" stroke="#0062B8" stroke-width="2"/>
  </g>
  <rect x="100" y="185" width="200" height="50" fill="#FAF6EC" stroke="#C9C0A8"/>
  <g fill="#1A1D24" font-family="Georgia" font-size="6">
    <text x="105" y="198" font-weight="700">Methodology</text>
    <line x1="105" y1="202" x2="290" y2="202" stroke="#C9C0A8"/>
    <text x="105" y="212" opacity="0.7">Recordings analyzed in Praat. F0 contour</text>
    <text x="105" y="220" opacity="0.7">extraction across 240 utterances. Mixed-</text>
    <text x="105" y="228" opacity="0.7">effects model with random slopes by speaker.</text>
  </g>
  <rect x="100" y="245" width="200" height="55" fill="#002E5D"/>
  <g fill="#FAF6EC" font-family="Georgia" font-size="7">
    <text x="105" y="260" font-weight="700">FINDINGS</text>
    <line x1="105" y1="264" x2="290" y2="264" stroke="#C5B783"/>
    <text x="105" y="276" opacity="0.95">Learners with 18+ months of immersion</text>
    <text x="105" y="284" opacity="0.95">show native-like nuclear stress placement</text>
    <text x="105" y="292" opacity="0.95">in 73% of contexts &mdash; a significant gain.</text>
  </g>
  <text x="200" y="345" text-anchor="middle" fill="#A89968" font-family="Georgia" font-style="italic" font-size="11">poster session · LSA 2026</text>
</svg>`);

  // 6. Bookshelf
  const IMG_BOOKS = svgImage(`
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="400" height="400">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#1B4079"/>
      <stop offset="1" stop-color="#001E3F"/>
    </linearGradient>
  </defs>
  <rect width="400" height="400" fill="url(#bg)"/>
  <rect x="40" y="290" width="320" height="8" fill="#A89968"/>
  <g>
    <rect x="60" y="160" width="32" height="130" fill="#8B2920"/>
    <rect x="92" y="180" width="28" height="110" fill="#2D5F3F"/>
    <rect x="120" y="150" width="34" height="140" fill="#C5B783"/>
    <rect x="154" y="170" width="30" height="120" fill="#002E5D"/>
    <rect x="184" y="155" width="32" height="135" fill="#8B6914"/>
    <rect x="216" y="175" width="26" height="115" fill="#A89968"/>
    <rect x="242" y="160" width="30" height="130" fill="#8B2920"/>
    <rect x="272" y="170" width="34" height="120" fill="#2D5F3F"/>
    <rect x="306" y="180" width="28" height="110" fill="#002E5D"/>
  </g>
  <g fill="#FAF6EC" font-family="Georgia" font-size="6" opacity="0.75">
    <text x="76" y="225" transform="rotate(-90 76 225)" font-style="italic">Editing Studies</text>
    <text x="106" y="235" transform="rotate(-90 106 235)" font-style="italic">Stylistics</text>
    <text x="137" y="220" transform="rotate(-90 137 220)" font-style="italic" fill="#1A1D24">Vol. III &middot; 2026</text>
    <text x="169" y="230" transform="rotate(-90 169 230)" font-style="italic">Discourse</text>
    <text x="200" y="222" transform="rotate(-90 200 222)" font-style="italic">Pragmatics</text>
    <text x="229" y="232" transform="rotate(-90 229 232)" font-style="italic" fill="#1A1D24">Sociolinguistics</text>
    <text x="257" y="225" transform="rotate(-90 257 225)" font-style="italic">Phonology</text>
    <text x="289" y="230" transform="rotate(-90 289 230)" font-style="italic">Syntax</text>
    <text x="320" y="235" transform="rotate(-90 320 235)" font-style="italic">Semantics</text>
  </g>
  <g transform="translate(150 100) rotate(-3)">
    <rect x="0" y="0" width="100" height="60" fill="#FAF6EC" stroke="#C5B783"/>
    <line x1="50" y1="0" x2="50" y2="60" stroke="#C9C0A8"/>
    <g stroke="#3A4150" stroke-width="0.4" opacity="0.5">
      <line x1="6" y1="12" x2="44" y2="12"/>
      <line x1="6" y1="20" x2="44" y2="20"/>
      <line x1="6" y1="28" x2="40" y2="28"/>
      <line x1="6" y1="36" x2="44" y2="36"/>
      <line x1="6" y1="44" x2="38" y2="44"/>
      <line x1="56" y1="12" x2="94" y2="12"/>
      <line x1="56" y1="20" x2="94" y2="20"/>
      <line x1="56" y1="28" x2="90" y2="28"/>
      <line x1="56" y1="36" x2="94" y2="36"/>
      <line x1="56" y1="44" x2="86" y2="44"/>
    </g>
  </g>
  <text x="200" y="335" text-anchor="middle" fill="#C5B783" font-family="Georgia" font-style="italic" font-size="14">student publications &mdash; 2026</text>
</svg>`);

  // 7. Globe / languages
  const IMG_GLOBES = svgImage(`
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="400" height="400">
  <rect width="400" height="400" fill="#FAF6EC"/>
  <circle cx="200" cy="190" r="120" fill="#0062B8"/>
  <ellipse cx="200" cy="190" rx="120" ry="40" fill="none" stroke="#FAF6EC" stroke-width="0.8" opacity="0.4"/>
  <ellipse cx="200" cy="190" rx="120" ry="80" fill="none" stroke="#FAF6EC" stroke-width="0.8" opacity="0.4"/>
  <line x1="200" y1="70" x2="200" y2="310" stroke="#FAF6EC" stroke-width="0.8" opacity="0.4"/>
  <g fill="#C5B783" opacity="0.95">
    <path d="M 130 140 Q 140 130 165 135 Q 175 150 170 175 Q 150 180 135 165 Z"/>
    <path d="M 175 195 Q 185 200 195 215 Q 200 230 192 245 Q 178 240 172 220 Z"/>
    <path d="M 215 130 Q 240 125 260 140 Q 270 165 255 180 Q 235 175 220 160 Z"/>
    <path d="M 245 195 Q 275 200 285 220 Q 280 245 260 250 Q 240 230 240 210 Z"/>
    <path d="M 285 145 Q 305 155 300 175 Q 290 180 280 170 Z"/>
  </g>
  <g font-family="Georgia" font-style="italic" fill="#001E3F">
    <text x="40" y="60" font-size="14">español</text>
    <text x="60" y="350" font-size="14">中文</text>
    <text x="290" y="60" font-size="14">العربية</text>
    <text x="320" y="350" font-size="14">português</text>
    <text x="35" y="200" font-size="13">français</text>
    <text x="320" y="200" font-size="13">한국어</text>
    <text x="155" y="40" font-size="12">日本語</text>
    <text x="200" y="380" font-size="12">tiếng việt</text>
  </g>
  <text x="200" y="195" text-anchor="middle" fill="#FAF6EC" font-family="Georgia" font-style="italic" font-size="18" font-weight="700" opacity="0.95">English</text>
  <text x="200" y="215" text-anchor="middle" fill="#FAF6EC" font-family="Georgia" font-style="italic" font-size="11" opacity="0.7">for speakers of other languages</text>
</svg>`);

  // 8. Typewriter / editing
  const IMG_TYPEWRITER = svgImage(`
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="400" height="400">
  <rect width="400" height="400" fill="#001E3F"/>
  <g opacity="0.07" fill="#C5B783" font-family="Georgia" font-size="14">
    <text x="20" y="30">a a a a a a a a a a a a a a</text>
    <text x="20" y="50">b b b b b b b b b b b b b b</text>
    <text x="20" y="70">c c c c c c c c c c c c c c</text>
  </g>
  <rect x="80" y="180" width="240" height="120" fill="#1A1D24" stroke="#C5B783" stroke-width="2" rx="4"/>
  <rect x="100" y="200" width="200" height="60" fill="#FAF6EC"/>
  <g fill="#1A1D24" font-family="Georgia" font-size="7">
    <text x="110" y="215">A study of editorial practice in</text>
    <text x="110" y="225">academic publishing &mdash; the long</text>
    <text x="110" y="235">labor of getting something right.</text>
    <text x="110" y="248" font-style="italic">— students of EngL 423</text>
  </g>
  <g fill="#C5B783">
    <circle cx="115" cy="278" r="6"/>
    <circle cx="135" cy="278" r="6"/>
    <circle cx="155" cy="278" r="6"/>
    <circle cx="175" cy="278" r="6"/>
    <circle cx="195" cy="278" r="6"/>
    <circle cx="215" cy="278" r="6"/>
    <circle cx="235" cy="278" r="6"/>
    <circle cx="255" cy="278" r="6"/>
    <circle cx="275" cy="278" r="6"/>
    <circle cx="295" cy="278" r="6"/>
  </g>
  <rect x="110" y="160" width="180" height="22" fill="#1A1D24" stroke="#C5B783" rx="2"/>
  <text x="200" y="345" text-anchor="middle" fill="#C5B783" font-family="Georgia" font-style="italic" font-size="14" opacity="0.9">editing practicum</text>
</svg>`);

  const SEED_ENTRIES = [
    {
      id: 'seed_corpus_l2',
      mentor: 'Dr. Mark Davies',
      venueType: 'Research Project',
      venue: 'Stance and engagement in L2 academic writing',
      discipline: 'Linguistics',
      term: 'Fall 2025 – Winter 2026',
      students: ['Sarah Johnson', 'Miguel Reyes', 'Elena Park', 'James Chen'],
      accomplishments:
        'Four undergraduates completed independent corpus analyses of stance markers in graduate-level student writing. Sarah Johnson and Miguel Reyes co-authored a paper accepted at the Linguistic Society of America 2026 annual meeting. Elena Park won the Humanities Undergraduate Research Award for her work on hedging across disciplines. All four learned to use the BYU corpus infrastructure, ran their own queries, and presented findings at the BYU Annual Linguistics Symposium.',
      notes:
        'Watching Sarah present at LSA was one of the high points of my year. She walked into that room nervous about presenting to senior scholars and walked out a colleague, fielding questions with the kind of poise I rarely see even in graduate students. The four of them built real friendships over those late nights in the corpus lab — the kind that outlast a semester. Miguel told me he had never imagined himself as a researcher before this; now he is applying to PhD programs. That is the work, right there.',
      image: null,
      imageName: 'corpus_distribution.svg',
      createdAt: '2026-04-12T15:30:00.000Z'
    },
    {
      id: 'seed_mexico_studyabroad',
      mentor: 'Dr. Lynn Henrichsen',
      venueType: 'Study Abroad',
      venue: 'TESOL methods in Mexico City',
      discipline: 'TESOL',
      term: 'Summer 2025',
      students: [
        'Hannah Whitmore', 'Tyler Brockbank', 'Maria González', 'Joseph Ngata',
        'Elise Tanner', 'Dallin Park', 'Rachel Ko', 'Brigham Hall', 'Paige Sorensen'
      ],
      accomplishments:
        'Nine students taught alongside teachers in three Mexico City secondary schools, completing more than 200 supervised teaching hours. Each student designed and taught a thematic unit on a topic chosen with their host teacher. Tyler Brockbank and Joseph Ngata produced lesson-plan portfolios that the host school adopted into its standing curriculum. Two students earned their TESOL certificates. All nine improved their Spanish enough to coordinate parent-teacher communication directly.',
      notes:
        'I have led this trip seven times. Every time, something cracks open in students that no classroom can produce on its own. This year, watching Hannah teach a poetry lesson to a room of teenagers in her second language — using contrastive stress to explain English meter, of all things — I had to step out into the hallway. Joseph stayed in touch with his host teacher all year and is going back this summer. The work in Mexico City reshapes how these students think about language, about teaching, and about what they can do.',
      image: null,
      imageName: 'mexico_city.svg',
      createdAt: '2026-03-08T10:15:00.000Z'
    },
    {
      id: 'seed_editing_practicum',
      mentor: 'Dr. Daniel Adams',
      venueType: 'Editing Practicum',
      venue: 'Schreiner Press undergraduate editing internship',
      discipline: 'Editing & Publishing',
      term: 'Winter 2026',
      students: [
        'Caroline Ashby', 'Nathaniel Park', 'Olivia Chen',
        'Marcus Liu', 'Sophie Andersen', 'Daniel Reyes'
      ],
      accomplishments:
        'Six students worked through every stage of producing a peer-reviewed scholarly volume — from substantive editing through copyediting, typesetting, and proofing. The completed volume, an edited collection on the rhetoric of climate communication, was sent to the press and is forthcoming this fall. Caroline Ashby led the indexing team. Nathaniel Park and Olivia Chen designed the interior typography and managed the InDesign master files. Two students received offers from academic presses for postgraduate positions before graduation.',
      notes:
        'Editing teaches patience the way few other disciplines do. You cannot rush a manuscript into being a book. What I am proud of this term is how seriously these six took the work — checking every reference, every quotation, twice. Caroline caught a cited statistic that turned out to be wrong in the original journal article, ten years uncontested. Olivia rebuilt the running heads from scratch when the originals would not align. The book is real because they made it real, page by page.',
      image: null,
      imageName: 'editing_practicum.svg',
      createdAt: '2026-04-22T14:45:00.000Z'
    },
    {
      id: 'seed_elc_speaking',
      mentor: 'Dr. Norman Evans',
      venueType: 'TESOL Practicum',
      venue: 'English Language Center — advanced speaking course',
      discipline: 'TESOL',
      term: 'Winter 2026',
      students: ['Jenna Morton', 'Kavita Shah', 'Alex Robinson', 'Brooke Hyer'],
      accomplishments:
        'Four MA TESOL students designed and taught a pronunciation-focused speaking course for advanced ELC learners. They built a curriculum around prosody, connected speech, and discourse-level intonation — areas often underserved at the advanced level. Jenna Morton produced shadowing materials that the ELC has adopted into its permanent curriculum bank. Alex Robinson is presenting the curricular design at TESOL International this spring. Course evaluations from learners were the highest in the program for the term.',
      notes:
        'These four are the kind of teachers I wish I had been when I started. They came in with theories of language pedagogy and let those theories meet real learners — students from twelve countries, all with their own histories of why they were sitting in that classroom. By week four they had stopped quoting the textbooks and started teaching what was in front of them. Kavita gave a debrief one Friday afternoon that made me realize she understands learner identity in a way I am still working toward.',
      image: null,
      imageName: 'elc_classroom.svg',
      createdAt: '2026-04-25T09:00:00.000Z'
    },
    {
      id: 'seed_lsa_poster',
      mentor: 'Dr. Earl K. Brown',
      venueType: 'Conference / Presentation',
      venue: 'L2 prosody acquisition — LSA 2026 poster session',
      discipline: 'Linguistics',
      term: 'Winter 2026',
      students: ['Sarah Johnson', 'Miguel Reyes'],
      accomplishments:
        'Two undergraduate students presented original research at the Linguistic Society of America annual meeting. Their poster on nuclear stress placement in advanced L2 English speakers drew sustained engagement and resulted in a follow-up invitation to submit to the Journal of Second Language Pronunciation. Sarah and Miguel handled all stages independently — IRB, recruitment, recording, Praat analysis, statistics in R, and design.',
      notes:
        'There is a moment at every conference poster session when an undergraduate realizes a senior scholar is taking them seriously. I watched Sarah hit that moment at about minute twelve, when a phonetician from Edinburgh started arguing with her about her statistical model and she argued back. Miguel kept his cool when a methodological challenge came in and produced exactly the right counterexample from his data. The two of them flew home different from how they flew out.',
      image: null,
      imageName: 'lsa_poster.svg',
      createdAt: '2026-01-12T17:20:00.000Z'
    },
    {
      id: 'seed_thesis_corpus',
      mentor: 'Dr. Cynthia Hallen',
      venueType: 'Thesis / Capstone',
      venue: 'Lexicographic patterns in early modern American English',
      discipline: 'Applied English Linguistics',
      term: '2025–2026 academic year',
      students: ['Rebecca Tanaka'],
      accomplishments:
        'Rebecca Tanaka completed an honors thesis on the lexicographic conventions of early American dictionaries, focusing on the period 1790–1830. Her work won the Department of Linguistics Outstanding Undergraduate Thesis award. She has been accepted into the doctoral program in English language at the University of Edinburgh with full funding. A revised chapter is under review at a major journal in historical linguistics.',
      notes:
        'Rebecca came into my office two years ago with a question about an entry in Webster\'s 1828 dictionary. I sent her to special collections to look at original printings and she did not come back for three days. What she produced this year is the kind of thesis that some of my graduate students do not write. She has the eye for detail of a textual editor and the patience of a lexicographer. I will miss her terribly. Edinburgh is lucky.',
      image: null,
      imageName: 'lexicography.svg',
      createdAt: '2026-04-04T13:00:00.000Z'
    },
    {
      id: 'seed_journal_publication',
      mentor: 'Dr. Wendy Baker Smemoe',
      venueType: 'Publication',
      venue: 'Schwa: Linguistics Undergraduate Journal — Volume XIV',
      discipline: 'Linguistics',
      term: '2025–2026',
      students: [
        'Brigham Daniels', 'Chloe Park', 'Tyler Mendoza',
        'Ava Christensen', 'Jonathan Reeves', 'Sophie Lin',
        'Marcus Brennan', 'Hannah Yoo'
      ],
      accomplishments:
        'Eight undergraduate editors produced the fourteenth volume of Schwa, the department\'s peer-reviewed undergraduate linguistics journal. The volume contains seven articles spanning phonology, sociolinguistics, syntax, and computational linguistics — the most submissions in the journal\'s history. Chloe Park served as editor-in-chief and led the team through a complete redesign of the journal\'s typographic identity. The volume is available in print and as an open-access PDF in BYU\'s ScholarsArchive.',
      notes:
        'Schwa is one of those low-key wonders of the department that students mostly run themselves. My job, mostly, is to stay out of their way and answer questions when asked. What Chloe and her team accomplished this year is genuinely impressive — they raised the editorial standards, expanded the call for submissions to neighboring institutions, and produced a beautifully typeset volume. I tell them every year that this is the closest they will come, as undergraduates, to running a real scholarly publication. They believed me this year.',
      image: null,
      imageName: 'schwa_journal.svg',
      createdAt: '2026-04-18T11:30:00.000Z'
    },
    {
      id: 'seed_elc_diversity',
      mentor: 'Dr. K. James Hartshorn',
      venueType: 'Course',
      venue: 'Ling 377: Methods of teaching English to speakers of other languages',
      discipline: 'TESOL',
      term: 'Fall 2025',
      students: [
        'Bryan Christensen', 'Lisette Marin', 'Jorge Mendez', 'Emma Thompson',
        'Kaylee Walker', 'Devon Park', 'Ashlyn Reeves', 'Nathan Goh',
        'Lauren Tanner', 'Pedro Silva', 'Ria Patel', 'Elliot Wong',
        'Sienna Choi', 'Marshall Ng'
      ],
      accomplishments:
        'Fourteen undergraduates completed supervised teaching observations and a culminating teaching demonstration at the BYU English Language Center. Eleven students continued into ELC tutoring positions for the following term. Two students presented their lesson designs at the BYU Linguistics Symposium. The course also produced a shared resource bank of reflective teaching journals that will inform next year\'s offering.',
      notes:
        'Every fall, this course is where I get to watch students discover that teaching is harder than they thought, and also more wonderful. Lisette taught a lesson on pragmatic markers that I am going to steal for my own classes. Pedro stayed after his demo to talk with his learners for half an hour. Ria turned in a reflective journal that I have been thinking about for weeks. I keep teaching this course because it is where the next generation of language teachers becomes itself.',
      image: null,
      imageName: 'languages_globe.svg',
      createdAt: '2025-12-15T16:00:00.000Z'
    }
  ];

  window.SEED_ENTRIES = SEED_ENTRIES;

})();
