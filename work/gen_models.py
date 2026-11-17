"""Generic pairwise 4-state models on the polygon diagonal intersection graph, by variable elimination.
State x of a vertex: s = x&1 (in the set), t = x>>1 (inclusion-exclusion marker 'left undominated')."""
import sys, subprocess, os
from pdig import build
from elim import elim_order
from run_elim import PRIMES
MODELS={
 # independent sets (A291948): validation only
 'indep': ([1,1,0,0], lambda x,y: int(not((x&1) and (y&1)))),
 # maximal independent sets (A292356): independent, and every vertex outside has a neighbour inside
 'maxindep': ([1,1,-1,0], lambda x,y: int(not((x&1) and (y&1)) and not((x>>1) and (y&1)) and not((y>>1) and (x&1)))),
 # total dominating sets (A347480): re-derivation through the generic code
 'tds': ([1,1,-1,-1], lambda x,y: int(not((x>>1) and (y&1)) and not((y>>1) and (x&1)))),
}
def binary(p):
    b='./elimgen_%d'%p
    if not os.path.exists(b): subprocess.check_call(['clang','-O3','-march=native','-DP=%dULL'%p,'-o',b,'elimgen.c'])
    return b
def count(N,E,order,model,nprimes):
    vw,f=MODELS[model]
    inp="%d %d\n"%(N,len(E))+"\n".join("%d %d"%tuple(e) for e in E)+"\n"+" ".join(map(str,order))+"\n"+" ".join(map(str,vw))+"\n"+" ".join(str(f(x,y)) for x in range(4) for y in range(4))+"\n"
    x=0;m=1
    for p in PRIMES[:nprimes]:
        r=subprocess.run([binary(p)],input=inp,capture_output=True,text=True)
        if r.returncode: raise RuntimeError(r.stderr)
        r=int(r.stdout); t=((r-x)*pow(m,-1,p))%p; x+=m*t; m*=p
    return x
def brute(N,E,model):
    nb=[0]*N
    for a,b in E: nb[a]|=1<<b; nb[b]|=1<<a
    c=0
    for S in range(1<<N):
        ind=all(not(nb[v]&S) for v in range(N) if S>>v&1)
        if model=='indep': c+=ind
        elif model=='maxindep': c+= ind and all((S>>v&1) or (nb[v]&S) for v in range(N))
        else: c+= all(nb[v]&S for v in range(N))
    return c
if __name__=='__main__':
    if sys.argv[1]=='test':
        import random; random.seed(5); bad=0;t=0
        for _ in range(120):
            N=random.randint(2,11); pr=random.choice([.2,.35,.5,.8])
            E=[(a,b) for a in range(N) for b in range(a+1,N) if random.random()<pr]
            o=list(range(N)); random.shuffle(o); mdl=random.choice(list(MODELS))
            g=count(N,E,o,mdl,1); e=brute(N,E,mdl); t+=1
            if g!=e: bad+=1; print('MISMATCH',mdl,N,E,g,e)
        print('tested',t,'mismatches',bad)
    else:
        model=sys.argv[1]
        for n in map(int,sys.argv[2:]):
            N,E,_=build(n)
            w,o=min((elim_order(N,E,r,s) for r in ('fill','deg') for s in range(8)),key=lambda t:t[0])
            x=count(N,E,o,model,N//61+2); assert x<(1<<N)
            print(model,n,'width',w,x,flush=True)
