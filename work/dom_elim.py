"""A300529: dominating sets = 'total dominating sets' of the graph with a loop added at every vertex."""
import sys
from pdig import build
from elim import elim_order
from run_elim import count_elim
for n in map(int,sys.argv[1:]):
    N,E,_=build(n)
    w,o=min((elim_order(N,E,r,s) for r in ('fill','deg') for s in range(8)),key=lambda t:t[0])
    EL=E+[(v,v) for v in range(N)]
    x,m=count_elim(N,EL,o,N//61+2); assert x<(1<<N)
    print(n,'width',w,'dominating sets',x,flush=True)
