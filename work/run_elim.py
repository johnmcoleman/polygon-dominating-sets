import sys, subprocess, os, random
from pdig import build
from elim import elim_order
def is_prime(n):
    if n<2: return False
    for p in (2,3,5,7,11,13,17,19,23,29,31,37):
        if n%p==0: return n==p
    d=n-1;s=0
    while d%2==0: d//=2;s+=1
    for a in (2,3,5,7,11,13,17,19,23,29,31,37):
        x=pow(a,d,n)
        if x in (1,n-1): continue
        for _ in range(s-1):
            x=x*x%n
            if x==n-1: break
        else: return False
    return True
PRIMES=[]
q=(1<<62)-1
while len(PRIMES)<4:
    if is_prime(q): PRIMES.append(q)
    q-=2
def binary(p):
    b='./elimdp_%d'%p
    if not os.path.exists(b):
        subprocess.check_call(['clang','-O3','-march=native','-DP=%dULL'%p,'-o',b,'elimdp.c'])
    return b
def count_elim(N,E,order,nprimes):
    inp="%d %d\n"%(N,len(E))+"\n".join("%d %d"%e for e in E)+"\n"+" ".join(map(str,order))+"\n"
    res=[]
    for p in PRIMES[:nprimes]:
        r=subprocess.run([binary(p)],input=inp,capture_output=True,text=True)
        if r.returncode: raise RuntimeError(r.stderr)
        res.append(int(r.stdout))
    x=0;m=1
    for p,r in zip(PRIMES,res):
        t=((r-x)*pow(m,-1,p))%p if sys.version_info>=(3,8) else None
        x+=m*t; m*=p
    return x,m
if __name__=='__main__':
    if sys.argv[1]=='test':
        def brute(N,E):
            nb=[0]*N
            for a,b in E: nb[a]|=1<<b; nb[b]|=1<<a
            return sum(all(nb[v]&S for v in range(N)) for S in range(1<<N))
        random.seed(3); bad=0; t=0
        for _ in range(150):
            N=random.randint(2,11); pr=random.choice([.2,.35,.5,.8])
            E=[(a,b) for a in range(N) for b in range(a+1,N) if random.random()<pr]
            o=list(range(N)); random.shuffle(o)
            got,_=count_elim(N,E,o,1); exp=brute(N,E); t+=1
            if got!=exp: bad+=1; print('MISMATCH',N,E,o,got,exp)
        print('tested',t,'mismatches',bad)
    else:
        for n in map(int,sys.argv[1:]):
            N,E,_=build(n)
            w,o=min((elim_order(N,E,r,s) for r in ('fill','deg') for s in range(8)),key=lambda t:t[0])
            npr=N//61+2   # one more prime than needed: result must still be < 2^N
            x,m=count_elim(N,E,o,npr)
            assert x < (1<<N), 'CRT result out of range'
            print(n,'elim width',w,'primes',npr,'TDS',x,flush=True)
