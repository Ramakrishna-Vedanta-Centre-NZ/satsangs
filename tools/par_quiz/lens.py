import json,sys
for n in sys.argv[1:]:
    d=json.load(open('data/PAR-%02d.json'%int(n)))
    for k,q in enumerate(d['questions'],1):
        if q['t']=='mc':
            L=[len(o) for o in q['o']]; c=L[q['a']]
            o=sorted(L[:q['a']]+L[q['a']+1:]);print(k,L,q['a'],'LONG' if c>o[-1]*1.1 else 'SHORT' if c<o[0]*0.9 else 'ok')
