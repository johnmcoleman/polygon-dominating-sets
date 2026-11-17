import random
from run2 import count
def brute(N,E):
    nb=[0]*N
    for a,b in E: nb[a]|=1<<b; nb[b]|=1<<a
    return sum(all(nb[v]&S for v in range(N)) for S in range(1<<N))
random.seed(7); bad=0; tested=0
import sys, io
for t in range(250):
    N=random.randint(3,13); p=random.choice([.25,.35,.5,.8])
    E=[(a,b) for a in range(N) for b in range(a+1,N) if random.random()<p]
    if len({x for e in E for x in e})<N: continue
    o=list(range(N)); random.shuffle(o)
    target=random.randint(0,6)
    err=sys.stderr; sys.stderr=io.StringIO()
    got=count(None,o,target,nw=3,procs=4,chunks_per=random.choice([1,3]),rawgraph=(N,E))
    info=sys.stderr.getvalue(); sys.stderr=err
    exp=brute(N,E); tested+=1
    if got!=exp: bad+=1; print('MISMATCH',N,E,o,target,got,exp,info)
print('tested',tested,'mismatches',bad)
