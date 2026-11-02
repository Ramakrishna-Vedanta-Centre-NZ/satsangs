#!/usr/bin/env python3
"""Build the published files for one satsang from its data file.

  python3 make_satsang.py data/CODE.json --repo /path/to/satsangs [--wix-out DIR]

Writes into the repository checkout:
  CODE/quiz/index.html   the revision quiz (from templates/quiz.template.html)
  CODE/answers/index.html  answers, explanations and reflections, one anchor per question (templates/answers.template.html)
  CODE/index.html        the web deck: slide images, notes, reading view (from templates/deck.template.html)
Writes into --wix-out (not published, for Claude to upload with the Wix API):
  cms_row.json           the row for the Wix CMS collection "Satsangs"
  study_step.ricos.json  the Study step (buttons for the deck and the handout) for Satsang Study
Slide images (CODE/slides/s-01.jpg ...) and cover.jpg, logo.png are made separately; see README.md.
No third-party packages are needed. Prose written by this script contains no em dashes.
"""
import argparse, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PAGES = "https://ramakrishna-vedanta-centre-nz.github.io/satsangs/"

def fill(t, vals):
    for k, v in vals.items():
        t = t.replace("{{%s}}" % k, v)
    left = [w for w in __import__("re").findall(r"\{\{[A-Z_]+\}\}", t)]
    if left:
        sys.exit("unfilled placeholders: %s" % sorted(set(left)))
    return t

def check(d):
    q = d["questions"]
    assert len(q) == 25, "expected 25 questions, found %d" % len(q)
    mc = [x for x in q if x["t"] == "mc"]
    for x in mc:
        assert len(x["o"]) == 4 and 0 <= x["a"] < 4, x["q"]
    from collections import Counter
    c = Counter(x["a"] for x in mc)
    assert max(c.values()) - min(c.get(i, 0) for i in range(4)) <= 3, "answers badly skewed: %s" % dict(c)
    assert len(d["slides"]) >= 1
    marks = d["quiz"]["marks_per_question"]
    assert marks * len(q) == d["quiz"]["total"], "marks do not add up to the total"
    for k in ("code", "title", "handout_url"):
        assert d.get(k), "missing " + k
    blob = json.dumps(d, ensure_ascii=False)
    assert "—" not in blob, "em dash found in data"

def build_quiz(d):
    q = json.dumps(d["questions"], ensure_ascii=False)
    z = d["quiz"]
    t = open(os.path.join(HERE, "templates", "quiz.template.html"), encoding="utf-8").read()
    return fill(t, {
        "QUESTIONS": q, "M": str(z["marks_per_question"]), "TOT": str(z["total"]),
        "PAGE_KIND": d["page_kind"], "CODE": d["code"], "DESC": z["desc"],
        "OG_TITLE": z["og_title"], "OG_DESC": z["og_desc"], "TITLE": d["title"],
        "HERO_LINE": z["hero_line"], "NOUN": d["noun"], "BLESSING": z["blessing"],
        "QTITLE_JSON": json.dumps(d["qtitle"], ensure_ascii=False).replace('"', "'")
            if "'" not in d["qtitle"] else json.dumps(d["qtitle"], ensure_ascii=False),
        "QPROG_JSON": "'" + d["program"] + "'"})

