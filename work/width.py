from pdig import build
import sys, math
def boundary_width(N,E,order):
    """max over prefixes of #vertices having both processed and unprocessed nbrs"""
    adj=[[] for _ in range(N)]
    for a,b in E: adj[a].append(b);adj[b].append(a)
    done=[0]*N; deg=[len(a) for a in adj]; cur=0; mx=0; active=[False]*N
    for u in order:
        for v in adj[u]:
            done[v]+=1
            a=(0<done[v]<deg[v])
            if a and not active[v]: active[v]=True;cur+=1
            elif not a and active[v]: active[v]=False;cur-=1
        mx=max(mx,cur)
    return mx
def greedy(N,E,start):
    adj=[[] for _ in range(N)]
    for a,b in E: adj[a].append(b);adj[b].append(a)
    deg=[len(a) for a in adj]; done=[0]*N; proc=[False]*N; order=[]
    active=set(); cur=start
    for _ in range(N):
        if cur is None:
            # pick unprocessed vertex minimizing growth of active set
            best=None;bs=None
            cand=set()
            for v in active:
                for w in adj[v]:
                    if not proc[w]: cand.add(w)
            if not cand: cand={v for v in range(N) if not proc[v]}
            for u in cand:
                d=0
                for v in adj[u]:
                    nd=done[v]+1
                    was=0<done[v]<deg[v]; now=0<nd<deg[v]
                    d+=now-was
                key=(d,-sum(proc[w] for w in adj[u]))
                if bs is None or key<bs: bs=key;best=u
            cur=best
        u=cur;cur=None
        proc[u]=True;order.append(u)
        for v in adj[u]:
            done[v]+=1
            if 0<done[v]<deg[v]: active.add(v)
            else: active.discard(v)
    return order
def main():
  for n in range(5,15):
      N,E,pts=build(n)
      best=10**9
      for s in range(N):
          o=greedy(N,E,s); w=boundary_width(N,E,o); best=min(best,w)
          if N>400 and s>30: break
      # sweep orders
      sw=10**9
      for k in range(40):
          th=math.pi*k/40
          o=sorted(range(N),key=lambda v:pts[v][0]*math.cos(th)+pts[v][1]*math.sin(th))
          sw=min(sw,boundary_width(N,E,o))
      # radial (angle) order
      o=sorted(range(N),key=lambda v:(math.atan2(pts[v][1],pts[v][0]+1e-12),))
      print(n,N,'greedy',best,'sweep',sw,'angular',boundary_width(N,E,o),flush=True)

if __name__=='__main__': main()
