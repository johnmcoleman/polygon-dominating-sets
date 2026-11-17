from pdig import build
import sys
def tds_brute(n):
    N,E,_=build(n)
    nb=[0]*N
    for a,b in E: nb[a]|=1<<b; nb[b]|=1<<a
    full=(1<<N)-1; cnt=0
    # Gray-code free simple loop; N<=19
    for S in range(1<<N):
        ok=True
        for v in range(N):
            if not (nb[v]&S): ok=False;break
        cnt+=ok
    return cnt
for n in range(3,7): print(n,tds_brute(n))
