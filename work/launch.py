import sys, json, math, os
from pdig import build
from run4 import make_plan, run
n=int(sys.argv[1]); target=int(sys.argv[2]); procs=int(sys.argv[3]); tag=sys.argv[4]; cb=int(sys.argv[5])
pf='plan_%s.json'%tag
if os.path.exists(pf): pl=json.load(open(pf))
else:
    w,(px,py,th),c=json.load(open('pivot_%d_%d.json'%(n,target)))
    N,E,pts=build(n)
    o=sorted(range(N),key=lambda v:(math.atan2(pts[v][1]-py,pts[v][0]-px)+th)%(2*math.pi))
    pl=make_plan(n,target,order=o); json.dump(pl,open(pf,'w'))
nw=3 if pl['N']<=190 else 6
r=run(pl,nw,procs,tag,chunk_bits=cb)
print(n,r); open('result_%s.txt'%tag,'w').write('%d %d\n'%(n,r))
