import random, subprocess
from run_path import boundary_width
def brute(N,E):
    nb=[0]*N
    for a,b in E: nb[a]|=1<<b; nb[b]|=1<<a
    return sum(all(nb[v]&S for v in range(N)) for S in range(1<<N))
random.seed(1); bad=0
for t in range(300):
    N=random.randint(2,13); p=random.choice([.2,.35,.5,.8])
    E=[(a,b) for a in range(N) for b in range(a+1,N) if random.random()<p]
    o=list(range(N)); random.shuffle(o)
    w=max(1,boundary_width(N,E,o))
    inp="%d %d %d\n"%(N,len(E),w)+"\n".join("%d %d"%e for e in E)+"\n"+" ".join(map(str,o))+"\n"
    r=subprocess.run(['./pathdp'],input=inp,capture_output=True,text=True)
    got=int(r.stdout.strip(),16) if r.returncode==0 else r.stderr
    exp=brute(N,E)
    if got!=exp: bad+=1; print('MISMATCH',N,E,o,got,exp)
print('random tests done, mismatches:',bad)
