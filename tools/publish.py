#!/usr/bin/env python3
"""One command from the data file to everything ready to publish. Nothing goes live from here.

  python3 publish.py data/CODE.json --repo /path/to/satsangs --pdf "CODE Slides.pdf" \\
        --cover cover.jpg --logo logo.png --backup "/path/to/Drive/.../CODE Title/Published" --wix-out /tmp/wix-CODE

Steps: slide images from the PDF (if --pdf), build deck and quiz, copy cover and logo, run all checks,
back up the published folder to Drive (if --backup), write the Wix files, print what is left to do.
It stops with an error if any check fails. Pushing to GitHub and the Wix calls are done by Claude afterwards,
only after Swamiji has approved, and Claude asks before anything goes live on vedanta.nz.
"""
import argparse, glob, json, os, shutil, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))

def run(cmd):
    print("$", " ".join(cmd)); r = subprocess.run(cmd)
    if r.returncode: sys.exit("step failed: %s" % cmd[0])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data"); ap.add_argument("--repo", required=True)
    ap.add_argument("--pdf"); ap.add_argument("--cover"); ap.add_argument("--logo")
    ap.add_argument("--backup"); ap.add_argument("--wix-out", default="wix-out"); ap.add_argument("--online", action="store_true")
    a = ap.parse_args(); d = json.load(open(a.data, encoding="utf-8")); code = d["code"]
    out = os.path.join(a.repo, code); os.makedirs(os.path.join(out, "slides"), exist_ok=True)
    if a.pdf:
        for f in glob.glob(os.path.join(out, "slides", "s-*.jpg")): os.remove(f)
        run(["pdftoppm", "-jpeg", "-jpegopt", "quality=80", "-scale-to-x", "1600", "-scale-to-y", "-1", a.pdf, os.path.join(out, "slides", "s")])
        for f in glob.glob(os.path.join(out, "slides", "s-*.jpg")):   # s-1.jpg or s-01.jpg -> s-01.jpg
            n = int(os.path.basename(f)[2:-4]); os.rename(f, os.path.join(out, "slides", "s-%02d.jpg" % n)) if os.path.basename(f) != "s-%02d.jpg" % n else None
    for src, name in ((a.cover, "cover.jpg"), (a.logo, "logo.png")):
        if src: shutil.copy(src, os.path.join(out, name))
    run([sys.executable, "-I", os.path.join(HERE, "make_satsang.py"), a.data, "--repo", a.repo, "--wix-out", a.wix_out])
    run([sys.executable, os.path.join(HERE, "check_satsang.py"), a.data, "--repo", a.repo] + (["--online"] if a.online else []))
    if a.backup:
        shutil.rmtree(a.backup, ignore_errors=True); shutil.copytree(out, a.backup); print("backed up to", a.backup)
    print("""
READY. Left to do, in order (Claude does these, asking before anything goes live):
  1. Swamiji approves the quiz, quotations and the pages (use the GitHub Pages preview after step 2)
  2. git add %s, commit, push to main; check https://ramakrishna-vedanta-centre-nz.github.io/satsangs/%s/
  3. Wix Media: import the handout PDF and cover (plan, step 6); put their links in the data file and run again
  4. Wix: create the section; Study step from %s/study_step.ricos.json, Quiz step, Answers step from answers_step.ricos.json
  5. Wix: insert the row from %s/cms_row.json into Satsangs
  6. Signed-in phone check, then tracker "Live", README row, handover note""" % (code, code, a.wix_out, a.wix_out))

if __name__ == "__main__":
    main()
