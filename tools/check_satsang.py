#!/usr/bin/env python3
"""Automated checks for one satsang's built pages.

  python3 check_satsang.py data/CODE.json --repo /path/to/satsangs [--online]

1. Data: em dashes, bare "Swamiji" or "Vivekananda" in public text, question count, marks.
2. Quiz: opens CODE/quiz/index.html in a headless browser (Playwright), answers every question correctly,
   and requires 100 out of 100. Also checks that the deck has one slide image per slide.
3. --online: every link used by the pages and Wix files returns 200.
Exit code 0 only if everything passes.
"""
import argparse, json, os, re, sys, urllib.request

def fail(msg, errs): errs.append(msg); print("FAIL", msg)
def ok(msg): print("ok  ", msg)

def public_text(d):
    parts = [d["title"], d["subtitle"], d["qtitle"], d["cms"]["summary"]] + d["cms"]["reflection_questions"] + d["cms"]["suggested_reading"]
    for x in d["questions"]:
        parts += [x["q"], x["e"], x["r"]] + x.get("o", []) + x.get("rows", []) + x.get("c", [])
    for s in d["slides"]:
        parts += [json.dumps(s, ensure_ascii=False)]
    return "\n".join(parts)

def data_checks(d, errs):
    t = public_text(d)
    if "\u2014" in json.dumps(d, ensure_ascii=False): fail("em dash in data", errs)
    else: ok("no em dashes")
    bad = [m.group(0) for m in re.finditer(r"(?<!Swami )\bVivekananda\b|\bSwamiji\b", t)]
    # 'Swami Vivekananda' is fine; bare 'Vivekananda' or 'Swamiji' needs a look
    if bad: fail("bare name(s) in public text: %s (check each: Swamiji means Swami Tadananda, keep out of public text)" % sorted(set(bad)), errs)
    else: ok("names are written in full")
    if len(d["questions"]) == 25: ok("25 questions")
    else: fail("question count %d" % len(d["questions"]), errs)

def quiz_test(d, repo, errs):
    """Click the correct answer on every question in a real headless browser; the page must show 100."""
    from playwright.sync_api import sync_playwright
    path = os.path.join(repo, d["code"], "quiz", "index.html")
    qs = d["questions"]; tot = d["quiz"]["total"]
    with sync_playwright() as pw:
        b = pw.chromium.launch(); pg = b.new_page(viewport={"width": 390, "height": 800})
        pg.goto("file://" + os.path.abspath(path)); pg.wait_for_timeout(500)
        try:
            for x in qs:
                if x["t"] == "mc":
                    pg.locator(".opt").nth(x["a"]).click()
                else:
                    for r, c in enumerate(x["ans"]):
                        pg.locator('.ch[data-r="%d"] button[data-c="%d"]' % (r, c)).click()
                    pg.locator("#chk").click()
                pg.locator("#nx").click()
            pg.wait_for_timeout(300)
            body = pg.locator("body").inner_text()
            m = re.search(r"(\d+)\s*(?:/|out of|of)\s*%d" % tot, body)
            score_line = pg.locator("#sc").inner_text()
            good = ("Score: %d" % tot) in score_line
        except Exception as e:
            fail("quiz click-through error: %s" % str(e)[:200], errs); b.close(); return
        b.close()
    if good: ok("quiz click-through: all correct gives %d of %d" % (tot, tot))
    else: fail("quiz click-through ended with '%s'" % score_line, errs)

def deck_checks(d, repo, errs):
    sl = os.path.join(repo, d["code"], "slides")
    have = sorted(f for f in os.listdir(sl)) if os.path.isdir(sl) else []
    if len(have) == len(d["slides"]): ok("%d slide images" % len(have))
    else: fail("slide images %d but slides %d" % (len(have), len(d["slides"])), errs)
    for f in ("logo.png", "cover.jpg", "index.html", os.path.join("quiz", "index.html")):
        if os.path.exists(os.path.join(repo, d["code"], f)): ok("has " + f)
        else: fail("missing " + f, errs)

def links(d):
    base = "https://ramakrishna-vedanta-centre-nz.github.io/satsangs/" + d["code"]
    return [base + "/", base + "/quiz/", d["handout_url"], d["cms"]["cover_url"], "https://www.vedanta.nz/quiz?q=" + d["code"]]

def online(d, errs):
    for u in links(d):
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=20)
            (ok if r.status == 200 else lambda m: fail(m, errs))("%s %s" % (r.status, u))
        except Exception as e:
            fail("%s %s" % (u, e), errs)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("data"); ap.add_argument("--repo", required=True); ap.add_argument("--online", action="store_true")
    a = ap.parse_args(); d = json.load(open(a.data, encoding="utf-8")); errs = []
    data_checks(d, errs); deck_checks(d, a.repo, errs); quiz_test(d, a.repo, errs)
    if a.online: online(d, errs)
    print("\nALL CHECKS PASSED" if not errs else "\n%d CHECK(S) FAILED" % len(errs))
    sys.exit(1 if errs else 0)

if __name__ == "__main__":
    main()
