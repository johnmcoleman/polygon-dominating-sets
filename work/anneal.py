"""Anneal a vertex order to minimise total DP work = sum over steps of 2^(slots in use)."""
import math, random, sys, json
from pdig import build
def profile(adj,deg,order,N):
    done=[0]*N; cur=0; prof=[]
    for u in order:
        fin=0
        for v in adj[u]:
            if done[v]==0: cur+=1
            done[v]+=1
            if done[v]==deg[v]: fin+=1
        prof.append(cur); cur-=fin
    return prof
def cost(prof):
    m=max(prof); return m+math.log2(sum(2.0**(p-m) for p in prof))
def anneal(n,iters=200000,seed=0,start=None,T0=0.3,T1=0.01):
    N,E,pts=build(n); rnd=random.Random(seed)
    adj=[[] for _ in range(N)]
    for a,b in E: adj[a].append(b);adj[b].append(a)
    deg=[len(a) for a in adj]
    if start is None:
        best=None
        for k in range(180):
            th=math.pi*k/180
            for o in (sorted(range(N),key=lambda v:pts[v][0]*math.cos(th)+pts[v][1]*math.sin(th)),
                      sorted(range(N),key=lambda v:(math.atan2(pts[v][1],pts[v][0])+2*th)%(2*math.pi))):
                c=cost(profile(adj,deg,o,N))
                if best is None or c<best[0]: best=(c,o)
        c,o=best
    else: o=list(start); c=cost(profile(adj,deg,o,N))
    print(n,'start cost',round(c,2),flush=True)
    bo,bc=list(o),c
    for it in range(iters):
        T=T0*(T1/T0)**(it/iters)
        i=rnd.randrange(N); r=rnd.random()
        if r<0.5:
            j=min(N-1,max(0,i+rnd.randint(-12,12)))
            if i==j: continue
            v=o.pop(i); o.insert(j,v); undo=('mv',i,j)
        elif r<0.8:
            j=min(N-1,i+rnd.randint(1,10)); o[i:j+1]=o[i:j+1][::-1]; undo=('rev',i,j)
        else:
            j=rnd.randrange(N); v=o.pop(i); o.insert(j,v); undo=('mv',i,j)
        c2=cost(profile(adj,deg,o,N))
        if c2<=c or rnd.random()<math.exp((c-c2)/T):
            c=c2
            if c<bc: bc=c;bo=list(o)
        else:
            if undo[0]=='mv': v=o.pop(undo[2]); o.insert(undo[1],v)
            else: o[undo[1]:undo[2]+1]=o[undo[1]:undo[2]+1][::-1]
    p=profile(adj,deg,bo,N)
    print(n,'final cost',round(bc,2),'peak',max(p),flush=True)
    return bc,bo
if __name__=='__main__':
    n=int(sys.argv[1]); iters=int(sys.argv[2]); seed=int(sys.argv[3])
    bc,bo=anneal(n,iters,seed)
    json.dump({'n':n,'cost':bc,'order':bo},open('order_%d_s%d.json'%(n,seed),'w'))