def build_answers(d):
    import html
    h = lambda x: html.escape(x, quote=False)
    L = "ABCD"
    chips = "".join('<a href="#q%d">%d</a>' % (i, i) for i in range(1, len(d["questions"]) + 1))
    cards = []
    for i, x in enumerate(d["questions"], 1):
        c = ['<section class="card" id="q%d"><p class="qn">QUESTION %d%s</p><p class="q">%s</p>' % (i, i, " · MATCHING" if x["t"] == "match" else "", h(x["q"]))]
        if x["t"] == "mc":
            for k, o in enumerate(x["o"]):
                if k == x["a"]:
                    c.append('<div class="opt right"><b>%s.</b> %s<span class="tick">\u2713 Correct answer</span></div>' % (L[k], h(o)))
                else:
                    c.append('<div class="opt"><b>%s.</b> %s</div>' % (L[k], h(o)))
        else:
            c.append('<table class="match">')
            for k, row in enumerate(x["rows"]):
                c.append("<tr><td>%d. %s</td><td>\u2713 %s</td></tr>" % (k + 1, h(row), h(x["c"][x["ans"][k]])))
            c.append("</table>")
        lab = str(x["s"]); first = __import__("re").search(r"\d+", lab)
        link = ('<a href="../#%s">See slide%s %s</a>.' % (first.group(0), "" if lab.isdigit() else "s", h(lab))) if first else ""
        c.append('<p class="ex">%s %s</p>' % (h(x["e"]), link))
        c.append('<div class="refl"><b>Reflect:</b> <i>%s</i></div>' % h(x["r"]))
        c.append('<a class="top" href="#top-of-page" onclick="window.scrollTo(0,0);return false">\u2191 Back to the top</a></section>')
        cards.append("".join(c))
    t = open(os.path.join(HERE, "templates", "answers.template.html"), encoding="utf-8").read()
    return fill(t, {"PAGE_KIND": d["page_kind"], "CODE": d["code"], "TITLE": d["title"], "CHIPS": chips, "CARDS": "\n".join(cards)})

