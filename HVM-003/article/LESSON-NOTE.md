# HVM-003 Satsang Study lesson: the live page is the master

The Satsang Study lesson "003 - Free Will and Divine Will (09 DEC 26)" (Wix Online Programs step
`a9a6f667-0a05-4eeb-aa85-215354c2fc71`, program `eb9c2b62-87b4-4e2e-aab6-19043659ded5`) is the main
study site for HVM-003. Since 27 November 2026 it holds, in order:

1. Cover image, date and venue, summary.
2. "Study materials": eight buttons (slides web deck, slides PDF, article PDF, interactives, quiz,
   answers, course dashboard, event page).
3. The web deck embedded (HTML node, width 1000, height 760).
4. The whole study article from the Word file, with figures (Wix Media ids in `build_lesson.py`
   output), tables, Going deeper panels, key ideas, and each live interactive embedded at its
   callout (HTML node, width 1000, height 820) with a full-screen link.
5. The original quiz, event, reflection, reading and offering sections.

Formatting applied on the live page after `lesson.json` was written: dark body text (#1F2937),
an empty paragraph between blocks, the embed sizes above, and the study-materials list turned
into buttons. So `lesson.json` here is the source of the article part only, not a full copy.

**Do not repost** `lesson_step.ricos.json` from `tools/make_satsang.py --wix-out` over this
lesson: the generator still writes the older short lesson and would wipe the article.
Make targeted edits to the live step (read its revision first), as the workflow plan says.
