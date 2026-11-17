"""A300529 by method 1 (path DP with loops), as an independent check of dom_elim.py.  Also random tests."""
import sys, math, subprocess, random, json
from concurrent.futures import ThreadPoolExecutor
from pdig import build
from condplan import plan, candidates
def count_loops(N,E,order,target,nw=3,procs=4,C=None,pk=None):
    """E may contain loops (v,v)."""
    adj=[[] for _ in range(N)]
    for a,b in E:
        adj[a].append(b)
        if a!=b: adj[b].append(a)
    if C is None: C,w,pk=plan(N,adj,order,target)
    inp="%d %d %d %d\n"%(N,len(E),max(pk,1),len(C))+"\n".join("%d %d"%tuple(e) for e in E)+"\n"+" ".join(map(str,order))+"\n"+" ".join(map(str,C))+"\n"
    tot=1<<len(C); nch=min(tot,procs*8); bounds=[tot*i//nch for i in range(nch+1)]
    def job(i):
        r=subprocess.run(['./pathdp4_%d'%nw,str(bounds[i]),str(bounds[i+1])],input=inp,capture_output=True,text=True)
        if r.returncode: raise RuntimeError(r.stderr)
        return int(r.stdout.strip(),16)
    with ThreadPoolExecutor(procs) as ex: s=sum(ex.map(job,range(nch)))%(1<<(64*nw))
    assert s<(1<<N); return s
def brute(N,E):
    nb=[0]*N
    for a,b in E: nb[a]|=1<<b; nb[b]|=1<<a
    return sum(all(nb[v]&S for v in range(N)) for S in range(1<<N))
if __name__=='__main__':
    if sys.argv[1]=='test':
        random.seed(11); bad=0; t=0
        for _ in range(200):
            N=random.randint(2,12); p=random.choice([.2,.35,.5,.8])
            E=[(a,b) for a in range(N) for b in range(a+1,N) if random.random()<p]
            E+=[(v,v) for v in range(N) if random.random()<random.choice([0.3,1.0])]
            if len({x for e in E for x in e})<N: continue
            o=list(range(N)); random.shuffle(o)
            got=count_loops(N,E,o,random.randint(0,6)); exp=brute(N,E); t+=1
            if got!=exp: bad+=1; print('MISMATCH',N,E,o,got,exp)
        print('tested',t,'mismatches',bad)
    else:
        procs=int(sys.argv[1])
        for n in map(int,sys.argv[2:]):
            N,E,pts=build(n); EL=E+[(v,v) for v in range(N)]
            adj=[[] for _ in range(N)]
            for a,b in EL:
                adj[a].append(b)
                if a!=b: adj[b].append(a)
            best=None
            for name,o in candidates(N,pts,60):
                C,w,pk=plan(N,adj,o,22)
                if best is None or w<best[0]: best=(w,o,C,pk)
            w,o,C,pk=best
            print(n,'work 2^%.1f |C|=%d peak %d'%(w,len(C),pk),'dominating sets',count_loops(N,EL,o,22,3,procs,C,pk),flush=True)