def build_deck(d):
    data = json.dumps(d["slides"], ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    t = open(os.path.join(HERE, "templates", "deck.template.html"), encoding="utf-8").read()
    return fill(t, {
        "DATA": data, "HANDOUT_URL": d["handout_url"], "TITLE": d["title"],
        "PAGE_KIND": d["page_kind"], "CODE": d["code"], "META_DESC": d["deck"]["meta_desc"],
        "QTITLE": d["qtitle"], "OG_DESC": d["deck"]["og_desc"], "SUBTITLE": d["subtitle"],
        "WHEN_WHERE": d["when_where"]})

def li(items, tag):
    return "<%s>%s</%s>" % (tag, "".join("<li>%s</li>" % i for i in items), tag)

def cms_row(d):
    c = d["cms"]
    row = {
        "code": d["code"], "title": d["qtitle"], "satsangDate": d["date"], "series": c["series"],
        "themes": c["themes"], "coverImage": c["cover_url"], "summary": c["summary"],
        "reflectionQuestions": li(c["reflection_questions"], "ol"),
        "suggestedReading": li(c["suggested_reading"], "ul"),
        "slidesLink": PAGES + d["code"] + "/", "slidesDownload": c["slides_download"]}
    if c.get("event_link"):
        row["eventLink"] = c["event_link"]
    if c.get("recording"):
        row["recording"] = c["recording"]
    return {"dataCollectionId": "Satsangs", "dataItem": {"data": row}}

def para(id_, parts):
    nodes = []
    for text, bold in parts:
        dec = [{"type": "BOLD", "fontWeightValue": 700}] if bold else []
        nodes.append({"type": "TEXT", "id": "", "nodes": [], "textData": {"text": text, "decorations": dec}})
    return {"type": "PARAGRAPH", "id": id_, "nodes": nodes, "paragraphData": {}}

def button(text, url):
    return {"type": "BUTTON", "buttonData": {"type": "LINK", "text": text,
        "link": {"url": url, "target": "BLANK"},
        "containerData": {"alignment": "LEFT", "width": {"size": "ORIGINAL"}, "textWrap": False},
        "styles": {"borderRadius": 6, "borderWidth": 0, "backgroundColor": "#00695C", "textColor": "#FFFFFF"}}}

def study_step(d):
    n = [para("p0", [("Study the class at your own pace, then take the revision quiz in the next step.", False)]),
         para("p1", [("Slides for self-study (with study notes and the quiz): ", True)]), {"type": "PARAGRAPH"},
         button("open the slides (with study notes)", PAGES + d["code"] + "/"), {"type": "PARAGRAPH"},
         para("p2", [("Members' handout: ", True)]), {"type": "PARAGRAPH"},
         button(d["handout_label"], d["handout_url"]), {"type": "PARAGRAPH"}]
    if d.get("recording_url"):
        n += [para("p3", [("Recording: ", True)]), {"type": "PARAGRAPH"}, button("watch the recording", d["recording_url"]), {"type": "PARAGRAPH"}]
    n.append(para("p4", [("Share your reflections and questions in the members' group (Group Discussion).", False)]))
    return {"title": "Study the class: slides and handout" if d["noun"] == "class" else "Study the satsang: slides and handout",
            "details": json.dumps({"nodes": n, "metadata": {"version": 1}}, ensure_ascii=False)}


# ---- Answers step (Satsang Study) -------------------------------------------
INTRO = ("Read this after you have taken the quiz. For each question you will find the answer, a fuller explanation "
         "of the teaching, and a question to reflect on in your own life. You may like to take one reflection each day, "
         "write a few lines in a journal, and share an insight in the members\u2019 group.")

def _t(text, bold=False, italic=False, color="#333333", bg=None, size=15):
    dec = []
    if bold: dec.append({"type": "BOLD", "fontWeightValue": 700})
    cd = {"foreground": color}
    if bg: cd["background"] = bg
    dec.append({"type": "COLOR", "colorData": cd})
    dec.append({"type": "FONT_SIZE", "fontSizeData": {"unit": "PX", "value": size}})
    if italic: dec.append({"type": "ITALIC", "italicData": True})
    return {"type": "TEXT", "id": "", "nodes": [], "textData": {"text": text, "decorations": dec}}

def answers_step(d):
    n = []
    def P(*runs):
        n.append({"type": "PARAGRAPH", "id": "a%d" % len(n), "nodes": list(runs), "paragraphData": {}})
    L = "ABCD"
    P(_t(INTRO)); P()
    for i, x in enumerate(d["questions"], 1):
        n.append({"type": "HEADING", "id": "a%d" % len(n), "nodes": [_t("Question %d" % i, color="#283593", size=22)],
                  "headingData": {"level": 3}})
        P(_t(x["q"], bold=True)); P()
        if x["t"] == "mc":
            P(_t("Answer choices:", bold=True))
            for k, o in enumerate(x["o"]):
                P(_t("%s. %s" % (L[k], o)))
            P(); P(_t("Answer: ", bold=True, color="#00695C"), _t("%s. %s" % (L[x["a"]], x["o"][x["a"]])))
        else:
            P(_t("Choices: ", bold=True), _t(" / ".join(x["c"]))); P()
            P(_t("Answer: ", bold=True, color="#00695C"))
            for k, row in enumerate(x["rows"], 1):
                P(_t("%d. %s \u2192 " % (k, row)), _t(x["c"][x["ans"][k - 1]]))
        P(_t("%s (Slide %d)" % (x["e"], x["s"]))); P()
        P(_t("Reflect: ", bold=True, color="#6A356A", bg="#F5F0F7"), _t(x["r"], italic=True))
        P()
        n.append({"type": "DIVIDER", "id": "a%d" % len(n), "nodes": [], "dividerData": {}}); P()
    del n[-2:]  # no divider after the last question
    return {"title": "Answers and reflections",
            "details": json.dumps({"nodes": n, "metadata": {"version": 1}}, ensure_ascii=False)}

# ---- One-lesson page (Satsang Study, one lesson per satsang) -----------------
NAVY, TEAL = "#12285A", "#00695C"

def _run(text, bold=False, italic=False, color=None, size=None):
    dec = []
    if bold: dec.append({"type": "BOLD", "fontWeightValue": 700})
    if italic: dec.append({"type": "ITALIC", "italicData": True})
    if color: dec.append({"type": "COLOR", "colorData": {"foreground": color}})
    if size: dec.append({"type": "FONT_SIZE", "fontSizeData": {"unit": "PX", "value": size}})
    return {"type": "TEXT", "id": "", "nodes": [], "textData": {"text": text, "decorations": dec}}

def lesson_title(d):
    import datetime
    dt = datetime.date.fromisoformat(d["date"])
    return "%s - %s (%s)" % (d["code"].split("-", 1)[1], d["title"], dt.strftime("%d %b %y").upper())


def lesson_step(d):
    c = d["cms"]; base = PAGES + d["code"] + "/"
    n = []
    def nid(): return "L%d" % len(n)
    def P(*runs): n.append({"type": "PARAGRAPH", "id": nid(), "nodes": list(runs), "paragraphData": {}})
    def H(text, level=3): n.append({"type": "HEADING", "id": nid(), "nodes": [_run(text, color=NAVY)], "headingData": {"level": level}})
    def B(text, url): n.append(dict(button(text, url), id=nid(), nodes=[]))
    def lst(kind, items):
        n.append({"type": kind, "id": nid(), "nodes": [{"type": "LIST_ITEM", "id": "", "nodes": [
            {"type": "PARAGRAPH", "id": "", "nodes": [_run(i)], "paragraphData": {}}]} for i in items],
            ("orderedListData" if kind == "ORDERED_LIST" else "bulletedListData"): {"indentation": 0}})
    if c.get("wix_cover_id"):
        n.append({"type": "IMAGE", "id": nid(), "nodes": [], "imageData": {"image": {"src": {"id": c["wix_cover_id"]}, "width": 1600, "height": 900},
                  "containerData": {"alignment": "CENTER", "width": {"size": "CONTENT"}, "textWrap": True}, "altText": d["qtitle"]}})
    P(_run(c["place"], bold=True, color=TEAL)); P()
    P(_run(c["intro"])); P()
    H("Study")
    P(_run("Go through the slides at your own pace. Each slide has study notes, verses and songs."))
    B("open the slides", base)
    P(_run("The Study Companion is a printable handout with the verses, key terms and commentary for every slide."))
    B(d["handout_label"], d["handout_url"]); P()
    H("Test yourself")
    P(_run("A revision quiz of 25 questions. Sign in to keep your score under My Journey."))
    B("take the quiz", "https://www.vedanta.nz/quiz?q=" + d["code"])
    P(_run("After the quiz, read the answers with fuller explanations and a reflection for each question."))
    B("read the answers", base + "answers/"); P()
    if c.get("event_link") or d.get("recording_url"):
        H("Join us")
        if c.get("event_link"):
            P(_run("Come in person or join on Zoom. RSVP on the event page to receive the Zoom link."))
            B("event page and RSVP", c["event_link"])
        if d.get("recording_url"):
            P(_run("Watch the recording of the %s." % d.get("noun", "satsang")))
            B("watch the recording", d["recording_url"])
        P()
    H("Reflect")
    if c.get("reflection_questions"):
        lst("ORDERED_LIST", c["reflection_questions"])
    P(_run("Share your reflections and questions in the members\u2019 group (Group Discussion below)."))
    if c.get("suggested_reading"):
        P(); H("Suggested reading")
        lst("BULLETED_LIST", c["suggested_reading"])
    return {"title": lesson_title(d),
            "details": json.dumps({"nodes": n, "metadata": {"version": 1}}, ensure_ascii=False)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data"); ap.add_argument("--repo", required=True); ap.add_argument("--wix-out")
    a = ap.parse_args()
    d = json.load(open(a.data, encoding="utf-8"))
    if d.get("lesson_only"):
        os.makedirs(a.wix_out, exist_ok=True)
        json.dump(lesson_step(d), open(os.path.join(a.wix_out, "lesson_step.ricos.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("wrote lesson only"); return
    check(d)
    for sub, content in (("quiz/index.html", build_quiz(d)), ("answers/index.html", build_answers(d)), ("index.html", build_deck(d))):
        p = os.path.join(a.repo, d["code"], sub)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w", encoding="utf-8").write(content)
        print("wrote", p)
    if a.wix_out:
        os.makedirs(a.wix_out, exist_ok=True)
        json.dump(cms_row(d), open(os.path.join(a.wix_out, "cms_row.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        json.dump(study_step(d), open(os.path.join(a.wix_out, "study_step.ricos.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        json.dump(lesson_step(d), open(os.path.join(a.wix_out, "lesson_step.ricos.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        json.dump(answers_step(d), open(os.path.join(a.wix_out, "answers_step.ricos.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("wrote Wix files in", a.wix_out)

if __name__ == "__main__":
    main()
