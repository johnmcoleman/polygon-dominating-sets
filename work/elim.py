import random, sys
from pdig import build
def elim_order(N,E,rule='fill',seed=0):
    """greedy elimination order; returns (width = max #nbrs at elimination, order)"""
    rnd=random.Random(seed)
    adj=[set() for _ in range(N)]
    for a,b in E: adj[a].add(b);adj[b].add(a)
    alive=set(range(N)); order=[]; width=0
    def fill(v):
        nb=list(adj[v]); f=0
        for i in range(len(nb)):
            a=adj[nb[i]]
            for j in range(i+1,len(nb)):
                if nb[j] not in a: f+=1
        return f
    score={v:(fill(v) if rule=='fill' else len(adj[v])) for v in alive}
    while alive:
        m=min(score[v] for v in alive)
        if rule=='fill':
            c=[v for v in alive if score[v]==m]; md=min(len(adj[v]) for v in c); c=[v for v in c if len(adj[v])==md]
        else: c=[v for v in alive if score[v]==m]
        v=rnd.choice(c)
        nb=list(adj[v]); width=max(width,len(nb)); order.append(v); alive.discard(v)
        touched=set(nb)
        for i in range(len(nb)):
            adj[nb[i]].discard(v)
            for j in range(i+1,len(nb)):
                if nb[j] not in adj[nb[i]]:
                    adj[nb[i]].add(nb[j]); adj[nb[j]].add(nb[i])
        if rule=='fill':
            for x in nb: touched|=adj[x]
        for x in touched:
            if x in alive: score[x]=fill(x) if rule=='fill' else len(adj[x])
    return width,order
if __name__=='__main__':
    for n in range(7,15):
        N,E,_=build(n)
        r=[]
        for rule in ('fill','deg'):
            ws=[elim_order(N,E,rule,s)[0] for s in range(6 if N<400 else 2)]
            r.append((rule,min(ws)))
        print(n,N,r,flush=True)
