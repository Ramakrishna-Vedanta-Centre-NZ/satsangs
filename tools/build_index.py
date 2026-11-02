#!/usr/bin/env python3
"""Writes satsangs.json at the repo root: the list the My Journey dashboard shows (code, title, date, series, lesson).
Run after adding or changing a satsang:  python3 tools/build_index.py --repo /home/claude/satsangs
Each data file needs cms.lesson_step_id (the id of its lesson in the Satsang Study course)."""
import argparse, glob, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from make_satsang import lesson_title

ap = argparse.ArgumentParser(); ap.add_argument("--repo", required=True); a = ap.parse_args()
here = os.path.dirname(os.path.abspath(__file__))
items = []
for f in sorted(glob.glob(os.path.join(here, "data", "*.json"))):
    d = json.load(open(f, encoding="utf-8"))
    sid = d.get("cms", {}).get("lesson_step_id")
    if not sid:
        print("skipped (no lesson_step_id):", f); continue
    items.append({"code": d["code"], "title": d["title"], "date": d["date"],
                  "series": "Hamilton" if d["code"].startswith("HVM") else "Auckland",
                  "lessonTitle": lesson_title(d), "lessonStepId": sid})
items.sort(key=lambda x: x["date"], reverse=True)
out = os.path.join(a.repo, "satsangs.json")
json.dump({"satsangs": items}, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("wrote", out, len(items), "satsangs")
