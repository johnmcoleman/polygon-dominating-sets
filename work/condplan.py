"""Joint choice of order + conditioning set C minimising total work 2^|C| * sum_steps 2^(slots) under a memory cap."""
import math, sys, json
from pdig import build
def intervals(N,adj,order):
    """slot lifetime [first,last] step (inclusive) of each vertex, mirroring the C code"""
    pos={u:i for i,u in enumerate(order)}
    iv={}
    for v in range(N):
        ps=[pos[w] for w in adj[v]]
        iv[v]=(min(ps),max(ps))
    return iv
def plan(N,adj,order,target):
    iv=intervals(N,adj,order)
    prof=[0]*N
    for v,(a,b) in iv.items():
        for i in range(a,b+1): prof[i]+=1
    C=[]; alive=set(range(N))
    def work(p): 
        m=max(p); return m+math.log2(sum(2.0**(x-m) for x in p))
    while max(prof)>target:
        m=max(prof); wts=[2.0**(x-m) for x in prof]; tot=sum(wts)
        # prefix sums for fast gain evaluation
        pre=[0.0]
        for w in wts: pre.append(pre[-1]+w)
        peaks=[i for i,x in enumerate(prof) if x==m]
        best=None
        for v in alive:
            a,b=iv[v]
            if not any(a<=i<=b for i in peaks): continue
            cov=pre[b+1]-pre[a]
            neww=2*(tot-cov/2)   # relative
            if best is None or neww<best[0]: best=(neww,v)
        v=best[1]; C.append(v); alive.discard(v)
        a,b=iv[v]
        for i in range(a,b+1): prof[i]-=1
    return C, work(prof)+len(C), max(prof)
def candidates(N,pts,k=360):
    for i in range(k):
        th=2*math.pi*i/k
        yield ('sweep',i),sorted(range(N),key=lambda v:pts[v][0]*math.cos(th)+pts[v][1]*math.sin(th))
        yield ('ang',i),sorted(range(N),key=lambda v:(math.atan2(pts[v][1],pts[v][0])+th)%(2*math.pi))
if __name__=='__main__':
    n=int(sys.argv[1]); targets=list(map(int,sys.argv[2:]))
    N,E,pts=build(n)
    adj=[[] for _ in range(N)]
    for a,b in E: adj[a].append(b);adj[b].append(a)
    for target in targets:
        best=None
        for name,o in candidates(N,pts,120):
            C,w,pk=plan(N,adj,o,target)
            if best is None or w<best[0]: best=(w,name,len(C),pk)
        print(n,'target',target,'best',best,flush=True)
