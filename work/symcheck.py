"""Symmetry check: if g is a rotation of prime order p, then a(n) == #(g-invariant TDS) (mod p).
g-invariant TDS of G = TDS of the quotient graph G/<g> (loops allowed: an orbit containing an edge
dominates itself).  Counted with method 2 (elimdp, loops supported) and, when small, brute force."""
import math, sys
from pdig import build
from elim import elim_order
from run_elim import count_elim
def quotient(n,p):
    N,E,pts=build(n); th=2*math.pi/p; c,s=math.cos(th),math.sin(th)
    key={(round(x*1e6),round(y*1e6)):i for i,(x,y) in enumerate(pts)}
    def find(x,y):
        kx,ky=round(x*1e6),round(y*1e6)
        for dx in (-1,0,1):
            for dy in (-1,0,1):
                if (kx+dx,ky+dy) in key: return key[(kx+dx,ky+dy)]
        raise KeyError
    g=[find(x*c-y*s,x*s+y*c) for x,y in pts]
    assert sorted(g)==list(range(N))
    Es=set(E); assert all((min(g[a],g[b]),max(g[a],g[b])) in Es for a,b in E), 'not an automorphism'
    orb=[-1]*N; k=0
    for v in range(N):
        if orb[v]<0:
            w=v
            while orb[w]<0: orb[w]=k; w=g[w]
            k+=1
    QE=sorted({(min(orb[a],orb[b]),max(orb[a],orb[b])) for a,b in E})
    return k,QE
def brute(N,E):
    nb=[0]*N
    for a,b in E: nb[a]|=1<<b; nb[b]|=1<<a
    return sum(all(nb[v]&S for v in range(N)) for S in range(1<<N))
def inv_count(n,p):
    Q,QE=quotient(n,p)
    simple=[e for e in QE if e[0]!=e[1]]
    w,o=min((elim_order(Q,simple,r,sd) for r in ('fill','deg') for sd in range(4)),key=lambda t:t[0])
    x,m=count_elim(Q,QE,o,Q//61+2); assert x<(1<<Q)
    if Q<=22: assert brute(Q,QE)==x, 'brute force disagrees on quotient'
    return Q,w,x
if __name__=='__main__':
    known={3:4,4:24,5:648,6:263003,7:793290313945,8:19780521126498508,
           9:127122812445017255670206773047466222123,10:4445417218586525760827112474487874053620425707538}
    for a in sys.argv[1:]:
        n,v=a.split('='); known[int(n)]=int(v)
    for n in sorted(known):
        for p in (2,3,5,7,11,13):
            if n%p: continue
            Q,w,x=inv_count(n,p)
            ok=(known[n]-x)%p==0
            print('n=%d p=%d quotient vertices=%d width=%d invariant TDS=%d  a(n) mod p=%d  %s'%(n,p,Q,w,x,known[n]%p,'OK' if ok else 'FAIL'),flush=True)
