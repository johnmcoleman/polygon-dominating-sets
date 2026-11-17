import sys, math, subprocess
from pdig import build
from width import greedy
def boundary_width(N,E,order):
    """peak slot usage, mirroring pathdp.c: allocate nbrs of u, then free finished vertices"""
    adj=[[] for _ in range(N)]
    for a,b in E: adj[a].append(b);adj[b].append(a)
    done=[0]*N; act=set(); mx=0
    for u in order:
        for v in adj[u]:
            if done[v]==0: act.add(v)
            done[v]+=1
        mx=max(mx,len(act))
        for v in adj[u]+[u]:
            if v in act and done[v]==len(adj[v]): act.discard(v)
    return mx
def best_order(n,tries=None):
    N,E,pts=build(n); best=None
    cands=[]
    for s in range(N if tries is None else min(N,tries)): cands.append(greedy(N,E,s))
    for k in range(180):
        th=math.pi*k/180
        cands.append(sorted(range(N),key=lambda v:pts[v][0]*math.cos(th)+pts[v][1]*math.sin(th)))
        cands.append(sorted(range(N),key=lambda v:math.atan2(pts[v][1],pts[v][0])+ (th*2) if math.atan2(pts[v][1],pts[v][0])+th*2<math.pi else math.atan2(pts[v][1],pts[v][0])+th*2-2*math.pi))
    for o in cands:
        w=boundary_width(N,E,o)
        if best is None or w<best[0]: best=(w,o)
    return N,E,best
def run(n,order=None,tries=None):
    N,E,(w,o)=best_order(n,tries)
    if order is not None: o=order; w=boundary_width(N,E,o)
    inp="%d %d %d\n"%(N,len(E),w)+"\n".join("%d %d"%e for e in E)+"\n"+" ".join(map(str,o))+"\n"
    r=subprocess.run(['./pathdp'],input=inp,capture_output=True,text=True)
    if r.returncode: raise RuntimeError(r.stderr)
    return w,int(r.stdout.strip(),16)
if __name__=='__main__':
    for n in map(int,sys.argv[1:]):
        w,c=run(n); print(n,'width',w,'TDS',c,flush=True)
