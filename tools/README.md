# make_satsang: build one satsang's web pages from one data file

Needs only Python 3 (no packages). For slide images: `pdftoppm` (poppler).

## Files
- `make_satsang.py` the builder
- `templates/quiz.template.html`, `templates/deck.template.html` the page designs (change the design here once, every satsang follows)
- `data/HVM-001.json` the worked example. Copy it to `data/SAT-002.json` and replace the content.

## Data file keys
code, series (SAT or HVM), page_kind ("Satsang" or "Hamilton class"), noun ("satsang" or "class"), title, subtitle, qtitle (full title), date (YYYY-MM-DD), when_where, program ("Satsang Study"), handout_url, handout_label, recording_url (null if none), quiz{marks_per_question, total, desc, og_title, og_desc, hero_line, blessing}, deck{meta_desc, og_desc}, cms{series, themes[], cover_url, slides_download, event_link, summary, reflection_questions[], suggested_reading[]}, slides[] (n, t, on, vs, gl, base, deeper), questions[] (25; types mc and match).

## Run
    python3 make_satsang.py data/SAT-002.json --repo /path/to/satsangs --wix-out /tmp/wix-SAT-002
Writes `CODE/index.html` and `CODE/quiz/index.html` into the repository checkout, and `cms_row.json` and `study_step.ricos.json` for Wix. The script refuses to run if there are not 25 questions, marks do not add up, an answer is badly skewed, or any em dash is in the data.

## Slide images and cover
    pdftoppm -jpeg -jpegopt quality=80 -scale-to-x 1600 -scale-to-y -1 "CODE Slides.pdf" CODE/slides/s
    (rename s-1.jpg etc. to s-01.jpg ... if needed; keep logo.png and cover.jpg beside index.html)

## Test
Open `CODE/quiz/index.html`, answer everything correctly: the result must be 100 of 100. Open `CODE/index.html` and step through every slide.

## Proof it works
Run on `data/HVM-001.json`, the output is byte for byte identical to the live HVM-001 pages.
Not yet automated: the Answers step in Wix (copy the previous Answers step and replace the content).
