from pdig import build
from elim import elim_order
import sys
n=int(sys.argv[1]); N,E,_=build(n)
adj=[set() for _ in range(N)]
for a,b in E: adj[a].add(b);adj[b].add(a)
E2=set()
for v in range(N):
    c=sorted(adj[v]|{v})
    for i in range(len(c)):
        for j in range(i+1,len(c)): E2.add((c[i],c[j]))
E2=sorted(E2)
print(n,N,len(E2),[elim_order(N,E2,r,s)[0] for r in('fill','deg') for s in range(4)])
