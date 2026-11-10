# make_satsang: build one satsang's web pages from one data file

Needs only Python 3 (no packages). For slide images: `pdftoppm` (poppler).

## Files
- `make_satsang.py` the builder
- `templates/quiz.template.html`, `templates/deck.template.html` the page designs (change the design here once, every satsang follows)
- `data/HVM-001.json` the worked example. Copy it to `data/SAT-002.json` and replace the content.

## Data file keys
code, series (SAT or HVM), page_kind ("Satsang" or "Hamilton class"), noun ("satsang" or "class"), title, subtitle, qtitle (full title), date (YYYY-MM-DD), when_where, program ("Satsang Study"), handout_url, handout_label, recording_url (null if none), quiz{marks_per_question, total, desc, og_title, og_desc, hero_line, blessing}, deck{meta_desc, og_desc}, cms{series, themes[], cover_url, slides_download, event_link, summary, reflection_questions[], suggested_reading[]}, slides[] (n, t, on, vs, gl, base, deeper), questions[] (25; types mc and match).

## Run everything with one command
    python3 publish.py data/CODE.json --repo /path/to/satsangs --pdf "CODE Slides.pdf" --cover cover.jpg --logo logo.png --backup "<Drive folder>/Published" --wix-out /tmp/wix-CODE
It makes the slide images, builds the deck and quiz, runs `check_satsang.py` (em dashes, bare names, 25 questions, slide images, real headless-browser click-through of the quiz must give 100, `--online` also checks links), backs up to Drive, and writes the Wix files. It stops if any check fails. Needs `pip install playwright` once for the quiz test. Nothing goes live from it.

## Run the builder alone
    python3 make_satsang.py data/SAT-002.json --repo /path/to/satsangs --wix-out /tmp/wix-SAT-002
Writes `CODE/index.html` and `CODE/quiz/index.html` into the repository checkout, and `cms_row.json`, `study_step.ricos.json` and `answers_step.ricos.json` for Wix. The script refuses to run if there are not 25 questions, marks do not add up, an answer is badly skewed, or any em dash is in the data.

## Slide images and cover
    pdftoppm -jpeg -jpegopt quality=80 -scale-to-x 1600 -scale-to-y -1 "CODE Slides.pdf" CODE/slides/s
    (rename s-1.jpg etc. to s-01.jpg ... if needed; keep logo.png and cover.jpg beside index.html)

## Test
Open `CODE/quiz/index.html`, answer everything correctly: the result must be 100 of 100. Open `CODE/index.html` and step through every slide.

## Proof it works
Run on `data/HVM-001.json`, the output is byte for byte identical to the live HVM-001 pages.
Set `"allow_bare_names": true` only for an old satsang published before the naming rule (HVM-001); new ones must write "Swami Vivekananda" in full.

Not yet automated: sending the Wix files (Claude does this with the Wix API, after approval), tracker and README rows.

## Writing the quiz questions (standing rules from Swami Tadananda, 3 Nov 2026)
The quiz must serve a purpose: it tests that the person has understood the teaching and can apply it. Recall of facts is not enough.

### Test assimilation, not information (Swami Tadananda, 11 Nov 2026)
Swami Vivekananda: "Education is not the amount of information that is put into your brain and runs riot there, undigested, all your life. We must have life-building, man-making, character-making assimilation of ideas. If you have assimilated five ideas and made them your life and character, you have more education than any man who has got by heart a whole library." (The Future of India, Lectures from Colombo to Almora, Complete Works Vol. 3)

Bloom's six levels are information (remembering), understanding, application, analysis, synthesis and evaluation. The last three are what Swami Vivekananda calls assimilation: the idea has become part of the way we see, judge and act. Our quizzes test assimilation, so that the ideas grow into the personality and help each person manifest the inner light more and more.
- Tag every question with its level in `lv`: `understand`, `apply`, `analyse`, `evaluate` or `synthesise`. Never `remember`. The check fails if a level is missing, if more than 2 are `understand`, if fewer than 60% are `analyse`, `evaluate` or `synthesise`, or if any of those three has fewer than 3. Aim for about 4 apply, 7 analyse, 7 evaluate, 6 synthesise, with 0 to 1 understand. The level is shown on the answers page only.
- **Apply**: a realistic situation the person might face; choose what the teaching asks here.
- **Analyse**: diagnose what is really happening in a case: the hidden motive, the root error, which principle is at work, where an offering is incomplete. Matching questions belong here (which idea fits which person).
- **Evaluate**: judge between responses that all sound good, or assess someone's reasoning or decision. The wrong options are half-truths and over-corrections that sincere people hold (too lax, too harsh, one half of the truth without the other).
- **Synthesise**: bring two or more teachings together to plan something new: a practice, a branch decision, a change of culture, a next step in one's own growth.
- Include at least one question on how a person can tell that an idea has become part of their character (signs of growth, not amounts of activity), and one on moving from hearing and reading to living (śravaṇa, manana, nididhyāsana).
- Each explanation teaches: why the right answer is right, why each tempting option falls short, and the teaching behind it. Each reflection turns the idea into the person's own life and character, never back to a fact.
- Test comprehension (why, how, what follows) and application (a realistic situation, a common misunderstanding, a choice the person might face). At least two thirds of the questions should be a situation, a misunderstanding to correct, or a "what would follow" question.
- Make every question stand on its own months later, for someone who was not there. Never ask about the next class or satsang, dates, times, venues, who attended, slide numbers or the running order of the evening.
- Do not ask for a bare fact: no "which word completes the verse", no "which number", no "which teacher said X" unless knowing the teacher changes the meaning. A verse or a Sanskrit term may appear, but the question must ask what it means or how it applies.
- Matching questions are allowed only when the person must decide which idea fits a situation (for example, which knot or which pitfall is at work in a described case). No matching of term to definition, or name to quotation.
- Wrong options must be real misunderstandings that a thoughtful person might hold, written with the same length, tone and detail as the right one. Do not make the correct answer the longest, the most qualified, or the only one that sounds spiritual. The check fails if the correct answer is the longest option in more than half the questions.
- Spread the correct answers over A, B, C and D (the check refuses a badly skewed spread).
- Each explanation says why the right answer is right and why the tempting wrong ones are not, and gives the teaching behind it. Each reflection question turns the teaching to the person's own life.
- Quote only from the Centre's three publications when quoting teachers (The Gospel of Sri Ramakrishna, The Gospel of Holy Mother, The Complete Works of Swami Vivekananda). Paraphrase everything else and label it as such. No em dashes. Write "Swami Vivekananda" in full.
- Before sending, read each question and ask: could someone who had not studied answer it from common sense, or from the length of the options? Could someone who studied it well and thought deeply answer it? Then it is a good question.
