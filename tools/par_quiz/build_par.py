#!/usr/bin/env python3
"""Build Parents lesson quiz pages: data/PAR-NN.json -> ../../PAR-NN/quiz/index.html, then check them.
Usage: python3 build_par.py [NN ...]   (no args = every data file)"""
import json, sys, re, glob, os
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
tpl = open(os.path.join(HERE, 'template.html'), encoding='utf-8').read()
def js(x): return json.dumps(x, ensure_ascii=False).replace('</', '<\\/')
def problems(d):
    p = []; Q = d['questions']
    if len(Q) != 10: p.append('needs exactly 10 questions, has %d' % len(Q))
    mc = [q for q in Q if q['t'] == 'mc']; longest = 0; shortest = 0
    for k, q in enumerate(Q, 1):
        if q['t'] == 'mc':
            if len(q['o']) != 4 or not 0 <= q['a'] < 4: p.append('Q%d options/answer' % k)
            else:
                c = len(q['o'][q['a']]); L = [len(o) for o in q['o']]
                others = sorted(L[:q['a']] + L[q['a'] + 1:])
                if c > others[-1] * 1.10: longest += 1   # salient: more than 10% longer than the next longest
                if c < others[0] * 0.90: shortest += 1
        elif q['t'] == 'judge':
            if q['a'] not in (0, 1, 2): p.append('Q%d judge answer' % k)
        else: p.append('Q%d unknown type' % k)
        for f in ('q', 'e', 'c', 's'):
            if not q.get(f): p.append('Q%d missing %s' % (k, f))
        txt = json.dumps(q, ensure_ascii=False)
        if '—' in txt or '–' in txt: p.append('Q%d has a dash character' % k)
    if mc and longest > len(mc) / 3: p.append('correct option is the longest in %d of %d mc' % (longest, len(mc)))
    if mc and shortest > len(mc) / 2: p.append('correct option is the shortest in %d of %d mc' % (shortest, len(mc)))
    if sum(q['t'] == 'judge' for q in Q) not in (2, 3): p.append('judgements should be 2 or 3')
    if sum(q['t'] == 'mc' and q.get('kind') == 'A' for q in Q) < 5: p.append('fewer than 5 application mc questions (kind A)')
    return p
def build(path):
    d = json.load(open(path, encoding='utf-8')); pr = problems(d)
    code = d['code']
    meta = {'code': code, 'lesson': str(d['lesson']), 'quizTitle': 'Quiz: Lesson %s, %s' % (d['lesson'], d['title']), 'programme': 'Ritam Wellness for Parents', 'cut': 70}
    Q = [{k: v for k, v in q.items() if k in ('t', 'q', 'o', 'a', 'e', 'c', 's')} for q in d['questions']]
    out = (tpl.replace('@@LESSON@@', str(d['lesson'])).replace('@@TITLE@@', d['title']).replace('@@CODE@@', code)
           .replace('@@META@@', js(meta)).replace('@@REFLECT@@', js(d.get('reflection', ''))).replace('@@Q@@', js(Q)))
    out_dir = os.path.join(ROOT, code, 'quiz'); os.makedirs(out_dir, exist_ok=True)
    open(os.path.join(out_dir, 'index.html'), 'w', encoding='utf-8').write(out)
    print(code, 'built' + (' WITH PROBLEMS: ' + '; '.join(pr) if pr else ' ok'))
    return not pr
if __name__ == '__main__':
    files = [os.path.join(HERE, 'data', 'PAR-%02d.json' % int(n)) for n in sys.argv[1:]] or sorted(glob.glob(os.path.join(HERE, 'data', 'PAR-*.json')))
    sys.exit(0 if all([build(f) for f in files]) else 1)
