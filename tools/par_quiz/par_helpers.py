import json, os
def mc(kind, q, o, a, e, c, s): return {"t": "mc", "kind": kind, "q": q, "o": o, "a": a, "e": e, "c": c, "s": s}
def judge(q, a, e, c, s): return {"t": "judge", "kind": "J", "q": q, "a": a, "e": e, "c": c, "s": s}
T, F, P = 0, 1, 2
def save(num, title, reflection, qs):
    d = {"code": "PAR-%02d" % num, "lesson": num, "title": title, "reflection": reflection, "questions": qs}
    json.dump(d, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "PAR-%02d.json" % num), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
