"""Mirror-symmetry check: for a reflection g of the polygon, a(n) == #(g-invariant solutions) (mod 2),
and invariant solutions are solutions on the quotient graph G/<g> (an orbit {v,gv} with v~gv gets a loop).
phi = angle of the mirror axis: 0 (through vertex 0) or pi/n (through an edge midpoint; a different class when n is even)."""
import math, sys
from pdig import build
from elim import elim_order
from gen_models import count
def quotient(n,phi):
    N,E,pts=build(n); c,s=math.cos(2*phi),math.sin(2*phi)
    key={(round(x*1e6),round(y*1e6)):i for i,(x,y) in enumerate(pts)}
    def find(x,y):
        kx,ky=round(x*1e6),round(y*1e6)
        for dx in (-1,0,1):
            for dy in (-1,0,1):
                if (kx+dx,ky+dy) in key: return key[(kx+dx,ky+dy)]
        raise KeyError
    g=[find(x*c+y*s,x*s-y*c) for x,y in pts]
    assert sorted(g)==list(range(N)) and all(g[g[v]]==v for v in range(N))
    Es=set(E); assert all((min(g[a],g[b]),max(g[a],g[b])) in Es for a,b in E)
    orb=[-1]*N; k=0
    for v in range(N):
        if orb[v]<0: orb[v]=orb[g[v]]=k; k+=1
    return k,sorted({(min(orb[a],orb[b]),max(orb[a],orb[b])) for a,b in E})
def residues(n,phi,models=('tds','dom','maxindep')):
    Q,QE=quotient(n,phi); simple=[e for e in QE if e[0]!=e[1]]
    w,o=min((elim_order(Q,simple,r,sd) for r in ('fill','deg') for sd in range(6)),key=lambda t:t[0])
    out={'Q':Q,'w':w}
    if w>15: return out
    for m in models:
        if m=='dom': x=count(Q,sorted(set(QE)|{(v,v) for v in range(Q)}),o,'tds',Q//61+2)
        else: x=count(Q,QE,o,m,Q//61+2)
        assert 0<=x<(1<<Q); out[m]=x%2
    return out
KNOWN={'tds':{3:4,4:24,5:648,6:263003,7:793290313945,8:19780521126498508,9:127122812445017255670206773047466222123,10:4445417218586525760827112474487874053620425707538},
 'dom':{3:7,4:27,5:863,6:385063,7:1993292588087,8:54230068320039879,9:2773576274509432974802491946402927554739,10:119283874191819442231697481474634239320305447119279},
 'maxindep':{10:1272369852811691513}}
if __name__=='__main__':
    for n in map(int,sys.argv[1:]):
        for name,phi in (('vertex axis',0.0),('edge axis',math.pi/n)):
            if n%2 and phi: continue
            r=residues(n,phi)
            s=['n=%d %s: quotient %d vertices, width %d'%(n,name,r['Q'],r['w'])]
            for m in ('tds','dom','maxindep'):
                if m not in r: s.append(m+' skipped'); continue
                k=KNOWN[m].get(n)
                s.append('%s mod 2 = %d%s'%(m,r[m],'' if k is None else (' OK' if k%2==r[m] else ' FAIL')))
            print('; '.join(s),flush=True)
