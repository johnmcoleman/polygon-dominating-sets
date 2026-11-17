"""Search angular sweeps around off-centre pivots for the cheapest conditioned plan."""
import math, sys, json
from multiprocessing import Pool
from pdig import build
from condplan import plan
n=int(sys.argv[1]); target=int(sys.argv[2]); K=int(sys.argv[3])
N,E,pts=build(n)
adj=[[] for _ in range(N)]
for a,b in E: adj[a].append(b);adj[b].append(a)
def ev(arg):
    px,py,th=arg
    o=sorted(range(N),key=lambda v:(math.atan2(pts[v][1]-py,pts[v][0]-px)+th)%(2*math.pi))
    C,w,pk=plan(N,adj,o,target)
    return w,arg,len(C)
if __name__=='__main__':
    args=[]
    for r in [0,0.05,0.1,0.2,0.3,0.45,0.6,0.8,1.0,1.3,2,4]:
        for a in range(8 if r else 1):
            pa=2*math.pi*a/8/n   # pivot angle within one fundamental sector
            for k in range(K):
                args.append((r*math.cos(pa)+1e-7,r*math.sin(pa)+2e-7,2*math.pi*k/K))
    with Pool(8) as p: res=p.map(ev,args,chunksize=8)
    res.sort()
    for r in res[:8]: print(n,target,r)
    by={}
    for w,(px,py,th),c in res:
        k=round(math.hypot(px,py),2); by[k]=min(by.get(k,99),w)
    print('best by pivot radius',sorted(by.items()))
    json.dump(res[0],open('pivot_%d_%d.json'%(n,target),'w'))
