/* =========================================================
   Student seed data — 6 realistic sample entries
   ========================================================= */
(function () {
  'use strict';

  window.STUDENT_SEED_ENTRIES = [
    {
      id: 'student_seed_001',
      type: 'student',
      studentName: 'Sarah Johnson',
      mentorName: 'Dr. Mark Davies',
      program: 'Linguistics BA',
      term: 'Fall 2025 – Winter 2026',
      venueType: 'Research Project',
      venueDesc: 'Stance and engagement in L2 academic writing',
      transformative: 'During our third meeting, Dr. Davies asked me a question I couldn\'t answer. Instead of filling the silence, he waited — for nearly a full minute. I finally said "I don\'t know," and he leaned forward and said that was the most important thing I\'d said all semester. He told me that the moment a researcher admits they don\'t know something is the moment the real research begins. I had spent two years at BYU pretending to know things so I wouldn\'t look foolish. That afternoon I stopped pretending. My work got better immediately, and so did I.',
      aimsResponses: [
        {
          aim: 'intellectual',
          promptKey: 'rigorous-standard',
          promptLabel: 'The Rigorous Standard',
          promptFull: 'Describe a moment when a mentor refused to let you settle for a "good enough" answer.',
          response: 'I turned in a literature review I was genuinely proud of. Dr. Davies read it quietly, then put it on the table and said: "This is good. But good is the enemy of important. What is the one question this review cannot yet answer?" I sat there for five minutes trying to think of something while he waited. When I finally found it, he said "That\'s your dissertation." He was right. I had been aiming for competence when I should have been aiming for contribution.'
        },
        {
          aim: 'service',
          promptKey: 'pivot',
          promptLabel: 'The Pivot',
          promptFull: 'Describe a specific conversation that fundamentally changed how you approached your career goals.',
          response: 'I told Dr. Davies I was thinking about going into industry after graduation — corpus work for a tech company. He didn\'t push back. He asked me one question: "What problem do you want to solve that only you can solve?" I didn\'t have an answer. But that question has stayed with me every day since. I\'m applying to PhD programs now. Not because he told me to — because he asked me the right question.'
        }
      ],
      image: null,
      createdAt: '2026-04-15T10:30:00.000Z'
    },
    {
      id: 'student_seed_002',
      type: 'student',
      studentName: 'Miguel Reyes',
      mentorName: 'Dr. Earl K. Brown',
      program: 'Linguistics BA',
      term: 'Winter 2026',
      venueType: 'Conference / Presentation',
      venueDesc: 'L2 prosody acquisition — LSA 2026 poster session',
      transformative: 'At the LSA poster session, a senior phonetician from Edinburgh began challenging our methodology. She was polite but pointed — and I could feel myself starting to fold. Dr. Brown was standing behind me. He didn\'t step in. He just made a small gesture with his hand, like: you have this. I took a breath and answered her. Not perfectly — but I answered. When she walked away, she said "good work." Dr. Brown later told me he had been ready to step in but decided I didn\'t need him to. That decision — to let me struggle and succeed on my own — was the most generous thing a teacher has ever done for me.',
      aimsResponses: [
        {
          aim: 'intellectual',
          promptKey: 'breakthrough',
          promptLabel: 'The Breakthrough',
          promptFull: 'Recall a moment when you felt a sudden "click" in your understanding or confidence.',
          response: 'We were running our mixed-effects model for the third time, still getting a singular fit warning. I was ready to give up and just report it as a limitation. Dr. Brown sat down next to me and said "What does that warning actually mean?" I explained it. He said "Right — so what are you going to do about it?" Over the next hour I figured it out myself, with him asking questions but never giving answers. By the end I understood the model in a way I never would have if he\'d just fixed it for me.'
        },
        {
          aim: 'character',
          promptKey: 'vulnerable-expert',
          promptLabel: 'The Vulnerable Expert',
          promptFull: 'Describe an instance where your mentor admitted a mistake or shared a personal setback.',
          response: 'Before LSA, I asked Dr. Brown if he was ever nervous presenting. He laughed and told me about his first conference poster — how he got a methodological question he couldn\'t answer, froze completely, and had to say "I don\'t know, I\'ll look into that." He had been embarrassed for weeks afterward. Then he said: "Now I consider it one of the best things that ever happened to me. That question sent me down a research path I\'m still on twenty years later." I thought about that the whole flight to the conference.'
        }
      ],
      image: null,
      createdAt: '2026-02-20T14:15:00.000Z'
    },
    {
      id: 'student_seed_003',
      type: 'student',
      studentName: 'Hannah Whitmore',
      mentorName: 'Dr. Lynn Henrichsen',
      program: 'TESOL MA',
      term: 'Summer 2025',
      venueType: 'Study Abroad',
      venueDesc: 'TESOL methods in Mexico City',
      transformative: 'I was teaching a poetry lesson to a group of Mexican teenagers — in my second language, about meter in their third language — and something went wrong with my plan around minute fifteen. I had nothing left on my cards. In that moment I looked at my students and just... talked with them. About sound. About why some words feel heavy and some feel light. One boy, who had said almost nothing all week, started tapping rhythms on his desk and asking questions in halting English. After class, Dr. Henrichsen found me in the hallway. He didn\'t say anything for a moment. Then: "That\'s the lesson right there." I had failed my plan and succeeded at teaching. I didn\'t know those were different things until that day.',
      aimsResponses: [
        {
          aim: 'spiritual',
          promptKey: 'spiritual-model',
          promptLabel: 'The Spiritual Model',
          promptFull: 'Describe a time you saw your faculty member handle a professional challenge with Christlike character.',
          response: 'One of our host teachers became difficult partway through the trip — territorial about her classroom, dismissive of our methods. Other students were frustrated. Dr. Henrichsen met with her privately and afterward, at dinner, one of us asked what he\'d said. He said he\'d mostly listened. He told her she had thirty years of experience we didn\'t have and asked her to teach us. By the end of the week she was team-teaching with us. I learned more from watching that than from any methodology class I\'ve taken.'
        },
        {
          aim: 'service',
          promptKey: 'service-bridge',
          promptLabel: 'The Service Bridge',
          promptFull: 'Share an instance where your mentor helped you see how your skills could serve your community.',
          response: 'On our last evening in Mexico City, Dr. Henrichsen asked each of us where we wanted to teach. I said something about international schools or universities. He nodded, then said quietly: "What about the people who can\'t afford international schools?" I hadn\'t thought about that. He spent the next hour telling us about ELC students at BYU — refugees, immigrants, people with more courage than resources — and asking us to think about what our degrees could mean for them specifically. I changed my career trajectory that night.'
        }
      ],
      image: null,
      createdAt: '2026-03-12T09:45:00.000Z'
    },
    {
      id: 'student_seed_004',
      type: 'student',
      studentName: 'Caroline Ashby',
      mentorName: 'Dr. Daniel Adams',
      program: 'Editing & Publishing BA',
      term: 'Winter 2026',
      venueType: 'Editing Practicum',
      venueDesc: 'Schreiner Press undergraduate editing internship',
      transformative: 'I found an error in a source that had been cited correctly in the manuscript but was wrong in the original journal article — a statistic that had apparently been wrong for ten years without anyone noticing. I brought it to Dr. Adams expecting to be praised for the catch. Instead he sat with me for an hour asking: What are your obligations here? To the authors? To the original journal? To future readers? He didn\'t tell me what to do. He helped me think through every stakeholder until I arrived at the answer myself. I sent a note to the original authors. They were grateful. But more than the outcome, I remember realizing that editing isn\'t just grammar — it\'s ethics, all the way down.',
      aimsResponses: [
        {
          aim: 'character',
          promptKey: 'hidden-lesson',
          promptLabel: 'The Hidden Lesson',
          promptFull: 'What is one specific habit you adopted solely because you saw this faculty member doing it?',
          response: 'Dr. Adams reads every acknowledgments section. Every single one. I noticed him doing it once and asked why. He said the acknowledgments tell you who the author trusts, who they\'re indebted to, and sometimes who they\'re avoiding — and that this matters for understanding a book\'s argument. I now read acknowledgments before I read anything else. It\'s changed how I understand texts entirely. It\'s such a small thing, but it\'s completely his.'
        },
        {
          aim: 'intellectual',
          promptKey: 'deep-dive',
          promptLabel: 'The Deep Dive',
          promptFull: 'A time when their enthusiasm made you want to learn more on your own.',
          response: 'Dr. Adams once spent twenty minutes of our practicum session talking about the history of the em dash — why it\'s different from a hyphen and an en dash, how its use changed in the twentieth century, what it signals about a writer\'s relationship to their own prose. He was genuinely excited. I went home that night and read everything I could find about punctuation history. I am now the person at parties who has strong opinions about dashes. This is his fault and I am grateful.'
        }
      ],
      image: null,
      createdAt: '2026-04-23T16:00:00.000Z'
    },
    {
      id: 'student_seed_005',
      type: 'student',
      studentName: 'Rebecca Tanaka',
      mentorName: 'Dr. Cynthia Hallen',
      program: 'Applied English Linguistics BA',
      term: '2025–2026 academic year',
      venueType: 'Thesis / Capstone',
      venueDesc: 'Lexicographic patterns in early modern American English',
      transformative: 'Six months into my thesis, I hit a wall. My argument wasn\'t holding together, the primary sources were contradicting my hypothesis, and I had started to believe the whole project was wrong. I sent Dr. Hallen an email that was essentially a resignation letter. She called me within the hour. She didn\'t reassure me. She said: "Tell me what the sources are saying that you didn\'t expect." I talked for thirty minutes while she listened. At the end she said, "That\'s not a failed thesis — that\'s a better thesis. Your hypothesis was too small." We rebuilt the argument around what the evidence actually showed rather than what I had expected. The finished thesis won the department award. But the real gift was learning that being wrong can be the beginning of being right.',
      aimsResponses: [
        {
          aim: 'spiritual',
          promptKey: 'gospel-lens',
          promptLabel: 'The Gospel Lens',
          promptFull: 'A conversation where a mentor helped you see a connection between your field and a gospel principle.',
          response: 'I was frustrated by how much of early American lexicography was about authority — who had the right to define words, whose English counted. Dr. Hallen asked me if that reminded me of anything in Church history. We ended up talking for an hour about the Restoration — about Joseph Smith translating by the gift and power of God, outside established institutions. She helped me see that questions of linguistic authority are never just linguistic. They\'re always also about power, access, and whose voice gets heard. I\'ve never thought about language the same way since.'
        },
        {
          aim: 'service',
          promptKey: 'rescue',
          promptLabel: 'The Rescue',
          promptFull: 'Tell me about a time you were struggling and what specific steps the faculty member took to help you forward.',
          response: 'When I sent the resignation email, Dr. Hallen did something unexpected: she shared her own thesis crisis. She told me about a chapter she had thrown away entirely in the fourth year of her doctoral program — how she had cried on the floor of the university library and been certain she would never finish. She told me this not to make me feel better but to make me understand that this is part of the process. Then she gave me three specific tasks to complete before we met again — small enough to be doable, targeted enough to matter. That combination of honesty and practical structure saved my project.'
        }
      ],
      image: null,
      createdAt: '2026-04-08T11:00:00.000Z'
    },
    {
      id: 'student_seed_006',
      type: 'student',
      studentName: 'Kavita Shah',
      mentorName: 'Dr. Norman Evans',
      program: 'TESOL MA',
      term: 'Winter 2026',
      venueType: 'TESOL Practicum',
      venueDesc: 'English Language Center — advanced speaking course',
      transformative: 'My most advanced learner \u2014 a software engineer from Iran who had been speaking English for fifteen years \u2014 told me after class one day that my feedback had felt condescending. He was right. I had been over-praising small things, which to him communicated that I had low expectations. I brought this to Dr. Evans. He said: \u201CWhat he\u2019s describing is actually a theory \u2014 look up wise feedback.\u201D He sent me a paper that night. I came to our next session with research and my own plan for changing my practice. Dr. Evans didn\u2019t tell me what to do \u2014 he handed me the tools and trusted me to figure it out. That trust felt like respect. It still does.',
      aimsResponses: [
        {
          aim: 'intellectual',
          promptKey: 'breakthrough',
          promptLabel: 'The Breakthrough',
          promptFull: 'Recall a moment when you felt a sudden "click" in understanding or confidence.',
          response: 'Reading the wise feedback research that night felt like someone had named something I had been experiencing but couldn\'t articulate. The idea that combining high expectations with genuine belief in a student\'s ability isn\'t just kind — it\'s pedagogically distinct from either alone — reorganized everything I thought I knew about teaching. I went back through my lesson plans and found instance after instance where I had been choosing warmth over challenge. Dr. Evans gave me a new lens and I have never stopped using it.'
        },
        {
          aim: 'character',
          promptKey: 'acts-kindness',
          promptLabel: 'Acts of Kindness',
          promptFull: 'A small act of kindness that had nothing to do with coursework but everything to do with your well-being.',
          response: 'Halfway through the semester, I mentioned in passing that I was homesick — my family is in Gujarat and the time difference makes calls difficult. The next day Dr. Evans sent me a list of Gujarati community events in Utah County. He had looked them up himself. He didn\'t mention it in class, didn\'t make it a teaching moment. He just sent the email. I went to one of those events and met people who became real friends. That one quiet act reminded me that my mentor saw me as a person first.'
        }
      ],
      image: null,
      createdAt: '2026-04-26T08:30:00.000Z'
    }
  ];
})();
