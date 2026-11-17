"""Symmetry congruence for the generic models: a(n) == (count on quotient graph by a rotation of prime order p) mod p."""
import sys
from symcheck import quotient
from elim import elim_order
from gen_models import count
def residue(model,n,p):
    Q,QE=quotient(n,p); simple=[e for e in QE if e[0]!=e[1]]
    w,o=min((elim_order(Q,simple,r,sd) for r in ('fill','deg') for sd in range(6)),key=lambda t:t[0])
    if w>15: return None
    x=count(Q,QE,o,model,Q//61+2); assert x<(1<<Q); return x%p
if __name__=='__main__':
    model=sys.argv[1]
    for a in sys.argv[2:]:
        n,v=a.split('='); n=int(n); v=int(v)
        for p in (2,3,5,7,11):
            if n%p: continue
            r=residue(model,n,p)
            print(model,'n=%d p=%d'%(n,p),'skipped (quotient too wide)' if r is None else 'quotient residue %d, a(n) mod p %d  %s'%(r,v%p,'OK' if r==v%p else 'FAIL'),flush=True)
