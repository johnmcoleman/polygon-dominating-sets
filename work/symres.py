"""Expected residues from rotational symmetry for the long runs (TDS and dominating sets)."""
from symcheck import quotient
from elim import elim_order
from run_elim import count_elim
for n,ps in ((11,(11,)),(12,(2,3))):
    for p in ps:
        Q,QE=quotient(n,p)
        simple=[e for e in QE if e[0]!=e[1]]
        w,o=min((elim_order(Q,simple,r,sd) for r in ('fill','deg') for sd in range(4)),key=lambda t:t[0])
        x,_=count_elim(Q,QE,o,Q//61+2); assert x<(1<<Q)
        QL=sorted(set(QE)|{(v,v) for v in range(Q)})
        y,_=count_elim(Q,QL,o,Q//61+2); assert y<(1<<Q)
        print('n=%d p=%d quotient=%d width=%d: TDS mod p = %d, DOM mod p = %d'%(n,p,Q,w,x%p,y%p),flush=True)
